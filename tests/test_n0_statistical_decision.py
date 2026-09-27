import math

import pytest

from src.n0_statistics import (
    N0_PHASE_VALIDATION_MULTIPLICITY_RULE,
    N0Preregistration,
    PhaseValidationCell,
    PreregisteredParameter,
    evaluate_preregistered_phase_validation,
    validate_resolved_physical_preregistration,
)


def parameter(
    name,
    value,
    units,
):
    return PreregisteredParameter(
        name=name,
        status="RESOLVED",
        value=value,
        units=units,
    )


def build_plan(
    *,
    alpha=0.05,
    margin=0.50,
    power=0.80,
    minimum_valid=100,
    maximum_invalid=0.10,
    multiplicity_rule=(
        N0_PHASE_VALIDATION_MULTIPLICITY_RULE
    ),
):
    return N0Preregistration(
        preregistration_id=(
            "N0-STATISTICAL-TEST-PLAN-v1"
        ),
        alpha=parameter(
            "alpha",
            alpha,
            "probability",
        ),
        equivalence_margin_rad=parameter(
            "equivalence_margin_rad",
            margin,
            "rad",
        ),
        power_target=parameter(
            "power_target",
            power,
            "probability",
        ),
        minimum_valid_samples=parameter(
            "minimum_valid_samples",
            minimum_valid,
            "count",
        ),
        maximum_invalid_fraction=parameter(
            "maximum_invalid_fraction",
            maximum_invalid,
            "fraction",
        ),
        calibration_gate_id=(
            "TEST-CALIBRATION-GATE-v1"
        ),
        operational_gate_id=(
            "TEST-HELDOUT-VALIDATION-GATE-v1"
        ),
        multiplicity_rule=(
            multiplicity_rule
        ),
    )


def cell(
    *,
    cell_id,
    truth,
    estimate,
    n=1000,
    invalid=0,
    command_phase=0.0,
):
    return PhaseValidationCell(
        cell_id=cell_id,
        command_phase_rad=command_phase,
        truth_phase_rad=truth,
        valid_trial_ids=tuple(
            f"{cell_id}-valid-{index:04d}"
            for index in range(n)
        ),
        estimates_rad=tuple(
            estimate
            for _ in range(n)
        ),
        invalid_trial_ids=tuple(
            f"{cell_id}-invalid-{index:04d}"
            for index in range(invalid)
        ),
    )


def test_resolved_plan_semantics_are_validated():
    plan = build_plan()

    values = (
        validate_resolved_physical_preregistration(
            plan
        )
    )

    assert values["alpha"] == 0.05
    assert (
        values["minimum_valid_samples"]
        == 100
    )


@pytest.mark.parametrize(
    "alpha",
    (
        0.0,
        1.0,
        -0.01,
    ),
)
def test_invalid_alpha_is_rejected(alpha):
    with pytest.raises(
        ValueError,
        match="alpha",
    ):
        validate_resolved_physical_preregistration(
            build_plan(
                alpha=alpha
            )
        )


def test_invalid_equivalence_margin_is_rejected():
    with pytest.raises(
        ValueError,
        match="equivalence_margin_rad",
    ):
        validate_resolved_physical_preregistration(
            build_plan(
                margin=math.pi + 0.01
            )
        )


def test_minimum_valid_samples_must_be_integer():
    with pytest.raises(
        ValueError,
        match="integer",
    ):
        validate_resolved_physical_preregistration(
            build_plan(
                minimum_valid=10.5
            )
        )


def test_multiplicity_rule_is_frozen():
    with pytest.raises(
        ValueError,
        match="multiplicity",
    ):
        validate_resolved_physical_preregistration(
            build_plan(
                multiplicity_rule="NONE"
            )
        )


def test_calibration_and_validation_trials_must_be_disjoint():
    plan = build_plan(
        minimum_valid=2
    )

    validation = PhaseValidationCell(
        cell_id="phase-zero",
        command_phase_rad=0.0,
        truth_phase_rad=0.0,
        valid_trial_ids=(
            "shared-trial",
            "heldout-2",
        ),
        estimates_rad=(
            0.01,
            -0.01,
        ),
        invalid_trial_ids=(),
    )

    with pytest.raises(
        ValueError,
        match="must be disjoint",
    ):
        evaluate_preregistered_phase_validation(
            preregistration=plan,
            cells=(
                validation,
            ),
            calibration_trial_ids=(
                "cal-1",
                "shared-trial",
            ),
        )


def test_nonheldout_partition_is_rejected():
    with pytest.raises(
        ValueError,
        match="held-out",
    ):
        PhaseValidationCell(
            cell_id="bad",
            command_phase_rad=0.0,
            truth_phase_rad=0.0,
            valid_trial_ids=(
                "trial-1",
                "trial-2",
            ),
            estimates_rad=(
                0.0,
                0.0,
            ),
            invalid_trial_ids=(),
            source_partition="calibration",
        )


def test_bonferroni_alpha_is_split_across_cells():
    plan = build_plan(
        margin=1.0
    )

    result = (
        evaluate_preregistered_phase_validation(
            preregistration=plan,
            cells=(
                cell(
                    cell_id="cell-a",
                    truth=0.0,
                    estimate=0.01,
                ),
                cell(
                    cell_id="cell-b",
                    truth=math.pi / 2.0,
                    estimate=(
                        math.pi / 2.0
                        + 0.01
                    ),
                ),
            ),
            calibration_trial_ids=(
                "cal-1",
                "cal-2",
            ),
        )
    )

    assert math.isclose(
        result.per_cell_alpha,
        0.025,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )

    assert math.isclose(
        result.simultaneous_coverage_lower_bound,
        0.95,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )


def test_small_error_cells_establish_equivalence():
    plan = build_plan(
        margin=0.30,
        minimum_valid=100,
    )

    result = (
        evaluate_preregistered_phase_validation(
            preregistration=plan,
            cells=(
                cell(
                    cell_id="phase-zero",
                    truth=0.0,
                    estimate=0.01,
                    n=1000,
                ),
                cell(
                    cell_id="phase-pi2",
                    truth=math.pi / 2.0,
                    estimate=(
                        math.pi / 2.0
                        + 0.01
                    ),
                    n=1000,
                    command_phase=(
                        math.pi / 2.0
                    ),
                ),
            ),
            calibration_trial_ids=(
                "cal-a",
                "cal-b",
            ),
        )
    )

    assert (
        result.status
        == "EQUIVALENCE_ESTABLISHED"
    )

    assert all(
        item.passed
        for item in result.cells
    )

    assert (
        result.physical_claim_permitted
        is False
    )


def test_large_phase_error_fails_equivalence():
    plan = build_plan(
        margin=0.30,
    )

    result = (
        evaluate_preregistered_phase_validation(
            preregistration=plan,
            cells=(
                cell(
                    cell_id="bad-phase",
                    truth=0.0,
                    estimate=0.80,
                    n=1000,
                ),
            ),
            calibration_trial_ids=(
                "cal-a",
            ),
        )
    )

    assert (
        result.status
        == "EQUIVALENCE_NOT_ESTABLISHED"
    )

    assert (
        result.cells[0]
        .equivalence_bound_passed
        is False
    )


def test_minimum_sample_gate_fails_closed():
    plan = build_plan(
        margin=1.0,
        minimum_valid=100,
    )

    result = (
        evaluate_preregistered_phase_validation(
            preregistration=plan,
            cells=(
                cell(
                    cell_id="undersampled",
                    truth=0.0,
                    estimate=0.0,
                    n=99,
                ),
            ),
            calibration_trial_ids=(
                "cal-a",
            ),
        )
    )

    assert (
        result.status
        == "EQUIVALENCE_NOT_ESTABLISHED"
    )

    assert (
        result.cells[0]
        .minimum_valid_samples_passed
        is False
    )


def test_invalid_fraction_gate_fails_closed():
    plan = build_plan(
        margin=1.0,
        minimum_valid=100,
        maximum_invalid=0.10,
    )

    result = (
        evaluate_preregistered_phase_validation(
            preregistration=plan,
            cells=(
                cell(
                    cell_id="too-many-invalid",
                    truth=0.0,
                    estimate=0.0,
                    n=100,
                    invalid=12,
                ),
            ),
            calibration_trial_ids=(
                "cal-a",
            ),
        )
    )

    assert (
        result.status
        == "EQUIVALENCE_NOT_ESTABLISHED"
    )

    assert (
        result.cells[0]
        .invalid_fraction_passed
        is False
    )


def test_wrapped_branch_cut_is_handled():
    plan = build_plan(
        margin=0.30,
    )

    result = (
        evaluate_preregistered_phase_validation(
            preregistration=plan,
            cells=(
                cell(
                    cell_id="branch-cut",
                    truth=(
                        2.0 * math.pi
                        - 0.01
                    ),
                    estimate=0.01,
                    n=1000,
                ),
            ),
            calibration_trial_ids=(
                "cal-a",
            ),
        )
    )

    observed = (
        result.cells[0]
        .mean_absolute_wrapped_error_rad
    )

    assert observed is not None

    assert math.isclose(
        observed,
        0.02,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )


def test_validation_trial_identity_cannot_be_reused_across_cells():
    plan = build_plan(
        minimum_valid=2,
        margin=1.0,
    )

    first = PhaseValidationCell(
        cell_id="first",
        command_phase_rad=0.0,
        truth_phase_rad=0.0,
        valid_trial_ids=(
            "shared",
            "first-only",
        ),
        estimates_rad=(
            0.0,
            0.0,
        ),
        invalid_trial_ids=(),
    )

    second = PhaseValidationCell(
        cell_id="second",
        command_phase_rad=math.pi / 2.0,
        truth_phase_rad=math.pi / 2.0,
        valid_trial_ids=(
            "shared",
            "second-only",
        ),
        estimates_rad=(
            math.pi / 2.0,
            math.pi / 2.0,
        ),
        invalid_trial_ids=(),
    )

    with pytest.raises(
        ValueError,
        match="reused across cells",
    ):
        evaluate_preregistered_phase_validation(
            preregistration=plan,
            cells=(
                first,
                second,
            ),
            calibration_trial_ids=(
                "cal-a",
            ),
        )
