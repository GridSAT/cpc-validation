from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable, Mapping, Sequence

from src.compiler import (
    ParityConstraint,
    ParityInstance,
)


@dataclass(frozen=True)
class CompletionResult:
    boundary_values: tuple[tuple[int, int], ...]
    continuation_value: int
    completion_count: int
    completions: tuple[tuple[tuple[int, int], ...], ...]


def evaluate_parity_instance(
    instance: ParityInstance,
    boundary_values: Mapping[int, int],
) -> CompletionResult:
    """
    Independently evaluate whether a parity instance has at least one internal
    completion for the admitted boundary assignment.

    This function does not call the SPICE compiler and does not inspect any
    generated netlist.
    """
    normalized_boundary = _validate_boundary_values(
        instance,
        boundary_values,
    )

    completions: list[tuple[tuple[int, int], ...]] = []

    for internal_assignment in enumerate_internal_assignments(
        instance.internal_variables
    ):
        complete_assignment = {
            **normalized_boundary,
            **internal_assignment,
        }

        if all(
            constraint_is_satisfied(
                constraint,
                complete_assignment,
            )
            for constraint in instance.constraints
        ):
            completions.append(
                tuple(
                    sorted(
                        internal_assignment.items()
                    )
                )
            )

    completion_tuple = tuple(completions)

    return CompletionResult(
        boundary_values=tuple(
            sorted(
                normalized_boundary.items()
            )
        ),
        continuation_value=int(bool(completion_tuple)),
        completion_count=len(completion_tuple),
        completions=completion_tuple,
    )


def enumerate_boundary_assignments(
    boundary_variables: Sequence[int],
) -> Iterable[dict[int, int]]:
    for values in product(
        (0, 1),
        repeat=len(boundary_variables),
    ):
        yield dict(
            zip(
                boundary_variables,
                values,
                strict=True,
            )
        )


def enumerate_internal_assignments(
    internal_variables: Sequence[int],
) -> Iterable[dict[int, int]]:
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


def constraint_is_satisfied(
    constraint: ParityConstraint,
    assignment: Mapping[int, int],
) -> bool:
    parity = 0

    for variable in constraint.variables:
        if variable not in assignment:
            raise ValueError(
                f"assignment is missing x{variable}"
            )

        value = assignment[variable]
        _validate_bit(
            value,
            f"x{variable}",
        )

        parity ^= value

    return parity == constraint.parity


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
