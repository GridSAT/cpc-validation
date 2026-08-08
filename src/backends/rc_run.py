from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from src.backend import (
    BackendSpecification,
    ExecutionArtifact,
)
from src.backends.rc_decode import decode_rc
from src.backends.rc_execute import execute_rc
from src.backends.rc_prepare import prepare_rc_execution
from src.ccir import CCIRProgram
from src.observable_execution import ObservableExecution
from src.prepared_execution import PreparedExecution


@dataclass(frozen=True)
class RCExecutionResult:
    """
    End-to-end RFC-0004 RC execution result.

    The individual stages remain available separately; this type simply
    records their composition for callers that want one orchestration API.
    """

    prepared: PreparedExecution
    observable: ObservableExecution
    decoded: int


def run_rc_execution(
    program: CCIRProgram,
    artifact: ExecutionArtifact,
    boundary_values: Mapping[int, int],
    specification: BackendSpecification,
) -> RCExecutionResult:
    """
    Compose RFC-0004 preparation, execution, and decoding.

    This function performs no independent semantic reference evaluation.
    """

    prepared = prepare_rc_execution(
        program,
        artifact,
        boundary_values,
        specification,
    )

    observable = execute_rc(
        prepared
    )

    decoded = decode_rc(
        observable,
        prepared.decoder_specification,
    )

    return RCExecutionResult(
        prepared=prepared,
        observable=observable,
        decoded=decoded,
    )
