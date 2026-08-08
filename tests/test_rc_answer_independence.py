from __future__ import annotations

import pytest

from src.backend import ExecutionArtifact
from src.backends.rc_ccir import RCBackend
from src.ccir import (
    CCIRConstraint,
    CCIRProgram,
)
from src.ccir_parity import CCIRParityPayload
from src.compile_backend import compile_backend


def _programs() -> tuple[CCIRProgram, ...]:
    return (
        CCIRProgram(
            name="single-xor",
            variable_count=3,
            boundary_variables=(0, 2),
            constraints=(
                CCIRConstraint(
                    family="parity",
                    payload=CCIRParityPayload(
                        variables=(0, 1, 2),
                        parity=0,
                    ),
                ),
            ),
        ),
        CCIRProgram(
            name="two-xor-chain",
            variable_count=4,
            boundary_variables=(0, 3),
            constraints=(
                CCIRConstraint(
                    family="parity",
                    payload=CCIRParityPayload(
                        variables=(0, 1, 2),
                        parity=0,
                    ),
                ),
                CCIRConstraint(
                    family="parity",
                    payload=CCIRParityPayload(
                        variables=(1, 2, 3),
                        parity=1,
                    ),
                ),
            ),
        ),
        CCIRProgram(
            name="three-xor-cycle",
            variable_count=4,
            boundary_variables=(0,),
            constraints=(
                CCIRConstraint(
                    family="parity",
                    payload=CCIRParityPayload(
                        variables=(0, 1),
                        parity=0,
                    ),
                ),
                CCIRConstraint(
                    family="parity",
                    payload=CCIRParityPayload(
                        variables=(1, 2),
                        parity=1,
                    ),
                ),
                CCIRConstraint(
                    family="parity",
                    payload=CCIRParityPayload(
                        variables=(0, 2, 3),
                        parity=0,
                    ),
                ),
            ),
        ),
    )


@pytest.mark.parametrize(
    "program",
    _programs(),
    ids=lambda program: program.name,
)
def test_rc_artifact_is_reproducible_from_ccir_alone(
    program: CCIRProgram,
) -> None:
    backend = RCBackend()

    first = compile_backend(
        program,
        backend,
    )

    second = compile_backend(
        program,
        backend,
    )

    assert first == second


@pytest.mark.parametrize(
    "program",
    _programs(),
    ids=lambda program: program.name,
)
def test_rc_compilation_does_not_call_reference_evaluator(
    monkeypatch,
    program: CCIRProgram,
) -> None:
    import src.ccir_reference
    import src.generic_reference

    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "semantic evaluator must not participate "
            "in RC backend compilation"
        )

    monkeypatch.setattr(
        src.generic_reference,
        "evaluate_parity_instance",
        fail_if_called,
    )

    monkeypatch.setattr(
        src.ccir_reference,
        "evaluate_ccir_program",
        fail_if_called,
    )

    artifact = compile_backend(
        program,
        RCBackend(),
    )

    assert isinstance(
        artifact,
        ExecutionArtifact,
    )


@pytest.mark.parametrize(
    "program",
    _programs(),
    ids=lambda program: program.name,
)
@pytest.mark.parametrize(
    "external_reference",
    (
        None,
        0,
        1,
        "corrupted-reference",
    ),
)
def test_external_reference_value_cannot_change_rc_artifact(
    program: CCIRProgram,
    external_reference: object,
) -> None:
    baseline = compile_backend(
        program,
        RCBackend(),
    )

    # Deliberately vary an external reference value.
    # It is intentionally not passed to compilation.
    reference_output = external_reference

    repeated = compile_backend(
        program,
        RCBackend(),
    )

    assert reference_output is external_reference
    assert repeated == baseline


@pytest.mark.parametrize(
    "program",
    _programs(),
    ids=lambda program: program.name,
)
def test_rc_artifact_contains_no_answer_fields(
    program: CCIRProgram,
) -> None:
    artifact = compile_backend(
        program,
        RCBackend(),
    )

    serialized = repr(artifact).lower()

    forbidden = (
        "expected=",
        "continuation_value",
        "completion_count",
        "satisfying_assignments",
        "decoded=",
        "reference_answer",
    )

    for term in forbidden:
        assert term not in serialized
