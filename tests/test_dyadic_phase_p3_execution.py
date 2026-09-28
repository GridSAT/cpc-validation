"""Deterministic C Kraus prechecks, scripted path replay, and seal blocking."""
import ctypes
import inspect
from pathlib import Path
import subprocess

import numpy as np
import pytest

from src.dyadic_phase_p3 import Bank, bank_step, compile_bank, prepare_bank
from src.dyadic_phase_p3_execution import _engine, _compiled_profile, execute_operational
from src.dyadic_phase_p3_fast import load_filter


@pytest.fixture(scope='module')
def lib(tmp_path_factory):
    path = tmp_path_factory.mktemp('p3-execution-kernel')/'kernel.so'
    source = Path(__file__).resolve().parents[1]/'src/dyadic_phase_p3_kernel.c'
    subprocess.run(['cc', '-O2', '-std=c11', '-shared', '-fPIC', str(source), '-lm', '-o', str(path)], check=True)
    return load_filter(path)


@pytest.mark.parametrize('eta', [0., .8, 1.])
@pytest.mark.parametrize('mask', [1, 2, 4])
def test_hidden_kraus_mixture_is_exact_inefficient_collision(lib, eta, mask):
    D = 8
    v = np.array([1, .2j, -.4, .7j, .3, .6j, -.8, .1j]); v /= np.linalg.norm(v)
    ptr = np.ctypeslib.ndpointer(dtype=np.complex128, flags='C_CONTIGUOUS')
    function = lib.p3_ket_branch
    function.argtypes = [ctypes.c_int]*2+[ctypes.c_double]*4+[ctypes.c_int, ptr, ptr, ctypes.POINTER(ctypes.c_double)]
    mixture = np.zeros((D, D), complex)
    pd, angle, y = .031, .7, -.42
    lower = np.zeros((D, D), complex)
    for k in range(D):
        if not k & mask:
            lower[k, k|mask] = 1
    K0 = np.eye(D)+(np.sqrt(1-pd)-1)*lower.conj().T@lower
    K1 = np.sqrt(pd)*lower
    maps = (K0+np.sqrt(eta)*np.exp(-1j*angle)*y*K1, np.sqrt(1-eta)*K1)
    for hidden in (0, 1):
        out = np.empty_like(v); weight = ctypes.c_double()
        assert function(D, mask, pd, eta, angle, y, hidden, v, out, ctypes.byref(weight)) == 0
        expected = maps[hidden]@v
        np.testing.assert_allclose(out, expected, atol=1e-15)
        assert weight.value == pytest.approx(np.vdot(expected, expected).real, abs=1e-15)
        mixture += np.outer(out, out.conj())
    expected = sum(np.outer(k@v, (k@v).conj()) for k in maps)
    np.testing.assert_allclose(mixture, expected, atol=1e-15)


def test_scripted_nonrandom_bank_path_matches_independent_density_replay(lib):
    # Constant supplied uniforms make a fixed algebraic test path. No PRNG,
    # measurement population, or acceptance records are produced or saved.
    model = Bank(7, 3); steps = 3
    permutations, D = _compiled_profile(model, 'DP-P')
    initial = np.zeros(D, complex); initial[1] = 1
    sig = np.empty((3, 2, steps)); ref = np.empty_like(sig)
    final = np.empty(D, complex); counters = np.empty(8, np.uint64)
    callback_type = ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_void_p)
    fixed = callback_type(lambda _: .125)
    chi = np.array([.23, -.41, .67])
    status = _engine(lib)(0, 3, 8, steps, 0, model.g, 1., 1., .04,
                           chi, permutations, initial, None,
                           ctypes.cast(fixed, ctypes.c_void_p), sig, ref, final, counters)
    assert status == 0
    rho = prepare_bank(model); channels = compile_bank(model)
    for block, command in enumerate((0., np.pi/2)):
        for t in range(steps):
            for j, c in enumerate(channels):
                rho, _ = bank_step(rho, c, sig[j, block, t], .04, 1., command, chi[j])
    np.testing.assert_allclose(np.outer(final, final.conj()), rho[0], atol=1e-13)
    assert counters[0] == 1
    assert counters[1] == counters[2] == 0
    assert counters[3] == 2*3*2*steps


def test_execution_refuses_missing_acceptance_before_any_output(tmp_path):
    out = tmp_path/'records.npz'
    with pytest.raises(FileNotFoundError):
        execute_operational(Bank(7, 3), 'DP-P', 'no-trial', tmp_path/'absent.json',
                             tmp_path/'absent-seal.json', out)
    assert not out.exists()


def test_operational_signature_has_no_semantic_advice_or_seed_override():
    assert set(inspect.signature(execute_operational).parameters) == {
        'model', 'profile', 'trial_id', 'acceptance_path', 'seal_path', 'output_path'}


@pytest.mark.parametrize('failure', ['writable-acceptance', 'writable-seal', 'source',
                                      'acceptance', 'power', 'prechecks', 'missing-H', 'spec'])
def test_seal_rejects_tampered_or_incomplete_prerequisites(tmp_path, failure):
    import json
    from src.dyadic_phase_p3_execution import sha256, verify_execution_seal, FROZEN_SPEC_SHA256
    spec = Path(__file__).resolve().parents[1]/'docs/DYADIC-PHASE-P3-FROZEN-SPEC.md'
    source = tmp_path/'source.py'; source.write_text('immutable source\n')
    acceptance = tmp_path/'acceptance.json'; seal = tmp_path/'seal.json'
    body = {'schema':'cpc-shor-p3-acceptance/1', 'frozen_spec_sha256':FROZEN_SPEC_SHA256,
            'gates':{f'P3-{x}':{'numeric_definition':{'tolerance':1e-9}} for x in 'ABCDEFGH'}}
    if failure == 'missing-H':
        del body['gates']['P3-H']
    if failure == 'spec':
        body['frozen_spec_sha256'] = 'wrong'
    acceptance.write_text(json.dumps(body))
    proof = {'schema':'cpc-shor-p3-source-seal/1', 'frozen_spec_sha256':FROZEN_SPEC_SHA256,
             'frozen_spec_path':str(spec), 'acceptance_sha256':sha256(acceptance),
             'deterministic_prechecks_passed':failure!='prechecks',
             'power_error_analysis_complete':failure!='power',
             'sources':{str(source):sha256(source)}, 'library_path':str(source), 'required_evidence':{}}
    seal.write_text(json.dumps(proof))
    if failure == 'acceptance':
        acceptance.write_text(json.dumps(body)+'\n')
    if failure == 'source':
        source.write_text('changed source\n')
    acceptance.chmod(0o644 if failure=='writable-acceptance' else 0o444)
    seal.chmod(0o644 if failure=='writable-seal' else 0o444)
    with pytest.raises((ValueError, PermissionError)):
        verify_execution_seal(acceptance, seal)
