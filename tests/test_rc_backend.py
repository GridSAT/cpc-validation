from __future__ import annotations

import pytest

from src.backends.rc_ccir import (
    RCBackend,
    RC_SPECIFICATION,
)
from src.ccir import (
    CCIRConstraint,
    CCIRProgram,
)
from src.ccir_clause import (
    CCIRClausePayload,
    CCIRLiteral,
)
from src.ccir_parity import (
    CCIRParityPayload,
)
from src.compile_backend import (
    compile_backend,
)
from src.backend import (
    UnsupportedBackendCapabilityError,
)


def parity_program() -> CCIRProgram:
    return CCIRProgram(
        name="rc-parity",
        variable_count=4,
        boundary_variables=(0, 3),
        constraints=(
            CCIRConstraint(
                family="parity",
                payload=CCIRParityPayload(
                    variables=(0, 1, 2),
                    parity=0,
                ),
            ),
            CCIRConstraint(
                family="parity",
                payload=CCIRParityPayload(
                    variables=(1, 2, 3),
                    parity=1,
                ),
            ),
        ),
    )


def test_rc_backend_declares_parity_capability() -> None:
    backend = RCBackend()

    assert backend.capabilities.supports_constraint_family(
        "parity"
    )

    assert not backend.capabilities.supports_constraint_family(
        "clause"
    )


def test_rc_backend_compiles_directly_from_ccir() -> None:
    program = parity_program()

    artifact = compile_backend(
        program,
        RCBackend(),
    )

    metadata = dict(
        artifact.metadata
    )

    assert metadata["backend_id"] == "rc"
    assert metadata["program_name"] == "rc-parity"
    assert metadata["constraint_count"] == 2
    assert metadata["candidate_count"] == 4


def test_rc_backend_exposes_boundary_interface_without_values() -> None:
    artifact = compile_backend(
        parity_program(),
        RCBackend(),
    )

    interface = dict(
        artifact.interface
    )

    assert interface["boundary_variables"] == (
        0,
        3,
    )

    assert "boundary_assignment" not in interface


def test_rc_backend_topology_is_constraint_derived() -> None:
    artifact = compile_backend(
        parity_program(),
        RCBackend(),
    )

    element_ids = tuple(
        element_id
        for element_id, _ in artifact.topology
    )

    assert "node:x0" in element_ids
    assert "node:x1" in element_ids
    assert "node:x2" in element_ids
    assert "node:x3" in element_ids

    assert "candidate:0" in element_ids
    assert "candidate:1" in element_ids
    assert "candidate:2" in element_ids
    assert "candidate:3" in element_ids

    assert "aggregate:existential" in element_ids
    assert "readout:vout" in element_ids


def test_rc_backend_artifact_has_complete_provenance() -> None:
    artifact = compile_backend(
        parity_program(),
        RCBackend(),
    )

    topology_ids = {
        element_id
        for element_id, _ in artifact.topology
    }

    provenance_ids = {
        element_id
        for element_id, _ in artifact.provenance
    }

    assert provenance_ids == topology_ids


def test_rc_backend_uses_fixed_theta_rc() -> None:
    artifact = compile_backend(
        parity_program(),
        RCBackend(),
    )

    assert dict(
        artifact.parameters
    ) == dict(
        RC_SPECIFICATION.fixed_parameters
    )


def test_rc_backend_rejects_clause_ccir() -> None:
    program = CCIRProgram(
        name="clause",
        variable_count=1,
        boundary_variables=(),
        constraints=(
            CCIRConstraint(
                family="clause",
                payload=CCIRClausePayload(
                    literals=(
                        CCIRLiteral(
                            variable=0,
                        ),
                    ),
                ),
            ),
        ),
    )

    with pytest.raises(
        UnsupportedBackendCapabilityError,
        match="unsupported CCIR constraint families: clause",
    ):
        compile_backend(
            program,
            RCBackend(),
        )


def test_rc_backend_does_not_call_legacy_ir_compiler(
    monkeypatch,
) -> None:
    import src.ir_compiler

    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "legacy IR compiler must not participate "
            "in native CCIR RC compilation"
        )

    monkeypatch.setattr(
        src.ir_compiler,
        "compile_parity_instance_to_ir",
        fail_if_called,
    )

    artifact = compile_backend(
        parity_program(),
        RCBackend(),
    )

    assert artifact.topology


def test_rc_backend_does_not_call_public_parity_compiler(
    monkeypatch,
) -> None:
    import src.compiler

    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "public parity compiler must not participate "
            "in native CCIR RC compilation"
        )

    monkeypatch.setattr(
        src.compiler,
        "compile_parity_instance",
        fail_if_called,
    )

    artifact = compile_backend(
        parity_program(),
        RCBackend(),
    )

    assert artifact.topology
