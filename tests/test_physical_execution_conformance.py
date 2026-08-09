from __future__ import annotations

import pytest

from src.observable_execution import ObservableExecution
from src.physical_execution_conformance import (
    PhysicalEvidenceProfile,
    evaluate_physical_execution_conformance,
)
from src.physical_execution_evidence import (
    EvidenceRecord,
    evidence_from_execution,
)
from src.prepared_execution import PreparedExecution


def _prepared() -> PreparedExecution:
    return PreparedExecution(
        backend_id="physical-test",
        backend_version="1",
        payload=("configured-state", 1),
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
            ("execution_engine_version", "1.0"),
            ("execution_id", "physical.execute.v1"),
        ),
    )


def _records() -> tuple[EvidenceRecord, ...]:
    return (
        EvidenceRecord.from_bytes(
            record_id="measurement",
            evidence_type="measurement-log",
            media_type="text/plain",
            content=b"result=1\n",
            description="Measurement log",
        ),
        EvidenceRecord.from_bytes(
            record_id="preparation",
            evidence_type="preparation-log",
            media_type="text/plain",
            content=b"prepared\n",
            description="Preparation log",
        ),
    )


def _profile() -> PhysicalEvidenceProfile:
    return PhysicalEvidenceProfile(
        profile_id="physical-test.v1",
        required_substrate_fields=(
            "device_id",
            "device_type",
        ),
        required_instrumentation_fields=(
            "instrument_id",
        ),
        required_calibration_fields=(
            "calibration_id",
        ),
        required_evidence_types=(
            "measurement-log",
            "preparation-log",
        ),
    )


def _evidence():
    return evidence_from_execution(
        prepared=_prepared(),
        observable=_observable(),
        substrate=(
            ("device_id", "device-001"),
            ("device_type", "test-device"),
        ),
        instrumentation=(
            ("instrument_id", "instrument-001"),
        ),
        calibration=(
            ("calibration_id", "cal-001"),
        ),
        records=_records(),
    )


def test_complete_physical_evidence_passes() -> None:
    result = evaluate_physical_execution_conformance(
        evidence=_evidence(),
        prepared=_prepared(),
        observable=_observable(),
        profile=_profile(),
    )

    assert result.backend_identity_match
    assert result.lifecycle_binding_match
    assert result.execution_identity_match
    assert result.substrate_complete
    assert result.instrumentation_complete
    assert result.calibration_complete
    assert result.evidence_types_complete
    assert result.record_integrity_valid
    assert result.overall_pass


def test_changed_prepared_execution_breaks_binding() -> None:
    prepared = _prepared()

    evidence = evidence_from_execution(
        prepared=prepared,
        observable=_observable(),
        substrate=_evidence().substrate,
        instrumentation=_evidence().instrumentation,
        calibration=_evidence().calibration,
        records=_evidence().records,
    )

    changed = PreparedExecution(
        backend_id=prepared.backend_id,
        backend_version=prepared.backend_version,
        payload=("configured-state", 0),
        interface=prepared.interface,
        decoder_specification=(
            prepared.decoder_specification
        ),
        provenance=prepared.provenance,
        metadata=prepared.metadata,
    )

    result = evaluate_physical_execution_conformance(
        evidence=evidence,
        prepared=changed,
        observable=_observable(),
        profile=_profile(),
    )

    assert not result.lifecycle_binding_match
    assert not result.overall_pass


def test_changed_observation_breaks_binding() -> None:
    observable = _observable()

    evidence = evidence_from_execution(
        prepared=_prepared(),
        observable=observable,
        substrate=_evidence().substrate,
        instrumentation=_evidence().instrumentation,
        calibration=_evidence().calibration,
        records=_evidence().records,
    )

    changed = ObservableExecution(
        backend_id=observable.backend_id,
        backend_version=observable.backend_version,
        observations=(
            ("result", 0),
        ),
        provenance=observable.provenance,
        metadata=observable.metadata,
    )

    result = evaluate_physical_execution_conformance(
        evidence=evidence,
        prepared=_prepared(),
        observable=changed,
        profile=_profile(),
    )

    assert not result.lifecycle_binding_match
    assert not result.overall_pass


def test_missing_required_substrate_field_fails() -> None:
    evidence = evidence_from_execution(
        prepared=_prepared(),
        observable=_observable(),
        substrate=(
            ("device_id", "device-001"),
        ),
        instrumentation=_evidence().instrumentation,
        calibration=_evidence().calibration,
        records=_evidence().records,
    )

    result = evaluate_physical_execution_conformance(
        evidence=evidence,
        prepared=_prepared(),
        observable=_observable(),
        profile=_profile(),
    )

    assert not result.substrate_complete
    assert not result.overall_pass


def test_missing_required_evidence_type_fails() -> None:
    evidence = evidence_from_execution(
        prepared=_prepared(),
        observable=_observable(),
        substrate=_evidence().substrate,
        instrumentation=_evidence().instrumentation,
        calibration=_evidence().calibration,
        records=(
            _records()[0],
        ),
    )

    result = evaluate_physical_execution_conformance(
        evidence=evidence,
        prepared=_prepared(),
        observable=_observable(),
        profile=_profile(),
    )

    assert not result.evidence_types_complete
    assert not result.overall_pass


def test_profile_requirements_are_sorted() -> None:
    with pytest.raises(
        ValueError,
        match="required_evidence_types must be sorted",
    ):
        PhysicalEvidenceProfile(
            profile_id="bad",
            required_evidence_types=(
                "z",
                "a",
            ),
        )


def test_conformance_result_contains_no_semantic_result() -> None:
    result = evaluate_physical_execution_conformance(
        evidence=_evidence(),
        prepared=_prepared(),
        observable=_observable(),
        profile=_profile(),
    )

    names = {
        field
        for field in result.__dataclass_fields__
    }

    assert "decoded" not in names
    assert "reference" not in names
    assert "expected" not in names
    assert "semantic_match" not in names
