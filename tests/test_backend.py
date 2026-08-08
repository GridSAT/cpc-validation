from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.backend import (
    ArtifactProvenance,
    Backend,
    ExecutionArtifact,
)
from src.ccir import CCIRProgram


def test_artifact_provenance_accepts_ccir_origin() -> None:
    provenance = ArtifactProvenance(
        ccir_origin="constraint:0",
    )

    assert provenance.ccir_origin == "constraint:0"
    assert provenance.backend_rule is None


def test_artifact_provenance_accepts_backend_rule() -> None:
    provenance = ArtifactProvenance(
        backend_rule="rc.fixed-node-rule",
    )

    assert provenance.ccir_origin is None
    assert provenance.backend_rule == "rc.fixed-node-rule"


def test_artifact_provenance_accepts_both_origins() -> None:
    provenance = ArtifactProvenance(
        ccir_origin="constraint:0",
        backend_rule="rc.constraint-rule",
    )

    assert provenance.ccir_origin == "constraint:0"
    assert provenance.backend_rule == "rc.constraint-rule"


def test_artifact_provenance_rejects_empty_origin() -> None:
    with pytest.raises(
        ValueError,
        match="requires a CCIR origin or backend rule",
    ):
        ArtifactProvenance()


def test_execution_artifact_preserves_contract_fields() -> None:
    provenance = ArtifactProvenance(
        backend_rule="test.rule",
    )

    artifact = ExecutionArtifact(
        topology=("node-0",),
        parameters=(("r", 1000.0),),
        interface=("out",),
        metadata=(("backend", "test"),),
        provenance=(
            ("node-0", provenance),
        ),
    )

    assert artifact.topology == ("node-0",)
    assert artifact.parameters == (("r", 1000.0),)
    assert artifact.interface == ("out",)
    assert artifact.metadata == (("backend", "test"),)
    assert artifact.provenance == (
        ("node-0", provenance),
    )


@dataclass(frozen=True)
class DummyBackend:
    def compile(
        self,
        program: CCIRProgram,
    ) -> ExecutionArtifact:
        return ExecutionArtifact(
            topology=(),
            parameters=(),
            interface=(),
            metadata=(
                ("variable_count", program.variable_count),
            ),
            provenance=(),
        )


def test_backend_protocol_compile_shape() -> None:
    backend: Backend = DummyBackend()

    program = CCIRProgram(
        name="test",
        variable_count=0,
        boundary_variables=(),
        constraints=(),
    )

    artifact = backend.compile(program)

    assert isinstance(
        artifact,
        ExecutionArtifact,
    )

    assert artifact.metadata == (
        ("variable_count", 0),
    )
