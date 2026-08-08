from __future__ import annotations

import pytest

from src.backends.digital_ccir import (
    DIGITAL_SPECIFICATION,
    DigitalBackend,
)
from src.backends.digital_execute import (
    DIGITAL_EXECUTION_ID,
    execute_digital,
)
from src.backends.digital_prepare import (
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
from src.observable_execution import ObservableExecution
from src.prepared_execution import PreparedExecution


def _program() -> CCIRProgram:
    return CCIRProgram(
        name="digital-execution",
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


def _prepared(
    x0: int,
    x3: int,
) -> PreparedExecution:
    program = _program()

    artifact = DigitalBackend().compile(
        program
    )

    return prepare_digital_execution(
        program,
        artifact,
        {
            0: x0,
            3: x3,
        },
        DIGITAL_SPECIFICATION,
    )


@pytest.mark.parametrize(
    (
        "x0",
        "x3",
        "expected",
    ),
    (
        (
            0,
            0,
            0,
        ),
        (
            0,
            1,
            1,
        ),
        (
            1,
            0,
            1,
        ),
        (
            1,
            1,
            0,
        ),
    ),
)
def test_execute_digital_computes_parity_continuation(
    x0: int,
    x3: int,
    expected: int,
) -> None:
    observable = execute_digital(
        _prepared(
            x0,
            x3,
        )
    )

    assert isinstance(
        observable,
        ObservableExecution,
    )

    assert observable.observations == (
        (
            "result_bit",
            expected,
        ),
    )


def test_execute_digital_preserves_backend_identity() -> None:
    prepared = _prepared(
        0,
        1,
    )

    observable = execute_digital(
        prepared
    )

    assert observable.backend_id == "digital"
    assert observable.backend_version == "1"


def test_execute_digital_preserves_provenance() -> None:
    prepared = _prepared(
        0,
        1,
    )

    observable = execute_digital(
        prepared
    )

    assert observable.provenance == prepared.provenance


def test_execute_digital_records_execution_environment() -> None:
    observable = execute_digital(
        _prepared(
            0,
            1,
        )
    )

    assert dict(
        observable.metadata
    ) == {
        "execution_engine": "python-digital-interpreter",
        "execution_engine_version": "1",
        "execution_id": DIGITAL_EXECUTION_ID,
    }


def test_execute_digital_rejects_wrong_backend() -> None:
    prepared = PreparedExecution(
        backend_id="rc",
        backend_version="1",
        payload=(),
        interface=(),
        decoder_specification=(),
    )

    with pytest.raises(
        ValueError,
        match="requires a digital prepared execution",
    ):
        execute_digital(
            prepared
        )


def test_digital_execution_module_has_no_semantic_reference_dependency() -> None:
    import ast
    from pathlib import Path

    path = Path(
        "src/backends/digital_execute.py"
    )

    tree = ast.parse(
        path.read_text(
            encoding="utf-8"
        )
    )

    forbidden_modules = {
        "src.ccir",
        "src.ccir_reference",
        "src.generic_reference",
        "src.physical_validation",
    }

    imports = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            imports.update(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            if node.module is not None:
                imports.add(
                    node.module
                )

    assert forbidden_modules.isdisjoint(
        imports
    )
