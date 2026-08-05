from __future__ import annotations

import pytest

from src.compiler import (
    DEFAULT_XOR_INSTANCE,
    ParityConstraint,
    ParityInstance,
    compile_parity_instance,
    enumerate_internal_assignments,
    xor_expression,
)


def test_default_instance_structure() -> None:
    assert DEFAULT_XOR_INSTANCE.variables == (
        0,
        1,
        2,
        3,
    )

    assert DEFAULT_XOR_INSTANCE.boundary_variables == (
        0,
        3,
    )

    assert DEFAULT_XOR_INSTANCE.internal_variables == (
        1,
        2,
    )


def test_internal_assignment_enumeration() -> None:
    assignments = list(
        enumerate_internal_assignments((1, 2))
    )

    assert assignments == [
        {1: 0, 2: 0},
        {1: 0, 2: 1},
        {1: 1, 2: 0},
        {1: 1, 2: 1},
    ]


def test_empty_internal_assignment_has_one_candidate() -> None:
    assignments = list(
        enumerate_internal_assignments(())
    )

    assert assignments == [{}]


def test_default_instance_compiles_four_candidates() -> None:
    compiled = compile_parity_instance(
        DEFAULT_XOR_INSTANCE,
        {
            0: 0,
            3: 1,
        },
    )

    assert compiled.statistics.constraint_count == 2
    assert compiled.statistics.variable_count == 4
    assert compiled.statistics.boundary_variable_count == 2
    assert compiled.statistics.internal_variable_count == 2
    assert compiled.statistics.candidate_count == 4
    assert compiled.statistics.candidate_source_count == 4
    assert compiled.statistics.behavioral_source_count == 5

    for candidate_index in range(4):
        assert (
            f"Bcandidate{candidate_index} "
            f"candidate{candidate_index} 0"
        ) in compiled.netlist

    assert "Bexist logic 0" in compiled.netlist
    assert "Rout logic vout 10.0k" in compiled.netlist
    assert "Cout vout 0 1.0u" in compiled.netlist


def test_compilation_uses_boundary_sources() -> None:
    compiled = compile_parity_instance(
        DEFAULT_XOR_INSTANCE,
        {
            0: 1,
            3: 0,
        },
        supply_voltage=5.0,
    )

    assert "Vx0 x0 0 5.0" in compiled.netlist
    assert "Vx3 x3 0 0.0" in compiled.netlist


def test_compiler_does_not_insert_reference_answer() -> None:
    compiled = compile_parity_instance(
        DEFAULT_XOR_INSTANCE,
        {
            0: 0,
            3: 1,
        },
    )

    assert "expected_continuation" not in compiled.netlist
    assert "continuation truth table" not in compiled.netlist.lower()
    assert (
        "The continuation answer is not inserted into this netlist."
        in compiled.netlist
    )


def test_arbitrary_length_xor_expression() -> None:
    expression = xor_expression(
        (
            "a",
            "b",
            "c",
            "d",
        )
    )

    assert "a" in expression
    assert "b" in expression
    assert "c" in expression
    assert "d" in expression

    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                for d in (0, 1):
                    evaluated = eval(
                        expression,
                        {
                            "__builtins__": {},
                        },
                        {
                            "a": a,
                            "b": b,
                            "c": c,
                            "d": d,
                        },
                    )

                    assert evaluated == (a ^ b ^ c ^ d)


def test_single_term_xor_expression() -> None:
    assert xor_expression(("a",)) == "(a)"


def test_constraint_validation() -> None:
    with pytest.raises(ValueError):
        ParityConstraint(
            variables=(),
            parity=0,
        )

    with pytest.raises(ValueError):
        ParityConstraint(
            variables=(0, 0),
            parity=0,
        )

    with pytest.raises(ValueError):
        ParityConstraint(
            variables=(-1, 0),
            parity=0,
        )

    with pytest.raises(ValueError):
        ParityConstraint(
            variables=(0, 1),
            parity=2,
        )


def test_instance_validation() -> None:
    constraint = ParityConstraint(
        variables=(0, 1),
        parity=1,
    )

    with pytest.raises(ValueError):
        ParityInstance(
            constraints=(),
            boundary_variables=(0,),
        )

    with pytest.raises(ValueError):
        ParityInstance(
            constraints=(constraint,),
            boundary_variables=(0, 0),
        )

    with pytest.raises(ValueError):
        ParityInstance(
            constraints=(constraint,),
            boundary_variables=(0, 7),
        )


def test_boundary_values_must_be_complete() -> None:
    with pytest.raises(ValueError):
        compile_parity_instance(
            DEFAULT_XOR_INSTANCE,
            {
                0: 0,
            },
        )

    with pytest.raises(ValueError):
        compile_parity_instance(
            DEFAULT_XOR_INSTANCE,
            {
                0: 0,
                3: 1,
                7: 0,
            },
        )


def test_boundary_values_must_be_boolean() -> None:
    with pytest.raises(ValueError):
        compile_parity_instance(
            DEFAULT_XOR_INSTANCE,
            {
                0: 0,
                3: 2,
            },
        )


@pytest.mark.parametrize(
    (
        "parameter",
        "value",
    ),
    [
        ("supply_voltage", 0.0),
        ("resistance_kohm", 0.0),
        ("capacitance_uf", 0.0),
        ("end_time_ms", 0.0),
    ],
)
def test_physical_parameters_must_be_positive(
    parameter: str,
    value: float,
) -> None:
    arguments = {
        "instance": DEFAULT_XOR_INSTANCE,
        "boundary_values": {
            0: 0,
            3: 1,
        },
        "supply_voltage": 5.0,
        "resistance_kohm": 10.0,
        "capacitance_uf": 1.0,
        "end_time_ms": 50.0,
    }

    arguments[parameter] = value

    with pytest.raises(ValueError):
        compile_parity_instance(**arguments)


def test_default_compiler_netlist_executes_in_ngspice(
    tmp_path,
) -> None:
    from src.spice_model import (
        _read_measured_voltage,
        _run_ngspice,
    )

    compiled = compile_parity_instance(
        DEFAULT_XOR_INSTANCE,
        {
            0: 0,
            3: 1,
        },
    )

    netlist_path = tmp_path / "compiled_default_xor.cir"
    log_path = tmp_path / "compiled_default_xor.out"

    netlist_path.write_text(
        compiled.netlist,
        encoding="utf-8",
    )

    _run_ngspice(
        netlist_path,
        log_path,
    )

    output_voltage = _read_measured_voltage(log_path)

    assert output_voltage > 2.5


@pytest.mark.parametrize(
    ("x0", "x3", "expected"),
    [
        (0, 0, 0),
        (0, 1, 1),
        (1, 0, 1),
        (1, 1, 0),
    ],
)
def test_generic_compiler_and_simulator_agree(
    x0: int,
    x3: int,
    expected: int,
) -> None:
    from src.spice_model import simulate_response

    response = simulate_response(
        x0=x0,
        x3=x3,
    )

    assert response.expected == expected
    assert response.decoded == expected
    assert "CPC generic parity-constraint compiler" in (
        response.netlist_path.read_text(encoding="utf-8")
    )
