from __future__ import annotations

import argparse
import csv
import time
from dataclasses import dataclass
from pathlib import Path

from src.benchmark_io import load_parity_benchmark
from src.compiler import compile_parity_instance
from src.generic_reference import (
    enumerate_boundary_assignments,
    evaluate_parity_instance,
)
from src.spice_model import (
    _read_measured_voltage,
    _run_ngspice,
)


@dataclass(frozen=True)
class BenchmarkValidationResult:
    benchmark_name: str
    benchmark_path: Path
    boundary_values: tuple[tuple[int, int], ...]
    expected: int
    decoded: int
    passed: bool
    output_voltage: float
    completion_count: int
    constraint_count: int
    variable_count: int
    internal_variable_count: int
    candidate_count: int
    netlist_bytes: int
    compilation_seconds: float
    simulation_seconds: float


def validate_benchmark(
    benchmark_path: Path,
    *,
    supply_voltage: float,
    resistance_kohm: float,
    capacitance_uf: float,
    threshold_voltage: float,
    end_time_ms: float,
    working_directory: Path,
) -> list[BenchmarkValidationResult]:
    benchmark = load_parity_benchmark(
        benchmark_path
    )

    results: list[BenchmarkValidationResult] = []

    benchmark_directory = (
        working_directory
        / benchmark.name
    )
    benchmark_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    for boundary_values in enumerate_boundary_assignments(
        benchmark.instance.boundary_variables
    ):
        reference = evaluate_parity_instance(
            benchmark.instance,
            boundary_values,
        )

        compiled_started = time.perf_counter()

        compiled = compile_parity_instance(
            benchmark.instance,
            boundary_values,
            supply_voltage=supply_voltage,
            resistance_kohm=resistance_kohm,
            capacitance_uf=capacitance_uf,
            end_time_ms=end_time_ms,
        )

        compilation_seconds = (
            time.perf_counter()
            - compiled_started
        )

        boundary_label = "_".join(
            f"x{variable}-{value}"
            for variable, value in sorted(
                boundary_values.items()
            )
        )

        netlist_path = (
            benchmark_directory
            / f"{boundary_label}.cir"
        )
        log_path = (
            benchmark_directory
            / f"{boundary_label}.out"
        )

        netlist_path.write_text(
            compiled.netlist,
            encoding="utf-8",
        )

        simulation_started = time.perf_counter()

        _run_ngspice(
            netlist_path,
            log_path,
        )

        simulation_seconds = (
            time.perf_counter()
            - simulation_started
        )

        output_voltage = _read_measured_voltage(
            log_path
        )
        decoded = int(
            output_voltage >= threshold_voltage
        )

        statistics = compiled.statistics

        results.append(
            BenchmarkValidationResult(
                benchmark_name=benchmark.name,
                benchmark_path=benchmark_path,
                boundary_values=tuple(
                    sorted(
                        boundary_values.items()
                    )
                ),
                expected=reference.continuation_value,
                decoded=decoded,
                passed=(
                    decoded
                    == reference.continuation_value
                ),
                output_voltage=output_voltage,
                completion_count=reference.completion_count,
                constraint_count=statistics.constraint_count,
                variable_count=statistics.variable_count,
                internal_variable_count=(
                    statistics.internal_variable_count
                ),
                candidate_count=statistics.candidate_count,
                netlist_bytes=len(
                    compiled.netlist.encode("utf-8")
                ),
                compilation_seconds=compilation_seconds,
                simulation_seconds=simulation_seconds,
            )
        )

    return results


def write_csv(
    path: Path,
    results: list[BenchmarkValidationResult],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.writer(handle)

        writer.writerow(
            (
                "benchmark",
                "benchmark_path",
                "boundary",
                "expected",
                "decoded",
                "passed",
                "output_voltage",
                "completion_count",
                "constraint_count",
                "variable_count",
                "internal_variable_count",
                "candidate_count",
                "netlist_bytes",
                "compilation_seconds",
                "simulation_seconds",
            )
        )

        for result in results:
            boundary = ",".join(
                f"x{variable}={value}"
                for variable, value in (
                    result.boundary_values
                )
            )

            writer.writerow(
                (
                    result.benchmark_name,
                    result.benchmark_path,
                    boundary,
                    result.expected,
                    result.decoded,
                    int(result.passed),
                    f"{result.output_voltage:.12f}",
                    result.completion_count,
                    result.constraint_count,
                    result.variable_count,
                    result.internal_variable_count,
                    result.candidate_count,
                    result.netlist_bytes,
                    f"{result.compilation_seconds:.12f}",
                    f"{result.simulation_seconds:.12f}",
                )
            )


def discover_benchmark_paths(
    inputs: list[Path],
) -> list[Path]:
    """
    Resolve benchmark files from explicit JSON paths and directories.

    Directories are searched recursively for ``*.json`` files. Results are
    deduplicated and returned in deterministic sorted order.
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
                    f"benchmark file must use the .json extension: "
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

    return sorted(
        discovered,
        key=lambda path: path.as_posix(),
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate every boundary assignment for one or more "
            "JSON parity benchmarks."
        )
    )

    parser.add_argument(
        "benchmarks",
        nargs="+",
        type=Path,
        help=(
            "Benchmark JSON files or directories searched recursively "
            "for JSON benchmark files."
        ),
    )

    parser.add_argument(
        "--supply",
        type=float,
        default=5.0,
    )

    parser.add_argument(
        "--resistance-kohm",
        type=float,
        default=10.0,
    )

    parser.add_argument(
        "--capacitance-uf",
        type=float,
        default=1.0,
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=2.5,
    )

    parser.add_argument(
        "--end-time-ms",
        type=float,
        default=50.0,
    )

    parser.add_argument(
        "--working-directory",
        type=Path,
        default=Path(
            "netlists/benchmark-validation"
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/benchmark_validation.csv"
        ),
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    benchmark_paths = discover_benchmark_paths(
        arguments.benchmarks
    )

    all_results: list[
        BenchmarkValidationResult
    ] = []

    print("CPC generic benchmark validation")
    print()

    for benchmark_path in benchmark_paths:
        benchmark_results = validate_benchmark(
            benchmark_path,
            supply_voltage=arguments.supply,
            resistance_kohm=(
                arguments.resistance_kohm
            ),
            capacitance_uf=arguments.capacitance_uf,
            threshold_voltage=arguments.threshold,
            end_time_ms=arguments.end_time_ms,
            working_directory=(
                arguments.working_directory
            ),
        )

        all_results.extend(
            benchmark_results
        )

        passed = sum(
            result.passed
            for result in benchmark_results
        )
        total = len(benchmark_results)

        first = benchmark_results[0]

        print(
            f"{first.benchmark_name}: "
            f"{passed}/{total} boundary assignments PASS; "
            f"constraints={first.constraint_count}; "
            f"variables={first.variable_count}; "
            f"internal={first.internal_variable_count}; "
            f"candidates={first.candidate_count}"
        )

        for result in benchmark_results:
            boundary = " ".join(
                f"x{variable}={value}"
                for variable, value in (
                    result.boundary_values
                )
            )

            print(
                f"  {boundary} "
                f"expected={result.expected} "
                f"decoded={result.decoded} "
                f"completions={result.completion_count} "
                f"vout={result.output_voltage:.6f} V "
                f"{'PASS' if result.passed else 'FAIL'}"
            )

        print()

    write_csv(
        arguments.output,
        all_results,
    )

    passed = sum(
        result.passed
        for result in all_results
    )
    total = len(all_results)

    print(f"Benchmarks:            {len(benchmark_paths)}")
    print(f"Boundary simulations:  {total}")
    print(f"Passed:                {passed}")
    print(f"Failed:                {total - passed}")
    print(f"CSV result:            {arguments.output}")
    print()

    if passed != total:
        print("Generic benchmark validation: FAIL")
        raise SystemExit(1)

    print("Generic benchmark validation: PASS")


if __name__ == "__main__":
    main()
