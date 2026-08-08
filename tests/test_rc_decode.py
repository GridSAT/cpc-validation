from __future__ import annotations

import pytest

from src.backends.rc_decode import decode_rc
from src.observable_execution import ObservableExecution


def _observable(
    voltage: float,
) -> ObservableExecution:
    return ObservableExecution(
        backend_id="rc",
        backend_version="1",
        observations=(
            ("vout", voltage),
        ),
    )


def test_decode_rc_high() -> None:
    assert decode_rc(
        _observable(4.0),
        (
            ("threshold_voltage", 2.5),
        ),
    ) == 1


def test_decode_rc_low() -> None:
    assert decode_rc(
        _observable(1.0),
        (
            ("threshold_voltage", 2.5),
        ),
    ) == 0


def test_decode_rc_threshold_is_inclusive() -> None:
    assert decode_rc(
        _observable(2.5),
        (
            ("threshold_voltage", 2.5),
        ),
    ) == 1


def test_decode_rc_rejects_wrong_backend() -> None:
    observable = ObservableExecution(
        backend_id="other",
        backend_version="1",
        observations=(
            ("vout", 4.0),
        ),
    )

    with pytest.raises(
        ValueError,
        match="requires an RC observable execution",
    ):
        decode_rc(
            observable,
            (
                ("threshold_voltage", 2.5),
            ),
        )


def test_decode_rc_requires_vout() -> None:
    observable = ObservableExecution(
        backend_id="rc",
        backend_version="1",
        observations=(
            ("other", 4.0),
        ),
    )

    with pytest.raises(
        ValueError,
        match="requires admitted observation 'vout'",
    ):
        decode_rc(
            observable,
            (
                ("threshold_voltage", 2.5),
            ),
        )


def test_decode_rc_requires_threshold() -> None:
    with pytest.raises(
        ValueError,
        match="requires threshold_voltage",
    ):
        decode_rc(
            _observable(4.0),
            (),
        )
