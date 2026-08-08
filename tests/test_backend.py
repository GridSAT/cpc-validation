from __future__ import annotations

from dataclasses import dataclass

import pytest

from src.backend import (
    ArtifactProvenance,
    Backend,
    BackendRuleOrigin,
    CCIROrigin,
    ExecutionArtifact,
)
from src.ccir import CCIRProgram


def test_ccir_origin_is_machine_resolvable() -> None:
    origin = CCIROrigin(
        kind="constraint",
        identifier="0",
    )

    assert origin.kind == "constraint"
    assert origin.identifier == "0"


def test_ccir_origin_rejects_empty_kind() -> None:
    with pytest.raises(
        ValueError,
        match="kind must be non-empty",
    ):
        CCIROrigin(
            kind="",
            identifier="0",
        )


def test_ccir_origin_rejects_empty_identifier() -> None:
    with pytest.raises(
        ValueError,
        match="identifier must be non-empty",
    ):
        CCIROrigin(
            kind="constraint",
            identifier="",
        )


def test_backend_rule_origin_is_machine_resolvable() -> None:
    rule = BackendRuleOrigin(
        rule_id="rc.fixed-node-rule",
    )

    assert rule.rule_id == "rc.fixed-node-rule"


def test_backend_rule_origin_rejects_empty_identifier() -> None:
    with pytest.raises(
        ValueError,
        match="identifier must be non-empty",
    ):
        BackendRuleOrigin(
            rule_id="",
        )


def test_artifact_provenance_accepts_ccir_origin() -> None:
    origin = CCIROrigin(
        kind="constraint",
        identifier="0",
    )

    provenance = ArtifactProvenance(
        ccir_origins=(origin,),
    )

    assert provenance.ccir_origins == (
        origin,
    )

    assert provenance.backend_rules == ()


def test_artifact_provenance_accepts_backend_rule() -> None:
    rule = BackendRuleOrigin(
        rule_id="rc.fixed-node-rule",
    )

    provenance = ArtifactProvenance(
        backend_rules=(rule,),
    )

    assert provenance.ccir_origins == ()

    assert provenance.backend_rules == (
        rule,
    )


def test_artifact_provenance_accepts_both_origins() -> None:
    origin = CCIROrigin(
        kind="constraint",
        identifier="0",
    )

    rule = BackendRuleOrigin(
        rule_id="rc.constraint-rule",
    )

    provenance = ArtifactProvenance(
        ccir_origins=(origin,),
        backend_rules=(rule,),
    )

    assert provenance.ccir_origins == (
        origin,
    )

    assert provenance.backend_rules == (
        rule,
    )


def test_artifact_provenance_rejects_empty_origin() -> None:
    with pytest.raises(
        ValueError,
        match="requires a CCIR origin or backend rule",
    ):
        ArtifactProvenance()


def test_execution_artifact_preserves_contract_fields() -> None:
    rule = BackendRuleOrigin(
        rule_id="test.rule",
    )

    provenance = ArtifactProvenance(
        backend_rules=(rule,),
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


def test_validate_artifact_provenance_accepts_exact_coverage() -> None:
    from src.backend import validate_artifact_provenance

    provenance = ArtifactProvenance(
        backend_rules=(
            BackendRuleOrigin(
                rule_id="test.rule",
            ),
        ),
    )

    artifact = ExecutionArtifact(
        topology=(),
        parameters=(),
        interface=(),
        metadata=(),
        provenance=(
            ("node:0", provenance),
            ("interface:out", provenance),
        ),
    )

    validate_artifact_provenance(
        artifact,
        (
            "node:0",
            "interface:out",
        ),
    )


def test_validate_artifact_provenance_rejects_missing_element() -> None:
    from src.backend import validate_artifact_provenance

    provenance = ArtifactProvenance(
        backend_rules=(
            BackendRuleOrigin(
                rule_id="test.rule",
            ),
        ),
    )

    artifact = ExecutionArtifact(
        topology=(),
        parameters=(),
        interface=(),
        metadata=(),
        provenance=(
            ("node:0", provenance),
        ),
    )

    with pytest.raises(
        ValueError,
        match="artifact provenance missing elements: interface:out",
    ):
        validate_artifact_provenance(
            artifact,
            (
                "node:0",
                "interface:out",
            ),
        )


def test_validate_artifact_provenance_rejects_unknown_element() -> None:
    from src.backend import validate_artifact_provenance

    provenance = ArtifactProvenance(
        backend_rules=(
            BackendRuleOrigin(
                rule_id="test.rule",
            ),
        ),
    )

    artifact = ExecutionArtifact(
        topology=(),
        parameters=(),
        interface=(),
        metadata=(),
        provenance=(
            ("node:0", provenance),
            ("orphan:0", provenance),
        ),
    )

    with pytest.raises(
        ValueError,
        match="artifact provenance contains unknown elements: orphan:0",
    ):
        validate_artifact_provenance(
            artifact,
            (
                "node:0",
            ),
        )


def test_validate_artifact_provenance_rejects_duplicate_provenance() -> None:
    from src.backend import validate_artifact_provenance

    provenance = ArtifactProvenance(
        backend_rules=(
            BackendRuleOrigin(
                rule_id="test.rule",
            ),
        ),
    )

    artifact = ExecutionArtifact(
        topology=(),
        parameters=(),
        interface=(),
        metadata=(),
        provenance=(
            ("node:0", provenance),
            ("node:0", provenance),
        ),
    )

    with pytest.raises(
        ValueError,
        match="duplicate element identifiers",
    ):
        validate_artifact_provenance(
            artifact,
            (
                "node:0",
            ),
        )


def test_validate_artifact_provenance_rejects_duplicate_inventory() -> None:
    from src.backend import validate_artifact_provenance

    provenance = ArtifactProvenance(
        backend_rules=(
            BackendRuleOrigin(
                rule_id="test.rule",
            ),
        ),
    )

    artifact = ExecutionArtifact(
        topology=(),
        parameters=(),
        interface=(),
        metadata=(),
        provenance=(
            ("node:0", provenance),
        ),
    )

    with pytest.raises(
        ValueError,
        match="inventory contains duplicate identifiers",
    ):
        validate_artifact_provenance(
            artifact,
            (
                "node:0",
                "node:0",
            ),
        )


def test_validate_artifact_provenance_rejects_empty_identifier() -> None:
    from src.backend import validate_artifact_provenance

    artifact = ExecutionArtifact(
        topology=(),
        parameters=(),
        interface=(),
        metadata=(),
        provenance=(),
    )

    with pytest.raises(
        ValueError,
        match="artifact element identifiers must be non-empty strings",
    ):
        validate_artifact_provenance(
            artifact,
            ("",),
        )


def test_backend_specification_represents_theta_backend() -> None:
    from src.backend import (
        BackendCapabilities,
        BackendRuleDefinition,
        BackendSpecification,
    )

    capabilities = BackendCapabilities(
        constraint_families=frozenset(
            {
                "parity",
            }
        ),
    )

    rule = BackendRuleDefinition(
        rule_id="rc.parity.constraint",
    )

    specification = BackendSpecification(
        backend_id="rc",
        backend_version="1",
        capabilities=capabilities,
        rules=(
            rule,
        ),
        fixed_parameters=(
            ("resistance_ohm", 1000.0),
            ("capacitance_f", 1e-6),
        ),
    )

    assert specification.backend_id == "rc"
    assert specification.backend_version == "1"
    assert specification.capabilities == capabilities
    assert specification.rules == (
        rule,
    )

    assert specification.has_rule(
        "rc.parity.constraint"
    )

    assert not specification.has_rule(
        "rc.unknown"
    )

    assert specification.get_fixed_parameter(
        "resistance_ohm"
    ) == 1000.0


def test_backend_rule_definition_rejects_empty_identifier() -> None:
    from src.backend import BackendRuleDefinition

    with pytest.raises(
        ValueError,
        match="backend rule identifier must be non-empty",
    ):
        BackendRuleDefinition(
            rule_id="",
        )


def test_backend_specification_rejects_empty_backend_id() -> None:
    from src.backend import (
        BackendCapabilities,
        BackendSpecification,
    )

    with pytest.raises(
        ValueError,
        match="backend identifier must be non-empty",
    ):
        BackendSpecification(
            backend_id="",
            backend_version="1",
            capabilities=BackendCapabilities(
                constraint_families=frozenset()
            ),
        )


def test_backend_specification_rejects_empty_version() -> None:
    from src.backend import (
        BackendCapabilities,
        BackendSpecification,
    )

    with pytest.raises(
        ValueError,
        match="backend version must be non-empty",
    ):
        BackendSpecification(
            backend_id="rc",
            backend_version="",
            capabilities=BackendCapabilities(
                constraint_families=frozenset()
            ),
        )


def test_backend_specification_rejects_duplicate_rules() -> None:
    from src.backend import (
        BackendCapabilities,
        BackendRuleDefinition,
        BackendSpecification,
    )

    rule = BackendRuleDefinition(
        rule_id="rc.rule",
    )

    with pytest.raises(
        ValueError,
        match="backend rule identifiers must be unique",
    ):
        BackendSpecification(
            backend_id="rc",
            backend_version="1",
            capabilities=BackendCapabilities(
                constraint_families=frozenset()
            ),
            rules=(
                rule,
                rule,
            ),
        )


def test_backend_specification_rejects_duplicate_parameters() -> None:
    from src.backend import (
        BackendCapabilities,
        BackendSpecification,
    )

    with pytest.raises(
        ValueError,
        match="backend parameter names must be unique",
    ):
        BackendSpecification(
            backend_id="rc",
            backend_version="1",
            capabilities=BackendCapabilities(
                constraint_families=frozenset()
            ),
            fixed_parameters=(
                ("r", 1000.0),
                ("r", 2000.0),
            ),
        )


def test_backend_specification_rejects_empty_parameter_name() -> None:
    from src.backend import (
        BackendCapabilities,
        BackendSpecification,
    )

    with pytest.raises(
        ValueError,
        match="backend parameter names must be non-empty strings",
    ):
        BackendSpecification(
            backend_id="rc",
            backend_version="1",
            capabilities=BackendCapabilities(
                constraint_families=frozenset()
            ),
            fixed_parameters=(
                ("", 1000.0),
            ),
        )


def test_backend_specification_missing_parameter_raises_key_error() -> None:
    from src.backend import (
        BackendCapabilities,
        BackendSpecification,
    )

    specification = BackendSpecification(
        backend_id="rc",
        backend_version="1",
        capabilities=BackendCapabilities(
            constraint_families=frozenset()
        ),
    )

    with pytest.raises(
        KeyError,
        match="missing",
    ):
        specification.get_fixed_parameter(
            "missing"
        )
