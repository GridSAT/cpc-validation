from __future__ import annotations

from src.backend import validate_artifact_provenance
from src.backends.digital_ccir import (
    DIGITAL_CAPABILITIES,
    DIGITAL_SPECIFICATION,
    DigitalBackend,
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


def _program() -> CCIRProgram:
    return CCIRProgram(
        name="digital-parity",
        variable_count=4,
        boundary_variables=(
            0,
            3,
        ),
        constraints=(
            CCIRConstraint(
                family=PARITY_CONSTRAINT_FAMILY,
                payload=CCIRParityPayload(
                    variables=(
                        0,
                        1,
                        2,
                    ),
                    parity=0,
                ),
            ),
            CCIRConstraint(
                family=PARITY_CONSTRAINT_FAMILY,
                payload=CCIRParityPayload(
                    variables=(
                        1,
                        2,
                        3,
                    ),
                    parity=1,
                ),
            ),
        ),
    )


def test_digital_backend_declares_parity_capability() -> None:
    assert DIGITAL_CAPABILITIES.supports_constraint_family(
        PARITY_CONSTRAINT_FAMILY
    )


def test_digital_backend_has_distinct_identity() -> None:
    assert DIGITAL_SPECIFICATION.backend_id == "digital"

    assert (
        DIGITAL_SPECIFICATION.get_fixed_parameter(
            "execution_model"
        )
        == "deterministic-enumeration-v1"
    )


def test_digital_backend_compiles_ccir() -> None:
    artifact = compile_backend(
        _program(),
        DigitalBackend(),
    )

    metadata = dict(
        artifact.metadata
    )

    assert metadata["backend_id"] == "digital"
    assert metadata["program_name"] == "digital-parity"
    assert metadata["constraint_count"] == 2


def test_digital_artifact_uses_instruction_topology() -> None:
    artifact = DigitalBackend().compile(
        _program()
    )

    topology = dict(
        artifact.topology
    )

    assert topology[
        "instruction:parity:0"
    ] == (
        "parity-instruction",
        (
            0,
            1,
            2,
        ),
        0,
    )

    assert topology[
        "instruction:parity:1"
    ] == (
        "parity-instruction",
        (
            1,
            2,
            3,
        ),
        1,
    )


def test_digital_artifact_does_not_materialize_rc_candidates() -> None:
    artifact = DigitalBackend().compile(
        _program()
    )

    element_ids = tuple(
        element_id
        for element_id, _ in artifact.topology
    )

    assert not any(
        element_id.startswith("candidate:")
        for element_id in element_ids
    )

    assert not any(
        element_id.startswith("node:")
        for element_id in element_ids
    )


def test_digital_artifact_has_complete_provenance() -> None:
    artifact = DigitalBackend().compile(
        _program()
    )

    required_elements = tuple(
        element_id
        for element_id, _ in artifact.topology
    )

    validate_artifact_provenance(
        artifact,
        required_elements,
    )


def test_digital_constraint_provenance_resolves_to_ccir() -> None:
    artifact = DigitalBackend().compile(
        _program()
    )

    provenance = dict(
        artifact.provenance
    )

    first = provenance[
        "instruction:parity:0"
    ]

    assert tuple(
        (
            origin.kind,
            origin.identifier,
        )
        for origin in first.ccir_origins
    ) == (
        (
            "constraint",
            "0",
        ),
    )

    assert tuple(
        rule.rule_id
        for rule in first.backend_rules
    ) == (
        "digital.parity-instruction",
    )
