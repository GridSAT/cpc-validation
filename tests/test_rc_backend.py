from __future__ import annotations

import pytest

from src.backends.rc import (
    compile_ir_to_rc,
    parity_instance_from_ir,
)
from src.compiler import (
    DEFAULT_XOR_INSTANCE,
    compile_parity_instance,
)
from src.ir_compiler import (
    compile_parity_instance_to_ir,
)


@pytest.mark.parametrize(
    ("x0", "x3"),
    [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    ],
)
def test_rc_backend_is_byte_identical_to_existing_compiler(
    x0: int,
    x3: int,
) -> None:
    boundary_values = {
        0: x0,
        3: x3,
    }

    existing = compile_parity_instance(
        DEFAULT_XOR_INSTANCE,
        boundary_values,
    )

    program = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        boundary_values,
    )

    backend = compile_ir_to_rc(
        program
    )

    assert backend.netlist == existing.netlist
    assert (
        backend.netlist.encode("utf-8")
        == existing.netlist.encode("utf-8")
    )
    assert backend.statistics == existing.statistics
    assert backend.netlist_bytes == len(
        existing.netlist.encode("utf-8")
    )


@pytest.mark.parametrize(
    (
        "supply_voltage",
        "resistance_kohm",
        "capacitance_uf",
        "threshold_voltage",
        "end_time_ms",
    ),
    [
        (
            5.0,
            10.0,
            1.0,
            2.5,
            50.0,
        ),
        (
            4.2,
            8.5,
            0.75,
            2.0,
            70.0,
        ),
        (
            5.5,
            17.0,
            1.625,
            3.0,
            125.0,
        ),
    ],
)
def test_rc_backend_preserves_physical_parameters(
    supply_voltage: float,
    resistance_kohm: float,
    capacitance_uf: float,
    threshold_voltage: float,
    end_time_ms: float,
) -> None:
    boundary_values = {
        0: 0,
        3: 1,
    }

    existing = compile_parity_instance(
        DEFAULT_XOR_INSTANCE,
        boundary_values,
        supply_voltage=supply_voltage,
        resistance_kohm=resistance_kohm,
        capacitance_uf=capacitance_uf,
        end_time_ms=end_time_ms,
    )

    program = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        boundary_values,
        supply_voltage=supply_voltage,
        resistance_kohm=resistance_kohm,
        capacitance_uf=capacitance_uf,
        threshold_voltage=threshold_voltage,
        end_time_ms=end_time_ms,
    )

    backend = compile_ir_to_rc(
        program
    )

    assert backend.netlist == existing.netlist
    assert backend.statistics == existing.statistics

    # The semantic threshold is intentionally retained in the IR interface.
    # It does not alter the physical netlist emitted by the RC backend.
    assert (
        program.interface.threshold_voltage
        == threshold_voltage
    )


def test_rc_backend_reconstructs_source_instance() -> None:
    program = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        {
            0: 1,
            3: 0,
        },
    )

    reconstructed = parity_instance_from_ir(
        program
    )

    assert reconstructed == DEFAULT_XOR_INSTANCE


def test_backend_result_preserves_program_name() -> None:
    program = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        {
            0: 0,
            3: 1,
        },
        name="named-ir-program",
    )

    result = compile_ir_to_rc(
        program
    )

    assert result.program_name == "named-ir-program"


def test_backend_statistics_match_ir_structure() -> None:
    program = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        {
            0: 0,
            3: 1,
        },
    )

    result = compile_ir_to_rc(
        program
    )

    assert result.statistics.constraint_count == (
        len(program.constraints)
    )

    assert result.statistics.variable_count == (
        len(program.variables)
    )

    assert (
        result.statistics.boundary_variable_count
        == len(program.boundary_variables)
    )

    assert (
        result.statistics.internal_variable_count
        == len(program.internal_variables)
    )

    assert result.statistics.candidate_count == (
        program.candidate_count
    )

    assert (
        result.statistics.behavioral_source_count
        == program.behavioral_source_count
    )


def test_rc_backend_does_not_mutate_ir() -> None:
    program = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        {
            0: 0,
            3: 1,
        },
    )

    before = program.to_json()

    compile_ir_to_rc(
        program
    )

    after = program.to_json()

    assert after == before


def test_backend_output_contains_no_reference_answer_comment() -> None:
    program = compile_parity_instance_to_ir(
        DEFAULT_XOR_INSTANCE,
        {
            0: 0,
            3: 1,
        },
    )

    result = compile_ir_to_rc(
        program
    )

    forbidden_terms = (
        "expected=",
        "continuation_value",
        "completion_count",
        "satisfying_assignments",
        "decoded=",
    )

    for term in forbidden_terms:
        assert term not in result.netlist
