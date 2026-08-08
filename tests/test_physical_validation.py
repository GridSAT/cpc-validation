from __future__ import annotations

import pytest

from src.ccir import (
    CCIRConstraint,
    CCIRProgram,
)
from src.ccir_parity import (
    CCIRParityPayload,
    PARITY_CONSTRAINT_FAMILY,
)
from src.physical_validation import (
    PhysicalValidationResult,
    evaluate_ccir_continuation,
    validate_decoded_result,
)


def _program() -> CCIRProgram:
    return CCIRProgram(
        name="physical-validation",
        variable_count=3,
        boundary_variables=(0, 2),
        constraints=(
            CCIRConstraint(
                family=PARITY_CONSTRAINT_FAMILY,
                payload=CCIRParityPayload(
                    variables=(0, 1, 2),
                    parity=0,
                ),
            ),
        ),
    )


def test_evaluate_ccir_continuation_finds_completion() -> None:
    assert evaluate_ccir_continuation(
        _program(),
        {
            0: 0,
            2: 1,
        },
    ) == 1


def test_evaluate_ccir_continuation_handles_no_completion() -> None:
    program = CCIRProgram(
        name="no-completion",
        variable_count=2,
        boundary_variables=(0,),
        constraints=(
            CCIRConstraint(
                family=PARITY_CONSTRAINT_FAMILY,
                payload=CCIRParityPayload(
                    variables=(0,),
                    parity=0,
                ),
            ),
            CCIRConstraint(
                family=PARITY_CONSTRAINT_FAMILY,
                payload=CCIRParityPayload(
                    variables=(0,),
                    parity=1,
                ),
            ),
        ),
    )

    assert evaluate_ccir_continuation(
        program,
        {
            0: 0,
        },
    ) == 0


def test_validate_decoded_result_passes_on_agreement() -> None:
    result = validate_decoded_result(
        _program(),
        {
            0: 0,
            2: 1,
        },
        1,
    )

    assert isinstance(
        result,
        PhysicalValidationResult,
    )

    assert result.program_name == "physical-validation"
    assert result.boundary_values == (
        (0, 0),
        (2, 1),
    )
    assert result.decoded == 1
    assert result.reference == 1
    assert result.passed is True


def test_validate_decoded_result_records_failure() -> None:
    result = validate_decoded_result(
        _program(),
        {
            0: 0,
            2: 1,
        },
        0,
    )

    assert result.decoded == 0
    assert result.reference == 1
    assert result.passed is False


def test_physical_validation_requires_exact_boundary_interface() -> None:
    with pytest.raises(
        ValueError,
        match="missing boundary values",
    ):
        evaluate_ccir_continuation(
            _program(),
            {
                0: 0,
            },
        )

    with pytest.raises(
        ValueError,
        match="unexpected boundary values",
    ):
        evaluate_ccir_continuation(
            _program(),
            {
                0: 0,
                1: 0,
                2: 1,
            },
        )


def test_physical_validation_rejects_invalid_decoded_result() -> None:
    with pytest.raises(
        ValueError,
        match="decoded result must be integer 0 or 1",
    ):
        validate_decoded_result(
            _program(),
            {
                0: 0,
                2: 1,
            },
            2,
        )
