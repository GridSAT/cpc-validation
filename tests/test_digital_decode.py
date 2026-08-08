from __future__ import annotations

import pytest

from src.backends.digital_decode import (
    decode_digital,
)
from src.observable_execution import ObservableExecution


def _observable(
    value: int,
) -> ObservableExecution:
    return ObservableExecution(
        backend_id="digital",
        backend_version="1",
        observations=(
            (
                "result_bit",
                value,
            ),
        ),
    )


def test_decode_digital_returns_result_bit() -> None:
    assert decode_digital(
        _observable(1),
        (
            (
                "readout_register",
                "result",
            ),
        ),
    ) == 1


def test_decode_digital_preserves_zero() -> None:
    assert decode_digital(
        _observable(0),
        (
            (
                "readout_register",
                "result",
            ),
        ),
    ) == 0


def test_decode_digital_requires_digital_backend() -> None:
    observable = ObservableExecution(
        backend_id="rc",
        backend_version="1",
        observations=(
            (
                "result_bit",
                1,
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="requires a digital observable execution",
    ):
        decode_digital(
            observable,
            (
                (
                    "readout_register",
                    "result",
                ),
            ),
        )


def test_decode_digital_requires_fixed_readout_register() -> None:
    with pytest.raises(
        ValueError,
        match="requires fixed readout register",
    ):
        decode_digital(
            _observable(1),
            (
                (
                    "readout_register",
                    "other",
                ),
            ),
        )


def test_decode_digital_requires_result_bit() -> None:
    observable = ObservableExecution(
        backend_id="digital",
        backend_version="1",
        observations=(),
    )

    with pytest.raises(
        ValueError,
        match="requires admitted observation",
    ):
        decode_digital(
            observable,
            (
                (
                    "readout_register",
                    "result",
                ),
            ),
        )


def test_decode_digital_rejects_non_bit_observation() -> None:
    observable = ObservableExecution(
        backend_id="digital",
        backend_version="1",
        observations=(
            (
                "result_bit",
                2,
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="must be integer 0 or 1",
    ):
        decode_digital(
            observable,
            (
                (
                    "readout_register",
                    "result",
                ),
            ),
        )
