from __future__ import annotations
from fractions import Fraction
import inspect,itertools,math
import pytest
from src.dyadic_phase_ms_dp_p import (
    BranchAmbiguity,DEFAULT_DELTA,MultiscaleError,canonical_cycle,
    compile_scale_constants,required_highest_scale,resource_profile,unwrap_local_phases,
)
D=DEFAULT_DELTA
EPS=Fraction(1,4096)
ERRORS=(-D+EPS,-Fraction(3,32),-Fraction(1,16),Fraction(0),
        Fraction(1,16),Fraction(3,32),D-EPS)
FIXTURES=(
    (5,2,4),(7,2,3),(7,3,6),(9,2,6),(15,2,4),
    (21,2,6),(31,2,5),(33,2,10),(35,2,12),
)

def order(N,a):
    x=1
    for r in range(1,N+1):
        x=x*a%N
        if x==1:return r
    raise AssertionError("order not found")

def circ(a,b):
    q=canonical_cycle(a-b)
    return min(q,1-q)

def local_record(theta,J,errors):
    return tuple(canonical_cycle((1<<j)*theta+errors[j]) for j in range(J+1))

def strict_point_candidates(estimate,N):
    out=[]
    radius=Fraction(1,2*N*N)
    for q in range(1,N):
        for p in range(q):
            if math.gcd(p,q)!=1:continue
            if circ(estimate,Fraction(p,q))<radius:
                out.append(Fraction(p,q))
    return tuple(out)

@pytest.mark.parametrize("N,a,r_expected",FIXTURES)
def test_fixture_orders_and_answer_free_compilation(N,a,r_expected):
    assert order(N,a)==r_expected
    cs=compile_scale_constants(N,a)
    assert len(cs)==required_highest_scale(N)+1
    assert all(c==pow(a,1<<j,N) for j,c in enumerate(cs))

@pytest.mark.parametrize("N,a,r",FIXTURES)
def test_exact_all_sectors_reach_point_without_truth_inputs(N,a,r):
    J=required_highest_scale(N)
    for s in range(r):
        theta=Fraction(s,r)
        result=unwrap_local_phases(N,local_record(theta,J,[0]*(J+1)))
        assert circ(result.estimate,theta)==0
        assert circ(result.estimate,theta)<result.point_radius
        assert strict_point_candidates(result.estimate,N)==(Fraction(s,r),)
        assert result.as_dict()["truth_inputs_used"] is False

def test_exhaustive_error_alphabet_bounded_fixture_family():
    for N,a,r in ((5,2,4),(7,2,3)):
        J=required_highest_scale(N)
        assert J<=4
        for s in range(r):
            theta=Fraction(s,r)
            for errors in itertools.product(ERRORS,repeat=J+1):
                result=unwrap_local_phases(N,local_record(theta,J,errors))
                assert circ(result.estimate,theta)<=D/(1<<J)
                assert circ(result.estimate,theta)<result.point_radius
                assert min(result.branch_margins,default=Fraction(1,2))>0

@pytest.mark.parametrize("N,a,r",FIXTURES)
def test_adversarial_near_delta_patterns_all_sectors(N,a,r):
    J=required_highest_scale(N)
    patterns=[]
    for sign in (-1,1):
        patterns.append(tuple(sign*(D-EPS) for _ in range(J+1)))
        patterns.append(tuple((sign if j%2==0 else -sign)*(D-EPS) for j in range(J+1)))
        patterns.append(tuple((sign if j%3 else -sign)*(D-EPS) for j in range(J+1)))
    for s in range(r):
        theta=Fraction(s,r)
        for errors in patterns:
            result=unwrap_local_phases(N,local_record(theta,J,errors))
            assert circ(result.estimate,theta)<=D/(1<<J)
            assert circ(result.estimate,theta)<result.point_radius

@pytest.mark.parametrize("theta",[
    Fraction(0),Fraction(1,4096),Fraction(4095,4096),
    Fraction(1,3),Fraction(2,3),Fraction(5,6),Fraction(11,12),
])
def test_circular_boundaries(theta):
    N=35
    J=required_highest_scale(N)
    errors=tuple((D-EPS)*(-1 if j%2 else 1) for j in range(J+1))
    result=unwrap_local_phases(N,local_record(theta,J,errors))
    assert circ(result.estimate,theta)<=D/(1<<J)

def test_repeated_early_alias_fixture_r6():
    N=21; theta=Fraction(1,6); J=required_highest_scale(N)
    truth=tuple(canonical_cycle((1<<j)*theta) for j in range(J+1))
    assert truth[:5]==(Fraction(1,6),Fraction(1,3),Fraction(2,3),Fraction(1,3),Fraction(2,3))
    assert unwrap_local_phases(N,truth).estimate==theta

def test_exact_half_integer_branch_tie_fails_closed():
    J=required_highest_scale(3)
    assert J==2
    with pytest.raises(BranchAmbiguity,match="tie"):
        unwrap_local_phases(3,[Fraction(1,4),Fraction(0),Fraction(0)])

def test_wrong_phase_count_fails_closed():
    N=15; J=required_highest_scale(N)
    with pytest.raises(MultiscaleError,match="exactly"):
        unwrap_local_phases(N,[0]*J)
    with pytest.raises(MultiscaleError,match="exactly"):
        unwrap_local_phases(N,[0]*(J+2))

@pytest.mark.parametrize("bad",[0,Fraction(1,6),Fraction(1,5),-Fraction(1,8)])
def test_invalid_delta_rejected(bad):
    with pytest.raises(MultiscaleError):
        required_highest_scale(15,bad)

def test_logarithmic_scale_count_and_no_N2_grid():
    for bits in (8,16,32,64,128,256,512,1024):
        N=(1<<bits)-1
        J=required_highest_scale(N)
        assert J<=2*N.bit_length()+1
        profile=resource_profile(N)
        assert profile["channel_count"]==J+1
        assert profile["stored_local_phase_values"]==J+1
        assert profile["global_grid_points"]==0
        assert profile["global_N2_grid_used"] is False

def test_source_interface_has_no_truth_or_order_inputs():
    import src.dyadic_phase_ms_dp_p as mod
    sig=inspect.signature(mod.unwrap_local_phases)
    assert tuple(sig.parameters)==("N","local_estimates","delta")
    source=inspect.getsource(mod.unwrap_local_phases)
    for forbidden in ("true_phase","sector","expected_phase","order_table","factor"):
        assert forbidden not in source

def test_result_and_resource_sizes_are_logarithmic():
    for bits in (16,64,256):
        N=(1<<bits)-1
        J=required_highest_scale(N)
        result=unwrap_local_phases(N,[Fraction(0)]*(J+1))
        assert len(result.branches)==J
        assert len(result.branch_margins)==J
        assert result.channel_count==J+1
        assert result.as_dict()["global_N2_grid_used"] is False

@pytest.mark.parametrize("N,a,delta,J", [
    (2, 1, Fraction(1, 16), 0),
    (15, 2, DEFAULT_DELTA, 6),
])
def test_compiler_executes_exactly_J_modular_squarings(N, a, delta, J):
    counts = {"squares": 0, "reductions": 0}

    class CountedInt(int):
        def __mul__(self, other):
            assert int(self) == int(other)
            counts["squares"] += 1
            return CountedInt(int(self) * int(other))

        def __mod__(self, modulus):
            counts["reductions"] += 1
            return CountedInt(int(self) % modulus)

    result = compile_scale_constants(N, CountedInt(a), delta)

    assert result == tuple(pow(a, 1 << j, N) for j in range(J + 1))
    assert counts == {"squares": J, "reductions": J + 1}
