from __future__ import annotations

from dataclasses import replace

from src.backends.rc_ccir import (
    RCBackend,
    RC_SPECIFICATION,
)
from src.backends.rc_prepare import (
    prepare_rc_netlist,
)
from src.ccir_lower_parity import (
    lower_parity_instance_to_ccir,
)
from src.compile_backend import (
    compile_backend,
)
from src.compiler import (
    DEFAULT_XOR_INSTANCE,
)


def test_rc_preparation_applies_boundary_values_after_compilation() -> None:
    program = lower_parity_instance_to_ccir(
        DEFAULT_XOR_INSTANCE
    )

    specification = RC_SPECIFICATION

    artifact = compile_backend(
        program,
        RCBackend(
            specification=specification,
        ),
    )

    first, _ = prepare_rc_netlist(
        program,
        artifact,
        {
            0: 0,
            3: 1,
        },
        specification,
    )

    second, _ = prepare_rc_netlist(
        program,
        artifact,
        {
            0: 1,
            3: 0,
        },
        specification,
    )

    assert artifact == compile_backend(
        program,
        RCBackend(
            specification=specification,
        ),
    )

    assert first != second
    assert "Vx0 x0 0 0.0" in first
    assert "Vx3 x3 0 5.0" in first
    assert "Vx0 x0 0 5.0" in second
    assert "Vx3 x3 0 0.0" in second


def test_rc_preparation_preserves_fixed_backend_parameters() -> None:
    program = lower_parity_instance_to_ccir(
        DEFAULT_XOR_INSTANCE
    )

    specification = replace(
        RC_SPECIFICATION,
        fixed_parameters=(
            ("supply_voltage", 4.2),
            ("resistance_kohm", 8.5),
            ("capacitance_uf", 0.75),
            ("threshold_voltage", 2.0),
            ("end_time_ms", 70.0),
        ),
    )

    artifact = compile_backend(
        program,
        RCBackend(
            specification=specification,
        ),
    )

    netlist, _ = prepare_rc_netlist(
        program,
        artifact,
        {
            0: 0,
            3: 1,
        },
        specification,
    )

    assert "Vx0 x0 0 0.0" in netlist
    assert "Vx3 x3 0 4.2" in netlist
    assert "Rout logic vout 8.5k" in netlist
    assert "Cout vout 0 0.75u" in netlist
    assert ".tran 0.1m 70.0m" in netlist


def test_rc_preparation_does_not_change_compiled_artifact() -> None:
    program = lower_parity_instance_to_ccir(
        DEFAULT_XOR_INSTANCE
    )

    specification = RC_SPECIFICATION

    artifact = compile_backend(
        program,
        RCBackend(
            specification=specification,
        ),
    )

    before = artifact

    prepare_rc_netlist(
        program,
        artifact,
        {
            0: 1,
            3: 1,
        },
        specification,
    )

    assert artifact == before


def test_prepare_rc_execution_returns_first_class_prepared_state() -> None:
    from src.backends.rc_ccir import (
        RCBackend,
        RC_SPECIFICATION,
    )
    from src.backends.rc_prepare import (
        prepare_rc_execution,
    )
    from src.ccir import (
        CCIRConstraint,
        CCIRProgram,
    )
    from src.ccir_parity import (
        CCIRParityPayload,
        PARITY_CONSTRAINT_FAMILY,
    )
    from src.prepared_execution import PreparedExecution

    program = CCIRProgram(
        name="prepared-execution",
        variable_count=3,
        boundary_variables=(0, 2),
        constraints=(
            CCIRConstraint(
                family=PARITY_CONSTRAINT_FAMILY,
                payload=CCIRParityPayload(
                    variables=(0, 1, 2),
                    parity=0,
                ),
            ),
        ),
    )

    artifact = RCBackend().compile(
        program
    )

    prepared = prepare_rc_execution(
        program,
        artifact,
        {
            0: 0,
            2: 1,
        },
        RC_SPECIFICATION,
    )

    assert isinstance(
        prepared,
        PreparedExecution,
    )

    assert prepared.backend_id == "rc"
    assert prepared.backend_version == "1"
    assert isinstance(prepared.payload, str)

    assert prepared.interface == artifact.interface

    assert dict(
        prepared.decoder_specification
    ) == {
        "threshold_voltage": 2.5,
    }

    metadata = dict(
        prepared.metadata
    )

    assert metadata["preparation_id"] == (
        "rc.ngspice-netlist.v1"
    )

    assert metadata["boundary_values"] == (
        (0, 0),
        (2, 1),
    )

    emitter_metadata = dict(
        metadata["emitter_metadata"]
    )

    assert emitter_metadata["candidate_count"] == 2
    assert emitter_metadata["constraint_count"] == 1


def test_prepare_rc_netlist_compatibility_wrapper_matches_prepared_execution() -> None:
    from src.backends.rc_ccir import (
        RCBackend,
        RC_SPECIFICATION,
    )
    from src.backends.rc_prepare import (
        prepare_rc_execution,
        prepare_rc_netlist,
    )
    from src.ccir import (
        CCIRConstraint,
        CCIRProgram,
    )
    from src.ccir_parity import (
        CCIRParityPayload,
        PARITY_CONSTRAINT_FAMILY,
    )

    program = CCIRProgram(
        name="prepared-compatibility",
        variable_count=3,
        boundary_variables=(0, 2),
        constraints=(
            CCIRConstraint(
                family=PARITY_CONSTRAINT_FAMILY,
                payload=CCIRParityPayload(
                    variables=(0, 1, 2),
                    parity=0,
                ),
            ),
        ),
    )

    artifact = RCBackend().compile(
        program
    )

    boundary_values = {
        0: 0,
        2: 1,
    }

    prepared = prepare_rc_execution(
        program,
        artifact,
        boundary_values,
        RC_SPECIFICATION,
    )

    netlist, legacy_metadata = prepare_rc_netlist(
        program,
        artifact,
        boundary_values,
        RC_SPECIFICATION,
    )

    assert netlist == prepared.payload

    assert legacy_metadata == dict(
        dict(prepared.metadata)[
            "emitter_metadata"
        ]
    )
