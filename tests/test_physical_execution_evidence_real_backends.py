from __future__ import annotations

import pytest

from src.ccir_lower_parity import (
    lower_parity_instance_to_ccir,
)
from src.compiler import DEFAULT_XOR_INSTANCE
from src.observable_execution import ObservableExecution
from src.physical_execution_evidence import (
    evidence_from_execution,
    observable_execution_hash,
    prepared_execution_hash,
)
from src.prepared_execution import PreparedExecution
from src.tri_backend_validation import (
    validate_tri_backend,
)


def _tri_backend_result():
    program = lower_parity_instance_to_ccir(
        DEFAULT_XOR_INSTANCE
    )

    return validate_tri_backend(
        program,
        {
            0: 0,
            3: 1,
        },
    )


@pytest.mark.parametrize(
    "backend_name",
    (
        "rc",
        "digital",
        "fpga",
    ),
)
def test_real_backend_execution_binds_to_evidence(
    backend_name: str,
) -> None:
    result = _tri_backend_result()
    execution = getattr(
        result,
        backend_name,
    )

    evidence = evidence_from_execution(
        prepared=execution.prepared,
        observable=execution.observable,
        substrate=(
            ("profile", f"{backend_name}-current"),
        ),
    )

    prepared_metadata = dict(
        execution.prepared.metadata
    )

    observable_metadata = dict(
        execution.observable.metadata
    )

    assert evidence.backend_id == (
        execution.prepared.backend_id
    )

    assert evidence.backend_id == (
        execution.observable.backend_id
    )

    assert evidence.backend_version == (
        execution.prepared.backend_version
    )

    assert evidence.backend_version == (
        execution.observable.backend_version
    )

    assert evidence.preparation_id == (
        prepared_metadata["preparation_id"]
    )

    assert evidence.execution_id == (
        observable_metadata["execution_id"]
    )

    assert evidence.execution_engine == (
        observable_metadata["execution_engine"]
    )

    assert evidence.execution_engine_version == (
        observable_metadata[
            "execution_engine_version"
        ]
    )

    assert evidence.prepared_execution_hash == (
        prepared_execution_hash(
            execution.prepared
        )
    )

    assert evidence.observable_execution_hash == (
        observable_execution_hash(
            execution.observable
        )
    )


def test_real_backends_produce_distinct_execution_bindings() -> None:
    result = _tri_backend_result()

    rc = evidence_from_execution(
        prepared=result.rc.prepared,
        observable=result.rc.observable,
    )

    digital = evidence_from_execution(
        prepared=result.digital.prepared,
        observable=result.digital.observable,
    )

    fpga = evidence_from_execution(
        prepared=result.fpga.prepared,
        observable=result.fpga.observable,
    )

    assert len(
        {
            rc.prepared_execution_hash,
            digital.prepared_execution_hash,
            fpga.prepared_execution_hash,
        }
    ) == 3

    assert len(
        {
            rc.observable_execution_hash,
            digital.observable_execution_hash,
            fpga.observable_execution_hash,
        }
    ) == 3

    assert len(
        {
            rc.evidence_hash,
            digital.evidence_hash,
            fpga.evidence_hash,
        }
    ) == 3


def test_prepared_binding_changes_when_prepared_state_changes() -> None:
    result = _tri_backend_result()

    original = result.digital.prepared

    mutated = PreparedExecution(
        backend_id=original.backend_id,
        backend_version=original.backend_version,
        payload=(
            original.payload,
            ("rfc0009-test-mutation", 1),
        ),
        interface=original.interface,
        decoder_specification=(
            original.decoder_specification
        ),
        provenance=original.provenance,
        metadata=original.metadata,
    )

    assert (
        prepared_execution_hash(original)
        != prepared_execution_hash(mutated)
    )


def test_observable_binding_changes_when_observation_changes() -> None:
    result = _tri_backend_result()

    original = result.digital.observable

    mutated = ObservableExecution(
        backend_id=original.backend_id,
        backend_version=original.backend_version,
        observations=(
            ("result_bit", 1 - int(
                dict(original.observations)[
                    "result_bit"
                ]
            )),
        ),
        provenance=original.provenance,
        metadata=original.metadata,
    )

    assert (
        observable_execution_hash(original)
        != observable_execution_hash(mutated)
    )


def test_execution_evidence_contains_no_decoded_or_reference_result() -> None:
    result = _tri_backend_result()

    evidence = evidence_from_execution(
        prepared=result.fpga.prepared,
        observable=result.fpga.observable,
    )

    data = evidence.to_evidence_dict()

    text = repr(data).lower()

    assert "decoded" not in text
    assert "reference" not in text
    assert "semantic_match" not in text
    assert "overall_pass" not in text
