from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.cross_backend_benchmarks import (
    CrossBackendBenchmarkResult,
    discover_benchmark_paths,
    validate_cross_backend_benchmark,
    write_csv_report,
    write_json_summary,
)


def _results() -> list[CrossBackendBenchmarkResult]:
    return validate_cross_backend_benchmark(
        Path("benchmarks/default_xor.json")
    )


# BV-1 — Deterministic Discovery

def test_bv1_discovery_is_deterministic() -> None:
    first = discover_benchmark_paths(
        [Path("benchmarks")]
    )

    second = discover_benchmark_paths(
        [Path("benchmarks")]
    )

    assert first == second

    assert first == tuple(
        sorted(
            first,
            key=lambda path: path.as_posix(),
        )
    )


# BV-2 — Canonical Input

def test_bv2_complete_permanent_corpus_is_lowerable() -> None:
    from src.benchmark_io import (
        load_parity_benchmark,
    )
    from src.ccir_lower_parity import (
        lower_parity_instance_to_ccir,
    )

    paths = discover_benchmark_paths(
        [Path("benchmarks")]
    )

    for path in paths:
        benchmark = load_parity_benchmark(
            path
        )

        program = lower_parity_instance_to_ccir(
            benchmark.instance
        )

        for constraint in program.constraints:
            payload = constraint.payload

            variables = getattr(
                payload,
                "variables",
                (),
            )

            assert tuple(
                sorted(
                    variables
                )
            ) == variables


# BV-3 — Deterministic Boundary Enumeration

def test_bv3_boundary_order_is_deterministic() -> None:
    first = _results()
    second = _results()

    assert [
        result.boundary
        for result in first
    ] == [
        result.boundary
        for result in second
    ]


# BV-4 — RFC-0005 Reuse

def test_bv4_corpus_module_uses_cross_backend_validator() -> None:
    text = Path(
        "src/cross_backend_benchmarks.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "validate_cross_backend"
        in text
    )


# BV-5 — Backend Isolation

def test_bv5_result_preserves_distinct_backend_identities() -> None:
    results = _results()

    assert results

    assert all(
        result.rc_backend == "rc/1"
        for result in results
    )

    assert all(
        result.digital_backend == "digital/1"
        for result in results
    )

    assert all(
        result.rc_execution_engine
        != result.digital_execution_engine
        for result in results
    )


# BV-6 — Reference Isolation

def test_bv6_corpus_runner_does_not_evaluate_reference_directly() -> None:
    text = Path(
        "src/cross_backend_benchmarks.py"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "evaluate_ccir_continuation"
        not in text
    )

    assert (
        "evaluate_ccir_program"
        not in text
    )


# BV-7 — Agreement Separation

def test_bv7_agreement_is_distinct_field() -> None:
    result = _results()[0]

    assert isinstance(
        result.backend_agreement,
        bool,
    )

    assert isinstance(
        result.rc_semantic_match,
        bool,
    )

    assert isinstance(
        result.digital_semantic_match,
        bool,
    )


# BV-8 — Per-Backend Semantic Validation

def test_bv8_each_backend_has_independent_semantic_match() -> None:
    results = _results()

    assert all(
        result.rc_semantic_match
        for result in results
    )

    assert all(
        result.digital_semantic_match
        for result in results
    )


# BV-9 — Machine-Readable Evidence

def test_bv9_csv_contains_required_validation_fields(
    tmp_path: Path,
) -> None:
    output = (
        tmp_path
        / "validation.csv"
    )

    write_csv_report(
        output,
        _results(),
    )

    header = output.read_text(
        encoding="utf-8"
    ).splitlines()[0]

    required = (
        "benchmark",
        "boundary",
        "rc_backend",
        "rc_decoded",
        "digital_backend",
        "digital_decoded",
        "reference_result",
        "backend_agreement",
        "rc_semantic_match",
        "digital_semantic_match",
        "overall_pass",
    )

    for field in required:
        assert field in header.split(",")


# BV-10 — Deterministic Aggregation

def test_bv10_json_summary_is_deterministic(
    tmp_path: Path,
) -> None:
    first = (
        tmp_path
        / "first.json"
    )

    second = (
        tmp_path
        / "second.json"
    )

    results = _results()

    write_json_summary(
        first,
        results,
    )

    write_json_summary(
        second,
        results,
    )

    assert (
        first.read_text(
            encoding="utf-8"
        )
        ==
        second.read_text(
            encoding="utf-8"
        )
    )


# BV-11 — Failure Propagation

def test_bv11_summary_propagates_case_failure(
    tmp_path: Path,
) -> None:
    passing = _results()[0]

    failing = CrossBackendBenchmarkResult(
        benchmark=passing.benchmark,
        benchmark_path=passing.benchmark_path,
        boundary=passing.boundary,
        rc_backend=passing.rc_backend,
        rc_execution_engine=passing.rc_execution_engine,
        rc_decoded=passing.rc_decoded,
        digital_backend=passing.digital_backend,
        digital_execution_engine=(
            passing.digital_execution_engine
        ),
        digital_decoded=passing.digital_decoded,
        reference_result=passing.reference_result,
        backend_agreement=False,
        rc_semantic_match=True,
        digital_semantic_match=True,
        overall_pass=False,
    )

    output = (
        tmp_path
        / "summary.json"
    )

    write_json_summary(
        output,
        [
            passing,
            failing,
        ],
    )

    summary = json.loads(
        output.read_text(
            encoding="utf-8"
        )
    )

    assert summary["overall_failed"] == 1
    assert summary["overall_pass"] is False


# BV-12 — Non-Vacuity

def test_bv12_empty_summary_is_not_pass(
    tmp_path: Path,
) -> None:
    output = (
        tmp_path
        / "summary.json"
    )

    write_json_summary(
        output,
        [],
    )

    summary = json.loads(
        output.read_text(
            encoding="utf-8"
        )
    )

    assert summary["boundary_case_count"] == 0
    assert summary["overall_pass"] is False


def test_bv12_empty_discovery_is_rejected(
    tmp_path: Path,
) -> None:
    empty = (
        tmp_path
        / "empty"
    )

    empty.mkdir()

    with pytest.raises(
        ValueError,
        match="no benchmark JSON files were discovered",
    ):
        discover_benchmark_paths(
            [empty]
        )


# BV-13 — Reproducibility Metadata

def test_bv13_result_records_backend_and_engine_identity() -> None:
    result = _results()[0]

    assert result.rc_backend
    assert result.rc_execution_engine

    assert result.digital_backend
    assert result.digital_execution_engine

    assert result.benchmark
    assert result.benchmark_path
    assert result.boundary


# BV-14 — Evidence-Boundary Discipline

def test_bv14_rfc_states_finite_evidence_boundary() -> None:
    text = Path(
        "docs/design/"
        "RFC-0006-Cross-Backend-Benchmark-Validation-and-Reproducibility.md"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "Finite benchmark success is evidence of implementation conformance"
        in text
    )

    assert (
        "It is not a proof of universal semantic correctness"
        in text
    )
