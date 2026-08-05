# python reference.py

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable, Mapping, Sequence


Bit = int


@dataclass(frozen=True)
class XorConstraint:
    """Constraint of the form XOR(variables) = parity."""

    variables: tuple[int, ...]
    parity: Bit

    def __post_init__(self) -> None:
        if not self.variables:
            raise ValueError("An XOR constraint must contain at least one variable.")
        if self.parity not in (0, 1):
            raise ValueError("Parity must be 0 or 1.")

    def is_satisfied(self, assignment: Sequence[Bit]) -> bool:
        value = 0

        for variable in self.variables:
            value ^= assignment[variable]

        return value == self.parity


@dataclass(frozen=True)
class XorSystem:
    """
    Finite XOR constraint system.

    Variable indices are zero-based:
        x0, x1, ..., x(n-1)
    """

    variable_count: int
    constraints: tuple[XorConstraint, ...]

    def __post_init__(self) -> None:
        if self.variable_count < 1:
            raise ValueError("variable_count must be positive.")

        for constraint in self.constraints:
            for variable in constraint.variables:
                if variable < 0 or variable >= self.variable_count:
                    raise ValueError(
                        f"Variable index {variable} is outside "
                        f"0..{self.variable_count - 1}."
                    )

    def satisfies(self, assignment: Sequence[Bit]) -> bool:
        if len(assignment) != self.variable_count:
            raise ValueError(
                f"Expected {self.variable_count} bits, got {len(assignment)}."
            )

        if any(bit not in (0, 1) for bit in assignment):
            raise ValueError("Assignments must contain only 0 and 1.")

        return all(
            constraint.is_satisfied(assignment)
            for constraint in self.constraints
        )

    def completions(
        self,
        boundary: Mapping[int, Bit],
    ) -> list[tuple[Bit, ...]]:
        """
        Return all full assignments extending the supplied boundary condition
        and satisfying the complete XOR system.
        """

        self._validate_boundary(boundary)

        free_variables = [
            variable
            for variable in range(self.variable_count)
            if variable not in boundary
        ]

        satisfying_assignments: list[tuple[Bit, ...]] = []

        for free_values in product((0, 1), repeat=len(free_variables)):
            assignment = [0] * self.variable_count

            for variable, value in boundary.items():
                assignment[variable] = value

            for variable, value in zip(free_variables, free_values):
                assignment[variable] = value

            assignment_tuple = tuple(assignment)

            if self.satisfies(assignment_tuple):
                satisfying_assignments.append(assignment_tuple)

        return satisfying_assignments

    def evaluate(self, boundary: Mapping[int, Bit]) -> Bit:
        """
        Exact continuation function:

            Eval_X(boundary) = 1

        iff the supplied boundary condition has at least one satisfying
        extension.
        """

        return int(bool(self.completions(boundary)))

    def continuation_table(
        self,
        boundary_variables: Iterable[int],
    ) -> list[dict[str, object]]:
        boundary_variables = tuple(boundary_variables)

        if len(set(boundary_variables)) != len(boundary_variables):
            raise ValueError("Boundary variables must be distinct.")

        for variable in boundary_variables:
            if variable < 0 or variable >= self.variable_count:
                raise ValueError(f"Invalid boundary variable x{variable}.")

        rows: list[dict[str, object]] = []

        for values in product((0, 1), repeat=len(boundary_variables)):
            boundary = dict(zip(boundary_variables, values))
            completions = self.completions(boundary)

            rows.append(
                {
                    "boundary": boundary,
                    "evaluation": int(bool(completions)),
                    "completion_count": len(completions),
                    "completions": completions,
                }
            )

        return rows

    def _validate_boundary(self, boundary: Mapping[int, Bit]) -> None:
        for variable, value in boundary.items():
            if variable < 0 or variable >= self.variable_count:
                raise ValueError(f"Invalid boundary variable x{variable}.")
            if value not in (0, 1):
                raise ValueError(
                    f"Boundary value for x{variable} must be 0 or 1."
                )


def build_initial_system() -> XorSystem:
    """
    Initial four-variable parity instance:

        x0 XOR x1 XOR x2 = 0
        x1 XOR x2 XOR x3 = 1

    The first Stage-0 boundary interface fixes x0 and x3.
    Variables x1 and x2 remain internal.
    """

    return XorSystem(
        variable_count=4,
        constraints=(
            XorConstraint((0, 1, 2), 0),
            XorConstraint((1, 2, 3), 1),
        ),
    )


def main() -> None:
    system = build_initial_system()
    table = system.continuation_table(boundary_variables=(0, 3))

    print("CPC reference continuation table")
    print()
    print("Constraints:")
    print("  x0 XOR x1 XOR x2 = 0")
    print("  x1 XOR x2 XOR x3 = 1")
    print()
    print("Boundary variables: x0, x3")
    print()

    for row in table:
        boundary = row["boundary"]
        evaluation = row["evaluation"]
        count = row["completion_count"]
        completions = row["completions"]

        print(
            f"x0={boundary[0]} x3={boundary[3]} "
            f"-> Eval={evaluation}, completions={count}: {completions}"
        )


if __name__ == "__main__":
    main()