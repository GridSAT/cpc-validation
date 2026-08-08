from __future__ import annotations

from dataclasses import dataclass

from src.backend import (
    ArtifactProvenance,
    BackendCapabilities,
    BackendRuleDefinition,
    BackendRuleOrigin,
    BackendSpecification,
    CCIROrigin,
    ExecutionArtifact,
    validate_execution_artifact,
)
from src.ccir import CCIRProgram
from src.ccir_parity import (
    CCIRParityPayload,
    PARITY_CONSTRAINT_FAMILY,
)


DIGITAL_CAPABILITIES = BackendCapabilities(
    constraint_families=frozenset(
        {
            PARITY_CONSTRAINT_FAMILY,
        }
    ),
    interface_features=frozenset(
        {
            "boundary-control",
            "restricted-readout",
        }
    ),
    execution_features=frozenset(
        {
            "deterministic-digital",
        }
    ),
    artifact_features=frozenset(
        {
            "provenance",
            "instruction-derived-topology",
        }
    ),
)


DIGITAL_SPECIFICATION = BackendSpecification(
    backend_id="digital",
    backend_version="1",
    capabilities=DIGITAL_CAPABILITIES,
    rules=(
        BackendRuleDefinition(
            rule_id="digital.variable-register",
        ),
        BackendRuleDefinition(
            rule_id="digital.boundary-port",
        ),
        BackendRuleDefinition(
            rule_id="digital.parity-instruction",
        ),
        BackendRuleDefinition(
            rule_id="digital.existential-reduction",
        ),
        BackendRuleDefinition(
            rule_id="digital.result-register",
        ),
        BackendRuleDefinition(
            rule_id="digital.readout",
        ),
    ),
    fixed_parameters=(
        (
            "word_domain",
            "bit",
        ),
        (
            "execution_model",
            "deterministic-enumeration-v1",
        ),
    ),
)


@dataclass(frozen=True)
class DigitalBackend:
    """
    Native RFC-0003 CCIR-facing deterministic digital compiler.

    Compilation produces a digital ExecutionArtifact without consuming
    boundary assignments or semantic reference results.
    """

    specification: BackendSpecification = DIGITAL_SPECIFICATION

    @property
    def capabilities(
        self,
    ) -> BackendCapabilities:
        return self.specification.capabilities

    def compile(
        self,
        program: CCIRProgram,
    ) -> ExecutionArtifact:
        artifact, required_elements = _compile_digital_artifact(
            program,
            self.specification,
        )

        validate_execution_artifact(
            program,
            artifact,
            self.specification,
            required_elements,
        )

        return artifact


def _compile_digital_artifact(
    program: CCIRProgram,
    specification: BackendSpecification,
) -> tuple[
    ExecutionArtifact,
    tuple[str, ...],
]:
    parity_constraints: list[
        tuple[int, CCIRParityPayload]
    ] = []

    for index, constraint in enumerate(
        program.constraints
    ):
        if constraint.family != PARITY_CONSTRAINT_FAMILY:
            continue

        if not isinstance(
            constraint.payload,
            CCIRParityPayload,
        ):
            raise ValueError(
                "parity CCIR constraint requires "
                "CCIRParityPayload"
            )

        parity_constraints.append(
            (
                index,
                constraint.payload,
            )
        )

    constrained_variables = {
        variable
        for _, payload in parity_constraints
        for variable in payload.variables
    }

    topology: list[tuple[str, object]] = []
    provenance: list[
        tuple[str, ArtifactProvenance]
    ] = []

    for variable in sorted(constrained_variables):
        element_id = f"register:x{variable}"

        topology.append(
            (
                element_id,
                (
                    "variable-register",
                    variable,
                ),
            )
        )

        provenance.append(
            (
                element_id,
                ArtifactProvenance(
                    ccir_origins=(
                        CCIROrigin(
                            kind="variable",
                            identifier=str(variable),
                        ),
                    ),
                    backend_rules=(
                        BackendRuleOrigin(
                            rule_id="digital.variable-register",
                        ),
                    ),
                ),
            )
        )

    for variable in program.boundary_variables:
        element_id = f"port:x{variable}"

        topology.append(
            (
                element_id,
                (
                    "boundary-port",
                    variable,
                ),
            )
        )

        provenance.append(
            (
                element_id,
                ArtifactProvenance(
                    ccir_origins=(
                        CCIROrigin(
                            kind="boundary_variable",
                            identifier=str(variable),
                        ),
                    ),
                    backend_rules=(
                        BackendRuleOrigin(
                            rule_id="digital.boundary-port",
                        ),
                    ),
                ),
            )
        )

    for constraint_index, payload in parity_constraints:
        element_id = f"instruction:parity:{constraint_index}"

        topology.append(
            (
                element_id,
                (
                    "parity-instruction",
                    payload.variables,
                    payload.parity,
                ),
            )
        )

        provenance.append(
            (
                element_id,
                ArtifactProvenance(
                    ccir_origins=(
                        CCIROrigin(
                            kind="constraint",
                            identifier=str(
                                constraint_index
                            ),
                        ),
                    ),
                    backend_rules=(
                        BackendRuleOrigin(
                            rule_id="digital.parity-instruction",
                        ),
                    ),
                ),
            )
        )

    fixed_elements = (
        (
            "reduction:existential",
            "existential-reduction",
            "digital.existential-reduction",
        ),
        (
            "register:result",
            "result-register",
            "digital.result-register",
        ),
        (
            "readout:result",
            "readout",
            "digital.readout",
        ),
    )

    for element_id, element_type, rule_id in fixed_elements:
        topology.append(
            (
                element_id,
                (
                    element_type,
                    None,
                ),
            )
        )

        provenance.append(
            (
                element_id,
                ArtifactProvenance(
                    backend_rules=(
                        BackendRuleOrigin(
                            rule_id=rule_id,
                        ),
                    ),
                ),
            )
        )

    interface = (
        (
            "boundary_variables",
            program.boundary_variables,
        ),
        (
            "readout_register",
            "result",
        ),
    )

    metadata = (
        (
            "backend_id",
            specification.backend_id,
        ),
        (
            "backend_version",
            specification.backend_version,
        ),
        (
            "constraint_count",
            len(parity_constraints),
        ),
        (
            "program_name",
            program.name,
        ),
    )

    artifact = ExecutionArtifact(
        topology=tuple(topology),
        parameters=tuple(
            specification.fixed_parameters
        ),
        interface=interface,
        metadata=metadata,
        provenance=tuple(provenance),
    )

    required_elements = tuple(
        element_id
        for element_id, _ in topology
    )

    return (
        artifact,
        required_elements,
    )
