from __future__ import annotations

import pytest

from src.backends.digital_ccir import (
    DIGITAL_SPECIFICATION,
    DigitalBackend,
)
from src.backends.digital_run import run_digital_execution
from src.backends.rc_ccir import (
    RC_SPECIFICATION,
    RCBackend,
)
from src.backends.rc_run import run_rc_execution
from src.ccir import (
    CCIRConstraint,
    CCIRProgram,
)
from src.ccir_parity import (
    CCIRParityPayload,
    PARITY_CONSTRAINT_FAMILY,
)
from src.cross_backend_validation import (
    CrossBackendValidationResult,
    validate_cross_backend,
)
from src.physical_validation import (
    evaluate_ccir_continuation,
)


def _program() -> CCIRProgram:
    return CCIRProgram(
        name="rfc0005-conformance",
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


def _boundary() -> dict[int, int]:
    return {
        0: 0,
        3: 1,
    }


# CB-1 — Canonical Input Identity

def test_cb1_backends_consume_same_canonical_ccir() -> None:
    program = _program()

    rc_artifact = RCBackend().compile(program)
    digital_artifact = DigitalBackend().compile(program)

    assert dict(rc_artifact.metadata)["program_name"] == program.name
    assert dict(digital_artifact.metadata)["program_name"] == program.name


# CB-2 — Independent Compilation

def test_cb2_backends_compile_independent_artifacts() -> None:
    program = _program()

    rc_artifact = RCBackend().compile(program)
    digital_artifact = DigitalBackend().compile(program)

    assert dict(rc_artifact.metadata)["backend_id"] == "rc"
    assert dict(digital_artifact.metadata)["backend_id"] == "digital"

    assert rc_artifact is not digital_artifact
    assert rc_artifact.topology != digital_artifact.topology


# CB-3 — Independent Execution Lifecycle

def test_cb3_backends_traverse_independent_execution_lifecycles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.spice_model

    monkeypatch.setattr(
        src.spice_model,
        "_run_ngspice",
        lambda netlist_path, log_path: log_path.write_text(
            "vout_final = 5.0\n",
            encoding="utf-8",
        ),
    )

    program = _program()
    boundary = _boundary()

    rc_result = run_rc_execution(
        program,
        RCBackend().compile(program),
        boundary,
        RC_SPECIFICATION,
    )

    digital_result = run_digital_execution(
        program,
        DigitalBackend().compile(program),
        boundary,
        DIGITAL_SPECIFICATION,
    )

    assert rc_result.prepared.backend_id == "rc"
    assert rc_result.observable.backend_id == "rc"

    assert digital_result.prepared.backend_id == "digital"
    assert digital_result.observable.backend_id == "digital"

    assert (
        dict(rc_result.prepared.metadata)["preparation_id"]
        !=
        dict(digital_result.prepared.metadata)["preparation_id"]
    )


# CB-4 — Backend Heterogeneity

def test_cb4_reference_backends_are_structurally_heterogeneous() -> None:
    program = _program()

    rc_artifact = RCBackend().compile(program)
    digital_artifact = DigitalBackend().compile(program)

    rc_types = {
        value[0]
        for _, value in rc_artifact.topology
        if isinstance(value, tuple) and value
    }

    digital_types = {
        value[0]
        for _, value in digital_artifact.topology
        if isinstance(value, tuple) and value
    }

    assert rc_artifact.topology != digital_artifact.topology
    assert rc_types != digital_types

    assert "deterministic-digital" in (
        DIGITAL_SPECIFICATION.capabilities.execution_features
    )

    assert "deterministic-digital" not in (
        RC_SPECIFICATION.capabilities.execution_features
    )


# CB-5 — Reference Isolation

def test_cb5_backend_modules_do_not_import_reference_evaluator() -> None:
    from pathlib import Path

    backend_files = (
        "src/backends/rc_ccir.py",
        "src/backends/rc_prepare.py",
        "src/backends/rc_execute.py",
        "src/backends/rc_decode.py",
        "src/backends/rc_run.py",
        "src/backends/digital_ccir.py",
        "src/backends/digital_prepare.py",
        "src/backends/digital_execute.py",
        "src/backends/digital_decode.py",
        "src/backends/digital_run.py",
    )

    forbidden = (
        "evaluate_ccir_continuation",
        "evaluate_ccir_program",
        "physical_validation",
        "ccir_reference",
        "cross_backend_validation",
    )

    for filename in backend_files:
        text = Path(filename).read_text(
            encoding="utf-8"
        )

        for symbol in forbidden:
            assert symbol not in text, (
                f"{filename} violates RFC-0005 reference isolation "
                f"through {symbol!r}"
            )


# CB-6 — Post-Execution Comparison

def test_cb6_reference_evaluation_occurs_after_both_backend_runs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import src.cross_backend_validation as module

    events: list[str] = []

    original_rc = module.run_rc_execution
    original_digital = module.run_digital_execution
    original_reference = module.evaluate_ccir_continuation

    def rc_wrapper(*args, **kwargs):
        events.append("rc")
        return original_rc(*args, **kwargs)

    def digital_wrapper(*args, **kwargs):
        events.append("digital")
        return original_digital(*args, **kwargs)

    def reference_wrapper(*args, **kwargs):
        events.append("reference")
        return original_reference(*args, **kwargs)

    monkeypatch.setattr(
        module,
        "run_rc_execution",
        rc_wrapper,
    )

    monkeypatch.setattr(
        module,
        "run_digital_execution",
        digital_wrapper,
    )

    monkeypatch.setattr(
        module,
        "evaluate_ccir_continuation",
        reference_wrapper,
    )

    validate_cross_backend(
        _program(),
        _boundary(),
    )

    assert events == [
        "rc",
        "digital",
        "reference",
    ]


# CB-7 — Agreement Separation

def test_cb7_backend_agreement_does_not_imply_pass() -> None:
    result = CrossBackendValidationResult(
        rc=object(),
        digital=object(),
        reference_result=1,
        backend_agreement=True,
        rc_semantic_match=False,
        digital_semantic_match=False,
    )

    assert result.backend_agreement
    assert not result.passed


# CB-8 — Independent Semantic Match

def test_cb8_each_backend_is_compared_with_reference() -> None:
    result = validate_cross_backend(
        _program(),
        _boundary(),
    )

    reference = evaluate_ccir_continuation(
        _program(),
        _boundary(),
    )

    assert result.reference_result == reference

    assert result.rc_semantic_match == (
        result.rc.decoded
        == reference
    )

    assert result.digital_semantic_match == (
        result.digital.decoded
        == reference
    )


# CB-9 — Overall Validation

@pytest.mark.parametrize(
    (
        "agreement",
        "rc_match",
        "digital_match",
        "expected",
    ),
    (
        (True, True, True, True),
        (False, True, True, False),
        (True, False, True, False),
        (True, True, False, False),
        (False, False, False, False),
    ),
)
def test_cb9_pass_requires_all_conditions(
    agreement: bool,
    rc_match: bool,
    digital_match: bool,
    expected: bool,
) -> None:
    result = CrossBackendValidationResult(
        rc=object(),
        digital=object(),
        reference_result=1,
        backend_agreement=agreement,
        rc_semantic_match=rc_match,
        digital_semantic_match=digital_match,
    )

    assert result.passed is expected


# CB-10 — Reproducibility

def test_cb10_validation_preserves_reproducibility_information() -> None:
    result = validate_cross_backend(
        _program(),
        _boundary(),
    )

    rc_prepared_metadata = dict(
        result.rc.prepared.metadata
    )

    digital_prepared_metadata = dict(
        result.digital.prepared.metadata
    )

    rc_execution_metadata = dict(
        result.rc.observable.metadata
    )

    digital_execution_metadata = dict(
        result.digital.observable.metadata
    )

    assert result.rc.prepared.backend_id == "rc"
    assert result.rc.prepared.backend_version

    assert result.digital.prepared.backend_id == "digital"
    assert result.digital.prepared.backend_version

    assert rc_prepared_metadata["boundary_values"] == (
        (0, 0),
        (3, 1),
    )

    assert digital_prepared_metadata["boundary_values"] == (
        (0, 0),
        (3, 1),
    )

    assert rc_prepared_metadata["preparation_id"]
    assert digital_prepared_metadata["preparation_id"]

    assert rc_execution_metadata["execution_id"]
    assert digital_execution_metadata["execution_id"]

    assert result.reference_result in (0, 1)
