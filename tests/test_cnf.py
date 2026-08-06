from __future__ import annotations

import pytest

from src.cnf import (
    CNFInstance,
    Clause,
    Literal,
)


def test_literal() -> None:
    literal = Literal(
        variable=3,
        negated=True,
    )

    assert literal.variable == 3
    assert literal.negated is True


@pytest.mark.parametrize(
    "variable",
    [
        0,
        -1,
        True,
        1.5,
    ],
)
def test_invalid_literal_variable_rejected(
    variable: object,
) -> None:
    with pytest.raises(
        ValueError,
        match="literal variable",
    ):
        Literal(variable=variable)  # type: ignore[arg-type]


def test_invalid_negated_flag_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="negated flag",
    ):
        Literal(
            variable=1,
            negated=1,  # type: ignore[arg-type]
        )


def test_clause() -> None:
    clause = Clause(
        literals=(
            Literal(1),
            Literal(2, negated=True),
        ),
    )

    assert len(clause.literals) == 2


def test_empty_clause_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="at least one literal",
    ):
        Clause(literals=())


def test_nonliteral_clause_member_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="must be a Literal",
    ):
        Clause(
            literals=("x1",),  # type: ignore[arg-type]
        )


def test_cnf_instance() -> None:
    instance = CNFInstance(
        variable_count=3,
        clauses=(
            Clause(
                literals=(
                    Literal(1),
                    Literal(2, negated=True),
                ),
            ),
            Clause(
                literals=(
                    Literal(3),
                ),
            ),
        ),
    )

    assert instance.variable_count == 3
    assert len(instance.clauses) == 2


@pytest.mark.parametrize(
    "variable_count",
    [
        0,
        -1,
        True,
        2.5,
    ],
)
def test_invalid_variable_count_rejected(
    variable_count: object,
) -> None:
    with pytest.raises(
        ValueError,
        match="variable_count",
    ):
        CNFInstance(
            variable_count=variable_count,  # type: ignore[arg-type]
            clauses=(
                Clause(
                    literals=(
                        Literal(1),
                    ),
                ),
            ),
        )


def test_empty_cnf_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="at least one clause",
    ):
        CNFInstance(
            variable_count=1,
            clauses=(),
        )


def test_literal_beyond_declared_range_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="exceeds declared",
    ):
        CNFInstance(
            variable_count=2,
            clauses=(
                Clause(
                    literals=(
                        Literal(3),
                    ),
                ),
            ),
        )
