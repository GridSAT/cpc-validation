from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.backend_qualification_profiles import (
    build_digital_qualification_manifest,
    build_rc_qualification_manifest,
)
from src.spice_model import _ngspice_version


DEFAULT_SUMMARY = Path(
    "results/cross_backend_summary.json"
)

DEFAULT_OUTPUT = Path(
    "results/qualification"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate CPC backend qualification manifests from "
            "RFC-0006 corpus-validation evidence."
        )
    )

    parser.add_argument(
        "--summary",
        type=Path,
        default=DEFAULT_SUMMARY,
        help=(
            "RFC-0006 JSON summary "
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


def main() -> int:
    args = build_parser().parse_args()

    summary = json.loads(
        args.summary.read_text(
            encoding="utf-8"
        )
    )

    if summary.get("schema") != (
        "cpc.cross-backend-summary.v1"
    ):
        raise ValueError(
            "unsupported RFC-0006 summary schema"
        )

    if summary.get("overall_pass") is not True:
        raise ValueError(
            "backend qualification requires a passing "
            "RFC-0006 corpus summary"
        )

    rc = build_rc_qualification_manifest(
        execution_engine_version=(
            _ngspice_version()
        ),
        summary=summary,
    )

    digital = build_digital_qualification_manifest(
        summary=summary
    )

    args.output.mkdir(
        parents=True,
        exist_ok=True,
    )

    rc_path = (
        args.output
        / "rc.backend-qualification.json"
    )

    digital_path = (
        args.output
        / "digital.backend-qualification.json"
    )

    rc_path.write_text(
        rc.to_json(),
        encoding="utf-8",
    )

    digital_path.write_text(
        digital.to_json(),
        encoding="utf-8",
    )

    print(
        "CPC Backend Qualification"
    )
    print(
        "========================="
    )
    print()

    for name, manifest, path in (
        (
            "RC",
            rc,
            rc_path,
        ),
        (
            "Digital",
            digital,
            digital_path,
        ),
    ):
        print(
            f"{name} backend"
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
            f"  output:        {path}"
        )

        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
