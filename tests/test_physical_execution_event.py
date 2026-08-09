from __future__ import annotations

import hashlib
import json

import pytest

from src.observable_execution import (
    ObservableExecution,
)
from src.physical_build_provenance import (
    BuildInputRecord,
    BuildToolIdentity,
    build_manifest_for_prepared_execution,
)
from src.physical_device_programming import (
    programming_record_from_build,
)
from src.physical_execution_event import (
    PHYSICAL_EXECUTION_EVENT_SCHEMA,
    execution_event_from_records,
)
from src.physical_execution_evidence import (
    observable_execution_hash,
    prepared_execution_hash,
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

STIMULUS_LOG = b"stimulus x0=0 x3=1\n"

MEASUREMENT_LOG = b"result=1\n"


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


def _observable() -> ObservableExecution:
    return ObservableExecution(
        backend_id="fpga",
        backend_version="1",
        observations=(
            ("result_bit", 1),
        ),
        metadata=(
            (
                "execution_engine",
                "physical-fpga-device",
            ),
            (
                "execution_engine_version",
                "device-001",
            ),
            (
                "execution_id",
                "fpga.physical-execution.v1",
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


def _programming():
    return programming_record_from_build(
        build=_build(),
        board_id="board-001",
        device_id="device-001",
        programming_interface="jtag",
        programmer="example-programmer",
        programmer_version="1",
        programming_log_sha256=_sha256(
            PROGRAMMING_LOG
        ),
    )


def _event():
    return execution_event_from_records(
        programming=_programming(),
        prepared=_prepared(),
        observable=_observable(),
        stimulus_interface="gpio",
        observation_interface="gpio",
        stimulus_record_sha256=_sha256(
            STIMULUS_LOG
        ),
        measurement_record_sha256=_sha256(
            MEASUREMENT_LOG
        ),
        metadata=(
            ("mode", "single-shot"),
        ),
    )


def test_execution_event_has_explicit_schema() -> None:
    event = _event()

    assert event.schema == (
        PHYSICAL_EXECUTION_EVENT_SCHEMA
    )

    assert event.schema == (
        "cpc.physical-execution-event.v1"
    )


def test_execution_event_binds_programming_record() -> None:
    event = _event()
    programming = _programming()

    assert event.programming_record_hash == (
        programming.record_hash
    )

    assert event.board_id == (
        programming.board_id
    )

    assert event.device_id == (
        programming.device_id
    )


def test_execution_event_binds_prepared_execution() -> None:
    assert (
        _event().prepared_execution_hash
        == prepared_execution_hash(
            _prepared()
        )
    )


def test_execution_event_binds_observable_execution() -> None:
    assert (
        _event().observable_execution_hash
        == observable_execution_hash(
            _observable()
        )
    )


def test_execution_event_commits_to_stimulus_and_measurement() -> None:
    event = _event()

    assert event.stimulus_record_sha256 == (
        _sha256(
            STIMULUS_LOG
        )
    )

    assert event.measurement_record_sha256 == (
        _sha256(
            MEASUREMENT_LOG
        )
    )


def test_execution_event_hash_is_deterministic() -> None:
    first = _event()
    second = _event()

    assert first.event_hash == (
        second.event_hash
    )

    assert first.event_hash.startswith(
        "sha256:"
    )


def test_execution_event_hash_changes_with_measurement() -> None:
    programming = _programming()

    first = execution_event_from_records(
        programming=programming,
        prepared=_prepared(),
        observable=_observable(),
        stimulus_interface="gpio",
        observation_interface="gpio",
        stimulus_record_sha256=_sha256(
            STIMULUS_LOG
        ),
        measurement_record_sha256=_sha256(
            b"measurement-a\n"
        ),
    )

    second = execution_event_from_records(
        programming=programming,
        prepared=_prepared(),
        observable=_observable(),
        stimulus_interface="gpio",
        observation_interface="gpio",
        stimulus_record_sha256=_sha256(
            STIMULUS_LOG
        ),
        measurement_record_sha256=_sha256(
            b"measurement-b\n"
        ),
    )

    assert first.event_hash != (
        second.event_hash
    )


def test_execution_event_rejects_backend_mismatch() -> None:
    observable = ObservableExecution(
        backend_id="digital",
        backend_version="1",
        observations=(
            ("result_bit", 1),
        ),
        metadata=(
            ("execution_engine", "test"),
            ("execution_engine_version", "1"),
            ("execution_id", "test"),
        ),
    )

    with pytest.raises(
        ValueError,
        match="backend IDs do not match",
    ):
        execution_event_from_records(
            programming=_programming(),
            prepared=_prepared(),
            observable=observable,
            stimulus_interface="gpio",
            observation_interface="gpio",
            stimulus_record_sha256=_sha256(
                STIMULUS_LOG
            ),
            measurement_record_sha256=_sha256(
                MEASUREMENT_LOG
            ),
        )


def test_json_contains_event_hash() -> None:
    event = _event()

    data = json.loads(
        event.to_json()
    )

    assert data["event_hash"] == (
        event.event_hash
    )


def test_execution_event_contains_no_semantic_claim() -> None:
    names = {
        field
        for field in _event().__dataclass_fields__
    }

    assert "decoded" not in names
    assert "reference" not in names
    assert "expected" not in names
    assert "semantic_match" not in names
    assert "overall_pass" not in names
