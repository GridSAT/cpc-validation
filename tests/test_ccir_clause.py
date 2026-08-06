from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.ccir import CCIRConstraint
from src.ccir_clause import (
    CLAUSE_CONSTRAINT_FAMILY,
    CCIRClausePayload,
    CCIRLiteral,
)


def test_literal() -> None:
    literal = CCIRLiteral(
        variable=2,
        negated=True,
    )

    assert literal.to_dict() == {
        "variable": 2,
        "negated": True,
    }


def test_clause_payload() -> None:
    payload = CCIRClausePayload(
        literals=(
            CCIRLiteral(0),
            CCIRLiteral(
                2,
                True,
            ),
        )
    )

    assert payload.to_dict() == {
        "literals": [
            {
                "variable": 0,
                "negated": False,
            },
            {
                "variable": 2,
                "negated": True,
            },
        ]
    }


def test_constraint_integration() -> None:
    constraint = CCIRConstraint(
        family=CLAUSE_CONSTRAINT_FAMILY,
        payload=CCIRClausePayload(
            literals=(
                CCIRLiteral(0),
            ),
        ),
    )

    assert constraint.family == "clause"


def test_payload_is_immutable() -> None:
    payload = CCIRClausePayload(
        literals=(
            CCIRLiteral(0),
        ),
    )

    with pytest.raises(FrozenInstanceError):
        payload.literals = ()  # type: ignore[misc]


def test_empty_clause_is_valid() -> None:
    payload = CCIRClausePayload(
        literals=(),
    )

    assert payload.literals == ()
    assert payload.to_dict() == {
        "literals": [],
    }


def test_duplicate_variable_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="unique",
    ):
        CCIRClausePayload(
            literals=(
                CCIRLiteral(0),
                CCIRLiteral(
                    0,
                    True,
                ),
            ),
        )


def test_unsorted_literals_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="sorted",
    ):
        CCIRClausePayload(
            literals=(
                CCIRLiteral(2),
                CCIRLiteral(0),
            ),
        )


def test_negative_variable_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="non-negative",
    ):
        CCIRLiteral(-1)
