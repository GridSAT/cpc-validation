from __future__ import annotations

import csv
import json
from pathlib import Path

from src.cross_backend_benchmarks import (
    discover_benchmark_paths,
    validate_cross_backend_benchmark,
    validate_cross_backend_corpus,
    write_csv_report,
    write_json_summary,
)


def test_discovers_benchmark_directory_deterministically() -> None:
    paths = discover_benchmark_paths(
        [
            Path("benchmarks"),
        ]
    )

    assert paths == tuple(
        sorted(
            paths,
            key=lambda path: path.as_posix(),
        )
    )

    assert Path(
        "benchmarks/default_xor.json"
    ) in paths

    assert Path(
        "benchmarks/parity_chain_5.json"
    ) in paths

    assert Path(
        "benchmarks/parity_cycle_6.json"
    ) in paths


def test_default_xor_exhaustive_cross_backend_validation() -> None:
    results = validate_cross_backend_benchmark(
        Path(
            "benchmarks/default_xor.json"
        )
    )

    assert len(results) == 4

    assert all(
        result.backend_agreement
        for result in results
    )

    assert all(
        result.rc_semantic_match
        for result in results
    )

    assert all(
        result.digital_semantic_match
        for result in results
    )

    assert all(
        result.overall_pass
        for result in results
    )


def test_permanent_corpus_passes_cross_backend_validation() -> None:
    paths = discover_benchmark_paths(
        [
            Path("benchmarks"),
        ]
    )

    results = validate_cross_backend_corpus(
        paths
    )

    assert results

    assert all(
        result.overall_pass
        for result in results
    )


def test_csv_report_is_machine_readable(
    tmp_path: Path,
) -> None:
    results = validate_cross_backend_benchmark(
        Path(
            "benchmarks/default_xor.json"
        )
    )

    output = (
        tmp_path
        / "cross_backend_validation.csv"
    )

    write_csv_report(
        output,
        results,
    )

    with output.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        rows = list(
            csv.DictReader(
                handle
            )
        )

    assert len(rows) == 4

    assert rows[0]["rc_backend"] == "rc/1"
    assert rows[0]["digital_backend"] == "digital/1"

    assert all(
        row["backend_agreement"] == "1"
        for row in rows
    )

    assert all(
        row["overall_pass"] == "1"
        for row in rows
    )


def test_json_summary_records_separate_validation_conditions(
    tmp_path: Path,
) -> None:
    results = validate_cross_backend_benchmark(
        Path(
            "benchmarks/default_xor.json"
        )
    )

    output = (
        tmp_path
        / "cross_backend_summary.json"
    )

    write_json_summary(
        output,
        results,
    )

    summary = json.loads(
        output.read_text(
            encoding="utf-8"
        )
    )

    assert summary["schema"] == (
        "cpc.cross-backend-summary.v1"
    )

    assert summary["benchmark_count"] == 1
    assert summary["boundary_case_count"] == 4

    assert summary["backend_agreement_passed"] == 4
    assert summary["rc_semantic_passed"] == 4
    assert summary["digital_semantic_passed"] == 4

    assert summary["overall_passed"] == 4
    assert summary["overall_failed"] == 0
    assert summary["overall_pass"] is True
