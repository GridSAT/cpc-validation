from __future__ import annotations

import base64
import hashlib
import json
import math
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Mapping

from src.observable_execution import ObservableExecution
from src.prepared_execution import PreparedExecution


PHYSICAL_EXECUTION_EVIDENCE_SCHEMA = (
    "cpc.physical-execution-evidence.v1"
)


def _canonical_value(value: object) -> object:
    """
    Convert admitted CPC execution values into a deterministic JSON form.

    Unsupported opaque Python objects are rejected rather than serialized
    through repr(), because repr() may contain process-local identity.
    """

    if value is None:
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(
                "non-finite floats are not admissible in canonical "
                "execution evidence"
            )
        return value

    if isinstance(value, str):
        return value

    if isinstance(value, bytes):
        return {
            "$bytes": base64.b64encode(value).decode("ascii"),
        }

    if is_dataclass(value) and not isinstance(
        value,
        type,
    ):
        return {
            "$dataclass": (
                f"{value.__class__.__module__}."
                f"{value.__class__.__qualname__}"
            ),
            "fields": {
                field.name: _canonical_value(
                    getattr(value, field.name)
                )
                for field in fields(value)
            },
        }

    if isinstance(value, tuple):
        return {
            "$tuple": [
                _canonical_value(item)
                for item in value
            ],
        }

    if isinstance(value, list):
        return {
            "$list": [
                _canonical_value(item)
                for item in value
            ],
        }

    if isinstance(value, Mapping):
        if any(
            not isinstance(key, str) or not key
            for key in value
        ):
            raise ValueError(
                "canonical execution mappings require "
                "non-empty string keys"
            )

        return {
            "$map": {
                key: _canonical_value(value[key])
                for key in sorted(value)
            },
        }

    if isinstance(value, (set, frozenset)):
        normalized = [
            _canonical_value(item)
            for item in value
        ]

        normalized.sort(
            key=lambda item: json.dumps(
                item,
                sort_keys=True,
                separators=(",", ":"),
            )
        )

        return {
            "$set": normalized,
        }

    raise TypeError(
        "unsupported value in canonical execution evidence: "
        f"{value.__class__.__module__}."
        f"{value.__class__.__qualname__}"
    )


def _canonical_json(value: object) -> str:
    return (
        json.dumps(
            _canonical_value(value),
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    )


def _sha256_text(text: str) -> str:
    digest = hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()

    return f"sha256:{digest}"


def prepared_execution_hash(
    prepared: PreparedExecution,
) -> str:
    """
    Deterministic identity of one PreparedExecution.
    """

    return _sha256_text(
        _canonical_json(prepared)
    )


def observable_execution_hash(
    observable: ObservableExecution,
) -> str:
    """
    Deterministic identity of one ObservableExecution.
    """

    return _sha256_text(
        _canonical_json(observable)
    )


def _validate_sha256(
    value: str,
    field_name: str,
) -> None:
    prefix = "sha256:"

    if (
        not isinstance(value, str)
        or not value.startswith(prefix)
    ):
        raise ValueError(
            f"{field_name} must be a sha256 digest"
        )

    digest = value[len(prefix):]

    if len(digest) != 64:
        raise ValueError(
            f"{field_name} must be a sha256 digest"
        )

    if any(
        character not in "0123456789abcdef"
        for character in digest
    ):
        raise ValueError(
            f"{field_name} must be a lowercase sha256 digest"
        )


def _validate_pairs(
    pairs: tuple[tuple[str, object], ...],
    field_name: str,
) -> None:
    keys = [
        key
        for key, _ in pairs
    ]

    if any(
        not isinstance(key, str) or not key
        for key in keys
    ):
        raise ValueError(
            f"{field_name} keys must be non-empty strings"
        )

    if len(set(keys)) != len(keys):
        raise ValueError(
            f"{field_name} keys must be unique"
        )

    if tuple(keys) != tuple(sorted(keys)):
        raise ValueError(
            f"{field_name} keys must be sorted"
        )

    # Validate that all values can participate in deterministic
    # evidence serialization.
    _canonical_value(pairs)


@dataclass(frozen=True, order=True)
class EvidenceRecord:
    """
    Immutable reference to one external physical-evidence record.

    The record stores a content digest, not the evidence payload itself.
    """

    record_id: str
    evidence_type: str
    media_type: str
    sha256: str
    description: str

    def __post_init__(self) -> None:
        for name, value in (
            ("record_id", self.record_id),
            ("evidence_type", self.evidence_type),
            ("media_type", self.media_type),
            ("description", self.description),
        ):
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"{name} must be a non-empty string"
                )

        _validate_sha256(
            self.sha256,
            "sha256",
        )

    @classmethod
    def from_bytes(
        cls,
        *,
        record_id: str,
        evidence_type: str,
        media_type: str,
        content: bytes,
        description: str,
    ) -> EvidenceRecord:
        digest = hashlib.sha256(
            content
        ).hexdigest()

        return cls(
            record_id=record_id,
            evidence_type=evidence_type,
            media_type=media_type,
            sha256=f"sha256:{digest}",
            description=description,
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "record_id": self.record_id,
            "evidence_type": self.evidence_type,
            "media_type": self.media_type,
            "sha256": self.sha256,
            "description": self.description,
        }


@dataclass(frozen=True)
class PhysicalExecutionEvidence:
    """
    RFC-0009 evidence envelope for one substrate execution.

    This object binds physical evidence to one PreparedExecution and one
    ObservableExecution. It contains no semantic reference result and does
    not establish semantic correctness by itself.
    """

    backend_id: str
    backend_version: str

    preparation_id: str
    execution_id: str
    execution_engine: str
    execution_engine_version: str

    prepared_execution_hash: str
    observable_execution_hash: str

    substrate: tuple[tuple[str, object], ...] = ()
    instrumentation: tuple[tuple[str, object], ...] = ()
    calibration: tuple[tuple[str, object], ...] = ()
    records: tuple[EvidenceRecord, ...] = ()
    metadata: tuple[tuple[str, object], ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("backend_id", self.backend_id),
            ("backend_version", self.backend_version),
            ("preparation_id", self.preparation_id),
            ("execution_id", self.execution_id),
            ("execution_engine", self.execution_engine),
            (
                "execution_engine_version",
                self.execution_engine_version,
            ),
        ):
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"{name} must be a non-empty string"
                )

        _validate_sha256(
            self.prepared_execution_hash,
            "prepared_execution_hash",
        )

        _validate_sha256(
            self.observable_execution_hash,
            "observable_execution_hash",
        )

        for name, value in (
            ("substrate", self.substrate),
            ("instrumentation", self.instrumentation),
            ("calibration", self.calibration),
            ("metadata", self.metadata),
        ):
            _validate_pairs(
                value,
                name,
            )

        if any(
            not isinstance(record, EvidenceRecord)
            for record in self.records
        ):
            raise ValueError(
                "records must contain EvidenceRecord values"
            )

        record_ids = tuple(
            record.record_id
            for record in self.records
        )

        if len(set(record_ids)) != len(record_ids):
            raise ValueError(
                "evidence record IDs must be unique"
            )

        if record_ids != tuple(sorted(record_ids)):
            raise ValueError(
                "evidence records must be sorted by record_id"
            )

    @property
    def schema(self) -> str:
        return PHYSICAL_EXECUTION_EVIDENCE_SCHEMA

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "backend": {
                "id": self.backend_id,
                "version": self.backend_version,
            },
            "execution": {
                "preparation_id": self.preparation_id,
                "execution_id": self.execution_id,
                "execution_engine": (
                    self.execution_engine
                ),
                "execution_engine_version": (
                    self.execution_engine_version
                ),
            },
            "binding": {
                "prepared_execution_hash": (
                    self.prepared_execution_hash
                ),
                "observable_execution_hash": (
                    self.observable_execution_hash
                ),
            },
            "substrate": {
                key: _canonical_value(value)
                for key, value in self.substrate
            },
            "instrumentation": {
                key: _canonical_value(value)
                for key, value in self.instrumentation
            },
            "calibration": {
                key: _canonical_value(value)
                for key, value in self.calibration
            },
            "records": [
                record.to_dict()
                for record in self.records
            ],
            "metadata": {
                key: _canonical_value(value)
                for key, value in self.metadata
            },
        }

    def canonical_json(self) -> str:
        return (
            json.dumps(
                self.to_dict(),
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        )

    @property
    def evidence_hash(self) -> str:
        return _sha256_text(
            self.canonical_json()
        )

    def to_evidence_dict(self) -> dict[str, object]:
        data = self.to_dict()
        data["evidence_hash"] = self.evidence_hash
        return data

    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        return (
            json.dumps(
                self.to_evidence_dict(),
                indent=indent,
                sort_keys=True,
            )
            + "\n"
        )


def evidence_from_execution(
    *,
    prepared: PreparedExecution,
    observable: ObservableExecution,
    substrate: tuple[tuple[str, object], ...] = (),
    instrumentation: tuple[tuple[str, object], ...] = (),
    calibration: tuple[tuple[str, object], ...] = (),
    records: tuple[EvidenceRecord, ...] = (),
    metadata: tuple[tuple[str, object], ...] = (),
) -> PhysicalExecutionEvidence:
    """
    Bind physical evidence to one existing RFC-0004 lifecycle execution.

    Execution identity is derived from the lifecycle records rather than
    supplied independently by the reporting layer.
    """

    if prepared.backend_id != observable.backend_id:
        raise ValueError(
            "prepared and observable backend IDs do not match"
        )

    if prepared.backend_version != observable.backend_version:
        raise ValueError(
            "prepared and observable backend versions do not match"
        )

    prepared_metadata = dict(
        prepared.metadata
    )
    observable_metadata = dict(
        observable.metadata
    )

    try:
        preparation_id = str(
            prepared_metadata["preparation_id"]
        )
        execution_id = str(
            observable_metadata["execution_id"]
        )
        execution_engine = str(
            observable_metadata["execution_engine"]
        )
        execution_engine_version = str(
            observable_metadata[
                "execution_engine_version"
            ]
        )
    except KeyError as exc:
        raise ValueError(
            "execution evidence requires lifecycle identity metadata: "
            f"{exc.args[0]}"
        ) from exc

    return PhysicalExecutionEvidence(
        backend_id=prepared.backend_id,
        backend_version=prepared.backend_version,
        preparation_id=preparation_id,
        execution_id=execution_id,
        execution_engine=execution_engine,
        execution_engine_version=execution_engine_version,
        prepared_execution_hash=(
            prepared_execution_hash(prepared)
        ),
        observable_execution_hash=(
            observable_execution_hash(observable)
        ),
        substrate=substrate,
        instrumentation=instrumentation,
        calibration=calibration,
        records=records,
        metadata=metadata,
    )
