from __future__ import annotations

from src.observable_execution import ObservableExecution


def decode_digital(
    observable: ObservableExecution,
    decoder_specification: tuple[
        tuple[str, object],
        ...
    ],
) -> int:
    """
    Decode the admitted digital observation using the fixed backend decoder.

    This stage performs no execution and no independent semantic
    reference evaluation.
    """

    if observable.backend_id != "digital":
        raise ValueError(
            "digital decoder requires a digital observable execution"
        )

    observations = dict(
        observable.observations
    )

    decoder = dict(
        decoder_specification
    )

    readout_register = decoder.get(
        "readout_register"
    )

    if readout_register != "result":
        raise ValueError(
            "digital decoder requires fixed readout register 'result'"
        )

    if "result_bit" not in observations:
        raise ValueError(
            "digital decoder requires admitted observation 'result_bit'"
        )

    result = observations[
        "result_bit"
    ]

    if isinstance(
        result,
        bool,
    ) or result not in (
        0,
        1,
    ):
        raise ValueError(
            "digital result_bit must be integer 0 or 1"
        )

    return result
