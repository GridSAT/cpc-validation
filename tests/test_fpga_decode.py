from __future__ import annotations

import pytest

from src.backends.fpga_decode import (
    decode_fpga,
)
from src.observable_execution import ObservableExecution


def _observable(
    value: int,
) -> ObservableExecution:
    return ObservableExecution(
        backend_id="fpga",
        backend_version="1",
        observations=(
            (
                "result_bit",
                value,
            ),
        ),
    )


@pytest.mark.parametrize(
    (
        "value",
        "expected",
    ),
    (
        (0, 0),
        (1, 1),
    ),
)
def test_decode_fpga_returns_result_bit(
    value: int,
    expected: int,
) -> None:
    assert decode_fpga(
        _observable(value),
        (
            (
                "readout_signal",
                "result",
            ),
        ),
    ) == expected


def test_decode_fpga_requires_fpga_backend() -> None:
    observable = ObservableExecution(
        backend_id="digital",
        backend_version="1",
        observations=(
            ("result_bit", 1),
        ),
    )

    with pytest.raises(
        ValueError,
        match="requires an FPGA observable execution",
    ):
        decode_fpga(
            observable,
            (
                ("readout_signal", "result"),
            ),
        )


def test_decode_fpga_requires_fixed_readout_signal() -> None:
    with pytest.raises(
        ValueError,
        match="requires fixed readout signal",
    ):
        decode_fpga(
            _observable(1),
            (
                ("readout_signal", "other"),
            ),
        )


def test_decode_fpga_requires_result_bit() -> None:
    observable = ObservableExecution(
        backend_id="fpga",
        backend_version="1",
        observations=(),
    )

    with pytest.raises(
        ValueError,
        match="requires admitted observation",
    ):
        decode_fpga(
            observable,
            (
                ("readout_signal", "result"),
            ),
        )


@pytest.mark.parametrize(
    "value",
    (
        -1,
        2,
        True,
    ),
)
def test_decode_fpga_rejects_non_bit_observation(
    value: object,
) -> None:
    observable = ObservableExecution(
        backend_id="fpga",
        backend_version="1",
        observations=(
            (
                "result_bit",
                value,
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="must be integer 0 or 1",
    ):
        decode_fpga(
            observable,
            (
                ("readout_signal", "result"),
            ),
        )
