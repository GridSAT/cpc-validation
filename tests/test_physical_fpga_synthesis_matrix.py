from __future__ import annotations

import pytest

from src.physical_fpga_synthesis import (
    FPGA_SYNTHESIS_PROJECTION_ID,
)
from src.physical_fpga_synthesis_matrix import (
    P1_BOUNDARY_CASES,
    synthesize_p1_case,
    synthesize_p1_matrix,
)


def test_p1_boundary_matrix_is_complete() -> None:
    assert P1_BOUNDARY_CASES == (
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    )


@pytest.mark.parametrize(
    ("x0", "x3"),
    P1_BOUNDARY_CASES,
)
def test_each_p1_case_synthesizes(
    x0: int,
    x3: int,
) -> None:
    case = synthesize_p1_case(
        x0,
        x3,
    )

    assert case.case_id == (
        f"p1-{x0}{x3}"
    )

    assert case.boundary_values == (
        (0, x0),
        (3, x3),
    )

    assert case.projection_id == (
        FPGA_SYNTHESIS_PROJECTION_ID
    )

    assert case.synthesis_tool == "yosys"

    assert case.synthesis_tool_version.startswith(
        "Yosys "
    )

    assert case.synthesized_json_size > 0

    assert case.prepared_execution_hash.startswith(
        "sha256:"
    )

    assert case.synthesis_source_sha256.startswith(
        "sha256:"
    )

    assert case.synthesized_json_sha256.startswith(
        "sha256:"
    )


def test_p1_matrix_contains_four_cases() -> None:
    matrix = synthesize_p1_matrix()

    assert tuple(
        case.case_id
        for case in matrix
    ) == (
        "p1-00",
        "p1-01",
        "p1-10",
        "p1-11",
    )


def test_p1_matrix_has_distinct_prepared_bindings() -> None:
    matrix = synthesize_p1_matrix()

    assert len(
        {
            case.prepared_execution_hash
            for case in matrix
        }
    ) == 4


def test_p1_matrix_has_distinct_synthesis_sources() -> None:
    matrix = synthesize_p1_matrix()

    assert len(
        {
            case.synthesis_source_sha256
            for case in matrix
        }
    ) == 4


def test_p1_synthesis_does_not_claim_later_physical_stages() -> None:
    for case in synthesize_p1_matrix():
        assert case.place_route_complete is False
        assert case.bitstream_complete is False
        assert case.physical_programming is False
        assert case.physical_execution is False


def test_p1_case_is_deterministic() -> None:
    first = synthesize_p1_case(
        0,
        1,
    )

    second = synthesize_p1_case(
        0,
        1,
    )

    assert first == second


@pytest.mark.parametrize(
    ("x0", "x3"),
    (
        (-1, 0),
        (0, 2),
        (True, 0),
    ),
)
def test_p1_case_rejects_non_bit_boundary(
    x0: int,
    x3: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="boundary values must be integer bits",
    ):
        synthesize_p1_case(
            x0,
            x3,
        )
