from fractions import Fraction as F
from math import gcd
import pytest
from src.dyadic_phase_p4_types import Policy, parse_phase
from src.dyadic_phase_p4_decode import decode_point, decode_set, aggregate, circular_distance
from p4_helpers import phase

@pytest.mark.parametrize('N',[2,5,7,15,21])
def test_strict_rational_neighborhoods(N):
    for q in range(1,N):
        for p in range(q):
            if gcd(p,q)!=1:continue
            x=F(p,q)
            for t in (F(-9,10),F(0),F(9,10)):
                v=parse_phase(phase(N,1,(x+t/F(2*N*N))%1),Policy())
                assert decode_point(N,1,v,Policy()).values==(x,)

@pytest.mark.parametrize('N',[2,5,7,15])
def test_strict_boundary_and_wrap(N):
    for sign in (-1,1):
        v=parse_phase(phase(N,1,(sign*F(1,2*N*N))%1),Policy())
        assert F(0) not in decode_point(N,1,v,Policy()).values

def test_set_enumerates_modes_wrap_and_endpoints():
    C=((F(0),F(1,10)),(F(9,10),F(1)),(F(1,3),F(1,3)))
    v=parse_phase(phase(intervals=C),Policy());got=decode_set(7,3,v,Policy())
    assert got.complete and got.values==(F(0),F(1,3))
    p=phase(value=F(0),intervals=((F(1),F(1)),));assert decode_set(7,3,parse_phase(p,Policy()),Policy()).values==(F(0),)

def test_epsilon_outward_enlargement():
    p=phase(value=F(0));p['epsilon']=[1,6];v=parse_phase(p,Policy())
    assert decode_set(7,3,v,Policy()).values==(F(0),F(1,6),F(5,6))

@pytest.mark.parametrize('cap',[0,1,5])
def test_set_cap_never_claims_complete(cap):
    policy=Policy(max_rational_visits=cap);v=parse_phase(phase(intervals=((F(0),F(1)),)),policy)
    out=decode_set(7,3,v,policy);assert not out.complete
    assert not aggregate(7,3,[out],[v],policy).complete

def test_aggregate_choices_not_lcm_of_alternatives():
    v=parse_phase(phase(intervals=((F(1,3),F(1,3)),(F(1,2),F(1,2)))),Policy())
    c=decode_set(7,3,v,Policy());out=aggregate(7,3,[c],[v],Policy())
    assert out.values==(2,3) and out.status=='AMBIGUOUS_CANDIDATES'

def test_fresh_complementary_denominators_and_caps():
    vs=[parse_phase(phase(value=x,slot=i),Policy()) for i,x in enumerate((F(1,3),F(1,2)))]
    cs=[decode_point(7,3,v,Policy()) for v in vs]
    out=aggregate(7,3,cs,vs,Policy());assert out.values==(6,) and out.lcm_calls==2
    assert not aggregate(7,3,cs,vs,Policy(max_lcm_calls=1)).complete
