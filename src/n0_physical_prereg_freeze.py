from __future__ import annotations

from dataclasses import dataclass

from src.n0_controller_protocol import (
    N0_CONTROLLER_PROTOCOL_ID,
    N0_CONTROLLER_PROTOCOL_SCHEMA,
)
from src.n0_raw_record import (
    N0_RAW_RECORD_SCHEMA,
    canonical_json_value,
    canonical_sha256_value,
)
from src.n0_statistics import (
    N0_PHASE_VALIDATION_MULTIPLICITY_RULE,
    N0_PHASE_VALIDATION_SCHEMA,
    N0_STATISTICS_SCHEMA,
    N0Preregistration,
    PreregisteredParameter,
    UNRESOLVED_PHYSICAL_PARAMETER,
    validate_resolved_physical_preregistration,
)


N0_PHYSICAL_PREREG_FREEZE_SCHEMA = (
    "cpc.shor.n0.physical-prereg-freeze.v1"
)

N0_PHYSICAL_PREREG_FREEZE_ID = (
    "CPC-SHOR-N0-PHYSICAL-PREREG-FREEZE-v1"
)

UNRESOLVED_PHYSICAL_FIELD = (
    "UNRESOLVED_PHYSICAL_FIELD"
)

SIMULATION_ONLY_PROFILE_ID = (
    "CPC-SHOR-N0-PHYSICAL-PROFILE-v1"
)

N0_PHYSICAL_REDUCER_ID = (
    "cpc.shor.n0.independent-phase-reducer.v1"
)

N0_CONFIDENCE_METHOD_ID = (
    "ONE-SIDED-HOEFFDING-ABSOLUTE-WRAPPED-ERROR-v1"
)

N0_REQUIRED_RAW_PAYLOAD_PROVENANCE = (
    "native-instrument-bytes"
)

N0_NEGATIVE_CONTROL_REQUIREMENTS = (
    "acquisition-negative-control-required",
    "statistical-negative-control-required",
    "negative-controls-excluded-from-operational-cells",
    "negative-control-failure-blocks-physical-pass",
)

N0_PREREG_STATUSES = (
    "DRAFT_UNRESOLVED",
    "MATERIAL_COMPLETE_AWAITING_HUMAN_GO",
    "EXECUTION_AUTHORIZED",
)


def unresolved(
    field_name: str,
) -> str:
    if (
        not isinstance(field_name, str)
        or not field_name
    ):
        raise ValueError(
            "field_name must be non-empty"
        )

    return (
        UNRESOLVED_PHYSICAL_FIELD
        + ":"
        + field_name
    )


def _is_unresolved(
    value: str,
) -> bool:
    return (
        isinstance(value, str)
        and value.startswith(
            "UNRESOLVED"
        )
    )


def _validate_nonempty(
    value: str,
    field_name: str,
) -> None:
    if (
        not isinstance(value, str)
        or not value
    ):
        raise ValueError(
            f"{field_name} must be a non-empty string"
        )


def _validate_sha256_or_unresolved(
    value: str,
    field_name: str,
) -> None:
    _validate_nonempty(
        value,
        field_name,
    )

    if _is_unresolved(
        value
    ):
        return

    prefix = "sha256:"

    if not value.startswith(
        prefix
    ):
        raise ValueError(
            f"{field_name} must be sha256 or unresolved"
        )

    digest = value[
        len(prefix):
    ]

    if (
        len(digest) != 64
        or any(
            character
            not in "0123456789abcdef"
            for character in digest
        )
    ):
        raise ValueError(
            f"{field_name} must be lowercase sha256"
        )


@dataclass(frozen=True)
class N0PhysicalBindings:
    physical_profile_id: str

    apparatus_id: str
    calibration_id: str

    probe_realization_id: str
    reference_id: str
    timebase_id: str
    raw_transport_encoding_id: str

    controller_constraint_id: str
    controller_place_route_id: str
    controller_clock_binding_id: str
    controller_pin_binding_id: str
    controller_adc_dac_binding_id: str

    negative_control_protocol_id: str

    source_manifest_sha256: str
    physical_evidence_manifest_sha256: str

    raw_payload_provenance: str = (
        N0_REQUIRED_RAW_PAYLOAD_PROVENANCE
    )

    def __post_init__(
        self,
    ) -> None:
        string_fields = (
            "physical_profile_id",
            "apparatus_id",
            "calibration_id",
            "probe_realization_id",
            "reference_id",
            "timebase_id",
            "raw_transport_encoding_id",
            "controller_constraint_id",
            "controller_place_route_id",
            "controller_clock_binding_id",
            "controller_pin_binding_id",
            "controller_adc_dac_binding_id",
            "negative_control_protocol_id",
        )

        for field_name in (
            string_fields
        ):
            value = getattr(
                self,
                field_name,
            )

            _validate_nonempty(
                value,
                field_name,
            )

        _validate_sha256_or_unresolved(
            self.source_manifest_sha256,
            "source_manifest_sha256",
        )

        _validate_sha256_or_unresolved(
            self.physical_evidence_manifest_sha256,
            "physical_evidence_manifest_sha256",
        )

        if (
            self.raw_payload_provenance
            != N0_REQUIRED_RAW_PAYLOAD_PROVENANCE
        ):
            raise ValueError(
                "physical preregistration requires "
                "native instrument-byte provenance"
            )

        if (
            not _is_unresolved(
                self.physical_profile_id
            )
            and self.physical_profile_id
            == SIMULATION_ONLY_PROFILE_ID
        ):
            raise ValueError(
                "simulation-only N0 profile may not be "
                "bound as physical profile"
            )

        for field_name in (
            string_fields
        ):
            value = getattr(
                self,
                field_name,
            )

            if _is_unresolved(
                value
            ):
                continue

            if "simulated" in value.lower():
                raise ValueError(
                    f"{field_name} may not bind "
                    "simulated identity"
                )

    @property
    def unresolved_fields(
        self,
    ) -> tuple[str, ...]:
        names = (
            "physical_profile_id",
            "apparatus_id",
            "calibration_id",
            "probe_realization_id",
            "reference_id",
            "timebase_id",
            "raw_transport_encoding_id",
            "controller_constraint_id",
            "controller_place_route_id",
            "controller_clock_binding_id",
            "controller_pin_binding_id",
            "controller_adc_dac_binding_id",
            "negative_control_protocol_id",
            "source_manifest_sha256",
            "physical_evidence_manifest_sha256",
        )

        return tuple(
            name
            for name in names
            if _is_unresolved(
                getattr(
                    self,
                    name,
                )
            )
        )

    @property
    def is_complete(
        self,
    ) -> bool:
        return not (
            self.unresolved_fields
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "physical_profile_id": (
                self.physical_profile_id
            ),
            "apparatus_id": (
                self.apparatus_id
            ),
            "calibration_id": (
                self.calibration_id
            ),
            "probe_realization_id": (
                self.probe_realization_id
            ),
            "reference_id": (
                self.reference_id
            ),
            "timebase_id": (
                self.timebase_id
            ),
            "raw_transport_encoding_id": (
                self.raw_transport_encoding_id
            ),
            "raw_payload_provenance": (
                self.raw_payload_provenance
            ),
            "controller_constraint_id": (
                self.controller_constraint_id
            ),
            "controller_place_route_id": (
                self.controller_place_route_id
            ),
            "controller_clock_binding_id": (
                self.controller_clock_binding_id
            ),
            "controller_pin_binding_id": (
                self.controller_pin_binding_id
            ),
            "controller_adc_dac_binding_id": (
                self.controller_adc_dac_binding_id
            ),
            "negative_control_protocol_id": (
                self.negative_control_protocol_id
            ),
            "source_manifest_sha256": (
                self.source_manifest_sha256
            ),
            "physical_evidence_manifest_sha256": (
                self.physical_evidence_manifest_sha256
            ),
            "unresolved_fields": (
                self.unresolved_fields
            ),
        }


def build_frozen_method_physical_statistics(
) -> N0Preregistration:
    """
    Physical numerical thresholds remain unresolved.

    The statistical method itself is already frozen:
    held-out phase cells + Bonferroni + one-sided Hoeffding.
    """

    unresolved_status = (
        UNRESOLVED_PHYSICAL_PARAMETER
    )

    def parameter(
        name: str,
        units: str,
    ) -> PreregisteredParameter:
        return PreregisteredParameter(
            name=name,
            status=unresolved_status,
            units=units,
        )

    return N0Preregistration(
        preregistration_id=(
            "CPC-SHOR-N0-PHYSICAL-PREREGISTRATION-v1"
        ),
        alpha=parameter(
            "alpha",
            "probability",
        ),
        equivalence_margin_rad=parameter(
            "equivalence_margin_rad",
            "rad",
        ),
        power_target=parameter(
            "power_target",
            "probability",
        ),
        minimum_valid_samples=parameter(
            "minimum_valid_samples",
            "count",
        ),
        maximum_invalid_fraction=parameter(
            "maximum_invalid_fraction",
            "fraction",
        ),
        calibration_gate_id=(
            unresolved(
                "calibration_gate_id"
            )
        ),
        operational_gate_id=(
            unresolved(
                "operational_gate_id"
            )
        ),
        multiplicity_rule=(
            N0_PHASE_VALIDATION_MULTIPLICITY_RULE
        ),
    )


@dataclass(frozen=True)
class N0PhysicalPreregistrationFreeze:
    bindings: N0PhysicalBindings
    statistics: N0Preregistration

    human_go_id: str = (
        "UNRESOLVED_HUMAN_GO"
    )

    freeze_id: str = (
        N0_PHYSICAL_PREREG_FREEZE_ID
    )

    # This artifact never authorizes FPGA programming.
    # Any such action requires a separate control path.
    fpga_programming_authorized: bool = False

    # Preregistration cannot itself establish a physical PASS.
    physical_pass_authorized: bool = False

    def __post_init__(
        self,
    ) -> None:
        if (
            self.freeze_id
            != N0_PHYSICAL_PREREG_FREEZE_ID
        ):
            raise ValueError(
                "unsupported preregistration freeze identity"
            )

        _validate_nonempty(
            self.human_go_id,
            "human_go_id",
        )

        if (
            self.fpga_programming_authorized
            is not False
        ):
            raise ValueError(
                "physical preregistration may not authorize "
                "FPGA programming"
            )

        if (
            self.physical_pass_authorized
            is not False
        ):
            raise ValueError(
                "preregistration may not pre-authorize "
                "a physical PASS"
            )

        if (
            self.statistics.multiplicity_rule
            != N0_PHASE_VALIDATION_MULTIPLICITY_RULE
        ):
            raise ValueError(
                "statistical multiplicity method is not frozen"
            )

    @property
    def schema(
        self,
    ) -> str:
        return (
            N0_PHYSICAL_PREREG_FREEZE_SCHEMA
        )

    @property
    def methodology(
        self,
    ) -> dict[str, object]:
        return {
            "raw_record_schema": (
                N0_RAW_RECORD_SCHEMA
            ),
            "statistics_schema": (
                N0_STATISTICS_SCHEMA
            ),
            "phase_validation_schema": (
                N0_PHASE_VALIDATION_SCHEMA
            ),
            "controller_protocol_id": (
                N0_CONTROLLER_PROTOCOL_ID
            ),
            "controller_protocol_schema": (
                N0_CONTROLLER_PROTOCOL_SCHEMA
            ),
            "reducer_id": (
                N0_PHYSICAL_REDUCER_ID
            ),
            "confidence_method_id": (
                N0_CONFIDENCE_METHOD_ID
            ),
            "multiplicity_rule": (
                N0_PHASE_VALIDATION_MULTIPLICITY_RULE
            ),
            "raw_payload_provenance": (
                N0_REQUIRED_RAW_PAYLOAD_PROVENANCE
            ),
            "negative_control_requirements": (
                N0_NEGATIVE_CONTROL_REQUIREMENTS
            ),
            "truth_blind_reduction_required": True,
            "heldout_validation_required": True,
            "calibration_validation_id_disjointness_required": True,
        }

    @property
    def unresolved_fields(
        self,
    ) -> tuple[str, ...]:
        unresolved_names = list(
            self.bindings.unresolved_fields
        )

        unresolved_names.extend(
            "statistics."
            + name
            for name
            in self.statistics.unresolved_parameters
        )

        if _is_unresolved(
            self.statistics.calibration_gate_id
        ):
            unresolved_names.append(
                "statistics.calibration_gate_id"
            )

        if _is_unresolved(
            self.statistics.operational_gate_id
        ):
            unresolved_names.append(
                "statistics.operational_gate_id"
            )

        return tuple(
            unresolved_names
        )

    @property
    def material_complete(
        self,
    ) -> bool:
        return not (
            self.unresolved_fields
        )

    @property
    def human_go_present(
        self,
    ) -> bool:
        return (
            not _is_unresolved(
                self.human_go_id
            )
            and self.human_go_id.startswith(
                "HUMAN-GO:"
            )
        )

    @property
    def execution_authorized(
        self,
    ) -> bool:
        return (
            self.material_complete
            and self.human_go_present
        )

    @property
    def status(
        self,
    ) -> str:
        if not (
            self.material_complete
        ):
            return (
                "DRAFT_UNRESOLVED"
            )

        if not (
            self.human_go_present
        ):
            return (
                "MATERIAL_COMPLETE_AWAITING_HUMAN_GO"
            )

        return (
            "EXECUTION_AUTHORIZED"
        )

    def require_material_complete(
        self,
    ) -> None:
        if self.unresolved_fields:
            raise RuntimeError(
                "physical preregistration incomplete: "
                + ", ".join(
                    self.unresolved_fields
                )
            )

        validate_resolved_physical_preregistration(
            self.statistics
        )

    def require_execution_authorized(
        self,
    ) -> None:
        self.require_material_complete()

        if not (
            self.human_go_present
        ):
            raise RuntimeError(
                "physical execution requires separate explicit human GO"
            )

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "schema": self.schema,
            "freeze_id": (
                self.freeze_id
            ),
            "methodology": (
                self.methodology
            ),
            "bindings": (
                self.bindings.to_dict()
            ),
            "statistics": {
                "preregistration_id": (
                    self.statistics.preregistration_id
                ),
                "alpha": {
                    "status": self.statistics.alpha.status,
                    "value": self.statistics.alpha.value,
                    "units": self.statistics.alpha.units,
                },
                "equivalence_margin_rad": {
                    "status": (
                        self.statistics
                        .equivalence_margin_rad
                        .status
                    ),
                    "value": (
                        self.statistics
                        .equivalence_margin_rad
                        .value
                    ),
                    "units": (
                        self.statistics
                        .equivalence_margin_rad
                        .units
                    ),
                },
                "power_target": {
                    "status": (
                        self.statistics
                        .power_target
                        .status
                    ),
                    "value": (
                        self.statistics
                        .power_target
                        .value
                    ),
                    "units": (
                        self.statistics
                        .power_target
                        .units
                    ),
                },
                "minimum_valid_samples": {
                    "status": (
                        self.statistics
                        .minimum_valid_samples
                        .status
                    ),
                    "value": (
                        self.statistics
                        .minimum_valid_samples
                        .value
                    ),
                    "units": (
                        self.statistics
                        .minimum_valid_samples
                        .units
                    ),
                },
                "maximum_invalid_fraction": {
                    "status": (
                        self.statistics
                        .maximum_invalid_fraction
                        .status
                    ),
                    "value": (
                        self.statistics
                        .maximum_invalid_fraction
                        .value
                    ),
                    "units": (
                        self.statistics
                        .maximum_invalid_fraction
                        .units
                    ),
                },
                "calibration_gate_id": (
                    self.statistics.calibration_gate_id
                ),
                "operational_gate_id": (
                    self.statistics.operational_gate_id
                ),
                "multiplicity_rule": (
                    self.statistics.multiplicity_rule
                ),
            },
            "human_go_id": (
                self.human_go_id
            ),
            "unresolved_fields": (
                self.unresolved_fields
            ),
            "material_complete": (
                self.material_complete
            ),
            "human_go_present": (
                self.human_go_present
            ),
            "execution_authorized": (
                self.execution_authorized
            ),
            "fpga_programming_authorized": (
                self.fpga_programming_authorized
            ),
            "physical_pass_authorized": (
                self.physical_pass_authorized
            ),
            "status": (
                self.status
            ),
        }

    @property
    def canonical_json(
        self,
    ) -> str:
        return canonical_json_value(
            self.to_dict()
        )

    @property
    def freeze_hash(
        self,
    ) -> str:
        return canonical_sha256_value(
            self.to_dict()
        )


def build_unresolved_n0_physical_preregistration_freeze(
) -> N0PhysicalPreregistrationFreeze:
    bindings = N0PhysicalBindings(
        physical_profile_id=unresolved(
            "physical_profile_id"
        ),
        apparatus_id=unresolved(
            "apparatus_id"
        ),
        calibration_id=unresolved(
            "calibration_id"
        ),
        probe_realization_id=unresolved(
            "probe_realization_id"
        ),
        reference_id=unresolved(
            "reference_id"
        ),
        timebase_id=unresolved(
            "timebase_id"
        ),
        raw_transport_encoding_id=unresolved(
            "raw_transport_encoding_id"
        ),
        controller_constraint_id=unresolved(
            "controller_constraint_id"
        ),
        controller_place_route_id=unresolved(
            "controller_place_route_id"
        ),
        controller_clock_binding_id=unresolved(
            "controller_clock_binding_id"
        ),
        controller_pin_binding_id=unresolved(
            "controller_pin_binding_id"
        ),
        controller_adc_dac_binding_id=unresolved(
            "controller_adc_dac_binding_id"
        ),
        negative_control_protocol_id=unresolved(
            "negative_control_protocol_id"
        ),
        source_manifest_sha256=unresolved(
            "source_manifest_sha256"
        ),
        physical_evidence_manifest_sha256=unresolved(
            "physical_evidence_manifest_sha256"
        ),
    )

    return N0PhysicalPreregistrationFreeze(
        bindings=bindings,
        statistics=(
            build_frozen_method_physical_statistics()
        ),
        human_go_id=(
            "UNRESOLVED_HUMAN_GO"
        ),
    )
