from __future__ import annotations

from src.observable_execution import ObservableExecution


def decode_fpga(
    observable: ObservableExecution,
    decoder_specification: tuple[
        tuple[str, object],
        ...
    ],
) -> int:
    """
    Decode the admitted FPGA observation using the fixed backend decoder.

    This stage performs no execution and no independent semantic
    reference evaluation.
    """

    if observable.backend_id != "fpga":
        raise ValueError(
            "FPGA decoder requires an FPGA observable execution"
        )

    decoder = dict(
        decoder_specification
    )

    if decoder.get(
        "readout_signal"
    ) != "result":
        raise ValueError(
            "FPGA decoder requires fixed readout signal 'result'"
        )

    observations = dict(
        observable.observations
    )

    if "result_bit" not in observations:
        raise ValueError(
            "FPGA decoder requires admitted observation 'result_bit'"
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
            "FPGA result_bit must be integer 0 or 1"
        )

    return result
