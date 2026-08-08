from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from src.benchmark_io import load_parity_benchmark
from src.ccir_lower_parity import lower_parity_instance_to_ccir
from src.cross_backend_validation import validate_cross_backend
from src.generic_reference import enumerate_boundary_assignments


@dataclass(frozen=True)
class CrossBackendBenchmarkResult:
    """
    Machine-readable result for one benchmark boundary assignment.

    Backend agreement and independent semantic correctness remain
    intentionally separate validation conditions.
    """

    benchmark: str
    benchmark_path: str
    boundary: str

    rc_backend: str
    rc_execution_engine: str
    rc_decoded: int

    digital_backend: str
    digital_execution_engine: str
    digital_decoded: int

    reference_result: int

    backend_agreement: bool
    rc_semantic_match: bool
    digital_semantic_match: bool
    overall_pass: bool


def discover_benchmark_paths(
    inputs: Iterable[Path],
) -> tuple[Path, ...]:
    """
    Discover JSON benchmark files deterministically.

    Explicit files and recursively searched directories are supported.
    Duplicate paths are removed.
    """
    discovered: set[Path] = set()

    for input_path in inputs:
        if input_path.is_dir():
            discovered.update(
                path
                for path in input_path.rglob("*.json")
                if path.is_file()
            )
            continue

        if input_path.is_file():
            if input_path.suffix.lower() != ".json":
                raise ValueError(
                    "benchmark file must use the .json extension: "
                    f"{input_path}"
                )

            discovered.add(input_path)
            continue

        raise FileNotFoundError(
            f"benchmark input does not exist: {input_path}"
        )

    if not discovered:
        raise ValueError(
            "no benchmark JSON files were discovered"
        )

    return tuple(
        sorted(
            discovered,
            key=lambda path: path.as_posix(),
        )
    )


def validate_cross_backend_benchmark(
    benchmark_path: Path,
) -> list[CrossBackendBenchmarkResult]:
    """
    Exhaustively validate every boundary assignment for one benchmark
    through the RC and deterministic digital execution backends.
    """
    benchmark = load_parity_benchmark(
        benchmark_path
    )

    program = lower_parity_instance_to_ccir(
        benchmark.instance
    )

    results: list[
        CrossBackendBenchmarkResult
    ] = []

    for boundary_values in enumerate_boundary_assignments(
        benchmark.instance.boundary_variables
    ):
        validation = validate_cross_backend(
            program,
            boundary_values,
        )

        rc_metadata = dict(
            validation.rc.observable.metadata
        )

        digital_metadata = dict(
            validation.digital.observable.metadata
        )

        boundary = ",".join(
            f"x{variable}={value}"
            for variable, value in sorted(
                boundary_values.items()
            )
        )

        results.append(
            CrossBackendBenchmarkResult(
                benchmark=benchmark.name,
                benchmark_path=str(
                    benchmark_path
                ),
                boundary=boundary,
                rc_backend=(
                    f"{validation.rc.prepared.backend_id}/"
                    f"{validation.rc.prepared.backend_version}"
                ),
                rc_execution_engine=str(
                    rc_metadata.get(
                        "execution_engine"
                    )
                ),
                rc_decoded=validation.rc.decoded,
                digital_backend=(
                    f"{validation.digital.prepared.backend_id}/"
                    f"{validation.digital.prepared.backend_version}"
                ),
                digital_execution_engine=str(
                    digital_metadata.get(
                        "execution_engine"
                    )
                ),
                digital_decoded=validation.digital.decoded,
                reference_result=validation.reference_result,
                backend_agreement=validation.backend_agreement,
                rc_semantic_match=validation.rc_semantic_match,
                digital_semantic_match=(
                    validation.digital_semantic_match
                ),
                overall_pass=validation.passed,
            )
        )

    return results


def validate_cross_backend_corpus(
    benchmark_paths: Iterable[Path],
) -> list[CrossBackendBenchmarkResult]:
    """
    Validate every boundary assignment of every supplied benchmark.
    """
    results: list[
        CrossBackendBenchmarkResult
    ] = []

    for benchmark_path in benchmark_paths:
        results.extend(
            validate_cross_backend_benchmark(
                benchmark_path
            )
        )

    return results


def write_csv_report(
    path: Path,
    results: Iterable[CrossBackendBenchmarkResult],
) -> None:
    rows = list(results)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        field.name
        for field in CrossBackendBenchmarkResult.__dataclass_fields__.values()
    ]

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for result in rows:
            row = asdict(result)

            for key in (
                "backend_agreement",
                "rc_semantic_match",
                "digital_semantic_match",
                "overall_pass",
            ):
                row[key] = int(
                    row[key]
                )

            writer.writerow(
                row
            )


def write_json_summary(
    path: Path,
    results: Iterable[CrossBackendBenchmarkResult],
) -> None:
    rows = list(results)

    benchmark_names = sorted(
        {
            result.benchmark
            for result in rows
        }
    )

    total = len(rows)

    backend_agreement_passed = sum(
        result.backend_agreement
        for result in rows
    )

    rc_semantic_passed = sum(
        result.rc_semantic_match
        for result in rows
    )

    digital_semantic_passed = sum(
        result.digital_semantic_match
        for result in rows
    )

    overall_passed = sum(
        result.overall_pass
        for result in rows
    )

    summary = {
        "schema": "cpc.cross-backend-summary.v1",
        "benchmark_count": len(
            benchmark_names
        ),
        "benchmarks": benchmark_names,
        "boundary_case_count": total,
        "backend_agreement_passed": backend_agreement_passed,
        "backend_agreement_failed": (
            total - backend_agreement_passed
        ),
        "rc_semantic_passed": rc_semantic_passed,
        "rc_semantic_failed": (
            total - rc_semantic_passed
        ),
        "digital_semantic_passed": digital_semantic_passed,
        "digital_semantic_failed": (
            total - digital_semantic_passed
        ),
        "overall_passed": overall_passed,
        "overall_failed": (
            total - overall_passed
        ),
        "overall_pass": (
            total > 0
            and overall_passed == total
        ),
    }

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
