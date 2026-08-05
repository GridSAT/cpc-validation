from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


IR_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class IRConstraint:
    """
    Backend-independent Boolean parity constraint.

    The constraint represents

        XOR(variables) = parity

    for Boolean variables and parity in {0, 1}.
    """

    variables: tuple[int, ...]
    parity: int

    def __post_init__(self) -> None:
        normalized_variables = tuple(
            int(variable)
            for variable in self.variables
        )

        if not normalized_variables:
            raise ValueError(
                "IR constraint must contain at least one variable"
            )

        if any(
            variable < 0
            for variable in normalized_variables
        ):
            raise ValueError(
                "IR constraint variables must be non-negative"
            )

        if len(set(normalized_variables)) != len(
            normalized_variables
        ):
            raise ValueError(
                "IR constraint variables must be unique"
            )

        if self.parity not in (0, 1):
            raise ValueError(
                "IR constraint parity must be 0 or 1"
            )

        object.__setattr__(
            self,
            "variables",
            normalized_variables,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "variables": list(self.variables),
            "parity": self.parity,
        }

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> IRConstraint:
        _require_exact_keys(
            data,
            required={
                "variables",
                "parity",
            },
            context="IR constraint",
        )

        variables = data["variables"]

        if not isinstance(
            variables,
            Sequence,
        ) or isinstance(
            variables,
            (
                str,
                bytes,
            ),
        ):
            raise ValueError(
                "IR constraint variables must be a sequence"
            )

        return cls(
            variables=tuple(
                _require_int(
                    variable,
                    context="IR constraint variable",
                )
                for variable in variables
            ),
            parity=_require_int(
                data["parity"],
                context="IR constraint parity",
            ),
        )


@dataclass(frozen=True)
class IRCandidate:
    """
    One enumerated assignment of the internal variables.

    Candidate validity is determined by a backend from the program constraints,
    admitted boundary assignment, and this internal assignment. The candidate
    object contains no expected continuation value.
    """

    index: int
    assignment: tuple[tuple[int, int], ...]

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError(
                "IR candidate index must be non-negative"
            )

        normalized_assignment = tuple(
            (
                int(variable),
                int(value),
            )
            for variable, value in self.assignment
        )

        variables = tuple(
            variable
            for variable, _ in normalized_assignment
        )

        if len(set(variables)) != len(variables):
            raise ValueError(
                "IR candidate assignment variables must be unique"
            )

        if any(
            variable < 0
            for variable in variables
        ):
            raise ValueError(
                "IR candidate assignment variables must be non-negative"
            )

        for variable, value in normalized_assignment:
            if value not in (0, 1):
                raise ValueError(
                    "IR candidate assignment values must be 0 or 1; "
                    f"x{variable} received {value!r}"
                )

        if variables != tuple(sorted(variables)):
            raise ValueError(
                "IR candidate assignment variables must be sorted"
            )

        object.__setattr__(
            self,
            "assignment",
            normalized_assignment,
        )

    @property
    def assignment_dict(self) -> dict[int, int]:
        return dict(self.assignment)

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "assignment": [
                {
                    "variable": variable,
                    "value": value,
                }
                for variable, value in self.assignment
            ],
        }

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> IRCandidate:
        _require_exact_keys(
            data,
            required={
                "index",
                "assignment",
            },
            context="IR candidate",
        )

        raw_assignment = data["assignment"]

        if not isinstance(
            raw_assignment,
            Sequence,
        ) or isinstance(
            raw_assignment,
            (
                str,
                bytes,
            ),
        ):
            raise ValueError(
                "IR candidate assignment must be a sequence"
            )

        assignment: list[tuple[int, int]] = []

        for item in raw_assignment:
            if not isinstance(item, Mapping):
                raise ValueError(
                    "IR candidate assignment entries must be objects"
                )

            _require_exact_keys(
                item,
                required={
                    "variable",
                    "value",
                },
                context="IR candidate assignment entry",
            )

            assignment.append(
                (
                    _require_int(
                        item["variable"],
                        context=(
                            "IR candidate assignment variable"
                        ),
                    ),
                    _require_int(
                        item["value"],
                        context=(
                            "IR candidate assignment value"
                        ),
                    ),
                )
            )

        return cls(
            index=_require_int(
                data["index"],
                context="IR candidate index",
            ),
            assignment=tuple(assignment),
        )


@dataclass(frozen=True)
class IRInterface:
    """
    Backend-independent physical-interface parameters.

    These values describe the current RC-compatible execution contract without
    encoding ngspice syntax in the IR.
    """

    supply_voltage: float = 5.0
    resistance_kohm: float = 10.0
    capacitance_uf: float = 1.0
    threshold_voltage: float = 2.5
    end_time_ms: float = 50.0

    def __post_init__(self) -> None:
        positive_fields = {
            "supply_voltage": self.supply_voltage,
            "resistance_kohm": self.resistance_kohm,
            "capacitance_uf": self.capacitance_uf,
            "end_time_ms": self.end_time_ms,
        }

        for name, value in positive_fields.items():
            if value <= 0.0:
                raise ValueError(
                    f"{name} must be greater than zero"
                )

        if not (
            0.0
            <= self.threshold_voltage
            <= self.supply_voltage
        ):
            raise ValueError(
                "threshold_voltage must lie between zero "
                "and supply_voltage"
            )

    def to_dict(self) -> dict[str, float]:
        return {
            "supply_voltage": self.supply_voltage,
            "resistance_kohm": self.resistance_kohm,
            "capacitance_uf": self.capacitance_uf,
            "threshold_voltage": self.threshold_voltage,
            "end_time_ms": self.end_time_ms,
        }

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> IRInterface:
        _require_exact_keys(
            data,
            required={
                "supply_voltage",
                "resistance_kohm",
                "capacitance_uf",
                "threshold_voltage",
                "end_time_ms",
            },
            context="IR interface",
        )

        return cls(
            supply_voltage=_require_number(
                data["supply_voltage"],
                context="IR interface supply_voltage",
            ),
            resistance_kohm=_require_number(
                data["resistance_kohm"],
                context="IR interface resistance_kohm",
            ),
            capacitance_uf=_require_number(
                data["capacitance_uf"],
                context="IR interface capacitance_uf",
            ),
            threshold_voltage=_require_number(
                data["threshold_voltage"],
                context="IR interface threshold_voltage",
            ),
            end_time_ms=_require_number(
                data["end_time_ms"],
                context="IR interface end_time_ms",
            ),
        )


@dataclass(frozen=True)
class IRProgram:
    """
    Backend-independent compiled continuation program.

    The program records:

    - the logical parity constraints;
    - the boundary and internal variable partitions;
    - one admitted boundary assignment;
    - all internal candidate assignments; and
    - the physical-interface contract.

    It intentionally does not contain:

    - an expected continuation value;
    - satisfying completion counts;
    - expected output voltages;
    - decoded results; or
    - backend-specific syntax.
    """

    name: str
    constraints: tuple[IRConstraint, ...]
    boundary_variables: tuple[int, ...]
    internal_variables: tuple[int, ...]
    boundary_assignment: tuple[tuple[int, int], ...]
    candidates: tuple[IRCandidate, ...]
    interface: IRInterface = IRInterface()
    schema_version: int = IR_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != IR_SCHEMA_VERSION:
            raise ValueError(
                "unsupported IR schema version: "
                f"{self.schema_version}"
            )

        if not self.name.strip():
            raise ValueError(
                "IR program name may not be empty"
            )

        if not self.constraints:
            raise ValueError(
                "IR program must contain at least one constraint"
            )

        boundary_variables = tuple(
            int(variable)
            for variable in self.boundary_variables
        )

        internal_variables = tuple(
            int(variable)
            for variable in self.internal_variables
        )

        _validate_variable_partition(
            boundary_variables,
            internal_variables,
        )

        constrained_variables = tuple(
            sorted(
                {
                    variable
                    for constraint in self.constraints
                    for variable in constraint.variables
                }
            )
        )

        declared_variables = tuple(
            sorted(
                (
                    *boundary_variables,
                    *internal_variables,
                )
            )
        )

        if declared_variables != constrained_variables:
            raise ValueError(
                "IR boundary and internal variables must exactly cover "
                "the constrained variables"
            )

        boundary_assignment = tuple(
            (
                int(variable),
                int(value),
            )
            for variable, value in self.boundary_assignment
        )

        assignment_variables = tuple(
            variable
            for variable, _ in boundary_assignment
        )

        if assignment_variables != boundary_variables:
            raise ValueError(
                "IR boundary assignment must follow the exact "
                "boundary-variable order"
            )

        for variable, value in boundary_assignment:
            if value not in (0, 1):
                raise ValueError(
                    "IR boundary values must be 0 or 1; "
                    f"x{variable} received {value!r}"
                )

        expected_candidate_count = 2 ** len(
            internal_variables
        )

        if len(self.candidates) != expected_candidate_count:
            raise ValueError(
                "IR candidate count must equal 2^k for k internal "
                f"variables: expected {expected_candidate_count}, "
                f"received {len(self.candidates)}"
            )

        expected_indices = tuple(
            range(expected_candidate_count)
        )

        actual_indices = tuple(
            candidate.index
            for candidate in self.candidates
        )

        if actual_indices != expected_indices:
            raise ValueError(
                "IR candidate indices must be contiguous from zero"
            )

        expected_assignment_variables = internal_variables

        seen_assignments: set[
            tuple[tuple[int, int], ...]
        ] = set()

        for candidate in self.candidates:
            candidate_variables = tuple(
                variable
                for variable, _ in candidate.assignment
            )

            if candidate_variables != expected_assignment_variables:
                raise ValueError(
                    "every IR candidate must assign exactly the "
                    "internal variables in declared order"
                )

            if candidate.assignment in seen_assignments:
                raise ValueError(
                    "IR candidate assignments must be unique"
                )

            seen_assignments.add(
                candidate.assignment
            )

        object.__setattr__(
            self,
            "boundary_variables",
            boundary_variables,
        )

        object.__setattr__(
            self,
            "internal_variables",
            internal_variables,
        )

        object.__setattr__(
            self,
            "boundary_assignment",
            boundary_assignment,
        )

    @property
    def variables(self) -> tuple[int, ...]:
        return tuple(
            sorted(
                (
                    *self.boundary_variables,
                    *self.internal_variables,
                )
            )
        )

    @property
    def boundary_assignment_dict(
        self,
    ) -> dict[int, int]:
        return dict(self.boundary_assignment)

    @property
    def candidate_count(self) -> int:
        return len(self.candidates)

    @property
    def behavioral_source_count(self) -> int:
        return self.candidate_count + 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "name": self.name,
            "constraints": [
                constraint.to_dict()
                for constraint in self.constraints
            ],
            "boundary_variables": list(
                self.boundary_variables
            ),
            "internal_variables": list(
                self.internal_variables
            ),
            "boundary_assignment": [
                {
                    "variable": variable,
                    "value": value,
                }
                for variable, value in self.boundary_assignment
            ],
            "candidates": [
                candidate.to_dict()
                for candidate in self.candidates
            ],
            "interface": self.interface.to_dict(),
        }

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> IRProgram:
        _require_exact_keys(
            data,
            required={
                "schema_version",
                "name",
                "constraints",
                "boundary_variables",
                "internal_variables",
                "boundary_assignment",
                "candidates",
                "interface",
            },
            context="IR program",
        )

        constraints = _require_sequence(
            data["constraints"],
            context="IR program constraints",
        )

        boundary_variables = _require_sequence(
            data["boundary_variables"],
            context="IR program boundary_variables",
        )

        internal_variables = _require_sequence(
            data["internal_variables"],
            context="IR program internal_variables",
        )

        raw_boundary_assignment = _require_sequence(
            data["boundary_assignment"],
            context="IR program boundary_assignment",
        )

        candidates = _require_sequence(
            data["candidates"],
            context="IR program candidates",
        )

        interface = data["interface"]

        if not isinstance(interface, Mapping):
            raise ValueError(
                "IR program interface must be an object"
            )

        parsed_boundary_assignment: list[
            tuple[int, int]
        ] = []

        for item in raw_boundary_assignment:
            if not isinstance(item, Mapping):
                raise ValueError(
                    "IR boundary-assignment entries must be objects"
                )

            _require_exact_keys(
                item,
                required={
                    "variable",
                    "value",
                },
                context="IR boundary-assignment entry",
            )

            parsed_boundary_assignment.append(
                (
                    _require_int(
                        item["variable"],
                        context=(
                            "IR boundary-assignment variable"
                        ),
                    ),
                    _require_int(
                        item["value"],
                        context=(
                            "IR boundary-assignment value"
                        ),
                    ),
                )
            )

        return cls(
            schema_version=_require_int(
                data["schema_version"],
                context="IR schema_version",
            ),
            name=_require_string(
                data["name"],
                context="IR program name",
            ),
            constraints=tuple(
                IRConstraint.from_dict(item)
                for item in _require_mapping_items(
                    constraints,
                    context="IR program constraint",
                )
            ),
            boundary_variables=tuple(
                _require_int(
                    variable,
                    context="IR boundary variable",
                )
                for variable in boundary_variables
            ),
            internal_variables=tuple(
                _require_int(
                    variable,
                    context="IR internal variable",
                )
                for variable in internal_variables
            ),
            boundary_assignment=tuple(
                parsed_boundary_assignment
            ),
            candidates=tuple(
                IRCandidate.from_dict(item)
                for item in _require_mapping_items(
                    candidates,
                    context="IR program candidate",
                )
            ),
            interface=IRInterface.from_dict(
                interface
            ),
        )

    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        return (
            json.dumps(
                self.to_dict(),
                indent=indent,
                sort_keys=False,
            )
            + "\n"
        )

    @classmethod
    def from_json(
        cls,
        text: str,
    ) -> IRProgram:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as error:
            raise ValueError(
                "invalid IR JSON"
            ) from error

        if not isinstance(data, Mapping):
            raise ValueError(
                "IR JSON root must be an object"
            )

        return cls.from_dict(data)

    def write_json(
        self,
        path: Path,
        *,
        indent: int = 2,
    ) -> None:
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            self.to_json(indent=indent),
            encoding="utf-8",
        )

    @classmethod
    def read_json(
        cls,
        path: Path,
    ) -> IRProgram:
        return cls.from_json(
            path.read_text(
                encoding="utf-8"
            )
        )

    def pretty(self) -> str:
        lines = [
            f"IR program: {self.name}",
            f"Schema version: {self.schema_version}",
            (
                "Variables: "
                + ", ".join(
                    f"x{variable}"
                    for variable in self.variables
                )
            ),
            (
                "Boundary variables: "
                + ", ".join(
                    f"x{variable}"
                    for variable in self.boundary_variables
                )
            ),
            (
                "Internal variables: "
                + (
                    ", ".join(
                        f"x{variable}"
                        for variable in self.internal_variables
                    )
                    or "(none)"
                )
            ),
            (
                "Boundary assignment: "
                + ", ".join(
                    f"x{variable}={value}"
                    for variable, value
                    in self.boundary_assignment
                )
            ),
            f"Constraints: {len(self.constraints)}",
        ]

        for index, constraint in enumerate(
            self.constraints,
            start=1,
        ):
            expression = " XOR ".join(
                f"x{variable}"
                for variable in constraint.variables
            )

            lines.append(
                f"  {index}. {expression} = {constraint.parity}"
            )

        lines.extend(
            [
                f"Candidates: {self.candidate_count}",
                (
                    "Behavioral sources: "
                    f"{self.behavioral_source_count}"
                ),
                (
                    "Interface: "
                    f"supply={self.interface.supply_voltage:g} V, "
                    f"R={self.interface.resistance_kohm:g} kOhm, "
                    f"C={self.interface.capacitance_uf:g} uF, "
                    f"threshold={self.interface.threshold_voltage:g} V, "
                    f"end={self.interface.end_time_ms:g} ms"
                ),
            ]
        )

        return "\n".join(lines)


def enumerate_ir_candidates(
    internal_variables: Sequence[int],
) -> tuple[IRCandidate, ...]:
    """
    Enumerate all internal assignments in deterministic binary order.

    The last declared internal variable changes fastest.
    """
    normalized_variables = tuple(
        int(variable)
        for variable in internal_variables
    )

    if len(set(normalized_variables)) != len(
        normalized_variables
    ):
        raise ValueError(
            "internal variables must be unique"
        )

    if normalized_variables != tuple(
        sorted(normalized_variables)
    ):
        raise ValueError(
            "internal variables must be sorted"
        )

    if any(
        variable < 0
        for variable in normalized_variables
    ):
        raise ValueError(
            "internal variables must be non-negative"
        )

    candidate_count = 2 ** len(
        normalized_variables
    )

    candidates: list[IRCandidate] = []

    for candidate_index in range(candidate_count):
        assignment: list[tuple[int, int]] = []

        for offset, variable in enumerate(
            normalized_variables
        ):
            shift = (
                len(normalized_variables)
                - offset
                - 1
            )

            value = (
                candidate_index
                >> shift
            ) & 1

            assignment.append(
                (
                    variable,
                    value,
                )
            )

        candidates.append(
            IRCandidate(
                index=candidate_index,
                assignment=tuple(assignment),
            )
        )

    return tuple(candidates)


def _validate_variable_partition(
    boundary_variables: tuple[int, ...],
    internal_variables: tuple[int, ...],
) -> None:
    for label, variables in (
        (
            "boundary",
            boundary_variables,
        ),
        (
            "internal",
            internal_variables,
        ),
    ):
        if len(set(variables)) != len(variables):
            raise ValueError(
                f"IR {label} variables must be unique"
            )

        if variables != tuple(sorted(variables)):
            raise ValueError(
                f"IR {label} variables must be sorted"
            )

        if any(
            variable < 0
            for variable in variables
        ):
            raise ValueError(
                f"IR {label} variables must be non-negative"
            )

    overlap = (
        set(boundary_variables)
        & set(internal_variables)
    )

    if overlap:
        raise ValueError(
            "IR boundary and internal variables must be disjoint"
        )


def _require_exact_keys(
    data: Mapping[str, Any],
    *,
    required: set[str],
    context: str,
) -> None:
    actual = set(data)

    missing = required - actual
    extra = actual - required

    if missing:
        raise ValueError(
            f"{context} is missing keys: "
            + ", ".join(sorted(missing))
        )

    if extra:
        raise ValueError(
            f"{context} contains unsupported keys: "
            + ", ".join(sorted(extra))
        )


def _require_int(
    value: Any,
    *,
    context: str,
) -> int:
    if isinstance(value, bool) or not isinstance(
        value,
        int,
    ):
        raise ValueError(
            f"{context} must be an integer"
        )

    return value


def _require_number(
    value: Any,
    *,
    context: str,
) -> float:
    if isinstance(value, bool) or not isinstance(
        value,
        (
            int,
            float,
        ),
    ):
        raise ValueError(
            f"{context} must be numeric"
        )

    return float(value)


def _require_string(
    value: Any,
    *,
    context: str,
) -> str:
    if not isinstance(value, str):
        raise ValueError(
            f"{context} must be a string"
        )

    return value


def _require_sequence(
    value: Any,
    *,
    context: str,
) -> Sequence[Any]:
    if not isinstance(
        value,
        Sequence,
    ) or isinstance(
        value,
        (
            str,
            bytes,
        ),
    ):
        raise ValueError(
            f"{context} must be a sequence"
        )

    return value


def _require_mapping_items(
    values: Iterable[Any],
    *,
    context: str,
) -> Iterable[Mapping[str, Any]]:
    for value in values:
        if not isinstance(value, Mapping):
            raise ValueError(
                f"{context} entries must be objects"
            )

        yield value
