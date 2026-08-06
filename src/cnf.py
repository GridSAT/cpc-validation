from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Literal:
    """
    One Boolean CNF literal.

    Variable identifiers follow the DIMACS convention and therefore begin
    at one. Negation is represented independently from the variable number.
    """

    variable: int
    negated: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.variable, bool) or not isinstance(
            self.variable,
            int,
        ):
            raise ValueError(
                "literal variable must be an integer"
            )

        if self.variable <= 0:
            raise ValueError(
                "literal variable must be greater than zero"
            )

        if not isinstance(self.negated, bool):
            raise ValueError(
                "literal negated flag must be Boolean"
            )


@dataclass(frozen=True)
class Clause:
    """
    One disjunction of CNF literals.

    An empty clause is valid CNF and represents falsity.
    """

    literals: tuple[Literal, ...]

    def __post_init__(self) -> None:
        if any(
            not isinstance(literal, Literal)
            for literal in self.literals
        ):
            raise ValueError(
                "every clause member must be a Literal"
            )


@dataclass(frozen=True)
class CNFInstance:
    """
    One finite CNF source-language instance.

    This class defines source structure only. It performs no parsing,
    evaluation, lowering, compilation, or backend work.
    """

    variable_count: int
    clauses: tuple[Clause, ...]

    def __post_init__(self) -> None:
        if isinstance(self.variable_count, bool) or not isinstance(
            self.variable_count,
            int,
        ):
            raise ValueError(
                "CNF variable_count must be an integer"
            )

        if self.variable_count < 0:
            raise ValueError(
                "CNF variable_count must be non-negative"
            )

        if any(
            not isinstance(clause, Clause)
            for clause in self.clauses
        ):
            raise ValueError(
                "every CNF constraint must be a Clause"
            )

        declared_variables = (
            literal.variable
            for clause in self.clauses
            for literal in clause.literals
        )

        largest_variable = max(
            declared_variables,
            default=0,
        )

        if largest_variable > self.variable_count:
            raise ValueError(
                "literal variable exceeds declared CNF variable_count"
            )
