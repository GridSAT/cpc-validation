from __future__ import annotations

from src.ccir import (
    CCIRConstraint,
    CCIRProgram,
)
from src.ccir_parity import (
    CCIRParityPayload,
    PARITY_CONSTRAINT_FAMILY,
)
from src.compiler import (
    ParityInstance,
)


def lower_parity_instance_to_ccir(
    instance: ParityInstance,
) -> CCIRProgram:
    """
    Lower a ParityInstance into the canonical CCIR representation.

    This transformation is purely structural. It preserves the declared
    constraint sequence and boundary variables while canonicalizing variable
    order within each parity constraint. It performs no optimization, semantic
    evaluation, candidate generation, or backend-specific processing.
    """

    variable_count = 0

    for constraint in instance.constraints:
        if constraint.variables:
            variable_count = max(
                variable_count,
                max(constraint.variables) + 1,
            )

    if instance.boundary_variables:
        variable_count = max(
            variable_count,
            max(instance.boundary_variables) + 1,
        )

    constraints = tuple(
        CCIRConstraint(
            family=PARITY_CONSTRAINT_FAMILY,
            payload=CCIRParityPayload(
                variables=tuple(
                    sorted(
                        constraint.variables
                    )
                ),
                parity=constraint.parity,
            ),
        )
        for constraint in instance.constraints
    )

    return CCIRProgram(
        name="parity",
        variable_count=variable_count,
        boundary_variables=instance.boundary_variables,
        constraints=constraints,
        metadata=(
            ("source", "parity"),
        ),
    )
