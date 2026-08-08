from __future__ import annotations

from src.observable_execution import ObservableExecution


def decode_rc(
    observable: ObservableExecution,
    decoder_specification: tuple[
        tuple[str, object],
        ...
    ],
) -> int:
    """
    Decode an admitted RC observation using the fixed backend decoder.

    This stage performs no execution and no independent semantic
    reference evaluation.
    """

    if observable.backend_id != "rc":
        raise ValueError(
            "RC decoder requires an RC observable execution"
        )

    observations = dict(
        observable.observations
    )

    if "vout" not in observations:
        raise ValueError(
            "RC decoder requires admitted observation 'vout'"
        )

    decoder = dict(
        decoder_specification
    )

    if "threshold_voltage" not in decoder:
        raise ValueError(
            "RC decoder specification requires threshold_voltage"
        )

    output_voltage = float(
        observations["vout"]
    )

    threshold_voltage = float(
        decoder["threshold_voltage"]
    )

    return int(
        output_voltage >= threshold_voltage
    )
