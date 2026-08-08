from __future__ import annotations

from src.backend import (
    Backend,
    ExecutionArtifact,
    validate_backend_capabilities,
)
from src.ccir import CCIRProgram


def compile_backend(
    program: CCIRProgram,
    backend: Backend,
) -> ExecutionArtifact:
    """
    Canonical RFC-0003 backend-dispatch entry point.

    The dispatcher accepts only canonical CCIR as instance-specific
    compilation input.

    Backend capability rejection occurs before backend compilation.

    The dispatcher performs no source-language parsing, semantic
    evaluation, boundary-value preparation, execution, or decoding.
    """
    validate_backend_capabilities(
        program,
        backend.capabilities,
    )

    return backend.compile(
        program
    )
