from __future__ import annotations

import hashlib
import json

import pytest

from src.physical_build_provenance import (
    PHYSICAL_BUILD_MANIFEST_SCHEMA,
    BuildInputRecord,
    BuildToolIdentity,
    PhysicalBuildManifest,
    build_manifest_for_prepared_execution,
)
from src.physical_execution_evidence import (
    prepared_execution_hash,
)
from src.physical_fpga_profile import (
    PHYSICAL_FPGA_PROFILE_ID,
)
from src.prepared_execution import (
    PreparedExecution,
)


VERILOG = b"module cpc(output wire result); assign result=1'b1; endmodule\n"
BITSTREAM = b"synthetic-bitstream-for-rfc0009-test"


def _sha256(
    content: bytes,
) -> str:
    return (
        "sha256:"
        + hashlib.sha256(
            content
        ).hexdigest()
    )


def _prepared() -> PreparedExecution:
    return PreparedExecution(
        backend_id="fpga",
        backend_version="1",
        payload=VERILOG.decode(
            "utf-8"
        ),
        interface=(
            ("readout_signal", "result"),
        ),
        decoder_specification=(
            ("readout_signal", "result"),
        ),
        metadata=(
            (
                "preparation_id",
                "fpga.verilog.v1",
            ),
        ),
    )


def _tools() -> tuple[
    BuildToolIdentity,
    ...
]:
    return (
        BuildToolIdentity(
            stage="place-route",
            tool="example-pnr",
            version="1.0",
        ),
        BuildToolIdentity(
            stage="synthesis",
            tool="example-synth",
            version="1.0",
        ),
    )


def _inputs() -> tuple[
    BuildInputRecord,
    ...
]:
    return (
        BuildInputRecord(
            input_id="constraints",
            media_type="text/plain",
            sha256=_sha256(
                b"constraints\n"
            ),
        ),
        BuildInputRecord(
            input_id="prepared-verilog",
            media_type="text/x-verilog",
            sha256=_sha256(
                VERILOG
            ),
        ),
    )


def _manifest() -> PhysicalBuildManifest:
    return build_manifest_for_prepared_execution(
        prepared=_prepared(),
        physical_profile_id=(
            PHYSICAL_FPGA_PROFILE_ID
        ),
        device_family="example-family",
        device_part="example-part",
        tools=_tools(),
        inputs=_inputs(),
        bitstream_format="example-bitstream",
        bitstream_sha256=_sha256(
            BITSTREAM
        ),
        metadata=(
            ("build_mode", "deterministic"),
        ),
    )


def test_build_manifest_has_explicit_schema() -> None:
    manifest = _manifest()

    assert manifest.schema == (
        PHYSICAL_BUILD_MANIFEST_SCHEMA
    )

    assert manifest.schema == (
        "cpc.physical-build-manifest.v1"
    )


def test_build_manifest_binds_prepared_execution() -> None:
    manifest = _manifest()

    assert (
        manifest.prepared_execution_hash
        == prepared_execution_hash(
            _prepared()
        )
    )


def test_build_manifest_preserves_backend_identity() -> None:
    manifest = _manifest()

    assert manifest.backend_id == "fpga"
    assert manifest.backend_version == "1"

    assert manifest.physical_profile_id == (
        "fpga.physical-device.v1"
    )


def test_build_manifest_records_toolchain_identity() -> None:
    manifest = _manifest()

    assert manifest.tools == (
        BuildToolIdentity(
            stage="place-route",
            tool="example-pnr",
            version="1.0",
        ),
        BuildToolIdentity(
            stage="synthesis",
            tool="example-synth",
            version="1.0",
        ),
    )


def test_build_manifest_records_input_digests() -> None:
    manifest = _manifest()

    inputs = {
        item.input_id: item.sha256
        for item in manifest.inputs
    }

    assert inputs[
        "prepared-verilog"
    ] == _sha256(
        VERILOG
    )


def test_build_manifest_records_bitstream_identity() -> None:
    manifest = _manifest()

    assert manifest.bitstream_sha256 == (
        _sha256(
            BITSTREAM
        )
    )


def test_manifest_hash_is_deterministic() -> None:
    first = _manifest()
    second = _manifest()

    assert (
        first.manifest_hash
        == second.manifest_hash
    )

    assert first.manifest_hash.startswith(
        "sha256:"
    )


def test_manifest_hash_changes_with_bitstream() -> None:
    first = _manifest()

    second = build_manifest_for_prepared_execution(
        prepared=_prepared(),
        physical_profile_id=(
            PHYSICAL_FPGA_PROFILE_ID
        ),
        device_family=(
            first.device_family
        ),
        device_part=(
            first.device_part
        ),
        tools=first.tools,
        inputs=first.inputs,
        bitstream_format=(
            first.bitstream_format
        ),
        bitstream_sha256=_sha256(
            b"different-bitstream"
        ),
        metadata=first.metadata,
    )

    assert (
        first.manifest_hash
        != second.manifest_hash
    )


def test_json_contains_manifest_hash() -> None:
    manifest = _manifest()

    data = json.loads(
        manifest.to_json()
    )

    assert data["manifest_hash"] == (
        manifest.manifest_hash
    )


def test_build_tool_stages_must_be_sorted() -> None:
    with pytest.raises(
        ValueError,
        match="build tools must be sorted by stage",
    ):
        PhysicalBuildManifest(
            backend_id="fpga",
            backend_version="1",
            physical_profile_id="profile",
            prepared_execution_hash=(
                "sha256:" + "0" * 64
            ),
            device_family="family",
            device_part="part",
            tools=(
                BuildToolIdentity(
                    stage="synthesis",
                    tool="synth",
                    version="1",
                ),
                BuildToolIdentity(
                    stage="place-route",
                    tool="pnr",
                    version="1",
                ),
            ),
            inputs=(),
            bitstream_format="bit",
            bitstream_sha256=(
                "sha256:" + "1" * 64
            ),
        )


def test_build_input_ids_must_be_unique() -> None:
    record = BuildInputRecord(
        input_id="input",
        media_type="text/plain",
        sha256=(
            "sha256:" + "0" * 64
        ),
    )

    with pytest.raises(
        ValueError,
        match="build input IDs must be unique",
    ):
        PhysicalBuildManifest(
            backend_id="fpga",
            backend_version="1",
            physical_profile_id="profile",
            prepared_execution_hash=(
                "sha256:" + "0" * 64
            ),
            device_family="family",
            device_part="part",
            tools=(),
            inputs=(
                record,
                record,
            ),
            bitstream_format="bit",
            bitstream_sha256=(
                "sha256:" + "1" * 64
            ),
        )


def test_build_manifest_contains_no_execution_claim() -> None:
    names = {
        field
        for field in _manifest().__dataclass_fields__
    }

    assert "programmed" not in names
    assert "executed" not in names
    assert "observed" not in names
    assert "decoded" not in names
    assert "semantic_match" not in names
    assert "overall_pass" not in names
