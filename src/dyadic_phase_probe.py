"""Bounded arithmetic-only single QND probe; no decoder or record sampler."""
from dataclasses import dataclass
import math
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import expm_multiply
from src.shor_modular_node import gksl

LOWER = np.array([[0,1],[0,0]],complex)

@dataclass(frozen=True)
class Probe:
    N: int
    a: int
    j: int = 0
    g: float = 1.
    Gamma: float = 1.

    def __post_init__(self):
        if type(self.N) is not int or not 2<=self.N<=7 or type(self.a) is not int or not 1<=self.a<self.N or math.gcd(self.a,self.N)!=1:
            raise ValueError('bounded coprime arithmetic inputs required')
        if type(self.j) is not int or not 0<=self.j<=8:
            raise ValueError('power cap exceeded')
        if any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or x<=0 for x in (self.g,self.Gamma)):
            raise ValueError('positive finite rates required')

    @property
    def d(self): return 1 << (self.N-1).bit_length()


def multiplier(model):
    c=model.a
    for _ in range(model.j): c=c*c%model.N
    rows=[c*y%model.N if y<model.N else y for y in range(model.d)]
    return sparse.csr_matrix((np.ones(model.d),(rows,np.arange(model.d))),shape=(model.d,model.d))


def operators(model):
    u=multiplier(model)
    h=model.g*(sparse.kron(LOWER.conjugate().T,u)+sparse.kron(LOWER,u.getH()))
    jump=math.sqrt(model.Gamma)*sparse.kron(LOWER,sparse.eye(model.d))
    return h.tocsr(),jump.tocsr()


def generator(model):
    h,j=operators(model);identity=sparse.eye(2*model.d)
    return gksl((j,))-1j*(sparse.kron(identity,h)-sparse.kron(h.T,identity))


def prepare(model):
    v=np.zeros(2*model.d,complex);v[1]=1
    return np.outer(v,v.conjugate())


def evolve(model,initial,times):
    rho=np.asarray(initial,complex);D=2*model.d
    if rho.shape!=(D,D) or not np.isfinite(rho).all() or not np.allclose(rho,rho.conjugate().T) or not np.isclose(np.trace(rho),1) or np.linalg.eigvalsh(rho).min() < -1e-10:
        raise ValueError('invalid density')
    if not times or len(times)>8 or any(not math.isfinite(t) or t<0 or max(model.g,model.Gamma)*t>80 for t in times) or any(b<=a for a,b in zip(times,times[1:])):
        raise ValueError('bounded increasing times required')
    L=generator(model)
    return tuple(expm_multiply(L*t,rho.reshape(-1,order='F')).reshape((D,D),order='F') for t in times)


def observation_means(model,rho,theta=0.,eta=1.):
    """Unconditional expected flux/current, NOT a measured classical record."""
    if not math.isfinite(theta) or not math.isfinite(eta) or not 0<=eta<=1:
        raise ValueError('invalid reference/efficiency')
    _,j=operators(model)
    return {'photon_flux':float(np.trace((j.getH()@j)@rho).real),
            'homodyne_mean':float(2*math.sqrt(eta)*np.trace(np.exp(-1j*theta)*j@rho).real)}
