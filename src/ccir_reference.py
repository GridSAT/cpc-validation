from __future__ import annotations

from typing import Mapping

from src.ccir import CCIRProgram
from src.ccir_clause import (
    CCIRClausePayload,
    CLAUSE_CONSTRAINT_FAMILY,
)
from src.ccir_parity import (
    CCIRParityPayload,
    PARITY_CONSTRAINT_FAMILY,
)


def evaluate_ccir_program(
    program: CCIRProgram,
    assignment: Mapping[int, int],
) -> bool:
    """
    Evaluate a complete Boolean assignment against a CCIR program.

    This initial reference evaluator supports only parity-family constraints.
    """

    _validate_assignment(
        program,
        assignment,
    )

    for constraint in program.constraints:
        payload = constraint.payload

        if constraint.family == PARITY_CONSTRAINT_FAMILY:
            if not isinstance(
                payload,
                CCIRParityPayload,
            ):
                raise ValueError(
                    "parity-family constraint has invalid payload type"
                )

            value = 0

            for variable in payload.variables:
                value ^= assignment[variable]

            if value != payload.parity:
                return False

            continue

        if constraint.family == CLAUSE_CONSTRAINT_FAMILY:
            if not isinstance(
                payload,
                CCIRClausePayload,
            ):
                raise ValueError(
                    "clause-family constraint has invalid payload type"
                )

            satisfied = any(
                (
                    not bool(assignment[literal.variable])
                    if literal.negated
                    else bool(assignment[literal.variable])
                )
                for literal in payload.literals
            )

            if not satisfied:
                return False

            continue

        raise NotImplementedError(
            "unsupported CCIR constraint family: "
            f"{constraint.family}"
        )

    return True


def _validate_assignment(
    program: CCIRProgram,
    assignment: Mapping[int, int],
) -> None:
    expected = set(
        range(program.variable_count)
    )
    supplied = set(assignment)

    missing = expected - supplied

    if missing:
        raise ValueError(
            "missing assignment for variables: "
            + ", ".join(
                str(variable)
                for variable in sorted(missing)
            )
        )

    for variable in expected:
        value = assignment[variable]

        if isinstance(value, bool) or value not in (0, 1):
            raise ValueError(
                f"variable {variable} must be assigned integer 0 or 1"
            )
