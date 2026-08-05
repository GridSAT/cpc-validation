from __future__ import annotations

import argparse
import csv
import math
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Iterable, Sequence

import matplotlib.pyplot as plt

from generate_parity_benchmarks import (
    SUPPORTED_FAMILIES,
    GeneratedBenchmark,
    generate_benchmark,
    parse_size_specification,
    write_benchmark,
)
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


DEFAULT_SEED = 20260806
DEFAULT_SUPPLY_VOLTAGE = 5.0
DEFAULT_RESISTANCE_KOHM = 10.0
DEFAULT_CAPACITANCE_UF = 1.0
DEFAULT_THRESHOLD_VOLTAGE = 2.5
DEFAULT_END_TIME_MS = 50.0


@dataclass(frozen=True)
class BoundaryMeasurement:
    boundary_label: str
    expected: int
    decoded: int
    passed: bool
    completion_count: int
    output_voltage: float
    compilation_seconds: float
    simulation_seconds: float
    netlist_bytes: int


@dataclass(frozen=True)
class ScalingResult:
    family: str
    benchmark_name: str
    variable_count: int
    constraint_count: int
    boundary_variable_count: int
    internal_variable_count: int
    candidate_count: int
    candidate_source_count: int
    behavioral_source_count: int
    boundary_simulations: int
    passed: int
    failed: int
    success_rate: float
    minimum_netlist_bytes: int
    mean_netlist_bytes: float
    maximum_netlist_bytes: int
    total_compilation_seconds: float
    mean_compilation_seconds: float
    maximum_compilation_seconds: float
    total_simulation_seconds: float
    mean_simulation_seconds: float
    maximum_simulation_seconds: float
    minimum_output_voltage: float
    maximum_output_voltage: float
    minimum_completion_count: int
    maximum_completion_count: int


def random_constraint_count(
    variable_count: int,
    arity: int,
    requested: int | None,
) -> int:
    """
    Resolve a valid random-family constraint count.

    At least ceil(variable_count / arity) constraints are required for the
    generator's full-variable coverage contract. Four constraints are used as
    the minimum study density unless the caller supplies a larger value.
    """
    minimum_for_coverage = math.ceil(
        variable_count / arity
    )

    if requested is None:
        return max(
            4,
            minimum_for_coverage,
        )

    if requested < minimum_for_coverage:
        raise ValueError(
            "random constraint count is too small for full variable "
            f"coverage: variables={variable_count}, arity={arity}, "
            f"required_at_least={minimum_for_coverage}, "
            f"received={requested}"
        )

    return requested


def generate_study_benchmark(
    family: str,
    variable_count: int,
    *,
    random_constraints: int | None,
    random_arity: int,
    seed: int,
) -> GeneratedBenchmark:
    constraint_count: int | None = None

    if family == "random":
        constraint_count = random_constraint_count(
            variable_count,
            random_arity,
            random_constraints,
        )

    return generate_benchmark(
        family,
        variable_count,
        constraint_count=constraint_count,
        arity=random_arity,
        seed=seed,
    )


def validate_generated_benchmark(
    benchmark_path: Path,
    *,
    family: str,
    supply_voltage: float,
    resistance_kohm: float,
    capacitance_uf: float,
    threshold_voltage: float,
    end_time_ms: float,
    netlist_directory: Path,
) -> ScalingResult:
    benchmark = load_parity_benchmark(
        benchmark_path
    )

    netlist_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    measurements: list[BoundaryMeasurement] = []

    statistics = None

    for boundary_values in enumerate_boundary_assignments(
        benchmark.instance.boundary_variables
    ):
        reference = evaluate_parity_instance(
            benchmark.instance,
            boundary_values,
        )

        compilation_started = time.perf_counter()

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
            - compilation_started
        )

        statistics = compiled.statistics

        boundary_label = "_".join(
            f"x{variable}-{value}"
            for variable, value in sorted(
                boundary_values.items()
            )
        )

        netlist_path = (
            netlist_directory
            / f"{boundary_label}.cir"
        )

        log_path = (
            netlist_directory
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

        measurements.append(
            BoundaryMeasurement(
                boundary_label=",".join(
                    f"x{variable}={value}"
                    for variable, value in sorted(
                        boundary_values.items()
                    )
                ),
                expected=reference.continuation_value,
                decoded=decoded,
                passed=(
                    decoded
                    == reference.continuation_value
                ),
                completion_count=reference.completion_count,
                output_voltage=output_voltage,
                compilation_seconds=compilation_seconds,
                simulation_seconds=simulation_seconds,
                netlist_bytes=len(
                    compiled.netlist.encode("utf-8")
                ),
            )
        )

    if statistics is None:
        raise RuntimeError(
            f"benchmark produced no boundary measurements: {benchmark_path}"
        )

    compilation_times = [
        measurement.compilation_seconds
        for measurement in measurements
    ]

    simulation_times = [
        measurement.simulation_seconds
        for measurement in measurements
    ]

    netlist_sizes = [
        measurement.netlist_bytes
        for measurement in measurements
    ]

    output_voltages = [
        measurement.output_voltage
        for measurement in measurements
    ]

    completion_counts = [
        measurement.completion_count
        for measurement in measurements
    ]

    passed = sum(
        measurement.passed
        for measurement in measurements
    )

    boundary_simulations = len(measurements)

    return ScalingResult(
        family=family,
        benchmark_name=benchmark.name,
        variable_count=statistics.variable_count,
        constraint_count=statistics.constraint_count,
        boundary_variable_count=(
            statistics.boundary_variable_count
        ),
        internal_variable_count=(
            statistics.internal_variable_count
        ),
        candidate_count=statistics.candidate_count,
        candidate_source_count=(
            statistics.candidate_source_count
        ),
        behavioral_source_count=(
            statistics.behavioral_source_count
        ),
        boundary_simulations=boundary_simulations,
        passed=passed,
        failed=boundary_simulations - passed,
        success_rate=(
            passed / boundary_simulations
        ),
        minimum_netlist_bytes=min(netlist_sizes),
        mean_netlist_bytes=mean(netlist_sizes),
        maximum_netlist_bytes=max(netlist_sizes),
        total_compilation_seconds=sum(
            compilation_times
        ),
        mean_compilation_seconds=mean(
            compilation_times
        ),
        maximum_compilation_seconds=max(
            compilation_times
        ),
        total_simulation_seconds=sum(
            simulation_times
        ),
        mean_simulation_seconds=mean(
            simulation_times
        ),
        maximum_simulation_seconds=max(
            simulation_times
        ),
        minimum_output_voltage=min(
            output_voltages
        ),
        maximum_output_voltage=max(
            output_voltages
        ),
        minimum_completion_count=min(
            completion_counts
        ),
        maximum_completion_count=max(
            completion_counts
        ),
    )


def write_summary_csv(
    path: Path,
    results: Sequence[ScalingResult],
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
                "family",
                "benchmark_name",
                "variable_count",
                "constraint_count",
                "boundary_variable_count",
                "internal_variable_count",
                "candidate_count",
                "candidate_source_count",
                "behavioral_source_count",
                "boundary_simulations",
                "passed",
                "failed",
                "success_rate",
                "minimum_netlist_bytes",
                "mean_netlist_bytes",
                "maximum_netlist_bytes",
                "total_compilation_seconds",
                "mean_compilation_seconds",
                "maximum_compilation_seconds",
                "total_simulation_seconds",
                "mean_simulation_seconds",
                "maximum_simulation_seconds",
                "minimum_output_voltage",
                "maximum_output_voltage",
                "minimum_completion_count",
                "maximum_completion_count",
            )
        )

        for result in results:
            writer.writerow(
                (
                    result.family,
                    result.benchmark_name,
                    result.variable_count,
                    result.constraint_count,
                    result.boundary_variable_count,
                    result.internal_variable_count,
                    result.candidate_count,
                    result.candidate_source_count,
                    result.behavioral_source_count,
                    result.boundary_simulations,
                    result.passed,
                    result.failed,
                    f"{result.success_rate:.12f}",
                    result.minimum_netlist_bytes,
                    f"{result.mean_netlist_bytes:.6f}",
                    result.maximum_netlist_bytes,
                    f"{result.total_compilation_seconds:.12f}",
                    f"{result.mean_compilation_seconds:.12f}",
                    f"{result.maximum_compilation_seconds:.12f}",
                    f"{result.total_simulation_seconds:.12f}",
                    f"{result.mean_simulation_seconds:.12f}",
                    f"{result.maximum_simulation_seconds:.12f}",
                    f"{result.minimum_output_voltage:.12f}",
                    f"{result.maximum_output_voltage:.12f}",
                    result.minimum_completion_count,
                    result.maximum_completion_count,
                )
            )


def grouped_results(
    results: Sequence[ScalingResult],
) -> dict[str, list[ScalingResult]]:
    grouped: dict[str, list[ScalingResult]] = {}

    for result in results:
        grouped.setdefault(
            result.family,
            [],
        ).append(result)

    for family_results in grouped.values():
        family_results.sort(
            key=lambda result: result.variable_count
        )

    return grouped


def plot_candidate_growth(
    results: Sequence[ScalingResult],
    path: Path,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure, axis = plt.subplots()

    for family, family_results in grouped_results(
        results
    ).items():
        axis.plot(
            [
                result.variable_count
                for result in family_results
            ],
            [
                result.candidate_count
                for result in family_results
            ],
            marker="o",
            label=family,
        )

    axis.set_xlabel("Variables")
    axis.set_ylabel("Candidate assignments")
    axis.set_yscale("log", base=2)
    axis.set_title("CPC Candidate Growth")
    axis.grid(True)
    axis.legend()
    figure.tight_layout()
    figure.savefig(
        path,
        dpi=200,
    )
    plt.close(figure)


def plot_behavioral_source_growth(
    results: Sequence[ScalingResult],
    path: Path,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure, axis = plt.subplots()

    for family, family_results in grouped_results(
        results
    ).items():
        axis.plot(
            [
                result.variable_count
                for result in family_results
            ],
            [
                result.behavioral_source_count
                for result in family_results
            ],
            marker="o",
            label=family,
        )

    axis.set_xlabel("Variables")
    axis.set_ylabel("Behavioral sources")
    axis.set_yscale("log", base=2)
    axis.set_title("CPC Behavioral-Source Growth")
    axis.grid(True)
    axis.legend()
    figure.tight_layout()
    figure.savefig(
        path,
        dpi=200,
    )
    plt.close(figure)


def plot_netlist_growth(
    results: Sequence[ScalingResult],
    path: Path,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure, axis = plt.subplots()

    for family, family_results in grouped_results(
        results
    ).items():
        axis.plot(
            [
                result.variable_count
                for result in family_results
            ],
            [
                result.mean_netlist_bytes
                for result in family_results
            ],
            marker="o",
            label=family,
        )

    axis.set_xlabel("Variables")
    axis.set_ylabel("Mean netlist size (bytes)")
    axis.set_title("CPC Generated-Netlist Growth")
    axis.grid(True)
    axis.legend()
    figure.tight_layout()
    figure.savefig(
        path,
        dpi=200,
    )
    plt.close(figure)


def plot_compilation_time(
    results: Sequence[ScalingResult],
    path: Path,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure, axis = plt.subplots()

    for family, family_results in grouped_results(
        results
    ).items():
        axis.plot(
            [
                result.variable_count
                for result in family_results
            ],
            [
                1000.0
                * result.mean_compilation_seconds
                for result in family_results
            ],
            marker="o",
            label=family,
        )

    axis.set_xlabel("Variables")
    axis.set_ylabel("Mean compilation time (ms)")
    axis.set_title("CPC Compilation Time")
    axis.grid(True)
    axis.legend()
    figure.tight_layout()
    figure.savefig(
        path,
        dpi=200,
    )
    plt.close(figure)


def plot_simulation_time(
    results: Sequence[ScalingResult],
    path: Path,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure, axis = plt.subplots()

    for family, family_results in grouped_results(
        results
    ).items():
        axis.plot(
            [
                result.variable_count
                for result in family_results
            ],
            [
                1000.0
                * result.mean_simulation_seconds
                for result in family_results
            ],
            marker="o",
            label=family,
        )

    axis.set_xlabel("Variables")
    axis.set_ylabel("Mean ngspice time (ms)")
    axis.set_title("CPC ngspice Simulation Time")
    axis.grid(True)
    axis.legend()
    figure.tight_layout()
    figure.savefig(
        path,
        dpi=200,
    )
    plt.close(figure)


def parse_family_list(
    text: str,
) -> tuple[str, ...]:
    families = tuple(
        item.strip()
        for item in text.split(",")
        if item.strip()
    )

    if not families:
        raise ValueError(
            "at least one benchmark family is required"
        )

    unknown = [
        family
        for family in families
        if family not in SUPPORTED_FAMILIES
    ]

    if unknown:
        raise ValueError(
            "unsupported benchmark families: "
            + ", ".join(unknown)
        )

    if len(set(families)) != len(families):
        raise ValueError(
            "benchmark families may not be repeated"
        )

    return families


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate, compile, simulate, validate, and aggregate "
            "CPC parity benchmark scaling data."
        )
    )

    parser.add_argument(
        "--families",
        default="chain,cycle,star,random",
        help=(
            "Comma-separated benchmark families. "
            "Default: chain,cycle,star,random."
        ),
    )

    parser.add_argument(
        "--variables",
        default="4:10:2",
        help=(
            "Variable count or inclusive START:STOP:STEP range. "
            "Default: 4:10:2."
        ),
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Random-family seed.",
    )

    parser.add_argument(
        "--random-constraints",
        type=int,
        default=None,
        help=(
            "Fixed random-family constraint count. By default the study "
            "uses the larger of four or ceil(variables / arity)."
        ),
    )

    parser.add_argument(
        "--random-arity",
        type=int,
        default=3,
        help="Random-family constraint arity.",
    )

    parser.add_argument(
        "--supply",
        type=float,
        default=DEFAULT_SUPPLY_VOLTAGE,
    )

    parser.add_argument(
        "--resistance-kohm",
        type=float,
        default=DEFAULT_RESISTANCE_KOHM,
    )

    parser.add_argument(
        "--capacitance-uf",
        type=float,
        default=DEFAULT_CAPACITANCE_UF,
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD_VOLTAGE,
    )

    parser.add_argument(
        "--end-time-ms",
        type=float,
        default=DEFAULT_END_TIME_MS,
    )

    parser.add_argument(
        "--working-directory",
        type=Path,
        default=Path("results/scaling_work"),
    )

    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("results/scaling_summary.csv"),
    )

    parser.add_argument(
        "--candidate-figure",
        type=Path,
        default=Path("figures/scaling_candidates.png"),
    )

    parser.add_argument(
        "--source-figure",
        type=Path,
        default=Path("figures/scaling_sources.png"),
    )

    parser.add_argument(
        "--netlist-figure",
        type=Path,
        default=Path("figures/scaling_netlist_size.png"),
    )

    parser.add_argument(
        "--compilation-figure",
        type=Path,
        default=Path("figures/scaling_compile_time.png"),
    )

    parser.add_argument(
        "--simulation-figure",
        type=Path,
        default=Path("figures/scaling_simulation_time.png"),
    )

    parser.add_argument(
        "--keep-work",
        action="store_true",
        help="Retain generated benchmark, netlist, and ngspice work files.",
    )

    return parser.parse_args()


def run_scaling_study(
    *,
    families: Sequence[str],
    variable_counts: Sequence[int],
    seed: int,
    random_constraints: int | None,
    random_arity: int,
    supply_voltage: float,
    resistance_kohm: float,
    capacitance_uf: float,
    threshold_voltage: float,
    end_time_ms: float,
    working_directory: Path,
) -> list[ScalingResult]:
    if working_directory.exists():
        shutil.rmtree(working_directory)

    benchmark_directory = (
        working_directory
        / "benchmarks"
    )

    netlist_root = (
        working_directory
        / "netlists"
    )

    results: list[ScalingResult] = []

    for family in families:
        for variable_count in variable_counts:
            benchmark = generate_study_benchmark(
                family,
                variable_count,
                random_constraints=random_constraints,
                random_arity=random_arity,
                seed=seed,
            )

            benchmark_path = (
                benchmark_directory
                / family
                / f"{benchmark.name}.json"
            )

            write_benchmark(
                benchmark,
                benchmark_path,
            )

            result = validate_generated_benchmark(
                benchmark_path,
                family=family,
                supply_voltage=supply_voltage,
                resistance_kohm=resistance_kohm,
                capacitance_uf=capacitance_uf,
                threshold_voltage=threshold_voltage,
                end_time_ms=end_time_ms,
                netlist_directory=(
                    netlist_root
                    / family
                    / benchmark.name
                ),
            )

            results.append(result)

    return results


def print_results(
    results: Sequence[ScalingResult],
) -> None:
    print(
        f"{'Family':10} "
        f"{'Vars':>5} "
        f"{'Cons':>5} "
        f"{'Int':>5} "
        f"{'Cand':>7} "
        f"{'Sources':>8} "
        f"{'Bytes':>10} "
        f"{'Compile ms':>12} "
        f"{'SPICE ms':>10} "
        f"{'Pass':>7}"
    )

    print("-" * 98)

    for result in sorted(
        results,
        key=lambda item: (
            item.family,
            item.variable_count,
        ),
    ):
        print(
            f"{result.family:10} "
            f"{result.variable_count:5d} "
            f"{result.constraint_count:5d} "
            f"{result.internal_variable_count:5d} "
            f"{result.candidate_count:7d} "
            f"{result.behavioral_source_count:8d} "
            f"{result.mean_netlist_bytes:10.0f} "
            f"{1000.0 * result.mean_compilation_seconds:12.6f} "
            f"{1000.0 * result.mean_simulation_seconds:10.6f} "
            f"{result.passed:2d}/{result.boundary_simulations:<4d}"
        )


def main() -> None:
    arguments = parse_arguments()

    families = parse_family_list(
        arguments.families
    )

    variable_counts = parse_size_specification(
        arguments.variables
    )

    print("CPC compiler scaling study")
    print()
    print(
        "Families:           "
        + ", ".join(families)
    )
    print(
        "Variable counts:    "
        + ", ".join(
            str(value)
            for value in variable_counts
        )
    )
    print(f"Random seed:         {arguments.seed}")
    print()

    started = time.perf_counter()

    results = run_scaling_study(
        families=families,
        variable_counts=variable_counts,
        seed=arguments.seed,
        random_constraints=arguments.random_constraints,
        random_arity=arguments.random_arity,
        supply_voltage=arguments.supply,
        resistance_kohm=arguments.resistance_kohm,
        capacitance_uf=arguments.capacitance_uf,
        threshold_voltage=arguments.threshold,
        end_time_ms=arguments.end_time_ms,
        working_directory=arguments.working_directory,
    )

    elapsed_seconds = (
        time.perf_counter()
        - started
    )

    write_summary_csv(
        arguments.summary_output,
        results,
    )

    plot_candidate_growth(
        results,
        arguments.candidate_figure,
    )

    plot_behavioral_source_growth(
        results,
        arguments.source_figure,
    )

    plot_netlist_growth(
        results,
        arguments.netlist_figure,
    )

    plot_compilation_time(
        results,
        arguments.compilation_figure,
    )

    plot_simulation_time(
        results,
        arguments.simulation_figure,
    )

    print_results(results)

    total_boundary_simulations = sum(
        result.boundary_simulations
        for result in results
    )

    total_passed = sum(
        result.passed
        for result in results
    )

    total_failed = sum(
        result.failed
        for result in results
    )

    print()
    print(f"Benchmarks:           {len(results)}")
    print(
        f"Boundary simulations: {total_boundary_simulations}"
    )
    print(f"Passed:               {total_passed}")
    print(f"Failed:               {total_failed}")
    print(f"Measured runtime:     {elapsed_seconds:.6f} s")
    print()
    print(f"Summary CSV:          {arguments.summary_output}")
    print(f"Candidate figure:     {arguments.candidate_figure}")
    print(f"Source figure:        {arguments.source_figure}")
    print(f"Netlist figure:       {arguments.netlist_figure}")
    print(f"Compilation figure:   {arguments.compilation_figure}")
    print(f"Simulation figure:    {arguments.simulation_figure}")

    if not arguments.keep_work:
        shutil.rmtree(
            arguments.working_directory,
            ignore_errors=True,
        )

    print()

    if total_failed:
        print("Compiler scaling study: FAIL")
        raise SystemExit(1)

    print("Compiler scaling study: PASS")


if __name__ == "__main__":
    main()
