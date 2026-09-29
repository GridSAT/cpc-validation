"""Bounded P4 model/compiler checks only; no native loading or acquisition."""
import numpy as np
import pytest

from src.dyadic_phase_p4_instrument import Bank, compile_bank, _compiled_profile


@pytest.mark.parametrize("N,a", [(2, 1), (5, 2), (7, 3), (15, 2)])
def test_compiled_columns_match_modular_arithmetic(N, a):
    model = Bank(N, a)
    d = 1 << (N - 1).bit_length()
    assert model.d == d
    assert model.dimension == 8 * d
    channels = compile_bank(model)
    assert len(channels) == 3
    for slot, channel in enumerate(channels):
        j = slot
        mask = 1 << (2 - slot)
        c = pow(a, 2**j, N)
        inverse = pow(c, -1, N)
        perm = channel["permutation"]
        assert channel["scale"] == j
        assert channel["slot"] == slot
        np.testing.assert_array_equal(np.sort(perm), np.arange(8 * d))
        np.testing.assert_array_equal(perm[perm], np.arange(8 * d))
        # The stored permutation maps output rows to input columns.
        # Check every input column against the forward arithmetic action.
        for probes in range(8):
            factor = inverse if probes & mask else c
            for y in range(d):
                output_y = factor * y % N if y < N else y
                output_row = (probes ^ mask) * d + output_y
                assert perm[output_row] == probes * d + y
        front = channel["front"]
        np.testing.assert_array_equal(np.sort(front), np.arange(8 * d))
        np.testing.assert_array_equal(
            front[channel["inverse_front"]], np.arange(8 * d)
        )
        assert all(not ((k // d) & mask) for k in front[:4 * d])
        assert all((k // d) & mask for k in front[4 * d:])
        np.testing.assert_array_equal(channel["coefficients"], np.ones(8 * d))
    packed, dimension = _compiled_profile(model, "DP-P")
    assert dimension == 8 * d
    assert packed.dtype == np.int64
    assert packed.flags.c_contiguous
    np.testing.assert_array_equal(
        packed, np.array([channel["permutation"] for channel in channels])
    )


@pytest.mark.parametrize("kwargs", [
    {"N": 1, "a": 1},
    {"N": 16, "a": 3},
    {"N": 15, "a": 3},
    {"N": 7, "a": 3, "scales": (0, 1)},
    {"N": 7, "a": 3, "g": 0.},
])
def test_model_rejects_outside_declared_domain(kwargs):
    with pytest.raises(ValueError):
        Bank(**kwargs)


def test_profile_rejects_sequential_fallback():
    with pytest.raises(ValueError, match="no silent sequential fallback"):
        _compiled_profile(Bank(15, 2), "DP-S")
