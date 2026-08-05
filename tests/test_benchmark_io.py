from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.benchmark_io import (
    BENCHMARK_SCHEMA_VERSION,
    benchmark_to_dict,
    load_boundary_values,
    load_parity_benchmark,
)


def test_load_default_xor_benchmark() -> None:
    benchmark = load_parity_benchmark(
        Path("benchmarks/default_xor.json")
    )

    assert benchmark.name == "default-xor"
    assert benchmark.instance.variables == (
        0,
        1,
        2,
        3,
    )
    assert benchmark.instance.boundary_variables == (
        0,
        3,
    )
    assert benchmark.instance.internal_variables == (
        1,
        2,
    )
    assert len(benchmark.instance.constraints) == 2


def test_load_parity_chain_benchmark() -> None:
    benchmark = load_parity_benchmark(
        Path("benchmarks/parity_chain_5.json")
    )

    assert benchmark.name == "parity-chain-5"
    assert benchmark.instance.variables == (
        0,
        1,
        2,
        3,
        4,
    )
    assert benchmark.instance.boundary_variables == (
        0,
        4,
    )
    assert benchmark.instance.internal_variables == (
        1,
        2,
        3,
    )
    assert len(benchmark.instance.constraints) == 3


def test_boundary_parser_accepts_prefixed_names() -> None:
    values = load_boundary_values(
        "x0=0,x3=1",
        (0, 3),
    )

    assert values == {
        0: 0,
        3: 1,
    }


def test_boundary_parser_accepts_numeric_names() -> None:
    values = load_boundary_values(
        "0=1,3=0",
        (0, 3),
    )

    assert values == {
        0: 1,
        3: 0,
    }


@pytest.mark.parametrize(
    "text",
    [
        "",
        "x0",
        "x0=2,x3=0",
        "x0=0,x0=1,x3=0",
        "x0=0",
        "x0=0,x3=1,x7=0",
        "foo=0,x3=1",
    ],
)
def test_invalid_boundary_assignment_is_rejected(
    text: str,
) -> None:
    with pytest.raises(ValueError):
        load_boundary_values(
            text,
            (0, 3),
        )


def test_benchmark_round_trip_dictionary() -> None:
    benchmark = load_parity_benchmark(
        Path("benchmarks/default_xor.json")
    )

    encoded = benchmark_to_dict(
        benchmark
    )

    assert encoded["schema_version"] == (
        BENCHMARK_SCHEMA_VERSION
    )
    assert encoded["name"] == "default-xor"
    assert encoded["boundary_variables"] == [
        0,
        3,
    ]
    assert encoded["constraints"] == [
        {
            "variables": [0, 1, 2],
            "parity": 0,
        },
        {
            "variables": [1, 2, 3],
            "parity": 1,
        },
    ]


def test_missing_benchmark_file_is_rejected(
    tmp_path: Path,
) -> None:
    with pytest.raises(FileNotFoundError):
        load_parity_benchmark(
            tmp_path / "missing.json"
        )


def test_invalid_json_is_rejected(
    tmp_path: Path,
) -> None:
    path = tmp_path / "invalid.json"
    path.write_text(
        "{not valid json",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_parity_benchmark(path)


def test_unsupported_schema_version_is_rejected(
    tmp_path: Path,
) -> None:
    path = tmp_path / "future.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 999,
                "name": "future",
                "boundary_variables": [0],
                "constraints": [
                    {
                        "variables": [0],
                        "parity": 0,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_parity_benchmark(path)


def test_invalid_constraint_shape_is_rejected(
    tmp_path: Path,
) -> None:
    path = tmp_path / "invalid-constraint.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "name": "invalid",
                "boundary_variables": [0],
                "constraints": [
                    "not-an-object"
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_parity_benchmark(path)


def test_discover_benchmark_directory() -> None:
    from validate_benchmarks import discover_benchmark_paths

    paths = discover_benchmark_paths(
        [
            Path("benchmarks"),
        ]
    )

    assert paths == [
        Path("benchmarks/default_xor.json"),
        Path("benchmarks/parity_chain_5.json"),
        Path("benchmarks/parity_cycle_6.json"),
    ]


def test_discovery_deduplicates_explicit_and_directory_paths() -> None:
    from validate_benchmarks import discover_benchmark_paths

    paths = discover_benchmark_paths(
        [
            Path("benchmarks"),
            Path("benchmarks/default_xor.json"),
        ]
    )

    assert paths == [
        Path("benchmarks/default_xor.json"),
        Path("benchmarks/parity_chain_5.json"),
        Path("benchmarks/parity_cycle_6.json"),
    ]


def test_discovery_rejects_missing_input(
    tmp_path: Path,
) -> None:
    from validate_benchmarks import discover_benchmark_paths

    with pytest.raises(FileNotFoundError):
        discover_benchmark_paths(
            [
                tmp_path / "missing",
            ]
        )


def test_discovery_rejects_non_json_file(
    tmp_path: Path,
) -> None:
    from validate_benchmarks import discover_benchmark_paths

    path = tmp_path / "benchmark.txt"
    path.write_text(
        "not JSON",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        discover_benchmark_paths(
            [
                path,
            ]
        )


def test_discovery_rejects_empty_directory(
    tmp_path: Path,
) -> None:
    from validate_benchmarks import discover_benchmark_paths

    with pytest.raises(ValueError):
        discover_benchmark_paths(
            [
                tmp_path,
            ]
        )


def test_load_parity_cycle_benchmark() -> None:
    benchmark = load_parity_benchmark(
        Path("benchmarks/parity_cycle_6.json")
    )

    assert benchmark.name == "parity-cycle-6"

    assert benchmark.instance.variables == (
        0,
        1,
        2,
        3,
        4,
        5,
    )

    assert benchmark.instance.boundary_variables == (
        0,
        5,
    )

    assert benchmark.instance.internal_variables == (
        1,
        2,
        3,
        4,
    )

    assert len(benchmark.instance.constraints) == 6
