from __future__ import annotations

import csv
from pathlib import Path

import pytest

from run_threshold_sweep import (
    BOUNDARY_CONDITIONS,
    ThresholdResult,
    ThresholdSummary,
    decimal_range,
    run_threshold_sweep,
    signed_decoding_margin,
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
    assert decimal_range(0.5, 0.8, 0.1) == [
        0.5,
        0.6,
        0.7,
        0.8,
    ]


def test_decimal_range_rejects_invalid_step() -> None:
    with pytest.raises(ValueError):
        decimal_range(0.5, 4.5, 0.0)

    with pytest.raises(ValueError):
        decimal_range(0.5, 4.5, -0.1)


def test_decimal_range_rejects_reversed_interval() -> None:
    with pytest.raises(ValueError):
        decimal_range(4.5, 0.5, 0.1)


@pytest.mark.parametrize(
    (
        "expected",
        "output_voltage",
        "threshold_voltage",
        "expected_margin",
    ),
    [
        (1, 5.0, 2.5, 2.5),
        (0, 0.0, 2.5, 2.5),
        (1, 2.0, 2.5, -0.5),
        (0, 3.0, 2.5, -0.5),
    ],
)
def test_signed_decoding_margin(
    expected: int,
    output_voltage: float,
    threshold_voltage: float,
    expected_margin: float,
) -> None:
    assert signed_decoding_margin(
        expected=expected,
        output_voltage=output_voltage,
        threshold_voltage=threshold_voltage,
    ) == pytest.approx(expected_margin)


def test_threshold_sweep_executes_complete_table() -> None:
    results, summaries = run_threshold_sweep(
        threshold_start=2.4,
        threshold_stop=2.6,
        threshold_step=0.1,
        supply_voltage=5.0,
        resistance_kohm=10.0,
        capacitance_uf=1.0,
    )

    assert len(summaries) == 3
    assert len(results) == 12
    assert all(item.passed for item in results)
    assert all(item.failed == 0 for item in summaries)
    assert all(item.success_rate == 1.0 for item in summaries)

    for threshold in (2.4, 2.5, 2.6):
        boundaries = {
            (item.x0, item.x3)
            for item in results
            if item.threshold_voltage == pytest.approx(threshold)
        }

        assert boundaries == set(BOUNDARY_CONDITIONS)


def test_threshold_sweep_is_deterministic() -> None:
    first_results, first_summaries = run_threshold_sweep(
        threshold_start=2.5,
        threshold_stop=2.5,
        threshold_step=0.1,
        supply_voltage=5.0,
        resistance_kohm=10.0,
        capacitance_uf=1.0,
    )

    second_results, second_summaries = run_threshold_sweep(
        threshold_start=2.5,
        threshold_stop=2.5,
        threshold_step=0.1,
        supply_voltage=5.0,
        resistance_kohm=10.0,
        capacitance_uf=1.0,
    )

    assert first_results == second_results
    assert first_summaries == second_summaries


def test_write_detailed_csv(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "threshold_detail.csv"

    rows = [
        ThresholdResult(
            threshold_voltage=2.5,
            x0=0,
            x3=1,
            expected=1,
            decoded=1,
            passed=True,
            output_voltage=4.99995,
            signed_margin=2.49995,
        )
    ]

    write_detailed_csv(output_path, rows)

    with output_path.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        data = list(csv.DictReader(handle))

    assert len(data) == 1
    assert data[0]["threshold_voltage"] == "2.500000000000"
    assert data[0]["x0"] == "0"
    assert data[0]["x3"] == "1"
    assert data[0]["expected"] == "1"
    assert data[0]["decoded"] == "1"
    assert data[0]["passed"] == "1"
    assert float(data[0]["output_voltage"]) == pytest.approx(4.99995)
    assert float(data[0]["signed_margin"]) == pytest.approx(2.49995)


def test_write_summary_csv(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "threshold_summary.csv"

    rows = [
        ThresholdSummary(
            threshold_voltage=2.5,
            simulations=4,
            passed=4,
            failed=0,
            success_rate=1.0,
            minimum_margin=2.49995,
            average_margin=2.499975,
            maximum_margin=2.5,
        )
    ]

    write_summary_csv(output_path, rows)

    with output_path.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        data = list(csv.DictReader(handle))

    assert len(data) == 1
    assert data[0]["threshold_voltage"] == "2.500000000000"
    assert data[0]["simulations"] == "4"
    assert data[0]["passed"] == "4"
    assert data[0]["failed"] == "0"
    assert float(data[0]["success_rate"]) == pytest.approx(1.0)
    assert float(data[0]["minimum_margin"]) == pytest.approx(2.49995)
