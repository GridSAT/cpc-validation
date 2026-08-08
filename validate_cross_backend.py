from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.ccir_lower_parity import lower_parity_instance_to_ccir
from src.cross_backend_validation import (
    CrossBackendValidationResult,
    validate_cross_backend,
)
from src.benchmark_io import load_parity_benchmark


def _parse_boundary(
    values: list[str],
) -> dict[int, int]:
    boundary: dict[int, int] = {}

    for item in values:
        if "=" not in item:
            raise ValueError(
                f"invalid boundary assignment {item!r}; "
                "expected VARIABLE=BIT"
            )

        variable_text, value_text = item.split(
            "=",
            1,
        )

        try:
            variable = int(
                variable_text
            )
        except ValueError as exc:
            raise ValueError(
                f"invalid boundary variable {variable_text!r}"
            ) from exc

        try:
            value = int(
                value_text
            )
        except ValueError as exc:
            raise ValueError(
                f"invalid boundary value {value_text!r}"
            ) from exc

        if variable < 0:
            raise ValueError(
                "boundary variable must be non-negative"
            )

        if value not in (
            0,
            1,
        ):
            raise ValueError(
                "boundary value must be 0 or 1"
            )

        if variable in boundary:
            raise ValueError(
                f"duplicate boundary assignment for variable {variable}"
            )

        boundary[
            variable
        ] = value

    return boundary


def _status(
    value: bool,
) -> str:
    return (
        "PASS"
        if value
        else "FAIL"
    )


def _print_result(
    benchmark_path: Path,
    result: CrossBackendValidationResult,
) -> None:
    boundary = dict(
        result.rc.prepared.metadata
    )["boundary_values"]

    print()
    print("CPC Cross-Backend Validation")
    print("=" * 40)
    print()
    print(
        f"Benchmark:            {benchmark_path}"
    )
    print(
        "Boundary:             "
        + ", ".join(
            f"x{variable}={value}"
            for variable, value in boundary
        )
    )
    print()

    print("RC Reference Backend")
    print(
        "  backend:            "
        f"{result.rc.prepared.backend_id}/"
        f"{result.rc.prepared.backend_version}"
    )
    print(
        "  execution engine:   "
        f"{dict(result.rc.observable.metadata).get('execution_engine')}"
    )
    print(
        f"  decoded result:     {result.rc.decoded}"
    )
    print()

    print("Digital Backend")
    print(
        "  backend:            "
        f"{result.digital.prepared.backend_id}/"
        f"{result.digital.prepared.backend_version}"
    )
    print(
        "  execution engine:   "
        f"{dict(result.digital.observable.metadata).get('execution_engine')}"
    )
    print(
        f"  decoded result:     {result.digital.decoded}"
    )
    print()

    print("Independent Reference")
    print(
        f"  semantic result:    {result.reference_result}"
    )
    print()

    print(
        "Backend agreement:    "
        f"{_status(result.backend_agreement)}"
    )
    print(
        "RC semantic match:    "
        f"{_status(result.rc_semantic_match)}"
    )
    print(
        "Digital semantic:     "
        f"{_status(result.digital_semantic_match)}"
    )
    print()
    print(
        "OVERALL:              "
        f"{_status(result.passed)}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compile and execute one canonical CPC constraint program "
            "through the RC and deterministic digital backends and "
            "independently validate both decoded results."
        )
    )

    parser.add_argument(
        "benchmark",
        type=Path,
        help="parity benchmark JSON file",
    )

    parser.add_argument(
        "--boundary",
        action="append",
        default=[],
        metavar="VARIABLE=BIT",
        help=(
            "boundary assignment, for example --boundary 0=0; "
            "repeat once per boundary variable"
        ),
    )

    args = parser.parse_args()

    try:
        instance = load_parity_benchmark(
            args.benchmark
        )

        program = lower_parity_instance_to_ccir(
            instance.instance
        )

        boundary = _parse_boundary(
            args.boundary
        )

        result = validate_cross_backend(
            program,
            boundary,
        )

    except (
        ValueError,
        OSError,
    ) as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )
        return 2

    _print_result(
        args.benchmark,
        result,
    )

    return (
        0
        if result.passed
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
