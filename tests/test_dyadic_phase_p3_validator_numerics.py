"""Numerical validator checks only; no historical replay or execution."""
import copy
import math
from pathlib import Path
import subprocess

import numpy as np
import pytest

from src.dyadic_phase_p3_fast import circular_joint, load_filter
from validate_dyadic_p3 import (
    independent_confidence, independent_curves, merge_intervals,
)


@pytest.fixture(scope="module")
def library(tmp_path_factory):
    output = tmp_path_factory.mktemp("p3-validator") / "kernel.so"
    source = Path(__file__).resolve().parents[1] / "src/dyadic_phase_p3_kernel.c"
    subprocess.run(
        ["cc", "-O2", "-std=c11", "-shared", "-fPIC",
         str(source), "-lm", "-o", str(output)],
        check=True,
    )
    lib = load_filter(output)
    assert Path(lib._name).resolve() == output.resolve()
    return lib


@pytest.mark.parametrize("eta", [0., .8, 1.])
def test_scripted_curves_and_ablations(library, eta):
    t = np.arange(37)
    raw = .2 * np.stack([np.sin(1.17 * t), np.cos(.91 * t)])
    signal = np.array([raw, 1.2 * raw, -raw])
    reference = np.array([.4 * raw, .7 * raw, .9 * raw])
    saved = (signal.copy(), reference.copy())
    settings = dict(g=1 / np.sqrt(8), Gamma=1., eta=eta, dt=.04, burn_steps=3)
    before = settings.copy()
    result = independent_curves(library, signal, reference, (0, 1, 2), 32, settings)
    primary = circular_joint(
        library, signal, reference, (0, 1, 2), grid_size=32, **settings,
    )
    for name, expected in [
        ("full", primary["log_likelihood"]),
        ("j0", primary["j0_only_log_likelihood"]),
        ("ablated", np.array([primary["ablated_log_likelihoods"][j] for j in range(3)])),
        ("sl", primary["signal_phase_log_likelihoods"]),
        ("rl", primary["reference_phase_log_likelihoods"]),
    ]:
        np.testing.assert_allclose(result[name], expected, rtol=0, atol=2e-12)
    assert result["full"].shape == result["j0"].shape == (32,)
    assert result["factors"].shape == result["ablated"].shape == (3, 32)
    np.testing.assert_allclose(
        result["full"][None, :] - result["ablated"], result["factors"],
        rtol=0, atol=2e-12,
    )
    if eta == 0:
        assert np.ptp(result["full"]) < 2e-12
    np.testing.assert_array_equal(signal, saved[0])
    np.testing.assert_array_equal(reference, saved[1])
    assert settings == before


@pytest.mark.parametrize("theta", [0., .25, .99])
def test_confidence_against_one_scale_circle_geometry(theta):
    radius = .1
    alpha = .05
    bounds = dict(fourth_moment_upper=alpha * radius**4 / 2,
                  signed_amplitude=1., template_error_upper=0.)
    signal = np.array([np.exp(2j * np.pi * theta)])
    reference = np.array([1. + 0j])
    saved = (signal.copy(), reference.copy(), bounds.copy())
    result = independent_confidence(signal, reference, (0,), bounds, alpha)
    half = math.acos(1 - radius**2 / 2) / math.pi
    lo, hi = theta - half, theta + half
    if lo < 0:
        expected = [[0., hi], [1 + lo, 1.]]
    elif hi > 1:
        expected = [[0., hi - 1], [lo, 1.]]
    else:
        expected = [[lo, hi]]
    np.testing.assert_allclose(result["intervals"], expected, rtol=0, atol=2e-14)
    assert result["span"] == pytest.approx(2 * half, rel=0, abs=2e-14)
    assert result["length"] == pytest.approx(2 * half, rel=0, abs=2e-14)
    assert not result["empty"]
    np.testing.assert_array_equal(signal, saved[0])
    np.testing.assert_array_equal(reference, saved[1])
    assert bounds == saved[2]


def test_confidence_full_circle_and_empty():
    bounds = dict(fourth_moment_upper=.001, signed_amplitude=0.,
                  template_error_upper=0.)
    zero = np.zeros(3, complex)
    full = independent_confidence(zero, zero, (0, 1, 2), bounds, .05)
    assert full == dict(intervals=[[0., 1.]], span=1., length=1., empty=False)
    empty = independent_confidence(np.full(3, 10. + 0j), zero, (0, 1, 2), bounds, .05)
    assert empty == dict(intervals=[], span=0., length=0., empty=True)


def test_interval_union_without_input_mutation():
    intervals = [[.5, .7], [.2, .3], [.1, .2], [.15, .25], [.5, .6]]
    before = copy.deepcopy(intervals)
    assert merge_intervals(intervals) == [[.1, .3], [.5, .7]]
    assert intervals == before
    assert merge_intervals([]) == []
    assert merge_intervals([[0., .2], [.2 + 5e-15, .3]]) == [[0., .3]]
    assert merge_intervals([[0., .2], [.2 + 2e-14, .3]]) == [
        [0., .2], [.2 + 2e-14, .3]
    ]
