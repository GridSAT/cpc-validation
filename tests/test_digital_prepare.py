from __future__ import annotations

import pytest

from src.backends.digital_ccir import (
    DIGITAL_SPECIFICATION,
    DigitalBackend,
)
from src.backends.digital_prepare import (
    DIGITAL_PREPARATION_ID,
    prepare_digital_execution,
)
from src.ccir import (
    CCIRConstraint,
    CCIRProgram,
)
from src.ccir_parity import (
    CCIRParityPayload,
    PARITY_CONSTRAINT_FAMILY,
)
from src.prepared_execution import PreparedExecution


def _program() -> CCIRProgram:
    return CCIRProgram(
        name="digital-preparation",
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


def test_prepare_digital_execution_returns_prepared_state() -> None:
    program = _program()
    artifact = DigitalBackend().compile(
        program
    )

    prepared = prepare_digital_execution(
        program,
        artifact,
        {
            0: 0,
            3: 1,
        },
        DIGITAL_SPECIFICATION,
    )

    assert isinstance(
        prepared,
        PreparedExecution,
    )

    assert prepared.backend_id == "digital"
    assert prepared.backend_version == "1"
    assert prepared.interface == artifact.interface
    assert prepared.provenance == artifact.provenance


def test_digital_preparation_records_boundary_values() -> None:
    program = _program()
    artifact = DigitalBackend().compile(
        program
    )

    prepared = prepare_digital_execution(
        program,
        artifact,
        {
            0: 1,
            3: 0,
        },
        DIGITAL_SPECIFICATION,
    )

    metadata = dict(
        prepared.metadata
    )

    assert metadata[
        "boundary_values"
    ] == (
        (0, 1),
        (3, 0),
    )

    assert metadata[
        "preparation_id"
    ] == DIGITAL_PREPARATION_ID


def test_digital_preparation_preserves_instruction_program() -> None:
    program = _program()
    artifact = DigitalBackend().compile(
        program
    )

    prepared = prepare_digital_execution(
        program,
        artifact,
        {
            0: 0,
            3: 1,
        },
        DIGITAL_SPECIFICATION,
    )

    payload = dict(
        prepared.payload
    )

    assert payload[
        "program"
    ] == artifact.topology

    assert payload[
        "boundary_values"
    ] == (
        (0, 0),
        (3, 1),
    )


def test_digital_decoder_specification_is_fixed() -> None:
    program = _program()
    artifact = DigitalBackend().compile(
        program
    )

    prepared = prepare_digital_execution(
        program,
        artifact,
        {
            0: 0,
            3: 1,
        },
        DIGITAL_SPECIFICATION,
    )

    assert prepared.decoder_specification == (
        (
            "readout_register",
            "result",
        ),
    )


def test_digital_preparation_rejects_wrong_backend() -> None:
    from src.backends.rc_ccir import (
        RC_SPECIFICATION,
    )

    program = _program()
    artifact = DigitalBackend().compile(
        program
    )

    with pytest.raises(
        ValueError,
        match="execution artifact backend does not match",
    ):
        prepare_digital_execution(
            program,
            artifact,
            {
                0: 0,
                3: 1,
            },
            RC_SPECIFICATION,
        )


def test_digital_preparation_requires_exact_boundary_values() -> None:
    program = _program()
    artifact = DigitalBackend().compile(
        program
    )

    with pytest.raises(
        ValueError,
        match="missing boundary values",
    ):
        prepare_digital_execution(
            program,
            artifact,
            {
                0: 0,
            },
            DIGITAL_SPECIFICATION,
        )

    with pytest.raises(
        ValueError,
        match="unexpected boundary values",
    ):
        prepare_digital_execution(
            program,
            artifact,
            {
                0: 0,
                1: 0,
                3: 1,
            },
            DIGITAL_SPECIFICATION,
        )


def test_digital_preparation_rejects_non_bit_boundary_value() -> None:
    program = _program()
    artifact = DigitalBackend().compile(
        program
    )

    with pytest.raises(
        ValueError,
        match="must be assigned integer 0 or 1",
    ):
        prepare_digital_execution(
            program,
            artifact,
            {
                0: 2,
                3: 1,
            },
            DIGITAL_SPECIFICATION,
        )
