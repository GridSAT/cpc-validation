from __future__ import annotations

from src.backend import ExecutionArtifact
from src.backends.rc_ccir import (
    RCBackend,
    RC_SPECIFICATION,
)
from src.backends.rc_run import (
    RCExecutionResult,
    run_rc_execution,
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


def _program() -> CCIRProgram:
    return CCIRProgram(
        name="rc-run",
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


def test_run_rc_execution_composes_rfc0004_stages(
    monkeypatch,
) -> None:
    import src.backends.rc_run as rc_run

    program = _program()

    artifact: ExecutionArtifact = RCBackend().compile(
        program
    )

    seen = {}

    def fake_execute(prepared):
        seen["prepared"] = prepared

        return ObservableExecution(
            backend_id="rc",
            backend_version="1",
            observations=(
                ("vout", 4.0),
            ),
            metadata=(
                ("execution_id", "test"),
            ),
        )

    monkeypatch.setattr(
        rc_run,
        "execute_rc",
        fake_execute,
    )

    result = run_rc_execution(
        program,
        artifact,
        {
            0: 0,
            2: 1,
        },
        RC_SPECIFICATION,
    )

    assert isinstance(
        result,
        RCExecutionResult,
    )

    assert seen["prepared"] is result.prepared
    assert result.observable.backend_id == "rc"
    assert result.decoded == 1


def test_run_rc_execution_uses_prepared_decoder_specification(
    monkeypatch,
) -> None:
    import src.backends.rc_run as rc_run

    program = _program()
    artifact = RCBackend().compile(
        program
    )

    def fake_execute(prepared):
        return ObservableExecution(
            backend_id="rc",
            backend_version="1",
            observations=(
                ("vout", 2.5),
            ),
        )

    monkeypatch.setattr(
        rc_run,
        "execute_rc",
        fake_execute,
    )

    result = run_rc_execution(
        program,
        artifact,
        {
            0: 1,
            2: 0,
        },
        RC_SPECIFICATION,
    )

    assert dict(
        result.prepared.decoder_specification
    ) == {
        "threshold_voltage": 2.5,
    }

    assert result.decoded == 1
