from __future__ import annotations

from dataclasses import replace

import pytest

from src.backends.fpga_ccir import FPGABackend
from src.backends.fpga_prepare import prepare_fpga_execution
from src.ccir_lower_parity import (
    lower_parity_instance_to_ccir,
)
from src.compiler import DEFAULT_XOR_INSTANCE
from src.physical_execution_evidence import (
    prepared_execution_hash,
)
from src.physical_fpga_synthesis import (
    FPGA_SYNTHESIS_PROJECTION_ID,
    project_fpga_synthesis_source,
)


def _prepared(
    boundary_values: dict[int, int] | None = None,
):
    program = lower_parity_instance_to_ccir(
        DEFAULT_XOR_INSTANCE
    )

    artifact = FPGABackend().compile(
        program
    )

    return prepare_fpga_execution(
        program,
        artifact,
        boundary_values or {
            0: 0,
            3: 1,
        },
    )


def test_projection_has_explicit_identity() -> None:
    projected = project_fpga_synthesis_source(
        _prepared()
    )

    assert projected.projection_id == (
        FPGA_SYNTHESIS_PROJECTION_ID
    )


def test_projection_binds_prepared_execution() -> None:
    prepared = _prepared()

    projected = project_fpga_synthesis_source(
        prepared
    )

    assert projected.prepared_execution_hash == (
        prepared_execution_hash(
            prepared
        )
    )


def test_projection_removes_only_simulation_readout() -> None:
    prepared = _prepared()

    projected = project_fpga_synthesis_source(
        prepared
    )

    expected = prepared.payload.replace(
        "\n"
        "  initial begin\n"
        "    #1;\n"
        '    $display("CPC_RESULT=%b", result);\n'
        "    $finish;\n"
        "  end\n",
        "\n",
        1,
    )

    assert projected.source == expected

    assert "$display" not in projected.source
    assert "$finish" not in projected.source
    assert "#1;" not in projected.source


def test_projection_preserves_combinational_result_logic() -> None:
    projected = project_fpga_synthesis_source(
        _prepared()
    )

    assert (
        "assign result = "
        "completion_0 | completion_1 | "
        "completion_2 | completion_3;"
        in projected.source
    )

    assert "module cpc_fpga_execution(" in (
        projected.source
    )

    assert projected.source.rstrip().endswith(
        "endmodule"
    )


def test_projection_is_deterministic() -> None:
    first = project_fpga_synthesis_source(
        _prepared()
    )

    second = project_fpga_synthesis_source(
        _prepared()
    )

    assert first == second


def test_boundary_change_changes_projected_source() -> None:
    first = project_fpga_synthesis_source(
        _prepared(
            {
                0: 0,
                3: 1,
            }
        )
    )

    second = project_fpga_synthesis_source(
        _prepared(
            {
                0: 1,
                3: 0,
            }
        )
    )

    assert first.source != second.source
    assert first.source_sha256 != second.source_sha256

    assert "assign x0 = 1'b0;" in first.source
    assert "assign x0 = 1'b1;" in second.source


def test_projection_rejects_non_fpga_backend() -> None:
    prepared = replace(
        _prepared(),
        backend_id="digital",
    )

    with pytest.raises(
        ValueError,
        match="requires fpga backend",
    ):
        project_fpga_synthesis_source(
            prepared
        )


def test_projection_rejects_unknown_preparation() -> None:
    prepared = _prepared()

    metadata = dict(
        prepared.metadata
    )
    metadata["preparation_id"] = "fpga.other.v1"

    prepared = replace(
        prepared,
        metadata=tuple(
            sorted(
                metadata.items()
            )
        ),
    )

    with pytest.raises(
        ValueError,
        match="unsupported FPGA preparation identity",
    ):
        project_fpga_synthesis_source(
            prepared
        )


def test_projection_fails_closed_when_block_is_missing() -> None:
    prepared = _prepared()

    prepared = replace(
        prepared,
        payload=prepared.payload.replace(
            "$finish;",
            "$stop;",
        ),
    )

    with pytest.raises(
        ValueError,
        match="exactly one canonical simulation readout block",
    ):
        project_fpga_synthesis_source(
            prepared
        )


def test_projection_fails_closed_on_duplicate_block() -> None:
    prepared = _prepared()

    block = (
        "\n"
        "  initial begin\n"
        "    #1;\n"
        '    $display("CPC_RESULT=%b", result);\n'
        "    $finish;\n"
        "  end\n"
    )

    prepared = replace(
        prepared,
        payload=prepared.payload.replace(
            "\nendmodule\n",
            block + "\nendmodule\n",
        ),
    )

    with pytest.raises(
        ValueError,
        match="exactly one canonical simulation readout block",
    ):
        project_fpga_synthesis_source(
            prepared
        )


def test_source_digest_is_content_addressed() -> None:
    projected = project_fpga_synthesis_source(
        _prepared()
    )

    assert projected.source_sha256.startswith(
        "sha256:"
    )

    assert len(projected.source_sha256) == (
        len("sha256:") + 64
    )
