from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Mapping

from src.backend import BackendSpecification


BACKEND_QUALIFICATION_SCHEMA = (
    "cpc.backend-qualification.v1"
)


@dataclass(frozen=True)
class BackendConformance:
    """
    Declared qualification status against CPC architectural RFCs.

    These fields record machine-readable qualification claims. They do not
    themselves prove conformance; the corresponding conformance suites and
    validation records remain the executable evidence.
    """

    rfc0003: bool
    rfc0004: bool
    rfc0005_eligible: bool
    rfc0006_qualified: bool

    answer_independence: bool
    provenance_support: bool


@dataclass(frozen=True)
class BackendExecutionProfile:
    """
    Stable backend execution identifiers required for reproduction.
    """

    preparation_id: str
    execution_id: str
    execution_engine: str
    execution_engine_version: str

    def __post_init__(self) -> None:
        for name, value in (
            (
                "preparation_id",
                self.preparation_id,
            ),
            (
                "execution_id",
                self.execution_id,
            ),
            (
                "execution_engine",
                self.execution_engine,
            ),
            (
                "execution_engine_version",
                self.execution_engine_version,
            ),
        ):
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"{name} must be a non-empty string"
                )


@dataclass(frozen=True)
class BackendCorpusQualification:
    """
    Optional RFC-0006 corpus qualification summary.
    """

    report_schema: str
    benchmark_count: int
    boundary_case_count: int
    overall_pass: bool

    def __post_init__(self) -> None:
        if not self.report_schema:
            raise ValueError(
                "report_schema must be non-empty"
            )

        if self.benchmark_count < 0:
            raise ValueError(
                "benchmark_count must be non-negative"
            )

        if self.boundary_case_count < 0:
            raise ValueError(
                "boundary_case_count must be non-negative"
            )


@dataclass(frozen=True)
class BackendQualificationManifest:
    """
    RFC-0007 machine-readable backend qualification manifest.

    Manifest identity is deterministic and derived only from canonical
    qualification content.
    """

    specification: BackendSpecification
    execution: BackendExecutionProfile
    conformance: BackendConformance
    corpus: BackendCorpusQualification | None = None

    @property
    def schema(self) -> str:
        return BACKEND_QUALIFICATION_SCHEMA

    def to_dict(self) -> dict[str, object]:
        capabilities = self.specification.capabilities

        data: dict[str, object] = {
            "schema": self.schema,
            "backend": {
                "id": self.specification.backend_id,
                "version": self.specification.backend_version,
            },
            "capabilities": {
                "constraint_families": sorted(
                    capabilities.constraint_families
                ),
                "interface_features": sorted(
                    capabilities.interface_features
                ),
                "execution_features": sorted(
                    capabilities.execution_features
                ),
                "artifact_features": sorted(
                    capabilities.artifact_features
                ),
            },
            "fixed_parameters": {
                key: value
                for key, value in (
                    self.specification.fixed_parameters
                )
            },
            "backend_rules": [
                rule.rule_id
                for rule in self.specification.rules
            ],
            "execution": {
                "preparation_id": (
                    self.execution.preparation_id
                ),
                "execution_id": (
                    self.execution.execution_id
                ),
                "execution_engine": (
                    self.execution.execution_engine
                ),
                "execution_engine_version": (
                    self.execution.execution_engine_version
                ),
            },
            "conformance": {
                "rfc0003": self.conformance.rfc0003,
                "rfc0004": self.conformance.rfc0004,
                "rfc0005_eligible": (
                    self.conformance.rfc0005_eligible
                ),
                "rfc0006_qualified": (
                    self.conformance.rfc0006_qualified
                ),
                "answer_independence": (
                    self.conformance.answer_independence
                ),
                "provenance_support": (
                    self.conformance.provenance_support
                ),
            },
        }

        if self.corpus is not None:
            data["corpus"] = {
                "report_schema": (
                    self.corpus.report_schema
                ),
                "benchmark_count": (
                    self.corpus.benchmark_count
                ),
                "boundary_case_count": (
                    self.corpus.boundary_case_count
                ),
                "overall_pass": (
                    self.corpus.overall_pass
                ),
            }

        return data

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
    def manifest_hash(self) -> str:
        digest = hashlib.sha256(
            self.canonical_json().encode(
                "utf-8"
            )
        ).hexdigest()

        return f"sha256:{digest}"

    def to_manifest_dict(self) -> dict[str, object]:
        data = self.to_dict()
        data["manifest_hash"] = self.manifest_hash
        return data

    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        return (
            json.dumps(
                self.to_manifest_dict(),
                indent=indent,
                sort_keys=True,
            )
            + "\n"
        )


def manifest_from_summary(
    *,
    specification: BackendSpecification,
    execution: BackendExecutionProfile,
    conformance: BackendConformance,
    summary: Mapping[str, object] | None = None,
) -> BackendQualificationManifest:
    """
    Construct a qualification manifest from an optional RFC-0006 summary.

    Only the aggregate qualification fields admitted by RFC-0007 are imported
    from the summary.
    """

    corpus = None

    if summary is not None:
        corpus = BackendCorpusQualification(
            report_schema=str(
                summary["schema"]
            ),
            benchmark_count=int(
                summary["benchmark_count"]
            ),
            boundary_case_count=int(
                summary["boundary_case_count"]
            ),
            overall_pass=bool(
                summary["overall_pass"]
            ),
        )

    return BackendQualificationManifest(
        specification=specification,
        execution=execution,
        conformance=conformance,
        corpus=corpus,
    )
