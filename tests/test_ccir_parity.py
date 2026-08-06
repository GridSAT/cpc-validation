from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.ccir import CCIRConstraint
from src.ccir_parity import (
    CCIRParityPayload,
    PARITY_CONSTRAINT_FAMILY,
)


def test_ccir_parity_payload() -> None:
    payload = CCIRParityPayload(
        variables=(
            0,
            2,
            3,
        ),
        parity=1,
    )

    assert payload.to_dict() == {
        "variables": [
            0,
            2,
            3,
        ],
        "parity": 1,
    }


def test_payload_integrates_with_constraint() -> None:
    constraint = CCIRConstraint(
        family=PARITY_CONSTRAINT_FAMILY,
        payload=CCIRParityPayload(
            variables=(
                0,
                1,
            ),
            parity=0,
        ),
    )

    assert constraint.family == "parity"
    assert constraint.payload.to_dict() == {
        "variables": [
            0,
            1,
        ],
        "parity": 0,
    }


def test_payload_is_immutable() -> None:
    payload = CCIRParityPayload(
        variables=(0,),
        parity=1,
    )

    with pytest.raises(FrozenInstanceError):
        payload.parity = 0  # type: ignore[misc]


def test_empty_variable_sequence_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="at least one variable",
    ):
        CCIRParityPayload(
            variables=(),
            parity=0,
        )


@pytest.mark.parametrize(
    "variables",
    [
        (0, True),
        (0, 1.5),
    ],
)
def test_noninteger_variable_rejected(
    variables: tuple[object, ...],
) -> None:
    with pytest.raises(
        ValueError,
        match="must be integers",
    ):
        CCIRParityPayload(
            variables=variables,  # type: ignore[arg-type]
            parity=0,
        )


def test_negative_variable_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="non-negative",
    ):
        CCIRParityPayload(
            variables=(-1,),
            parity=0,
        )


def test_duplicate_variable_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="unique",
    ):
        CCIRParityPayload(
            variables=(
                0,
                0,
            ),
            parity=0,
        )


def test_unsorted_variables_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="sorted",
    ):
        CCIRParityPayload(
            variables=(
                2,
                0,
            ),
            parity=0,
        )


@pytest.mark.parametrize(
    "parity",
    [
        -1,
        2,
        True,
        0.5,
    ],
)
def test_invalid_parity_rejected(
    parity: object,
) -> None:
    with pytest.raises(
        ValueError,
        match="integer 0 or 1",
    ):
        CCIRParityPayload(
            variables=(0,),
            parity=parity,  # type: ignore[arg-type]
        )
