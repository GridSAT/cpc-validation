from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.ccir import CCIRPayload


CLAUSE_CONSTRAINT_FAMILY = "clause"


@dataclass(frozen=True, order=True)
class CCIRLiteral:
    """
    Canonical CCIR literal.

    A literal represents either x_i or ¬x_i.
    """

    variable: int
    negated: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.variable, bool) or not isinstance(
            self.variable,
            int,
        ):
            raise ValueError(
                "CCIR literal variable must be an integer"
            )

        if self.variable < 0:
            raise ValueError(
                "CCIR literal variable must be non-negative"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "variable": self.variable,
            "negated": self.negated,
        }


@dataclass(frozen=True)
class CCIRClausePayload(CCIRPayload):
    """
    Typed CCIR payload representing one Boolean clause.
    """

    literals: tuple[CCIRLiteral, ...]

    def __post_init__(self) -> None:
        if not self.literals:
            raise ValueError(
                "CCIR clause must contain at least one literal"
            )

        variables = tuple(
            literal.variable
            for literal in self.literals
        )

        if len(set(variables)) != len(variables):
            raise ValueError(
                "CCIR clause variables must be unique"
            )

        if tuple(sorted(self.literals)) != self.literals:
            raise ValueError(
                "CCIR literals must be sorted"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "literals": [
                literal.to_dict()
                for literal in self.literals
            ]
        }
