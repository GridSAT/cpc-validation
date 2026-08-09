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


def test_fpga_profile_uses_reference_backend_identity() -> None:
    from src.backend_qualification_profiles import (
        FPGA_EXECUTION_ENGINE,
        build_fpga_qualification_manifest,
    )

    summary = {
        "schema": "cpc.tri-backend-summary.v1",
        "benchmark_count": 16,
        "boundary_case_count": 64,
        "overall_pass": True,
    }

    manifest = build_fpga_qualification_manifest(
        execution_engine_version="12.0 (stable) ()",
        summary=summary,
    )

    assert manifest.specification.backend_id == "fpga"
    assert manifest.specification.backend_version == "1"

    assert (
        manifest.execution.execution_engine
        == FPGA_EXECUTION_ENGINE
    )

    assert (
        manifest.execution.execution_engine_version
        == "12.0 (stable) ()"
    )

    assert manifest.corpus is not None
    assert manifest.corpus.report_schema == (
        "cpc.tri-backend-summary.v1"
    )


def test_fpga_profile_records_fpga_lifecycle_identifiers() -> None:
    from src.backend_qualification_profiles import (
        build_fpga_qualification_manifest,
    )
    from src.backends.fpga_execute import (
        FPGA_EXECUTION_ID,
    )
    from src.backends.fpga_prepare import (
        FPGA_PREPARATION_ID,
    )

    manifest = build_fpga_qualification_manifest(
        execution_engine_version="12.0",
    )

    assert (
        manifest.execution.preparation_id
        == FPGA_PREPARATION_ID
    )

    assert (
        manifest.execution.execution_id
        == FPGA_EXECUTION_ID
    )


def test_fpga_manifest_identity_is_distinct_from_reference_backends() -> None:
    from src.backend_qualification_profiles import (
        build_fpga_qualification_manifest,
    )

    fpga = build_fpga_qualification_manifest(
        execution_engine_version="12.0",
        summary={
            "schema": "cpc.tri-backend-summary.v1",
            "benchmark_count": 16,
            "boundary_case_count": 64,
            "overall_pass": True,
        },
    )

    rc = build_rc_qualification_manifest(
        execution_engine_version="ngspice-42",
        summary=SUMMARY,
    )

    digital = build_digital_qualification_manifest(
        summary=SUMMARY
    )

    assert fpga.manifest_hash != rc.manifest_hash
    assert fpga.manifest_hash != digital.manifest_hash
