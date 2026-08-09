from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping

from src.backend_qualification_profiles import (
    build_fpga_qualification_manifest,
)
from src.backends.fpga_execute import (
    _iverilog_version,
)


TRI_BACKEND_SUMMARY_SCHEMA = (
    "cpc.tri-backend-summary.v1"
)

DEFAULT_SUMMARY = Path(
    "results/tri_backend_summary.json"
)

DEFAULT_OUTPUT = Path(
    "results/qualification"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the CPC FPGA backend qualification manifest "
            "from RFC-0008 tri-backend corpus-validation evidence."
        )
    )

    parser.add_argument(
        "--summary",
        type=Path,
        default=DEFAULT_SUMMARY,
        help=(
            "RFC-0008 tri-backend JSON summary "
            f"(default: {DEFAULT_SUMMARY})"
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=(
            "qualification manifest directory "
            f"(default: {DEFAULT_OUTPUT})"
        ),
    )

    return parser


def validate_fpga_summary(
    summary: Mapping[str, object],
) -> None:
    if summary.get("schema") != (
        TRI_BACKEND_SUMMARY_SCHEMA
    ):
        raise ValueError(
            "unsupported RFC-0008 tri-backend summary schema"
        )

    benchmark_count = int(
        summary.get(
            "benchmark_count",
            0,
        )
    )

    boundary_case_count = int(
        summary.get(
            "boundary_case_count",
            0,
        )
    )

    if benchmark_count <= 0:
        raise ValueError(
            "FPGA qualification requires a non-empty benchmark corpus"
        )

    if boundary_case_count <= 0:
        raise ValueError(
            "FPGA qualification requires non-empty boundary-case evidence"
        )

    fpga_semantic_passed = int(
        summary.get(
            "fpga_semantic_passed",
            -1,
        )
    )

    fpga_semantic_failed = int(
        summary.get(
            "fpga_semantic_failed",
            -1,
        )
    )

    overall_passed = int(
        summary.get(
            "overall_passed",
            -1,
        )
    )

    overall_failed = int(
        summary.get(
            "overall_failed",
            -1,
        )
    )

    if (
        fpga_semantic_passed
        != boundary_case_count
        or fpga_semantic_failed != 0
    ):
        raise ValueError(
            "FPGA qualification requires every FPGA semantic case to pass"
        )

    if (
        overall_passed
        != boundary_case_count
        or overall_failed != 0
        or summary.get("overall_pass") is not True
    ):
        raise ValueError(
            "FPGA qualification requires a fully passing tri-backend corpus"
        )


def main() -> int:
    args = build_parser().parse_args()

    summary = json.loads(
        args.summary.read_text(
            encoding="utf-8"
        )
    )

    validate_fpga_summary(
        summary
    )

    manifest = build_fpga_qualification_manifest(
        execution_engine_version=(
            _iverilog_version()
        ),
        summary=summary,
    )

    args.output.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        args.output
        / "fpga.backend-qualification.json"
    )

    output_path.write_text(
        manifest.to_json(),
        encoding="utf-8",
    )

    print(
        "CPC FPGA Backend Qualification"
    )
    print(
        "=============================="
    )
    print()

    print(
        "FPGA backend"
    )

    print(
        "  identity:      "
        f"{manifest.specification.backend_id}/"
        f"{manifest.specification.backend_version}"
    )

    print(
        "  engine:        "
        f"{manifest.execution.execution_engine} "
        f"{manifest.execution.execution_engine_version}"
    )

    assert manifest.corpus is not None

    print(
        "  corpus:        "
        f"{manifest.corpus.benchmark_count} benchmarks, "
        f"{manifest.corpus.boundary_case_count} cases"
    )

    print(
        "  qualification: "
        f"{'PASS' if manifest.corpus.overall_pass else 'FAIL'}"
    )

    print(
        f"  manifest hash: {manifest.manifest_hash}"
    )

    print(
        f"  output:        {output_path}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
