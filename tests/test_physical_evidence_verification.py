from __future__ import annotations

from src.observable_execution import ObservableExecution
from src.physical_evidence_verification import (
    verify_evidence_record_bytes,
    verify_evidence_record_file,
    verify_evidence_set_bytes,
    verify_evidence_set_files,
)
from src.physical_execution_evidence import (
    EvidenceRecord,
    evidence_from_execution,
)
from src.prepared_execution import PreparedExecution


PREPARATION_BYTES = b"device configured\n"
MEASUREMENT_BYTES = b"result=1\n"


def _prepared() -> PreparedExecution:
    return PreparedExecution(
        backend_id="physical-test",
        backend_version="1",
        payload=("configured", 1),
        interface=(
            ("readout", "result"),
        ),
        decoder_specification=(
            ("kind", "boolean"),
        ),
        metadata=(
            ("preparation_id", "physical.prepare.v1"),
        ),
    )


def _observable() -> ObservableExecution:
    return ObservableExecution(
        backend_id="physical-test",
        backend_version="1",
        observations=(
            ("result", 1),
        ),
        metadata=(
            ("execution_engine", "physical-device"),
            ("execution_engine_version", "1"),
            ("execution_id", "physical.execute.v1"),
        ),
    )


def _records() -> tuple[EvidenceRecord, ...]:
    return (
        EvidenceRecord.from_bytes(
            record_id="measurement",
            evidence_type="measurement-log",
            media_type="text/plain",
            content=MEASUREMENT_BYTES,
            description="Raw measurement",
        ),
        EvidenceRecord.from_bytes(
            record_id="preparation",
            evidence_type="preparation-log",
            media_type="text/plain",
            content=PREPARATION_BYTES,
            description="Preparation record",
        ),
    )


def _evidence():
    return evidence_from_execution(
        prepared=_prepared(),
        observable=_observable(),
        records=_records(),
    )


def test_record_bytes_verify_exact_content() -> None:
    record = _records()[0]

    result = verify_evidence_record_bytes(
        record=record,
        content=MEASUREMENT_BYTES,
    )

    assert result.record_id == "measurement"
    assert result.digest_match
    assert (
        result.actual_sha256
        == result.expected_sha256
        == record.sha256
    )


def test_record_bytes_reject_changed_content() -> None:
    result = verify_evidence_record_bytes(
        record=_records()[0],
        content=b"result=0\n",
    )

    assert not result.digest_match
    assert (
        result.actual_sha256
        != result.expected_sha256
    )


def test_record_file_verifies_exact_bytes(
    tmp_path,
) -> None:
    path = tmp_path / "measurement.log"

    path.write_bytes(
        MEASUREMENT_BYTES
    )

    result = verify_evidence_record_file(
        record=_records()[0],
        path=path,
    )

    assert result.digest_match


def test_complete_evidence_set_passes() -> None:
    result = verify_evidence_set_bytes(
        evidence=_evidence(),
        contents={
            "measurement": MEASUREMENT_BYTES,
            "preparation": PREPARATION_BYTES,
        },
    )

    assert len(result.record_results) == 2
    assert result.missing_record_ids == ()
    assert result.unexpected_record_ids == ()
    assert result.overall_pass


def test_changed_record_fails_complete_set() -> None:
    result = verify_evidence_set_bytes(
        evidence=_evidence(),
        contents={
            "measurement": b"result=0\n",
            "preparation": PREPARATION_BYTES,
        },
    )

    assert not result.overall_pass

    matches = {
        item.record_id: item.digest_match
        for item in result.record_results
    }

    assert matches == {
        "measurement": False,
        "preparation": True,
    }


def test_missing_record_fails_complete_set() -> None:
    result = verify_evidence_set_bytes(
        evidence=_evidence(),
        contents={
            "measurement": MEASUREMENT_BYTES,
        },
    )

    assert result.missing_record_ids == (
        "preparation",
    )

    assert not result.overall_pass


def test_unexpected_record_fails_complete_set() -> None:
    result = verify_evidence_set_bytes(
        evidence=_evidence(),
        contents={
            "measurement": MEASUREMENT_BYTES,
            "preparation": PREPARATION_BYTES,
            "uncommitted": b"extra\n",
        },
    )

    assert result.unexpected_record_ids == (
        "uncommitted",
    )

    assert not result.overall_pass


def test_complete_file_set_passes(
    tmp_path,
) -> None:
    measurement = (
        tmp_path / "measurement.log"
    )

    preparation = (
        tmp_path / "preparation.log"
    )

    measurement.write_bytes(
        MEASUREMENT_BYTES
    )

    preparation.write_bytes(
        PREPARATION_BYTES
    )

    result = verify_evidence_set_files(
        evidence=_evidence(),
        paths={
            "measurement": measurement,
            "preparation": preparation,
        },
    )

    assert result.overall_pass


def test_verification_results_contain_no_semantic_claim() -> None:
    result = verify_evidence_set_bytes(
        evidence=_evidence(),
        contents={
            "measurement": MEASUREMENT_BYTES,
            "preparation": PREPARATION_BYTES,
        },
    )

    names = {
        field
        for field in result.__dataclass_fields__
    }

    assert "decoded" not in names
    assert "reference" not in names
    assert "expected_answer" not in names
    assert "semantic_match" not in names
