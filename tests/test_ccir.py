from __future__ import annotations

import pytest

from src.ccir import (
    CCIRConstraint,
    CCIRPayload,
    CCIRProgram,
    CCIR_SCHEMA_VERSION,
)


class ExamplePayload(CCIRPayload):
    def __init__(self, value: int) -> None:
        self.value = value

    def to_dict(self) -> dict[str, int]:
        return {
            "value": self.value,
        }


def test_ccir_constraint() -> None:
    constraint = CCIRConstraint(
        family="example",
        payload=ExamplePayload(1),
    )

    assert constraint.family == "example"
    assert constraint.payload.to_dict() == {
        "value": 1,
    }


@pytest.mark.parametrize(
    "family",
    [
        "",
        "   ",
        1,
    ],
)
def test_invalid_constraint_family_rejected(
    family: object,
) -> None:
    with pytest.raises(
        ValueError,
        match="family",
    ):
        CCIRConstraint(
            family=family,  # type: ignore[arg-type]
            payload=ExamplePayload(1),
        )


def test_ccir_program() -> None:
    program = CCIRProgram(
        name="example",
        variable_count=4,
        boundary_variables=(
            0,
            3,
        ),
        constraints=(
            CCIRConstraint(
                family="example",
                payload=ExamplePayload(1),
            ),
        ),
        metadata=(
            (
                "source",
                "test",
            ),
        ),
    )

    assert program.internal_variables == (
        1,
        2,
    )

    assert program.metadata_dict == {
        "source": "test",
    }

    assert program.to_dict() == {
        "schema_version": CCIR_SCHEMA_VERSION,
        "name": "example",
        "variable_count": 4,
        "boundary_variables": [
            0,
            3,
        ],
        "constraints": [
            {
                "family": "example",
                "payload": {
                    "value": 1,
                },
            },
        ],
        "metadata": {
            "source": "test",
        },
    }


def test_empty_ccir_program() -> None:
    program = CCIRProgram(
        name="empty",
        variable_count=0,
        boundary_variables=(),
        constraints=(),
    )

    assert program.internal_variables == ()
    assert program.constraints == ()


@pytest.mark.parametrize(
    "name",
    [
        "",
        "   ",
        1,
    ],
)
def test_invalid_program_name_rejected(
    name: object,
) -> None:
    with pytest.raises(
        ValueError,
        match="name",
    ):
        CCIRProgram(
            name=name,  # type: ignore[arg-type]
            variable_count=0,
            boundary_variables=(),
            constraints=(),
        )


@pytest.mark.parametrize(
    "variable_count",
    [
        -1,
        True,
        1.5,
    ],
)
def test_invalid_variable_count_rejected(
    variable_count: object,
) -> None:
    with pytest.raises(
        ValueError,
        match="variable_count",
    ):
        CCIRProgram(
            name="invalid",
            variable_count=variable_count,  # type: ignore[arg-type]
            boundary_variables=(),
            constraints=(),
        )


def test_duplicate_boundary_variable_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="unique",
    ):
        CCIRProgram(
            name="invalid",
            variable_count=2,
            boundary_variables=(
                0,
                0,
            ),
            constraints=(),
        )


def test_unsorted_boundary_variables_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="sorted",
    ):
        CCIRProgram(
            name="invalid",
            variable_count=3,
            boundary_variables=(
                2,
                0,
            ),
            constraints=(),
        )


def test_boundary_variable_out_of_range_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="outside declared range",
    ):
        CCIRProgram(
            name="invalid",
            variable_count=2,
            boundary_variables=(
                2,
            ),
            constraints=(),
        )


def test_nonconstraint_member_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="CCIRConstraint",
    ):
        CCIRProgram(
            name="invalid",
            variable_count=0,
            boundary_variables=(),
            constraints=(
                "constraint",  # type: ignore[arg-type]
            ),
        )


def test_duplicate_metadata_key_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="unique",
    ):
        CCIRProgram(
            name="invalid",
            variable_count=0,
            boundary_variables=(),
            constraints=(),
            metadata=(
                (
                    "source",
                    "one",
                ),
                (
                    "source",
                    "two",
                ),
            ),
        )


def test_unsorted_metadata_keys_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="sorted",
    ):
        CCIRProgram(
            name="invalid",
            variable_count=0,
            boundary_variables=(),
            constraints=(),
            metadata=(
                (
                    "z",
                    1,
                ),
                (
                    "a",
                    2,
                ),
            ),
        )


def test_untyped_constraint_payload_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="CCIRPayload",
    ):
        CCIRConstraint(
            family="invalid",
            payload={"value": 1},  # type: ignore[arg-type]
        )
