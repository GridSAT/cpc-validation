import math

import pytest

from src.n0_statistics import (
    OutcomeCounts,
    PreregisteredParameter,
    UNRESOLVED_PHYSICAL_PARAMETER,
    build_unresolved_physical_preregistration,
    circular_bias,
    circular_dispersion,
    circular_mean,
    sample_covariance,
    summarize_phase_estimates,
    wrap_phase_error,
)


def test_wrapped_phase_error_handles_branch_cut():
    error = wrap_phase_error(
        0.05,
        2.0 * math.pi - 0.05,
    )

    assert math.isclose(
        error,
        0.10,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )


def test_wrapped_phase_error_is_signed():
    error = wrap_phase_error(
        0.9,
        1.0,
    )

    assert math.isclose(
        error,
        -0.1,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )


def test_circular_mean_handles_zero_boundary():
    mean = circular_mean(
        (
            2.0 * math.pi - 0.1,
            0.1,
        )
    )

    assert (
        min(
            abs(mean),
            abs(
                mean
                - 2.0 * math.pi
            ),
        )
        <= 1.0e-12
    )


def test_circular_bias_matches_truth():
    bias = circular_bias(
        estimates_rad=(
            0.1,
            0.2,
            0.3,
        ),
        truth_rad=0.2,
    )

    assert abs(
        bias
    ) <= 1.0e-12


def test_identical_phases_have_zero_dispersion():
    dispersion = circular_dispersion(
        (
            0.4,
            0.4,
            0.4,
        )
    )

    assert abs(
        dispersion
    ) <= 1.0e-15


def test_opposed_phases_have_high_dispersion():
    dispersion = circular_dispersion(
        (
            0.0,
            math.pi,
        )
    )

    assert math.isclose(
        dispersion,
        1.0,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )


def test_sample_covariance_known_result():
    covariance = sample_covariance(
        (
            1.0,
            2.0,
            3.0,
        ),
        (
            2.0,
            4.0,
            6.0,
        ),
    )

    assert math.isclose(
        covariance,
        2.0,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )


def test_outcome_counts_total_and_invalid_fraction():
    counts = OutcomeCounts(
        correct=10,
        wrong=2,
        abstained=3,
        invalid=5,
    )

    assert counts.total == 20
    assert counts.valid_decisions == 12

    assert math.isclose(
        counts.invalid_fraction,
        0.25,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )


def test_negative_outcome_count_is_rejected():
    with pytest.raises(
        ValueError,
        match="non-negative",
    ):
        OutcomeCounts(
            correct=-1,
            wrong=0,
            abstained=0,
            invalid=0,
        )


def test_resolved_parameter_requires_value():
    with pytest.raises(
        ValueError,
        match="requires a value",
    ):
        PreregisteredParameter(
            name="alpha",
            status="RESOLVED",
            units="probability",
        )


def test_unresolved_parameter_rejects_value():
    with pytest.raises(
        ValueError,
        match="must not have a value",
    ):
        PreregisteredParameter(
            name="alpha",
            status=(
                UNRESOLVED_PHYSICAL_PARAMETER
            ),
            value=0.05,
            units="probability",
        )


def test_default_physical_preregistration_is_unresolved():
    preregistration = (
        build_unresolved_physical_preregistration()
    )

    assert not (
        preregistration
        .is_complete_for_physical_decision
    )

    assert set(
        preregistration.unresolved_parameters
    ) == {
        "alpha",
        "equivalence_margin_rad",
        "power_target",
        "minimum_valid_samples",
        "maximum_invalid_fraction",
    }


def test_unresolved_physical_preregistration_blocks_pass():
    preregistration = (
        build_unresolved_physical_preregistration()
    )

    with pytest.raises(
        RuntimeError,
        match="physical PASS blocked",
    ):
        preregistration.require_complete_for_physical_pass()


def test_phase_summary_reports_expected_bias():
    summary = summarize_phase_estimates(
        estimates_rad=(
            0.9,
            1.0,
            1.1,
        ),
        truth_rad=1.0,
    )

    assert summary.count == 3

    assert abs(
        summary.circular_bias_rad
    ) <= 1.0e-12

    assert (
        summary.mean_absolute_wrapped_error_rad
        > 0.0
    )


def test_phase_summary_crosses_zero_boundary_correctly():
    summary = summarize_phase_estimates(
        estimates_rad=(
            2.0 * math.pi - 0.05,
            0.0,
            0.05,
        ),
        truth_rad=0.0,
    )

    assert abs(
        summary.circular_bias_rad
    ) <= 1.0e-12

    assert (
        summary.mean_absolute_wrapped_error_rad
        < 0.04
    )
