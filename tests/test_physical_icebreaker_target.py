from __future__ import annotations

import pytest

from src.physical_fpga_profile import (
    PHYSICAL_FPGA_PROFILE,
    PHYSICAL_FPGA_PROFILE_ID,
)
from src.physical_icebreaker_target import (
    ICEBREAKER_TARGET,
    ICEBREAKER_TARGET_ID,
    IceBreakerTarget,
)


def test_icebreaker_target_has_explicit_identity() -> None:
    assert ICEBREAKER_TARGET_ID == (
        "icebreaker-up5k-sg48.v1"
    )

    assert ICEBREAKER_TARGET.target_id == (
        ICEBREAKER_TARGET_ID
    )


def test_icebreaker_target_binds_physical_fpga_profile() -> None:
    target = ICEBREAKER_TARGET

    assert target.physical_profile_id == (
        PHYSICAL_FPGA_PROFILE_ID
    )

    assert target.backend_id == (
        PHYSICAL_FPGA_PROFILE.backend_id
    )

    assert target.backend_version == (
        PHYSICAL_FPGA_PROFILE.backend_version
    )


def test_icebreaker_target_declares_device() -> None:
    target = ICEBREAKER_TARGET

    assert target.board_family == "icebreaker"
    assert target.device_family == "ice40up5k"
    assert target.device_part == "up5k-sg48"

    assert target.nextpnr_device == "up5k"
    assert target.nextpnr_package == "sg48"


def test_icebreaker_target_declares_open_toolchain() -> None:
    target = ICEBREAKER_TARGET

    assert target.synthesis_tool == "yosys"
    assert target.place_route_tool == "nextpnr-ice40"
    assert target.bitstream_tool == "icepack"
    assert target.programmer == "iceprog"


def test_icebreaker_target_declares_bitstream_format() -> None:
    assert ICEBREAKER_TARGET.bitstream_format == (
        "ice40-asc-bin"
    )


def test_target_contains_no_physical_execution_claim() -> None:
    names = {
        field
        for field in ICEBREAKER_TARGET.__dataclass_fields__
    }

    for forbidden in (
        "built",
        "programmed",
        "executed",
        "observed",
        "decoded",
        "semantic_match",
        "overall_pass",
    ):
        assert forbidden not in names


def test_target_does_not_embed_constraint_identity() -> None:
    names = {
        field
        for field in ICEBREAKER_TARGET.__dataclass_fields__
    }

    assert "pcf" not in names
    assert "constraints" not in names
    assert "constraint_sha256" not in names


def test_target_rejects_empty_identity() -> None:
    with pytest.raises(
        ValueError,
        match="target_id must be a non-empty string",
    ):
        IceBreakerTarget(
            target_id="",
        )
