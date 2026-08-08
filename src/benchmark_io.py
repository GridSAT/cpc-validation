from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from src.compiler import (
    ParityConstraint,
    ParityInstance,
)


BENCHMARK_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ParityBenchmark:
    name: str
    description: str
    instance: ParityInstance
    source_path: Path


def load_parity_benchmark(
    path: str | Path,
) -> ParityBenchmark:
    source_path = Path(path)

    if not source_path.exists():
        raise FileNotFoundError(
            f"benchmark file does not exist: {source_path}"
        )

    try:
        raw = json.loads(
            source_path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            f"invalid benchmark JSON in {source_path}: {error}"
        ) from error

    if not isinstance(raw, dict):
        raise ValueError(
            "benchmark root must be a JSON object"
        )

    schema_version = _required_integer(
        raw,
        "schema_version",
    )

    if schema_version != BENCHMARK_SCHEMA_VERSION:
        raise ValueError(
            "unsupported benchmark schema version: "
            f"{schema_version}; expected "
            f"{BENCHMARK_SCHEMA_VERSION}"
        )

    name = _required_string(
        raw,
        "name",
    )

    description = _optional_string(
        raw,
        "description",
        default="",
    )

    boundary_variables = tuple(
        _required_integer_list(
            raw,
            "boundary_variables",
        )
    )

    raw_constraints = raw.get("constraints")

    if not isinstance(raw_constraints, list):
        raise ValueError(
            "benchmark field 'constraints' must be a JSON array"
        )

    constraints: list[ParityConstraint] = []

    for index, raw_constraint in enumerate(raw_constraints):
        if not isinstance(raw_constraint, dict):
            raise ValueError(
                f"constraint {index} must be a JSON object"
            )

        variables = tuple(
            _required_integer_list(
                raw_constraint,
                "variables",
                context=f"constraint {index}",
            )
        )

        parity = _required_integer(
            raw_constraint,
            "parity",
            context=f"constraint {index}",
        )

        constraints.append(
            ParityConstraint(
                variables=variables,
                parity=parity,
            )
        )

    instance = ParityInstance(
        constraints=tuple(constraints),
        boundary_variables=boundary_variables,
    )

    return ParityBenchmark(
        name=name,
        description=description,
        instance=instance,
        source_path=source_path,
    )


def load_boundary_values(
    text: str,
    boundary_variables: tuple[int, ...],
) -> dict[int, int]:
    """
    Parse boundary values such as:

        x0=0,x3=1

    Variable names may also be supplied without the leading x:

        0=0,3=1
    """
    if not text.strip():
        raise ValueError(
            "boundary assignment may not be empty"
        )

    values: dict[int, int] = {}

    for item in text.split(","):
        item = item.strip()

        if not item:
            raise ValueError(
                "empty boundary-assignment item"
            )

        if "=" not in item:
            raise ValueError(
                f"invalid boundary assignment: {item!r}"
            )

        name, raw_value = (
            part.strip()
            for part in item.split("=", 1)
        )

        if name.startswith("x"):
            name = name[1:]

        try:
            variable = int(name)
        except ValueError as error:
            raise ValueError(
                f"invalid boundary variable: {name!r}"
            ) from error

        try:
            value = int(raw_value)
        except ValueError as error:
            raise ValueError(
                f"invalid boundary value: {raw_value!r}"
            ) from error

        if value not in (0, 1):
            raise ValueError(
                f"x{variable} must be 0 or 1"
            )

        if variable in values:
            raise ValueError(
                f"duplicate boundary assignment for x{variable}"
            )

        values[variable] = value

    required = set(boundary_variables)
    supplied = set(values)

    missing = required - supplied
    unexpected = supplied - required

    if missing:
        raise ValueError(
            "missing boundary assignments for: "
            + ", ".join(
                f"x{variable}"
                for variable in sorted(missing)
            )
        )

    if unexpected:
        raise ValueError(
            "unexpected boundary assignments for: "
            + ", ".join(
                f"x{variable}"
                for variable in sorted(unexpected)
            )
        )

    return values


def benchmark_to_dict(
    benchmark: ParityBenchmark,
) -> dict[str, Any]:
    return {
        "schema_version": BENCHMARK_SCHEMA_VERSION,
        "name": benchmark.name,
        "description": benchmark.description,
        "boundary_variables": list(
            benchmark.instance.boundary_variables
        ),
        "constraints": [
            {
                "variables": list(
                    constraint.variables
                ),
                "parity": constraint.parity,
            }
            for constraint in benchmark.instance.constraints
        ],
    }


def _required_string(
    mapping: Mapping[str, Any],
    key: str,
    *,
    context: str = "benchmark",
) -> str:
    value = mapping.get(key)

    if not isinstance(value, str):
        raise ValueError(
            f"{context} field {key!r} must be a string"
        )

    if not value.strip():
        raise ValueError(
            f"{context} field {key!r} may not be empty"
        )

    return value


def _optional_string(
    mapping: Mapping[str, Any],
    key: str,
    *,
    default: str,
) -> str:
    value = mapping.get(key, default)

    if not isinstance(value, str):
        raise ValueError(
            f"benchmark field {key!r} must be a string"
        )

    return value


def _required_integer(
    mapping: Mapping[str, Any],
    key: str,
    *,
    context: str = "benchmark",
) -> int:
    value = mapping.get(key)

    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            f"{context} field {key!r} must be an integer"
        )

    return value


def _required_integer_list(
    mapping: Mapping[str, Any],
    key: str,
    *,
    context: str = "benchmark",
) -> list[int]:
    value = mapping.get(key)

    if not isinstance(value, list):
        raise ValueError(
            f"{context} field {key!r} must be a JSON array"
        )

    result: list[int] = []

    for index, item in enumerate(value):
        if isinstance(item, bool) or not isinstance(item, int):
            raise ValueError(
                f"{context} field {key!r} item {index} "
                "must be an integer"
            )

        result.append(item)

    return result
