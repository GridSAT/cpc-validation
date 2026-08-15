from __future__ import annotations

from pathlib import Path

import pytest

from src.backends.fpga_ccir import FPGABackend
from src.backends.fpga_prepare import prepare_fpga_execution
from src.ccir_lower_parity import (
    lower_parity_instance_to_ccir,
)
from src.compiler import DEFAULT_XOR_INSTANCE
from src.physical_fpga_output_wrapper import (
    wrap_fpga_physical_output,
)
from src.physical_fpga_synthesis import (
    project_fpga_synthesis_source,
)
from src.physical_lattice_up5k_build import (
    LATTICE_UP5K_BUILD_ID,
    LATTICE_UP5K_TIMING_VALIDATION_ID,
    build_lattice_up5k_bitstream,
)


def _inputs():
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
            0: 0,
            3: 1,
        },
    )

    synthesis = project_fpga_synthesis_source(
        prepared
    )

    physical_source = wrap_fpga_physical_output(
        synthesis
    )

    return prepared, physical_source


def _build():
    prepared, physical_source = _inputs()

    return build_lattice_up5k_bitstream(
        prepared=prepared,
        physical_source=physical_source,
    )


def test_build_has_explicit_identity() -> None:
    build = _build()

    assert build.build_id == (
        LATTICE_UP5K_BUILD_ID
    )


def test_build_produces_non_empty_bitstream() -> None:
    build = _build()

    assert isinstance(
        build.bitstream,
        bytes,
    )

    assert build.bitstream


def test_build_records_artifact_digests() -> None:
    build = _build()

    for digest in (
        build.verilog_sha256,
        build.pcf_sha256,
        build.asc_sha256,
        build.bitstream_sha256,
        build.timing_report_sha256,
    ):
        assert digest.startswith(
            "sha256:"
        )

        assert len(digest) == (
            len("sha256:") + 64
        )


def test_manifest_binds_generated_bitstream() -> None:
    build = _build()

    assert (
        build.manifest.bitstream_sha256
        == build.bitstream_sha256
    )


def test_build_retains_static_timing_validation() -> None:
    build = _build()

    assert build.timing_report
    assert LATTICE_UP5K_TIMING_VALIDATION_ID.encode() in (
        build.timing_report
    )
    assert b'"clock_domains": 0' in build.timing_report
    assert b'"interior_timing_paths_found": false' in (
        build.timing_report
    )


def test_manifest_records_target_and_constraint() -> None:
    build = _build()

    metadata = dict(
        build.manifest.metadata
    )

    assert metadata["build_id"] == (
        LATTICE_UP5K_BUILD_ID
    )

    assert metadata["target_id"] == (
        "lattice-ice40up5k-b-evn-sg48.v1"
    )

    assert metadata["constraint_id"] == (
        "lattice-ice40up5k-b-evn-p1-red-led.v1"
    )


def test_manifest_records_open_toolchain() -> None:
    build = _build()

    tools = {
        item.stage: item.tool
        for item in build.manifest.tools
    }

    assert tools == {
        "bitstream-generation": "icepack",
        "place-route": "nextpnr-ice40",
        "synthesis": "yosys",
    }


def test_manifest_records_build_inputs() -> None:
    build = _build()

    inputs = {
        item.input_id: item.sha256
        for item in build.manifest.inputs
    }

    assert inputs["physical-verilog"] == (
        build.verilog_sha256
    )

    assert inputs["physical-constraints"] == (
        build.pcf_sha256
    )


def test_build_contains_no_execution_claim() -> None:
    build = _build()

    names = set(
        build.__dataclass_fields__
    )

    for forbidden in (
        "programmed",
        "executed",
        "observed",
        "decoded",
        "semantic_match",
        "overall_pass",
    ):
        assert forbidden not in names


def test_build_rejects_modified_constraint(
    tmp_path: Path,
) -> None:
    prepared, physical_source = _inputs()

    modified = tmp_path / "modified.pcf"

    modified.write_text(
        "set_io result_out 42\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match=(
            "physical constraint file does not match "
            "accepted constraint"
        ),
    ):
        build_lattice_up5k_bitstream(
            prepared=prepared,
            physical_source=physical_source,
            pcf_path=modified,
        )


def test_build_is_deterministic() -> None:
    first = _build()
    second = _build()

    assert first.verilog_sha256 == (
        second.verilog_sha256
    )

    assert first.pcf_sha256 == (
        second.pcf_sha256
    )

    assert first.asc_sha256 == (
        second.asc_sha256
    )

    assert first.bitstream_sha256 == (
        second.bitstream_sha256
    )

    assert first.bitstream == (
        second.bitstream
    )

    assert first.timing_report_sha256 == (
        second.timing_report_sha256
    )

    assert first.timing_report == (
        second.timing_report
    )

    assert first.manifest.manifest_hash == (
        second.manifest.manifest_hash
    )
