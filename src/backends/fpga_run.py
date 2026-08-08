from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from src.backend import ExecutionArtifact
from src.backends.fpga_decode import decode_fpga
from src.backends.fpga_execute import execute_fpga
from src.backends.fpga_prepare import prepare_fpga_execution
from src.ccir import CCIRProgram
from src.observable_execution import ObservableExecution
from src.prepared_execution import PreparedExecution


@dataclass(frozen=True)
class FPGAExecutionResult:
    """
    End-to-end RFC-0008 FPGA execution result.

    The individual preparation, execution, and decoding stages remain
    separately available. This object records their composition only.
    """

    prepared: PreparedExecution
    observable: ObservableExecution
    decoded: int


def run_fpga_execution(
    program: CCIRProgram,
    artifact: ExecutionArtifact,
    boundary_values: Mapping[int, int],
) -> FPGAExecutionResult:
    """
    Compose FPGA preparation, execution, and fixed decoding.

    This function performs no independent semantic reference evaluation.
    """

    prepared = prepare_fpga_execution(
        program,
        artifact,
        boundary_values,
    )

    observable = execute_fpga(
        prepared
    )

    decoded = decode_fpga(
        observable,
        prepared.decoder_specification,
    )

    return FPGAExecutionResult(
        prepared=prepared,
        observable=observable,
        decoded=decoded,
    )
