from __future__ import annotations

import hashlib

import pytest

from src.backends.fpga_ccir import FPGA_SPECIFICATION
from src.ccir_lower_parity import lower_parity_instance_to_ccir
from src.compiler import DEFAULT_XOR_INSTANCE
from src.observable_execution import ObservableExecution
from src.physical_build_provenance import (
    BuildInputRecord,
    BuildToolIdentity,
    build_manifest_for_prepared_execution,
)
from src.physical_device_programming import (
    programming_record_from_build,
)
from src.physical_evidence_verification import (
    verify_evidence_record_bytes,
    verify_evidence_set_bytes,
)
from src.physical_execution_conformance import (
    PhysicalExecutionConformanceResult,
    evaluate_physical_execution_conformance,
)
from src.physical_execution_event import (
    PhysicalExecutionEvent,
    execution_event_from_records,
)
from src.physical_execution_evidence import (
    EvidenceRecord,
    PhysicalExecutionEvidence,
    evidence_from_execution,
    observable_execution_hash,
    prepared_execution_hash,
)
from src.physical_fpga_profile import (
    PHYSICAL_FPGA_PROFILE,
    PHYSICAL_FPGA_PROFILE_ID,
)
from src.tri_backend_validation import validate_tri_backend


BITSTREAM_BYTES = b"rfc0009-synthetic-bitstream\n"
BUILD_REPORT_BYTES = b"build complete\n"
MEASUREMENT_BYTES = b"result_bit=1\n"
PROGRAMMING_BYTES = b"programming complete\n"
STIMULUS_BYTES = b"x0=0 x3=1\n"
TIMING_BYTES = b"timing validation complete\n"


def _sha256(content: bytes) -> str:
    return (
        "sha256:"
        + hashlib.sha256(content).hexdigest()
    )


def _real_fpga_execution():
    program = lower_parity_instance_to_ccir(
        DEFAULT_XOR_INSTANCE
    )

    result = validate_tri_backend(
        program,
        {
            0: 0,
            3: 1,
        },
    )

    return result.fpga


def _records() -> tuple[EvidenceRecord, ...]:
    return (
        EvidenceRecord.from_bytes(
            record_id="bitstream",
            evidence_type="bitstream",
            media_type="application/octet-stream",
            content=BITSTREAM_BYTES,
            description="Synthetic RFC-0009 bitstream identity fixture",
        ),
        EvidenceRecord.from_bytes(
            record_id="build-report",
            evidence_type="build-report",
            media_type="text/plain",
            content=BUILD_REPORT_BYTES,
            description="Synthetic RFC-0009 build report fixture",
        ),
        EvidenceRecord.from_bytes(
            record_id="measurement-log",
            evidence_type="measurement-log",
            media_type="text/plain",
            content=MEASUREMENT_BYTES,
            description="Synthetic RFC-0009 measurement fixture",
        ),
        EvidenceRecord.from_bytes(
            record_id="programming-log",
            evidence_type="programming-log",
            media_type="text/plain",
            content=PROGRAMMING_BYTES,
            description="Synthetic RFC-0009 programming fixture",
        ),
        EvidenceRecord.from_bytes(
            record_id="timing-report",
            evidence_type="timing-report",
            media_type="text/plain",
            content=TIMING_BYTES,
            description="Synthetic RFC-0009 timing fixture",
        ),
    )


def _evidence():
    execution = _real_fpga_execution()

    return evidence_from_execution(
        prepared=execution.prepared,
        observable=execution.observable,
        substrate=(
            ("board_id", "synthetic-board-001"),
            ("device_family", "synthetic-family"),
            ("device_id", "synthetic-device-001"),
            ("device_part", "synthetic-part"),
        ),
        instrumentation=(
            ("observation_interface", "gpio"),
            ("programming_interface", "jtag"),
            ("stimulus_interface", "gpio"),
        ),
        calibration=(
            ("timing_validation_id", "synthetic-timing-001"),
        ),
        records=_records(),
        metadata=(
            ("fixture_kind", "contract-only"),
        ),
    )


def _build():
    execution = _real_fpga_execution()

    payload = execution.prepared.payload
    if not isinstance(payload, str):
        raise AssertionError(
            "RFC-0008 FPGA prepared payload must be Verilog text"
        )

    return build_manifest_for_prepared_execution(
        prepared=execution.prepared,
        physical_profile_id=PHYSICAL_FPGA_PROFILE_ID,
        device_family="synthetic-family",
        device_part="synthetic-part",
        tools=(
            BuildToolIdentity(
                stage="synthesis",
                tool="synthetic-synthesis-tool",
                version="1",
            ),
        ),
        inputs=(
            BuildInputRecord(
                input_id="prepared-verilog",
                media_type="text/x-verilog",
                sha256=_sha256(
                    payload.encode("utf-8")
                ),
            ),
        ),
        bitstream_format="synthetic-bitstream",
        bitstream_sha256=_sha256(
            BITSTREAM_BYTES
        ),
        metadata=(
            ("fixture_kind", "contract-only"),
        ),
    )


def _programming():
    return programming_record_from_build(
        build=_build(),
        board_id="synthetic-board-001",
        device_id="synthetic-device-001",
        programming_interface="jtag",
        programmer="synthetic-programmer",
        programmer_version="1",
        programming_log_sha256=_sha256(
            PROGRAMMING_BYTES
        ),
        metadata=(
            ("fixture_kind", "contract-only"),
        ),
    )


def _event():
    execution = _real_fpga_execution()

    return execution_event_from_records(
        programming=_programming(),
        prepared=execution.prepared,
        observable=execution.observable,
        stimulus_interface="gpio",
        observation_interface="gpio",
        stimulus_record_sha256=_sha256(
            STIMULUS_BYTES
        ),
        measurement_record_sha256=_sha256(
            MEASUREMENT_BYTES
        ),
        metadata=(
            ("fixture_kind", "contract-only"),
        ),
    )


# PE-1 — Canonical prepared-execution identity
def test_pe_1_canonical_prepared_execution_identity() -> None:
    execution = _real_fpga_execution()

    first = prepared_execution_hash(
        execution.prepared
    )
    second = prepared_execution_hash(
        execution.prepared
    )

    assert first == second
    assert first.startswith("sha256:")


# PE-2 — Canonical observable-execution identity
def test_pe_2_canonical_observable_execution_identity() -> None:
    execution = _real_fpga_execution()

    first = observable_execution_hash(
        execution.observable
    )
    second = observable_execution_hash(
        execution.observable
    )

    assert first == second
    assert first.startswith("sha256:")


# PE-3 — External evidence identity
def test_pe_3_external_evidence_identity() -> None:
    record = EvidenceRecord.from_bytes(
        record_id="measurement",
        evidence_type="measurement-log",
        media_type="text/plain",
        content=MEASUREMENT_BYTES,
        description="Measurement",
    )

    assert record.sha256 == _sha256(
        MEASUREMENT_BYTES
    )


# PE-4 — Independent evidence verification
def test_pe_4_independent_evidence_verification() -> None:
    record = EvidenceRecord.from_bytes(
        record_id="measurement",
        evidence_type="measurement-log",
        media_type="text/plain",
        content=MEASUREMENT_BYTES,
        description="Measurement",
    )

    valid = verify_evidence_record_bytes(
        record=record,
        content=MEASUREMENT_BYTES,
    )

    changed = verify_evidence_record_bytes(
        record=record,
        content=b"changed measurement\n",
    )

    assert valid.digest_match
    assert not changed.digest_match


# PE-5 — Profile-defined completeness
def test_pe_5_profile_defined_completeness() -> None:
    execution = _real_fpga_execution()

    complete = evaluate_physical_execution_conformance(
        evidence=_evidence(),
        prepared=execution.prepared,
        observable=execution.observable,
        profile=PHYSICAL_FPGA_PROFILE.evidence_profile(),
    )

    incomplete_evidence = evidence_from_execution(
        prepared=execution.prepared,
        observable=execution.observable,
        substrate=(
            ("board_id", "synthetic-board-001"),
        ),
        instrumentation=_evidence().instrumentation,
        calibration=_evidence().calibration,
        records=_records(),
    )

    incomplete = evaluate_physical_execution_conformance(
        evidence=incomplete_evidence,
        prepared=execution.prepared,
        observable=execution.observable,
        profile=PHYSICAL_FPGA_PROFILE.evidence_profile(),
    )

    assert complete.overall_pass
    assert not incomplete.substrate_complete
    assert not incomplete.overall_pass


# PE-6 — Integrity/completeness separation
def test_pe_6_integrity_and_completeness_are_distinct() -> None:
    execution = _real_fpga_execution()

    conformance = evaluate_physical_execution_conformance(
        evidence=_evidence(),
        prepared=execution.prepared,
        observable=execution.observable,
        profile=PHYSICAL_FPGA_PROFILE.evidence_profile(),
    )

    verification = verify_evidence_set_bytes(
        evidence=_evidence(),
        contents={
            "bitstream": BITSTREAM_BYTES,
            "build-report": BUILD_REPORT_BYTES,
            "measurement-log": b"tampered\n",
            "programming-log": PROGRAMMING_BYTES,
            "timing-report": TIMING_BYTES,
        },
    )

    assert conformance.evidence_types_complete
    assert conformance.record_integrity_valid
    assert not verification.overall_pass


# PE-7 — Build provenance
def test_pe_7_build_provenance() -> None:
    execution = _real_fpga_execution()
    build = _build()

    assert build.backend_id == "fpga"
    assert build.backend_version == "1"
    assert build.prepared_execution_hash == (
        prepared_execution_hash(
            execution.prepared
        )
    )
    assert build.device_family == "synthetic-family"
    assert build.device_part == "synthetic-part"
    assert build.tools
    assert build.inputs
    assert build.bitstream_sha256 == _sha256(
        BITSTREAM_BYTES
    )


# PE-8 — Programming binding
def test_pe_8_programming_binding() -> None:
    build = _build()
    programming = _programming()

    assert programming.build_manifest_hash == (
        build.manifest_hash
    )
    assert programming.bitstream_sha256 == (
        build.bitstream_sha256
    )
    assert programming.board_id == (
        "synthetic-board-001"
    )
    assert programming.device_id == (
        "synthetic-device-001"
    )
    assert programming.programming_log_sha256 == (
        _sha256(PROGRAMMING_BYTES)
    )


# PE-9 — Execution-event binding
def test_pe_9_execution_event_binding() -> None:
    execution = _real_fpga_execution()
    programming = _programming()
    event = _event()

    assert event.programming_record_hash == (
        programming.record_hash
    )
    assert event.prepared_execution_hash == (
        prepared_execution_hash(
            execution.prepared
        )
    )
    assert event.observable_execution_hash == (
        observable_execution_hash(
            execution.observable
        )
    )
    assert event.stimulus_record_sha256 == (
        _sha256(STIMULUS_BYTES)
    )
    assert event.measurement_record_sha256 == (
        _sha256(MEASUREMENT_BYTES)
    )


# PE-10 — Backend identity consistency
def test_pe_10_backend_identity_consistency() -> None:
    execution = _real_fpga_execution()

    mismatched = ObservableExecution(
        backend_id="digital",
        backend_version="1",
        observations=execution.observable.observations,
        provenance=execution.observable.provenance,
        metadata=execution.observable.metadata,
    )

    with pytest.raises(
        ValueError,
        match="backend IDs do not match",
    ):
        execution_event_from_records(
            programming=_programming(),
            prepared=execution.prepared,
            observable=mismatched,
            stimulus_interface="gpio",
            observation_interface="gpio",
            stimulus_record_sha256=_sha256(
                STIMULUS_BYTES
            ),
            measurement_record_sha256=_sha256(
                MEASUREMENT_BYTES
            ),
        )


# PE-11 — Semantic separation
def test_pe_11_semantic_separation() -> None:
    fields = set(
        PhysicalExecutionConformanceResult.__dataclass_fields__
    )

    forbidden = {
        "decoded",
        "expected",
        "expected_answer",
        "reference",
        "reference_result",
        "semantic_match",
    }

    assert fields.isdisjoint(
        forbidden
    )


# PE-12 — Restricted semantic readout
def test_pe_12_restricted_semantic_readout() -> None:
    evidence_text = repr(
        _evidence().to_evidence_dict()
    ).lower()

    for forbidden in (
        "decoded",
        "expected_answer",
        "reference_result",
        "semantic_match",
    ):
        assert forbidden not in evidence_text


# PE-13 — Deterministic record identity
def test_pe_13_deterministic_record_identity() -> None:
    assert _evidence().evidence_hash == (
        _evidence().evidence_hash
    )

    assert _build().manifest_hash == (
        _build().manifest_hash
    )

    assert _programming().record_hash == (
        _programming().record_hash
    )

    assert _event().event_hash == (
        _event().event_hash
    )


# PE-14 — Explicit physical profile
def test_pe_14_explicit_physical_profile() -> None:
    profile = PHYSICAL_FPGA_PROFILE
    evidence_profile = profile.evidence_profile()

    assert profile.profile_id == (
        PHYSICAL_FPGA_PROFILE_ID
    )

    assert evidence_profile.profile_id == (
        PHYSICAL_FPGA_PROFILE_ID
    )

    assert _build().physical_profile_id == (
        PHYSICAL_FPGA_PROFILE_ID
    )

    assert _programming().physical_profile_id == (
        PHYSICAL_FPGA_PROFILE_ID
    )

    assert _event().physical_profile_id == (
        PHYSICAL_FPGA_PROFILE_ID
    )


# PE-15 — No implicit physical-execution claim
def test_pe_15_no_implicit_physical_execution_claim() -> None:
    model_fields = (
        set(
            PhysicalExecutionEvidence.__dataclass_fields__
        )
        | set(
            PhysicalExecutionEvent.__dataclass_fields__
        )
        | set(
            PhysicalExecutionConformanceResult.__dataclass_fields__
        )
    )

    forbidden = {
        "executed",
        "physical_execution_pass",
        "physical_execution_proven",
        "semantic_match",
    }

    assert model_fields.isdisjoint(
        forbidden
    )


# PF-1 — RFC-0008 backend binding
def test_pf_1_rfc0008_backend_binding() -> None:
    execution = _real_fpga_execution()

    assert FPGA_SPECIFICATION.backend_id == "fpga"
    assert FPGA_SPECIFICATION.backend_version == "1"

    assert execution.prepared.backend_id == "fpga"
    assert execution.prepared.backend_version == "1"

    assert execution.observable.backend_id == "fpga"
    assert execution.observable.backend_version == "1"

    assert PHYSICAL_FPGA_PROFILE.backend_id == "fpga"
    assert PHYSICAL_FPGA_PROFILE.backend_version == "1"


# PF-2 — Prepared HDL binding
def test_pf_2_prepared_hdl_binding() -> None:
    execution = _real_fpga_execution()
    build = _build()

    assert isinstance(
        execution.prepared.payload,
        str,
    )

    assert "module" in (
        execution.prepared.payload
    )

    assert build.prepared_execution_hash == (
        prepared_execution_hash(
            execution.prepared
        )
    )


# PF-3 — Device target identity
def test_pf_3_device_target_identity() -> None:
    evidence = _evidence()
    programming = _programming()

    substrate = dict(
        evidence.substrate
    )

    assert substrate == {
        "board_id": "synthetic-board-001",
        "device_family": "synthetic-family",
        "device_id": "synthetic-device-001",
        "device_part": "synthetic-part",
    }

    assert programming.board_id == (
        "synthetic-board-001"
    )
    assert programming.device_family == (
        "synthetic-family"
    )
    assert programming.device_part == (
        "synthetic-part"
    )
    assert programming.device_id == (
        "synthetic-device-001"
    )


# PF-4 — Build identity
def test_pf_4_build_identity() -> None:
    build = _build()

    assert build.tools == (
        BuildToolIdentity(
            stage="synthesis",
            tool="synthetic-synthesis-tool",
            version="1",
        ),
    )

    assert len(build.inputs) == 1
    assert build.inputs[0].input_id == (
        "prepared-verilog"
    )

    assert build.bitstream_sha256 == (
        _sha256(BITSTREAM_BYTES)
    )


# PF-5 — Programming identity
def test_pf_5_programming_identity() -> None:
    programming = _programming()

    assert programming.programming_interface == (
        "jtag"
    )
    assert programming.programmer == (
        "synthetic-programmer"
    )
    assert programming.programmer_version == "1"
    assert programming.programming_log_sha256 == (
        _sha256(PROGRAMMING_BYTES)
    )


# PF-6 — Stimulus identity
def test_pf_6_stimulus_identity() -> None:
    event = _event()

    assert event.stimulus_interface == "gpio"
    assert event.stimulus_record_sha256 == (
        _sha256(STIMULUS_BYTES)
    )


# PF-7 — Observation identity
def test_pf_7_observation_identity() -> None:
    execution = _real_fpga_execution()
    event = _event()

    assert event.observation_interface == "gpio"
    assert event.measurement_record_sha256 == (
        _sha256(MEASUREMENT_BYTES)
    )
    assert event.observable_execution_hash == (
        observable_execution_hash(
            execution.observable
        )
    )


# PF-8 — Timing evidence
def test_pf_8_timing_evidence() -> None:
    profile = (
        PHYSICAL_FPGA_PROFILE.evidence_profile()
    )

    assert profile.required_calibration_fields == (
        "timing_validation_id",
    )

    assert "timing-report" in (
        profile.required_evidence_types
    )

    assert dict(
        _evidence().calibration
    )["timing_validation_id"] == (
        "synthetic-timing-001"
    )


# PF-9 — Required evidence types
def test_pf_9_required_evidence_types() -> None:
    execution = _real_fpga_execution()
    evidence = _evidence()
    profile = (
        PHYSICAL_FPGA_PROFILE.evidence_profile()
    )

    required = set(
        profile.required_evidence_types
    )

    present = {
        record.evidence_type
        for record in evidence.records
    }

    result = evaluate_physical_execution_conformance(
        evidence=evidence,
        prepared=execution.prepared,
        observable=execution.observable,
        profile=profile,
    )

    assert present == required
    assert result.evidence_types_complete
    assert result.overall_pass


# PF-10 — Semantic independence
def test_pf_10_semantic_independence() -> None:
    objects = (
        _evidence().to_evidence_dict(),
        _build().to_manifest_dict(),
        _programming().to_record_dict(),
        _event().to_event_dict(),
    )

    text = repr(
        objects
    ).lower()

    for forbidden in (
        "expected_answer",
        "reference_result",
        "semantic_match",
    ):
        assert forbidden not in text

    result_fields = set(
        PhysicalExecutionConformanceResult.__dataclass_fields__
    )

    assert "semantic_match" not in result_fields
