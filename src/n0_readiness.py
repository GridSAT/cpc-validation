from __future__ import annotations

from dataclasses import dataclass, replace

from src.n0_physical_prereg_freeze import (
    N0PhysicalPreregistrationFreeze,
)


N0_READINESS_SCHEMA = "cpc.shor.n0.readiness.v3"


SOFTWARE_COMPONENTS = (
    "calibration_contract",
    "claim_firewall",
    "device_adapter",
    "fault_suite",
    "physical_adapter_boundary",
    "physical_prereg_freeze",
    "physical_profile",
    "raw_record_schema",
    "reducer",
    "rfc0010_mapping",
    "statistical_decision",
    "statistical_rehearsal",
    "statistics",
    "synthetic_rehearsal",
)


MATERIAL_REQUIREMENTS = (
    "PHYSICAL_PROFILE",
    "PHYSICAL_APPARATUS_IDENTITY",
    "PHYSICAL_CALIBRATION",
    "PHYSICAL_CPC_PROBE_REALIZATION",
    "RAW_TRANSPORT_ENCODING",
    "PHYSICAL_TIMEBASE",
    "CONTROLLER_CLOCK_BINDING",
    "CONTROLLER_PIN_BINDING",
    "CONTROLLER_ADC_DAC_BINDING",
    "CONTROLLER_PHYSICAL_CONSTRAINTS",
    "CONTROLLER_PLACE_ROUTE",
    "CONTROLLER_BITSTREAM",
    "SOURCE_MANIFEST",
    "PHYSICAL_EVIDENCE_MANIFEST",
    "PHYSICAL_PREREGISTRATION",
)


@dataclass(frozen=True)
class N0ReadinessAssessment:
    completed_software_components: tuple[str, ...]

    controller_logical_protocol_complete: bool
    controller_rtl_simulation_complete: bool
    controller_synthesis_complete: bool

    physical_profile_defined: bool
    physical_apparatus_identity_present: bool
    physical_calibration_values_present: bool
    physical_cpc_probe_realized: bool

    raw_transport_encoding_defined: bool
    physical_timebase_present: bool

    controller_clock_binding_complete: bool
    controller_pin_binding_complete: bool
    controller_adc_dac_binding_complete: bool

    controller_physical_constraints_complete: bool
    controller_place_route_complete: bool
    controller_bitstream_complete: bool

    source_manifest_present: bool
    physical_evidence_manifest_present: bool

    physical_preregistration_material_complete: bool

    human_go_present: bool

    fpga_programming_authorized: bool
    fpga_programmed: bool

    physical_raw_records_present: bool

    def __post_init__(self) -> None:
        unknown = (
            set(
                self.completed_software_components
            )
            - set(
                SOFTWARE_COMPONENTS
            )
        )

        if unknown:
            raise ValueError(
                "unknown software component(s): "
                + ", ".join(
                    sorted(
                        unknown
                    )
                )
            )

        if (
            len(
                set(
                    self.completed_software_components
                )
            )
            != len(
                self.completed_software_components
            )
        ):
            raise ValueError(
                "completed software components must be unique"
            )

        boolean_fields = (
            "controller_logical_protocol_complete",
            "controller_rtl_simulation_complete",
            "controller_synthesis_complete",
            "physical_profile_defined",
            "physical_apparatus_identity_present",
            "physical_calibration_values_present",
            "physical_cpc_probe_realized",
            "raw_transport_encoding_defined",
            "physical_timebase_present",
            "controller_clock_binding_complete",
            "controller_pin_binding_complete",
            "controller_adc_dac_binding_complete",
            "controller_physical_constraints_complete",
            "controller_place_route_complete",
            "controller_bitstream_complete",
            "source_manifest_present",
            "physical_evidence_manifest_present",
            "physical_preregistration_material_complete",
            "human_go_present",
            "fpga_programming_authorized",
            "fpga_programmed",
            "physical_raw_records_present",
        )

        for field_name in boolean_fields:
            if not isinstance(
                getattr(
                    self,
                    field_name,
                ),
                bool,
            ):
                raise ValueError(
                    f"{field_name} must be boolean"
                )

        # Logical controller progression.
        if (
            self.controller_rtl_simulation_complete
            and not self.controller_logical_protocol_complete
        ):
            raise ValueError(
                "RTL simulation cannot precede "
                "logical protocol completion"
            )

        if (
            self.controller_synthesis_complete
            and not self.controller_rtl_simulation_complete
        ):
            raise ValueError(
                "controller synthesis cannot precede "
                "RTL simulation"
            )

        # Physical controller progression.
        if (
            self.controller_physical_constraints_complete
            and not self.controller_synthesis_complete
        ):
            raise ValueError(
                "physical constraints cannot precede "
                "controller synthesis"
            )

        if (
            self.controller_physical_constraints_complete
            and not self.controller_clock_binding_complete
        ):
            raise ValueError(
                "physical constraints require "
                "controller clock binding"
            )

        if (
            self.controller_physical_constraints_complete
            and not self.controller_pin_binding_complete
        ):
            raise ValueError(
                "physical constraints require "
                "controller pin binding"
            )

        if (
            self.controller_place_route_complete
            and not self.controller_physical_constraints_complete
        ):
            raise ValueError(
                "place-and-route cannot precede "
                "physical constraints"
            )

        if (
            self.controller_bitstream_complete
            and not self.controller_place_route_complete
        ):
            raise ValueError(
                "bitstream cannot precede "
                "place-and-route"
            )

        # A material-complete physical preregistration must not
        # contradict the readiness flags that it binds.
        if self.physical_preregistration_material_complete:
            required = (
                self.physical_profile_defined,
                self.physical_apparatus_identity_present,
                self.physical_calibration_values_present,
                self.physical_cpc_probe_realized,
                self.raw_transport_encoding_defined,
                self.physical_timebase_present,
                self.controller_clock_binding_complete,
                self.controller_pin_binding_complete,
                self.controller_adc_dac_binding_complete,
                self.controller_physical_constraints_complete,
                self.controller_place_route_complete,
                self.controller_bitstream_complete,
                self.source_manifest_present,
                self.physical_evidence_manifest_present,
            )

            if not all(
                required
            ):
                raise ValueError(
                    "material-complete physical preregistration "
                    "requires all bound physical material"
                )

        if (
            self.human_go_present
            and not self.physical_preregistration_material_complete
        ):
            raise ValueError(
                "human GO cannot precede material-complete "
                "physical preregistration"
            )

        if (
            self.fpga_programming_authorized
            and not self.human_go_present
        ):
            raise ValueError(
                "FPGA programming authorization cannot precede "
                "human GO"
            )

        if (
            self.fpga_programming_authorized
            and not self.controller_bitstream_complete
        ):
            raise ValueError(
                "FPGA programming authorization requires "
                "a completed bitstream"
            )

        if (
            self.fpga_programmed
            and not self.fpga_programming_authorized
        ):
            raise ValueError(
                "FPGA programming cannot precede "
                "programming authorization"
            )

        # Raw records are post-execution evidence.
        if (
            self.physical_raw_records_present
            and not self.human_go_present
        ):
            raise ValueError(
                "physical raw records cannot precede human GO"
            )

    @property
    def schema(self) -> str:
        return (
            N0_READINESS_SCHEMA
        )

    @property
    def software_profile_complete(
        self,
    ) -> bool:
        return set(
            self.completed_software_components
        ) == set(
            SOFTWARE_COMPONENTS
        )

    @property
    def controller_logical_stack_complete(
        self,
    ) -> bool:
        return all(
            (
                self.controller_logical_protocol_complete,
                self.controller_rtl_simulation_complete,
                self.controller_synthesis_complete,
            )
        )

    @property
    def controller_physical_build_complete(
        self,
    ) -> bool:
        return all(
            (
                self.controller_physical_constraints_complete,
                self.controller_place_route_complete,
                self.controller_bitstream_complete,
            )
        )

    @property
    def unresolved_material_requirements(
        self,
    ) -> tuple[str, ...]:
        blockers: list[str] = []

        mapping = (
            (
                "PHYSICAL_PROFILE",
                self.physical_profile_defined,
            ),
            (
                "PHYSICAL_APPARATUS_IDENTITY",
                self.physical_apparatus_identity_present,
            ),
            (
                "PHYSICAL_CALIBRATION",
                self.physical_calibration_values_present,
            ),
            (
                "PHYSICAL_CPC_PROBE_REALIZATION",
                self.physical_cpc_probe_realized,
            ),
            (
                "RAW_TRANSPORT_ENCODING",
                self.raw_transport_encoding_defined,
            ),
            (
                "PHYSICAL_TIMEBASE",
                self.physical_timebase_present,
            ),
            (
                "CONTROLLER_CLOCK_BINDING",
                self.controller_clock_binding_complete,
            ),
            (
                "CONTROLLER_PIN_BINDING",
                self.controller_pin_binding_complete,
            ),
            (
                "CONTROLLER_ADC_DAC_BINDING",
                self.controller_adc_dac_binding_complete,
            ),
            (
                "CONTROLLER_PHYSICAL_CONSTRAINTS",
                self.controller_physical_constraints_complete,
            ),
            (
                "CONTROLLER_PLACE_ROUTE",
                self.controller_place_route_complete,
            ),
            (
                "CONTROLLER_BITSTREAM",
                self.controller_bitstream_complete,
            ),
            (
                "SOURCE_MANIFEST",
                self.source_manifest_present,
            ),
            (
                "PHYSICAL_EVIDENCE_MANIFEST",
                self.physical_evidence_manifest_present,
            ),
            (
                "PHYSICAL_PREREGISTRATION",
                self.physical_preregistration_material_complete,
            ),
        )

        for name, complete in mapping:
            if not complete:
                blockers.append(
                    name
                )

        return tuple(
            blockers
        )

    @property
    def execution_authorized(
        self,
    ) -> bool:
        return (
            self.physical_preregistration_material_complete
            and self.human_go_present
        )

    @property
    def acquisition_ready(
        self,
    ) -> bool:
        return all(
            (
                self.execution_authorized,
                self.fpga_programming_authorized,
                self.fpga_programmed,
            )
        )

    @property
    def status(self) -> str:
        if not self.software_profile_complete:
            return (
                "SOFTWARE_PROFILE_INCOMPLETE"
            )

        if not self.controller_logical_protocol_complete:
            return (
                "CONTROLLER_LOGICAL_PROTOCOL_PENDING"
            )

        if not self.controller_rtl_simulation_complete:
            return (
                "CONTROLLER_RTL_SIMULATION_PENDING"
            )

        if not self.controller_synthesis_complete:
            return (
                "CONTROLLER_SYNTHESIS_PENDING"
            )

        if not self.physical_profile_defined:
            return (
                "PHYSICAL_PROFILE_PENDING"
            )

        if not self.physical_apparatus_identity_present:
            return (
                "PHYSICAL_APPARATUS_IDENTITY_PENDING"
            )

        if not self.physical_calibration_values_present:
            return (
                "PHYSICAL_CALIBRATION_PENDING"
            )

        if not self.physical_cpc_probe_realized:
            return (
                "PHYSICAL_CPC_PROBE_REALIZATION_PENDING"
            )

        if not self.raw_transport_encoding_defined:
            return (
                "RAW_TRANSPORT_ENCODING_PENDING"
            )

        if not self.physical_timebase_present:
            return (
                "PHYSICAL_TIMEBASE_PENDING"
            )

        if not self.controller_clock_binding_complete:
            return (
                "CONTROLLER_CLOCK_BINDING_PENDING"
            )

        if not self.controller_pin_binding_complete:
            return (
                "CONTROLLER_PIN_BINDING_PENDING"
            )

        if not self.controller_adc_dac_binding_complete:
            return (
                "CONTROLLER_ADC_DAC_BINDING_PENDING"
            )

        if not self.controller_physical_constraints_complete:
            return (
                "CONTROLLER_PHYSICAL_CONSTRAINTS_PENDING"
            )

        if not self.controller_place_route_complete:
            return (
                "CONTROLLER_PLACE_ROUTE_PENDING"
            )

        if not self.controller_bitstream_complete:
            return (
                "CONTROLLER_BITSTREAM_PENDING"
            )

        if not self.source_manifest_present:
            return (
                "SOURCE_MANIFEST_PENDING"
            )

        if not self.physical_evidence_manifest_present:
            return (
                "PHYSICAL_EVIDENCE_MANIFEST_PENDING"
            )

        if not self.physical_preregistration_material_complete:
            return (
                "PHYSICAL_PREREGISTRATION_PENDING"
            )

        if not self.human_go_present:
            return (
                "HUMAN_GO_PENDING"
            )

        if not self.fpga_programming_authorized:
            return (
                "FPGA_PROGRAMMING_AUTHORIZATION_PENDING"
            )

        if not self.fpga_programmed:
            return (
                "FPGA_PROGRAMMING_PENDING"
            )

        if not self.physical_raw_records_present:
            return (
                "EXECUTION_AUTHORIZED_AWAITING_PHYSICAL_ACQUISITION"
            )

        return (
            "PHYSICAL_EVIDENCE_PRESENT_VALIDATION_PENDING"
        )

    def require_acquisition_ready(
        self,
    ) -> None:
        if not self.acquisition_ready:
            raise RuntimeError(
                "N0 stack is not ready for physical acquisition"
            )

        if self.physical_raw_records_present:
            raise RuntimeError(
                "physical acquisition already produced raw records"
            )


def complete_software_components(
) -> tuple[str, ...]:
    return tuple(
        sorted(
            SOFTWARE_COMPONENTS
        )
    )


def build_current_pre_controller_assessment(
) -> N0ReadinessAssessment:
    return N0ReadinessAssessment(
        completed_software_components=(
            complete_software_components()
        ),
        controller_logical_protocol_complete=False,
        controller_rtl_simulation_complete=False,
        controller_synthesis_complete=False,
        physical_profile_defined=False,
        physical_apparatus_identity_present=False,
        physical_calibration_values_present=False,
        physical_cpc_probe_realized=False,
        raw_transport_encoding_defined=False,
        physical_timebase_present=False,
        controller_clock_binding_complete=False,
        controller_pin_binding_complete=False,
        controller_adc_dac_binding_complete=False,
        controller_physical_constraints_complete=False,
        controller_place_route_complete=False,
        controller_bitstream_complete=False,
        source_manifest_present=False,
        physical_evidence_manifest_present=False,
        physical_preregistration_material_complete=False,
        human_go_present=False,
        fpga_programming_authorized=False,
        fpga_programmed=False,
        physical_raw_records_present=False,
    )


def build_post_logical_controller_assessment(
) -> N0ReadinessAssessment:
    return replace(
        build_current_pre_controller_assessment(),
        controller_logical_protocol_complete=True,
        controller_rtl_simulation_complete=True,
        controller_synthesis_complete=True,
    )


def build_current_repository_assessment(
) -> N0ReadinessAssessment:
    """
    Current repository state after Blocks 1-12D.

    The software/controller logical stack is complete.
    No physical N0 profile or apparatus has yet been defined.
    """

    return (
        build_post_logical_controller_assessment()
    )


def apply_physical_preregistration_freeze(
    *,
    assessment: N0ReadinessAssessment,
    freeze: N0PhysicalPreregistrationFreeze,
) -> N0ReadinessAssessment:
    """
    Project only the freeze-owned readiness facts.

    This does not infer FPGA programming authorization,
    programming completion, or physical raw records.
    """

    unresolved = set(
        freeze.bindings.unresolved_fields
    )

    return replace(
        assessment,
        physical_profile_defined=(
            "physical_profile_id"
            not in unresolved
        ),
        physical_apparatus_identity_present=(
            "apparatus_id"
            not in unresolved
        ),
        physical_calibration_values_present=(
            "calibration_id"
            not in unresolved
        ),
        physical_cpc_probe_realized=(
            "probe_realization_id"
            not in unresolved
        ),
        raw_transport_encoding_defined=(
            "raw_transport_encoding_id"
            not in unresolved
        ),
        physical_timebase_present=(
            "timebase_id"
            not in unresolved
        ),
        controller_clock_binding_complete=(
            "controller_clock_binding_id"
            not in unresolved
        ),
        controller_pin_binding_complete=(
            "controller_pin_binding_id"
            not in unresolved
        ),
        controller_adc_dac_binding_complete=(
            "controller_adc_dac_binding_id"
            not in unresolved
        ),
        controller_physical_constraints_complete=(
            "controller_constraint_id"
            not in unresolved
        ),
        controller_place_route_complete=(
            "controller_place_route_id"
            not in unresolved
        ),
        source_manifest_present=(
            "source_manifest_sha256"
            not in unresolved
        ),
        physical_evidence_manifest_present=(
            "physical_evidence_manifest_sha256"
            not in unresolved
        ),
        physical_preregistration_material_complete=(
            freeze.material_complete
        ),
        human_go_present=(
            freeze.human_go_present
        ),
    )
