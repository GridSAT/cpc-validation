from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt

from src.spice_model import simulate_response


BOUNDARY_CONDITIONS = (
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
)


@dataclass(frozen=True)
class ThresholdResult:
    threshold_voltage: float
    x0: int
    x3: int
    expected: int
    decoded: int
    passed: bool
    output_voltage: float
    signed_margin: float


@dataclass(frozen=True)
class ThresholdSummary:
    threshold_voltage: float
    simulations: int
    passed: int
    failed: int
    success_rate: float
    minimum_margin: float
    average_margin: float
    maximum_margin: float


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


def signed_decoding_margin(
    *,
    expected: int,
    output_voltage: float,
    threshold_voltage: float,
) -> float:
    if expected == 1:
        return output_voltage - threshold_voltage

    return threshold_voltage - output_voltage


def run_threshold_sweep(
    *,
    threshold_start: float,
    threshold_stop: float,
    threshold_step: float,
    supply_voltage: float,
    resistance_kohm: float,
    capacitance_uf: float,
) -> tuple[list[ThresholdResult], list[ThresholdSummary]]:
    thresholds = decimal_range(
        threshold_start,
        threshold_stop,
        threshold_step,
    )

    results: list[ThresholdResult] = []
    summaries: list[ThresholdSummary] = []

    for threshold_voltage in thresholds:
        threshold_results: list[ThresholdResult] = []

        for x0, x3 in BOUNDARY_CONDITIONS:
            response = simulate_response(
                x0=x0,
                x3=x3,
                supply_voltage=supply_voltage,
                resistance_kohm=resistance_kohm,
                capacitance_uf=capacitance_uf,
                threshold_voltage=threshold_voltage,
            )

            margin = signed_decoding_margin(
                expected=response.expected,
                output_voltage=response.output_voltage,
                threshold_voltage=threshold_voltage,
            )

            item = ThresholdResult(
                threshold_voltage=threshold_voltage,
                x0=x0,
                x3=x3,
                expected=response.expected,
                decoded=response.decoded,
                passed=response.decoded == response.expected,
                output_voltage=response.output_voltage,
                signed_margin=margin,
            )

            threshold_results.append(item)
            results.append(item)

        margins = [
            item.signed_margin
            for item in threshold_results
        ]
        passed = sum(item.passed for item in threshold_results)
        simulations = len(threshold_results)

        summaries.append(
            ThresholdSummary(
                threshold_voltage=threshold_voltage,
                simulations=simulations,
                passed=passed,
                failed=simulations - passed,
                success_rate=passed / simulations,
                minimum_margin=min(margins),
                average_margin=mean(margins),
                maximum_margin=max(margins),
            )
        )

    return results, summaries


def write_detailed_csv(
    output_path: Path,
    results: list[ThresholdResult],
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
                "threshold_voltage",
                "x0",
                "x3",
                "expected",
                "decoded",
                "passed",
                "output_voltage",
                "signed_margin",
            )
        )

        for item in results:
            writer.writerow(
                (
                    f"{item.threshold_voltage:.12f}",
                    item.x0,
                    item.x3,
                    item.expected,
                    item.decoded,
                    int(item.passed),
                    f"{item.output_voltage:.12f}",
                    f"{item.signed_margin:.12f}",
                )
            )


def write_summary_csv(
    output_path: Path,
    summaries: list[ThresholdSummary],
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
                "threshold_voltage",
                "simulations",
                "passed",
                "failed",
                "success_rate",
                "minimum_margin",
                "average_margin",
                "maximum_margin",
            )
        )

        for item in summaries:
            writer.writerow(
                (
                    f"{item.threshold_voltage:.12f}",
                    item.simulations,
                    item.passed,
                    item.failed,
                    f"{item.success_rate:.12f}",
                    f"{item.minimum_margin:.12f}",
                    f"{item.average_margin:.12f}",
                    f"{item.maximum_margin:.12f}",
                )
            )


def plot_success_rate(
    output_path: Path,
    summaries: list[ThresholdSummary],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    thresholds = [
        item.threshold_voltage
        for item in summaries
    ]
    success_rates = [
        100.0 * item.success_rate
        for item in summaries
    ]

    figure = plt.figure(figsize=(9, 5.5))
    axes = figure.add_subplot(111)

    axes.plot(
        thresholds,
        success_rates,
        marker="o",
        linewidth=1.8,
        markersize=4,
    )

    axes.set_title("CPC Decoder Success Rate versus Threshold")
    axes.set_xlabel("Decoder threshold (V)")
    axes.set_ylabel("Success rate (%)")
    axes.set_ylim(-2.0, 102.0)
    axes.grid(True, alpha=0.3)

    figure.tight_layout()
    figure.savefig(output_path, dpi=200)
    plt.close(figure)


def plot_margin(
    output_path: Path,
    summaries: list[ThresholdSummary],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    thresholds = [
        item.threshold_voltage
        for item in summaries
    ]
    minimum_margins = [
        item.minimum_margin
        for item in summaries
    ]
    average_margins = [
        item.average_margin
        for item in summaries
    ]
    maximum_margins = [
        item.maximum_margin
        for item in summaries
    ]

    figure = plt.figure(figsize=(9, 5.5))
    axes = figure.add_subplot(111)

    axes.plot(
        thresholds,
        minimum_margins,
        marker="o",
        linewidth=1.8,
        markersize=4,
        label="Minimum signed margin",
    )
    axes.plot(
        thresholds,
        average_margins,
        linewidth=1.8,
        label="Average signed margin",
    )
    axes.plot(
        thresholds,
        maximum_margins,
        linewidth=1.8,
        label="Maximum signed margin",
    )
    axes.axhline(
        0.0,
        linewidth=1.0,
    )

    axes.set_title("CPC Decoder Margin versus Threshold")
    axes.set_xlabel("Decoder threshold (V)")
    axes.set_ylabel("Signed decoding margin (V)")
    axes.grid(True, alpha=0.3)
    axes.legend()

    figure.tight_layout()
    figure.savefig(output_path, dpi=200)
    plt.close(figure)


def print_summary(
    *,
    results: list[ThresholdResult],
    summaries: list[ThresholdSummary],
    detail_csv: Path,
    summary_csv: Path,
    success_figure: Path,
    margin_figure: Path,
) -> None:
    total = len(results)
    passed = sum(item.passed for item in results)
    failed = total - passed

    fully_passing_thresholds = [
        item.threshold_voltage
        for item in summaries
        if item.failed == 0
    ]

    print("CPC deterministic threshold sweep")
    print()
    print(f"Threshold points:      {len(summaries)}")
    print(f"Boundary simulations:  {total}")
    print(f"Passed:                {passed}")
    print(f"Failed:                {failed}")
    print(f"Overall success rate:  {passed / total:.6%}")
    print()

    if fully_passing_thresholds:
        print(
            "Fully passing interval: "
            f"{min(fully_passing_thresholds):.6f} V "
            f"to {max(fully_passing_thresholds):.6f} V"
        )
    else:
        print("Fully passing interval: none")

    print(
        "Global minimum margin: "
        f"{min(item.signed_margin for item in results):.6f} V"
    )
    print(
        "Global average margin: "
        f"{mean(item.signed_margin for item in results):.6f} V"
    )
    print(
        "Global maximum margin: "
        f"{max(item.signed_margin for item in results):.6f} V"
    )
    print()
    print(f"Detailed CSV:          {detail_csv}")
    print(f"Summary CSV:           {summary_csv}")
    print(f"Success-rate figure:   {success_figure}")
    print(f"Margin figure:         {margin_figure}")
    print()

    if failed:
        print("Threshold sweep: PARTIAL PASS")
        print(
            "At least one tested threshold produced a decoding failure. "
            "Inspect the summary CSV to determine the valid operating interval."
        )
    else:
        print("Threshold sweep: PASS")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a deterministic decoder-threshold sweep for the "
            "CPC XOR boundary-response SPICE baseline."
        )
    )

    parser.add_argument(
        "--start",
        type=float,
        default=0.5,
        help="Initial decoder threshold in volts.",
    )
    parser.add_argument(
        "--stop",
        type=float,
        default=4.5,
        help="Final decoder threshold in volts.",
    )
    parser.add_argument(
        "--step",
        type=float,
        default=0.1,
        help="Threshold increment in volts.",
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
        "--detail-output",
        type=Path,
        default=Path("results/threshold_sweep.csv"),
        help="Detailed CSV output path.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("results/threshold_sweep_summary.csv"),
        help="Threshold summary CSV output path.",
    )
    parser.add_argument(
        "--success-figure",
        type=Path,
        default=Path("figures/threshold_success_rate.png"),
        help="Success-rate figure output path.",
    )
    parser.add_argument(
        "--margin-figure",
        type=Path,
        default=Path("figures/threshold_margin.png"),
        help="Decoder-margin figure output path.",
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    results, summaries = run_threshold_sweep(
        threshold_start=arguments.start,
        threshold_stop=arguments.stop,
        threshold_step=arguments.step,
        supply_voltage=arguments.supply,
        resistance_kohm=arguments.resistance_kohm,
        capacitance_uf=arguments.capacitance_uf,
    )

    write_detailed_csv(
        arguments.detail_output,
        results,
    )
    write_summary_csv(
        arguments.summary_output,
        summaries,
    )
    plot_success_rate(
        arguments.success_figure,
        summaries,
    )
    plot_margin(
        arguments.margin_figure,
        summaries,
    )

    print_summary(
        results=results,
        summaries=summaries,
        detail_csv=arguments.detail_output,
        summary_csv=arguments.summary_output,
        success_figure=arguments.success_figure,
        margin_figure=arguments.margin_figure,
    )


if __name__ == "__main__":
    main()
