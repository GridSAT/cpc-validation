from __future__ import annotations

import pytest

from src.backends.digital_ccir import (
    DIGITAL_SPECIFICATION,
    DigitalBackend,
)
from src.backends.digital_run import (
    DigitalExecutionResult,
    run_digital_execution,
)
from src.ccir import (
    CCIRConstraint,
    CCIRProgram,
)
from src.ccir_parity import (
    CCIRParityPayload,
    PARITY_CONSTRAINT_FAMILY,
)


def _program() -> CCIRProgram:
    return CCIRProgram(
        name="digital-run",
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
def test_run_digital_execution_end_to_end(
    x0: int,
    x3: int,
    expected: int,
) -> None:
    program = _program()

    artifact = DigitalBackend().compile(
        program
    )

    result = run_digital_execution(
        program,
        artifact,
        {
            0: x0,
            3: x3,
        },
        DIGITAL_SPECIFICATION,
    )

    assert isinstance(
        result,
        DigitalExecutionResult,
    )

    assert result.prepared.backend_id == "digital"
    assert result.observable.backend_id == "digital"
    assert result.decoded == expected


def test_run_digital_execution_preserves_provenance() -> None:
    program = _program()

    artifact = DigitalBackend().compile(
        program
    )

    result = run_digital_execution(
        program,
        artifact,
        {
            0: 0,
            3: 1,
        },
        DIGITAL_SPECIFICATION,
    )

    assert result.prepared.provenance == artifact.provenance
    assert result.observable.provenance == artifact.provenance
