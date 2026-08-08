from src.backends.fpga_ccir import (
    FPGA_SPECIFICATION,
    FPGABackend,
)
from src.ccir import (
    CCIRConstraint,
    CCIRProgram,
)
from src.ccir_parity import (
    CCIRParityPayload,
    PARITY_CONSTRAINT_FAMILY,
)
from src.compile_backend import compile_backend


def make_program() -> CCIRProgram:
    return CCIRProgram(
        name="fpga-test",
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


def test_fpga_backend_has_distinct_identity() -> None:
    assert FPGA_SPECIFICATION.backend_id == "fpga"
    assert FPGA_SPECIFICATION.backend_version == "1"


def test_fpga_backend_declares_hardware_capabilities() -> None:
    capabilities = FPGABackend().capabilities

    assert "synthesizable-logic" in (
        capabilities.execution_features
    )
    assert "logic-network-topology" in (
        capabilities.artifact_features
    )
    assert "hdl-preparable" in (
        capabilities.artifact_features
    )


def test_compile_backend_dispatches_fpga() -> None:
    program = make_program()

    artifact = compile_backend(
        program,
        FPGABackend(),
    )

    metadata = dict(artifact.metadata)

    assert metadata["backend_id"] == "fpga"
    assert metadata["backend_version"] == "1"
    assert metadata["program_name"] == "fpga-test"


def test_fpga_artifact_is_logic_network_not_digital_program() -> None:
    artifact = FPGABackend().compile(
        make_program()
    )

    element_types = {
        element[0]
        for _, element in artifact.topology
        if isinstance(element, tuple) and element
    }

    assert "variable-signal" in element_types
    assert "parity-network" in element_types
    assert "constraint-match" in element_types
    assert "result-signal" in element_types

    assert "variable-register" not in element_types
    assert "parity-instruction" not in element_types
    assert "result-register" not in element_types


def test_fpga_artifact_has_distinct_fixed_parameters() -> None:
    artifact = FPGABackend().compile(
        make_program()
    )

    parameters = dict(artifact.parameters)

    assert parameters == {
        "logic_domain": "bit",
        "representation": (
            "synthesizable-logic-network-v1"
        ),
        "hdl_target": "verilog-2001",
    }


def test_fpga_artifact_preserves_boundary_interface() -> None:
    artifact = FPGABackend().compile(
        make_program()
    )

    interface = dict(artifact.interface)

    assert interface["boundary_variables"] == (
        0,
        3,
    )
    assert interface["readout_signal"] == "result"


def test_fpga_artifact_provenance_is_complete() -> None:
    artifact = FPGABackend().compile(
        make_program()
    )

    topology_ids = {
        element_id
        for element_id, _ in artifact.topology
    }

    provenance_ids = {
        element_id
        for element_id, _ in artifact.provenance
    }

    assert topology_ids == provenance_ids


def test_fpga_compilation_is_deterministic() -> None:
    program = make_program()

    assert (
        FPGABackend().compile(program)
        ==
        FPGABackend().compile(program)
    )


def test_fpga_compilation_does_not_require_boundary_values() -> None:
    artifact = FPGABackend().compile(
        make_program()
    )

    assert dict(
        artifact.metadata
    )["backend_id"] == "fpga"
