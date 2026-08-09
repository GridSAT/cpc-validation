from __future__ import annotations

from dataclasses import dataclass

from src.physical_execution_conformance import (
    PhysicalEvidenceProfile,
)


PHYSICAL_FPGA_PROFILE_ID = "fpga.physical-device.v1"


@dataclass(frozen=True)
class PhysicalFPGAProfile:
    """
    RFC-0009 substrate profile for physical realization of an fpga/1
    prepared execution.

    The profile defines required realization stages and evidence fields.
    It is independent of FPGA vendor, device family, board, synthesis
    implementation, place-and-route implementation, and programmer.
    """

    profile_id: str = PHYSICAL_FPGA_PROFILE_ID
    backend_id: str = "fpga"
    backend_version: str = "1"
    hdl_target: str = "verilog-2001"

    realization_stages: tuple[str, ...] = (
        "synthesis",
        "technology-mapping",
        "placement",
        "routing",
        "bitstream-generation",
        "device-programming",
        "physical-stimulus",
        "physical-observation",
        "timing-validation",
    )

    def __post_init__(self) -> None:
        for name, value in (
            ("profile_id", self.profile_id),
            ("backend_id", self.backend_id),
            ("backend_version", self.backend_version),
            ("hdl_target", self.hdl_target),
        ):
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"{name} must be a non-empty string"
                )

        if not self.realization_stages:
            raise ValueError(
                "realization_stages must be non-empty"
            )

        if any(
            not isinstance(stage, str) or not stage
            for stage in self.realization_stages
        ):
            raise ValueError(
                "realization_stages must contain non-empty strings"
            )

        if len(set(self.realization_stages)) != len(
            self.realization_stages
        ):
            raise ValueError(
                "realization_stages must be unique"
            )

    def evidence_profile(self) -> PhysicalEvidenceProfile:
        """
        Return the generic RFC-0009 evidence requirements for a physical
        FPGA execution.

        These requirements establish execution traceability and evidentiary
        completeness. They do not establish semantic correctness.
        """

        return PhysicalEvidenceProfile(
            profile_id=self.profile_id,
            required_substrate_fields=(
                "board_id",
                "device_family",
                "device_id",
                "device_part",
            ),
            required_instrumentation_fields=(
                "observation_interface",
                "programming_interface",
                "stimulus_interface",
            ),
            required_calibration_fields=(
                "timing_validation_id",
            ),
            required_evidence_types=(
                "bitstream",
                "build-report",
                "measurement-log",
                "programming-log",
                "timing-report",
            ),
        )


PHYSICAL_FPGA_PROFILE = PhysicalFPGAProfile()
