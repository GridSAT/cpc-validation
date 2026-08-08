from __future__ import annotations

import pytest

from src.compiler import (
    DEFAULT_XOR_INSTANCE,
    ParityConstraint,
    ParityInstance,
    compile_parity_instance,
    enumerate_internal_assignments,
)
from src.ir_compiler import (
    DEFAULT_IR_THRESHOLD_V,
    compile_parity_instance_to_ir,
)


def test_default_instance_compiles_to_ir() -> None:
    program = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        {
            0: 0,
            3: 1,
        },
    )

    assert program.constraints == tuple(
        type(program.constraints[0])(
            variables=constraint.variables,
            parity=constraint.parity,
        )
        for constraint in DEFAULT_XOR_INSTANCE.constraints
    )

    assert program.boundary_variables == (
        0,
        3,
    )

    assert program.internal_variables == (
        1,
        2,
    )

    assert program.boundary_assignment == (
        (
            0,
            0,
        ),
        (
            3,
            1,
        ),
    )

    assert program.candidate_count == 4
    assert program.behavioral_source_count == 5


def test_ir_candidate_order_matches_existing_compiler() -> None:
    program = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        {
            0: 1,
            3: 0,
        },
    )

    existing_assignments = list(
        enumerate_internal_assignments(
            DEFAULT_XOR_INSTANCE.internal_variables
        )
    )

    ir_assignments = [
        candidate.assignment_dict
        for candidate in program.candidates
    ]

    assert ir_assignments == existing_assignments


def test_ir_statistics_match_existing_compiler() -> None:
    boundary_values = {
        0: 0,
        3: 1,
    }

    program = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        boundary_values,
    )

    compiled = compile_parity_instance(
        DEFAULT_XOR_INSTANCE,
        boundary_values,
    )

    statistics = compiled.statistics

    assert len(program.constraints) == (
        statistics.constraint_count
    )

    assert len(program.variables) == (
        statistics.variable_count
    )

    assert len(program.boundary_variables) == (
        statistics.boundary_variable_count
    )

    assert len(program.internal_variables) == (
        statistics.internal_variable_count
    )

    assert program.candidate_count == (
        statistics.candidate_count
    )

    assert program.candidate_count == (
        statistics.candidate_source_count
    )

    assert program.behavioral_source_count == (
        statistics.behavioral_source_count
    )


def test_interface_parameters_are_preserved() -> None:
    program = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        {
            0: 0,
            3: 1,
        },
        supply_voltage=4.8,
        resistance_kohm=12.5,
        capacitance_uf=0.75,
        threshold_voltage=2.1,
        end_time_ms=80.0,
    )

    assert program.interface.supply_voltage == 4.8
    assert program.interface.resistance_kohm == 12.5
    assert program.interface.capacitance_uf == 0.75
    assert program.interface.threshold_voltage == 2.1
    assert program.interface.end_time_ms == 80.0


def test_default_threshold_is_preserved() -> None:
    program = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        {
            0: 0,
            3: 1,
        },
    )

    assert program.interface.threshold_voltage == (
        DEFAULT_IR_THRESHOLD_V
    )


def test_explicit_program_name_is_preserved() -> None:
    program = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        {
            0: 0,
            3: 1,
        },
        name="default-xor-test",
    )

    assert program.name == "default-xor-test"


def test_default_program_name_is_deterministic() -> None:
    first = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        {
            0: 0,
            3: 1,
        },
    )

    second = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        {
            0: 0,
            3: 1,
        },
    )

    assert first.name == second.name

    assert first.name == (
        "parity-4v-2c-x0-0-x3-1"
    )


@pytest.mark.parametrize(
    "boundary_values",
    [
        {
            0: 0,
        },
        {
            0: 0,
            3: 1,
            7: 0,
        },
        {
            0: 2,
            3: 1,
        },
        {
            0: True,
            3: 1,
        },
    ],
)
def test_invalid_boundary_assignment_is_rejected(
    boundary_values: dict[int, int],
) -> None:
    with pytest.raises(ValueError):
        compile_parity_instance_to_ir(
            DEFAULT_XOR_INSTANCE,
            boundary_values,
        )


def test_instance_without_internal_variables() -> None:
    instance = ParityInstance(
        constraints=(
            ParityConstraint(
                variables=(
                    0,
                    1,
                ),
                parity=1,
            ),
        ),
        boundary_variables=(
            0,
            1,
        ),
    )

    program = compile_parity_instance_to_ir(
        instance,
        {
            0: 0,
            1: 1,
        },
    )

    assert program.internal_variables == ()
    assert program.candidate_count == 1
    assert program.candidates[0].assignment == ()


def test_ir_serialization_contains_no_reference_answer() -> None:
    program = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        {
            0: 0,
            3: 1,
        },
    )

    serialized = program.to_json()

    forbidden_terms = (
        '"expected"',
        '"continuation_value"',
        '"completion_count"',
        '"decoded"',
        '"output_voltage"',
        '"satisfying_assignments"',
    )

    for term in forbidden_terms:
        assert term not in serialized


@pytest.mark.parametrize(
    ("x0", "x3"),
    [
        (
            0,
            0,
        ),
        (
            0,
            1,
        ),
        (
            1,
            0,
        ),
        (
            1,
            1,
        ),
    ],
)
def test_all_default_boundaries_compile(
    x0: int,
    x3: int,
) -> None:
    program = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        {
            0: x0,
            3: x3,
        },
    )

    assert program.boundary_assignment_dict == {
        0: x0,
        3: x3,
    }

    assert program.candidate_count == 4
