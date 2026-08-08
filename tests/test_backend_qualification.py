from __future__ import annotations

import json

import pytest

from src.backend_qualification import (
    BACKEND_QUALIFICATION_SCHEMA,
    BackendConformance,
    BackendCorpusQualification,
    BackendExecutionProfile,
    BackendQualificationManifest,
    manifest_from_summary,
)
from src.backends.digital_ccir import (
    DIGITAL_SPECIFICATION,
)


def _manifest() -> BackendQualificationManifest:
    return BackendQualificationManifest(
        specification=DIGITAL_SPECIFICATION,
        execution=BackendExecutionProfile(
            preparation_id="digital.program.v1",
            execution_id=(
                "digital.deterministic-enumeration.v1"
            ),
            execution_engine=(
                "python-digital-interpreter"
            ),
            execution_engine_version="1",
        ),
        conformance=BackendConformance(
            rfc0003=True,
            rfc0004=True,
            rfc0005_eligible=True,
            rfc0006_qualified=True,
            answer_independence=True,
            provenance_support=True,
        ),
        corpus=BackendCorpusQualification(
            report_schema=(
                "cpc.cross-backend-summary.v1"
            ),
            benchmark_count=16,
            boundary_case_count=64,
            overall_pass=True,
        ),
    )


def test_manifest_serializes_backend_identity() -> None:
    manifest = _manifest()

    data = manifest.to_manifest_dict()

    assert data["schema"] == (
        BACKEND_QUALIFICATION_SCHEMA
    )

    assert data["backend"] == {
        "id": "digital",
        "version": "1",
    }


def test_manifest_serializes_capabilities_deterministically() -> None:
    data = _manifest().to_manifest_dict()

    capabilities = data["capabilities"]

    assert capabilities["constraint_families"] == [
        "parity"
    ]

    assert capabilities["interface_features"] == [
        "boundary-control",
        "restricted-readout",
    ]

    assert capabilities["execution_features"] == [
        "deterministic-digital"
    ]


def test_manifest_preserves_backend_rules() -> None:
    data = _manifest().to_manifest_dict()

    assert data["backend_rules"] == [
        rule.rule_id
        for rule in DIGITAL_SPECIFICATION.rules
    ]


def test_manifest_records_execution_profile() -> None:
    data = _manifest().to_manifest_dict()

    assert data["execution"] == {
        "preparation_id": "digital.program.v1",
        "execution_id": (
            "digital.deterministic-enumeration.v1"
        ),
        "execution_engine": (
            "python-digital-interpreter"
        ),
        "execution_engine_version": "1",
    }


def test_manifest_records_conformance_separately() -> None:
    data = _manifest().to_manifest_dict()

    assert data["conformance"] == {
        "rfc0003": True,
        "rfc0004": True,
        "rfc0005_eligible": True,
        "rfc0006_qualified": True,
        "answer_independence": True,
        "provenance_support": True,
    }


def test_manifest_records_corpus_qualification() -> None:
    data = _manifest().to_manifest_dict()

    assert data["corpus"] == {
        "report_schema": (
            "cpc.cross-backend-summary.v1"
        ),
        "benchmark_count": 16,
        "boundary_case_count": 64,
        "overall_pass": True,
    }


def test_manifest_hash_is_deterministic() -> None:
    first = _manifest()
    second = _manifest()

    assert first.manifest_hash == second.manifest_hash
    assert first.manifest_hash.startswith(
        "sha256:"
    )


def test_manifest_hash_changes_with_qualification_content() -> None:
    first = _manifest()

    second = BackendQualificationManifest(
        specification=first.specification,
        execution=first.execution,
        conformance=BackendConformance(
            rfc0003=True,
            rfc0004=True,
            rfc0005_eligible=True,
            rfc0006_qualified=False,
            answer_independence=True,
            provenance_support=True,
        ),
        corpus=first.corpus,
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


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("preparation_id", ""),
        ("execution_id", ""),
        ("execution_engine", ""),
        ("execution_engine_version", ""),
    ),
)
def test_execution_profile_requires_non_empty_identifiers(
    field: str,
    value: str,
) -> None:
    values = {
        "preparation_id": "prep",
        "execution_id": "exec",
        "execution_engine": "engine",
        "execution_engine_version": "1",
    }

    values[field] = value

    with pytest.raises(
        ValueError,
        match=f"{field} must be a non-empty string",
    ):
        BackendExecutionProfile(
            **values
        )


def test_empty_corpus_is_allowed_but_not_implicitly_passing() -> None:
    corpus = BackendCorpusQualification(
        report_schema="schema",
        benchmark_count=0,
        boundary_case_count=0,
        overall_pass=False,
    )

    assert corpus.overall_pass is False


def test_manifest_from_rfc0006_summary() -> None:
    manifest = manifest_from_summary(
        specification=DIGITAL_SPECIFICATION,
        execution=BackendExecutionProfile(
            preparation_id="digital.program.v1",
            execution_id=(
                "digital.deterministic-enumeration.v1"
            ),
            execution_engine=(
                "python-digital-interpreter"
            ),
            execution_engine_version="1",
        ),
        conformance=BackendConformance(
            rfc0003=True,
            rfc0004=True,
            rfc0005_eligible=True,
            rfc0006_qualified=True,
            answer_independence=True,
            provenance_support=True,
        ),
        summary={
            "schema": "cpc.cross-backend-summary.v1",
            "benchmark_count": 16,
            "boundary_case_count": 64,
            "overall_pass": True,
        },
    )

    assert manifest.corpus is not None
    assert manifest.corpus.benchmark_count == 16
    assert manifest.corpus.boundary_case_count == 64
    assert manifest.corpus.overall_pass is True
