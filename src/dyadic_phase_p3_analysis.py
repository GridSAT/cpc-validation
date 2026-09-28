"""P3 deterministic finite-record moments and globally calibrated phase sets.

Power/error analysis only: no stochastic execution and no acceptance defaults.
All finite-step outcome moments use exact Gaussian integrals of the P2 CP map.
"""
from __future__ import annotations

import math
import numpy as np
from scipy.linalg import expm

PAIRS = tuple((p, q) for total in range(5) for p in range(total+1)
              for q in (total-p,))


def weighted_maps(phi, g, Gamma, eta, command, chi, dt):
    """Integral dY^k M_dY against the ostensible Gaussian, k=0..4."""
    h = g*np.array([[0, np.exp(-1j*phi)], [np.exp(1j*phi), 0]])
    Q = expm(-1j*h*dt/2)
    K0 = Q@np.diag([1., math.exp(-Gamma*dt/2)])@Q
    K1 = Q@np.array([[0, math.sqrt(-math.expm1(-Gamma*dt))], [0, 0]])@Q
    a, b = np.kron(K0.conj(), K0), np.kron(K1.conj(), K1)
    cross = (np.exp(-1j*(command-chi))*np.kron(K0.conj(), K1)
             + np.exp(1j*(command-chi))*np.kron(K1.conj(), K0))
    return (a+b, math.sqrt(eta*dt)*cross, dt*(a+(1+2*eta)*b),
            3*math.sqrt(eta)*dt**1.5*cross, dt*dt*(3*a+(3+12*eta)*b))


def augmented_map(maps, active):
    result = np.kron(np.eye(len(PAIRS)), maps[0])
    if active is None:
        return result
    for row, (p, q) in enumerate(PAIRS):
        degree = (p, q)[active]
        for k in range(1, degree+1):
            source = (p-k, q) if active == 0 else (p, q-k)
            col = PAIRS.index(source)
            result[4*row:4*row+4, 4*col:4*col+4] += math.comb(degree, k)*maps[k]
    return result


def quadrature_moments(phi, *, g, Gamma, eta, chi, dt, burn, window):
    """Exact E[Re(Z)^p Im(Z)^q], total degree <=4, retaining temporal memory."""
    if (not 0 < dt <= .04 or not 0 <= eta <= 1 or burn < 0 or window <= 0
            or any(abs(x/dt-round(x/dt)) > 1e-7 for x in (burn, window))):
        raise ValueError('invalid integral finite-step schedule')
    state = np.zeros(4*len(PAIRS), complex); state[0] = 1
    for active, command in enumerate((0., math.pi/2)):
        maps = tuple(x/window**k for k, x in enumerate(
            weighted_maps(phi, g, Gamma, eta, command, chi, dt)))
        state = np.linalg.matrix_power(augmented_map(maps, None), round(burn/dt))@state
        state = np.linalg.matrix_power(augmented_map(maps, active), round(window/dt))@state
    trace = np.array([1., 0, 0, 1.])
    raw = {pair: trace@state[4*k:4*k+4] for k, pair in enumerate(PAIRS)}
    if max(abs(v.imag) for v in raw.values()) > 1e-9:
        raise ArithmeticError('nonreal raw moment')
    return {pair: float((-1)**pair[0]*raw[(pair[1], pair[0])].real)
            for pair in PAIRS}


def central_moment(raw, p, q):
    mx, my = raw[(1, 0)], raw[(0, 1)]
    return sum(math.comb(p, a)*math.comb(q, b)*(-mx)**(p-a)*(-my)**(q-b)*raw[(a, b)]
               for a in range(p+1) for b in range(q+1))


def radial_moments(raw):
    return (central_moment(raw, 2, 0)+central_moment(raw, 0, 2),
            central_moment(raw, 4, 0)+2*central_moment(raw, 2, 2)+central_moment(raw, 0, 4))


def uniform_moment_bounds(*, numerical_margin, **settings):
    """Conservative Fourier coefficient sums, uniform over all drive phases.

    Degree of kth output moment is <=k by phase covariance and k insertions
    of the quadrature superoperator. Nine nodes exactly resolve degree four;
    an independent shifted grid checks the finite-dimensional calculation.
    numerical_margin is an explicit absolute allowance, not a stochastic fit.
    """
    if not numerical_margin > 0:
        raise ValueError('positive numerical allowance required')
    phases = 2*np.pi*np.arange(9)/9
    raws = [quadrature_moments(float(phi), **settings) for phi in phases]
    values = np.array([radial_moments(raw) for raw in raws])
    coeff = np.fft.fft(values, axis=0)/9
    mean = np.array([[raw[(1, 0)], raw[(0, 1)]] for raw in raws])
    mean_coeff = np.fft.fft(mean, axis=0)/9
    frequencies = np.fft.fftfreq(9)*9
    errors = []
    for phi in (0.137, .811, 1.971, 3.217, 5.411):
        raw = quadrature_moments(phi, **settings)
        predicted = np.real(np.exp(1j*phi*frequencies)@coeff)
        errors.append(float(np.max(abs(predicted-radial_moments(raw)))))
    # z convention has one common signed amplitude; anisotropy/transients are
    # bounded explicitly instead of assumed absent after burn.
    raw0 = quadrature_moments(0., **settings)
    raw90 = quadrature_moments(np.pi/2, **settings)
    columns = np.array([[raw0[(1, 0)], raw90[(1, 0)]],
                        [raw0[(0, 1)], raw90[(0, 1)]]])
    # chi=0 for model template; known constant chi rotates phi, so uniform bounds
    # apply to unknown transfer without supplying it to inference.
    if settings['chi'] != 0.:
        raise ValueError('use zero-transfer template; uniform phase absorbs transfer')
    amplitude = float(np.trace(columns)/2)
    template_error = float(np.linalg.norm(columns-amplitude*np.eye(2), 2))
    return {'second_moment_upper': float(np.abs(coeff[:, 0]).sum()+numerical_margin),
            'fourth_moment_upper': float(np.abs(coeff[:, 1]).sum()+numerical_margin),
            'signed_amplitude': amplitude,
            'template_error_upper': template_error+numerical_margin,
            'fourier_reconstruction_error': max(errors),
            'numerical_margin': numerical_margin,
            'degree': 4, 'nodes': 9,
            'scope': 'exact finite-step moment algebra with explicit floating-point allowance'}


def _wrapped_interval(center, radius):
    if radius >= .5:
        return [(0., 1.)]
    center %= 1.
    lo, hi = center-radius, center+radius
    if lo < 0:
        return [(0., hi), (lo+1, 1.)]
    if hi > 1:
        return [(0., hi-1), (lo, 1.)]
    return [(lo, hi)]


def _intersect(left, right):
    return sorted((max(a, c), min(b, d)) for a, b in left for c, d in right
                  if max(a, c) <= min(b, d))


def _phase_arc(z, amplitude, radius):
    # Work with the signed model amplitude; the two negative signs cancel in
    # relative phase. A zero observation admits all phases only if the circle
    # of predicted means lies inside the observation disc.
    if amplitude == 0:
        return (0., .5) if abs(z) <= radius else None
    z = complex(z)*np.sign(amplitude); A = abs(amplitude); R = abs(z)
    if R == 0:
        return (0., .5) if A <= radius else None
    threshold = (R*R+A*A-radius*radius)/(2*R*A)
    if threshold > 1:
        return None
    half = .5 if threshold <= -1 else math.acos(threshold)/(2*math.pi)
    return (float(np.angle(z)/(2*math.pi)), half)


def joint_confidence_set(signal_records, reference_records, scales, *, dt,
                         moment_bounds, alpha):
    """Global continuous-circle confidence by simultaneous moment discs.

    Markov on ||Z-EZ||^4, a union bound across 2m outputs, and elimination of
    unknown matched transfers guarantee >=1-alpha coverage under the finite
    model (subject to the declared numerical allowance). All lifts survive.
    This is neither a Bayesian credible set nor a likelihood-grid confidence.
    """
    sig, ref = np.asarray(signal_records), np.asarray(reference_records)
    if (sig.shape != ref.shape or sig.ndim != 3 or sig.shape[0] != len(scales)
            or sig.shape[1] != 2 or sig.shape[2] < 1
            or not np.isfinite(sig).all() or not np.isfinite(ref).all()
            or not scales or len(set(scales)) != len(scales)
            or any(type(j) is not int or not 0 <= j <= 2 for j in scales)
            or not 0 < alpha < 1 or not 0 < dt <= .04
            or not all(math.isfinite(moment_bounds[k]) for k in
                       ('fourth_moment_upper', 'signed_amplitude', 'template_error_upper'))
            or moment_bounds['fourth_moment_upper'] < 0
            or moment_bounds['template_error_upper'] < 0):
        raise ValueError('invalid confidence input')
    window = sig.shape[2]*dt
    def zmean(record):
        means = record.sum(axis=1)/window
        return -means[1]+1j*means[0]
    signals, refs = [zmean(x) for x in sig], [zmean(x) for x in ref]
    radius = (2*len(scales)*moment_bounds['fourth_moment_upper']/alpha)**.25
    radius += moment_bounds['template_error_upper']
    intervals = [(0., 1.)]; arcs = []
    for j, s, r in zip(scales, signals, refs):
        sa = _phase_arc(s, moment_bounds['signed_amplitude'], radius)
        ra = _phase_arc(r, moment_bounds['signed_amplitude'], radius)
        if sa is None or ra is None:
            intervals = []; arcs.append(None); continue
        center, half = sa[0]-ra[0], min(.5, sa[1]+ra[1])
        arcs.append({'scale': j, 'center_cycles': center % 1, 'half_width_cycles': half})
        lifted = []
        for lo, hi in _wrapped_interval(center, half):
            for k in range(2**j):
                lifted.append(((lo+k)/2**j, (hi+k)/2**j))
        intervals = _intersect(intervals, lifted)
    total = sum(b-a for a, b in intervals)
    if not intervals:
        span = 0.
    else:
        gaps = [intervals[k+1][0]-intervals[k][1] for k in range(len(intervals)-1)]
        gaps.append(intervals[0][0]+1-intervals[-1][1])
        span = 1-max(gaps)
    return {'intervals': intervals, 'total_length_cycles': total,
            'minimum_covering_arc_cycles': span, 'empty': not intervals,
            'per_output_radius': radius, 'dyadic_arcs': arcs, 'nominal_coverage': 1-alpha,
            'scope': 'global moment confidence, including all dyadic aliases'}
