from __future__ import annotations

from collections.abc import Mapping

from src.compiler import ParityInstance
from src.ir import (
    IRConstraint,
    IRInterface,
    IRProgram,
    enumerate_ir_candidates,
)


DEFAULT_IR_THRESHOLD_V = 2.5


def compile_parity_instance_to_ir(
    instance: ParityInstance,
    boundary_values: Mapping[int, int],
    *,
    name: str | None = None,
    supply_voltage: float = 5.0,
    resistance_kohm: float = 10.0,
    capacitance_uf: float = 1.0,
    threshold_voltage: float = DEFAULT_IR_THRESHOLD_V,
    end_time_ms: float = 50.0,
) -> IRProgram:
    """
    Compile one admitted parity instance into backend-independent IR.

    The adapter records only:

    - the source parity constraints;
    - the boundary/internal variable partition;
    - the admitted boundary assignment;
    - deterministic internal candidate assignments; and
    - the backend-neutral interface contract.

    It does not compute or embed:

    - the continuation value;
    - satisfying completions;
    - completion counts;
    - decoded results;
    - output voltages; or
    - backend-specific syntax.
    """
    normalized_boundary_values = _normalize_boundary_values(
        instance,
        boundary_values,
    )

    boundary_assignment = tuple(
        (
            variable,
            normalized_boundary_values[variable],
        )
        for variable in instance.boundary_variables
    )

    constraints = tuple(
        IRConstraint(
            variables=constraint.variables,
            parity=constraint.parity,
        )
        for constraint in instance.constraints
    )

    resolved_name = (
        name
        if name is not None
        else _default_program_name(
            instance,
            normalized_boundary_values,
        )
    )

    return IRProgram(
        name=resolved_name,
        constraints=constraints,
        boundary_variables=instance.boundary_variables,
        internal_variables=instance.internal_variables,
        boundary_assignment=boundary_assignment,
        candidates=enumerate_ir_candidates(
            instance.internal_variables
        ),
        interface=IRInterface(
            supply_voltage=supply_voltage,
            resistance_kohm=resistance_kohm,
            capacitance_uf=capacitance_uf,
            threshold_voltage=threshold_voltage,
            end_time_ms=end_time_ms,
        ),
    )


def _normalize_boundary_values(
    instance: ParityInstance,
    boundary_values: Mapping[int, int],
) -> dict[int, int]:
    expected_variables = set(
        instance.boundary_variables
    )

    actual_variables = set(
        boundary_values
    )

    missing = (
        expected_variables
        - actual_variables
    )

    extra = (
        actual_variables
        - expected_variables
    )

    if missing:
        raise ValueError(
            "missing boundary values for: "
            + ", ".join(
                f"x{variable}"
                for variable in sorted(missing)
            )
        )

    if extra:
        raise ValueError(
            "received values for non-boundary variables: "
            + ", ".join(
                f"x{variable}"
                for variable in sorted(extra)
            )
        )

    normalized: dict[int, int] = {}

    for variable in instance.boundary_variables:
        value = boundary_values[variable]

        if isinstance(value, bool) or value not in (0, 1):
            raise ValueError(
                "boundary values must be integer bits; "
                f"x{variable} received {value!r}"
            )

        normalized[variable] = int(value)

    return normalized


def _default_program_name(
    instance: ParityInstance,
    boundary_values: Mapping[int, int],
) -> str:
    boundary_label = "-".join(
        f"x{variable}-{boundary_values[variable]}"
        for variable in instance.boundary_variables
    )

    return (
        "parity-"
        f"{len(instance.variables)}v-"
        f"{len(instance.constraints)}c-"
        f"{boundary_label}"
    )
