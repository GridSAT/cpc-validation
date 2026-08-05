from __future__ import annotations

import argparse
from pathlib import Path

from src.benchmark_io import (
    load_boundary_values,
    load_parity_benchmark,
)
from src.compiler import compile_parity_instance
from src.spice_model import (
    _read_measured_voltage,
    _run_ngspice,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compile and simulate a parity benchmark supplied as JSON."
        )
    )

    parser.add_argument(
        "benchmark",
        type=Path,
        help="Path to the benchmark JSON file.",
    )

    parser.add_argument(
        "--boundary",
        required=True,
        help=(
            "Boundary assignment, for example "
            "'x0=0,x3=1'."
        ),
    )

    parser.add_argument(
        "--supply",
        type=float,
        default=5.0,
        help="Supply voltage in volts.",
    )

    parser.add_argument(
        "--resistance-kohm",
        type=float,
        default=10.0,
        help="Output resistance in kilohms.",
    )

    parser.add_argument(
        "--capacitance-uf",
        type=float,
        default=1.0,
        help="Output capacitance in microfarads.",
    )

    parser.add_argument(
        "--end-time-ms",
        type=float,
        default=50.0,
        help="Transient simulation end time in milliseconds.",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=2.5,
        help="Decoder threshold in volts.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("netlists/benchmark.cir"),
        help="Generated netlist output path.",
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    benchmark = load_parity_benchmark(
        arguments.benchmark
    )

    boundary_values = load_boundary_values(
        arguments.boundary,
        benchmark.instance.boundary_variables,
    )

    compiled = compile_parity_instance(
        benchmark.instance,
        boundary_values,
        supply_voltage=arguments.supply,
        resistance_kohm=arguments.resistance_kohm,
        capacitance_uf=arguments.capacitance_uf,
        end_time_ms=arguments.end_time_ms,
    )

    arguments.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    arguments.output.write_text(
        compiled.netlist,
        encoding="utf-8",
    )

    log_path = arguments.output.with_suffix(".out")

    _run_ngspice(
        arguments.output,
        log_path,
    )

    output_voltage = _read_measured_voltage(
        log_path
    )

    decoded = int(
        output_voltage >= arguments.threshold
    )

    statistics = compiled.statistics

    print("CPC JSON parity benchmark")
    print()
    print(f"Benchmark:          {benchmark.name}")
    print(f"Source:             {benchmark.source_path}")
    print(f"Description:        {benchmark.description}")
    print(
        "Boundary:           "
        + ", ".join(
            f"x{variable}={boundary_values[variable]}"
            for variable in benchmark.instance.boundary_variables
        )
    )
    print(f"Constraints:        {statistics.constraint_count}")
    print(f"Variables:          {statistics.variable_count}")
    print(
        f"Boundary variables: {statistics.boundary_variable_count}"
    )
    print(
        f"Internal variables: {statistics.internal_variable_count}"
    )
    print(f"Candidates:         {statistics.candidate_count}")
    print(
        f"Behavioral sources: {statistics.behavioral_source_count}"
    )
    print(f"Output voltage:     {output_voltage:.6f} V")
    print(f"Decoded value:      {decoded}")
    print(f"Netlist:            {arguments.output}")
    print(f"ngspice log:        {log_path}")
    print()
    print("Benchmark compilation and simulation: PASS")


if __name__ == "__main__":
    main()
