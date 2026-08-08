from __future__ import annotations

import csv
from pathlib import Path

import pytest

from run_scaling_study import (
    grouped_results,
    parse_family_list,
    random_constraint_count,
    run_scaling_study,
    write_summary_csv,
)


def test_parse_family_list() -> None:
    assert parse_family_list(
        "chain,cycle,star,random"
    ) == (
        "chain",
        "cycle",
        "star",
        "random",
    )


@pytest.mark.parametrize(
    "text",
    [
        "",
        "unknown",
        "chain,chain",
    ],
)
def test_invalid_family_list_is_rejected(
    text: str,
) -> None:
    with pytest.raises(ValueError):
        parse_family_list(text)


@pytest.mark.parametrize(
    ("variables", "arity", "requested", "expected"),
    [
        (4, 3, None, 4),
        (8, 3, None, 4),
        (13, 3, None, 5),
        (8, 3, 6, 6),
    ],
)
def test_random_constraint_count(
    variables: int,
    arity: int,
    requested: int | None,
    expected: int,
) -> None:
    assert random_constraint_count(
        variables,
        arity,
        requested,
    ) == expected


def test_random_constraint_count_rejects_insufficient_coverage() -> None:
    with pytest.raises(ValueError):
        random_constraint_count(
            10,
            3,
            2,
        )


def test_small_scaling_study(
    tmp_path: Path,
) -> None:
    results = run_scaling_study(
        families=(
            "chain",
            "star",
        ),
        variable_counts=(
            4,
        ),
        seed=20260806,
        random_constraints=None,
        random_arity=3,
        supply_voltage=5.0,
        resistance_kohm=10.0,
        capacitance_uf=1.0,
        threshold_voltage=2.5,
        end_time_ms=50.0,
        working_directory=(
            tmp_path
            / "work"
        ),
    )

    assert len(results) == 2

    for result in results:
        assert result.variable_count == 4
        assert result.internal_variable_count == 2
        assert result.candidate_count == 4
        assert result.behavioral_source_count == 5
        assert result.boundary_simulations == 4
        assert result.passed == 4
        assert result.failed == 0
        assert result.success_rate == 1.0
        assert result.mean_netlist_bytes > 0
        assert result.mean_compilation_seconds >= 0.0
        assert result.mean_simulation_seconds > 0.0


def test_grouped_results_are_sorted(
    tmp_path: Path,
) -> None:
    results = run_scaling_study(
        families=(
            "chain",
        ),
        variable_counts=(
            6,
            4,
        ),
        seed=20260806,
        random_constraints=None,
        random_arity=3,
        supply_voltage=5.0,
        resistance_kohm=10.0,
        capacitance_uf=1.0,
        threshold_voltage=2.5,
        end_time_ms=50.0,
        working_directory=(
            tmp_path
            / "work"
        ),
    )

    grouped = grouped_results(results)

    assert [
        result.variable_count
        for result in grouped["chain"]
    ] == [
        4,
        6,
    ]


def test_summary_csv(
    tmp_path: Path,
) -> None:
    results = run_scaling_study(
        families=(
            "chain",
        ),
        variable_counts=(
            4,
        ),
        seed=20260806,
        random_constraints=None,
        random_arity=3,
        supply_voltage=5.0,
        resistance_kohm=10.0,
        capacitance_uf=1.0,
        threshold_voltage=2.5,
        end_time_ms=50.0,
        working_directory=(
            tmp_path
            / "work"
        ),
    )

    output_path = (
        tmp_path
        / "scaling.csv"
    )

    write_summary_csv(
        output_path,
        results,
    )

    rows = list(
        csv.DictReader(
            output_path.open(
                newline="",
                encoding="utf-8",
            )
        )
    )

    assert len(rows) == 1
    assert rows[0]["family"] == "chain"
    assert rows[0]["variable_count"] == "4"
    assert rows[0]["candidate_count"] == "4"
    assert rows[0]["passed"] == "4"
    assert rows[0]["failed"] == "0"
