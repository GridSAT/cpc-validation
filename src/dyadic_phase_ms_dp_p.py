"""Truth-free deterministic multiscale dyadic phase unwrapping for MS-DP-P E2."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Iterable

DEFAULT_DELTA=Fraction(1,8)
MAX_DELTA=Fraction(1,6)

class MultiscaleError(ValueError): pass
class BranchAmbiguity(MultiscaleError): pass

def _fraction(value)->Fraction:
    if isinstance(value,bool): raise MultiscaleError("boolean phase value")
    if isinstance(value,Fraction): return value
    if isinstance(value,int): return Fraction(value,1)
    if isinstance(value,float):
        if not math.isfinite(value): raise MultiscaleError("non-finite phase value")
        return Fraction.from_float(value)
    if isinstance(value,str):
        try: return Fraction(value)
        except (ValueError,ZeroDivisionError) as exc:
            raise MultiscaleError("invalid rational phase string") from exc
    raise MultiscaleError("phase value must be int, Fraction, finite float, or rational string")

def canonical_cycle(value)->Fraction:
    return _fraction(value)%1

def validate_delta(delta=DEFAULT_DELTA)->Fraction:
    d=_fraction(delta)
    if not Fraction(0)<d<MAX_DELTA:
        raise MultiscaleError("delta must satisfy 0 < delta < 1/6")
    return d

def required_highest_scale(N:int,delta=DEFAULT_DELTA)->int:
    if isinstance(N,bool) or not isinstance(N,int) or N<2:
        raise MultiscaleError("N must be an integer >= 2")
    d=validate_delta(delta)
    threshold=2*d*N*N
    J=0
    power=1
    while power<=threshold:
        power<<=1
        J+=1
    return J

def compile_scale_constants(N:int,a:int,delta=DEFAULT_DELTA)->tuple[int,...]:
    J=required_highest_scale(N,delta)
    if isinstance(a,bool) or not isinstance(a,int):
        raise MultiscaleError("a must be an integer")
    if math.gcd(a,N)!=1:
        raise MultiscaleError("gcd(a,N) must equal 1")
    c=a%N
    out=[c]
    for _ in range(J):
        c=(c*c)%N
        out.append(c)
    return tuple(out)

def _nearest_integer_unique(x:Fraction)->tuple[int,Fraction]:
    lo=x.numerator//x.denominator
    f=x-lo
    if f==Fraction(1,2):
        raise BranchAmbiguity("nearest-integer branch tie")
    if f<Fraction(1,2):
        k=lo
        distance=f
    else:
        k=lo+1
        distance=1-f
    margin=Fraction(1,2)-distance
    if margin<=0: raise BranchAmbiguity("non-positive branch margin")
    return k,margin

@dataclass(frozen=True)
class MultiscaleResult:
    estimate:Fraction
    delta:Fraction
    highest_scale:int
    channel_count:int
    branches:tuple[int,...]
    branch_margins:tuple[Fraction,...]
    point_radius:Fraction
    def as_dict(self)->dict:
        pair=lambda q:[q.numerator,q.denominator]
        return {
            "schema":"cpc-shor-ms-dp-p-e2-result/1",
            "estimate":pair(self.estimate),
            "delta":pair(self.delta),
            "highest_scale":self.highest_scale,
            "channel_count":self.channel_count,
            "branches":list(self.branches),
            "branch_margins":[pair(q) for q in self.branch_margins],
            "point_radius":pair(self.point_radius),
            "truth_inputs_used":False,
            "global_N2_grid_used":False,
        }

def unwrap_local_phases(N:int,local_estimates:Iterable,delta=DEFAULT_DELTA)->MultiscaleResult:
    """Truth-free recursive unwrapping at the exact frozen scale count."""
    d=validate_delta(delta)
    J=required_highest_scale(N,d)
    phases=tuple(canonical_cycle(x) for x in local_estimates)
    if len(phases)!=J+1:
        raise MultiscaleError(f"expected exactly {J+1} local phase estimates for N={N}; got {len(phases)}")
    theta=phases[0]
    branches=[]
    margins=[]
    for j in range(1,J+1):
        x=(1<<j)*theta-phases[j]
        k,margin=_nearest_integer_unique(x)
        theta=canonical_cycle((phases[j]+k)/(1<<j))
        branches.append(k)
        margins.append(margin)
    return MultiscaleResult(
        estimate=theta,delta=d,highest_scale=J,channel_count=J+1,
        branches=tuple(branches),branch_margins=tuple(margins),
        point_radius=Fraction(1,2*N*N),
    )

def resource_profile(N:int,delta=DEFAULT_DELTA)->dict:
    J=required_highest_scale(N,delta)
    return {
        "schema":"cpc-shor-ms-dp-p-e2-resource/1",
        "highest_scale":J,
        "channel_count":J+1,
        "compiler_modular_squarings":J,
        "unwrap_nearest_integer_ops":J,
        "stored_local_phase_values":J+1,
        "global_grid_points":0,
        "global_N2_grid_used":False,
    }
