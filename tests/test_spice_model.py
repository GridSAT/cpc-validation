from __future__ import annotations

import pytest

from src.spice_model import (
    DECODE_THRESHOLD_V,
    expected_continuation,
    simulate_response,
)


@pytest.mark.parametrize(
    ("x0", "x3", "expected"),
    [
        (0, 0, 0),
        (0, 1, 1),
        (1, 0, 1),
        (1, 1, 0),
    ],
)
def test_spice_response_matches_continuation(
    x0: int,
    x3: int,
    expected: int,
) -> None:
    result = simulate_response(x0, x3)

    assert expected_continuation(x0, x3) == expected
    assert result.decoded_value == expected


@pytest.mark.parametrize(
    ("x0", "x3"),
    [
        (0, 0),
        (1, 1),
    ],
)
def test_equal_boundaries_produce_low_response(x0: int, x3: int) -> None:
    result = simulate_response(x0, x3)

    assert result.final_voltage < DECODE_THRESHOLD_V


@pytest.mark.parametrize(
    ("x0", "x3"),
    [
        (0, 1),
        (1, 0),
    ],
)
def test_unequal_boundaries_produce_high_response(x0: int, x3: int) -> None:
    result = simulate_response(x0, x3)

    assert result.final_voltage > DECODE_THRESHOLD_V


@pytest.mark.parametrize(
    ("x0", "x3"),
    [
        (-1, 0),
        (0, 2),
        (1, 7),
    ],
)
def test_invalid_boundary_values_are_rejected(x0: int, x3: int) -> None:
    with pytest.raises(ValueError):
        simulate_response(x0, x3)


def test_ngspice_version_reports_execution_engine(
    monkeypatch,
) -> None:
    import subprocess

    import src.spice_model as spice_model

    class Completed:
        returncode = 0
        stdout = "ngspice-42 : Circuit level simulation program\n"
        stderr = ""

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: Completed(),
    )

    assert spice_model._ngspice_version() == "ngspice-42"


def test_ngspice_version_ignores_banner_delimiters(
    monkeypatch,
) -> None:
    import src.spice_model as spice_model

    class Completed:
        stdout = """******
** ngspice-42 : Circuit level simulation program
** Compiled with KLU Direct Linear Solver
******
"""
        stderr = ""

    def fake_run(*args, **kwargs):
        return Completed()

    monkeypatch.setattr(
        spice_model.subprocess,
        "run",
        fake_run,
    )

    assert spice_model._ngspice_version() == "ngspice-42"
