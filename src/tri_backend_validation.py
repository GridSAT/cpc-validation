from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from src.backends.digital_ccir import (
    DIGITAL_SPECIFICATION,
    DigitalBackend,
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
from src.backends.fpga_ccir import (
    FPGA_SPECIFICATION,
    FPGABackend,
)
from src.backends.fpga_decode import (
    decode_fpga,
)
from src.backends.fpga_execute import (
    execute_fpga,
)
from src.backends.fpga_prepare import (
    prepare_fpga_execution,
)
from src.backends.rc_ccir import (
    RC_SPECIFICATION,
    RCBackend,
)
from src.backends.rc_decode import (
    decode_rc,
)
from src.backends.rc_execute import (
    execute_rc,
)
from src.backends.rc_prepare import (
    prepare_rc_execution,
)
from src.ccir import CCIRProgram
from src.physical_validation import (
    evaluate_ccir_continuation,
)


@dataclass(frozen=True)
class TriBackendValidationResult:
    """
    Post-execution comparison across RC, Digital, and FPGA backends.

    Independent semantic evaluation occurs only after all three backend
    execution and decoding paths have completed.
    """

    rc_decoded: int
    digital_decoded: int
    fpga_decoded: int
    reference: int

    backend_agreement: bool
    rc_semantic_match: bool
    digital_semantic_match: bool
    fpga_semantic_match: bool
    overall_pass: bool


def validate_tri_backend(
    program: CCIRProgram,
    boundary_values: Mapping[int, int],
) -> TriBackendValidationResult:
    """
    Compile, prepare, execute, and decode one CCIR program through the three
    current heterogeneous reference backends.

    Reference semantics are evaluated only after all backend results exist.
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

    rc_prepared = prepare_rc_execution(
        program,
        rc_artifact,
        boundary_values,
        RC_SPECIFICATION,
    )

    digital_prepared = prepare_digital_execution(
        program,
        digital_artifact,
        boundary_values,
        DIGITAL_SPECIFICATION,
    )

    fpga_prepared = prepare_fpga_execution(
        program,
        fpga_artifact,
        boundary_values,
    )

    rc_observable = execute_rc(
        rc_prepared
    )

    digital_observable = execute_digital(
        digital_prepared
    )

    fpga_observable = execute_fpga(
        fpga_prepared
    )

    rc_decoded = decode_rc(
        rc_observable,
        rc_prepared.decoder_specification,
    )

    digital_decoded = decode_digital(
        digital_observable,
        digital_prepared.decoder_specification,
    )

    fpga_decoded = decode_fpga(
        fpga_observable,
        fpga_prepared.decoder_specification,
    )

    reference = evaluate_ccir_continuation(
        program,
        boundary_values,
    )

    backend_agreement = (
        rc_decoded
        == digital_decoded
        == fpga_decoded
    )

    rc_semantic_match = (
        rc_decoded == reference
    )

    digital_semantic_match = (
        digital_decoded == reference
    )

    fpga_semantic_match = (
        fpga_decoded == reference
    )

    overall_pass = (
        backend_agreement
        and rc_semantic_match
        and digital_semantic_match
        and fpga_semantic_match
    )

    return TriBackendValidationResult(
        rc_decoded=rc_decoded,
        digital_decoded=digital_decoded,
        fpga_decoded=fpga_decoded,
        reference=reference,
        backend_agreement=backend_agreement,
        rc_semantic_match=rc_semantic_match,
        digital_semantic_match=digital_semantic_match,
        fpga_semantic_match=fpga_semantic_match,
        overall_pass=overall_pass,
    )
