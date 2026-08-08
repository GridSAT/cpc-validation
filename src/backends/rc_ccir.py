from __future__ import annotations

from dataclasses import dataclass
from itertools import product

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


RC_CAPABILITIES = BackendCapabilities(
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
            "transient",
        }
    ),
    artifact_features=frozenset(
        {
            "provenance",
            "constraint-derived-topology",
        }
    ),
)


RC_SPECIFICATION = BackendSpecification(
    backend_id="rc",
    backend_version="1",
    capabilities=RC_CAPABILITIES,
    rules=(
        BackendRuleDefinition(
            rule_id="rc.variable-node",
        ),
        BackendRuleDefinition(
            rule_id="rc.boundary-interface",
        ),
        BackendRuleDefinition(
            rule_id="rc.candidate-source",
        ),
        BackendRuleDefinition(
            rule_id="rc.existential-aggregator",
        ),
        BackendRuleDefinition(
            rule_id="rc.output-resistor",
        ),
        BackendRuleDefinition(
            rule_id="rc.output-capacitor",
        ),
        BackendRuleDefinition(
            rule_id="rc.output-leak",
        ),
        BackendRuleDefinition(
            rule_id="rc.transient-control",
        ),
        BackendRuleDefinition(
            rule_id="rc.readout",
        ),
    ),
    fixed_parameters=(
        ("supply_voltage", 5.0),
        ("resistance_kohm", 10.0),
        ("capacitance_uf", 1.0),
        ("threshold_voltage", 2.5),
        ("end_time_ms", 50.0),
    ),
)


@dataclass(frozen=True)
class RCBackend:
    """
    Native RFC-0003 CCIR-facing RC compiler.

    Compilation produces an RC execution artifact without consuming any
    boundary assignment or semantic reference result.
    """

    specification: BackendSpecification = RC_SPECIFICATION

    @property
    def capabilities(
        self,
    ) -> BackendCapabilities:
        return self.specification.capabilities

    def compile(
        self,
        program: CCIRProgram,
    ) -> ExecutionArtifact:
        artifact, required_elements = _compile_rc_artifact(
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


def _compile_rc_artifact(
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

    internal_variables = tuple(
        variable
        for variable in sorted(constrained_variables)
        if variable not in set(
            program.boundary_variables
        )
    )

    candidate_assignments = tuple(
        tuple(
            zip(
                internal_variables,
                values,
                strict=True,
            )
        )
        for values in product(
            (0, 1),
            repeat=len(internal_variables),
        )
    )

    topology: list[tuple[str, object]] = []
    provenance: list[
        tuple[str, ArtifactProvenance]
    ] = []

    for variable in sorted(constrained_variables):
        element_id = f"node:x{variable}"

        topology.append(
            (
                element_id,
                (
                    "variable-node",
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
                            rule_id="rc.variable-node",
                        ),
                    ),
                ),
            )
        )

    for variable in program.boundary_variables:
        element_id = f"interface:x{variable}"

        topology.append(
            (
                element_id,
                (
                    "boundary-interface",
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
                            rule_id="rc.boundary-interface",
                        ),
                    ),
                ),
            )
        )

    for candidate_index, assignment in enumerate(
        candidate_assignments
    ):
        element_id = (
            f"candidate:{candidate_index}"
        )

        topology.append(
            (
                element_id,
                (
                    "candidate-source",
                    assignment,
                    tuple(
                        (
                            constraint_index,
                            payload.variables,
                            payload.parity,
                        )
                        for (
                            constraint_index,
                            payload,
                        ) in parity_constraints
                    ),
                ),
            )
        )

        provenance.append(
            (
                element_id,
                ArtifactProvenance(
                    ccir_origins=tuple(
                        CCIROrigin(
                            kind="constraint",
                            identifier=str(
                                constraint_index
                            ),
                        )
                        for (
                            constraint_index,
                            _,
                        ) in parity_constraints
                    ),
                    backend_rules=(
                        BackendRuleOrigin(
                            rule_id="rc.candidate-source",
                        ),
                    ),
                ),
            )
        )

    fixed_elements = (
        (
            "aggregate:existential",
            "existential-aggregator",
            "rc.existential-aggregator",
        ),
        (
            "output:rout",
            "output-resistor",
            "rc.output-resistor",
        ),
        (
            "output:cout",
            "output-capacitor",
            "rc.output-capacitor",
        ),
        (
            "output:rleak",
            "output-leak",
            "rc.output-leak",
        ),
        (
            "control:tran",
            "transient-control",
            "rc.transient-control",
        ),
        (
            "readout:vout",
            "readout",
            "rc.readout",
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

    parameters = tuple(
        specification.fixed_parameters
    )

    interface = (
        (
            "boundary_variables",
            program.boundary_variables,
        ),
        (
            "readout_node",
            "vout",
        ),
        (
            "threshold_voltage",
            specification.get_fixed_parameter(
                "threshold_voltage"
            ),
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
            "program_name",
            program.name,
        ),
        (
            "constraint_count",
            len(parity_constraints),
        ),
        (
            "candidate_count",
            len(candidate_assignments),
        ),
    )

    artifact = ExecutionArtifact(
        topology=tuple(topology),
        parameters=parameters,
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
