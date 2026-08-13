from __future__ import annotations

import pytest

from src.backends.fpga_ccir import FPGABackend
from src.backends.fpga_prepare import prepare_fpga_execution
from src.ccir_lower_parity import (
    lower_parity_instance_to_ccir,
)
from src.compiler import DEFAULT_XOR_INSTANCE
from src.physical_fpga_output_wrapper import (
    FPGA_PHYSICAL_RESULT_PORT,
    FPGA_PHYSICAL_TOP_MODULE,
    FPGA_PHYSICAL_WRAPPER_ID,
    wrap_fpga_physical_output,
)
from src.physical_fpga_synthesis import (
    project_fpga_synthesis_source,
)


def _synthesis(
    x0: int = 0,
    x3: int = 1,
):
    program = lower_parity_instance_to_ccir(
        DEFAULT_XOR_INSTANCE
    )

    artifact = FPGABackend().compile(
        program
    )

    prepared = prepare_fpga_execution(
        program,
        artifact,
        {
            0: x0,
            3: x3,
        },
    )

    return project_fpga_synthesis_source(
        prepared
    )


def test_wrapper_has_explicit_identity() -> None:
    wrapped = wrap_fpga_physical_output(
        _synthesis()
    )

    assert wrapped.wrapper_id == (
        FPGA_PHYSICAL_WRAPPER_ID
    )

    assert wrapped.top_module == (
        FPGA_PHYSICAL_TOP_MODULE
    )

    assert wrapped.result_port == (
        FPGA_PHYSICAL_RESULT_PORT
    )


def test_wrapper_binds_synthesis_source() -> None:
    synthesis = _synthesis()

    wrapped = wrap_fpga_physical_output(
        synthesis
    )

    assert wrapped.synthesis_source_sha256 == (
        synthesis.source_sha256
    )


def test_wrapper_preserves_synthesis_source_as_prefix() -> None:
    synthesis = _synthesis()

    wrapped = wrap_fpga_physical_output(
        synthesis
    )

    assert wrapped.source.startswith(
        synthesis.source.rstrip()
    )


def test_wrapper_exposes_result_without_inversion() -> None:
    wrapped = wrap_fpga_physical_output(
        _synthesis()
    )

    assert "module cpc_physical_top(" in (
        wrapped.source
    )

    assert "output wire result_out" in (
        wrapped.source
    )

    assert ".result(result)" in wrapped.source

    assert "assign result_out = result;" in (
        wrapped.source
    )

    assert "assign result_out = ~result;" not in (
        wrapped.source
    )


def test_wrapper_contains_no_board_binding() -> None:
    wrapped = wrap_fpga_physical_output(
        _synthesis()
    )

    text = wrapped.source.lower()

    for forbidden in (
        "icebreaker",
        "ledr_n",
        "ledg_n",
        "pin 11",
        "set_io",
        "sg48",
    ):
        assert forbidden not in text


def test_wrapper_contains_no_physical_execution_claim() -> None:
    wrapped = wrap_fpga_physical_output(
        _synthesis()
    )

    names = {
        field
        for field in wrapped.__dataclass_fields__
    }

    assert wrapped.source

    for forbidden in (
        "place_route_complete",
        "bitstream_complete",
        "programmed",
        "executed",
        "observed",
        "semantic_match",
        "overall_pass",
    ):
        assert forbidden not in names


def test_wrapper_is_deterministic() -> None:
    first = wrap_fpga_physical_output(
        _synthesis()
    )

    second = wrap_fpga_physical_output(
        _synthesis()
    )

    assert first == second


def test_boundary_change_changes_wrapped_source() -> None:
    first = wrap_fpga_physical_output(
        _synthesis(
            0,
            1,
        )
    )

    second = wrap_fpga_physical_output(
        _synthesis(
            1,
            0,
        )
    )

    assert first.source != second.source
    assert first.source_sha256 != (
        second.source_sha256
    )


def test_wrapper_rejects_missing_execution_module() -> None:
    import hashlib

    synthesis = _synthesis()

    mutated_source = synthesis.source.replace(
        "module cpc_fpga_execution(",
        "module cpc_other_execution(",
        1,
    )

    mutated = synthesis.__class__(
        projection_id=synthesis.projection_id,
        prepared_execution_hash=(
            synthesis.prepared_execution_hash
        ),
        source=mutated_source,
        source_sha256=(
            "sha256:"
            + hashlib.sha256(
                mutated_source.encode("utf-8")
            ).hexdigest()
        ),
    )

    with pytest.raises(
        ValueError,
        match="lacks canonical FPGA execution module",
    ):
        wrap_fpga_physical_output(
            mutated
        )
