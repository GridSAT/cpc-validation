from __future__ import annotations

from pathlib import Path

import pytest

from src.transient_analysis import (
    TransientSample,
    _calculate_rise_time,
    _calculate_settling_time,
    simulate_transient_response,
)


def test_high_transient_matches_nominal_rc_timing() -> None:
    response = simulate_transient_response(
        x0=0,
        x3=1,
        supply_voltage=5.0,
        resistance_kohm=10.0,
        capacitance_uf=1.0,
        threshold_voltage=2.5,
        step_time_ms=0.1,
        end_time_ms=150.0,
        settling_fraction=0.01,
    )

    assert response.expected == 1
    assert response.decoded == 1
    assert response.final_voltage == pytest.approx(5.0, abs=1e-4)
    assert response.rise_time_seconds is not None
    assert response.settling_time_seconds is not None
    assert 1000.0 * response.rise_time_seconds == pytest.approx(
        22.0,
        abs=0.2,
    )
    assert 1000.0 * response.settling_time_seconds == pytest.approx(
        46.1,
        abs=0.2,
    )


def test_low_transient_remains_low() -> None:
    response = simulate_transient_response(
        x0=0,
        x3=0,
        supply_voltage=5.0,
        resistance_kohm=10.0,
        capacitance_uf=1.0,
        threshold_voltage=2.5,
        step_time_ms=0.1,
        end_time_ms=20.0,
    )

    assert response.expected == 0
    assert response.decoded == 0
    assert response.final_voltage == pytest.approx(0.0, abs=1e-8)
    assert response.rise_time_seconds is None
    assert response.settling_time_seconds is not None


def test_calculate_rise_time_from_known_samples() -> None:
    samples = (
        TransientSample(0.0, 0.0),
        TransientSample(0.001, 0.5),
        TransientSample(0.002, 2.5),
        TransientSample(0.003, 4.5),
        TransientSample(0.004, 5.0),
    )

    rise_time = _calculate_rise_time(
        samples=samples,
        target_voltage=5.0,
        expected=1,
    )

    assert rise_time == pytest.approx(0.002)


def test_calculate_rise_time_is_none_for_low_state() -> None:
    samples = (
        TransientSample(0.0, 0.0),
        TransientSample(0.001, 0.0),
    )

    assert _calculate_rise_time(
        samples=samples,
        target_voltage=0.0,
        expected=0,
    ) is None


def test_calculate_settling_time() -> None:
    samples = (
        TransientSample(0.0, 0.0),
        TransientSample(0.001, 4.0),
        TransientSample(0.002, 4.96),
        TransientSample(0.003, 4.98),
        TransientSample(0.004, 5.0),
    )

    settling_time = _calculate_settling_time(
        samples=samples,
        target_voltage=5.0,
        tolerance_voltage=0.05,
    )

    assert settling_time == pytest.approx(0.002)


def test_settling_time_is_none_when_not_reached() -> None:
    samples = (
        TransientSample(0.0, 0.0),
        TransientSample(0.001, 3.0),
        TransientSample(0.002, 4.0),
    )

    assert _calculate_settling_time(
        samples=samples,
        target_voltage=5.0,
        tolerance_voltage=0.05,
    ) is None


@pytest.mark.parametrize(
    ("argument", "value"),
    [
        ("step_time_ms", 0.0),
        ("end_time_ms", 0.0),
        ("settling_fraction", 0.0),
        ("settling_fraction", 1.0),
        ("minimum_settling_tolerance_voltage", 0.0),
    ],
)
def test_invalid_transient_parameters_are_rejected(
    argument: str,
    value: float,
) -> None:
    arguments = {
        "x0": 0,
        "x3": 1,
        "step_time_ms": 0.1,
        "end_time_ms": 150.0,
        "settling_fraction": 0.01,
        "minimum_settling_tolerance_voltage": 0.01,
    }
    arguments[argument] = value

    with pytest.raises(ValueError):
        simulate_transient_response(**arguments)


def test_transient_paths_are_reported() -> None:
    response = simulate_transient_response(
        x0=1,
        x3=0,
        end_time_ms=20.0,
    )

    assert isinstance(response.netlist_path, Path)
    assert isinstance(response.log_path, Path)
    assert response.netlist_path.exists()
    assert response.log_path.exists()
