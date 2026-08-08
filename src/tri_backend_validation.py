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
from src.backends.fpga_ccir import (
    FPGABackend,
)
from src.backends.fpga_run import (
    FPGAExecutionResult,
    run_fpga_execution,
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
class TriBackendValidationResult:
    """
    Post-execution comparison across RC, Digital, and FPGA backends.

    Backend execution results are retained so backend identity, execution
    metadata, admitted observations, provenance, and decoded values remain
    available to downstream validation and reporting layers.

    Independent semantic evaluation occurs only after all three backend
    execution paths have completed.
    """

    rc: RCExecutionResult
    digital: DigitalExecutionResult
    fpga: FPGAExecutionResult
    reference_result: int

    backend_agreement: bool
    rc_semantic_match: bool
    digital_semantic_match: bool
    fpga_semantic_match: bool

    @property
    def rc_decoded(self) -> int:
        return self.rc.decoded

    @property
    def digital_decoded(self) -> int:
        return self.digital.decoded

    @property
    def fpga_decoded(self) -> int:
        return self.fpga.decoded

    @property
    def reference(self) -> int:
        return self.reference_result

    @property
    def overall_pass(self) -> bool:
        return (
            self.backend_agreement
            and self.rc_semantic_match
            and self.digital_semantic_match
            and self.fpga_semantic_match
        )


def validate_tri_backend(
    program: CCIRProgram,
    boundary_values: Mapping[int, int],
) -> TriBackendValidationResult:
    """
    Compile and execute one CCIR program through the RC, deterministic
    digital, and FPGA backends, then compare all decoded results with
    independent CCIR continuation semantics.

    Reference evaluation occurs only after all three backend executions
    have completed and does not participate in any backend dependency graph.
    """

    rc_artifact = RCBackend().compile(
        program
    )

    digital_artifact = DigitalBackend().compile(
        program
    )

    fpga_artifact = FPGABackend().compile(
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

    fpga_result = run_fpga_execution(
        program,
        fpga_artifact,
        boundary_values,
    )

    reference_result = evaluate_ccir_continuation(
        program,
        boundary_values,
    )

    backend_agreement = (
        rc_result.decoded
        == digital_result.decoded
        == fpga_result.decoded
    )

    return TriBackendValidationResult(
        rc=rc_result,
        digital=digital_result,
        fpga=fpga_result,
        reference_result=reference_result,
        backend_agreement=backend_agreement,
        rc_semantic_match=(
            rc_result.decoded
            == reference_result
        ),
        digital_semantic_match=(
            digital_result.decoded
            == reference_result
        ),
        fpga_semantic_match=(
            fpga_result.decoded
            == reference_result
        ),
    )
