"""Independent exact-matrix regression for C replay, using fixed increments."""
from pathlib import Path
import subprocess
import numpy as np
import pytest
from src.dyadic_phase_p3 import local_loglikelihood, joint_loglikelihood
from src.dyadic_phase_p3_fast import load_filter, replay, circular_joint


@pytest.fixture(scope='module')
def lib(tmp_path_factory):
    path = tmp_path_factory.mktemp('p3-kernel')/'kernel.so'
    source = Path(__file__).resolve().parents[1]/'src/dyadic_phase_p3_kernel.c'
    subprocess.run(['cc', '-O2', '-std=c11', '-shared', '-fPIC', str(source), '-lm', '-o', str(path)], check=True)
    return load_filter(path)


@pytest.mark.parametrize('eta', [0., .8, 1.])
def test_accelerated_filter_matches_density_replay(lib, eta):
    records = np.stack([np.sin(np.arange(67)*1.79), np.cos(np.arange(67)*.73)])*.2
    phases = np.array([0., .31, np.pi/3, -np.pi/2, 5.13])
    settings = dict(g=1/np.sqrt(8), Gamma=1., eta=eta, dt=.04, burn_steps=11)
    expected = local_loglikelihood(records, phases, **settings)
    actual = replay(lib, records, phases, **settings)
    np.testing.assert_allclose(actual, expected, atol=3e-13)


@pytest.mark.parametrize('shared', [False, True])
def test_circular_joint_and_all_ablations_match_generic_filter(lib, shared):
    r = np.stack([np.sin(np.arange(7)*1.79), np.cos(np.arange(7)*.73)])*.2
    sig, ref = np.array([r, r*2, -r]), np.array([r*.7, r*.3, r*1.2])
    settings = dict(g=1/np.sqrt(8), Gamma=1., eta=.8, dt=.04, burn_steps=3)
    fast = circular_joint(lib, sig, ref, (0, 1, 2), grid_size=16,
                          shared_nuisance=shared, **settings)
    slow = joint_loglikelihood(sig, ref, np.arange(16)/16, (0, 1, 2),
                               2*np.pi*np.arange(16)/16, np.ones(16)/16,
                               shared_nuisance=shared, **settings)
    for key in ('log_likelihood', 'j0_only_log_likelihood', 'working_prior_weights'):
        np.testing.assert_allclose(fast[key], slow[key], atol=2e-13)
    for j in (0, 1, 2):
        np.testing.assert_allclose(fast['ablated_log_likelihoods'][j],
                                   slow['ablated_log_likelihoods'][j], atol=2e-13)
