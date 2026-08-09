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


FPGA_CAPABILITIES = BackendCapabilities(
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
            "synthesizable-logic",
        }
    ),
    artifact_features=frozenset(
        {
            "provenance",
            "logic-network-topology",
            "hdl-preparable",
        }
    ),
)


FPGA_SPECIFICATION = BackendSpecification(
    backend_id="fpga",
    backend_version="1",
    capabilities=FPGA_CAPABILITIES,
    rules=(
        BackendRuleDefinition(
            rule_id="fpga.variable-signal",
        ),
        BackendRuleDefinition(
            rule_id="fpga.boundary-port",
        ),
        BackendRuleDefinition(
            rule_id="fpga.parity-network",
        ),
        BackendRuleDefinition(
            rule_id="fpga.constraint-match",
        ),
        BackendRuleDefinition(
            rule_id="fpga.existential-reduction",
        ),
        BackendRuleDefinition(
            rule_id="fpga.result-signal",
        ),
        BackendRuleDefinition(
            rule_id="fpga.readout",
        ),
    ),
    fixed_parameters=(
        (
            "logic_domain",
            "bit",
        ),
        (
            "representation",
            "synthesizable-logic-network-v1",
        ),
        (
            "hdl_target",
            "verilog-2001",
        ),
    ),
)


@dataclass(frozen=True)
class FPGABackend:
    """
    Native RFC-0003 CCIR-facing FPGA compiler.

    Compilation produces a hardware-oriented logic-network
    ExecutionArtifact without consuming boundary assignments,
    semantic reference results, HDL-tool output, or expected answers.
    """

    specification: BackendSpecification = FPGA_SPECIFICATION

    @property
    def capabilities(
        self,
    ) -> BackendCapabilities:
        return self.specification.capabilities

    def compile(
        self,
        program: CCIRProgram,
    ) -> ExecutionArtifact:
        artifact, required_elements = _compile_fpga_artifact(
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


def _compile_fpga_artifact(
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
        element_id = f"signal:x{variable}"

        topology.append(
            (
                element_id,
                (
                    "variable-signal",
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
                            rule_id="fpga.variable-signal",
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
                            rule_id="fpga.boundary-port",
                        ),
                    ),
                ),
            )
        )

    for constraint_index, payload in parity_constraints:
        network_id = (
            f"logic:parity:{constraint_index}"
        )

        topology.append(
            (
                network_id,
                (
                    "parity-network",
                    payload.variables,
                    payload.parity,
                ),
            )
        )

        provenance.append(
            (
                network_id,
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
                            rule_id="fpga.parity-network",
                        ),
                    ),
                ),
            )
        )

        match_id = (
            f"logic:match:{constraint_index}"
        )

        topology.append(
            (
                match_id,
                (
                    "constraint-match",
                    constraint_index,
                ),
            )
        )

        provenance.append(
            (
                match_id,
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
                            rule_id="fpga.constraint-match",
                        ),
                    ),
                ),
            )
        )

    fixed_elements = (
        (
            "logic:existential",
            "existential-reduction",
            "fpga.existential-reduction",
        ),
        (
            "signal:result",
            "result-signal",
            "fpga.result-signal",
        ),
        (
            "readout:result",
            "readout",
            "fpga.readout",
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
            "readout_signal",
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
