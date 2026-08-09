from __future__ import annotations

import hashlib
import json

import pytest

from src.physical_build_provenance import (
    BuildInputRecord,
    BuildToolIdentity,
    build_manifest_for_prepared_execution,
)
from src.physical_device_programming import (
    DEVICE_PROGRAMMING_RECORD_SCHEMA,
    programming_record_from_build,
)
from src.physical_fpga_profile import (
    PHYSICAL_FPGA_PROFILE_ID,
)
from src.prepared_execution import (
    PreparedExecution,
)


def _sha256(
    content: bytes,
) -> str:
    return (
        "sha256:"
        + hashlib.sha256(
            content
        ).hexdigest()
    )


VERILOG = (
    b"module cpc(output wire result); "
    b"assign result=1'b1; endmodule\n"
)

BITSTREAM = b"synthetic-bitstream"
PROGRAMMING_LOG = b"programming completed\n"


def _prepared() -> PreparedExecution:
    return PreparedExecution(
        backend_id="fpga",
        backend_version="1",
        payload=VERILOG.decode("utf-8"),
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


def _build():
    return build_manifest_for_prepared_execution(
        prepared=_prepared(),
        physical_profile_id=(
            PHYSICAL_FPGA_PROFILE_ID
        ),
        device_family="example-family",
        device_part="example-part",
        tools=(
            BuildToolIdentity(
                stage="synthesis",
                tool="example-synth",
                version="1",
            ),
        ),
        inputs=(
            BuildInputRecord(
                input_id="prepared-verilog",
                media_type="text/x-verilog",
                sha256=_sha256(
                    VERILOG
                ),
            ),
        ),
        bitstream_format="example-bitstream",
        bitstream_sha256=_sha256(
            BITSTREAM
        ),
    )


def _record():
    return programming_record_from_build(
        build=_build(),
        board_id="board-001",
        device_id="device-001",
        programming_interface="jtag",
        programmer="example-programmer",
        programmer_version="1.0",
        programming_log_sha256=_sha256(
            PROGRAMMING_LOG
        ),
        metadata=(
            ("mode", "nonvolatile"),
        ),
    )


def test_programming_record_has_explicit_schema() -> None:
    record = _record()

    assert record.schema == (
        DEVICE_PROGRAMMING_RECORD_SCHEMA
    )

    assert record.schema == (
        "cpc.device-programming-record.v1"
    )


def test_programming_record_binds_build_manifest() -> None:
    build = _build()
    record = _record()

    assert (
        record.build_manifest_hash
        == build.manifest_hash
    )

    assert (
        record.bitstream_sha256
        == build.bitstream_sha256
    )


def test_programming_record_preserves_device_target() -> None:
    build = _build()
    record = _record()

    assert record.device_family == (
        build.device_family
    )

    assert record.device_part == (
        build.device_part
    )

    assert record.board_id == "board-001"
    assert record.device_id == "device-001"


def test_programming_record_records_programmer_identity() -> None:
    record = _record()

    assert record.programming_interface == "jtag"
    assert record.programmer == (
        "example-programmer"
    )
    assert record.programmer_version == "1.0"


def test_programming_record_commits_to_programming_log() -> None:
    assert (
        _record().programming_log_sha256
        == _sha256(
            PROGRAMMING_LOG
        )
    )


def test_programming_record_hash_is_deterministic() -> None:
    first = _record()
    second = _record()

    assert first.record_hash == (
        second.record_hash
    )

    assert first.record_hash.startswith(
        "sha256:"
    )


def test_programming_record_hash_changes_with_device() -> None:
    build = _build()

    first = programming_record_from_build(
        build=build,
        board_id="board-001",
        device_id="device-001",
        programming_interface="jtag",
        programmer="programmer",
        programmer_version="1",
        programming_log_sha256=_sha256(
            PROGRAMMING_LOG
        ),
    )

    second = programming_record_from_build(
        build=build,
        board_id="board-002",
        device_id="device-002",
        programming_interface="jtag",
        programmer="programmer",
        programmer_version="1",
        programming_log_sha256=_sha256(
            PROGRAMMING_LOG
        ),
    )

    assert first.record_hash != (
        second.record_hash
    )


def test_json_contains_record_hash() -> None:
    record = _record()

    data = json.loads(
        record.to_json()
    )

    assert data["record_hash"] == (
        record.record_hash
    )


def test_programming_log_digest_must_be_valid() -> None:
    with pytest.raises(
        ValueError,
        match="programming_log_sha256",
    ):
        programming_record_from_build(
            build=_build(),
            board_id="board",
            device_id="device",
            programming_interface="jtag",
            programmer="programmer",
            programmer_version="1",
            programming_log_sha256="invalid",
        )


def test_programming_record_contains_no_execution_claim() -> None:
    names = {
        field
        for field in _record().__dataclass_fields__
    }

    assert "executed" not in names
    assert "observed" not in names
    assert "decoded" not in names
    assert "semantic_match" not in names
    assert "overall_pass" not in names
