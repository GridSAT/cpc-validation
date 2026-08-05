from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt

from src.spice_model import DECODE_THRESHOLD_V
from src.transient_analysis import simulate_transient_response


BOUNDARY_CONDITIONS = (
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
)


@dataclass(frozen=True)
class ResistanceResult:
    resistance_kohm: float
    x0: int
    x3: int
    expected: int
    decoded: int
    passed: bool
    final_voltage: float
    signed_margin: float
    rise_time_ms: float | None
    settling_time_ms: float | None
    sample_count: int


@dataclass(frozen=True)
class ResistanceSummary:
    resistance_kohm: float
    simulations: int
    passed: int
    failed: int
    success_rate: float
    minimum_margin: float
    average_margin: float
    maximum_margin: float
    mean_high_rise_time_ms: float
    mean_high_settling_time_ms: float
    theoretical_rise_time_ms: float
    theoretical_settling_time_ms: float
    rise_time_relative_error: float
    settling_time_relative_error: float


def decimal_range(
    start: float,
    stop: float,
    step: float,
) -> list[float]:
    if step <= 0:
        raise ValueError("step must be greater than zero")

    if stop < start:
        raise ValueError("stop must be greater than or equal to start")

    count = int(round((stop - start) / step))

    values = [
        round(start + index * step, 12)
        for index in range(count + 1)
    ]

    if values[-1] < stop:
        values.append(round(stop, 12))

    return values


def theoretical_rise_time_ms(
    resistance_kohm: float,
    capacitance_uf: float,
) -> float:
    time_constant_ms = resistance_kohm * capacitance_uf
    return 2.197224577 * time_constant_ms


def theoretical_settling_time_ms(
    resistance_kohm: float,
    capacitance_uf: float,
    settling_fraction: float,
) -> float:
    import math

    time_constant_ms = resistance_kohm * capacitance_uf
    return -math.log(settling_fraction) * time_constant_ms


def relative_error(
    measured: float,
    theoretical: float,
) -> float:
    if theoretical == 0:
        raise ValueError("theoretical value must be nonzero")

    return abs(measured - theoretical) / theoretical


def run_resistance_sweep(
    *,
    resistance_start_kohm: float,
    resistance_stop_kohm: float,
    resistance_step_kohm: float,
    supply_voltage: float,
    capacitance_uf: float,
    threshold_voltage: float,
    step_time_ms: float,
    end_time_ms: float,
    settling_fraction: float,
) -> tuple[list[ResistanceResult], list[ResistanceSummary]]:
    resistances = decimal_range(
        resistance_start_kohm,
        resistance_stop_kohm,
        resistance_step_kohm,
    )

    results: list[ResistanceResult] = []
    summaries: list[ResistanceSummary] = []

    for resistance_kohm in resistances:
        resistance_results: list[ResistanceResult] = []

        for x0, x3 in BOUNDARY_CONDITIONS:
            response = simulate_transient_response(
                x0=x0,
                x3=x3,
                supply_voltage=supply_voltage,
                resistance_kohm=resistance_kohm,
                capacitance_uf=capacitance_uf,
                threshold_voltage=threshold_voltage,
                step_time_ms=step_time_ms,
                end_time_ms=end_time_ms,
                settling_fraction=settling_fraction,
            )

            item = ResistanceResult(
                resistance_kohm=resistance_kohm,
                x0=x0,
                x3=x3,
                expected=response.expected,
                decoded=response.decoded,
                passed=response.decoded == response.expected,
                final_voltage=response.final_voltage,
                signed_margin=response.signed_margin,
                rise_time_ms=(
                    1000.0 * response.rise_time_seconds
                    if response.rise_time_seconds is not None
                    else None
                ),
                settling_time_ms=(
                    1000.0 * response.settling_time_seconds
                    if response.settling_time_seconds is not None
                    else None
                ),
                sample_count=len(response.samples),
            )

            resistance_results.append(item)
            results.append(item)

        margins = [
            item.signed_margin
            for item in resistance_results
        ]

        high_rise_times = [
            item.rise_time_ms
            for item in resistance_results
            if item.expected == 1 and item.rise_time_ms is not None
        ]

        high_settling_times = [
            item.settling_time_ms
            for item in resistance_results
            if item.expected == 1 and item.settling_time_ms is not None
        ]

        if len(high_rise_times) != 2:
            raise RuntimeError(
                f"Expected two high-state rise times at {resistance_kohm} kOhm"
            )

        if len(high_settling_times) != 2:
            raise RuntimeError(
                f"Expected two high-state settling times at "
                f"{resistance_kohm} kOhm"
            )

        measured_rise = mean(high_rise_times)
        measured_settling = mean(high_settling_times)

        theory_rise = theoretical_rise_time_ms(
            resistance_kohm,
            capacitance_uf,
        )

        theory_settling = theoretical_settling_time_ms(
            resistance_kohm,
            capacitance_uf,
            settling_fraction,
        )

        passed = sum(item.passed for item in resistance_results)
        simulations = len(resistance_results)

        summaries.append(
            ResistanceSummary(
                resistance_kohm=resistance_kohm,
                simulations=simulations,
                passed=passed,
                failed=simulations - passed,
                success_rate=passed / simulations,
                minimum_margin=min(margins),
                average_margin=mean(margins),
                maximum_margin=max(margins),
                mean_high_rise_time_ms=measured_rise,
                mean_high_settling_time_ms=measured_settling,
                theoretical_rise_time_ms=theory_rise,
                theoretical_settling_time_ms=theory_settling,
                rise_time_relative_error=relative_error(
                    measured_rise,
                    theory_rise,
                ),
                settling_time_relative_error=relative_error(
                    measured_settling,
                    theory_settling,
                ),
            )
        )

    return results, summaries


def write_detailed_csv(
    output_path: Path,
    results: list[ResistanceResult],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.writer(handle)

        writer.writerow(
            (
                "resistance_kohm",
                "x0",
                "x3",
                "expected",
                "decoded",
                "passed",
                "final_voltage",
                "signed_margin",
                "rise_time_ms",
                "settling_time_ms",
                "sample_count",
            )
        )

        for item in results:
            writer.writerow(
                (
                    f"{item.resistance_kohm:.12f}",
                    item.x0,
                    item.x3,
                    item.expected,
                    item.decoded,
                    int(item.passed),
                    f"{item.final_voltage:.12f}",
                    f"{item.signed_margin:.12f}",
                    (
                        f"{item.rise_time_ms:.12f}"
                        if item.rise_time_ms is not None
                        else ""
                    ),
                    (
                        f"{item.settling_time_ms:.12f}"
                        if item.settling_time_ms is not None
                        else ""
                    ),
                    item.sample_count,
                )
            )


def write_summary_csv(
    output_path: Path,
    summaries: list[ResistanceSummary],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.writer(handle)

        writer.writerow(
            (
                "resistance_kohm",
                "simulations",
                "passed",
                "failed",
                "success_rate",
                "minimum_margin",
                "average_margin",
                "maximum_margin",
                "mean_high_rise_time_ms",
                "mean_high_settling_time_ms",
                "theoretical_rise_time_ms",
                "theoretical_settling_time_ms",
                "rise_time_relative_error",
                "settling_time_relative_error",
            )
        )

        for item in summaries:
            writer.writerow(
                (
                    f"{item.resistance_kohm:.12f}",
                    item.simulations,
                    item.passed,
                    item.failed,
                    f"{item.success_rate:.12f}",
                    f"{item.minimum_margin:.12f}",
                    f"{item.average_margin:.12f}",
                    f"{item.maximum_margin:.12f}",
                    f"{item.mean_high_rise_time_ms:.12f}",
                    f"{item.mean_high_settling_time_ms:.12f}",
                    f"{item.theoretical_rise_time_ms:.12f}",
                    f"{item.theoretical_settling_time_ms:.12f}",
                    f"{item.rise_time_relative_error:.12f}",
                    f"{item.settling_time_relative_error:.12f}",
                )
            )


def plot_timing(
    output_path: Path,
    summaries: list[ResistanceSummary],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    resistances = [
        item.resistance_kohm
        for item in summaries
    ]

    measured_rise = [
        item.mean_high_rise_time_ms
        for item in summaries
    ]

    theoretical_rise = [
        item.theoretical_rise_time_ms
        for item in summaries
    ]

    measured_settling = [
        item.mean_high_settling_time_ms
        for item in summaries
    ]

    theoretical_settling = [
        item.theoretical_settling_time_ms
        for item in summaries
    ]

    figure = plt.figure(figsize=(9, 5.5))
    axes = figure.add_subplot(111)

    axes.plot(
        resistances,
        measured_rise,
        marker="o",
        linewidth=1.8,
        markersize=4,
        label="Measured 10–90% rise time",
    )

    axes.plot(
        resistances,
        theoretical_rise,
        linestyle="--",
        linewidth=1.5,
        label="Theoretical 10–90% rise time",
    )

    axes.plot(
        resistances,
        measured_settling,
        marker="o",
        linewidth=1.8,
        markersize=4,
        label="Measured 1% settling time",
    )

    axes.plot(
        resistances,
        theoretical_settling,
        linestyle="--",
        linewidth=1.5,
        label="Theoretical 1% settling time",
    )

    axes.set_title("CPC RC Timing versus Resistance")
    axes.set_xlabel("Resistance (kOhm)")
    axes.set_ylabel("Time (ms)")
    axes.grid(True, alpha=0.3)
    axes.legend()

    figure.tight_layout()
    figure.savefig(output_path, dpi=200)
    plt.close(figure)


def plot_timing_error(
    output_path: Path,
    summaries: list[ResistanceSummary],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    resistances = [
        item.resistance_kohm
        for item in summaries
    ]

    rise_errors = [
        100.0 * item.rise_time_relative_error
        for item in summaries
    ]

    settling_errors = [
        100.0 * item.settling_time_relative_error
        for item in summaries
    ]

    figure = plt.figure(figsize=(9, 5.5))
    axes = figure.add_subplot(111)

    axes.plot(
        resistances,
        rise_errors,
        marker="o",
        linewidth=1.8,
        markersize=4,
        label="Rise-time relative error",
    )

    axes.plot(
        resistances,
        settling_errors,
        marker="o",
        linewidth=1.8,
        markersize=4,
        label="Settling-time relative error",
    )

    axes.set_title("CPC RC Timing Error versus Resistance")
    axes.set_xlabel("Resistance (kOhm)")
    axes.set_ylabel("Relative error (%)")
    axes.grid(True, alpha=0.3)
    axes.legend()

    figure.tight_layout()
    figure.savefig(output_path, dpi=200)
    plt.close(figure)


def plot_success_rate(
    output_path: Path,
    summaries: list[ResistanceSummary],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    resistances = [
        item.resistance_kohm
        for item in summaries
    ]

    success_rates = [
        100.0 * item.success_rate
        for item in summaries
    ]

    figure = plt.figure(figsize=(9, 5.5))
    axes = figure.add_subplot(111)

    axes.plot(
        resistances,
        success_rates,
        marker="o",
        linewidth=1.8,
        markersize=4,
    )

    axes.set_title("CPC Decoder Success Rate versus Resistance")
    axes.set_xlabel("Resistance (kOhm)")
    axes.set_ylabel("Success rate (%)")
    axes.set_ylim(-2.0, 102.0)
    axes.grid(True, alpha=0.3)

    figure.tight_layout()
    figure.savefig(output_path, dpi=200)
    plt.close(figure)


def print_summary(
    *,
    results: list[ResistanceResult],
    summaries: list[ResistanceSummary],
    detail_csv: Path,
    summary_csv: Path,
    timing_figure: Path,
    error_figure: Path,
    success_figure: Path,
) -> None:
    total = len(results)
    passed = sum(item.passed for item in results)
    failed = total - passed

    print("CPC deterministic resistance sweep")
    print()
    print(f"Resistance points:     {len(summaries)}")
    print(f"Boundary simulations:  {total}")
    print(f"Passed:                {passed}")
    print(f"Failed:                {failed}")
    print(f"Overall success rate:  {passed / total:.6%}")
    print()

    print(
        "Measured rise range:  "
        f"{min(item.mean_high_rise_time_ms for item in summaries):.6f} ms "
        "to "
        f"{max(item.mean_high_rise_time_ms for item in summaries):.6f} ms"
    )

    print(
        "Measured settle range:"
        f" {min(item.mean_high_settling_time_ms for item in summaries):.6f} ms "
        "to "
        f"{max(item.mean_high_settling_time_ms for item in summaries):.6f} ms"
    )

    print(
        "Maximum rise error:   "
        f"{100.0 * max(item.rise_time_relative_error for item in summaries):.6f}%"
    )

    print(
        "Maximum settle error: "
        f"{100.0 * max(item.settling_time_relative_error for item in summaries):.6f}%"
    )

    print(
        "Global minimum margin:"
        f" {min(item.signed_margin for item in results):.6f} V"
    )

    print()
    print(f"Detailed CSV:          {detail_csv}")
    print(f"Summary CSV:           {summary_csv}")
    print(f"Timing figure:         {timing_figure}")
    print(f"Timing-error figure:   {error_figure}")
    print(f"Success-rate figure:   {success_figure}")
    print()

    if failed:
        print("Resistance sweep: FAIL")
        raise SystemExit(1)

    if any(
        item.mean_high_settling_time_ms >= 150.0
        for item in summaries
    ):
        print("Resistance sweep: FAIL")
        print("At least one high response did not settle inside the run window.")
        raise SystemExit(1)

    print("Resistance sweep: PASS")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a deterministic resistance sweep with transient timing "
            "analysis for the CPC XOR RC baseline."
        )
    )

    parser.add_argument(
        "--start",
        type=float,
        default=5.0,
        help="Initial resistance in kilohms.",
    )

    parser.add_argument(
        "--stop",
        type=float,
        default=20.0,
        help="Final resistance in kilohms.",
    )

    parser.add_argument(
        "--step",
        type=float,
        default=1.0,
        help="Resistance increment in kilohms.",
    )

    parser.add_argument(
        "--supply",
        type=float,
        default=5.0,
        help="Supply voltage in volts.",
    )

    parser.add_argument(
        "--capacitance-uf",
        type=float,
        default=1.0,
        help="Output capacitance in microfarads.",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=DECODE_THRESHOLD_V,
        help="Decoder threshold in volts.",
    )

    parser.add_argument(
        "--step-time-ms",
        type=float,
        default=0.1,
        help="Transient output interval in milliseconds.",
    )

    parser.add_argument(
        "--end-time-ms",
        type=float,
        default=150.0,
        help="Transient simulation end time in milliseconds.",
    )

    parser.add_argument(
        "--settling-fraction",
        type=float,
        default=0.01,
        help="Fractional settling tolerance.",
    )

    parser.add_argument(
        "--detail-output",
        type=Path,
        default=Path("results/resistance_sweep.csv"),
    )

    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("results/resistance_sweep_summary.csv"),
    )

    parser.add_argument(
        "--timing-figure",
        type=Path,
        default=Path("figures/resistance_timing.png"),
    )

    parser.add_argument(
        "--error-figure",
        type=Path,
        default=Path("figures/resistance_timing_error.png"),
    )

    parser.add_argument(
        "--success-figure",
        type=Path,
        default=Path("figures/resistance_success_rate.png"),
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    results, summaries = run_resistance_sweep(
        resistance_start_kohm=arguments.start,
        resistance_stop_kohm=arguments.stop,
        resistance_step_kohm=arguments.step,
        supply_voltage=arguments.supply,
        capacitance_uf=arguments.capacitance_uf,
        threshold_voltage=arguments.threshold,
        step_time_ms=arguments.step_time_ms,
        end_time_ms=arguments.end_time_ms,
        settling_fraction=arguments.settling_fraction,
    )

    write_detailed_csv(
        arguments.detail_output,
        results,
    )

    write_summary_csv(
        arguments.summary_output,
        summaries,
    )

    plot_timing(
        arguments.timing_figure,
        summaries,
    )

    plot_timing_error(
        arguments.error_figure,
        summaries,
    )

    plot_success_rate(
        arguments.success_figure,
        summaries,
    )

    print_summary(
        results=results,
        summaries=summaries,
        detail_csv=arguments.detail_output,
        summary_csv=arguments.summary_output,
        timing_figure=arguments.timing_figure,
        error_figure=arguments.error_figure,
        success_figure=arguments.success_figure,
    )


if __name__ == "__main__":
    main()
