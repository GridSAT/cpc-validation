from __future__ import annotations

import argparse
from pathlib import Path

from src.cross_backend_benchmarks import (
    discover_benchmark_paths,
    validate_cross_backend_corpus,
    write_csv_report,
    write_json_summary,
)


DEFAULT_CSV_REPORT = Path(
    "results/cross_backend_validation.csv"
)

DEFAULT_JSON_SUMMARY = Path(
    "results/cross_backend_summary.json"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Exhaustively validate a benchmark corpus through the "
            "CPC RC and deterministic digital execution backends."
        )
    )

    parser.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        help=(
            "benchmark JSON files or directories containing "
            "benchmark JSON files"
        ),
    )

    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV_REPORT,
        help=(
            "CSV result path "
            f"(default: {DEFAULT_CSV_REPORT})"
        ),
    )

    parser.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_JSON_SUMMARY,
        help=(
            "JSON summary path "
            f"(default: {DEFAULT_JSON_SUMMARY})"
        ),
    )

    return parser


def main() -> int:
    args = build_parser().parse_args()

    benchmark_paths = discover_benchmark_paths(
        args.inputs
    )

    print(
        "CPC Cross-Backend Benchmark Validation"
    )
    print(
        "======================================"
    )
    print()

    print(
        f"Discovered benchmarks: {len(benchmark_paths)}"
    )

    for path in benchmark_paths:
        print(
            f"  {path}"
        )

    print()
    print(
        "Executing exhaustive boundary validation..."
    )

    results = validate_cross_backend_corpus(
        benchmark_paths
    )

    write_csv_report(
        args.csv,
        results,
    )

    write_json_summary(
        args.json,
        results,
    )

    total = len(results)

    backend_agreement = sum(
        result.backend_agreement
        for result in results
    )

    rc_semantic = sum(
        result.rc_semantic_match
        for result in results
    )

    digital_semantic = sum(
        result.digital_semantic_match
        for result in results
    )

    overall = sum(
        result.overall_pass
        for result in results
    )

    passed = (
        total > 0
        and overall == total
    )

    print()
    print(
        f"Benchmarks:             {len(benchmark_paths)}"
    )
    print(
        f"Boundary cases:         {total}"
    )
    print()

    print(
        "Backend agreement:      "
        f"{backend_agreement}/{total} "
        f"{'PASS' if backend_agreement == total else 'FAIL'}"
    )

    print(
        "RC semantic match:      "
        f"{rc_semantic}/{total} "
        f"{'PASS' if rc_semantic == total else 'FAIL'}"
    )

    print(
        "Digital semantic match: "
        f"{digital_semantic}/{total} "
        f"{'PASS' if digital_semantic == total else 'FAIL'}"
    )

    print()
    print(
        "OVERALL:                "
        f"{'PASS' if passed else 'FAIL'}"
    )

    print()
    print(
        f"CSV report:             {args.csv}"
    )
    print(
        f"JSON summary:           {args.json}"
    )

    return (
        0
        if passed
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
