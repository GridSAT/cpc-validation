"""Record-only P3 inference and all ablations; no arithmetic/diagnostic imports."""
from __future__ import annotations
import math
import numpy as np
from src.dyadic_phase_p3_fast import load_filter, circular_joint
from src.dyadic_phase_p3_analysis import joint_confidence_set


def infer_records(signal_records, reference_records, scales, *, library_path,
                  g, Gamma, eta, dt, burn_steps, coarse_grid, fine_grid,
                  moment_bounds, confidence_alpha):
    """One full-circle common-theta estimator and a separate global confidence."""
    lib=load_filter(library_path)
    settings=dict(g=g,Gamma=Gamma,eta=eta,dt=dt,burn_steps=burn_steps)
    coarse=circular_joint(lib,signal_records,reference_records,scales,grid_size=coarse_grid,**settings)
    fine=circular_joint(lib,signal_records,reference_records,scales,grid_size=fine_grid,**settings)
    ratio=fine_grid//coarse_grid
    if ratio*coarse_grid!=fine_grid:raise ValueError('nested grids required')
    curves=['log_likelihood','j0_only_log_likelihood']
    errors={key:float(np.ptp(coarse[key]-fine[key][::ratio])) for key in curves}
    for j in scales:
        errors[f'ablated-{j}']=float(np.ptp(coarse['ablated_log_likelihoods'][j]-fine['ablated_log_likelihoods'][j][::ratio]))
    confidence=joint_confidence_set(signal_records,reference_records,scales,dt=dt,
                                    moment_bounds=moment_bounds,alpha=confidence_alpha)
    slot0=tuple(scales).index(0)
    baseline=joint_confidence_set(np.asarray(signal_records)[slot0:slot0+1],
                                  np.asarray(reference_records)[slot0:slot0+1],(0,),dt=dt,
                                  moment_bounds=moment_bounds,alpha=confidence_alpha)
    window=np.shape(signal_records)[-1]*dt
    sigmean=np.asarray(signal_records).sum(axis=2)/window
    refmean=np.asarray(reference_records).sum(axis=2)/window
    zs=-sigmean[:,1]+1j*sigmean[:,0];zr=-refmean[:,1]+1j*refmean[:,0]
    W=zs*zr.conj()
    # Independent reconstruction of each marginalized local factor from the
    # already replayed phase laws; full - ablation must equal that factor.
    from scipy.special import logsumexp
    M=fine_grid;index=np.arange(M);factor_error=0.
    for slot,j in enumerate(scales):
        signal=fine['signal_phase_log_likelihoods'][slot][(2**j*index[:,None]+index[None,:])%M]
        reference=fine['reference_phase_log_likelihoods'][slot]
        expected=logsumexp(signal+reference,axis=1)-logsumexp(reference)
        actual=fine['log_likelihood']-fine['ablated_log_likelihoods'][j]
        factor_error=max(factor_error,float(np.max(abs(actual-expected))))
    no_j0=fine['ablated_log_likelihoods'][0]
    alias_error=float(np.max(abs(no_j0-np.roll(no_j0,M//2))))
    summary={'estimate':fine['estimate'],'identifiable':eta>0,
             'confidence':confidence,'j0_confidence':baseline,
             'j0_estimate':float(np.argmax(fine['j0_only_log_likelihood'])/M),
             'maximizer_grid_change_cycles':float(abs((coarse['estimate']-fine['estimate']+.5)%1-.5)),
             'quadrature_errors':errors,'conditional_factor_error':factor_error,
             'j1_j2_half_turn_alias_error':alias_error,
             'eta0_loglaw_range':float(np.ptp(fine['log_likelihood'])),
             'eta0_working_prior_deviation':float(np.max(abs(fine['working_prior_weights']-1/M))),
             'referenced_real':W.real.tolist(),'referenced_imag':W.imag.tolist(),
             'fresh_data_feature':float(np.real(W[0]**2*np.conj(W[1]))),
             'wrong_sign_feature':float(np.imag(zs[0]*zr[0]-W[0])),
             'wrong_offset_feature':float(np.imag((np.exp(.7j)-1)*W[0])),
             'scope':'record-only joint likelihood; global frequentist moment set; Haar weights are working-prior only'}
    arrays={'theta_grid':fine['theta_grid'],'log_likelihood':fine['log_likelihood'],
            'working_prior_weights':fine['working_prior_weights'],
            'signal_phase_log_likelihoods':fine['signal_phase_log_likelihoods'],
            'reference_phase_log_likelihoods':fine['reference_phase_log_likelihoods'],
            'j0_only_log_likelihood':fine['j0_only_log_likelihood'],
            'ablated_log_likelihoods':np.asarray([fine['ablated_log_likelihoods'][j] for j in scales]),
            'coarse_log_likelihood':coarse['log_likelihood']}
    return summary,arrays
