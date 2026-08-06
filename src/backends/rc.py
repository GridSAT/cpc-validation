from __future__ import annotations

from dataclasses import dataclass

from src.compiler import (
    CompiledParityNetwork,
    CompilationStatistics,
    ParityConstraint,
    ParityInstance,
    compile_parity_instance,
)
from src.ir import IRProgram


@dataclass(frozen=True)
class RCBackendResult:
    """
    Result produced by the current ngspice-compatible RC backend.

    The backend consumes only backend-independent IR and returns the generated
    netlist plus the compiler statistics associated with that physical
    program.
    """

    program_name: str
    netlist: str
    statistics: CompilationStatistics

    @property
    def netlist_bytes(self) -> int:
        return len(
            self.netlist.encode("utf-8")
        )


def compile_ir_to_rc(
    program: IRProgram,
) -> RCBackendResult:
    """
    Compile backend-independent CPC IR into the current RC/ngspice netlist.

    This compatibility implementation deliberately delegates to the proven
    v0.3 parity netlist emitter after reconstructing the source parity
    instance exclusively from the IR.

    The delegation protects byte-for-byte compatibility while establishing
    the backend boundary:

        ParityInstance
              |
              v
          IRProgram
              |
              v
         RC backend
              |
              v
        ngspice netlist

    The backend does not receive or compute an independent continuation value.
    """
    instance = parity_instance_from_ir(
        program
    )

    compiled = compile_parity_instance(
        instance,
        program.boundary_assignment_dict,
        supply_voltage=(
            program.interface.supply_voltage
        ),
        resistance_kohm=(
            program.interface.resistance_kohm
        ),
        capacitance_uf=(
            program.interface.capacitance_uf
        ),
        end_time_ms=(
            program.interface.end_time_ms
        ),
    )

    return _result_from_compiled(
        program,
        compiled,
    )


def parity_instance_from_ir(
    program: IRProgram,
) -> ParityInstance:
    """
    Reconstruct the logical parity instance represented by an IR program.

    This conversion intentionally uses only logical IR fields. Candidate
    assignments and interface values do not alter the reconstructed source
    constraints.
    """
    return ParityInstance(
        constraints=tuple(
            ParityConstraint(
                variables=constraint.variables,
                parity=constraint.parity,
            )
            for constraint in program.constraints
        ),
        boundary_variables=(
            program.boundary_variables
        ),
    )


def _result_from_compiled(
    program: IRProgram,
    compiled: CompiledParityNetwork,
) -> RCBackendResult:
    return RCBackendResult(
        program_name=program.name,
        netlist=compiled.netlist,
        statistics=compiled.statistics,
    )
