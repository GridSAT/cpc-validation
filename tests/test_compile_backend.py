from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.backend import (
    BackendCapabilities,
    ExecutionArtifact,
    UnsupportedBackendCapabilityError,
)
from src.ccir import (
    CCIRConstraint,
    CCIRProgram,
)
from src.ccir_clause import (
    CCIRClausePayload,
    CCIRLiteral,
)
from src.compile_backend import compile_backend


@dataclass(frozen=True)
class DummyBackend:
    capabilities: BackendCapabilities

    def compile(
        self,
        program: CCIRProgram,
    ) -> ExecutionArtifact:
        return ExecutionArtifact(
            topology=(
                ("program", program.name),
            ),
            parameters=(),
            interface=(
                ("boundary_variables", program.boundary_variables),
            ),
            metadata=(
                ("backend", "dummy"),
            ),
            provenance=(),
        )


def test_compile_backend_dispatches_ccir_program() -> None:
    program = CCIRProgram(
        name="empty",
        variable_count=0,
        boundary_variables=(),
        constraints=(),
    )

    backend = DummyBackend(
        capabilities=BackendCapabilities(
            constraint_families=frozenset()
        )
    )

    artifact = compile_backend(
        program,
        backend,
    )

    assert artifact.topology == (
        ("program", "empty"),
    )

    assert artifact.metadata == (
        ("backend", "dummy"),
    )


def test_compile_backend_preserves_ccir_identity() -> None:
    program = CCIRProgram(
        name="identity-test",
        variable_count=2,
        boundary_variables=(0,),
        constraints=(),
        metadata=(
            ("source", "test"),
        ),
    )

    before = program.to_dict()

    backend = DummyBackend(
        capabilities=BackendCapabilities(
            constraint_families=frozenset()
        )
    )

    compile_backend(
        program,
        backend,
    )

    assert program.to_dict() == before


def test_compile_backend_rejects_unsupported_family_before_dispatch() -> None:
    program = CCIRProgram(
        name="clause",
        variable_count=1,
        boundary_variables=(),
        constraints=(
            CCIRConstraint(
                family="clause",
                payload=CCIRClausePayload(
                    literals=(
                        CCIRLiteral(
                            variable=0,
                        ),
                    ),
                ),
            ),
        ),
    )

    @dataclass(frozen=True)
    class FailingBackend:
        capabilities: BackendCapabilities

        def compile(
            self,
            program: CCIRProgram,
        ) -> ExecutionArtifact:
            raise AssertionError(
                "backend compile must not run "
                "for unsupported CCIR"
            )

    backend = FailingBackend(
        capabilities=BackendCapabilities(
            constraint_families=frozenset(
                {
                    "parity",
                }
            )
        )
    )

    with pytest.raises(
        UnsupportedBackendCapabilityError,
        match="unsupported CCIR constraint families: clause",
    ):
        compile_backend(
            program,
            backend,
        )


def test_compile_backend_has_no_reference_evaluator_dependency(
    monkeypatch,
) -> None:
    import src.generic_reference

    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "reference evaluator must not participate "
            "in backend compilation"
        )

    monkeypatch.setattr(
        src.generic_reference,
        "evaluate_parity_instance",
        fail_if_called,
    )

    program = CCIRProgram(
        name="empty",
        variable_count=0,
        boundary_variables=(),
        constraints=(),
    )

    backend = DummyBackend(
        capabilities=BackendCapabilities(
            constraint_families=frozenset()
        )
    )

    artifact = compile_backend(
        program,
        backend,
    )

    assert artifact.metadata == (
        ("backend", "dummy"),
    )
