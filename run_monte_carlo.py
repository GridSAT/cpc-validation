from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median

from src.spice_model import simulate_response


BOUNDARY_CONDITIONS = (
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
)


@dataclass(frozen=True)
class MonteCarloTrial:
    trial: int
    x0: int
    x3: int
    expected: int
    decoded: int
    passed: bool
    output_voltage: float
    supply_voltage: float
    resistance_kohm: float
    capacitance_uf: float
    threshold_voltage: float


def varied_value(
    nominal: float,
    relative_tolerance: float,
    rng: random.Random,
) -> float:
    lower = nominal * (1.0 - relative_tolerance)
    upper = nominal * (1.0 + relative_tolerance)
    return rng.uniform(lower, upper)


def run_trials(
    *,
    samples: int,
    seed: int,
    output_path: Path,
    supply_nominal: float = 5.0,
    resistance_nominal_kohm: float = 10.0,
    capacitance_nominal_uf: float = 1.0,
    threshold_nominal: float = 2.5,
    supply_tolerance: float = 0.05,
    resistance_tolerance: float = 0.05,
    capacitance_tolerance: float = 0.10,
    threshold_tolerance: float = 0.05,
) -> list[MonteCarloTrial]:
    if samples < 1:
        raise ValueError("samples must be at least 1")

    rng = random.Random(seed)
    trials: list[MonteCarloTrial] = []

    for trial_number in range(1, samples + 1):
        supply_voltage = varied_value(
            supply_nominal,
            supply_tolerance,
            rng,
        )
        resistance_kohm = varied_value(
            resistance_nominal_kohm,
            resistance_tolerance,
            rng,
        )
        capacitance_uf = varied_value(
            capacitance_nominal_uf,
            capacitance_tolerance,
            rng,
        )
        threshold_voltage = varied_value(
            threshold_nominal,
            threshold_tolerance,
            rng,
        )

        for x0, x3 in BOUNDARY_CONDITIONS:
            response = simulate_response(
                x0=x0,
                x3=x3,
                supply_voltage=supply_voltage,
                resistance_kohm=resistance_kohm,
                capacitance_uf=capacitance_uf,
                threshold_voltage=threshold_voltage,
            )

            trials.append(
                MonteCarloTrial(
                    trial=trial_number,
                    x0=x0,
                    x3=x3,
                    expected=response.expected,
                    decoded=response.decoded,
                    passed=response.decoded == response.expected,
                    output_voltage=response.output_voltage,
                    supply_voltage=supply_voltage,
                    resistance_kohm=resistance_kohm,
                    capacitance_uf=capacitance_uf,
                    threshold_voltage=threshold_voltage,
                )
            )

    write_csv(output_path, trials)
    return trials


def write_csv(
    output_path: Path,
    trials: list[MonteCarloTrial],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            (
                "trial",
                "x0",
                "x3",
                "expected",
                "decoded",
                "passed",
                "output_voltage",
                "supply_voltage",
                "resistance_kohm",
                "capacitance_uf",
                "threshold_voltage",
            )
        )

        for item in trials:
            writer.writerow(
                (
                    item.trial,
                    item.x0,
                    item.x3,
                    item.expected,
                    item.decoded,
                    int(item.passed),
                    f"{item.output_voltage:.12f}",
                    f"{item.supply_voltage:.12f}",
                    f"{item.resistance_kohm:.12f}",
                    f"{item.capacitance_uf:.12f}",
                    f"{item.threshold_voltage:.12f}",
                )
            )


def print_summary(
    trials: list[MonteCarloTrial],
    *,
    samples: int,
    seed: int,
    output_path: Path,
) -> None:
    passed = sum(item.passed for item in trials)
    total = len(trials)
    failed = total - passed
    success_rate = passed / total

    high_outputs = [
        item.output_voltage
        for item in trials
        if item.expected == 1
    ]
    low_outputs = [
        item.output_voltage
        for item in trials
        if item.expected == 0
    ]

    high_margins = [
        item.output_voltage - item.threshold_voltage
        for item in trials
        if item.expected == 1
    ]
    low_margins = [
        item.threshold_voltage - item.output_voltage
        for item in trials
        if item.expected == 0
    ]

    print("CPC Monte Carlo SPICE validation")
    print()
    print(f"Seed:                 {seed}")
    print(f"Parameter samples:    {samples}")
    print(f"Boundary simulations: {total}")
    print(f"Passed:               {passed}")
    print(f"Failed:               {failed}")
    print(f"Success rate:         {success_rate:.6%}")
    print()
    print(
        "Expected-1 voltage:  "
        f"min={min(high_outputs):.6f} V "
        f"mean={mean(high_outputs):.6f} V "
        f"median={median(high_outputs):.6f} V "
        f"max={max(high_outputs):.6f} V"
    )
    print(
        "Expected-0 voltage:  "
        f"min={min(low_outputs):.6f} V "
        f"mean={mean(low_outputs):.6f} V "
        f"median={median(low_outputs):.6f} V "
        f"max={max(low_outputs):.6f} V"
    )
    print(
        "High-state margin:   "
        f"min={min(high_margins):.6f} V "
        f"mean={mean(high_margins):.6f} V"
    )
    print(
        "Low-state margin:    "
        f"min={min(low_margins):.6f} V "
        f"mean={mean(low_margins):.6f} V"
    )
    print()
    print(f"CSV result:           {output_path}")

    if failed:
        print()
        print("Monte Carlo validation: FAIL")

        for item in trials:
            if not item.passed:
                print(
                    "First failure: "
                    f"trial={item.trial} "
                    f"x0={item.x0} "
                    f"x3={item.x3} "
                    f"expected={item.expected} "
                    f"decoded={item.decoded} "
                    f"vout={item.output_voltage:.6f} V "
                    f"threshold={item.threshold_voltage:.6f} V"
                )
                break

        raise SystemExit(1)

    print()
    print("Monte Carlo validation: PASS")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run reproducible Monte Carlo ngspice validation for the "
            "initial CPC XOR boundary-response benchmark."
        )
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=100,
        help="Number of parameter samples; each sample evaluates four boundaries.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260805,
        help="Deterministic random seed.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/monte_carlo.csv"),
        help="CSV output path.",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    trials = run_trials(
        samples=arguments.samples,
        seed=arguments.seed,
        output_path=arguments.output,
    )

    print_summary(
        trials,
        samples=arguments.samples,
        seed=arguments.seed,
        output_path=arguments.output,
    )


if __name__ == "__main__":
    main()
