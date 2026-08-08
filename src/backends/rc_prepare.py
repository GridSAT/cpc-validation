from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from src.backend import (
    BackendSpecification,
    ExecutionArtifact,
)
from src.ccir import CCIRProgram
from src.ccir_parity import (
    CCIRParityPayload,
    PARITY_CONSTRAINT_FAMILY,
)
from src.rc_emitter import (
    emit_parity_rc_netlist,
)
from src.prepared_execution import PreparedExecution


@dataclass(frozen=True)
class _CCIRParityInstanceView:
    """
    Structural parity view of canonical CCIR for the legacy RC emitter.

    This is an execution-preparation adapter only. It performs no semantic
    evaluation and does not reconstruct a source-language ParityInstance.
    """

    constraints: tuple[CCIRParityPayload, ...]
    boundary_variables: tuple[int, ...]

    @property
    def variables(self) -> tuple[int, ...]:
        return tuple(
            sorted(
                {
                    variable
                    for constraint in self.constraints
                    for variable in constraint.variables
                }
            )
        )

    @property
    def internal_variables(self) -> tuple[int, ...]:
        boundary = set(
            self.boundary_variables
        )

        return tuple(
            variable
            for variable in self.variables
            if variable not in boundary
        )


def prepare_rc_execution(
    program: CCIRProgram,
    artifact: ExecutionArtifact,
    boundary_values: Mapping[int, int],
    specification: BackendSpecification,
) -> PreparedExecution:
    """
    Prepare one concrete RC/ngspice execution from a compiled RC artifact.

    Boundary values enter here, after canonical RFC-0003 compilation.

    This function performs no independent semantic evaluation.
    """
    metadata = dict(
        artifact.metadata
    )

    if metadata.get("backend_id") != specification.backend_id:
        raise ValueError(
            "execution artifact backend does not match "
            "the supplied backend specification"
        )

    if metadata.get("program_name") != program.name:
        raise ValueError(
            "execution artifact program does not match CCIR input"
        )

    if dict(artifact.parameters) != dict(
        specification.fixed_parameters
    ):
        raise ValueError(
            "execution artifact parameters do not match "
            "the supplied backend specification"
        )

    constraints: list[
        CCIRParityPayload
    ] = []

    for constraint in program.constraints:
        if constraint.family != PARITY_CONSTRAINT_FAMILY:
            raise ValueError(
                "RC preparation currently supports only "
                "CCIR parity constraints"
            )

        if not isinstance(
            constraint.payload,
            CCIRParityPayload,
        ):
            raise ValueError(
                "parity CCIR constraint requires "
                "CCIRParityPayload"
            )

        constraints.append(
            constraint.payload
        )

    view = _CCIRParityInstanceView(
        constraints=tuple(constraints),
        boundary_variables=program.boundary_variables,
    )

    netlist, emitter_metadata = emit_parity_rc_netlist(
        view,
        boundary_values,
        supply_voltage=float(
            specification.get_fixed_parameter(
                "supply_voltage"
            )
        ),
        resistance_kohm=float(
            specification.get_fixed_parameter(
                "resistance_kohm"
            )
        ),
        capacitance_uf=float(
            specification.get_fixed_parameter(
                "capacitance_uf"
            )
        ),
        end_time_ms=float(
            specification.get_fixed_parameter(
                "end_time_ms"
            )
        ),
    )

    interface = tuple(
        artifact.interface
    )

    decoder_specification = (
        (
            "threshold_voltage",
            specification.get_fixed_parameter(
                "threshold_voltage"
            ),
        ),
    )

    metadata = (
        (
            "boundary_values",
            tuple(
                sorted(
                    boundary_values.items()
                )
            ),
        ),
        (
            "emitter_metadata",
            tuple(
                sorted(
                    emitter_metadata.items()
                )
            ),
        ),
        (
            "preparation_id",
            "rc.ngspice-netlist.v1",
        ),
    )

    return PreparedExecution(
        backend_id=specification.backend_id,
        backend_version=specification.backend_version,
        payload=netlist,
        interface=interface,
        decoder_specification=decoder_specification,
        metadata=metadata,
    )


def prepare_rc_netlist(
    program: CCIRProgram,
    artifact: ExecutionArtifact,
    boundary_values: Mapping[int, int],
    specification: BackendSpecification,
) -> tuple[str, dict[str, int]]:
    """
    Compatibility wrapper returning the historical RC preparation tuple.

    New RFC-0004 code should use prepare_rc_execution().
    """
    prepared = prepare_rc_execution(
        program,
        artifact,
        boundary_values,
        specification,
    )

    metadata = dict(
        prepared.metadata
    )

    return (
        prepared.payload,
        dict(
            metadata["emitter_metadata"]
        ),
    )
