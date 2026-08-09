from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from src.backend import ExecutionArtifact
from src.backend_qualification_profiles import (
    FPGA_EXECUTION_ENGINE,
    build_fpga_qualification_manifest,
)
from src.backends.digital_ccir import DigitalBackend
from src.backends.fpga_ccir import (
    FPGA_SPECIFICATION,
    FPGABackend,
)
from src.backends.fpga_decode import decode_fpga
from src.backends.fpga_execute import (
    FPGA_EXECUTION_ID,
    _iverilog_version,
    execute_fpga,
)
from src.backends.fpga_prepare import (
    FPGA_PREPARATION_ID,
    prepare_fpga_execution,
)
from src.backends.fpga_run import (
    FPGAExecutionResult,
    run_fpga_execution,
)
from src.backends.rc_ccir import RCBackend
from src.benchmark_io import load_parity_benchmark
from src.ccir_lower_parity import lower_parity_instance_to_ccir
from src.observable_execution import ObservableExecution
from src.prepared_execution import PreparedExecution
from src.cross_backend_benchmarks import (
    discover_benchmark_paths,
)
from src.tri_backend_benchmarks import (
    validate_tri_backend_corpus,
    write_tri_backend_json_summary,
)
from src.tri_backend_validation import (
    TriBackendValidationResult,
    validate_tri_backend,
)


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_BENCHMARK = (
    ROOT / "benchmarks" / "default_xor.json"
)


def _program():
    benchmark = load_parity_benchmark(
        DEFAULT_BENCHMARK
    )

    return lower_parity_instance_to_ccir(
        benchmark.instance
    )


def _boundary():
    return {
        0: 0,
        3: 1,
    }


def _fpga_artifact() -> ExecutionArtifact:
    return FPGABackend().compile(
        _program()
    )


def _fpga_result() -> FPGAExecutionResult:
    program = _program()

    return run_fpga_execution(
        program,
        FPGABackend().compile(program),
        _boundary(),
    )


# FPGA-1, FPGA-2, FPGA-5
def test_fpga_backend_is_distinct_hardware_oriented_ccir_backend() -> None:
    assert FPGA_SPECIFICATION.backend_id == "fpga"
    assert FPGA_SPECIFICATION.backend_version == "1"

    assert (
        FPGA_SPECIFICATION.backend_id
        != DigitalBackend().specification.backend_id
    )

    artifact = _fpga_artifact()

    assert isinstance(
        artifact,
        ExecutionArtifact,
    )

    metadata = dict(
        artifact.metadata
    )

    parameters = dict(
        artifact.parameters
    )

    assert metadata["backend_id"] == "fpga"
    assert metadata["backend_version"] == "1"

    assert (
        parameters["representation"]
        == "synthesizable-logic-network-v1"
    )


# FPGA-3
def test_fpga_compile_interface_is_answer_independent() -> None:
    signature = inspect.signature(
        FPGABackend.compile
    )

    assert tuple(
        signature.parameters
    ) == (
        "self",
        "program",
    )


# FPGA-4
def test_fpga_artifact_has_complete_provenance() -> None:
    artifact = _fpga_artifact()

    assert artifact.topology
    assert artifact.provenance

    provenance_targets = {
        element_id
        for element_id, _ in artifact.provenance
    }

    topology_targets = {
        element_id
        for element_id, _ in artifact.topology
    }

    assert provenance_targets == topology_targets


# FPGA-6, FPGA-7
def test_fpga_preparation_uses_common_contract_and_structural_completion() -> None:
    program = _program()
    artifact = FPGABackend().compile(
        program
    )

    prepared = prepare_fpga_execution(
        program,
        artifact,
        _boundary(),
    )

    assert isinstance(
        prepared,
        PreparedExecution,
    )

    metadata = dict(
        prepared.metadata
    )

    assert (
        metadata["preparation_id"]
        == FPGA_PREPARATION_ID
    )

    payload = prepared.payload

    assert "module cpc_fpga_execution" in payload
    assert "assign result" in payload

    # The reference v1 realization structurally materializes
    # existential completion branches in the generated HDL.
    assert "completion_" in payload


# FPGA-8, FPGA-9
def test_fpga_execution_uses_external_hdl_contract() -> None:
    signature = inspect.signature(
        execute_fpga
    )

    assert tuple(
        signature.parameters
    ) == (
        "prepared",
    )

    result = _fpga_result()

    assert isinstance(
        result.observable,
        ObservableExecution,
    )

    metadata = dict(
        result.observable.metadata
    )

    assert (
        metadata["execution_engine"]
        == "iverilog/vvp"
    )

    assert (
        metadata["execution_id"]
        == FPGA_EXECUTION_ID
    )


# FPGA-10, FPGA-11
def test_fpga_observation_and_decoder_are_restricted() -> None:
    result = _fpga_result()

    observations = dict(
        result.observable.observations
    )

    assert observations == {
        "result_bit": 1,
    }

    assert (
        decode_fpga(
            result.observable,
            result.prepared.decoder_specification,
        )
        == 1
    )


# FPGA-12
def test_fpga_composed_execution_retains_full_lifecycle() -> None:
    result = _fpga_result()

    assert isinstance(
        result,
        FPGAExecutionResult,
    )

    assert isinstance(
        result.prepared,
        PreparedExecution,
    )

    assert isinstance(
        result.observable,
        ObservableExecution,
    )

    assert result.decoded in (
        0,
        1,
    )


# TB-1, TB-3, TB-4, TB-5
def test_tri_backend_validation_records_three_backends_and_semantics() -> None:
    result = validate_tri_backend(
        _program(),
        _boundary(),
    )

    assert isinstance(
        result,
        TriBackendValidationResult,
    )

    assert result.rc.prepared.backend_id == "rc"
    assert result.digital.prepared.backend_id == "digital"
    assert result.fpga.prepared.backend_id == "fpga"

    assert result.backend_agreement is True
    assert result.rc_semantic_match is True
    assert result.digital_semantic_match is True
    assert result.fpga_semantic_match is True
    assert result.overall_pass is True


# TB-2
def test_tri_backend_reference_is_not_an_execution_backend() -> None:
    result = validate_tri_backend(
        _program(),
        _boundary(),
    )

    assert result.reference in (
        0,
        1,
    )

    backend_ids = {
        result.rc.prepared.backend_id,
        result.digital.prepared.backend_id,
        result.fpga.prepared.backend_id,
    }

    assert backend_ids == {
        "rc",
        "digital",
        "fpga",
    }

    assert "reference" not in backend_ids


# TB-6
def test_tri_backend_case_identity_matches_execution_records() -> None:
    results = validate_tri_backend_corpus(
        (
            DEFAULT_BENCHMARK,
        )
    )

    assert results

    case = results[0]

    assert case.rc_backend == "rc/1"
    assert case.digital_backend == "digital/1"
    assert case.fpga_backend == "fpga/1"

    assert case.rc_execution_engine == "ngspice"

    assert (
        case.digital_execution_engine
        == "python-digital-interpreter"
    )

    assert (
        case.fpga_execution_engine
        == "iverilog/vvp"
    )


# TB-7
def test_tri_backend_discovery_and_corpus_validation_are_deterministic() -> None:
    first_discovery = discover_benchmark_paths(
        (
            ROOT / "benchmarks",
        )
    )

    second_discovery = discover_benchmark_paths(
        (
            ROOT / "benchmarks",
        )
    )

    assert first_discovery == second_discovery

    first = validate_tri_backend_corpus(
        (
            DEFAULT_BENCHMARK,
        )
    )

    second = validate_tri_backend_corpus(
        (
            DEFAULT_BENCHMARK,
        )
    )

    assert first == second


# TB-8
def test_tri_backend_empty_aggregate_does_not_pass(
    tmp_path: Path,
) -> None:
    output = (
        tmp_path
        / "empty-tri-backend-summary.json"
    )

    write_tri_backend_json_summary(
        output,
        (),
    )

    summary = json.loads(
        output.read_text(
            encoding="utf-8"
        )
    )

    assert summary["boundary_case_count"] == 0
    assert summary["overall_pass"] is False


# TB-9
def test_tri_backend_report_schema_is_distinct_from_rfc0006(
    tmp_path: Path,
) -> None:
    results = validate_tri_backend_corpus(
        (
            DEFAULT_BENCHMARK,
        )
    )

    output = (
        tmp_path
        / "tri-backend-summary.json"
    )

    write_tri_backend_json_summary(
        output,
        results,
    )

    summary = json.loads(
        output.read_text(
            encoding="utf-8"
        )
    )

    assert (
        summary["schema"]
        == "cpc.tri-backend-summary.v1"
    )

    assert (
        summary["schema"]
        != "cpc.cross-backend-summary.v1"
    )


# QF-1, QF-2
def test_fpga_qualification_uses_generic_schema_and_actual_engine() -> None:
    version = _iverilog_version()

    manifest = build_fpga_qualification_manifest(
        execution_engine_version=version,
        summary={
            "schema": "cpc.tri-backend-summary.v1",
            "benchmark_count": 1,
            "boundary_case_count": 4,
            "overall_pass": True,
        },
    )

    data = manifest.to_dict()

    assert (
        data["schema"]
        == "cpc.backend-qualification.v1"
    )

    assert (
        manifest.execution.execution_engine
        == FPGA_EXECUTION_ENGINE
    )

    assert (
        manifest.execution.execution_engine_version
        == version
    )

    assert version


# QF-3, QF-4
def test_fpga_qualification_cli_enforces_semantic_and_aggregate_gates() -> None:
    import qualify_fpga_backend

    good = {
        "schema": "cpc.tri-backend-summary.v1",
        "benchmark_count": 1,
        "boundary_case_count": 4,
        "fpga_semantic_passed": 4,
        "fpga_semantic_failed": 0,
        "overall_passed": 4,
        "overall_failed": 0,
        "overall_pass": True,
    }

    qualify_fpga_backend.validate_fpga_summary(
        good
    )

    bad_fpga = dict(
        good
    )

    bad_fpga.update(
        {
            "fpga_semantic_passed": 3,
            "fpga_semantic_failed": 1,
        }
    )

    with pytest.raises(
        ValueError,
        match="every FPGA semantic case",
    ):
        qualify_fpga_backend.validate_fpga_summary(
            bad_fpga
        )

    bad_overall = dict(
        good
    )

    bad_overall.update(
        {
            "overall_passed": 3,
            "overall_failed": 1,
            "overall_pass": False,
        }
    )

    with pytest.raises(
        ValueError,
        match="fully passing tri-backend corpus",
    ):
        qualify_fpga_backend.validate_fpga_summary(
            bad_overall
        )


# QF-5
def test_fpga_qualification_manifest_is_deterministic() -> None:
    summary = {
        "schema": "cpc.tri-backend-summary.v1",
        "benchmark_count": 16,
        "boundary_case_count": 64,
        "overall_pass": True,
    }

    version = _iverilog_version()

    first = build_fpga_qualification_manifest(
        execution_engine_version=version,
        summary=summary,
    )

    second = build_fpga_qualification_manifest(
        execution_engine_version=version,
        summary=summary,
    )

    assert first.to_json() == second.to_json()

    assert (
        first.manifest_hash
        == second.manifest_hash
    )
