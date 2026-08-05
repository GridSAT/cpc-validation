from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.ir import (
    IRCandidate,
    IRConstraint,
    IRInterface,
    IRProgram,
    IR_SCHEMA_VERSION,
    enumerate_ir_candidates,
)


def make_program() -> IRProgram:
    return IRProgram(
        name="default-xor-boundary-0-1",
        constraints=(
            IRConstraint(
                variables=(
                    0,
                    1,
                    2,
                ),
                parity=0,
            ),
            IRConstraint(
                variables=(
                    1,
                    2,
                    3,
                ),
                parity=1,
            ),
        ),
        boundary_variables=(
            0,
            3,
        ),
        internal_variables=(
            1,
            2,
        ),
        boundary_assignment=(
            (
                0,
                0,
            ),
            (
                3,
                1,
            ),
        ),
        candidates=enumerate_ir_candidates(
            (
                1,
                2,
            )
        ),
        interface=IRInterface(),
    )


def test_constraint_structure() -> None:
    constraint = IRConstraint(
        variables=(
            0,
            1,
            2,
        ),
        parity=1,
    )

    assert constraint.variables == (
        0,
        1,
        2,
    )
    assert constraint.parity == 1


@pytest.mark.parametrize(
    "variables",
    [
        (),
        (
            0,
            0,
        ),
        (
            -1,
            2,
        ),
    ],
)
def test_invalid_constraint_variables_are_rejected(
    variables: tuple[int, ...],
) -> None:
    with pytest.raises(ValueError):
        IRConstraint(
            variables=variables,
            parity=0,
        )


@pytest.mark.parametrize(
    "parity",
    [
        -1,
        2,
        7,
    ],
)
def test_invalid_constraint_parity_is_rejected(
    parity: int,
) -> None:
    with pytest.raises(ValueError):
        IRConstraint(
            variables=(
                0,
                1,
            ),
            parity=parity,
        )


def test_candidate_enumeration() -> None:
    candidates = enumerate_ir_candidates(
        (
            1,
            2,
        )
    )

    assert candidates == (
        IRCandidate(
            index=0,
            assignment=(
                (
                    1,
                    0,
                ),
                (
                    2,
                    0,
                ),
            ),
        ),
        IRCandidate(
            index=1,
            assignment=(
                (
                    1,
                    0,
                ),
                (
                    2,
                    1,
                ),
            ),
        ),
        IRCandidate(
            index=2,
            assignment=(
                (
                    1,
                    1,
                ),
                (
                    2,
                    0,
                ),
            ),
        ),
        IRCandidate(
            index=3,
            assignment=(
                (
                    1,
                    1,
                ),
                (
                    2,
                    1,
                ),
            ),
        ),
    )


def test_empty_internal_variable_set_has_one_candidate() -> None:
    candidates = enumerate_ir_candidates(())

    assert candidates == (
        IRCandidate(
            index=0,
            assignment=(),
        ),
    )


def test_candidate_assignment_dict() -> None:
    candidate = enumerate_ir_candidates(
        (
            1,
            2,
        )
    )[2]

    assert candidate.assignment_dict == {
        1: 1,
        2: 0,
    }


def test_program_structure() -> None:
    program = make_program()

    assert program.schema_version == IR_SCHEMA_VERSION
    assert program.variables == (
        0,
        1,
        2,
        3,
    )
    assert program.boundary_variables == (
        0,
        3,
    )
    assert program.internal_variables == (
        1,
        2,
    )
    assert program.boundary_assignment_dict == {
        0: 0,
        3: 1,
    }
    assert program.candidate_count == 4
    assert program.behavioral_source_count == 5


def test_program_contains_no_expected_answer_fields() -> None:
    data = make_program().to_dict()

    forbidden_keys = {
        "expected",
        "continuation_value",
        "completion_count",
        "decoded",
        "output_voltage",
        "satisfying_assignments",
    }

    serialized_keys = set()

    def collect_keys(value: object) -> None:
        if isinstance(value, dict):
            serialized_keys.update(value)

            for child in value.values():
                collect_keys(child)

        elif isinstance(value, list):
            for child in value:
                collect_keys(child)

    collect_keys(data)

    assert serialized_keys.isdisjoint(
        forbidden_keys
    )


def test_program_json_round_trip() -> None:
    original = make_program()

    restored = IRProgram.from_json(
        original.to_json()
    )

    assert restored == original


def test_program_file_round_trip(
    tmp_path: Path,
) -> None:
    original = make_program()
    output_path = tmp_path / "program.json"

    original.write_json(output_path)

    restored = IRProgram.read_json(
        output_path
    )

    assert restored == original

    raw = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert raw["schema_version"] == 1
    assert raw["name"] == (
        "default-xor-boundary-0-1"
    )


def test_pretty_program() -> None:
    text = make_program().pretty()

    assert "IR program: default-xor-boundary-0-1" in text
    assert "Boundary variables: x0, x3" in text
    assert "Internal variables: x1, x2" in text
    assert "x0 XOR x1 XOR x2 = 0" in text
    assert "x1 XOR x2 XOR x3 = 1" in text
    assert "Candidates: 4" in text
    assert "Behavioral sources: 5" in text


def test_program_rejects_incomplete_variable_partition() -> None:
    with pytest.raises(
        ValueError,
        match="exactly cover",
    ):
        IRProgram(
            name="invalid",
            constraints=(
                IRConstraint(
                    variables=(
                        0,
                        1,
                        2,
                    ),
                    parity=0,
                ),
            ),
            boundary_variables=(
                0,
            ),
            internal_variables=(
                1,
            ),
            boundary_assignment=(
                (
                    0,
                    0,
                ),
            ),
            candidates=enumerate_ir_candidates(
                (
                    1,
                )
            ),
        )


def test_program_rejects_boundary_internal_overlap() -> None:
    with pytest.raises(
        ValueError,
        match="disjoint",
    ):
        IRProgram(
            name="invalid",
            constraints=(
                IRConstraint(
                    variables=(
                        0,
                        1,
                    ),
                    parity=0,
                ),
            ),
            boundary_variables=(
                0,
            ),
            internal_variables=(
                0,
                1,
            ),
            boundary_assignment=(
                (
                    0,
                    0,
                ),
            ),
            candidates=enumerate_ir_candidates(
                (
                    0,
                    1,
                )
            ),
        )


def test_program_rejects_wrong_candidate_count() -> None:
    with pytest.raises(
        ValueError,
        match=r"2\^k",
    ):
        IRProgram(
            name="invalid",
            constraints=(
                IRConstraint(
                    variables=(
                        0,
                        1,
                    ),
                    parity=0,
                ),
            ),
            boundary_variables=(
                0,
            ),
            internal_variables=(
                1,
            ),
            boundary_assignment=(
                (
                    0,
                    0,
                ),
            ),
            candidates=(),
        )


def test_program_rejects_wrong_boundary_order() -> None:
    program = make_program()

    with pytest.raises(
        ValueError,
        match="exact boundary-variable order",
    ):
        IRProgram(
            name=program.name,
            constraints=program.constraints,
            boundary_variables=(
                0,
                3,
            ),
            internal_variables=program.internal_variables,
            boundary_assignment=(
                (
                    3,
                    1,
                ),
                (
                    0,
                    0,
                ),
            ),
            candidates=program.candidates,
            interface=program.interface,
        )


def test_interface_validation() -> None:
    interface = IRInterface(
        supply_voltage=5.0,
        resistance_kohm=10.0,
        capacitance_uf=1.0,
        threshold_voltage=2.5,
        end_time_ms=50.0,
    )

    assert interface.supply_voltage == 5.0
    assert interface.threshold_voltage == 2.5


@pytest.mark.parametrize(
    "interface",
    [
        IRInterface,
    ],
)
def test_interface_type_is_available(
    interface: type[IRInterface],
) -> None:
    assert interface is IRInterface


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "supply_voltage": 0.0,
        },
        {
            "resistance_kohm": -1.0,
        },
        {
            "capacitance_uf": 0.0,
        },
        {
            "end_time_ms": -5.0,
        },
        {
            "supply_voltage": 5.0,
            "threshold_voltage": 6.0,
        },
        {
            "threshold_voltage": -0.1,
        },
    ],
)
def test_invalid_interface_parameters_are_rejected(
    kwargs: dict[str, float],
) -> None:
    with pytest.raises(ValueError):
        IRInterface(**kwargs)


def test_unknown_program_json_key_is_rejected() -> None:
    data = make_program().to_dict()
    data["expected"] = 1

    with pytest.raises(
        ValueError,
        match="unsupported keys",
    ):
        IRProgram.from_dict(data)


def test_invalid_json_root_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="root must be an object",
    ):
        IRProgram.from_json("[]")


def test_invalid_json_syntax_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="invalid IR JSON",
    ):
        IRProgram.from_json("{")
