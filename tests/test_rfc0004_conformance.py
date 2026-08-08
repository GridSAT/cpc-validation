from __future__ import annotations

from pathlib import Path

import pytest

from src.backend import (
    UnsupportedBackendCapabilityError,
    validate_artifact_provenance,
)
from src.backends.rc_ccir import (
    RCBackend,
    RC_SPECIFICATION,
)
from src.backends.rc_decode import decode_rc
from src.backends.rc_execute import execute_rc
from src.backends.rc_prepare import prepare_rc_execution
from src.ccir import (
    CCIRConstraint,
    CCIRProgram,
)
from src.ccir_clause import (
    CCIRClausePayload,
    CLAUSE_CONSTRAINT_FAMILY,
)
from src.ccir_parity import (
    CCIRParityPayload,
    PARITY_CONSTRAINT_FAMILY,
)
from src.compile_backend import compile_backend
from src.observable_execution import ObservableExecution
from src.prepared_execution import PreparedExecution


def _program() -> CCIRProgram:
    return CCIRProgram(
        name="rfc0004-conformance",
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


def _prepared() -> PreparedExecution:
    program = _program()
    artifact = RCBackend().compile(program)

    return prepare_rc_execution(
        program,
        artifact,
        {
            0: 0,
            2: 1,
        },
        RC_SPECIFICATION,
    )


def test_ec1_compilation_satisfies_rfc0003() -> None:
    program = _program()
    backend = RCBackend()

    artifact = compile_backend(
        program,
        backend,
    )

    assert artifact.metadata
    assert dict(artifact.metadata)["backend_id"] == "rc"


def test_ec2_preparation_preserves_artifact_identity() -> None:
    program = _program()
    artifact = RCBackend().compile(program)

    prepared = prepare_rc_execution(
        program,
        artifact,
        {
            0: 0,
            2: 1,
        },
        RC_SPECIFICATION,
    )

    assert prepared.backend_id == dict(
        artifact.metadata
    )["backend_id"]

    assert prepared.backend_version == dict(
        artifact.metadata
    )["backend_version"]

    assert prepared.interface == artifact.interface


def test_ec3_execution_consumes_prepared_execution_only(
    monkeypatch,
) -> None:
    import src.spice_model

    def fake_run(
        netlist_path: Path,
        log_path: Path,
    ) -> None:
        assert netlist_path.read_text(
            encoding="utf-8"
        )

        log_path.write_text(
            "fake",
            encoding="utf-8",
        )

    def fake_read(
        log_path: Path,
    ) -> float:
        assert log_path.exists()
        return 4.0

    monkeypatch.setattr(
        src.spice_model,
        "_run_ngspice",
        fake_run,
    )

    monkeypatch.setattr(
        src.spice_model,
        "_read_measured_voltage",
        fake_read,
    )

    observable = execute_rc(
        _prepared()
    )

    assert isinstance(
        observable,
        ObservableExecution,
    )


def test_ec4_only_admitted_observations_are_exposed(
    monkeypatch,
) -> None:
    import src.spice_model

    monkeypatch.setattr(
        src.spice_model,
        "_run_ngspice",
        lambda netlist_path, log_path: (
            log_path.write_text(
                "fake",
                encoding="utf-8",
            )
        ),
    )

    monkeypatch.setattr(
        src.spice_model,
        "_read_measured_voltage",
        lambda log_path: 3.5,
    )

    observable = execute_rc(
        _prepared()
    )

    assert observable.observations == (
        ("vout", 3.5),
    )


def test_ec5_decoder_is_fixed_by_prepared_specification() -> None:
    prepared = _prepared()

    observable = ObservableExecution(
        backend_id="rc",
        backend_version="1",
        observations=(
            ("vout", 2.5),
        ),
    )

    assert dict(
        prepared.decoder_specification
    ) == {
        "threshold_voltage": 2.5,
    }

    assert decode_rc(
        observable,
        prepared.decoder_specification,
    ) == 1


def test_ec6_execution_capabilities_are_declared() -> None:
    capabilities = RCBackend().capabilities

    assert capabilities.supports_constraint_family(
        PARITY_CONSTRAINT_FAMILY
    )

    assert "restricted-readout" in (
        capabilities.interface_features
    )

    assert "transient" in (
        capabilities.execution_features
    )


def test_ec7_unsupported_programs_are_rejected() -> None:
    program = CCIRProgram(
        name="unsupported",
        variable_count=1,
        boundary_variables=(0,),
        constraints=(
            CCIRConstraint(
                family=CLAUSE_CONSTRAINT_FAMILY,
                payload=CCIRClausePayload(
                    literals=(),
                ),
            ),
        ),
    )

    with pytest.raises(
        UnsupportedBackendCapabilityError,
    ):
        compile_backend(
            program,
            RCBackend(),
        )


def test_ec8_provenance_remains_available_through_execution(
    monkeypatch,
) -> None:
    import src.spice_model

    program = _program()
    artifact = RCBackend().compile(program)

    required_elements = tuple(
        element_id
        for element_id, _ in artifact.topology
    )

    validate_artifact_provenance(
        artifact,
        required_elements,
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

    assert prepared.provenance == artifact.provenance

    monkeypatch.setattr(
        src.spice_model,
        "_run_ngspice",
        lambda netlist_path, log_path: (
            log_path.write_text(
                "fake",
                encoding="utf-8",
            )
        ),
    )

    monkeypatch.setattr(
        src.spice_model,
        "_read_measured_voltage",
        lambda log_path: 3.5,
    )

    observable = execute_rc(
        prepared
    )

    assert observable.provenance == artifact.provenance
    assert observable.provenance == prepared.provenance
