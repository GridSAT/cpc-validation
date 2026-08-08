from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from src.backend import (
    BackendSpecification,
    ExecutionArtifact,
)
from src.backends.digital_decode import (
    decode_digital,
)
from src.backends.digital_execute import (
    execute_digital,
)
from src.backends.digital_prepare import (
    prepare_digital_execution,
)
from src.ccir import CCIRProgram
from src.observable_execution import ObservableExecution
from src.prepared_execution import PreparedExecution


@dataclass(frozen=True)
class DigitalExecutionResult:
    """
    End-to-end deterministic digital execution result.

    The individual preparation, execution, and decoding stages remain
    separately available. This object records their composition only.
    """

    prepared: PreparedExecution
    observable: ObservableExecution
    decoded: int


def run_digital_execution(
    program: CCIRProgram,
    artifact: ExecutionArtifact,
    boundary_values: Mapping[int, int],
    specification: BackendSpecification,
) -> DigitalExecutionResult:
    """
    Compose digital preparation, execution, and fixed decoding.

    This function performs no independent semantic reference evaluation.
    """

    prepared = prepare_digital_execution(
        program,
        artifact,
        boundary_values,
        specification,
    )

    observable = execute_digital(
        prepared
    )

    decoded = decode_digital(
        observable,
        prepared.decoder_specification,
    )

    return DigitalExecutionResult(
        prepared=prepared,
        observable=observable,
        decoded=decoded,
    )
