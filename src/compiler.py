from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from src.rc_emitter import (
    constraint_validity_expression,
    enumerate_internal_assignments,
    xor2_expression,
    xor_expression,
)


@dataclass(frozen=True)
class ParityConstraint:
    """
    Boolean parity constraint.

    The constraint is satisfied exactly when the XOR of the listed variables
    equals ``parity``.

    Example:

        ParityConstraint(variables=(0, 1, 2), parity=0)

    represents:

        x0 XOR x1 XOR x2 = 0
    """

    variables: tuple[int, ...]
    parity: int

    def __post_init__(self) -> None:
        if not self.variables:
            raise ValueError(
                "a parity constraint must contain at least one variable"
            )

        if len(set(self.variables)) != len(self.variables):
            raise ValueError(
                "a parity constraint may not repeat a variable"
            )

        if any(variable < 0 for variable in self.variables):
            raise ValueError(
                "variable indices must be nonnegative integers"
            )

        if self.parity not in (0, 1):
            raise ValueError(
                "constraint parity must be 0 or 1"
            )


@dataclass(frozen=True)
class ParityInstance:
    """
    Complete parity-system description admitted by the compiler.

    ``boundary_variables`` are externally supplied.

    Every remaining variable appearing in the constraints is treated as an
    internal variable and is existentially quantified by the compiled network.
    """

    constraints: tuple[ParityConstraint, ...]
    boundary_variables: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.constraints:
            raise ValueError(
                "a parity instance must contain at least one constraint"
            )

        if len(set(self.boundary_variables)) != len(
            self.boundary_variables
        ):
            raise ValueError(
                "boundary variables may not be repeated"
            )

        if any(variable < 0 for variable in self.boundary_variables):
            raise ValueError(
                "boundary-variable indices must be nonnegative integers"
            )

        unknown_boundaries = (
            set(self.boundary_variables)
            - set(self.variables)
        )

        if unknown_boundaries:
            raise ValueError(
                "boundary variables must occur in at least one constraint: "
                + ", ".join(
                    str(variable)
                    for variable in sorted(unknown_boundaries)
                )
            )

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
        boundary_set = set(self.boundary_variables)

        return tuple(
            variable
            for variable in self.variables
            if variable not in boundary_set
        )


@dataclass(frozen=True)
class CompilationStatistics:
    constraint_count: int
    variable_count: int
    boundary_variable_count: int
    internal_variable_count: int
    candidate_count: int
    candidate_source_count: int
    behavioral_source_count: int


@dataclass(frozen=True)
class CompiledParityNetwork:
    netlist: str
    statistics: CompilationStatistics


DEFAULT_XOR_INSTANCE = ParityInstance(
    constraints=(
        ParityConstraint(
            variables=(0, 1, 2),
            parity=0,
        ),
        ParityConstraint(
            variables=(1, 2, 3),
            parity=1,
        ),
    ),
    boundary_variables=(0, 3),
)


def compile_parity_instance(
    instance: ParityInstance,
    boundary_values: Mapping[int, int],
    *,
    supply_voltage: float = 5.0,
    resistance_kohm: float = 10.0,
    capacitance_uf: float = 1.0,
    end_time_ms: float = 50.0,
) -> CompiledParityNetwork:
    """
    Backward-compatible parity compilation entry point.

    The canonical compilation path is now:

        ParityInstance
            -> CCIR
            -> RFC-0003 backend dispatcher
            -> RC ExecutionArtifact
            -> boundary preparation
            -> ngspice netlist

    Boundary values are execution-preparation inputs and do not participate
    in canonical CCIR-to-RC backend compilation.
    """
    from dataclasses import replace

    from src.backends.rc_ccir import (
        RCBackend,
        RC_SPECIFICATION,
    )
    from src.backends.rc_prepare import (
        prepare_rc_netlist,
    )
    from src.ccir_lower_parity import (
        lower_parity_instance_to_ccir,
    )
    from src.compile_backend import (
        compile_backend,
    )

    program = lower_parity_instance_to_ccir(
        instance
    )

    specification = replace(
        RC_SPECIFICATION,
        fixed_parameters=(
            (
                "supply_voltage",
                float(supply_voltage),
            ),
            (
                "resistance_kohm",
                float(resistance_kohm),
            ),
            (
                "capacitance_uf",
                float(capacitance_uf),
            ),
            (
                "threshold_voltage",
                2.5,
            ),
            (
                "end_time_ms",
                float(end_time_ms),
            ),
        ),
    )

    artifact = compile_backend(
        program,
        RCBackend(
            specification=specification,
        ),
    )

    netlist, raw_statistics = prepare_rc_netlist(
        program,
        artifact,
        boundary_values,
        specification,
    )

    statistics = CompilationStatistics(
        constraint_count=(
            raw_statistics["constraint_count"]
        ),
        variable_count=(
            raw_statistics["variable_count"]
        ),
        boundary_variable_count=(
            raw_statistics["boundary_variable_count"]
        ),
        internal_variable_count=(
            raw_statistics["internal_variable_count"]
        ),
        candidate_count=(
            raw_statistics["candidate_count"]
        ),
        candidate_source_count=(
            raw_statistics["candidate_source_count"]
        ),
        behavioral_source_count=(
            raw_statistics["behavioral_source_count"]
        ),
    )

    return CompiledParityNetwork(
        netlist=netlist,
        statistics=statistics,
    )
