from __future__ import annotations

import csv
from pathlib import Path

import pytest

from run_resistance_sweep import (
    BOUNDARY_CONDITIONS,
    ResistanceResult,
    ResistanceSummary,
    decimal_range,
    relative_error,
    run_resistance_sweep,
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


def test_decimal_range_includes_endpoints() -> None:
    assert decimal_range(5.0, 8.0, 1.0) == [
        5.0,
        6.0,
        7.0,
        8.0,
    ]


def test_decimal_range_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        decimal_range(5.0, 20.0, 0.0)

    with pytest.raises(ValueError):
        decimal_range(5.0, 20.0, -1.0)

    with pytest.raises(ValueError):
        decimal_range(20.0, 5.0, 1.0)


def test_theoretical_timing_for_nominal_rc() -> None:
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
    assert relative_error(22.0, 21.97224577) == pytest.approx(
        0.001263149443,
    )

    with pytest.raises(ValueError):
        relative_error(1.0, 0.0)


def test_small_resistance_sweep_matches_rc_scaling() -> None:
    results, summaries = run_resistance_sweep(
        resistance_start_kohm=5.0,
        resistance_stop_kohm=6.0,
        resistance_step_kohm=1.0,
        supply_voltage=5.0,
        capacitance_uf=1.0,
        threshold_voltage=2.5,
        step_time_ms=0.1,
        end_time_ms=60.0,
        settling_fraction=0.01,
    )

    assert len(results) == 8
    assert len(summaries) == 2
    assert all(item.passed for item in results)
    assert all(item.failed == 0 for item in summaries)

    assert summaries[0].mean_high_rise_time_ms == pytest.approx(
        11.0,
        abs=0.2,
    )
    assert summaries[1].mean_high_rise_time_ms == pytest.approx(
        13.2,
        abs=0.2,
    )

    assert summaries[0].mean_high_settling_time_ms == pytest.approx(
        23.1,
        abs=0.2,
    )
    assert summaries[1].mean_high_settling_time_ms == pytest.approx(
        27.7,
        abs=0.2,
    )


def test_write_detailed_csv(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "resistance_detail.csv"

    rows = [
        ResistanceResult(
            resistance_kohm=10.0,
            x0=0,
            x3=1,
            expected=1,
            decoded=1,
            passed=True,
            final_voltage=4.999948,
            signed_margin=2.499948,
            rise_time_ms=22.0,
            settling_time_ms=46.096,
            sample_count=1511,
        )
    ]

    write_detailed_csv(output_path, rows)

    with output_path.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        data = list(csv.DictReader(handle))

    assert len(data) == 1
    assert data[0]["resistance_kohm"] == "10.000000000000"
    assert data[0]["passed"] == "1"
    assert float(data[0]["rise_time_ms"]) == pytest.approx(22.0)
    assert float(data[0]["settling_time_ms"]) == pytest.approx(46.096)


def test_write_summary_csv(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "resistance_summary.csv"

    rows = [
        ResistanceSummary(
            resistance_kohm=10.0,
            simulations=4,
            passed=4,
            failed=0,
            success_rate=1.0,
            minimum_margin=2.499948,
            average_margin=2.499974,
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
    assert data[0]["simulations"] == "4"
    assert data[0]["passed"] == "4"
    assert float(data[0]["mean_high_rise_time_ms"]) == pytest.approx(22.0)
    assert float(
        data[0]["mean_high_settling_time_ms"]
    ) == pytest.approx(46.096)
