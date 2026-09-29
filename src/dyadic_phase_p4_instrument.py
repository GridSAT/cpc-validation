"""Explicit P4 bounded N<=15 adapter; unchanged P3 sources are not patched.

The P4 C kernel differs only in five state-dimension/buffer limits (64 ->128).
No generator call is allowed outside the separately GO-gated acquisition layer.
"""
from dataclasses import dataclass
import math
import ctypes
import numpy as np
from src.dyadic_phase_instrument import digest_array
from src.dyadic_phase_p3_execution import _engine
from src.dyadic_phase_p3_fast import load_filter


@dataclass(frozen=True)
class Bank:
    N:int
    a:int
    scales:tuple=(0,1,2)
    g:float=1/math.sqrt(8)
    Gamma:float=1.

    def __post_init__(self):
        if type(self.N) is not int or not 2<=self.N<=15 or type(self.a) is not int or not 1<=self.a<self.N or math.gcd(self.a,self.N)!=1:raise ValueError('P4 bounded coprime domain N<=15')
        if self.scales!=(0,1,2):raise ValueError('P4 DP-P scales0,1,2 required')
        if any(type(x) not in (int,float) or not math.isfinite(x) or x<=0 for x in (self.g,self.Gamma)):raise ValueError('positive finite rates')

    @property
    def d(self):return 1<<(self.N-1).bit_length()

    @property
    def dimension(self):return self.d*8


def compile_bank(model):
    d,D=model.d,model.dimension;compiled=[]
    for slot,j in enumerate(model.scales):
        c=pow(model.a,2**j,model.N);inverse=pow(c,-1,model.N);mask=1<<(2-slot)
        perm=np.array([(probes^mask)*d+((inverse if probes&mask else c)*y%model.N if y<model.N else y)
                       for probes in range(8) for y in range(d)],dtype=np.int64)
        h=np.zeros((D,D),complex);h[np.arange(D),perm]=1
        front=np.array([k for bit in (0,1) for k in range(D) if bool((k//d)&mask)==bool(bit)])
        compiled.append({'scale':j,'slot':slot,'permutation':perm,'coefficients':np.ones(D,complex),'front':front,
                         'inverse_front':np.argsort(front),'g':model.g,'Gamma':model.Gamma,'H_hash':digest_array(model.g*h)})
    return tuple(compiled)


def _compiled_profile(model,profile):
    if profile!='DP-P':raise ValueError('P4 primary profile is DP-P; no silent sequential fallback')
    return np.ascontiguousarray([c['permutation'] for c in compile_bank(model)],dtype=np.int64),model.dimension


def _run_prepared(model,profile,schedule,seed,initial,library_path):
    """Same P3 finite instrument and RNG plumbing with explicit128-state library."""
    permutations,dimension=_compiled_profile(model,profile)
    dt,burn,window=(schedule[k] for k in ('dt','burn','window'))
    eta=schedule['eta'];chi=np.ascontiguousarray(schedule['transfer_phases'],dtype=float)
    if (not .005<=dt<=.04 or not 0<=eta<=1 or not 0<=burn<=32 or not 0<window<=4096
            or window/dt>500000 or any(abs(v/dt-round(v/dt))>1e-8 for v in (burn,window))
            or chi.shape!=(len(model.scales),) or not np.isfinite(chi).all()):raise ValueError('invalid schedule')
    initial=np.ascontiguousarray(initial,dtype=complex)
    if initial.shape!=(dimension,) or not np.isclose(np.vdot(initial,initial),1,atol=1e-12):raise ValueError('invalid initial ket')
    steps,burn_steps=round(window/dt),round(burn/dt)
    signal=np.empty((3,2,steps));reference=np.empty_like(signal);final=np.empty(dimension,complex);counters=np.empty(8,dtype=np.uint64)
    bitgen=np.random.PCG64(np.random.SeedSequence(seed));interface=bitgen.ctypes
    status=_engine(load_filter(library_path))(0,3,model.d,steps,burn_steps,model.g,model.Gamma,eta,dt,chi,permutations,initial,
        interface.state,ctypes.cast(interface.next_double,ctypes.c_void_p),signal,reference,final,counters)
    if status:raise ArithmeticError('P4 bounded finite instrument failed: '+str(status))
    if not np.isfinite(signal).all() or not np.isfinite(reference).all() or not np.isfinite(final).all() or abs(np.vdot(final,final)-1)>1e-9:raise ArithmeticError('invalid generated state/record')
    return signal,reference,final,counters,bitgen.state
