from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from src.physical_execution_evidence import (
    EvidenceRecord,
    PhysicalExecutionEvidence,
)


@dataclass(frozen=True)
class EvidenceRecordVerification:
    """
    RFC-0009 verification result for one external evidence record.

    Verification establishes byte-level identity with the digest committed
    by EvidenceRecord. It makes no semantic claim about the evidence.
    """

    record_id: str
    expected_sha256: str
    actual_sha256: str
    digest_match: bool


@dataclass(frozen=True)
class EvidenceSetVerification:
    """
    Aggregate verification of external evidence supplied for one
    PhysicalExecutionEvidence envelope.
    """

    record_results: tuple[EvidenceRecordVerification, ...]
    missing_record_ids: tuple[str, ...]
    unexpected_record_ids: tuple[str, ...]

    @property
    def overall_pass(self) -> bool:
        return (
            not self.missing_record_ids
            and not self.unexpected_record_ids
            and all(
                result.digest_match
                for result in self.record_results
            )
        )


def _sha256_bytes(content: bytes) -> str:
    digest = hashlib.sha256(
        content
    ).hexdigest()

    return f"sha256:{digest}"


def verify_evidence_record_bytes(
    *,
    record: EvidenceRecord,
    content: bytes,
) -> EvidenceRecordVerification:
    """
    Verify supplied bytes against one committed EvidenceRecord.
    """

    actual = _sha256_bytes(
        content
    )

    return EvidenceRecordVerification(
        record_id=record.record_id,
        expected_sha256=record.sha256,
        actual_sha256=actual,
        digest_match=(
            actual == record.sha256
        ),
    )


def verify_evidence_record_file(
    *,
    record: EvidenceRecord,
    path: str | Path,
) -> EvidenceRecordVerification:
    """
    Verify one external evidence file against its committed digest.
    """

    evidence_path = Path(path)

    if not evidence_path.is_file():
        raise ValueError(
            "evidence path must identify an existing regular file"
        )

    return verify_evidence_record_bytes(
        record=record,
        content=evidence_path.read_bytes(),
    )


def verify_evidence_set_bytes(
    *,
    evidence: PhysicalExecutionEvidence,
    contents: dict[str, bytes],
) -> EvidenceSetVerification:
    """
    Verify a complete external evidence set by record_id.

    Exact-set semantics are intentional: omitted committed records and
    supplied uncommitted records both prevent aggregate conformance.
    """

    records = {
        record.record_id: record
        for record in evidence.records
    }

    expected_ids = set(
        records
    )
    supplied_ids = set(
        contents
    )

    missing = tuple(
        sorted(
            expected_ids - supplied_ids
        )
    )

    unexpected = tuple(
        sorted(
            supplied_ids - expected_ids
        )
    )

    results = tuple(
        verify_evidence_record_bytes(
            record=records[record_id],
            content=contents[record_id],
        )
        for record_id in sorted(
            expected_ids & supplied_ids
        )
    )

    return EvidenceSetVerification(
        record_results=results,
        missing_record_ids=missing,
        unexpected_record_ids=unexpected,
    )


def verify_evidence_set_files(
    *,
    evidence: PhysicalExecutionEvidence,
    paths: dict[str, str | Path],
) -> EvidenceSetVerification:
    """
    Verify a complete external evidence set supplied as files.
    """

    contents: dict[str, bytes] = {}

    for record_id, path in paths.items():
        evidence_path = Path(path)

        if not evidence_path.is_file():
            raise ValueError(
                "evidence path must identify an existing regular file: "
                f"{record_id}"
            )

        contents[record_id] = (
            evidence_path.read_bytes()
        )

    return verify_evidence_set_bytes(
        evidence=evidence,
        contents=contents,
    )
