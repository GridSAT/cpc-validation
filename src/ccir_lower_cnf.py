from __future__ import annotations

from src.ccir import (
    CCIRConstraint,
    CCIRProgram,
)
from src.ccir_clause import (
    CCIRClausePayload,
    CCIRLiteral,
    CLAUSE_CONSTRAINT_FAMILY,
)
from src.cnf import (
    CNFInstance,
)


def lower_cnf_instance_to_ccir(
    instance: CNFInstance,
) -> CCIRProgram:
    """
    Lower a CNF source instance into the canonical CCIR representation.

    This transformation is purely structural.

    It preserves:

      - declared variable_count;
      - clause ordering;
      - literal ordering;
      - negation flags; and
      - empty clauses.

    DIMACS variable numbering (1-based) is translated into the internal
    CCIR numbering (0-based).
    """

    constraints = []

    for clause in instance.clauses:
        payload = CCIRClausePayload(
            literals=tuple(
                CCIRLiteral(
                    variable=literal.variable - 1,
                    negated=literal.negated,
                )
                for literal in clause.literals
            )
        )

        constraints.append(
            CCIRConstraint(
                family=CLAUSE_CONSTRAINT_FAMILY,
                payload=payload,
            )
        )

    return CCIRProgram(
        name="cnf",
        variable_count=instance.variable_count,
        boundary_variables=(),
        constraints=tuple(constraints),
        metadata=(
            ("source", "cnf"),
        ),
    )
