from __future__ import annotations

import csv
from pathlib import Path

import pytest

from run_temperature_sweep import (
    BOUNDARY_CONDITIONS,
    TemperatureResult,
    TemperatureSummary,
    decimal_range,
    relative_error,
    run_temperature_sweep,
    temperature_adjusted_value,
    theoretical_rise_time_ms,
    theoretical_settling_time_ms,
    write_detailed_csv,
    write_summary_csv,
)


def test_boundary_conditions_are_complete() -> None:
    assert BOUNDARY_CONDITIONS == (
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    )


def test_decimal_range_includes_both_endpoints() -> None:
    assert decimal_range(-40.0, -25.0, 5.0) == [
        -40.0,
        -35.0,
        -30.0,
        -25.0,
    ]


@pytest.mark.parametrize(
    ("start", "stop", "step"),
    [
        (-40.0, 125.0, 0.0),
        (-40.0, 125.0, -5.0),
        (125.0, -40.0, 5.0),
    ],
)
def test_decimal_range_rejects_invalid_inputs(
    start: float,
    stop: float,
    step: float,
) -> None:
    with pytest.raises(ValueError):
        decimal_range(start, stop, step)


def test_temperature_adjusted_resistance() -> None:
    value = temperature_adjusted_value(
        nominal_value=10.0,
        coefficient_per_c=100.0e-6,
        temperature_c=125.0,
        nominal_temperature_c=25.0,
    )

    assert value == pytest.approx(10.1)


def test_temperature_adjusted_capacitance() -> None:
    value = temperature_adjusted_value(
        nominal_value=1.0,
        coefficient_per_c=-200.0e-6,
        temperature_c=125.0,
        nominal_temperature_c=25.0,
    )

    assert value == pytest.approx(0.98)


def test_temperature_adjusted_value_must_remain_positive() -> None:
    with pytest.raises(ValueError):
        temperature_adjusted_value(
            nominal_value=1.0,
            coefficient_per_c=-1.0,
            temperature_c=27.0,
            nominal_temperature_c=25.0,
        )


def test_theoretical_timing_at_nominal_temperature() -> None:
    assert theoretical_rise_time_ms(
        10.0,
        1.0,
    ) == pytest.approx(21.97224577)

    assert theoretical_settling_time_ms(
        10.0,
        1.0,
        0.01,
    ) == pytest.approx(46.05170186)


def test_relative_error() -> None:
    assert relative_error(
        22.0,
        21.97224577,
    ) == pytest.approx(0.001263149443)

    with pytest.raises(ValueError):
        relative_error(1.0, 0.0)


def test_small_temperature_sweep() -> None:
    results, summaries = run_temperature_sweep(
        temperature_start_c=20.0,
        temperature_stop_c=30.0,
        temperature_step_c=5.0,
        nominal_temperature_c=25.0,
        nominal_resistance_kohm=10.0,
        nominal_capacitance_uf=1.0,
        resistance_coefficient_per_c=100.0e-6,
        capacitance_coefficient_per_c=-200.0e-6,
        supply_voltage=5.0,
        threshold_voltage=2.5,
        step_time_ms=0.1,
        end_time_ms=70.0,
        settling_fraction=0.01,
    )

    assert len(summaries) == 3
    assert len(results) == 12
    assert all(item.passed for item in results)
    assert all(item.failed == 0 for item in summaries)
    assert all(item.success_rate == 1.0 for item in summaries)

    nominal = summaries[1]

    assert nominal.temperature_c == pytest.approx(25.0)
    assert nominal.resistance_kohm == pytest.approx(10.0)
    assert nominal.capacitance_uf == pytest.approx(1.0)
    assert nominal.time_constant_ms == pytest.approx(10.0)
    assert nominal.mean_high_rise_time_ms == pytest.approx(
        22.0,
        abs=0.2,
    )
    assert nominal.mean_high_settling_time_ms == pytest.approx(
        46.1,
        abs=0.2,
    )


def test_write_detailed_csv(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "temperature_detail.csv"

    rows = [
        TemperatureResult(
            temperature_c=25.0,
            resistance_kohm=10.0,
            capacitance_uf=1.0,
            time_constant_ms=10.0,
            x0=0,
            x3=1,
            expected=1,
            decoded=1,
            passed=True,
            final_voltage=4.99995,
            signed_margin=2.49995,
            rise_time_ms=22.0,
            settling_time_ms=46.096,
            sample_count=811,
        )
    ]

    write_detailed_csv(output_path, rows)

    with output_path.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        data = list(csv.DictReader(handle))

    assert len(data) == 1
    assert data[0]["temperature_c"] == "25.000000000000"
    assert data[0]["resistance_kohm"] == "10.000000000000"
    assert data[0]["capacitance_uf"] == "1.000000000000"
    assert data[0]["passed"] == "1"
    assert float(data[0]["rise_time_ms"]) == pytest.approx(22.0)
    assert float(data[0]["settling_time_ms"]) == pytest.approx(46.096)


def test_write_summary_csv(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "temperature_summary.csv"

    rows = [
        TemperatureSummary(
            temperature_c=25.0,
            resistance_kohm=10.0,
            capacitance_uf=1.0,
            time_constant_ms=10.0,
            simulations=4,
            passed=4,
            failed=0,
            success_rate=1.0,
            minimum_margin=2.49995,
            average_margin=2.499975,
            maximum_margin=2.5,
            mean_high_rise_time_ms=22.0,
            mean_high_settling_time_ms=46.096,
            theoretical_rise_time_ms=21.97224577,
            theoretical_settling_time_ms=46.05170186,
            rise_time_relative_error=0.001263149443,
            settling_time_relative_error=0.000961921891,
        )
    ]

    write_summary_csv(output_path, rows)

    with output_path.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        data = list(csv.DictReader(handle))

    assert len(data) == 1
    assert data[0]["temperature_c"] == "25.000000000000"
    assert data[0]["simulations"] == "4"
    assert data[0]["passed"] == "4"
    assert data[0]["failed"] == "0"
    assert float(data[0]["success_rate"]) == pytest.approx(1.0)
    assert float(data[0]["mean_high_rise_time_ms"]) == pytest.approx(22.0)
    assert float(
        data[0]["mean_high_settling_time_ms"]
    ) == pytest.approx(46.096)
