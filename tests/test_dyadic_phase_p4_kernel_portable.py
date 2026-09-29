"""Deterministic host-C checks only; no generator calls or scientific records."""
import ctypes as ct
from pathlib import Path
import subprocess

import numpy as np
import pytest


@pytest.fixture
def library(tmp_path):
    source = Path(__file__).resolve().parents[1] / "src/dyadic_phase_p4_kernel.c"
    output = tmp_path / "p4-kernel.so"
    subprocess.run(
        ["cc", "-O2", "-std=c11", "-shared", "-fPIC", str(source),
         "-lm", "-o", str(output)],
        check=True, capture_output=True, text=True,
    )
    lib = ct.CDLL(str(output.resolve()))
    real = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
    integer = np.ctypeslib.ndpointer(dtype=np.int64, flags="C_CONTIGUOUS")
    complex_array = np.ctypeslib.ndpointer(dtype=np.complex128, flags="C_CONTIGUOUS")
    counts = np.ctypeslib.ndpointer(dtype=np.uint64, flags="C_CONTIGUOUS")
    lib.p3_local_filter.argtypes = [ct.c_size_t] * 3 + [ct.c_double] * 4 + [real] * 3
    lib.p3_local_filter.restype = ct.c_int
    lib.p3_ket_branch.argtypes = (
        [ct.c_int] * 2 + [ct.c_double] * 4
        + [ct.c_int, complex_array, complex_array, ct.POINTER(ct.c_double)]
    )
    lib.p3_ket_branch.restype = ct.c_int
    lib.p3_generate.argtypes = (
        [ct.c_int] * 5 + [ct.c_double] * 4
        + [real, integer, complex_array, ct.c_void_p, ct.c_void_p,
           real, real, complex_array, counts]
    )
    lib.p3_generate.restype = ct.c_int
    assert Path(lib._name).resolve().parent == tmp_path.resolve()
    return lib


def test_exported_symbols(library):
    for name in ("p3_local_filter", "p3_ket_branch", "p3_generate"):
        assert callable(getattr(library, name))
    # Resolving the generator symbol does not call it or construct an RNG.


@pytest.mark.parametrize("dimension", [2, 128])
@pytest.mark.parametrize("hidden", [0, 1])
def test_branch_matches_kraus_matrix(library, dimension, hidden):
    pd, eta, angle, y = .03, .8, .37, -.19
    initial = np.ascontiguousarray(
        np.exp(.31j * np.arange(dimension)) / np.sqrt(dimension)
    )
    before = initial.copy()
    output = np.full(dimension, complex(np.nan, np.nan), dtype=np.complex128)
    weight = ct.c_double(-1)
    status = library.p3_ket_branch(
        dimension, dimension // 2, pd, eta, angle, y, hidden,
        initial, output, ct.byref(weight),
    )
    assert status == 0
    kraus = (np.array([[0, np.sqrt((1 - eta) * pd)], [0, 0]], complex)
             if hidden else np.array(
                 [[1, np.sqrt(eta * pd) * np.exp(-1j * angle) * y],
                  [0, np.sqrt(1 - pd)]], complex))
    expected = np.kron(kraus, np.eye(dimension // 2)) @ initial
    np.testing.assert_allclose(output, expected, rtol=0, atol=2e-14)
    assert abs(weight.value - np.vdot(expected, expected).real) < 2e-14
    assert np.array_equal(initial, before)


def test_branch_rejects_guarded_arguments_without_writes(library):
    initial = np.zeros(129, dtype=np.complex128)
    for dimension, mask, pd, eta in (
        (129, 64, .03, .8), (2, 0, .03, .8),
        (2, 1, 1., .8), (2, 1, .03, 1.1),
    ):
        output = np.full(129, 7 + 2j, dtype=np.complex128)
        weight = ct.c_double(-1)
        assert library.p3_ket_branch(
            dimension, mask, pd, eta, .37, -.19, 0,
            initial, output, ct.byref(weight),
        ) == 1
        assert np.all(output == 7 + 2j)
        assert weight.value == -1


def density_loglaw(records, phase, eta):
    """Independent two-by-two unitary/Kraus calculation, not Bloch recursion."""
    g, gamma, dt, burn = 1 / np.sqrt(8), 1., .04, 2
    pd = -np.expm1(-gamma * dt)
    h = np.array([[0, np.exp(-1j * phase)], [np.exp(1j * phase), 0]])
    u = np.cos(g * dt / 2) * np.eye(2) - 1j * np.sin(g * dt / 2) * h
    damp = np.diag([1., np.sqrt(1 - pd)])
    loss = np.array([[0, np.sqrt(pd)], [0, 0]])
    hidden = np.sqrt(1 - eta) * loss
    rho = np.diag([1., 0.]).astype(complex)
    loglaw = 0.
    for block in range(2):
        for step in range(burn + records.shape[1]):
            rho = u @ rho @ u.conj().T
            if step < burn:
                rho = damp @ rho @ damp.conj().T + loss @ rho @ loss.conj().T
            else:
                k = damp.astype(complex)
                k[0, 1] = (np.sqrt(eta * pd / dt) * records[block, step - burn]
                           * np.exp(-1j * block * np.pi / 2))
                rho = k @ rho @ k.conj().T + hidden @ rho @ hidden.conj().T
                probability_ratio = np.trace(rho).real
                assert probability_ratio > 0
                loglaw += np.log(probability_ratio)
                rho /= probability_ratio
            rho = u @ rho @ u.conj().T
    return loglaw


@pytest.mark.parametrize("eta", [0., .8, 1.])
def test_filter_matches_density_matrices(library, eta):
    records = np.array([[.03, -.07, .11], [-.05, .02, .09]], dtype=np.float64)
    phases = np.array([0., .37, -1.2], dtype=np.float64)
    before = records.copy()
    output = np.full(3, np.nan)
    assert library.p3_local_filter(
        3, 3, 2, 1 / np.sqrt(8), 1., eta, .04, phases, records, output,
    ) == 0
    expected = np.array([density_loglaw(records, phase, eta) for phase in phases])
    np.testing.assert_allclose(output, expected, rtol=0, atol=3e-13)
    assert np.array_equal(records, before)
    if eta == 0:
        np.testing.assert_allclose(output, 0., rtol=0, atol=3e-13)


def test_filter_rejects_nonfinite_normalization(library):
    phases = np.array([.37])
    records = np.array([[np.nan], [0.]])
    output = np.array([123.])
    assert library.p3_local_filter(
        1, 1, 0, 1 / np.sqrt(8), 1., .8, .04, phases, records, output,
    ) == 1
    assert output[0] == 123.
