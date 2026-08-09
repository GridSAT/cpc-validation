from __future__ import annotations

from src.backends.fpga_ccir import (
    FPGA_SPECIFICATION,
)
from src.backends.fpga_prepare import (
    FPGA_PREPARATION_ID,
)
from src.physical_fpga_profile import (
    PHYSICAL_FPGA_PROFILE,
    PHYSICAL_FPGA_PROFILE_ID,
    PhysicalFPGAProfile,
)


def test_physical_fpga_profile_extends_existing_fpga_backend() -> None:
    profile = PHYSICAL_FPGA_PROFILE

    assert profile.backend_id == (
        FPGA_SPECIFICATION.backend_id
    )

    assert profile.backend_version == (
        FPGA_SPECIFICATION.backend_version
    )

    assert dict(
        FPGA_SPECIFICATION.fixed_parameters
    )["hdl_target"] == profile.hdl_target

    assert FPGA_PREPARATION_ID == (
        "fpga.verilog.v1"
    )


def test_physical_fpga_profile_has_distinct_identity() -> None:
    assert PHYSICAL_FPGA_PROFILE_ID == (
        "fpga.physical-device.v1"
    )

    assert (
        PHYSICAL_FPGA_PROFILE_ID
        != FPGA_PREPARATION_ID
    )


def test_physical_fpga_profile_requires_complete_deployment_chain() -> None:
    stages = PHYSICAL_FPGA_PROFILE.realization_stages

    assert stages == (
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


def test_physical_fpga_profile_is_vendor_neutral() -> None:
    text = repr(
        PHYSICAL_FPGA_PROFILE
    ).lower()

    for vendor_term in (
        "xilinx",
        "amd",
        "intel",
        "altera",
        "lattice",
        "vivado",
        "quartus",
        "yosys",
        "nextpnr",
    ):
        assert vendor_term not in text


def test_physical_fpga_evidence_profile_is_complete() -> None:
    evidence = (
        PHYSICAL_FPGA_PROFILE.evidence_profile()
    )

    assert evidence.profile_id == (
        "fpga.physical-device.v1"
    )

    assert evidence.required_substrate_fields == (
        "board_id",
        "device_family",
        "device_id",
        "device_part",
    )

    assert (
        evidence.required_instrumentation_fields
        == (
            "observation_interface",
            "programming_interface",
            "stimulus_interface",
        )
    )

    assert evidence.required_calibration_fields == (
        "timing_validation_id",
    )

    assert evidence.required_evidence_types == (
        "bitstream",
        "build-report",
        "measurement-log",
        "programming-log",
        "timing-report",
    )


def test_profile_does_not_claim_physical_execution() -> None:
    profile = PHYSICAL_FPGA_PROFILE

    names = {
        field
        for field in profile.__dataclass_fields__
    }

    assert "executed" not in names
    assert "physical_execution_pass" not in names
    assert "semantic_match" not in names
    assert "decoded" not in names
    assert "reference" not in names


def test_profile_rejects_duplicate_realization_stages() -> None:
    try:
        PhysicalFPGAProfile(
            realization_stages=(
                "synthesis",
                "synthesis",
            ),
        )
    except ValueError as exc:
        assert "must be unique" in str(exc)
    else:
        raise AssertionError(
            "duplicate realization stages were accepted"
        )
