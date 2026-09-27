from __future__ import annotations

import math
from dataclasses import dataclass


N0_STATISTICS_SCHEMA = "cpc.shor.n0.statistics.v1"

UNRESOLVED_PHYSICAL_PARAMETER = "UNRESOLVED_PHYSICAL_PARAMETER"

PREREGISTRATION_PARAMETER_STATUS = (
    "RESOLVED",
    "UNRESOLVED_PHYSICAL_PARAMETER",
)


def wrap_phase_error(
    estimate_rad: float,
    truth_rad: float,
) -> float:
    for name, value in (
        ("estimate_rad", estimate_rad),
        ("truth_rad", truth_rad),
    ):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
        ):
            raise ValueError(
                f"{name} must be finite"
            )

    error = (
        float(estimate_rad)
        - float(truth_rad)
        + math.pi
    ) % (
        2.0 * math.pi
    ) - math.pi

    # Canonicalize the branch endpoint.
    if math.isclose(
        error,
        -math.pi,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    ):
        return math.pi

    return error


def circular_mean(
    phases_rad: tuple[float, ...],
) -> float:
    if not phases_rad:
        raise ValueError(
            "phases_rad must not be empty"
        )

    if any(
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(value)
        for value in phases_rad
    ):
        raise ValueError(
            "phases_rad must contain finite numbers"
        )

    s = sum(
        math.sin(value)
        for value in phases_rad
    )

    c = sum(
        math.cos(value)
        for value in phases_rad
    )

    if (
        abs(s) <= 1.0e-15
        and abs(c) <= 1.0e-15
    ):
        raise ValueError(
            "circular mean is undefined"
        )

    mean = math.atan2(
        s,
        c,
    )

    if mean < 0.0:
        mean += 2.0 * math.pi

    return mean


def circular_bias(
    *,
    estimates_rad: tuple[float, ...],
    truth_rad: float,
) -> float:
    return wrap_phase_error(
        circular_mean(
            estimates_rad
        ),
        truth_rad,
    )


def circular_resultant_length(
    phases_rad: tuple[float, ...],
) -> float:
    if not phases_rad:
        raise ValueError(
            "phases_rad must not be empty"
        )

    s = sum(
        math.sin(value)
        for value in phases_rad
    )

    c = sum(
        math.cos(value)
        for value in phases_rad
    )

    n = len(
        phases_rad
    )

    return (
        math.sqrt(
            s * s
            + c * c
        )
        / n
    )


def circular_dispersion(
    phases_rad: tuple[float, ...],
) -> float:
    return (
        1.0
        - circular_resultant_length(
            phases_rad
        )
    )


def sample_covariance(
    first: tuple[float, ...],
    second: tuple[float, ...],
) -> float:
    if len(first) != len(second):
        raise ValueError(
            "covariance vectors must have equal length"
        )

    if len(first) < 2:
        raise ValueError(
            "covariance requires at least two samples"
        )

    if any(
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(value)
        for value in first + second
    ):
        raise ValueError(
            "covariance inputs must be finite numbers"
        )

    mean_first = sum(
        first
    ) / len(first)

    mean_second = sum(
        second
    ) / len(second)

    return (
        sum(
            (
                x - mean_first
            )
            * (
                y - mean_second
            )
            for x, y in zip(
                first,
                second,
            )
        )
        / (
            len(first)
            - 1
        )
    )


@dataclass(frozen=True)
class OutcomeCounts:
    correct: int
    wrong: int
    abstained: int
    invalid: int

    def __post_init__(self) -> None:
        for name, value in (
            ("correct", self.correct),
            ("wrong", self.wrong),
            ("abstained", self.abstained),
            ("invalid", self.invalid),
        ):
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
            ):
                raise ValueError(
                    f"{name} must be a non-negative integer"
                )

    @property
    def total(self) -> int:
        return (
            self.correct
            + self.wrong
            + self.abstained
            + self.invalid
        )

    @property
    def valid_decisions(self) -> int:
        return (
            self.correct
            + self.wrong
        )

    @property
    def invalid_fraction(self) -> float:
        if self.total == 0:
            return 0.0

        return (
            self.invalid
            / self.total
        )


@dataclass(frozen=True)
class PreregisteredParameter:
    name: str
    status: str

    value: float | int | None = None
    units: str = "dimensionless"

    def __post_init__(self) -> None:
        if (
            not isinstance(self.name, str)
            or not self.name
        ):
            raise ValueError(
                "name must be a non-empty string"
            )

        if self.status not in (
            PREREGISTRATION_PARAMETER_STATUS
        ):
            raise ValueError(
                "unknown preregistration parameter status"
            )

        if (
            not isinstance(self.units, str)
            or not self.units
        ):
            raise ValueError(
                "units must be a non-empty string"
            )

        if self.status == "RESOLVED":
            if self.value is None:
                raise ValueError(
                    "resolved parameter requires a value"
                )

            if (
                not isinstance(
                    self.value,
                    (int, float),
                )
                or isinstance(
                    self.value,
                    bool,
                )
                or not math.isfinite(
                    float(self.value)
                )
            ):
                raise ValueError(
                    "resolved parameter value must be finite"
                )

        if (
            self.status
            == UNRESOLVED_PHYSICAL_PARAMETER
            and self.value is not None
        ):
            raise ValueError(
                "unresolved physical parameter must not have a value"
            )


@dataclass(frozen=True)
class N0Preregistration:
    preregistration_id: str

    alpha: PreregisteredParameter
    equivalence_margin_rad: PreregisteredParameter
    power_target: PreregisteredParameter
    minimum_valid_samples: PreregisteredParameter
    maximum_invalid_fraction: PreregisteredParameter

    calibration_gate_id: str
    operational_gate_id: str
    multiplicity_rule: str

    def __post_init__(self) -> None:
        for name, value in (
            (
                "preregistration_id",
                self.preregistration_id,
            ),
            (
                "calibration_gate_id",
                self.calibration_gate_id,
            ),
            (
                "operational_gate_id",
                self.operational_gate_id,
            ),
            (
                "multiplicity_rule",
                self.multiplicity_rule,
            ),
        ):
            if (
                not isinstance(value, str)
                or not value
            ):
                raise ValueError(
                    f"{name} must be a non-empty string"
                )

    @property
    def schema(self) -> str:
        return N0_STATISTICS_SCHEMA

    @property
    def required_parameters(
        self,
    ) -> tuple[PreregisteredParameter, ...]:
        return (
            self.alpha,
            self.equivalence_margin_rad,
            self.power_target,
            self.minimum_valid_samples,
            self.maximum_invalid_fraction,
        )

    @property
    def unresolved_parameters(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            parameter.name
            for parameter in self.required_parameters
            if (
                parameter.status
                == UNRESOLVED_PHYSICAL_PARAMETER
            )
        )

    @property
    def is_complete_for_physical_decision(
        self,
    ) -> bool:
        return not self.unresolved_parameters

    def require_complete_for_physical_pass(
        self,
    ) -> None:
        unresolved = (
            self.unresolved_parameters
        )

        if unresolved:
            raise RuntimeError(
                "physical PASS blocked by unresolved "
                "preregistered parameter(s): "
                + ", ".join(unresolved)
            )


@dataclass(frozen=True)
class PhaseAnalysisSummary:
    count: int
    circular_mean_rad: float
    circular_bias_rad: float
    circular_dispersion: float
    mean_absolute_wrapped_error_rad: float

    def __post_init__(self) -> None:
        if (
            not isinstance(self.count, int)
            or isinstance(self.count, bool)
            or self.count <= 0
        ):
            raise ValueError(
                "count must be a positive integer"
            )


def summarize_phase_estimates(
    *,
    estimates_rad: tuple[float, ...],
    truth_rad: float,
) -> PhaseAnalysisSummary:
    if not estimates_rad:
        raise ValueError(
            "estimates_rad must not be empty"
        )

    mean = circular_mean(
        estimates_rad
    )

    errors = tuple(
        wrap_phase_error(
            estimate,
            truth_rad,
        )
        for estimate in estimates_rad
    )

    return PhaseAnalysisSummary(
        count=len(
            estimates_rad
        ),
        circular_mean_rad=mean,
        circular_bias_rad=wrap_phase_error(
            mean,
            truth_rad,
        ),
        circular_dispersion=(
            circular_dispersion(
                estimates_rad
            )
        ),
        mean_absolute_wrapped_error_rad=(
            sum(
                abs(error)
                for error in errors
            )
            / len(errors)
        ),
    )


def build_unresolved_physical_preregistration(
) -> N0Preregistration:
    unresolved = (
        UNRESOLVED_PHYSICAL_PARAMETER
    )

    return N0Preregistration(
        preregistration_id=(
            "CPC-SHOR-N0-PHYSICAL-PREREGISTRATION-v1"
        ),
        alpha=PreregisteredParameter(
            name="alpha",
            status=unresolved,
            units="probability",
        ),
        equivalence_margin_rad=PreregisteredParameter(
            name="equivalence_margin_rad",
            status=unresolved,
            units="rad",
        ),
        power_target=PreregisteredParameter(
            name="power_target",
            status=unresolved,
            units="probability",
        ),
        minimum_valid_samples=PreregisteredParameter(
            name="minimum_valid_samples",
            status=unresolved,
            units="count",
        ),
        maximum_invalid_fraction=PreregisteredParameter(
            name="maximum_invalid_fraction",
            status=unresolved,
            units="fraction",
        ),
        calibration_gate_id=(
            "UNRESOLVED-PHYSICAL-CALIBRATION-GATE"
        ),
        operational_gate_id=(
            "UNRESOLVED-PHYSICAL-OPERATIONAL-GATE"
        ),
        multiplicity_rule=(
            "UNRESOLVED-PHYSICAL-MULTIPLICITY-RULE"
        ),
    )


# ----------------------------------------------------------------------
# Preregistered held-out phase-equivalence validation.
#
# This layer is intentionally downstream of truth-blind reduction.
# It establishes a statistical equivalence result only. It does not
# itself authorize any physical/native CPC claim.
# ----------------------------------------------------------------------

N0_PHASE_VALIDATION_SCHEMA = (
    "cpc.shor.n0.phase-validation.v1"
)

N0_PHASE_VALIDATION_MULTIPLICITY_RULE = (
    "BONFERRONI_PER_PHASE_HOEFFDING_V1"
)

N0_HELDOUT_VALIDATION_PARTITION = (
    "heldout_validation"
)

N0_PHASE_VALIDATION_STATUSES = (
    "EQUIVALENCE_ESTABLISHED",
    "EQUIVALENCE_NOT_ESTABLISHED",
)


def _require_probability(
    value: float,
    name: str,
    *,
    allow_zero: bool = False,
) -> float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(float(value))
    ):
        raise ValueError(
            f"{name} must be finite"
        )

    result = float(value)

    lower_ok = (
        result >= 0.0
        if allow_zero
        else result > 0.0
    )

    if not lower_ok or result >= 1.0:
        relation = "[0, 1)" if allow_zero else "(0, 1)"
        raise ValueError(
            f"{name} must lie in {relation}"
        )

    return result


def _resolved_parameter_value(
    parameter: PreregisteredParameter,
) -> float | int:
    if (
        parameter.status != "RESOLVED"
        or parameter.value is None
    ):
        raise RuntimeError(
            "physical statistical decision requires resolved "
            f"parameter: {parameter.name}"
        )

    return parameter.value


def validate_resolved_physical_preregistration(
    preregistration: N0Preregistration,
) -> dict[str, float | int]:
    preregistration.require_complete_for_physical_pass()

    alpha = _require_probability(
        float(
            _resolved_parameter_value(
                preregistration.alpha
            )
        ),
        "alpha",
    )

    power_target = _require_probability(
        float(
            _resolved_parameter_value(
                preregistration.power_target
            )
        ),
        "power_target",
    )

    maximum_invalid_fraction = (
        _require_probability(
            float(
                _resolved_parameter_value(
                    preregistration.maximum_invalid_fraction
                )
            ),
            "maximum_invalid_fraction",
            allow_zero=True,
        )
    )

    margin = float(
        _resolved_parameter_value(
            preregistration.equivalence_margin_rad
        )
    )

    if (
        not math.isfinite(margin)
        or margin <= 0.0
        or margin > math.pi
    ):
        raise ValueError(
            "equivalence_margin_rad must lie in (0, pi]"
        )

    minimum_value = _resolved_parameter_value(
        preregistration.minimum_valid_samples
    )

    if (
        not isinstance(minimum_value, int)
        or isinstance(minimum_value, bool)
        or minimum_value < 2
    ):
        raise ValueError(
            "minimum_valid_samples must be an integer >= 2"
        )

    if (
        preregistration.multiplicity_rule
        != N0_PHASE_VALIDATION_MULTIPLICITY_RULE
    ):
        raise ValueError(
            "unsupported multiplicity rule"
        )

    if preregistration.calibration_gate_id.startswith(
        "UNRESOLVED"
    ):
        raise ValueError(
            "calibration gate must be resolved"
        )

    if preregistration.operational_gate_id.startswith(
        "UNRESOLVED"
    ):
        raise ValueError(
            "operational gate must be resolved"
        )

    return {
        "alpha": alpha,
        "equivalence_margin_rad": margin,
        "power_target": power_target,
        "minimum_valid_samples": minimum_value,
        "maximum_invalid_fraction": (
            maximum_invalid_fraction
        ),
    }


@dataclass(frozen=True)
class PhaseValidationCell:
    cell_id: str

    command_phase_rad: float
    truth_phase_rad: float

    valid_trial_ids: tuple[str, ...]
    estimates_rad: tuple[float, ...]

    invalid_trial_ids: tuple[str, ...]

    source_partition: str = (
        N0_HELDOUT_VALIDATION_PARTITION
    )

    def __post_init__(self) -> None:
        if (
            not isinstance(self.cell_id, str)
            or not self.cell_id
        ):
            raise ValueError(
                "cell_id must be a non-empty string"
            )

        for name, value in (
            (
                "command_phase_rad",
                self.command_phase_rad,
            ),
            (
                "truth_phase_rad",
                self.truth_phase_rad,
            ),
        ):
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(float(value))
            ):
                raise ValueError(
                    f"{name} must be finite"
                )

        if self.source_partition != (
            N0_HELDOUT_VALIDATION_PARTITION
        ):
            raise ValueError(
                "phase validation cells must come from "
                "the held-out validation partition"
            )

        if len(self.valid_trial_ids) != len(
            self.estimates_rad
        ):
            raise ValueError(
                "valid trial IDs must align one-to-one "
                "with phase estimates"
            )

        all_ids = (
            self.valid_trial_ids
            + self.invalid_trial_ids
        )

        if any(
            not isinstance(value, str)
            or not value
            for value in all_ids
        ):
            raise ValueError(
                "trial IDs must be non-empty strings"
            )

        if len(set(all_ids)) != len(all_ids):
            raise ValueError(
                "phase validation trial IDs must be unique"
            )

        if any(
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(float(value))
            for value in self.estimates_rad
        ):
            raise ValueError(
                "phase estimates must be finite"
            )

    @property
    def valid_count(self) -> int:
        return len(
            self.estimates_rad
        )

    @property
    def invalid_count(self) -> int:
        return len(
            self.invalid_trial_ids
        )

    @property
    def total_count(self) -> int:
        return (
            self.valid_count
            + self.invalid_count
        )

    @property
    def invalid_fraction(self) -> float:
        if self.total_count == 0:
            return 1.0

        return (
            self.invalid_count
            / self.total_count
        )

    @property
    def all_trial_ids(self) -> tuple[str, ...]:
        return (
            self.valid_trial_ids
            + self.invalid_trial_ids
        )


@dataclass(frozen=True)
class PhaseCellValidationResult:
    cell_id: str
    command_phase_rad: float
    truth_phase_rad: float

    valid_count: int
    invalid_count: int
    invalid_fraction: float

    mean_absolute_wrapped_error_rad: float | None
    upper_confidence_bound_rad: float | None

    per_cell_alpha: float
    equivalence_margin_rad: float

    minimum_valid_samples_passed: bool
    invalid_fraction_passed: bool
    equivalence_bound_passed: bool

    passed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "cell_id": self.cell_id,
            "command_phase_rad": (
                self.command_phase_rad
            ),
            "truth_phase_rad": (
                self.truth_phase_rad
            ),
            "valid_count": self.valid_count,
            "invalid_count": self.invalid_count,
            "invalid_fraction": (
                self.invalid_fraction
            ),
            "mean_absolute_wrapped_error_rad": (
                self.mean_absolute_wrapped_error_rad
            ),
            "upper_confidence_bound_rad": (
                self.upper_confidence_bound_rad
            ),
            "per_cell_alpha": (
                self.per_cell_alpha
            ),
            "equivalence_margin_rad": (
                self.equivalence_margin_rad
            ),
            "minimum_valid_samples_passed": (
                self.minimum_valid_samples_passed
            ),
            "invalid_fraction_passed": (
                self.invalid_fraction_passed
            ),
            "equivalence_bound_passed": (
                self.equivalence_bound_passed
            ),
            "passed": self.passed,
        }


@dataclass(frozen=True)
class N0PhaseValidationDecision:
    preregistration_id: str

    familywise_alpha: float
    simultaneous_coverage_lower_bound: float
    per_cell_alpha: float

    multiplicity_rule: str

    cells: tuple[
        PhaseCellValidationResult,
        ...
    ]

    status: str

    physical_claim_permitted: bool = False

    def __post_init__(self) -> None:
        if self.status not in (
            N0_PHASE_VALIDATION_STATUSES
        ):
            raise ValueError(
                "unknown phase-validation status"
            )

        if self.physical_claim_permitted is not False:
            raise ValueError(
                "statistical validation alone cannot "
                "authorize a physical claim"
            )

    @property
    def schema(self) -> str:
        return (
            N0_PHASE_VALIDATION_SCHEMA
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "preregistration_id": (
                self.preregistration_id
            ),
            "familywise_alpha": (
                self.familywise_alpha
            ),
            "simultaneous_coverage_lower_bound": (
                self.simultaneous_coverage_lower_bound
            ),
            "per_cell_alpha": (
                self.per_cell_alpha
            ),
            "multiplicity_rule": (
                self.multiplicity_rule
            ),
            "cells": [
                cell.to_dict()
                for cell in self.cells
            ],
            "status": self.status,
            "physical_claim_permitted": (
                self.physical_claim_permitted
            ),
        }


def evaluate_preregistered_phase_validation(
    *,
    preregistration: N0Preregistration,
    cells: tuple[
        PhaseValidationCell,
        ...
    ],
    calibration_trial_ids: tuple[str, ...],
) -> N0PhaseValidationDecision:
    """
    Distribution-free finite-sample phase-equivalence gate.

    For each preregistered held-out phase cell, Xi is the absolute
    wrapped phase error and therefore lies in [0, pi].  A one-sided
    Hoeffding upper confidence bound is constructed for E[Xi].
    Bonferroni allocation gives simultaneous family-wise coverage of
    at least 1 - alpha across all phase cells.

    This is a statistical equivalence result only.  Physical evidence
    provenance and claim authorization are separate gates.
    """

    plan = (
        validate_resolved_physical_preregistration(
            preregistration
        )
    )

    if not cells:
        raise ValueError(
            "phase validation requires at least one cell"
        )

    cell_ids = tuple(
        cell.cell_id
        for cell in cells
    )

    if len(set(cell_ids)) != len(cell_ids):
        raise ValueError(
            "phase validation cell IDs must be unique"
        )

    if not calibration_trial_ids:
        raise ValueError(
            "calibration trial IDs must not be empty"
        )

    if any(
        not isinstance(value, str)
        or not value
        for value in calibration_trial_ids
    ):
        raise ValueError(
            "calibration trial IDs must be non-empty strings"
        )

    if (
        len(set(calibration_trial_ids))
        != len(calibration_trial_ids)
    ):
        raise ValueError(
            "calibration trial IDs must be unique"
        )

    validation_trial_ids = tuple(
        trial_id
        for cell in cells
        for trial_id in cell.all_trial_ids
    )

    if (
        len(set(validation_trial_ids))
        != len(validation_trial_ids)
    ):
        raise ValueError(
            "validation trial identity reused across cells"
        )

    overlap = (
        set(calibration_trial_ids)
        & set(validation_trial_ids)
    )

    if overlap:
        raise ValueError(
            "calibration and held-out validation "
            "trial identities must be disjoint"
        )

    alpha = float(
        plan["alpha"]
    )

    margin = float(
        plan[
            "equivalence_margin_rad"
        ]
    )

    minimum_valid = int(
        plan[
            "minimum_valid_samples"
        ]
    )

    maximum_invalid = float(
        plan[
            "maximum_invalid_fraction"
        ]
    )

    per_cell_alpha = (
        alpha
        / len(cells)
    )

    results: list[
        PhaseCellValidationResult
    ] = []

    for cell in sorted(
        cells,
        key=lambda item: item.cell_id,
    ):
        minimum_pass = (
            cell.valid_count
            >= minimum_valid
        )

        invalid_pass = (
            cell.invalid_fraction
            <= maximum_invalid
        )

        if cell.valid_count == 0:
            mean_error = None
            upper_bound = None
            equivalence_pass = False
        else:
            absolute_errors = tuple(
                abs(
                    wrap_phase_error(
                        estimate,
                        cell.truth_phase_rad,
                    )
                )
                for estimate
                in cell.estimates_rad
            )

            mean_error = (
                sum(absolute_errors)
                / len(absolute_errors)
            )

            hoeffding_radius = (
                math.pi
                * math.sqrt(
                    math.log(
                        1.0
                        / per_cell_alpha
                    )
                    / (
                        2.0
                        * cell.valid_count
                    )
                )
            )

            upper_bound = min(
                math.pi,
                mean_error
                + hoeffding_radius,
            )

            equivalence_pass = (
                upper_bound
                <= margin
            )

        passed = (
            minimum_pass
            and invalid_pass
            and equivalence_pass
        )

        results.append(
            PhaseCellValidationResult(
                cell_id=cell.cell_id,
                command_phase_rad=(
                    cell.command_phase_rad
                ),
                truth_phase_rad=(
                    cell.truth_phase_rad
                ),
                valid_count=(
                    cell.valid_count
                ),
                invalid_count=(
                    cell.invalid_count
                ),
                invalid_fraction=(
                    cell.invalid_fraction
                ),
                mean_absolute_wrapped_error_rad=(
                    mean_error
                ),
                upper_confidence_bound_rad=(
                    upper_bound
                ),
                per_cell_alpha=(
                    per_cell_alpha
                ),
                equivalence_margin_rad=(
                    margin
                ),
                minimum_valid_samples_passed=(
                    minimum_pass
                ),
                invalid_fraction_passed=(
                    invalid_pass
                ),
                equivalence_bound_passed=(
                    equivalence_pass
                ),
                passed=passed,
            )
        )

    status = (
        "EQUIVALENCE_ESTABLISHED"
        if all(
            item.passed
            for item in results
        )
        else "EQUIVALENCE_NOT_ESTABLISHED"
    )

    return N0PhaseValidationDecision(
        preregistration_id=(
            preregistration.preregistration_id
        ),
        familywise_alpha=alpha,
        simultaneous_coverage_lower_bound=(
            1.0 - alpha
        ),
        per_cell_alpha=(
            per_cell_alpha
        ),
        multiplicity_rule=(
            preregistration.multiplicity_rule
        ),
        cells=tuple(
            results
        ),
        status=status,
        physical_claim_permitted=False,
    )
