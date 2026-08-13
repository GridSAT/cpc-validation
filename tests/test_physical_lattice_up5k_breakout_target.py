from __future__ import annotations

import pytest

from src.physical_fpga_profile import (
    PHYSICAL_FPGA_PROFILE,
    PHYSICAL_FPGA_PROFILE_ID,
)
from src.physical_lattice_up5k_breakout_target import (
    LATTICE_UP5K_BREAKOUT_TARGET,
    LATTICE_UP5K_BREAKOUT_TARGET_ID,
    LatticeUP5KBreakoutTarget,
)


def test_target_has_explicit_identity() -> None:
    assert LATTICE_UP5K_BREAKOUT_TARGET_ID == (
        "lattice-ice40up5k-b-evn-sg48.v1"
    )

    assert LATTICE_UP5K_BREAKOUT_TARGET.target_id == (
        LATTICE_UP5K_BREAKOUT_TARGET_ID
    )


def test_target_binds_physical_fpga_profile() -> None:
    target = LATTICE_UP5K_BREAKOUT_TARGET

    assert target.physical_profile_id == (
        PHYSICAL_FPGA_PROFILE_ID
    )

    assert target.backend_id == (
        PHYSICAL_FPGA_PROFILE.backend_id
    )

    assert target.backend_version == (
        PHYSICAL_FPGA_PROFILE.backend_version
    )


def test_target_declares_lattice_board_identity() -> None:
    target = LATTICE_UP5K_BREAKOUT_TARGET

    assert target.manufacturer == (
        "Lattice Semiconductor"
    )

    assert target.board_name == (
        "iCE40 UltraPlus Breakout Board"
    )

    assert target.ordering_part_number == (
        "iCE40UP5K-B-EVN"
    )


def test_target_declares_up5k_sg48_device() -> None:
    target = LATTICE_UP5K_BREAKOUT_TARGET

    assert target.device_family == "ice40up5k"
    assert target.device_part == "iCE40UP5K"
    assert target.package == "sg48"

    assert target.nextpnr_device == "up5k"
    assert target.nextpnr_package == "sg48"


def test_target_declares_build_toolchain() -> None:
    target = LATTICE_UP5K_BREAKOUT_TARGET

    assert target.synthesis_tool == "yosys"
    assert target.place_route_tool == "nextpnr-ice40"
    assert target.bitstream_tool == "icepack"


def test_target_declares_bitstream_format() -> None:
    assert (
        LATTICE_UP5K_BREAKOUT_TARGET.bitstream_format
        == "ice40-asc-bin"
    )


def test_target_contains_no_constraint_binding() -> None:
    names = {
        field
        for field in (
            LATTICE_UP5K_BREAKOUT_TARGET.__dataclass_fields__
        )
    }

    for forbidden in (
        "pcf",
        "constraints",
        "constraint_sha256",
        "result_pin",
        "led_pin",
    ):
        assert forbidden not in names


def test_target_contains_no_programming_or_execution_claim() -> None:
    names = {
        field
        for field in (
            LATTICE_UP5K_BREAKOUT_TARGET.__dataclass_fields__
        )
    }

    for forbidden in (
        "programmer",
        "programmed",
        "executed",
        "observed",
        "semantic_match",
        "overall_pass",
    ):
        assert forbidden not in names


def test_target_rejects_empty_identity() -> None:
    with pytest.raises(
        ValueError,
        match="target_id must be a non-empty string",
    ):
        LatticeUP5KBreakoutTarget(
            target_id="",
        )
