from __future__ import annotations

import json
from pathlib import Path

import pytest

from generate_parity_benchmarks import (
    generate_benchmark,
    generate_chain,
    generate_cycle,
    generate_random,
    generate_star,
    parse_size_specification,
    write_benchmark,
)
from src.benchmark_io import load_parity_benchmark


def test_generate_chain() -> None:
    benchmark = generate_chain(6)

    assert benchmark.name == "generated-chain-6"
    assert benchmark.family == "chain"
    assert benchmark.variable_count == 6
    assert benchmark.boundary_variables == (
        0,
        5,
    )
    assert len(benchmark.constraints) == 4

    assert benchmark.constraints[0].variables == (
        0,
        1,
        2,
    )
    assert benchmark.constraints[-1].variables == (
        3,
        4,
        5,
    )


def test_generate_cycle() -> None:
    benchmark = generate_cycle(6)

    assert benchmark.name == "generated-cycle-6"
    assert benchmark.boundary_variables == (
        0,
        5,
    )
    assert len(benchmark.constraints) == 7

    assert benchmark.constraints[-1].variables == (
        0,
        5,
    )
    assert benchmark.constraints[-1].parity == 1


def test_generate_star() -> None:
    benchmark = generate_star(6)

    assert benchmark.name == "generated-star-6"
    assert benchmark.boundary_variables == (
        0,
        5,
    )
    assert len(benchmark.constraints) == 5


def test_random_generation_is_reproducible() -> None:
    first = generate_random(
        8,
        constraint_count=4,
        arity=3,
        seed=12345,
    )

    second = generate_random(
        8,
        constraint_count=4,
        arity=3,
        seed=12345,
    )

    assert first == second


def test_random_generation_changes_with_seed() -> None:
    first = generate_random(
        8,
        constraint_count=4,
        arity=3,
        seed=1,
    )

    second = generate_random(
        8,
        constraint_count=4,
        arity=3,
        seed=2,
    )

    assert first != second


def test_generated_benchmark_round_trip(
    tmp_path: Path,
) -> None:
    generated = generate_chain(7)
    output_path = tmp_path / "chain.json"

    write_benchmark(
        generated,
        output_path,
    )

    loaded = load_parity_benchmark(
        output_path
    )

    assert loaded.name == generated.name
    assert loaded.instance.variables == tuple(
        range(7)
    )
    assert loaded.instance.boundary_variables == (
        0,
        6,
    )


def test_generated_json_contains_metadata(
    tmp_path: Path,
) -> None:
    benchmark = generate_random(
        6,
        constraint_count=4,
        arity=3,
        seed=17,
    )

    output_path = tmp_path / "random.json"

    write_benchmark(
        benchmark,
        output_path,
    )

    raw = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert raw["schema_version"] == 1
    assert raw["metadata"]["family"] == "random"
    assert raw["metadata"]["variable_count"] == 6
    assert raw["metadata"]["seed"] == 17


@pytest.mark.parametrize(
    ("specification", "expected"),
    [
        ("8", [8]),
        ("4:10:2", [4, 6, 8, 10]),
        ("4:9:2", [4, 6, 8, 9]),
    ],
)
def test_parse_size_specification(
    specification: str,
    expected: list[int],
) -> None:
    assert parse_size_specification(
        specification
    ) == expected


@pytest.mark.parametrize(
    "specification",
    [
        "",
        "0",
        "4:10",
        "10:4:1",
        "4:10:0",
    ],
)
def test_invalid_size_specification_is_rejected(
    specification: str,
) -> None:
    with pytest.raises(ValueError):
        parse_size_specification(
            specification
        )


@pytest.mark.parametrize(
    ("family", "variable_count"),
    [
        ("chain", 2),
        ("cycle", 3),
        ("star", 3),
    ],
)
def test_family_minimum_sizes_are_enforced(
    family: str,
    variable_count: int,
) -> None:
    with pytest.raises(ValueError):
        generate_benchmark(
            family,
            variable_count,
        )


def test_random_constraint_count_is_bounded() -> None:
    with pytest.raises(ValueError):
        generate_random(
            4,
            constraint_count=100,
            arity=3,
            seed=1,
        )


def test_unknown_family_is_rejected() -> None:
    with pytest.raises(ValueError):
        generate_benchmark(
            "unknown",
            6,
        )


@pytest.mark.parametrize(
    "variable_count",
    [
        4,
        6,
        8,
        10,
    ],
)
def test_random_generation_includes_both_boundaries(
    variable_count: int,
) -> None:
    benchmark = generate_random(
        variable_count,
        constraint_count=4,
        arity=3,
        seed=20260806,
    )

    constrained_variables = {
        variable
        for constraint in benchmark.constraints
        for variable in constraint.variables
    }

    assert 0 in constrained_variables
    assert variable_count - 1 in constrained_variables


@pytest.mark.parametrize(
    "variable_count",
    [
        4,
        6,
        8,
    ],
)
def test_generated_random_benchmark_loads_successfully(
    tmp_path: Path,
    variable_count: int,
) -> None:
    benchmark = generate_random(
        variable_count,
        constraint_count=4,
        arity=3,
        seed=20260806,
    )

    output_path = (
        tmp_path
        / f"random-{variable_count}.json"
    )

    write_benchmark(
        benchmark,
        output_path,
    )

    loaded = load_parity_benchmark(
        output_path
    )

    assert loaded.instance.boundary_variables == (
        0,
        variable_count - 1,
    )

    assert loaded.instance.variables == tuple(
        range(variable_count)
    )


@pytest.mark.parametrize(
    ("variable_count", "constraint_count", "arity"),
    [
        (4, 4, 3),
        (6, 4, 3),
        (8, 4, 3),
        (10, 4, 3),
    ],
)
def test_random_generation_covers_every_declared_variable(
    variable_count: int,
    constraint_count: int,
    arity: int,
) -> None:
    benchmark = generate_random(
        variable_count,
        constraint_count=constraint_count,
        arity=arity,
        seed=20260806,
    )

    constrained_variables = {
        variable
        for constraint in benchmark.constraints
        for variable in constraint.variables
    }

    assert constrained_variables == set(
        range(variable_count)
    )


def test_random_generation_rejects_insufficient_constraint_count() -> None:
    with pytest.raises(ValueError):
        generate_random(
            10,
            constraint_count=2,
            arity=3,
            seed=20260806,
        )
