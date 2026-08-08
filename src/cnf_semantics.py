from __future__ import annotations

from typing import Mapping

from src.cnf import (
    CNFInstance,
    Clause,
    Literal,
)


def validate_assignment(
    instance: CNFInstance,
    assignment: Mapping[int, int],
) -> None:
    """
    Validate that an assignment is complete and Boolean.
    """

    expected = set(range(1, instance.variable_count + 1))
    supplied = set(assignment)

    missing = expected - supplied
    unexpected = supplied - expected

    if missing:
        raise ValueError(
            "missing assignment for variables: "
            + ", ".join(str(v) for v in sorted(missing))
        )

    if unexpected:
        raise ValueError(
            "unexpected assignment for variables: "
            + ", ".join(str(v) for v in sorted(unexpected))
        )

    for variable, value in assignment.items():
        if value not in (0, 1):
            raise ValueError(
                f"variable {variable} must be assigned 0 or 1"
            )


def evaluate_literal(
    literal: Literal,
    assignment: Mapping[int, int],
) -> bool:
    value = bool(assignment[literal.variable])

    if literal.negated:
        return not value

    return value


def evaluate_clause(
    clause: Clause,
    assignment: Mapping[int, int],
) -> bool:
    """
    Empty clause evaluates to False.
    """
    return any(
        evaluate_literal(
            literal,
            assignment,
        )
        for literal in clause.literals
    )


def evaluate_cnf(
    instance: CNFInstance,
    assignment: Mapping[int, int],
) -> bool:
    """
    Empty CNF evaluates to True.
    """

    return all(
        evaluate_clause(
            clause,
            assignment,
        )
        for clause in instance.clauses
    )
