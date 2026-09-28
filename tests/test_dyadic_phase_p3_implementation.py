"""Deterministic P3 implementation checks. No random records are generated."""
import inspect
import math

import numpy as np
import pytest
from scipy.linalg import expm
from scipy.special import logsumexp

from src.dyadic_phase_p3 import (
    Bank, bank_step, compile_bank, joint_loglikelihood,
    local_loglikelihood, prepare_bank, reduced_data, reset_probe,
)

FIXTURES = ((7, 3, 6), (7, 2, 3), (5, 2, 4))
SETTINGS = dict(g=1/math.sqrt(8), Gamma=1., eta=.8, dt=.02, burn_steps=2)
RECORDS = np.array([[-.07, .02, .09], [.04, -.03, .01]])


def independent_step(rho, h, jump, dy, dt, eta, command, chi):
    q = expm(-1j*h*dt/2)
    k0 = np.eye(len(h))+(math.exp(-dt/2)-1)*(jump.conj().T@jump)
    k1 = math.sqrt(-math.expm1(-dt))*jump
    if dy is None:
        maps = (q@k0@q, q@k1@q)
    else:
        maps = (q@(k0+math.sqrt(eta/dt)*np.exp(-1j*(command-chi))*dy*k1)@q,
                math.sqrt(1-eta)*q@k1@q)
    return sum(k@rho@k.conj().T for k in maps)


def independent_law(phi, records, chi=0.):
    h = SETTINGS['g']*np.array([[0, np.exp(-1j*phi)], [np.exp(1j*phi), 0]])
    jump = np.array([[0, 1.], [0, 0]])
    rho = np.diag([1., 0.]).astype(complex)
    for block, command in enumerate((0., math.pi/2)):
        for _ in range(SETTINGS['burn_steps']):
            rho = independent_step(rho, h, jump, None, .02, .8, command, chi)
        for dy in records[block]:
            rho = independent_step(rho, h, jump, dy, .02, .8, command, chi)
    return float(np.trace(rho).real)


def projectors(N, a, r):
    d = 1 << (N-1).bit_length()
    for s in range(r):
        v = np.zeros(d, complex)
        for k in range(r):
            v[pow(a, k, N)] = np.exp(-2j*np.pi*s*k/r)/np.sqrt(r)
        yield np.outer(v, v.conj())


@pytest.mark.parametrize('N,a,r', FIXTURES)
def test_full_arithmetic_bank_matches_independent_sector_mixture(N, a, r):
    model = Bank(N, a)
    channels = compile_bank(model)
    rho = prepare_bank(model)
    loglaw = 0.
    for slot, c in enumerate(channels):
        records = RECORDS*(1+.3*slot)
        for block, command in enumerate((0., math.pi/2)):
            for dy in [None]*2+list(records[block]):
                rho, term = bank_step(rho, c, dy, .02, .8, command, .23)
                loglaw += term[0]
    laws = np.array([np.prod([independent_law(2*np.pi*2**j*s/r,
                                            RECORDS*(1+.3*j), .23)
                              for j in range(3)]) for s in range(r)])
    assert math.exp(loglaw) == pytest.approx(laws.mean(), abs=2e-12)
    data = reduced_data(rho, model.d)[0]
    weights = np.array([np.trace(p@data).real for p in projectors(N, a, r)])
    np.testing.assert_allclose(weights, laws/laws.sum(), atol=2e-12)
    assert np.linalg.eigvalsh(rho[0]).min() > -2e-13


@pytest.mark.parametrize('N,a,r', FIXTURES)
def test_dp_s_complete_reset_retains_same_likelihood(N, a, r):
    rho = prepare_bank(Bank(N, a, (0,)))
    total = 0.
    for j in range(3):
        c, = compile_bank(Bank(N, a, (j,)))
        for block, command in enumerate((0., math.pi/2)):
            for dy in [None]*2+list(RECORDS[block]*(1+.3*j)):
                rho, term = bank_step(rho, c, dy, .02, .8, command, .23)
                total += term[0]
        before = reduced_data(rho, model_d := (1 << (N-1).bit_length()))
        rho = reset_probe(rho, model_d)
        np.testing.assert_allclose(reduced_data(rho, model_d), before, atol=1e-14)
    expected = np.mean([np.prod([independent_law(2*np.pi*2**j*s/r,
                                               RECORDS*(1+.3*j), .23)
                                 for j in range(3)]) for s in range(r)])
    assert math.exp(total) == pytest.approx(expected, abs=2e-12)


@pytest.mark.parametrize('phi', [0., .7, -math.pi/2, math.pi/3])
def test_record_only_filter_and_transfer_sign(phi):
    actual = local_loglikelihood(RECORDS, [phi+.23], **SETTINGS)[0]
    assert actual == pytest.approx(math.log(independent_law(phi, RECORDS, .23)), abs=2e-13)


def test_bank_instrument_independent_dense_and_interchannel_commutation():
    model = Bank(7, 3, (0, 1))
    channels = compile_bank(model)
    rho = prepare_bank(model)
    c = channels[1]
    D = model.dimension
    h = np.zeros((D, D), complex)
    h[np.arange(D), c['permutation']] = model.g*c['coefficients']
    jump_front = np.kron(np.array([[0., 1], [0, 0]]), np.eye(D//2))
    jump = jump_front[c['inverse_front']][:, c['inverse_front']]
    expected = independent_step(rho[0], h, jump, .17, .02, .8, .7, .23)
    actual, loglaw = bank_step(rho, c, .17, .02, .8, .7, .23)
    np.testing.assert_allclose(actual[0]*np.exp(loglaw[0]), expected, atol=1e-14)
    first, _ = bank_step(rho, channels[0], -.07, .02, .8, 0., .23)
    first, _ = bank_step(first, channels[1], .17, .02, .8, .7, .23)
    second, _ = bank_step(rho, channels[1], .17, .02, .8, .7, .23)
    second, _ = bank_step(second, channels[0], -.07, .02, .8, 0., .23)
    np.testing.assert_allclose(first, second, atol=1e-14)


@pytest.mark.parametrize('shared', [False, True])
def test_joint_likelihood_ablations_and_j0_independent_recomputation(shared):
    grid = np.array([0., .13, .27, .5, .9])
    nu = np.array([-.7, .4]); weights = np.array([.3, .7])
    sig = np.array([RECORDS, RECORDS*1.7, RECORDS*-.8])
    ref = np.array([RECORDS*2.3, RECORDS*-.4, RECORDS*1.2])
    result = joint_loglikelihood(sig, ref, grid, (0, 1, 2), nu, weights,
                                 shared_nuisance=shared, **SETTINGS)
    f = np.empty((3, len(grid), 2)); rr = np.empty((3, 2))
    for j in range(3):
        for k, chi in enumerate(nu):
            rr[j, k] = independent_law(0., ref[j], chi)
            for q, theta in enumerate(grid):
                f[j, q, k] = independent_law(2*np.pi*2**j*theta, sig[j], chi)
    def expected(keep):
        if shared:
            return np.log(np.sum(weights*rr.prod(axis=0)*f[list(keep)].prod(axis=0), axis=-1))
        return sum(np.log(np.sum(weights*rr[j]*f[j], axis=-1)) if j in keep
                   else np.log(np.sum(weights*rr[j])) for j in range(3))
    np.testing.assert_allclose(result['log_likelihood'], expected([0, 1, 2]), atol=2e-13)
    np.testing.assert_allclose(result['j0_only_log_likelihood'], expected([0]), atol=2e-13)
    for j in (0, 1, 2):
        np.testing.assert_allclose(result['ablated_log_likelihoods'][j],
                                   expected([k for k in range(3) if k != j]), atol=2e-13)
    # Participation checks use all candidate theta values, never the true answer.
    assert all(np.ptp(result['log_likelihood']-result['ablated_log_likelihoods'][j]) > 1e-8
               for j in (1, 2))
    assert 'NOT yet' in result['scope']


def test_shared_calibration_ablation_keeps_all_reference_records():
    args = (np.array([RECORDS, RECORDS*2]), np.array([RECORDS*4, RECORDS*-3]),
            np.arange(12)/12, (0, 1), np.array([-.9, .8]), np.array([.5, .5]))
    common = joint_loglikelihood(*args, shared_nuisance=True, **SETTINGS)
    separate = joint_loglikelihood(*args, shared_nuisance=False, **SETTINGS)
    assert np.max(abs(common['log_likelihood']-separate['log_likelihood'])) > 1e-9


def test_zero_efficiency_flat_joint_law_and_tie():
    settings = {**SETTINGS, 'eta': 0.}
    grid = np.arange(12)/12
    result = joint_loglikelihood(np.array([RECORDS]*3), np.array([RECORDS]*3),
                                 grid, (0, 1, 2), np.array([0.]), np.array([1.]), **settings)
    np.testing.assert_allclose(result['log_likelihood'], 0, atol=1e-12)
    np.testing.assert_allclose(result['working_prior_weights'], 1/12, atol=1e-12)


def test_complete_reset_preserves_complex_coherence():
    v = np.array([1., 2j, -.7, .3j]); v /= np.linalg.norm(v)
    rho = np.outer(v, v.conj())[None]
    before = reduced_data(rho, 2)
    after = reduced_data(reset_probe(rho, 2), 2)
    np.testing.assert_allclose(before, after, atol=1e-15)
    assert abs(before[0, 0, 1].imag) > .1


@pytest.mark.parametrize('function', [Bank, compile_bank, prepare_bank, joint_loglikelihood])
def test_public_boundary_forbids_semantic_advice(function):
    forbidden = {'r', 's', 'order', 'sector', 'truth', 'expected_phase',
                 'factors', 'expected_peaks', 'initial', 'projectors'}
    assert not (set(inspect.signature(function).parameters) & forbidden)
    assert not any(p.kind in (p.VAR_KEYWORD, p.VAR_POSITIONAL)
                   for p in inspect.signature(function).parameters.values())


@pytest.mark.parametrize('scales', [(1, 0), (0, 0), (0, 1, 2, 3), (True,), (3,)])
def test_bad_scale_contract_rejected(scales):
    with pytest.raises(ValueError):
        Bank(7, 3, scales)
