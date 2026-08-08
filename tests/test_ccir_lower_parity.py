from __future__ import annotations

from src.ccir_parity import (
    CCIRParityPayload,
    PARITY_CONSTRAINT_FAMILY,
)
from src.ccir_lower_parity import (
    lower_parity_instance_to_ccir,
)
from src.compiler import (
    ParityConstraint,
    ParityInstance,
)


def test_minimal_instance() -> None:
    ccir = lower_parity_instance_to_ccir(
        ParityInstance(
            constraints=(
                ParityConstraint(
                    variables=(0,),
                    parity=0,
                ),
            ),
            boundary_variables=(),
        )
    )

    assert ccir.variable_count == 1
    assert len(ccir.constraints) == 1
    assert ccir.boundary_variables == ()
    assert ccir.metadata_dict == {
        "source": "parity",
    }


def test_single_constraint() -> None:
    ccir = lower_parity_instance_to_ccir(
        ParityInstance(
            constraints=(
                ParityConstraint(
                    variables=(0, 2),
                    parity=1,
                ),
            ),
            boundary_variables=(0,),
        )
    )

    assert len(ccir.constraints) == 1

    constraint = ccir.constraints[0]

    assert constraint.family == PARITY_CONSTRAINT_FAMILY

    payload = constraint.payload

    assert isinstance(
        payload,
        CCIRParityPayload,
    )

    assert payload.variables == (0, 2)
    assert payload.parity == 1


def test_boundary_variables_preserved() -> None:
    instance = ParityInstance(
        constraints=(
            ParityConstraint(
                variables=(0, 3),
                parity=1,
            ),
        ),
        boundary_variables=(0, 3),
    )

    ccir = lower_parity_instance_to_ccir(instance)

    assert ccir.boundary_variables == (0, 3)
    assert ccir.variable_count == 4


def test_constraint_order_preserved() -> None:
    instance = ParityInstance(
        constraints=(
            ParityConstraint(
                variables=(0,),
                parity=0,
            ),
            ParityConstraint(
                variables=(1,),
                parity=1,
            ),
        ),
        boundary_variables=(),
    )

    ccir = lower_parity_instance_to_ccir(instance)

    assert [
        c.payload.parity
        for c in ccir.constraints
    ] == [0, 1]


def test_lowering_is_deterministic() -> None:
    instance = ParityInstance(
        constraints=(
            ParityConstraint(
                variables=(0, 1),
                parity=1,
            ),
        ),
        boundary_variables=(0,),
    )

    assert (
        lower_parity_instance_to_ccir(instance)
        ==
        lower_parity_instance_to_ccir(instance)
    )


def test_lowering_canonicalizes_variable_order_within_constraint() -> None:
    instance = ParityInstance(
        constraints=(
            ParityConstraint(
                variables=(4, 5, 0),
                parity=0,
            ),
        ),
        boundary_variables=(0, 5),
    )

    ccir = lower_parity_instance_to_ccir(
        instance
    )

    payload = ccir.constraints[0].payload

    assert isinstance(
        payload,
        CCIRParityPayload,
    )

    assert payload.variables == (
        0,
        4,
        5,
    )

    assert payload.parity == 0


def test_source_variable_order_does_not_change_lowered_ccir() -> None:
    first = ParityInstance(
        constraints=(
            ParityConstraint(
                variables=(4, 5, 0),
                parity=0,
            ),
        ),
        boundary_variables=(0, 5),
    )

    second = ParityInstance(
        constraints=(
            ParityConstraint(
                variables=(0, 4, 5),
                parity=0,
            ),
        ),
        boundary_variables=(0, 5),
    )

    assert (
        lower_parity_instance_to_ccir(first)
        ==
        lower_parity_instance_to_ccir(second)
    )
