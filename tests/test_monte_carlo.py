from __future__ import annotations

import csv
import random
from pathlib import Path

import pytest

from run_monte_carlo import (
    BOUNDARY_CONDITIONS,
    MonteCarloTrial,
    run_trials,
    varied_value,
    write_csv,
)


def test_boundary_conditions_are_complete() -> None:
    assert BOUNDARY_CONDITIONS == (
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    )


def test_varied_value_is_reproducible_and_bounded() -> None:
    nominal = 10.0
    tolerance = 0.05

    first_rng = random.Random(20260805)
    second_rng = random.Random(20260805)

    first_values = [
        varied_value(nominal, tolerance, first_rng)
        for _ in range(20)
    ]
    second_values = [
        varied_value(nominal, tolerance, second_rng)
        for _ in range(20)
    ]

    assert first_values == second_values
    assert all(9.5 <= value <= 10.5 for value in first_values)


def test_write_csv_creates_machine_readable_output(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "monte_carlo.csv"

    trials = [
        MonteCarloTrial(
            trial=1,
            x0=0,
            x3=1,
            expected=1,
            decoded=1,
            passed=True,
            output_voltage=4.95,
            supply_voltage=5.00,
            resistance_kohm=10.00,
            capacitance_uf=1.00,
            threshold_voltage=2.50,
        )
    ]

    write_csv(output_path, trials)

    with output_path.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert rows[0]["trial"] == "1"
    assert rows[0]["x0"] == "0"
    assert rows[0]["x3"] == "1"
    assert rows[0]["expected"] == "1"
    assert rows[0]["decoded"] == "1"
    assert rows[0]["passed"] == "1"
    assert float(rows[0]["output_voltage"]) == pytest.approx(4.95)


def test_run_trials_executes_complete_boundary_table(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "integration.csv"

    trials = run_trials(
        samples=2,
        seed=20260805,
        output_path=output_path,
    )

    assert output_path.exists()
    assert len(trials) == 8
    assert all(trial.passed for trial in trials)

    for trial_number in (1, 2):
        trial_boundaries = {
            (trial.x0, trial.x3)
            for trial in trials
            if trial.trial == trial_number
        }

        assert trial_boundaries == set(BOUNDARY_CONDITIONS)


def test_run_trials_is_reproducible(
    tmp_path: Path,
) -> None:
    first = run_trials(
        samples=1,
        seed=20260805,
        output_path=tmp_path / "first.csv",
    )

    second = run_trials(
        samples=1,
        seed=20260805,
        output_path=tmp_path / "second.csv",
    )

    first_parameters = [
        (
            trial.x0,
            trial.x3,
            trial.supply_voltage,
            trial.resistance_kohm,
            trial.capacitance_uf,
            trial.threshold_voltage,
            trial.decoded,
        )
        for trial in first
    ]

    second_parameters = [
        (
            trial.x0,
            trial.x3,
            trial.supply_voltage,
            trial.resistance_kohm,
            trial.capacitance_uf,
            trial.threshold_voltage,
            trial.decoded,
        )
        for trial in second
    ]

    assert first_parameters == second_parameters
