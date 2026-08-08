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
from src.cross_backend_validation import (
    CrossBackendValidationResult,
    validate_cross_backend,
)


def _program() -> CCIRProgram:
    return CCIRProgram(
        name="cross-backend-validation",
        variable_count=4,
        boundary_variables=(
            0,
            3,
        ),
        constraints=(
            CCIRConstraint(
                family=PARITY_CONSTRAINT_FAMILY,
                payload=CCIRParityPayload(
                    variables=(
                        0,
                        1,
                        2,
                    ),
                    parity=0,
                ),
            ),
            CCIRConstraint(
                family=PARITY_CONSTRAINT_FAMILY,
                payload=CCIRParityPayload(
                    variables=(
                        1,
                        2,
                        3,
                    ),
                    parity=1,
                ),
            ),
        ),
    )


@pytest.mark.parametrize(
    (
        "x0",
        "x3",
        "expected",
    ),
    (
        (0, 0, 0),
        (0, 1, 1),
        (1, 0, 1),
        (1, 1, 0),
    ),
)
def test_cross_backend_validation(
    x0: int,
    x3: int,
    expected: int,
) -> None:
    result = validate_cross_backend(
        _program(),
        {
            0: x0,
            3: x3,
        },
    )

    assert isinstance(
        result,
        CrossBackendValidationResult,
    )

    assert result.rc.decoded == expected
    assert result.digital.decoded == expected
    assert result.reference_result == expected

    assert result.backend_agreement
    assert result.rc_semantic_match
    assert result.digital_semantic_match
    assert result.passed


def test_cross_backend_validation_preserves_distinct_backends() -> None:
    result = validate_cross_backend(
        _program(),
        {
            0: 0,
            3: 1,
        },
    )

    assert result.rc.prepared.backend_id == "rc"
    assert result.rc.observable.backend_id == "rc"

    assert result.digital.prepared.backend_id == "digital"
    assert result.digital.observable.backend_id == "digital"


def test_backend_agreement_is_distinct_from_semantic_correctness() -> None:
    result = CrossBackendValidationResult(
        rc=object(),
        digital=object(),
        reference_result=1,
        backend_agreement=True,
        rc_semantic_match=False,
        digital_semantic_match=False,
    )

    assert result.backend_agreement
    assert not result.passed
