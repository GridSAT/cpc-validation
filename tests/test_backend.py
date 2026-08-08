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


def test_backend_capabilities_support_declared_family() -> None:
    from src.backend import BackendCapabilities

    capabilities = BackendCapabilities(
        constraint_families=frozenset(
            {
                "parity",
                "clause",
            }
        ),
    )

    assert capabilities.supports_constraint_family(
        "parity"
    )

    assert capabilities.supports_constraint_family(
        "clause"
    )

    assert not capabilities.supports_constraint_family(
        "unknown"
    )


def test_backend_capabilities_preserve_feature_sets() -> None:
    from src.backend import BackendCapabilities

    capabilities = BackendCapabilities(
        constraint_families=frozenset(
            {
                "parity",
            }
        ),
        interface_features=frozenset(
            {
                "boundary-control",
            }
        ),
        execution_features=frozenset(
            {
                "transient",
            }
        ),
        artifact_features=frozenset(
            {
                "provenance",
            }
        ),
    )

    assert capabilities.constraint_families == frozenset(
        {
            "parity",
        }
    )

    assert capabilities.interface_features == frozenset(
        {
            "boundary-control",
        }
    )

    assert capabilities.execution_features == frozenset(
        {
            "transient",
        }
    )

    assert capabilities.artifact_features == frozenset(
        {
            "provenance",
        }
    )


def test_unsupported_backend_capability_error_is_value_error() -> None:
    from src.backend import (
        UnsupportedBackendCapabilityError,
    )

    error = UnsupportedBackendCapabilityError(
        "unsupported constraint family"
    )

    assert isinstance(
        error,
        ValueError,
    )


def test_validate_backend_capabilities_accepts_supported_program() -> None:
    from src.backend import (
        BackendCapabilities,
        validate_backend_capabilities,
    )
    from src.ccir import (
        CCIRConstraint,
        CCIRProgram,
    )
    from src.ccir_parity import (
        CCIRParityPayload,
    )

    program = CCIRProgram(
        name="supported",
        variable_count=2,
        boundary_variables=(),
        constraints=(
            CCIRConstraint(
                family="parity",
                payload=CCIRParityPayload(
                    variables=(0, 1),
                    parity=0,
                ),
            ),
        ),
    )

    capabilities = BackendCapabilities(
        constraint_families=frozenset(
            {
                "parity",
            }
        ),
    )

    validate_backend_capabilities(
        program,
        capabilities,
    )


def test_validate_backend_capabilities_rejects_unsupported_program() -> None:
    from src.backend import (
        BackendCapabilities,
        UnsupportedBackendCapabilityError,
        validate_backend_capabilities,
    )
    from src.ccir import (
        CCIRConstraint,
        CCIRProgram,
    )
    from src.ccir_clause import (
        CCIRClausePayload,
        CCIRLiteral,
    )

    program = CCIRProgram(
        name="unsupported",
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

    capabilities = BackendCapabilities(
        constraint_families=frozenset(
            {
                "parity",
            }
        ),
    )

    with pytest.raises(
        UnsupportedBackendCapabilityError,
        match=(
            "unsupported CCIR constraint families: "
            "clause"
        ),
    ):
        validate_backend_capabilities(
            program,
            capabilities,
        )


def test_validate_backend_capabilities_reports_families_sorted() -> None:
    from src.backend import (
        BackendCapabilities,
        UnsupportedBackendCapabilityError,
        validate_backend_capabilities,
    )
    from src.ccir import (
        CCIRConstraint,
        CCIRPayload,
        CCIRProgram,
    )

    class DummyPayload(CCIRPayload):
        def to_dict(self) -> dict[str, object]:
            return {}

    program = CCIRProgram(
        name="multiple-unsupported",
        variable_count=0,
        boundary_variables=(),
        constraints=(
            CCIRConstraint(
                family="zeta",
                payload=DummyPayload(),
            ),
            CCIRConstraint(
                family="alpha",
                payload=DummyPayload(),
            ),
        ),
    )

    capabilities = BackendCapabilities(
        constraint_families=frozenset(),
    )

    with pytest.raises(
        UnsupportedBackendCapabilityError,
        match=(
            "unsupported CCIR constraint families: "
            "alpha, zeta"
        ),
    ):
        validate_backend_capabilities(
            program,
            capabilities,
        )
