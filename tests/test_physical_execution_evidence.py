from __future__ import annotations

import json
from dataclasses import dataclass

import pytest

from src.observable_execution import ObservableExecution
from src.physical_execution_evidence import (
    PHYSICAL_EXECUTION_EVIDENCE_SCHEMA,
    EvidenceRecord,
    PhysicalExecutionEvidence,
    evidence_from_execution,
    observable_execution_hash,
    prepared_execution_hash,
)
from src.prepared_execution import PreparedExecution


def _prepared() -> PreparedExecution:
    return PreparedExecution(
        backend_id="test-physical",
        backend_version="1",
        payload=(
            ("signal", 1),
            ("configuration", (0, 1, 1)),
        ),
        interface=(
            ("readout", "result"),
        ),
        decoder_specification=(
            ("kind", "boolean"),
        ),
        provenance=(
            ("element:0", ("ccir", "constraint:0")),
        ),
        metadata=(
            ("preparation_id", "test.physical-preparation.v1"),
        ),
    )


def _observable() -> ObservableExecution:
    return ObservableExecution(
        backend_id="test-physical",
        backend_version="1",
        observations=(
            ("result", 1),
        ),
        provenance=(
            ("element:0", ("ccir", "constraint:0")),
        ),
        metadata=(
            ("execution_engine", "test-device"),
            ("execution_engine_version", "1.0"),
            ("execution_id", "test.physical-execution.v1"),
        ),
    )


def _record() -> EvidenceRecord:
    return EvidenceRecord.from_bytes(
        record_id="measurement-0001",
        evidence_type="measurement-log",
        media_type="text/plain",
        content=b"measured result=1\n",
        description="Raw admitted measurement log",
    )


def _evidence() -> PhysicalExecutionEvidence:
    return evidence_from_execution(
        prepared=_prepared(),
        observable=_observable(),
        substrate=(
            ("device_id", "device-001"),
            ("device_type", "test-substrate"),
        ),
        instrumentation=(
            ("instrument_id", "instrument-001"),
        ),
        calibration=(
            ("calibration_id", "cal-001"),
        ),
        records=(
            _record(),
        ),
        metadata=(
            ("operator_mode", "automated"),
        ),
    )


def test_evidence_record_hashes_content() -> None:
    first = EvidenceRecord.from_bytes(
        record_id="r",
        evidence_type="log",
        media_type="text/plain",
        content=b"abc",
        description="record",
    )

    second = EvidenceRecord.from_bytes(
        record_id="r",
        evidence_type="log",
        media_type="text/plain",
        content=b"abc",
        description="record",
    )

    assert first == second
    assert first.sha256.startswith("sha256:")


def test_execution_hashes_are_deterministic() -> None:
    assert (
        prepared_execution_hash(_prepared())
        == prepared_execution_hash(_prepared())
    )

    assert (
        observable_execution_hash(_observable())
        == observable_execution_hash(_observable())
    )


def test_execution_hash_changes_with_prepared_content() -> None:
    first = _prepared()

    second = PreparedExecution(
        backend_id=first.backend_id,
        backend_version=first.backend_version,
        payload=(
            ("signal", 0),
        ),
        interface=first.interface,
        decoder_specification=(
            first.decoder_specification
        ),
        provenance=first.provenance,
        metadata=first.metadata,
    )

    assert (
        prepared_execution_hash(first)
        != prepared_execution_hash(second)
    )


def test_evidence_binds_lifecycle_identity() -> None:
    evidence = _evidence()

    assert evidence.backend_id == "test-physical"
    assert evidence.backend_version == "1"

    assert evidence.preparation_id == (
        "test.physical-preparation.v1"
    )

    assert evidence.execution_id == (
        "test.physical-execution.v1"
    )

    assert evidence.execution_engine == "test-device"
    assert evidence.execution_engine_version == "1.0"

    assert evidence.prepared_execution_hash == (
        prepared_execution_hash(_prepared())
    )

    assert evidence.observable_execution_hash == (
        observable_execution_hash(_observable())
    )


def test_evidence_has_explicit_schema() -> None:
    evidence = _evidence()

    assert evidence.schema == (
        PHYSICAL_EXECUTION_EVIDENCE_SCHEMA
    )

    assert evidence.to_evidence_dict()["schema"] == (
        "cpc.physical-execution-evidence.v1"
    )


def test_evidence_hash_is_deterministic() -> None:
    first = _evidence()
    second = _evidence()

    assert first.evidence_hash == second.evidence_hash
    assert first.evidence_hash.startswith("sha256:")


def test_evidence_hash_changes_with_physical_metadata() -> None:
    first = _evidence()

    second = evidence_from_execution(
        prepared=_prepared(),
        observable=_observable(),
        substrate=(
            ("device_id", "device-002"),
            ("device_type", "test-substrate"),
        ),
        instrumentation=first.instrumentation,
        calibration=first.calibration,
        records=first.records,
        metadata=first.metadata,
    )

    assert first.evidence_hash != second.evidence_hash


def test_json_contains_evidence_hash() -> None:
    evidence = _evidence()

    data = json.loads(
        evidence.to_json()
    )

    assert data["evidence_hash"] == (
        evidence.evidence_hash
    )


def test_evidence_rejects_mismatched_backend_identity() -> None:
    observable = ObservableExecution(
        backend_id="other",
        backend_version="1",
        observations=(
            ("result", 1),
        ),
        metadata=_observable().metadata,
    )

    with pytest.raises(
        ValueError,
        match="backend IDs do not match",
    ):
        evidence_from_execution(
            prepared=_prepared(),
            observable=observable,
        )


def test_evidence_requires_execution_identity_metadata() -> None:
    observable = ObservableExecution(
        backend_id="test-physical",
        backend_version="1",
        observations=(
            ("result", 1),
        ),
        metadata=(),
    )

    with pytest.raises(
        ValueError,
        match="requires lifecycle identity metadata",
    ):
        evidence_from_execution(
            prepared=_prepared(),
            observable=observable,
        )


def test_records_must_have_unique_sorted_ids() -> None:
    first = EvidenceRecord.from_bytes(
        record_id="b",
        evidence_type="log",
        media_type="text/plain",
        content=b"b",
        description="b",
    )

    second = EvidenceRecord.from_bytes(
        record_id="a",
        evidence_type="log",
        media_type="text/plain",
        content=b"a",
        description="a",
    )

    with pytest.raises(
        ValueError,
        match="sorted by record_id",
    ):
        PhysicalExecutionEvidence(
            backend_id="b",
            backend_version="1",
            preparation_id="p",
            execution_id="e",
            execution_engine="engine",
            execution_engine_version="1",
            prepared_execution_hash=(
                "sha256:" + "0" * 64
            ),
            observable_execution_hash=(
                "sha256:" + "1" * 64
            ),
            records=(
                first,
                second,
            ),
        )


@dataclass(frozen=True)
class SamplePayload:
    value: int
    label: str


def test_canonical_binding_supports_dataclass_payloads() -> None:
    prepared = PreparedExecution(
        backend_id="b",
        backend_version="1",
        payload=SamplePayload(
            value=7,
            label="sample",
        ),
        interface=(),
        decoder_specification=(),
        metadata=(
            ("preparation_id", "p"),
        ),
    )

    assert prepared_execution_hash(
        prepared
    ).startswith("sha256:")


def test_canonical_binding_rejects_opaque_objects() -> None:
    class Opaque:
        pass

    prepared = PreparedExecution(
        backend_id="b",
        backend_version="1",
        payload=Opaque(),
        interface=(),
        decoder_specification=(),
        metadata=(
            ("preparation_id", "p"),
        ),
    )

    with pytest.raises(
        TypeError,
        match="unsupported value in canonical execution evidence",
    ):
        prepared_execution_hash(prepared)
