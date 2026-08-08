from __future__ import annotations

from src.ccir_clause import (
    CCIRClausePayload,
    CLAUSE_CONSTRAINT_FAMILY,
)
from src.ccir_lower_cnf import (
    lower_cnf_instance_to_ccir,
)
from src.cnf import (
    Clause,
    CNFInstance,
    Literal,
)


def test_empty_formula() -> None:
    program = lower_cnf_instance_to_ccir(
        CNFInstance(
            variable_count=0,
            clauses=(),
        )
    )

    assert program.variable_count == 0
    assert program.constraints == ()
    assert program.metadata_dict == {
        "source": "cnf",
    }


def test_empty_clause() -> None:
    program = lower_cnf_instance_to_ccir(
        CNFInstance(
            variable_count=0,
            clauses=(
                Clause(
                    literals=(),
                ),
            ),
        )
    )

    payload = program.constraints[0].payload

    assert isinstance(
        payload,
        CCIRClausePayload,
    )

    assert payload.literals == ()


def test_positive_literal_translation() -> None:
    program = lower_cnf_instance_to_ccir(
        CNFInstance(
            variable_count=3,
            clauses=(
                Clause(
                    literals=(
                        Literal(1),
                        Literal(3),
                    ),
                ),
            ),
        )
    )

    payload = program.constraints[0].payload

    assert payload.literals[0].variable == 0
    assert payload.literals[1].variable == 2


def test_negative_literal_translation() -> None:
    program = lower_cnf_instance_to_ccir(
        CNFInstance(
            variable_count=2,
            clauses=(
                Clause(
                    literals=(
                        Literal(
                            2,
                            negated=True,
                        ),
                    ),
                ),
            ),
        )
    )

    literal = program.constraints[0].payload.literals[0]

    assert literal.variable == 1
    assert literal.negated is True


def test_clause_order_preserved() -> None:
    program = lower_cnf_instance_to_ccir(
        CNFInstance(
            variable_count=2,
            clauses=(
                Clause(
                    literals=(Literal(1),),
                ),
                Clause(
                    literals=(Literal(2),),
                ),
            ),
        )
    )

    assert (
        program.constraints[0]
        .payload.literals[0]
        .variable
    ) == 0

    assert (
        program.constraints[1]
        .payload.literals[0]
        .variable
    ) == 1


def test_variable_count_preserved() -> None:
    program = lower_cnf_instance_to_ccir(
        CNFInstance(
            variable_count=17,
            clauses=(),
        )
    )

    assert program.variable_count == 17


def test_deterministic_lowering() -> None:
    instance = CNFInstance(
        variable_count=2,
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
        ),
    )

    assert (
        lower_cnf_instance_to_ccir(instance)
        ==
        lower_cnf_instance_to_ccir(instance)
    )


def test_constraint_family() -> None:
    program = lower_cnf_instance_to_ccir(
        CNFInstance(
            variable_count=1,
            clauses=(
                Clause(
                    literals=(Literal(1),),
                ),
            ),
        )
    )

    assert (
        program.constraints[0].family
        ==
        CLAUSE_CONSTRAINT_FAMILY
    )
