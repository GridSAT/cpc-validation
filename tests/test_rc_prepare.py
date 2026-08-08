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
