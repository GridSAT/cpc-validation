from __future__ import annotations

import csv
import json
from pathlib import Path

from src.cross_backend_benchmarks import (
    discover_benchmark_paths,
)
from src.tri_backend_benchmarks import (
    TRI_BACKEND_SUMMARY_SCHEMA,
    validate_tri_backend_benchmark,
    validate_tri_backend_corpus,
    write_tri_backend_csv_report,
    write_tri_backend_json_summary,
)


def test_default_xor_exhaustive_tri_backend_validation() -> None:
    results = validate_tri_backend_benchmark(
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
        result.fpga_semantic_match
        for result in results
    )

    assert all(
        result.overall_pass
        for result in results
    )


def test_permanent_corpus_passes_tri_backend_validation() -> None:
    paths = discover_benchmark_paths(
        [
            Path("benchmarks"),
        ]
    )

    results = validate_tri_backend_corpus(
        paths
    )

    assert results

    assert all(
        result.overall_pass
        for result in results
    )


def test_tri_backend_csv_report_is_machine_readable(
    tmp_path: Path,
) -> None:
    results = validate_tri_backend_benchmark(
        Path(
            "benchmarks/default_xor.json"
        )
    )

    output = (
        tmp_path
        / "tri_backend_validation.csv"
    )

    write_tri_backend_csv_report(
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
    assert rows[0]["fpga_backend"] == "fpga/1"

    assert all(
        row["backend_agreement"] == "1"
        for row in rows
    )

    assert all(
        row["fpga_semantic_match"] == "1"
        for row in rows
    )

    assert all(
        row["overall_pass"] == "1"
        for row in rows
    )


def test_tri_backend_json_summary_records_all_conditions(
    tmp_path: Path,
) -> None:
    results = validate_tri_backend_benchmark(
        Path(
            "benchmarks/default_xor.json"
        )
    )

    output = (
        tmp_path
        / "tri_backend_summary.json"
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

    assert summary["schema"] == (
        TRI_BACKEND_SUMMARY_SCHEMA
    )

    assert summary["benchmark_count"] == 1
    assert summary["boundary_case_count"] == 4

    assert summary["backend_agreement_passed"] == 4
    assert summary["rc_semantic_passed"] == 4
    assert summary["digital_semantic_passed"] == 4
    assert summary["fpga_semantic_passed"] == 4

    assert summary["overall_passed"] == 4
    assert summary["overall_failed"] == 0
    assert summary["overall_pass"] is True


def test_empty_tri_backend_summary_is_not_vacuously_passing(
    tmp_path: Path,
) -> None:
    output = (
        tmp_path
        / "tri_backend_summary.json"
    )

    write_tri_backend_json_summary(
        output,
        [],
    )

    summary = json.loads(
        output.read_text(
            encoding="utf-8"
        )
    )

    assert summary["boundary_case_count"] == 0
    assert summary["overall_passed"] == 0
    assert summary["overall_pass"] is False
