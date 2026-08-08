from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from src.backends.digital_ccir import (
    DIGITAL_SPECIFICATION,
    DigitalBackend,
)
from src.backends.digital_run import (
    DigitalExecutionResult,
    run_digital_execution,
)
from src.backends.rc_ccir import (
    RC_SPECIFICATION,
    RCBackend,
)
from src.backends.rc_run import (
    RCExecutionResult,
    run_rc_execution,
)
from src.ccir import CCIRProgram
from src.physical_validation import (
    evaluate_ccir_continuation,
)


@dataclass(frozen=True)
class CrossBackendValidationResult:
    """
    Independent comparison of two conforming execution backends.

    Backend agreement and semantic correctness are intentionally recorded
    separately. Agreement between backends is not treated as proof of
    correctness.
    """

    rc: RCExecutionResult
    digital: DigitalExecutionResult
    reference_result: int
    backend_agreement: bool
    rc_semantic_match: bool
    digital_semantic_match: bool

    @property
    def passed(self) -> bool:
        return (
            self.backend_agreement
            and self.rc_semantic_match
            and self.digital_semantic_match
        )


def validate_cross_backend(
    program: CCIRProgram,
    boundary_values: Mapping[int, int],
) -> CrossBackendValidationResult:
    """
    Compile and execute one CCIR program through the RC and deterministic
    digital backends, then compare both decoded results with independent
    CCIR continuation semantics.

    Reference evaluation occurs only after both backend executions have
    completed and does not participate in either backend dependency graph.
    """

    rc_artifact = RCBackend().compile(
        program
    )

    digital_artifact = DigitalBackend().compile(
        program
    )

    rc_result = run_rc_execution(
        program,
        rc_artifact,
        boundary_values,
        RC_SPECIFICATION,
    )

    digital_result = run_digital_execution(
        program,
        digital_artifact,
        boundary_values,
        DIGITAL_SPECIFICATION,
    )

    reference_result = evaluate_ccir_continuation(
        program,
        boundary_values,
    )

    return CrossBackendValidationResult(
        rc=rc_result,
        digital=digital_result,
        reference_result=reference_result,
        backend_agreement=(
            rc_result.decoded
            == digital_result.decoded
        ),
        rc_semantic_match=(
            rc_result.decoded
            == reference_result
        ),
        digital_semantic_match=(
            digital_result.decoded
            == reference_result
        ),
    )
