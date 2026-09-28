"""P3 deterministic arithmetic bank and record-only finite-instrument filters.

No random number generation, spectral oracle, acceptance defaults or P4.
The new module reuses the immutable P2 collision convention. Stochastic
execution is separately gated; supplied deterministic increments are not data.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.special import logsumexp

from src.dyadic_phase_instrument import _unitary_half, digest_array
from src.dyadic_phase_probe import Probe, multiplier


@dataclass(frozen=True)
class Bank:
    """Arithmetic-only DP-P input; at most three dyadic signal probes."""

    N: int
    a: int
    scales: tuple[int, ...] = (0, 1, 2)
    g: float = 1 / math.sqrt(8)
    Gamma: float = 1.0

    def __post_init__(self):
        Probe(self.N, self.a, 0, self.g, self.Gamma)
        if (not isinstance(self.scales, tuple) or not 1 <= len(self.scales) <= 3
                or any(type(j) is not int or not 0 <= j <= 2 for j in self.scales)
                or tuple(sorted(set(self.scales))) != self.scales):
            raise ValueError('ordered distinct scales in 0..2 required')

    @property
    def d(self):
        return 1 << (self.N - 1).bit_length()

    @property
    def dimension(self):
        return self.d * 2 ** len(self.scales)


def compile_bank(model: Bank):
    """Monomial local Hamiltonians in probe-major/data-last register order."""
    m, d, D = len(model.scales), model.d, model.dimension
    compiled = []
    for slot, scale in enumerate(model.scales):
        U = multiplier(Probe(model.N, model.a, scale, model.g, model.Gamma)).toarray()
        h = np.zeros((D, D), complex)
        mask = 1 << (m - slot - 1)
        for probes in range(2 ** m):
            other = probes ^ mask
            block = U if probes & mask else U.conj().T
            h[probes*d:(probes+1)*d, other*d:(other+1)*d] = block
        perm = np.argmax(np.abs(h), axis=1)
        coeff = h[np.arange(D), perm]
        front = np.array([k for bit in (0, 1) for k in range(D)
                          if bool((k // d) & mask) == bool(bit)])
        compiled.append({'scale': scale, 'slot': slot, 'permutation': perm,
                         'coefficients': coeff, 'front': front,
                         'inverse_front': np.argsort(front), 'g': model.g,
                         'Gamma': model.Gamma, 'H_hash': digest_array(model.g*h)})
    return tuple(compiled)


def prepare_bank(model: Bank, trajectories: int = 1):
    """Exactly one data |1> preparation; no optional state/sector advice."""
    if type(trajectories) is not int or not 1 <= trajectories <= 64:
        raise ValueError('bounded batch 1..64 required')
    rho = np.zeros((trajectories, model.dimension, model.dimension), complex)
    rho[:, 1, 1] = 1
    return rho


def _parameters(dt, eta, command, chi):
    if (not math.isfinite(dt) or not 0 < dt <= .04
            or not math.isfinite(eta) or not 0 <= eta <= 1
            or not math.isfinite(command) or not math.isfinite(chi)):
        raise ValueError('invalid finite instrument parameters')


def _collision_front(rho, dy, dt, Gamma, eta, angle):
    """Unnormalized CP map; dy=None marginalizes an unobserved outcome."""
    d = rho.shape[-1] // 2
    p = -math.expm1(-Gamma * dt)
    survival = math.exp(-Gamma * dt / 2)
    gg, ge = rho[:, :d, :d], rho[:, :d, d:]
    eg, ee = rho[:, d:, :d], rho[:, d:, d:]
    out = np.empty_like(rho)
    if dy is None:
        out[:, :d, :d] = gg + p * ee
        out[:, :d, d:] = survival * ge
        out[:, d:, :d] = survival * eg
    else:
        increments = np.broadcast_to(np.asarray(dy, float), (len(rho),))
        if not np.isfinite(increments).all():
            raise ValueError('nonfinite record')
        b = math.sqrt(eta * p / dt) * np.exp(-1j * angle) * increments
        out[:, :d, :d] = (gg + b[:, None, None] * eg
                          + b.conj()[:, None, None] * ge
                          + (abs(b)**2 + (1-eta)*p)[:, None, None] * ee)
        out[:, :d, d:] = survival * (ge + b[:, None, None] * ee)
        out[:, d:, :d] = survival * (eg + b.conj()[:, None, None] * ee)
    out[:, d:, d:] = survival**2 * ee
    return out


def bank_step(rho, compiled_channel, dy, dt, eta, command, chi):
    """One signal channel CP step; norm is density relative to Wiener law.

    Normalization is returned separately for likelihood accumulation. A None
    outcome is an averaged channel, never a truth-conditioned burn state.
    """
    _parameters(dt, eta, command, chi)
    c = compiled_channel
    state = _unitary_half(rho, c['permutation'], c['coefficients'], c['g'], dt)
    front, back = c['front'], c['inverse_front']
    state = _collision_front(state[:, front][:, :, front], dy, dt,
                             c['Gamma'], eta, command-chi)
    state = state[:, back][:, :, back]
    state = _unitary_half(state, c['permutation'], c['coefficients'], c['g'], dt)
    norms = np.trace(state, axis1=1, axis2=2)
    if (np.max(abs(norms.imag)) > 1e-10 or not np.isfinite(norms).all()
            or np.min(norms.real) <= 0):
        raise ArithmeticError('invalid finite-instrument probability')
    return state / norms.real[:, None, None], np.log(norms.real)


def reduced_data(rho, data_dimension):
    """Exact partial trace over every signal probe, retaining all coherences."""
    count = rho.shape[-1] // data_dimension
    blocks = rho.reshape(len(rho), count, data_dimension, count, data_dimension)
    return np.einsum('taiaj->tij', blocks)


def reset_probe(rho, data_dimension):
    """Complete unobserved DP-S trace-and-prepare with coupling disconnected."""
    if rho.shape[-2:] != (2*data_dimension, 2*data_dimension):
        raise ValueError('DP-S single-probe dimensions required')
    data = reduced_data(rho, data_dimension)
    out = np.zeros_like(rho)
    out[:, :data_dimension, :data_dimension] = data
    return out


def _sector_compiled(phases, g, Gamma):
    phases = np.asarray(phases, float)
    if phases.ndim != 1 or not np.isfinite(phases).all():
        raise ValueError('finite candidate phase vector required')
    return {'permutation': np.array([1, 0]),
            'coefficients': np.column_stack((np.exp(-1j*phases), np.exp(1j*phases))),
            'g': g, 'Gamma': Gamma, 'front': np.arange(2),
            'inverse_front': np.arange(2)}


def local_loglikelihood(records, phases, *, g, Gamma, eta, dt, burn_steps):
    """Full temporal two-quadrature filter from records only, not state advice.

    phases are full-circle candidate drive phases, not supplied truth labels.
    Constant transfer is absorbed by gauge covariance into the drive phase.
    records shape (2, retained_steps); all burn intervals are marginalized.
    """
    records = np.asarray(records, float)
    if (records.ndim != 2 or records.shape[0] != 2 or records.shape[1] < 1
            or not np.isfinite(records).all() or type(burn_steps) is not int
            or burn_steps < 0 or not all(math.isfinite(x) and x > 0 for x in (g, Gamma))):
        raise ValueError('invalid records, rates or burn count')
    c = _sector_compiled(phases, g, Gamma)
    rho = np.zeros((len(c['coefficients']), 2, 2), complex)
    rho[:, 0, 0] = 1
    loglaw = np.zeros(len(rho))
    for block, command in enumerate((0., math.pi/2)):
        for _ in range(burn_steps):
            rho, _ = bank_step(rho, c, None, dt, eta, command, 0.)
        for dy in records[block]:
            rho, term = bank_step(rho, c, dy, dt, eta, command, 0.)
            loglaw += term
    return loglaw


def joint_loglikelihood(signal_records, reference_records, theta_grid, scales,
                        nuisance_grid, nuisance_weights, *, shared_nuisance=False,
                        g, Gamma, eta, dt, burn_steps):
    """One common-theta likelihood; nuisance weights fixed before records.

    Separate outputs are independent only conditional on theta and transfer.
    shared_nuisance integrates once after multiplying every local law.
    Returns local conditional factors for independent P3-H audit and ablations.
    No operational spectral/order or true-transfer input is accepted.
    """
    sig, ref = np.asarray(signal_records, float), np.asarray(reference_records, float)
    grid, nu = np.asarray(theta_grid, float), np.asarray(nuisance_grid, float)
    w = np.asarray(nuisance_weights, float)
    if (sig.shape != ref.shape or sig.ndim != 3 or sig.shape[0] != len(scales)
            or not scales or len(set(scales)) != len(scales)
            or any(type(j) is not int or not 0 <= j <= 2 for j in scales)
            or grid.ndim != 1 or not len(grid) or not np.isfinite(grid).all()
            or np.any(grid < 0) or np.any(grid >= 1)
            or nu.ndim != 1 or not len(nu) or w.shape != nu.shape
            or not np.isfinite(nu).all() or not np.isfinite(w).all()
            or np.any(w <= 0) or not np.isclose(w.sum(), 1, atol=1e-13, rtol=0)):
        raise ValueError('invalid joint likelihood inputs')
    settings = dict(g=g, Gamma=Gamma, eta=eta, dt=dt, burn_steps=burn_steps)
    signal_factors, reference_factors = [], []
    for j, signal, reference in zip(scales, sig, ref):
        phases = (2*math.pi*2**j*grid[:, None]+nu[None, :]).ravel()
        signal_factors.append(local_loglikelihood(signal, phases, **settings).reshape(len(grid), len(nu)))
        reference_factors.append(local_loglikelihood(reference, nu, **settings))
    signal_factors = np.asarray(signal_factors)
    reference_factors = np.asarray(reference_factors)
    logw = np.log(w)

    def combine(keep):
        # Keep all references in each ablation: withhold only that SIGNAL law.
        # For shared calibration this retains the original calibration evidence.
        if shared_nuisance:
            return logsumexp(logw + reference_factors.sum(axis=0)
                             + signal_factors[list(keep)].sum(axis=0), axis=-1)
        result = np.zeros(len(grid))
        for slot in range(len(scales)):
            local = reference_factors[slot] + logw
            if slot in keep:
                result += logsumexp(local + signal_factors[slot], axis=-1)
            else:
                result += logsumexp(local)
        return result

    all_slots = tuple(range(len(scales)))
    full = combine(all_slots)
    return {'theta_grid': grid.copy(), 'log_likelihood': full,
            'estimate': float(np.min(grid[full == full.max()])),
            'signal_conditional_log_factors': signal_factors,
            'reference_conditional_log_factors': reference_factors,
            'ablated_log_likelihoods': {j: combine(tuple(k for k in all_slots if k != slot))
                                      for slot, j in enumerate(scales)},
            'j0_only_log_likelihood': combine(tuple(k for k, j in enumerate(scales) if j == 0)),
            'working_prior_weights': np.exp(full-logsumexp(full)),
            'scope': 'finite candidate-grid likelihood; NOT yet a calibrated continuous confidence set'}
