from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Mapping

from src.ccir import CCIRProgram
from src.ccir_reference import evaluate_ccir_program


@dataclass(frozen=True)
class PhysicalValidationResult:
    """
    RFC-0004 independent post-execution semantic validation result.

    This record is produced only after backend execution and decoding.
    It is not an input to compilation, preparation, execution, or decoding.
    """

    program_name: str
    boundary_values: tuple[tuple[int, int], ...]
    decoded: int
    reference: int
    passed: bool


def evaluate_ccir_continuation(
    program: CCIRProgram,
    boundary_values: Mapping[int, int],
) -> int:
    """
    Independently determine whether the CCIR program has at least one
    satisfying completion extending the admitted boundary assignment.

    This evaluator is backend-independent and inspects no ExecutionArtifact,
    PreparedExecution, ObservableExecution, netlist, or backend state.
    """

    normalized_boundary = _validate_boundary_values(
        program,
        boundary_values,
    )

    internal_variables = program.internal_variables

    for values in product(
        (0, 1),
        repeat=len(internal_variables),
    ):
        assignment = {
            **normalized_boundary,
            **dict(
                zip(
                    internal_variables,
                    values,
                    strict=True,
                )
            ),
        }

        if evaluate_ccir_program(
            program,
            assignment,
        ):
            return 1

    return 0


def validate_decoded_result(
    program: CCIRProgram,
    boundary_values: Mapping[int, int],
    decoded: int,
) -> PhysicalValidationResult:
    """
    Compare a decoded backend result with independent CCIR semantics.

    Reference evaluation occurs here, outside the backend implementation.
    """

    if isinstance(decoded, bool) or decoded not in (0, 1):
        raise ValueError(
            "decoded result must be integer 0 or 1"
        )

    normalized_boundary = _validate_boundary_values(
        program,
        boundary_values,
    )

    reference = evaluate_ccir_continuation(
        program,
        normalized_boundary,
    )

    return PhysicalValidationResult(
        program_name=program.name,
        boundary_values=tuple(
            sorted(
                normalized_boundary.items()
            )
        ),
        decoded=decoded,
        reference=reference,
        passed=(decoded == reference),
    )


def _validate_boundary_values(
    program: CCIRProgram,
    boundary_values: Mapping[int, int],
) -> dict[int, int]:
    required = set(
        program.boundary_variables
    )

    supplied = set(
        boundary_values
    )

    missing = required - supplied
    unexpected = supplied - required

    if missing:
        raise ValueError(
            "missing boundary values for: "
            + ", ".join(
                str(variable)
                for variable in sorted(missing)
            )
        )

    if unexpected:
        raise ValueError(
            "unexpected boundary values for: "
            + ", ".join(
                str(variable)
                for variable in sorted(unexpected)
            )
        )

    normalized = dict(
        boundary_values
    )

    for variable, value in normalized.items():
        if isinstance(value, bool) or value not in (0, 1):
            raise ValueError(
                f"boundary variable {variable} "
                "must be assigned integer 0 or 1"
            )

    return normalized
