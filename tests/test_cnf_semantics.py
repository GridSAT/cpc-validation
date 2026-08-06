from __future__ import annotations

import pytest

from src.cnf import (
    CNFInstance,
    Clause,
    Literal,
)

from src.cnf_semantics import (
    evaluate_clause,
    evaluate_cnf,
    evaluate_literal,
    validate_assignment,
)


def test_positive_literal() -> None:
    assert evaluate_literal(
        Literal(1),
        {1: 1},
    )

    assert not evaluate_literal(
        Literal(1),
        {1: 0},
    )


def test_negative_literal() -> None:
    assert evaluate_literal(
        Literal(
            1,
            negated=True,
        ),
        {1: 0},
    )

    assert not evaluate_literal(
        Literal(
            1,
            negated=True,
        ),
        {1: 1},
    )


def test_clause() -> None:
    clause = Clause(
        (
            Literal(1),
            Literal(
                2,
                negated=True,
            ),
        )
    )

    assert evaluate_clause(
        clause,
        {
            1: 0,
            2: 0,
        },
    )

    assert not evaluate_clause(
        clause,
        {
            1: 0,
            2: 1,
        },
    )


def test_empty_clause_false() -> None:
    assert not evaluate_clause(
        Clause(()),
        {},
    )


def test_cnf_true() -> None:
    instance = CNFInstance(
        variable_count=2,
        clauses=(
            Clause((Literal(1),)),
            Clause((Literal(2),)),
        ),
    )

    assert evaluate_cnf(
        instance,
        {
            1: 1,
            2: 1,
        },
    )


def test_cnf_false() -> None:
    instance = CNFInstance(
        variable_count=2,
        clauses=(
            Clause((Literal(1),)),
            Clause((Literal(2),)),
        ),
    )

    assert not evaluate_cnf(
        instance,
        {
            1: 1,
            2: 0,
        },
    )


def test_empty_formula_true() -> None:
    instance = CNFInstance(
        variable_count=0,
        clauses=(),
    )

    assert evaluate_cnf(
        instance,
        {},
    )


def test_missing_assignment() -> None:
    instance = CNFInstance(
        variable_count=2,
        clauses=(
            Clause((Literal(1),)),
        ),
    )

    with pytest.raises(ValueError):
        validate_assignment(
            instance,
            {
                1: 1,
            },
        )


def test_extra_assignment() -> None:
    instance = CNFInstance(
        variable_count=1,
        clauses=(
            Clause((Literal(1),)),
        ),
    )

    with pytest.raises(ValueError):
        validate_assignment(
            instance,
            {
                1: 1,
                2: 0,
            },
        )


def test_non_boolean_assignment() -> None:
    instance = CNFInstance(
        variable_count=1,
        clauses=(
            Clause((Literal(1),)),
        ),
    )

    with pytest.raises(ValueError):
        validate_assignment(
            instance,
            {
                1: 2,
            },
        )
