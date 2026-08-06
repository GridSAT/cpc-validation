from __future__ import annotations

import pytest

from src.ccir import (
    CCIRConstraint,
    CCIRPayload,
    CCIRProgram,
)
from src.ccir_parity import (
    CCIRParityPayload,
    PARITY_CONSTRAINT_FAMILY,
)
from src.ccir_reference import (
    evaluate_ccir_program,
)


def parity_constraint(
    variables: tuple[int, ...],
    parity: int,
) -> CCIRConstraint:
    return CCIRConstraint(
        family=PARITY_CONSTRAINT_FAMILY,
        payload=CCIRParityPayload(
            variables=variables,
            parity=parity,
        ),
    )


def test_satisfied_parity_constraint() -> None:
    program = CCIRProgram(
        name="satisfied",
        variable_count=2,
        boundary_variables=(),
        constraints=(
            parity_constraint(
                (0, 1),
                1,
            ),
        ),
    )

    assert evaluate_ccir_program(
        program,
        {
            0: 0,
            1: 1,
        },
    )


def test_unsatisfied_parity_constraint() -> None:
    program = CCIRProgram(
        name="unsatisfied",
        variable_count=2,
        boundary_variables=(),
        constraints=(
            parity_constraint(
                (0, 1),
                0,
            ),
        ),
    )

    assert not evaluate_ccir_program(
        program,
        {
            0: 0,
            1: 1,
        },
    )


def test_multiple_constraints() -> None:
    program = CCIRProgram(
        name="multiple",
        variable_count=3,
        boundary_variables=(),
        constraints=(
            parity_constraint(
                (0, 1),
                1,
            ),
            parity_constraint(
                (1, 2),
                0,
            ),
        ),
    )

    assert evaluate_ccir_program(
        program,
        {
            0: 0,
            1: 1,
            2: 1,
        },
    )


def test_one_failing_constraint_makes_program_false() -> None:
    program = CCIRProgram(
        name="failing",
        variable_count=3,
        boundary_variables=(),
        constraints=(
            parity_constraint(
                (0, 1),
                1,
            ),
            parity_constraint(
                (1, 2),
                1,
            ),
        ),
    )

    assert not evaluate_ccir_program(
        program,
        {
            0: 0,
            1: 1,
            2: 1,
        },
    )


class UnsupportedPayload(CCIRPayload):
    def to_dict(self) -> dict[str, int]:
        return {
            "value": 1,
        }


def test_unknown_family_rejected() -> None:
    program = CCIRProgram(
        name="unknown",
        variable_count=0,
        boundary_variables=(),
        constraints=(
            CCIRConstraint(
                family="unknown",
                payload=UnsupportedPayload(),
            ),
        ),
    )

    with pytest.raises(
        NotImplementedError,
        match="unsupported CCIR constraint family",
    ):
        evaluate_ccir_program(
            program,
            {},
        )


def test_missing_assignment_rejected() -> None:
    program = CCIRProgram(
        name="missing",
        variable_count=2,
        boundary_variables=(),
        constraints=(
            parity_constraint(
                (0, 1),
                0,
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="missing assignment",
    ):
        evaluate_ccir_program(
            program,
            {
                0: 0,
            },
        )


def test_invalid_assignment_value_rejected() -> None:
    program = CCIRProgram(
        name="invalid",
        variable_count=1,
        boundary_variables=(),
        constraints=(
            parity_constraint(
                (0,),
                0,
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="integer 0 or 1",
    ):
        evaluate_ccir_program(
            program,
            {
                0: 2,
            },
        )


def test_extra_assignment_variables_are_ignored() -> None:
    program = CCIRProgram(
        name="extra",
        variable_count=1,
        boundary_variables=(),
        constraints=(
            parity_constraint(
                (0,),
                1,
            ),
        ),
    )

    assert evaluate_ccir_program(
        program,
        {
            0: 1,
            9: 0,
        },
    )
