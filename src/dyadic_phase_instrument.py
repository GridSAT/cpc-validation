"""Single-probe finite-step homodyne instrument; no sector/oracle sampler.

Exact CP collision steps converge to the approved SME. Arithmetic compilation
and operational preparation are separate from diagnostic initializations.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
from time import monotonic

import numpy as np
from scipy.linalg import expm
from src.dyadic_phase_probe import Probe, operators, generator


def digest_array(array):
    a=np.ascontiguousarray(array)
    return hashlib.sha256(str((a.shape,str(a.dtype))).encode()+a.tobytes()).hexdigest()


def compile_probe(model: Probe):
    """Arithmetic-only monomial Hamiltonian; no truth label or eigenbasis."""
    h,j=operators(model)
    S=h.toarray()/model.g
    permutation=np.argmax(np.abs(S),axis=1)
    coefficients=S[np.arange(len(S)),permutation]
    return {'permutation':permutation,'coefficients':coefficients,
            'g':model.g,'Gamma':model.Gamma,'dimension':2*model.d,
            'H_hash':digest_array(h.toarray()),'J_hash':digest_array(j.toarray())}


def operational_initial(model: Probe, trajectories: int):
    """Always ground probe and data |1>; no initial-state advice accepted."""
    if type(trajectories) is not int or not 1<=trajectories<=1024:
        raise ValueError('trajectory cap')
    rho=np.zeros((trajectories,2*model.d,2*model.d),complex)
    rho[:,1,1]=1
    return rho


def _unitary_half(rho, permutation, coefficients, g, dt):
    c,s=math.cos(g*dt/2),math.sin(g*dt/2)
    coeff=np.broadcast_to(coefficients,(len(rho),rho.shape[-1]))
    perm=np.broadcast_to(permutation,(len(rho),rho.shape[-1]))
    left=coeff[:,:,None]*np.take_along_axis(rho,perm[:,:,None],axis=1)
    right=np.take_along_axis(rho,perm[:,None,:],axis=2)*coeff.conjugate()[:,None,:]
    both=np.take_along_axis(left,perm[:,None,:],axis=2)*coeff.conjugate()[:,None,:]
    return c*c*rho+s*s*both-1j*c*s*(left-right)


def _quadrature_draw(rho,p,eta,theta,rng):
    """Exact polynomial-times-Gaussian outcome law, sampled by rejection.

    Proposal is half vacuum Gaussian plus half one-photon quadrature law.
    Its density is normal(y)*(1+y*y)/2 and envelope constant is 2.
    """
    d=rho.shape[-1]//2
    pe=np.trace(rho[:,d:,d:],axis1=1,axis2=2).real
    q=np.trace(rho[:,d:,:d],axis1=1,axis2=2)
    a=1-eta*p*pe;c=eta*p*pe
    b=2*math.sqrt(eta*p)*np.real(np.exp(-1j*theta)*q)
    values=np.empty(len(rho));pending=np.arange(len(rho));violation=0.
    for _ in range(64):
        if not len(pending):break
        normal=rng.normal(size=len(pending))
        photon=np.sqrt(rng.chisquare(3,size=len(pending)))*rng.choice((-1.,1.),size=len(pending))
        y=np.where(rng.random(len(pending))<.5,normal,photon)
        probability=(a[pending]+b[pending]*y+c[pending]*y*y)/(1+y*y)
        violation=max(violation,float(max(0.,-probability.min(),probability.max()-1)))
        if violation>1e-10:raise ArithmeticError('rejection envelope violated')
        selected=rng.random(len(pending))<probability
        values[pending[selected]]=y[selected];pending=pending[~selected]
    if len(pending):raise RuntimeError('rejection iteration cap')
    return values,violation


def collision_update(rho,dy,dt,Gamma,eta,theta):
    """Positive instrument conditioned on the actual quadrature increment."""
    p=-math.expm1(-Gamma*dt);survival=math.exp(-Gamma*dt/2)
    y=np.asarray(dy)/math.sqrt(dt)
    b=math.sqrt(eta*p)*np.exp(-1j*theta)*y
    d=rho.shape[-1]//2;gg,ge,eg,ee=rho[:,:d,:d],rho[:,:d,d:],rho[:,d:,:d],rho[:,d:,d:]
    result=np.empty_like(rho)
    result[:,:d,:d]=gg+b[:,None,None]*eg+b.conjugate()[:,None,None]*ge+(np.abs(b)**2+(1-eta)*p)[:,None,None]*ee
    result[:,:d,d:]=survival*(ge+b[:,None,None]*ee)
    result[:,d:,:d]=survival*(eg+b.conjugate()[:,None,None]*ee)
    result[:,d:,d:]=survival**2*ee
    normalization=np.trace(result,axis1=1,axis2=2)
    if np.max(np.abs(normalization.imag))>1e-10 or np.min(normalization.real)<=0:
        raise ArithmeticError('invalid instrument normalization')
    return result/normalization.real[:,None,None]


def _validate(compiled,rho,dt,eta,chi,burn,window):
    if rho.ndim!=3 or rho.shape[1]!=rho.shape[2] or rho.shape[1]>16 or not 1<=len(rho)<=1024:
        raise ValueError('bounded density dimensions required')
    if not np.isfinite(rho).all() or not np.allclose(np.trace(rho,axis1=1,axis2=2),1,atol=1e-10) or not np.allclose(rho,rho.conjugate().transpose(0,2,1),atol=1e-10) or np.linalg.eigvalsh(rho).min() < -1e-10:
        raise ValueError('invalid initial density')
    if not (0<dt<=.04 and 0<=eta<=1 and math.isfinite(chi) and 0<=burn<=16 and 0<window<=128):
        raise ValueError('instrument/time cap')
    if any(abs(v/dt-round(v/dt))>1e-8 for v in (burn,window)):
        raise ValueError('windows must contain integral steps')
    S=np.zeros((len(rho),rho.shape[1],rho.shape[1]),complex)
    perm=np.broadcast_to(compiled['permutation'],(len(rho),rho.shape[1]))
    S[np.arange(len(rho))[:,None],np.arange(rho.shape[1])[None,:],perm]=compiled['coefficients']
    if not np.allclose(S,S.conjugate().transpose(0,2,1)) or not np.allclose(S@S,np.eye(rho.shape[1])):
        raise ValueError('Hamiltonian is not declared monomial involution')


def simulate_instrument(compiled,initial,dt,eta,chi,burn,window,seed,record_path):
    """Shared physics engine; caller must classify operational vs diagnostics.

    Saves every increment in the predeclared RECORD windows, not burn-in.
    Burn-in is propagated with the same instrument, deliberately discarded,
    and reproducible from the saved RNG rule. Window-start states are returned.
    """
    rho=np.asarray(initial,complex).copy()
    _validate(compiled,rho,dt,eta,chi,burn,window)
    path=Path(record_path)
    if path.exists():raise FileExistsError(path)
    steps=round(window/dt);burn_steps=round(burn/dt)
    records=np.lib.format.open_memmap(path,mode='w+',dtype=np.float64,shape=(2,steps,len(rho)))
    rng=np.random.default_rng(np.random.SeedSequence(seed));start=monotonic()
    diagnostics={'max_trace_error':0.,'max_Hermiticity_error':0.,'min_eigenvalue':1.,'max_envelope_violation':0.,'sampled_density_checks':0}
    starts=[]
    p=-math.expm1(-compiled['Gamma']*dt)
    for block,command in enumerate((0.,math.pi/2)):
        theta=command-chi
        for k in range(burn_steps+steps):
            if k%128==0 and monotonic()-start>240:raise TimeoutError('predeclared group time cap')
            if k==burn_steps:starts.append(rho.copy())
            rho=_unitary_half(rho,compiled['permutation'],compiled['coefficients'],compiled['g'],dt)
            y,violation=_quadrature_draw(rho,p,eta,theta,rng)
            dy=math.sqrt(dt)*y
            rho=collision_update(rho,dy,dt,compiled['Gamma'],eta,theta)
            rho=_unitary_half(rho,compiled['permutation'],compiled['coefficients'],compiled['g'],dt)
            if k>=burn_steps:records[block,k-burn_steps]=dy
            diagnostics['max_envelope_violation']=max(diagnostics['max_envelope_violation'],violation)
            if k%max(1,(steps+burn_steps)//32)==0 or k==steps+burn_steps-1:
                diagnostics['max_trace_error']=max(diagnostics['max_trace_error'],float(np.max(np.abs(np.trace(rho,axis1=1,axis2=2)-1))))
                diagnostics['max_Hermiticity_error']=max(diagnostics['max_Hermiticity_error'],float(np.max(np.abs(rho-rho.conjugate().transpose(0,2,1)))))
                diagnostics['min_eigenvalue']=min(diagnostics['min_eigenvalue'],float(np.linalg.eigvalsh(rho).min()))
                diagnostics['sampled_density_checks']+=len(rho)
    records.flush()
    means=np.asarray(records.sum(axis=1)/(window))
    diagnostics['seconds']=monotonic()-start
    return {'final_states':rho,'window_start_states':np.asarray(starts),'mean_quadratures':means,'diagnostics':diagnostics,'record_shape':records.shape}


def execute_operational(model,trajectories,dt,eta,chi,burn,window,seed,record_path):
    """The only operational entry: no phase, sector or initial-state arguments."""
    reference=Probe(model.N,1,model.j,model.g,model.Gamma)
    signal,ref=compile_probe(model),compile_probe(reference)
    compiled={**signal,'permutation':np.concatenate([np.tile(signal['permutation'],(trajectories,1)),np.tile(ref['permutation'],(trajectories,1))]),
              'coefficients':np.concatenate([np.tile(signal['coefficients'],(trajectories,1)),np.tile(ref['coefficients'],(trajectories,1))])}
    initial=np.concatenate([operational_initial(model,trajectories),operational_initial(reference,trajectories)])
    return simulate_instrument(compiled,initial,dt,eta,chi,burn,window,seed,record_path)


def estimate_phase(signal_records,reference_records,window,min_contrast=.2):
    """Record-only phase estimate; does not consume the generator or truth."""
    signal=np.asarray(signal_records).sum(axis=1)/window
    reference=np.asarray(reference_records).sum(axis=1)/window
    z=-signal[1]+1j*signal[0];r=-reference[1]+1j*reference[0]
    valid=(np.abs(z)>=min_contrast)&(np.abs(r)>=min_contrast)
    return {'phase':np.angle(z*r.conjugate()),'valid':valid,'signal_Z':z,'reference_Z':r}


def deterministic_split(model,initial,dt,duration):
    """Instrument-averaged deterministic consistency check; no random records."""
    h,j=operators(model);D=2*model.d
    Q=expm(-1j*h.toarray()*dt/2)
    k0=np.kron(np.diag([1.,math.exp(-model.Gamma*dt/2)]),np.eye(model.d))
    k1=math.sqrt(-math.expm1(-model.Gamma*dt))*j.toarray()/math.sqrt(model.Gamma)
    a,b=Q@k0@Q,Q@k1@Q
    channel=np.kron(a.conjugate(),a)+np.kron(b.conjugate(),b)
    result=np.linalg.matrix_power(channel,round(duration/dt))@initial.reshape(-1,order='F')
    return result.reshape(D,D,order='F')
