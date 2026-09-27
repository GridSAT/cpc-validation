from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass


N0_PHYSICAL_PROFILE_SCHEMA = "cpc.shor.n0.physical-profile.v1"

N0_REALIZATION_STATUS = "simulated"

N0_CARRIER_FAMILIES = (
    "gkp-multimode-bosonic",
    "stabilized-cat-bosonic",
)

N0_FORBIDDEN_TRUTH_FIELDS = (
    "expected_class",
    "expected_order",
    "expected_output",
    "expected_phase",
    "satisfying_assignment",
    "semantic_answer",
    "theta_truth",
    "truth_phase",
)

N0_CLAIM_BOUNDARY = (
    "Simulation-only N0 measurement-validation profile. "
    "It is not physical evidence, native CPC validation, native Shor, "
    "scaling evidence, or advantage evidence."
)

UNRESOLVED_PHYSICAL_APPARATUS = "UNRESOLVED_PHYSICAL_APPARATUS"


def canonical_json_value(value: object) -> str:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    )


def canonical_sha256_value(value: object) -> str:
    digest = hashlib.sha256(
        canonical_json_value(value).encode("utf-8")
    ).hexdigest()
    return f"sha256:{digest}"


def _validate_nonempty_string(
    value: str,
    field_name: str,
) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(
            f"{field_name} must be a non-empty string"
        )


def _validate_sorted_unique_strings(
    values: tuple[str, ...],
    field_name: str,
) -> None:
    if any(
        not isinstance(value, str) or not value
        for value in values
    ):
        raise ValueError(
            f"{field_name} must contain non-empty strings"
        )

    if len(set(values)) != len(values):
        raise ValueError(
            f"{field_name} must be unique"
        )

    if values != tuple(sorted(values)):
        raise ValueError(
            f"{field_name} must be sorted"
        )


@dataclass(frozen=True)
class N0PhysicalProfile:
    profile_id: str
    carrier_family: str

    protected_manifold_id: str
    state_preparation_id: str
    stabilization_model_id: str
    probe_model_id: str
    reference_model_id: str
    raw_record_schema_id: str
    calibration_model_id: str
    reducer_id: str
    statistical_analysis_id: str

    controller_id: str
    physical_apparatus_id: str

    permitted_command_phases_rad: tuple[float, ...]
    admitted_observations: tuple[str, ...]

    realization_status: str = N0_REALIZATION_STATUS

    forbidden_truth_fields: tuple[str, ...] = (
        N0_FORBIDDEN_TRUTH_FIELDS
    )

    claim_boundary: str = N0_CLAIM_BOUNDARY

    def __post_init__(self) -> None:
        for name, value in (
            ("profile_id", self.profile_id),
            ("protected_manifold_id", self.protected_manifold_id),
            ("state_preparation_id", self.state_preparation_id),
            ("stabilization_model_id", self.stabilization_model_id),
            ("probe_model_id", self.probe_model_id),
            ("reference_model_id", self.reference_model_id),
            ("raw_record_schema_id", self.raw_record_schema_id),
            ("calibration_model_id", self.calibration_model_id),
            ("reducer_id", self.reducer_id),
            (
                "statistical_analysis_id",
                self.statistical_analysis_id,
            ),
            ("controller_id", self.controller_id),
            ("physical_apparatus_id", self.physical_apparatus_id),
            ("claim_boundary", self.claim_boundary),
        ):
            _validate_nonempty_string(
                value,
                name,
            )

        if self.carrier_family not in N0_CARRIER_FAMILIES:
            raise ValueError(
                "carrier_family must be one of: "
                + ", ".join(N0_CARRIER_FAMILIES)
            )

        if self.realization_status != N0_REALIZATION_STATUS:
            raise ValueError(
                "N0 physical-profile v1 is simulation-only; "
                "realization_status must be simulated"
            )

        phases = self.permitted_command_phases_rad

        if not phases:
            raise ValueError(
                "permitted_command_phases_rad must not be empty"
            )

        if any(
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            for value in phases
        ):
            raise ValueError(
                "permitted command phases must be finite numbers"
            )

        if len(set(float(value) for value in phases)) != len(
            phases
        ):
            raise ValueError(
                "permitted command phases must be unique"
            )

        if tuple(float(value) for value in phases) != tuple(
            sorted(float(value) for value in phases)
        ):
            raise ValueError(
                "permitted command phases must be sorted"
            )

        _validate_sorted_unique_strings(
            self.admitted_observations,
            "admitted_observations",
        )

        if (
            self.forbidden_truth_fields
            != N0_FORBIDDEN_TRUTH_FIELDS
        ):
            raise ValueError(
                "forbidden_truth_fields cannot be weakened or changed"
            )

    @property
    def schema(self) -> str:
        return N0_PHYSICAL_PROFILE_SCHEMA

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "profile_id": self.profile_id,
            "carrier_family": self.carrier_family,
            "protected_manifold_id": self.protected_manifold_id,
            "state_preparation_id": self.state_preparation_id,
            "stabilization_model_id": self.stabilization_model_id,
            "probe_model_id": self.probe_model_id,
            "reference_model_id": self.reference_model_id,
            "raw_record_schema_id": self.raw_record_schema_id,
            "calibration_model_id": self.calibration_model_id,
            "reducer_id": self.reducer_id,
            "statistical_analysis_id": (
                self.statistical_analysis_id
            ),
            "controller_id": self.controller_id,
            "physical_apparatus_id": self.physical_apparatus_id,
            "permitted_command_phases_rad": (
                self.permitted_command_phases_rad
            ),
            "admitted_observations": self.admitted_observations,
            "realization_status": self.realization_status,
            "forbidden_truth_fields": self.forbidden_truth_fields,
            "claim_boundary": self.claim_boundary,
        }

    @property
    def canonical_json(self) -> str:
        return canonical_json_value(
            self.to_dict()
        )

    @property
    def profile_hash(self) -> str:
        return canonical_sha256_value(
            self.to_dict()
        )


def build_default_n0_physical_profile() -> N0PhysicalProfile:
    return N0PhysicalProfile(
        profile_id="CPC-SHOR-N0-PHYSICAL-PROFILE-v1",
        carrier_family="stabilized-cat-bosonic",
        protected_manifold_id=(
            "cpc.shor.n0.cat-protected-manifold.v1"
        ),
        state_preparation_id=(
            "cpc.shor.n0.logical-phase-preparation.v1"
        ),
        stabilization_model_id=(
            "cpc.shor.n0.cat-stabilization-model.v1"
        ),
        probe_model_id=(
            "cpc.shor.n0.phase-probe-model.v1"
        ),
        reference_model_id=(
            "cpc.shor.n0.microwave-reference-model.v1"
        ),
        raw_record_schema_id=(
            "cpc.shor.n0.raw-record.v2"
        ),
        calibration_model_id=(
            "cpc.shor.n0.calibration-model.v1"
        ),
        reducer_id=(
            "cpc.shor.n0.independent-phase-reducer.v1"
        ),
        statistical_analysis_id=(
            "cpc.shor.n0.statistics.v1"
        ),
        controller_id="CPC-SHOR-N0-CONTROLLER-v1",
        physical_apparatus_id=(
            UNRESOLVED_PHYSICAL_APPARATUS
        ),
        permitted_command_phases_rad=(
            0.0,
            math.pi / 2.0,
        ),
        admitted_observations=(
            "reference_i",
            "reference_q",
            "signal_i",
            "signal_q",
        ),
    )
