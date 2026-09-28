"""Exact quadrature integration and global-set tests; no stochastic records."""
import math
import numpy as np
import pytest
from numpy.polynomial.hermite import hermgauss
from scipy.linalg import expm
from src.dyadic_phase_p3_analysis import (
    PAIRS, quadrature_moments, radial_moments, uniform_moment_bounds,
    joint_confidence_set,
)

SETTINGS = dict(g=1/math.sqrt(8), Gamma=1., eta=.8, chi=0., dt=.02, burn=0., window=.02)


@pytest.mark.parametrize('phi', [0., .83, -math.pi/2])
def test_fourth_moments_against_independent_two_step_gaussian_integration(phi):
    nodes, weights = hermgauss(5); nodes *= math.sqrt(2); weights /= math.sqrt(math.pi)
    h = SETTINGS['g']*np.array([[0, np.exp(-1j*phi)], [np.exp(1j*phi), 0]])
    Q = expm(-1j*h*.01)
    K0 = np.diag([1., math.exp(-.01)])
    K1 = np.array([[0., math.sqrt(-math.expm1(-.02))], [0, 0]])
    raw = {pair: 0. for pair in PAIRS}
    for y0, w0 in zip(nodes, weights):
        for y1, w1 in zip(nodes, weights):
            rho = np.diag([1., 0.]).astype(complex)
            for y, command in ((y0, 0.), (y1, math.pi/2)):
                A = Q@(K0+math.sqrt(.8)*np.exp(-1j*command)*y*K1)@Q
                B = math.sqrt(.2)*Q@K1@Q
                rho = A@rho@A.conj().T+B@rho@B.conj().T
            p = np.trace(rho).real*w0*w1
            x, y = -y1/math.sqrt(.02), y0/math.sqrt(.02)
            for pair in raw:
                raw[pair] += p*x**pair[0]*y**pair[1]
    actual = quadrature_moments(phi, **SETTINGS)
    for pair in PAIRS:
        assert actual[pair] == pytest.approx(raw[pair], rel=2e-12, abs=2e-10)


def test_uniform_fourier_radial_bounds_and_transfer_covariance():
    settings = {**SETTINGS, 'burn': .04, 'window': .12}
    bounds = uniform_moment_bounds(numerical_margin=1e-9, **settings)
    assert bounds['fourier_reconstruction_error'] < 1e-9
    for phi in (.123, .411, 2.23):
        first = quadrature_moments(phi, **{**settings, 'chi': .23})
        second = quadrature_moments(phi+.23, **settings)
        for pair in PAIRS:
            assert first[pair] == pytest.approx(second[pair], abs=1e-10)
        v2, v4 = radial_moments(second)
        assert 0 < v2 <= bounds['second_moment_upper']
        assert 0 < v4 <= bounds['fourth_moment_upper']


def record_from_z(z):
    return np.array([[z.imag*.02], [-z.real*.02]])


def contains(intervals, theta):
    return any(lo-1e-12 <= theta % 1 <= hi+1e-12 for lo, hi in intervals)


@pytest.mark.parametrize('theta', [0., .001, 1/6, 1/3, .5, .999])
def test_global_confidence_retains_wrap_and_resolves_all_lifts(theta):
    scales = (0, 1, 2); chi = .23
    signals = np.array([record_from_z(np.exp(1j*(2*np.pi*2**j*theta+chi))) for j in scales])
    refs = np.array([record_from_z(np.exp(1j*chi)) for j in scales])
    bounds = {'fourth_moment_upper': 1e-8, 'signed_amplitude': 1., 'template_error_upper': 0.}
    full = joint_confidence_set(signals, refs, scales, dt=.02, moment_bounds=bounds, alpha=.05)
    assert contains(full['intervals'], theta)
    assert not contains(full['intervals'], theta+.5)
    assert full['minimum_covering_arc_cycles'] < .02
    alias = joint_confidence_set(signals[1:], refs[1:], (1, 2), dt=.02,
                                 moment_bounds=bounds, alpha=.05)
    assert contains(alias['intervals'], theta)
    assert contains(alias['intervals'], theta+.5)
    assert alias['minimum_covering_arc_cycles'] > .5


def test_phase_blind_confidence_is_full_circle_and_inconsistent_disc_empty():
    records = np.zeros((3, 2, 1))
    bounds = {'fourth_moment_upper': 1., 'signed_amplitude': 0., 'template_error_upper': 0.}
    full = joint_confidence_set(records, records, (0, 1, 2), dt=.02, moment_bounds=bounds, alpha=.05)
    assert full['total_length_cycles'] == pytest.approx(1.)
    bounds = {**bounds, 'fourth_moment_upper': 1e-12, 'signed_amplitude': 1.}
    empty = joint_confidence_set(records, records, (0, 1, 2), dt=.02, moment_bounds=bounds, alpha=.05)
    assert empty['empty'] and empty['intervals'] == []
