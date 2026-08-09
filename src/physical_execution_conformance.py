from __future__ import annotations

from dataclasses import dataclass

from src.observable_execution import ObservableExecution
from src.physical_execution_evidence import (
    EvidenceRecord,
    PhysicalExecutionEvidence,
    observable_execution_hash,
    prepared_execution_hash,
)
from src.prepared_execution import PreparedExecution


@dataclass(frozen=True)
class PhysicalEvidenceProfile:
    """
    RFC-0009 declared requirements for physical execution evidence.

    Profiles constrain evidentiary completeness. They do not define
    semantic correctness.
    """

    profile_id: str
    required_substrate_fields: tuple[str, ...] = ()
    required_instrumentation_fields: tuple[str, ...] = ()
    required_calibration_fields: tuple[str, ...] = ()
    required_evidence_types: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.profile_id, str) or not self.profile_id:
            raise ValueError(
                "profile_id must be a non-empty string"
            )

        for name, values in (
            (
                "required_substrate_fields",
                self.required_substrate_fields,
            ),
            (
                "required_instrumentation_fields",
                self.required_instrumentation_fields,
            ),
            (
                "required_calibration_fields",
                self.required_calibration_fields,
            ),
            (
                "required_evidence_types",
                self.required_evidence_types,
            ),
        ):
            if any(
                not isinstance(value, str) or not value
                for value in values
            ):
                raise ValueError(
                    f"{name} must contain non-empty strings"
                )

            if len(set(values)) != len(values):
                raise ValueError(
                    f"{name} must contain unique values"
                )

            if values != tuple(sorted(values)):
                raise ValueError(
                    f"{name} must be sorted"
                )


@dataclass(frozen=True)
class PhysicalExecutionConformanceResult:
    """
    Machine-checkable RFC-0009 evidence-conformance result.

    This result contains no decoded result, expected answer, or semantic
    correctness field.
    """

    profile_id: str

    backend_identity_match: bool
    lifecycle_binding_match: bool
    execution_identity_match: bool

    substrate_complete: bool
    instrumentation_complete: bool
    calibration_complete: bool
    evidence_types_complete: bool

    record_integrity_valid: bool

    @property
    def overall_pass(self) -> bool:
        return all(
            (
                self.backend_identity_match,
                self.lifecycle_binding_match,
                self.execution_identity_match,
                self.substrate_complete,
                self.instrumentation_complete,
                self.calibration_complete,
                self.evidence_types_complete,
                self.record_integrity_valid,
            )
        )


def _contains_required_fields(
    values: tuple[tuple[str, object], ...],
    required: tuple[str, ...],
) -> bool:
    present = {
        key
        for key, _ in values
    }

    return set(required).issubset(present)


def _evidence_types_complete(
    records: tuple[EvidenceRecord, ...],
    required: tuple[str, ...],
) -> bool:
    present = {
        record.evidence_type
        for record in records
    }

    return set(required).issubset(present)


def _record_integrity_valid(
    records: tuple[EvidenceRecord, ...],
) -> bool:
    """
    Structural digest validation.

    Content re-verification against external files is a separate operation,
    because PhysicalExecutionEvidence stores content digests rather than
    embedding external evidence payloads.
    """

    for record in records:
        digest = record.sha256

        if not digest.startswith("sha256:"):
            return False

        value = digest[len("sha256:"):]

        if len(value) != 64:
            return False

        if any(
            character not in "0123456789abcdef"
            for character in value
        ):
            return False

    return True


def evaluate_physical_execution_conformance(
    *,
    evidence: PhysicalExecutionEvidence,
    prepared: PreparedExecution,
    observable: ObservableExecution,
    profile: PhysicalEvidenceProfile,
) -> PhysicalExecutionConformanceResult:
    """
    Evaluate RFC-0009 physical-evidence conformance.

    No semantic reference evaluator is called here.
    """

    backend_identity_match = (
        evidence.backend_id
        == prepared.backend_id
        == observable.backend_id
        and evidence.backend_version
        == prepared.backend_version
        == observable.backend_version
    )

    lifecycle_binding_match = (
        evidence.prepared_execution_hash
        == prepared_execution_hash(prepared)
        and evidence.observable_execution_hash
        == observable_execution_hash(observable)
    )

    prepared_metadata = dict(
        prepared.metadata
    )
    observable_metadata = dict(
        observable.metadata
    )

    execution_identity_match = (
        evidence.preparation_id
        == prepared_metadata.get("preparation_id")
        and evidence.execution_id
        == observable_metadata.get("execution_id")
        and evidence.execution_engine
        == observable_metadata.get("execution_engine")
        and evidence.execution_engine_version
        == observable_metadata.get(
            "execution_engine_version"
        )
    )

    return PhysicalExecutionConformanceResult(
        profile_id=profile.profile_id,
        backend_identity_match=(
            backend_identity_match
        ),
        lifecycle_binding_match=(
            lifecycle_binding_match
        ),
        execution_identity_match=(
            execution_identity_match
        ),
        substrate_complete=_contains_required_fields(
            evidence.substrate,
            profile.required_substrate_fields,
        ),
        instrumentation_complete=_contains_required_fields(
            evidence.instrumentation,
            profile.required_instrumentation_fields,
        ),
        calibration_complete=_contains_required_fields(
            evidence.calibration,
            profile.required_calibration_fields,
        ),
        evidence_types_complete=_evidence_types_complete(
            evidence.records,
            profile.required_evidence_types,
        ),
        record_integrity_valid=_record_integrity_valid(
            evidence.records
        ),
    )
