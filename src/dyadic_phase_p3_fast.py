"""Explicit accelerated replay; same P3 instrument, no stochastic execution."""
from __future__ import annotations
import ctypes
from pathlib import Path
import math
import numpy as np
from scipy.special import logsumexp


def load_filter(library_path):
    lib = ctypes.CDLL(str(Path(library_path).resolve()))
    pointer = np.ctypeslib.ndpointer(dtype=np.float64, flags='C_CONTIGUOUS')
    lib.p3_local_filter.argtypes = [ctypes.c_size_t]*3+[ctypes.c_double]*4+[pointer]*3
    lib.p3_local_filter.restype = ctypes.c_int
    return lib


def replay(lib, records, phases, *, g, Gamma, eta, dt, burn_steps):
    r = np.ascontiguousarray(records, dtype=float)
    p = np.ascontiguousarray(phases, dtype=float)
    if (r.ndim != 2 or r.shape[0] != 2 or r.shape[1] < 1 or p.ndim != 1
            or len(p) < 1 or not np.isfinite(r).all() or not np.isfinite(p).all()
            or not 0 < dt <= .04 or not 0 <= eta <= 1
            or type(burn_steps) is not int or burn_steps < 0
            or not all(math.isfinite(x) and x > 0 for x in (g, Gamma))):
        raise ValueError('invalid replay inputs')
    out = np.empty(len(p))
    status = lib.p3_local_filter(len(p), r.shape[1], burn_steps, g, Gamma, eta, dt, p, r, out)
    if status or not np.isfinite(out).all():
        raise ArithmeticError('accelerated instrument failure')
    return out


def circular_joint(lib, signal_records, reference_records, scales, *, grid_size,
                   shared_nuisance=False, g, Gamma, eta, dt, burn_steps):
    """Uniform full-circle theta/transfer quadrature with all ablation reports.

    Gauge covariance avoids repeated filters at identical effective phases.
    The prior is independent uniform transfer per path (or one shared transfer).
    Confidence is constructed separately from exact record-moment bounds.
    """
    sig, ref = np.asarray(signal_records), np.asarray(reference_records)
    if (type(grid_size) is not int or not 16 <= grid_size <= 4096
            or grid_size & (grid_size-1) or sig.shape != ref.shape
            or sig.ndim != 3 or sig.shape[0] != len(scales)
            or not scales or len(set(scales)) != len(scales)
            or any(type(j) is not int or not 0 <= j <= 2 for j in scales)):
        raise ValueError('invalid circular grid or channel structure')
    phases = 2*np.pi*np.arange(grid_size)/grid_size
    settings = dict(g=g, Gamma=Gamma, eta=eta, dt=dt, burn_steps=burn_steps)
    sl = np.array([replay(lib, r, phases, **settings) for r in sig])
    rl = np.array([replay(lib, r, phases, **settings) for r in ref])
    indices = np.arange(grid_size)
    factors = np.array([sl[k][(2**j*indices[:, None]+indices[None, :]) % grid_size]
                        for k, j in enumerate(scales)])
    logweight = -math.log(grid_size)

    def combine(keep):
        if shared_nuisance:
            return logsumexp(factors[list(keep)].sum(axis=0)+rl.sum(axis=0), axis=-1)+logweight
        return sum(logsumexp(factors[k]+rl[k], axis=-1)+logweight if k in keep
                   else np.full(grid_size, logsumexp(rl[k])+logweight) for k in range(len(scales)))

    all_slots = tuple(range(len(scales))); full = combine(all_slots)
    return {'theta_grid': indices/grid_size, 'log_likelihood': full,
            'estimate': float(np.argmax(full)/grid_size),
            'signal_phase_log_likelihoods': sl, 'reference_phase_log_likelihoods': rl,
            'ablated_log_likelihoods': {j: combine(tuple(k for k in all_slots if k != slot))
                                      for slot, j in enumerate(scales)},
            'j0_only_log_likelihood': combine(tuple(k for k, j in enumerate(scales) if j == 0)),
            'working_prior_weights': np.exp(full-logsumexp(full)),
            'scope': 'uniform circular candidate/transfer quadrature; confidence is separate'}
