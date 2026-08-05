from __future__ import annotations

import pytest

from src.benchmark_io import (
    load_parity_benchmark,
)
from src.compiler import (
    ParityConstraint,
)
from src.generic_reference import (
    constraint_is_satisfied,
    enumerate_boundary_assignments,
    evaluate_parity_instance,
)


def test_default_xor_reference_table() -> None:
    benchmark = load_parity_benchmark(
        "benchmarks/default_xor.json"
    )

    expected = {
        (0, 0): (0, 0),
        (0, 1): (1, 2),
        (1, 0): (1, 2),
        (1, 1): (0, 0),
    }

    for x0 in (0, 1):
        for x3 in (0, 1):
            result = evaluate_parity_instance(
                benchmark.instance,
                {
                    0: x0,
                    3: x3,
                },
            )

            expected_value, expected_count = (
                expected[(x0, x3)]
            )

            assert (
                result.continuation_value
                == expected_value
            )
            assert (
                result.completion_count
                == expected_count
            )


def test_parity_chain_reference_table() -> None:
    benchmark = load_parity_benchmark(
        "benchmarks/parity_chain_5.json"
    )

    results = {}

    for boundary in enumerate_boundary_assignments(
        benchmark.instance.boundary_variables
    ):
        result = evaluate_parity_instance(
            benchmark.instance,
            boundary,
        )

        key = tuple(
            boundary[variable]
            for variable in (
                benchmark.instance.boundary_variables
            )
        )

        results[key] = (
            result.continuation_value,
            result.completion_count,
        )

    assert results == {
        (0, 0): (1, 1),
        (0, 1): (1, 1),
        (1, 0): (1, 1),
        (1, 1): (1, 1),
    }


def test_boundary_assignment_enumeration() -> None:
    assignments = list(
        enumerate_boundary_assignments((0, 3))
    )

    assert assignments == [
        {0: 0, 3: 0},
        {0: 0, 3: 1},
        {0: 1, 3: 0},
        {0: 1, 3: 1},
    ]


def test_constraint_satisfaction() -> None:
    constraint = ParityConstraint(
        variables=(0, 1, 2),
        parity=1,
    )

    assert constraint_is_satisfied(
        constraint,
        {
            0: 0,
            1: 0,
            2: 1,
        },
    )

    assert not constraint_is_satisfied(
        constraint,
        {
            0: 0,
            1: 0,
            2: 0,
        },
    )


def test_constraint_requires_complete_assignment() -> None:
    constraint = ParityConstraint(
        variables=(0, 1),
        parity=0,
    )

    with pytest.raises(ValueError):
        constraint_is_satisfied(
            constraint,
            {
                0: 0,
            },
        )


def test_reference_boundary_values_must_match_instance() -> None:
    benchmark = load_parity_benchmark(
        "benchmarks/default_xor.json"
    )

    with pytest.raises(ValueError):
        evaluate_parity_instance(
            benchmark.instance,
            {
                0: 0,
            },
        )

    with pytest.raises(ValueError):
        evaluate_parity_instance(
            benchmark.instance,
            {
                0: 0,
                3: 1,
                7: 0,
            },
        )

    with pytest.raises(ValueError):
        evaluate_parity_instance(
            benchmark.instance,
            {
                0: 0,
                3: 2,
            },
        )
