from __future__ import annotations

from pathlib import Path

import pytest

from src.physical_fpga_output_wrapper import (
    FPGA_PHYSICAL_RESULT_PORT,
)
from src.physical_lattice_up5k_breakout_constraints import (
    LATTICE_UP5K_P1_BOARD_NET,
    LATTICE_UP5K_P1_CONSTRAINT,
    LATTICE_UP5K_P1_CONSTRAINT_ID,
    LATTICE_UP5K_P1_PACKAGE_PIN,
    LATTICE_UP5K_P1_PCF_PATH,
    LatticeUP5KBreakoutConstraint,
)
from src.physical_lattice_up5k_breakout_target import (
    LATTICE_UP5K_BREAKOUT_TARGET_ID,
)


def test_constraint_has_explicit_identity() -> None:
    assert LATTICE_UP5K_P1_CONSTRAINT_ID == (
        "lattice-ice40up5k-b-evn-p1-red-led.v1"
    )

    assert LATTICE_UP5K_P1_CONSTRAINT.constraint_id == (
        LATTICE_UP5K_P1_CONSTRAINT_ID
    )


def test_constraint_binds_lattice_target() -> None:
    assert LATTICE_UP5K_P1_CONSTRAINT.target_id == (
        LATTICE_UP5K_BREAKOUT_TARGET_ID
    )


def test_constraint_binds_physical_result_port() -> None:
    assert (
        LATTICE_UP5K_P1_CONSTRAINT.logical_port
        == FPGA_PHYSICAL_RESULT_PORT
    )


def test_constraint_binds_red_led_net() -> None:
    constraint = LATTICE_UP5K_P1_CONSTRAINT

    assert constraint.board_net == (
        LATTICE_UP5K_P1_BOARD_NET
    )

    assert constraint.board_net == "LED_RED"

    assert constraint.package_pin == (
        LATTICE_UP5K_P1_PACKAGE_PIN
    )

    assert constraint.package_pin == "41"


def test_constraint_records_manufacturer_source() -> None:
    constraint = LATTICE_UP5K_P1_CONSTRAINT

    assert constraint.source_document == (
        "FPGA-UG-02001"
    )

    assert constraint.source_document_version == "1.2"

    assert constraint.source_figure == (
        "Figure A.3 DUT Connection"
    )


def test_constraint_emits_exact_pcf() -> None:
    assert LATTICE_UP5K_P1_CONSTRAINT.pcf_text == (
        "set_io result_out 41\n"
    )


def test_repository_pcf_matches_constraint_model() -> None:
    path = Path(
        LATTICE_UP5K_P1_PCF_PATH
    )

    assert path.is_file()

    assert path.read_text(
        encoding="utf-8"
    ) == LATTICE_UP5K_P1_CONSTRAINT.pcf_text


def test_constraint_pcf_digest_is_content_addressed() -> None:
    digest = (
        LATTICE_UP5K_P1_CONSTRAINT.pcf_sha256
    )

    assert digest.startswith(
        "sha256:"
    )

    assert len(digest) == (
        len("sha256:") + 64
    )


def test_constraint_contains_no_semantic_or_execution_claim() -> None:
    names = {
        field
        for field in (
            LATTICE_UP5K_P1_CONSTRAINT.__dataclass_fields__
        )
    }

    for forbidden in (
        "expected_result",
        "decoded_result",
        "semantic_match",
        "programmed",
        "executed",
        "observed",
        "overall_pass",
    ):
        assert forbidden not in names


def test_constraint_rejects_empty_identity() -> None:
    with pytest.raises(
        ValueError,
        match="constraint_id must be a non-empty string",
    ):
        LatticeUP5KBreakoutConstraint(
            constraint_id="",
        )
