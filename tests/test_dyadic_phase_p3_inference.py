"""Portable inference checks on scripted arrays; no acquisition or acceptance."""
import inspect
import math
from pathlib import Path
import subprocess

import numpy as np
import pytest
from scipy.special import logsumexp

from src.dyadic_phase_p3_analysis import joint_confidence_set
from src.dyadic_phase_p3_fast import load_filter, replay
from src.dyadic_phase_p3_inference import infer_records


@pytest.fixture(scope="module")
def library(tmp_path_factory):
    output = tmp_path_factory.mktemp("p3-inference") / "kernel.so"
    source = Path(__file__).resolve().parents[1] / "src/dyadic_phase_p3_kernel.c"
    subprocess.run(
        ["cc", "-O2", "-std=c11", "-shared", "-fPIC",
         str(source), "-lm", "-o", str(output)],
        check=True,
    )
    return output.resolve()


@pytest.mark.parametrize("eta", [0., .8, 1.])
def test_scripted_record_inference(library, eta):
    t = np.arange(37)
    raw = np.stack([np.sin(t * 1.17), np.cos(t * .91)]) * .2
    signal = np.array([raw, raw * 1.2, -raw])
    reference = np.array([raw * .4, raw * .7, raw * .9])
    before = (signal.copy(), reference.copy())
    scales = (0, 1, 2)
    settings = dict(g=1 / np.sqrt(8), Gamma=1., eta=eta, dt=.04, burn_steps=3)
    bounds = dict(fourth_moment_upper=.001,
                  signed_amplitude=.6 if eta else 0., template_error_upper=1e-9)
    summary, arrays = infer_records(
        signal, reference, scales, library_path=library,
        coarse_grid=16, fine_grid=32, moment_bounds=bounds,
        confidence_alpha=.05, **settings,
    )
    lib = load_filter(library)
    assert Path(lib._name).resolve() == library
    phases = 2 * np.pi * np.arange(32) / 32
    signal_laws = np.array([replay(lib, r, phases, **settings) for r in signal])
    reference_laws = np.array([replay(lib, r, phases, **settings) for r in reference])
    factors = np.array([
        [logsumexp(reference_laws[k] + np.roll(signal_laws[k], -(2**j * q) % 32))
         - logsumexp(reference_laws[k]) for q in range(32)]
        for k, j in enumerate(scales)
    ])
    constant = sum(logsumexp(r) - math.log(32) for r in reference_laws)
    expected = factors.sum(axis=0) + constant
    ablated = np.array([
        np.delete(factors, k, axis=0).sum(axis=0) + constant for k in range(3)
    ])
    for key, value in [
        ("log_likelihood", expected),
        ("ablated_log_likelihoods", ablated),
        ("j0_only_log_likelihood", factors[0] + constant),
    ]:
        np.testing.assert_allclose(arrays[key], value, rtol=0, atol=2e-12)
    assert summary["estimate"] == np.argmax(expected) / 32
    np.testing.assert_allclose(
        arrays["working_prior_weights"], np.exp(expected - logsumexp(expected)),
        rtol=0, atol=2e-12,
    )
    # Integration with the committed confidence implementation, not a coverage claim.
    confidence = joint_confidence_set(
        signal, reference, scales, dt=.04, moment_bounds=bounds, alpha=.05,
    )
    assert summary["confidence"] == confidence
    assert summary["conditional_factor_error"] < 2e-12
    assert summary["j1_j2_half_turn_alias_error"] < 2e-12
    assert summary["identifiable"] == (eta > 0)
    if eta == 0:
        assert np.ptp(arrays["log_likelihood"]) < 2e-12
        np.testing.assert_allclose(arrays["working_prior_weights"], 1 / 32,
                                   rtol=0, atol=2e-12)
        assert confidence["total_length_cycles"] == pytest.approx(1.)
    np.testing.assert_array_equal(signal, before[0])
    np.testing.assert_array_equal(reference, before[1])


def test_record_only_signature():
    assert not set(inspect.signature(infer_records).parameters) & {
        "N", "a", "r", "s", "theta", "sector", "order", "truth", "ket",
        "initial", "factors", "expected_phase", "chi",
    }
