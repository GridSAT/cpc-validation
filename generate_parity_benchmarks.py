from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from math import comb
from pathlib import Path


SCHEMA_VERSION = 1
SUPPORTED_FAMILIES = (
    "chain",
    "cycle",
    "star",
    "random",
)


@dataclass(frozen=True)
class GeneratedConstraint:
    variables: tuple[int, ...]
    parity: int

    def to_dict(self) -> dict[str, object]:
        return {
            "variables": list(self.variables),
            "parity": self.parity,
        }


@dataclass(frozen=True)
class GeneratedBenchmark:
    name: str
    description: str
    boundary_variables: tuple[int, ...]
    constraints: tuple[GeneratedConstraint, ...]
    family: str
    variable_count: int
    seed: int | None

    def to_dict(self) -> dict[str, object]:
        metadata: dict[str, object] = {
            "generator": "generate_parity_benchmarks.py",
            "family": self.family,
            "variable_count": self.variable_count,
        }

        if self.seed is not None:
            metadata["seed"] = self.seed

        return {
            "schema_version": SCHEMA_VERSION,
            "name": self.name,
            "description": self.description,
            "boundary_variables": list(self.boundary_variables),
            "constraints": [
                constraint.to_dict()
                for constraint in self.constraints
            ],
            "metadata": metadata,
        }


def generate_chain(
    variable_count: int,
) -> GeneratedBenchmark:
    _validate_minimum_variables(
        variable_count,
        minimum=3,
        family="chain",
    )

    constraints = tuple(
        GeneratedConstraint(
            variables=(
                index,
                index + 1,
                index + 2,
            ),
            parity=index % 2,
        )
        for index in range(variable_count - 2)
    )

    return GeneratedBenchmark(
        name=f"generated-chain-{variable_count}",
        description=(
            f"Generated overlapping parity chain with "
            f"{variable_count} variables."
        ),
        boundary_variables=(
            0,
            variable_count - 1,
        ),
        constraints=constraints,
        family="chain",
        variable_count=variable_count,
        seed=None,
    )


def generate_cycle(
    variable_count: int,
) -> GeneratedBenchmark:
    _validate_minimum_variables(
        variable_count,
        minimum=4,
        family="cycle",
    )

    sliding_constraints = tuple(
        GeneratedConstraint(
            variables=(
                index,
                (index + 1) % variable_count,
                (index + 2) % variable_count,
            ),
            parity=index % 2,
        )
        for index in range(variable_count)
    )

    boundary_constraint = GeneratedConstraint(
        variables=(
            0,
            variable_count - 1,
        ),
        parity=1,
    )

    return GeneratedBenchmark(
        name=f"generated-cycle-{variable_count}",
        description=(
            f"Generated closed parity cycle with "
            f"{variable_count} variables."
        ),
        boundary_variables=(
            0,
            variable_count - 1,
        ),
        constraints=(
            *sliding_constraints,
            boundary_constraint,
        ),
        family="cycle",
        variable_count=variable_count,
        seed=None,
    )


def generate_star(
    variable_count: int,
) -> GeneratedBenchmark:
    _validate_minimum_variables(
        variable_count,
        minimum=4,
        family="star",
    )

    constraints = [
        GeneratedConstraint(
            variables=(
                0,
                1,
                index,
            ),
            parity=index % 2,
        )
        for index in range(2, variable_count)
    ]

    constraints.append(
        GeneratedConstraint(
            variables=(
                1,
                variable_count - 1,
            ),
            parity=1,
        )
    )

    return GeneratedBenchmark(
        name=f"generated-star-{variable_count}",
        description=(
            f"Generated parity star with {variable_count} variables "
            "and center variable x1."
        ),
        boundary_variables=(
            0,
            variable_count - 1,
        ),
        constraints=tuple(constraints),
        family="star",
        variable_count=variable_count,
        seed=None,
    )


def generate_random(
    variable_count: int,
    *,
    constraint_count: int,
    arity: int,
    seed: int,
) -> GeneratedBenchmark:
    _validate_minimum_variables(
        variable_count,
        minimum=3,
        family="random",
    )

    if arity < 2:
        raise ValueError(
            "random constraint arity must be at least 2"
        )

    if arity > variable_count:
        raise ValueError(
            "random constraint arity may not exceed variable count"
        )

    if constraint_count <= 0:
        raise ValueError(
            "random constraint count must be greater than zero"
        )

    maximum_unique_constraints = comb(
        variable_count,
        arity,
    )

    if constraint_count > maximum_unique_constraints:
        raise ValueError(
            "requested random constraint count exceeds the number "
            "of unique variable combinations"
        )

    generator = random.Random(seed)

    # Construct a deterministic coverage set so every declared variable
    # occurs in at least one constraint. This keeps the requested variable
    # count equal to the loaded and compiled variable count.
    coverage_sets: set[tuple[int, ...]] = set()

    uncovered = set(range(variable_count))

    while uncovered:
        first = min(uncovered)

        selected = [first]

        remaining_uncovered = sorted(
            uncovered - {first}
        )

        for variable in remaining_uncovered:
            if len(selected) >= arity:
                break

            selected.append(variable)

        if len(selected) < arity:
            remaining_variables = [
                variable
                for variable in range(variable_count)
                if variable not in selected
            ]

            for variable in remaining_variables:
                if len(selected) >= arity:
                    break

                selected.append(variable)

        if len(selected) != arity:
            raise ValueError(
                "could not construct full-variable coverage constraints"
            )

        variable_set = tuple(sorted(selected))
        coverage_sets.add(variable_set)
        uncovered.difference_update(variable_set)

    if len(coverage_sets) > constraint_count:
        raise ValueError(
            "requested random constraint count is too small to cover "
            "every variable at the selected arity"
        )

    variable_sets: set[tuple[int, ...]] = set(
        coverage_sets
    )

    while len(variable_sets) < constraint_count:
        variables = tuple(
            sorted(
                generator.sample(
                    range(variable_count),
                    arity,
                )
            )
        )
        variable_sets.add(variables)

    ordered_variable_sets = sorted(variable_sets)

    constraints = tuple(
        GeneratedConstraint(
            variables=variables,
            parity=generator.randint(0, 1),
        )
        for variables in ordered_variable_sets
    )

    return GeneratedBenchmark(
        name=(
            f"generated-random-{variable_count}-"
            f"{constraint_count}-seed-{seed}"
        ),
        description=(
            f"Generated random parity system with {variable_count} "
            f"variables, {constraint_count} constraints, arity {arity}, "
            f"and seed {seed}."
        ),
        boundary_variables=(
            0,
            variable_count - 1,
        ),
        constraints=constraints,
        family="random",
        variable_count=variable_count,
        seed=seed,
    )


def generate_benchmark(
    family: str,
    variable_count: int,
    *,
    constraint_count: int | None = None,
    arity: int = 3,
    seed: int = 20260806,
) -> GeneratedBenchmark:
    if family == "chain":
        return generate_chain(variable_count)

    if family == "cycle":
        return generate_cycle(variable_count)

    if family == "star":
        return generate_star(variable_count)

    if family == "random":
        resolved_constraint_count = (
            constraint_count
            if constraint_count is not None
            else max(1, variable_count - 2)
        )

        return generate_random(
            variable_count,
            constraint_count=resolved_constraint_count,
            arity=arity,
            seed=seed,
        )

    raise ValueError(
        f"unsupported benchmark family: {family!r}"
    )


def write_benchmark(
    benchmark: GeneratedBenchmark,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            benchmark.to_dict(),
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def parse_size_specification(
    text: str,
) -> list[int]:
    stripped = text.strip()

    if not stripped:
        raise ValueError(
            "size specification may not be empty"
        )

    if ":" not in stripped:
        value = int(stripped)

        if value <= 0:
            raise ValueError(
                "variable count must be greater than zero"
            )

        return [value]

    parts = stripped.split(":")

    if len(parts) != 3:
        raise ValueError(
            "size range must use START:STOP:STEP"
        )

    start, stop, step = (
        int(part)
        for part in parts
    )

    if start <= 0:
        raise ValueError(
            "size-range start must be greater than zero"
        )

    if stop < start:
        raise ValueError(
            "size-range stop must be greater than or equal to start"
        )

    if step <= 0:
        raise ValueError(
            "size-range step must be greater than zero"
        )

    values = list(
        range(
            start,
            stop + 1,
            step,
        )
    )

    if not values:
        raise ValueError(
            "size range produced no values"
        )

    if values[-1] != stop:
        values.append(stop)

    return values


def _validate_minimum_variables(
    variable_count: int,
    *,
    minimum: int,
    family: str,
) -> None:
    if variable_count < minimum:
        raise ValueError(
            f"{family} family requires at least "
            f"{minimum} variables"
        )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate reproducible parity benchmark JSON files."
        )
    )

    parser.add_argument(
        "--family",
        choices=SUPPORTED_FAMILIES,
        required=True,
    )

    parser.add_argument(
        "--variables",
        required=True,
        help=(
            "Variable count or inclusive START:STOP:STEP range, "
            "for example 8 or 4:12:2."
        ),
    )

    parser.add_argument(
        "--constraints",
        type=int,
        default=None,
    )

    parser.add_argument(
        "--arity",
        type=int,
        default=3,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=20260806,
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=Path("benchmarks/generated"),
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    variable_counts = parse_size_specification(
        arguments.variables
    )

    print("CPC parity benchmark generator")
    print()
    print(f"Family:             {arguments.family}")
    print(
        "Variable counts:    "
        + ", ".join(
            str(value)
            for value in variable_counts
        )
    )

    if arguments.family == "random":
        print(f"Seed:               {arguments.seed}")
        print(f"Constraint arity:   {arguments.arity}")

    print()

    generated_count = 0

    for variable_count in variable_counts:
        benchmark = generate_benchmark(
            arguments.family,
            variable_count,
            constraint_count=arguments.constraints,
            arity=arguments.arity,
            seed=arguments.seed,
        )

        output_path = (
            arguments.output_directory
            / f"{benchmark.name}.json"
        )

        write_benchmark(
            benchmark,
            output_path,
        )

        generated_count += 1

        print(
            f"{benchmark.name}: "
            f"variables={benchmark.variable_count} "
            f"constraints={len(benchmark.constraints)} "
            f"boundary={len(benchmark.boundary_variables)} "
            f"output={output_path}"
        )

    print()
    print(f"Generated benchmarks: {generated_count}")
    print("Parity benchmark generation: PASS")


if __name__ == "__main__":
    main()
