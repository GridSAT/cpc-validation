from __future__ import annotations

from src.backend_qualification_profiles import (
    DIGITAL_EXECUTION_ENGINE,
    DIGITAL_EXECUTION_ENGINE_VERSION,
    RC_EXECUTION_ENGINE,
    build_digital_qualification_manifest,
    build_rc_qualification_manifest,
)


SUMMARY = {
    "schema": "cpc.cross-backend-summary.v1",
    "benchmark_count": 16,
    "boundary_case_count": 64,
    "overall_pass": True,
}


def test_rc_profile_uses_reference_backend_identity() -> None:
    manifest = build_rc_qualification_manifest(
        execution_engine_version="ngspice-42",
        summary=SUMMARY,
    )

    assert manifest.specification.backend_id == "rc"
    assert manifest.specification.backend_version == "1"

    assert (
        manifest.execution.execution_engine
        == RC_EXECUTION_ENGINE
    )

    assert (
        manifest.execution.execution_engine_version
        == "ngspice-42"
    )


def test_digital_profile_uses_reference_backend_identity() -> None:
    manifest = build_digital_qualification_manifest(
        summary=SUMMARY
    )

    assert (
        manifest.specification.backend_id
        == "digital"
    )

    assert (
        manifest.specification.backend_version
        == "1"
    )

    assert (
        manifest.execution.execution_engine
        == DIGITAL_EXECUTION_ENGINE
    )

    assert (
        manifest.execution.execution_engine_version
        == DIGITAL_EXECUTION_ENGINE_VERSION
    )


def test_reference_profiles_record_same_corpus_evidence() -> None:
    rc = build_rc_qualification_manifest(
        execution_engine_version="ngspice-42",
        summary=SUMMARY,
    )

    digital = build_digital_qualification_manifest(
        summary=SUMMARY
    )

    assert rc.corpus is not None
    assert digital.corpus is not None

    assert rc.corpus == digital.corpus

    assert rc.corpus.benchmark_count == 16
    assert rc.corpus.boundary_case_count == 64
    assert rc.corpus.overall_pass is True


def test_reference_profiles_declare_required_conformance() -> None:
    rc = build_rc_qualification_manifest(
        execution_engine_version="ngspice-42",
        summary=SUMMARY,
    )

    digital = build_digital_qualification_manifest(
        summary=SUMMARY
    )

    for manifest in (
        rc,
        digital,
    ):
        assert manifest.conformance.rfc0003
        assert manifest.conformance.rfc0004
        assert manifest.conformance.rfc0005_eligible
        assert manifest.conformance.rfc0006_qualified
        assert manifest.conformance.answer_independence
        assert manifest.conformance.provenance_support


def test_reference_backend_manifests_have_distinct_identity() -> None:
    rc = build_rc_qualification_manifest(
        execution_engine_version="ngspice-42",
        summary=SUMMARY,
    )

    digital = build_digital_qualification_manifest(
        summary=SUMMARY
    )

    assert (
        rc.manifest_hash
        != digital.manifest_hash
    )
