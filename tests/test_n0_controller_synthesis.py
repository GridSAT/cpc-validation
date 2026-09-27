from __future__ import annotations

import subprocess
from pathlib import Path

from src.n0_controller_synthesis import (
    EXPECTED_PORTS,
    N0_CONTROLLER_SYNTHESIS_ID,
    N0_CONTROLLER_SYNTHESIS_SCHEMA,
    audit_synthesized_json,
    synthesize_n0_controller,
)


ROOT = Path(
    __file__
).resolve().parents[1]

RTL = (
    ROOT
    / "rtl"
    / "n0_controller.v"
)


def test_controller_synthesizes_with_yosys():
    result, content = (
        synthesize_n0_controller(
            rtl_path=RTL
        )
    )

    assert (
        result.synthesis_id
        == N0_CONTROLLER_SYNTHESIS_ID
    )

    assert (
        result.schema
        == N0_CONTROLLER_SYNTHESIS_SCHEMA
    )

    assert (
        result.synthesis_complete
        is True
    )

    assert (
        result.synthesized_json_size
        == len(content)
    )

    assert (
        result.port_count
        == len(
            EXPECTED_PORTS
        )
    )

    assert (
        result.cell_count
        > 0
    )


def test_synthesis_is_byte_deterministic():
    first, first_content = (
        synthesize_n0_controller(
            rtl_path=RTL
        )
    )

    second, second_content = (
        synthesize_n0_controller(
            rtl_path=RTL
        )
    )

    assert (
        first_content
        == second_content
    )

    assert (
        first.synthesized_json_sha256
        == second.synthesized_json_sha256
    )

    assert (
        first.source_sha256
        == second.source_sha256
    )


def test_structural_audit_accepts_synthesized_controller():
    _, content = (
        synthesize_n0_controller(
            rtl_path=RTL
        )
    )

    (
        top,
        port_count,
        cell_count,
    ) = audit_synthesized_json(
        content
    )

    assert (
        top
        == "cpc_shor_n0_controller"
    )

    assert (
        port_count
        == len(
            EXPECTED_PORTS
        )
    )

    assert cell_count > 0


def test_synthesis_claims_no_later_physical_stage():
    result, _ = (
        synthesize_n0_controller(
            rtl_path=RTL
        )
    )

    assert (
        result.physical_constraints_complete
        is False
    )

    assert (
        result.place_route_complete
        is False
    )

    assert (
        result.bitstream_complete
        is False
    )

    assert (
        result.physical_programming
        is False
    )

    assert (
        result.physical_execution
        is False
    )


def test_synthesis_function_invokes_yosys_only(
    monkeypatch,
):
    actual_run = subprocess.run
    commands: list[str] = []

    def recording_run(
        args,
        *pargs,
        **kwargs,
    ):
        executable = str(
            args[0]
        )

        commands.append(
            executable
        )

        return actual_run(
            args,
            *pargs,
            **kwargs,
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        recording_run,
    )

    synthesize_n0_controller(
        rtl_path=RTL
    )

    assert commands

    assert set(
        commands
    ) == {
        "yosys",
    }

    assert (
        "nextpnr-ice40"
        not in commands
    )

    assert (
        "icepack"
        not in commands
    )

    assert (
        "iceprog"
        not in commands
    )


def test_synthesized_output_contains_no_truth_interface():
    _, content = (
        synthesize_n0_controller(
            rtl_path=RTL
        )
    )

    text = (
        content.decode(
            "utf-8"
        ).lower()
    )

    for token in (
        "truth",
        "expected_answer",
        "semantic_answer",
        "phase_estimate",
    ):
        assert token not in text
