from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.backend_qualification import (
    BACKEND_QUALIFICATION_SCHEMA,
    BackendConformance,
    BackendExecutionProfile,
    BackendQualificationManifest,
    manifest_from_summary,
)
from src.backend_qualification_profiles import (
    build_digital_qualification_manifest,
    build_rc_qualification_manifest,
)
from src.backends.digital_ccir import DIGITAL_SPECIFICATION


SUMMARY = {
    "schema": "cpc.cross-backend-summary.v1",
    "benchmark_count": 16,
    "boundary_case_count": 64,
    "overall_pass": True,
}


def _digital_manifest() -> BackendQualificationManifest:
    return build_digital_qualification_manifest(
        summary=SUMMARY
    )


# BQ-1 — Schema Identity

def test_bq1_manifest_has_explicit_schema_identity() -> None:
    manifest = _digital_manifest()

    assert manifest.schema == (
        BACKEND_QUALIFICATION_SCHEMA
    )

    assert manifest.to_manifest_dict()["schema"] == (
        "cpc.backend-qualification.v1"
    )


# BQ-2 — Canonical Backend Identity

def test_bq2_backend_identity_originates_from_specification() -> None:
    manifest = _digital_manifest()

    backend = manifest.to_manifest_dict()["backend"]

    assert backend == {
        "id": DIGITAL_SPECIFICATION.backend_id,
        "version": DIGITAL_SPECIFICATION.backend_version,
    }


# BQ-3 — Capability Fidelity

def test_bq3_capabilities_match_specification() -> None:
    manifest = _digital_manifest()

    data = manifest.to_manifest_dict()
    capabilities = data["capabilities"]

    specification = DIGITAL_SPECIFICATION.capabilities

    assert capabilities["constraint_families"] == sorted(
        specification.constraint_families
    )

    assert capabilities["interface_features"] == sorted(
        specification.interface_features
    )

    assert capabilities["execution_features"] == sorted(
        specification.execution_features
    )

    assert capabilities["artifact_features"] == sorted(
        specification.artifact_features
    )


# BQ-4 — Fixed-Parameter Fidelity

def test_bq4_fixed_parameters_match_specification() -> None:
    manifest = _digital_manifest()

    assert (
        manifest.to_manifest_dict()["fixed_parameters"]
        ==
        dict(
            DIGITAL_SPECIFICATION.fixed_parameters
        )
    )


# BQ-5 — Backend-Rule Fidelity

def test_bq5_backend_rules_match_specification() -> None:
    manifest = _digital_manifest()

    assert manifest.to_manifest_dict()["backend_rules"] == [
        rule.rule_id
        for rule in DIGITAL_SPECIFICATION.rules
    ]


# BQ-6 — Execution Identity

def test_bq6_execution_identity_is_explicit() -> None:
    manifest = _digital_manifest()

    execution = manifest.to_manifest_dict()["execution"]

    for field in (
        "preparation_id",
        "execution_id",
        "execution_engine",
        "execution_engine_version",
    ):
        assert isinstance(
            execution[field],
            str,
        )

        assert execution[field]


# BQ-7 — Claim Separation

def test_bq7_conformance_claims_are_independent_fields() -> None:
    conformance = (
        _digital_manifest()
        .to_manifest_dict()["conformance"]
    )

    assert set(conformance) == {
        "rfc0003",
        "rfc0004",
        "rfc0005_eligible",
        "rfc0006_qualified",
        "answer_independence",
        "provenance_support",
    }


# BQ-8 — Evidence Separation

def test_bq8_rfc_states_manifest_is_not_evidence() -> None:
    text = Path(
        "docs/design/"
        "RFC-0007-Backend-Qualification-and-Conformance-Manifests.md"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "The manifest itself is not proof that the claims are true."
        in text
    )

    assert (
        "manifest existence != backend qualification"
        in text
    )


# BQ-9 — Corpus Evidence Admission

def test_bq9_passing_rfc0006_summary_is_admitted() -> None:
    manifest = _digital_manifest()

    assert manifest.corpus is not None
    assert manifest.corpus.report_schema == (
        "cpc.cross-backend-summary.v1"
    )
    assert manifest.corpus.benchmark_count == 16
    assert manifest.corpus.boundary_case_count == 64
    assert manifest.corpus.overall_pass is True


# BQ-10 — Deterministic Serialization

def test_bq10_canonical_serialization_is_deterministic() -> None:
    first = _digital_manifest()
    second = _digital_manifest()

    assert (
        first.canonical_json()
        ==
        second.canonical_json()
    )


# BQ-11 — Deterministic Manifest Identity

def test_bq11_manifest_hash_is_deterministic() -> None:
    first = _digital_manifest()
    second = _digital_manifest()

    assert first.manifest_hash == second.manifest_hash


# BQ-12 — Content Sensitivity

def test_bq12_manifest_hash_changes_with_covered_content() -> None:
    first = _digital_manifest()

    changed = BackendQualificationManifest(
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
        != changed.manifest_hash
    )


# BQ-13 — Qualification Isolation

def test_bq13_qualification_modules_do_not_import_semantic_reference() -> None:
    files = (
        Path("src/backend_qualification.py"),
        Path("src/backend_qualification_profiles.py"),
    )

    forbidden = (
        "evaluate_ccir_continuation",
        "evaluate_ccir_program",
        "physical_validation",
        "ccir_reference",
        "generic_reference",
    )

    for path in files:
        text = path.read_text(
            encoding="utf-8"
        )

        for symbol in forbidden:
            assert symbol not in text, (
                f"{path} violates qualification isolation "
                f"through {symbol!r}"
            )


# BQ-14 — Failure Preservation

def test_bq14_failed_evidence_remains_non_passing() -> None:
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
            rfc0006_qualified=False,
            answer_independence=True,
            provenance_support=True,
        ),
        summary={
            "schema": "cpc.cross-backend-summary.v1",
            "benchmark_count": 16,
            "boundary_case_count": 64,
            "overall_pass": False,
        },
    )

    assert manifest.corpus is not None
    assert manifest.corpus.overall_pass is False
    assert (
        manifest.conformance.rfc0006_qualified
        is False
    )


# BQ-15 — Substrate Neutrality

def test_bq15_reference_backends_share_one_manifest_schema() -> None:
    rc = build_rc_qualification_manifest(
        execution_engine_version="ngspice-42",
        summary=SUMMARY,
    )

    digital = build_digital_qualification_manifest(
        summary=SUMMARY
    )

    assert rc.schema == digital.schema
    assert rc.schema == (
        "cpc.backend-qualification.v1"
    )

    assert (
        rc.specification.backend_id
        != digital.specification.backend_id
    )

    assert (
        rc.execution.execution_engine
        != digital.execution.execution_engine
    )
