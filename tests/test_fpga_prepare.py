import pytest

from src.backends.fpga_ccir import FPGABackend
from src.backends.fpga_prepare import (
    prepare_fpga_execution,
)
from src.prepared_execution import PreparedExecution
from src.ccir import (
    CCIRConstraint,
    CCIRProgram,
)
from src.ccir_parity import (
    CCIRParityPayload,
    PARITY_CONSTRAINT_FAMILY,
)


def make_program() -> CCIRProgram:
    return CCIRProgram(
        name="fpga-prepare-test",
        variable_count=4,
        boundary_variables=(0, 3),
        constraints=(
            CCIRConstraint(
                family=PARITY_CONSTRAINT_FAMILY,
                payload=CCIRParityPayload(
                    variables=(0, 1, 2),
                    parity=0,
                ),
            ),
            CCIRConstraint(
                family=PARITY_CONSTRAINT_FAMILY,
                payload=CCIRParityPayload(
                    variables=(1, 2, 3),
                    parity=1,
                ),
            ),
        ),
    )


def prepare(
    boundary_values: dict[int, int] | None = None,
) -> PreparedExecution:
    program = make_program()
    artifact = FPGABackend().compile(program)

    return prepare_fpga_execution(
        program,
        artifact,
        boundary_values or {
            0: 0,
            3: 1,
        },
    )


def test_preparation_identity() -> None:
    prepared = prepare()

    assert prepared.backend_id == "fpga"
    assert prepared.backend_version == "1"
    assert isinstance(
        prepared,
        PreparedExecution,
    )

    metadata = dict(
        prepared.metadata
    )

    assert metadata["execution_engine"] == "verilog-2001"
    assert metadata["module_name"] == "cpc_fpga_execution"


def test_preparation_preserves_boundary_values() -> None:
    prepared = prepare(
        {
            0: 1,
            3: 0,
        }
    )

    metadata = dict(
        prepared.metadata
    )

    assert metadata["boundary_values"] == (
        (0, 1),
        (3, 0),
    )

    assert "assign x0 = 1'b1;" in prepared.payload
    assert "assign x3 = 1'b0;" in prepared.payload


def test_two_internal_variables_create_four_parallel_completions() -> None:
    source = prepare().payload

    for index in range(4):
        assert (
            f"wire completion_{index};"
            in source
        )

    assert "wire completion_4;" not in source


def test_internal_assignments_are_structural_constants() -> None:
    source = prepare().payload

    assert (
        "assign completion_0_x1 = 1'b0;"
        in source
    )
    assert (
        "assign completion_0_x2 = 1'b0;"
        in source
    )
    assert (
        "assign completion_3_x1 = 1'b1;"
        in source
    )
    assert (
        "assign completion_3_x2 = 1'b1;"
        in source
    )


def test_constraints_are_emitted_as_xor_logic() -> None:
    source = prepare().payload

    assert (
        "assign completion_0_parity_0 = "
        "x0 ^ completion_0_x1 ^ completion_0_x2;"
        in source
    )

    assert (
        "assign completion_0_parity_1 = "
        "completion_0_x1 ^ completion_0_x2 ^ x3;"
        in source
    )


def test_result_is_existential_or_of_completions() -> None:
    source = prepare().payload

    assert (
        "assign result = "
        "completion_0 | completion_1 | "
        "completion_2 | completion_3;"
        in source
    )


def test_preparation_does_not_embed_expected_answer() -> None:
    source = prepare().payload.lower()

    assert "expected_continuation" not in source
    assert "semantic result" not in source
    assert "reference result" not in source


def test_preparation_is_deterministic() -> None:
    first = prepare()
    second = prepare()

    assert first == second


def test_boundary_assignment_changes_only_prepared_input_constants() -> None:
    first = prepare(
        {
            0: 0,
            3: 1,
        }
    )

    second = prepare(
        {
            0: 1,
            3: 0,
        }
    )

    assert first.payload != second.payload

    assert (
        "assign x0 = 1'b0;"
        in first.payload
    )
    assert (
        "assign x0 = 1'b1;"
        in second.payload
    )


def test_missing_boundary_is_rejected() -> None:
    program = make_program()
    artifact = FPGABackend().compile(program)

    with pytest.raises(
        ValueError,
        match="missing boundary values",
    ):
        prepare_fpga_execution(
            program,
            artifact,
            {
                0: 0,
            },
        )


def test_unexpected_boundary_is_rejected() -> None:
    program = make_program()
    artifact = FPGABackend().compile(program)

    with pytest.raises(
        ValueError,
        match="unexpected boundary values",
    ):
        prepare_fpga_execution(
            program,
            artifact,
            {
                0: 0,
                3: 1,
                2: 0,
            },
        )


def test_non_bit_boundary_is_rejected() -> None:
    program = make_program()
    artifact = FPGABackend().compile(program)

    with pytest.raises(
        ValueError,
        match="must be assigned integer 0 or 1",
    ):
        prepare_fpga_execution(
            program,
            artifact,
            {
                0: 2,
                3: 1,
            },
        )
