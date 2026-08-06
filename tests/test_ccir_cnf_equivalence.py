from __future__ import annotations

from itertools import product
from typing import Iterable

from src.ccir_lower_cnf import (
    lower_cnf_instance_to_ccir,
)
from src.ccir_reference import (
    evaluate_ccir_program,
)
from src.cnf import (
    Clause,
    CNFInstance,
    Literal,
)
from src.cnf_semantics import (
    evaluate_cnf,
)


def all_ccir_assignments(
    variable_count: int,
) -> Iterable[dict[int, int]]:
    for values in product(
        (0, 1),
        repeat=variable_count,
    ):
        yield dict(
            zip(
                range(variable_count),
                values,
                strict=True,
            )
        )


def to_cnf_assignment(
    ccir_assignment: dict[int, int],
) -> dict[int, int]:
    return {
        variable + 1: value
        for variable, value in ccir_assignment.items()
    }


def assert_lowering_equivalent(
    instance: CNFInstance,
) -> None:
    program = lower_cnf_instance_to_ccir(
        instance
    )

    for ccir_assignment in all_ccir_assignments(
        program.variable_count
    ):
        cnf_assignment = to_cnf_assignment(
            ccir_assignment
        )

        expected = evaluate_cnf(
            instance,
            cnf_assignment,
        )

        actual = evaluate_ccir_program(
            program,
            ccir_assignment,
        )

        assert actual == expected, (
            f"semantic mismatch for CCIR assignment "
            f"{ccir_assignment}: expected {expected}, "
            f"received {actual}"
        )


def test_empty_formula_equivalence() -> None:
    assert_lowering_equivalent(
        CNFInstance(
            variable_count=0,
            clauses=(),
        )
    )


def test_empty_clause_equivalence() -> None:
    assert_lowering_equivalent(
        CNFInstance(
            variable_count=0,
            clauses=(
                Clause(
                    literals=(),
                ),
            ),
        )
    )


def test_positive_literal_equivalence() -> None:
    assert_lowering_equivalent(
        CNFInstance(
            variable_count=1,
            clauses=(
                Clause(
                    literals=(
                        Literal(1),
                    ),
                ),
            ),
        )
    )


def test_negative_literal_equivalence() -> None:
    assert_lowering_equivalent(
        CNFInstance(
            variable_count=1,
            clauses=(
                Clause(
                    literals=(
                        Literal(
                            1,
                            negated=True,
                        ),
                    ),
                ),
            ),
        )
    )


def test_multiple_clause_equivalence() -> None:
    assert_lowering_equivalent(
        CNFInstance(
            variable_count=3,
            clauses=(
                Clause(
                    literals=(
                        Literal(1),
                        Literal(
                            2,
                            negated=True,
                        ),
                    ),
                ),
                Clause(
                    literals=(
                        Literal(2),
                        Literal(3),
                    ),
                ),
            ),
        )
    )


def test_mixed_literal_equivalence() -> None:
    assert_lowering_equivalent(
        CNFInstance(
            variable_count=4,
            clauses=(
                Clause(
                    literals=(
                        Literal(1),
                        Literal(
                            2,
                            negated=True,
                        ),
                        Literal(4),
                    ),
                ),
                Clause(
                    literals=(
                        Literal(
                            1,
                            negated=True,
                        ),
                        Literal(3),
                    ),
                ),
                Clause(
                    literals=(
                        Literal(
                            4,
                            negated=True,
                        ),
                    ),
                ),
            ),
        )
    )


def test_declared_unused_variables_preserved() -> None:
    instance = CNFInstance(
        variable_count=4,
        clauses=(
            Clause(
                literals=(
                    Literal(1),
                ),
            ),
        ),
    )

    program = lower_cnf_instance_to_ccir(
        instance
    )

    assert program.variable_count == 4

    assert_lowering_equivalent(instance)
