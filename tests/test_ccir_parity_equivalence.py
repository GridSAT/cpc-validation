from __future__ import annotations

from itertools import product
from typing import Iterable

from src.ccir_lower_parity import (
    lower_parity_instance_to_ccir,
)
from src.ccir_reference import (
    evaluate_ccir_program,
)
from src.compiler import (
    ParityConstraint,
    ParityInstance,
)
from src.generic_reference import (
    constraint_is_satisfied,
)


def all_assignments(
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


def source_is_satisfied(
    instance: ParityInstance,
    assignment: dict[int, int],
) -> bool:
    return all(
        constraint_is_satisfied(
            constraint,
            assignment,
        )
        for constraint in instance.constraints
    )


def assert_lowering_equivalent(
    instance: ParityInstance,
) -> None:
    program = lower_parity_instance_to_ccir(
        instance
    )

    for assignment in all_assignments(
        program.variable_count
    ):
        expected = source_is_satisfied(
            instance,
            assignment,
        )

        actual = evaluate_ccir_program(
            program,
            assignment,
        )

        assert actual == expected, (
            f"semantic mismatch for assignment "
            f"{assignment}: expected {expected}, "
            f"received {actual}"
        )


def test_one_variable_parity_equivalence() -> None:
    assert_lowering_equivalent(
        ParityInstance(
            constraints=(
                ParityConstraint(
                    variables=(0,),
                    parity=1,
                ),
            ),
            boundary_variables=(),
        )
    )


def test_two_variable_parity_equivalence() -> None:
    assert_lowering_equivalent(
        ParityInstance(
            constraints=(
                ParityConstraint(
                    variables=(0, 1),
                    parity=0,
                ),
            ),
            boundary_variables=(0,),
        )
    )


def test_three_variable_parity_equivalence() -> None:
    assert_lowering_equivalent(
        ParityInstance(
            constraints=(
                ParityConstraint(
                    variables=(0, 1, 2),
                    parity=1,
                ),
            ),
            boundary_variables=(
                0,
                2,
            ),
        )
    )


def test_multiple_constraint_equivalence() -> None:
    assert_lowering_equivalent(
        ParityInstance(
            constraints=(
                ParityConstraint(
                    variables=(0, 1, 2),
                    parity=0,
                ),
                ParityConstraint(
                    variables=(1, 2, 3),
                    parity=1,
                ),
            ),
            boundary_variables=(
                0,
                3,
            ),
        )
    )


def test_lowering_preserves_boundary_variables() -> None:
    instance = ParityInstance(
        constraints=(
            ParityConstraint(
                variables=(0, 1, 2, 3),
                parity=1,
            ),
        ),
        boundary_variables=(
            0,
            3,
        ),
    )

    program = lower_parity_instance_to_ccir(
        instance
    )

    assert program.boundary_variables == (
        0,
        3,
    )
    assert program.internal_variables == (
        1,
        2,
    )
