from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable, Mapping, Sequence


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
    Compile a parity instance into an ngspice netlist.

    Compilation uses only:

    - the parity constraints;
    - the declared boundary variables;
    - the admitted boundary values; and
    - fixed family-wide compilation rules.

    It does not use an independently computed continuation value.
    """
    _validate_positive(
        supply_voltage,
        "supply_voltage",
    )
    _validate_positive(
        resistance_kohm,
        "resistance_kohm",
    )
    _validate_positive(
        capacitance_uf,
        "capacitance_uf",
    )
    _validate_positive(
        end_time_ms,
        "end_time_ms",
    )

    normalized_boundary = _validate_boundary_values(
        instance,
        boundary_values,
    )

    internal_variables = instance.internal_variables
    assignments = tuple(
        enumerate_internal_assignments(internal_variables)
    )

    boundary_lines = [
        (
            f"Vx{variable} x{variable} 0 "
            f"{normalized_boundary[variable] * supply_voltage}"
        )
        for variable in instance.boundary_variables
    ]

    candidate_lines: list[str] = []
    candidate_nodes: list[str] = []

    for candidate_index, internal_assignment in enumerate(assignments):
        node = f"candidate{candidate_index}"
        candidate_nodes.append(node)

        complete_assignment = {
            **normalized_boundary,
            **internal_assignment,
        }

        constraint_validity_expressions = [
            constraint_validity_expression(
                constraint=constraint,
                fixed_values=complete_assignment,
                supply_voltage=supply_voltage,
                boundary_variables=instance.boundary_variables,
            )
            for constraint in instance.constraints
        ]

        candidate_validity = "*".join(
            f"({expression})"
            for expression in constraint_validity_expressions
        )

        candidate_lines.append(
            f"B{node} {node} 0 "
            f"V={{{supply_voltage}*({candidate_validity})}}"
        )

    no_candidate_expression = "*".join(
        f"(1-v({node})/{supply_voltage})"
        for node in candidate_nodes
    )

    existential_expression = (
        f"{supply_voltage}*(1-({no_candidate_expression}))"
    )

    constraint_comments = [
        (
            "*   "
            + " XOR ".join(
                f"x{variable}"
                for variable in constraint.variables
            )
            + f" = {constraint.parity}"
        )
        for constraint in instance.constraints
    ]

    internal_comment = (
        ", ".join(
            f"x{variable}"
            for variable in internal_variables
        )
        if internal_variables
        else "(none)"
    )

    boundary_comment = ", ".join(
        f"x{variable}"
        for variable in instance.boundary_variables
    )

    lines = [
        "* CPC generic parity-constraint compiler",
        "*",
        "* Source constraints:",
        *constraint_comments,
        "*",
        f"* Boundary variables: {boundary_comment}",
        f"* Internal variables: {internal_comment}",
        f"* Candidate assignments: {len(assignments)}",
        "*",
        "* The continuation answer is not inserted into this netlist.",
        "",
        *boundary_lines,
        "",
        "* One candidate-validity source per internal assignment",
        *candidate_lines,
        "",
        "* Existential aggregation over all internal assignments",
        f"Bexist logic 0 V={{{existential_expression}}}",
        "",
        "* Restricted RC interface",
        f"Rout logic vout {resistance_kohm}k",
        f"Cout vout 0 {capacitance_uf}u",
        "Rleak vout 0 1G",
        "",
        f".tran 0.1m {end_time_ms}m",
        f".meas tran vout_final FIND v(vout) AT={end_time_ms}m",
        ".end",
        "",
    ]

    statistics = CompilationStatistics(
        constraint_count=len(instance.constraints),
        variable_count=len(instance.variables),
        boundary_variable_count=len(instance.boundary_variables),
        internal_variable_count=len(internal_variables),
        candidate_count=len(assignments),
        candidate_source_count=len(candidate_lines),
        behavioral_source_count=len(candidate_lines) + 1,
    )

    return CompiledParityNetwork(
        netlist="\n".join(lines),
        statistics=statistics,
    )


def enumerate_internal_assignments(
    internal_variables: Sequence[int],
) -> Iterable[dict[int, int]]:
    """
    Enumerate all Boolean assignments to the internal variables.
    """
    for values in product(
        (0, 1),
        repeat=len(internal_variables),
    ):
        yield dict(
            zip(
                internal_variables,
                values,
                strict=True,
            )
        )


def constraint_validity_expression(
    *,
    constraint: ParityConstraint,
    fixed_values: Mapping[int, int],
    supply_voltage: float,
    boundary_variables: Sequence[int],
) -> str:
    """
    Return a normalized expression that is 1 exactly when the constraint holds.

    Internal variables are fixed candidate values.

    Boundary variables remain represented by their circuit-node voltages, so
    the generated expression is derived from the admitted boundary interface
    rather than from an independently computed continuation result.
    """
    boundary_set = set(boundary_variables)

    terms: list[str] = []

    for variable in constraint.variables:
        if variable not in fixed_values:
            raise ValueError(
                f"no value or boundary source supplied for x{variable}"
            )

        if variable in boundary_set:
            terms.append(
                f"(v(x{variable})/{supply_voltage})"
            )
        else:
            value = fixed_values[variable]
            _validate_bit(
                value,
                f"x{variable}",
            )
            terms.append(str(value))

    parity_expression = xor_expression(terms)

    if constraint.parity == 1:
        return f"({parity_expression})"

    return f"(1-({parity_expression}))"


def xor_expression(
    terms: Sequence[str],
) -> str:
    """
    Construct an algebraic XOR expression for one or more normalized terms.

    For normalized Boolean values a and b:

        XOR(a,b) = a + b - 2ab

    Longer XOR expressions are compiled by left-associated composition.
    """
    if not terms:
        raise ValueError(
            "xor_expression requires at least one term"
        )

    expression = f"({terms[0]})"

    for term in terms[1:]:
        expression = xor2_expression(
            expression,
            f"({term})",
        )

    return expression


def xor2_expression(
    first: str,
    second: str,
) -> str:
    return (
        f"(({first})+({second})"
        f"-2*({first})*({second}))"
    )


def _validate_boundary_values(
    instance: ParityInstance,
    boundary_values: Mapping[int, int],
) -> dict[int, int]:
    required = set(instance.boundary_variables)
    supplied = set(boundary_values)

    missing = required - supplied
    unexpected = supplied - required

    if missing:
        raise ValueError(
            "missing boundary values for: "
            + ", ".join(
                f"x{variable}"
                for variable in sorted(missing)
            )
        )

    if unexpected:
        raise ValueError(
            "unexpected boundary values for: "
            + ", ".join(
                f"x{variable}"
                for variable in sorted(unexpected)
            )
        )

    normalized = dict(boundary_values)

    for variable, value in normalized.items():
        _validate_bit(
            value,
            f"x{variable}",
        )

    return normalized


def _validate_bit(
    value: int,
    name: str,
) -> None:
    if value not in (0, 1):
        raise ValueError(
            f"{name} must be 0 or 1, received {value!r}"
        )


def _validate_positive(
    value: float,
    name: str,
) -> None:
    if value <= 0:
        raise ValueError(
            f"{name} must be greater than zero, received {value!r}"
        )
