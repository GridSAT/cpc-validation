from __future__ import annotations

import hashlib
import json
from pathlib import Path

from build_p1_physical_artifacts import (
    BITSTREAM_NAME,
    MANIFEST_NAME,
    REPORT_NAME as BUILD_REPORT_NAME,
    TIMING_REPORT_NAME,
    VERILOG_NAME,
    build_p1_inputs,
)
from record_p1_physical_execution import (
    EXECUTION_EVENT_NAME,
    MEASUREMENT_NAME,
    OBSERVABLE_NAME,
    PHOTO_NAME,
    STIMULUS_NAME,
    _atomic_write,
    _load_programming_record,
)
from record_p1_physical_programming import (
    EVIDENCE_DIRECTORY,
    PROGRAMMING_LOG_NAME,
    PROGRAMMING_RECORD_NAME,
    PROGRAMMING_REPORT_NAME,
    _load_build_manifest,
)
from src.observable_execution import ObservableExecution
from src.physical_evidence_verification import verify_evidence_set_files
from src.physical_execution_conformance import (
    evaluate_physical_execution_conformance,
)
from src.physical_execution_evidence import (
    EvidenceRecord,
    evidence_from_execution,
    observable_execution_hash,
    prepared_execution_hash,
)
from src.physical_fpga_profile import (
    PHYSICAL_FPGA_PROFILE,
    PHYSICAL_FPGA_PROFILE_ID,
)
from src.physical_lattice_up5k_build import (
    LATTICE_UP5K_TIMING_VALIDATION_ID,
)
from validate_p1_physical_execution import _load_event


EVIDENCE_ENVELOPE_NAME = "p1-physical-execution-evidence.json"
CONFORMANCE_REPORT_NAME = "p1-physical-evidence-conformance-report.json"


def _sha256(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def _require_equal(actual: object, expected: object, name: str) -> None:
    if actual != expected:
        raise ValueError(f"physical evidence binding mismatch: {name}")


def _record(
    directory: Path,
    *,
    record_id: str,
    filename: str,
    evidence_type: str,
    media_type: str,
    description: str,
) -> tuple[EvidenceRecord, Path]:
    path = directory / filename
    return (
        EvidenceRecord.from_bytes(
            record_id=record_id,
            evidence_type=evidence_type,
            media_type=media_type,
            content=path.read_bytes(),
            description=description,
        ),
        path,
    )


def _evidence_records(
    directory: Path,
) -> tuple[tuple[EvidenceRecord, ...], dict[str, Path]]:
    specifications = (
        (
            "bitstream",
            BITSTREAM_NAME,
            "bitstream",
            "application/octet-stream",
            "Programmed iCE40 SRAM bitstream.",
        ),
        (
            "build-manifest",
            MANIFEST_NAME,
            "build-manifest",
            "application/json",
            "RFC-0009 physical build manifest.",
        ),
        (
            "build-report",
            BUILD_REPORT_NAME,
            "build-report",
            "application/json",
            "Deterministic physical build report.",
        ),
        (
            "device-programming-record",
            PROGRAMMING_RECORD_NAME,
            "device-programming-record",
            "application/json",
            "RFC-0009 device programming binding.",
        ),
        (
            "execution-event",
            EXECUTION_EVENT_NAME,
            "execution-event",
            "application/json",
            "RFC-0009 physical execution event.",
        ),
        (
            "measurement-log",
            MEASUREMENT_NAME,
            "measurement-log",
            "application/json",
            "Restricted LED measurement record.",
        ),
        (
            "observable-execution",
            OBSERVABLE_NAME,
            "observable-execution",
            "application/json",
            "Admitted observable execution record.",
        ),
        (
            "physical-observation",
            PHOTO_NAME,
            "physical-observation",
            "image/heic",
            "Original user-supplied physical observation.",
        ),
        (
            "physical-verilog",
            VERILOG_NAME,
            "build-input",
            "text/x-verilog",
            "Physical FPGA top-level build input.",
        ),
        (
            "programming-log",
            PROGRAMMING_LOG_NAME,
            "programming-log",
            "application/json",
            "Guarded device-programming action result.",
        ),
        (
            "programming-report",
            PROGRAMMING_REPORT_NAME,
            "programming-report",
            "application/json",
            "Programming-stage status report.",
        ),
        (
            "stimulus-log",
            STIMULUS_NAME,
            "stimulus-log",
            "application/json",
            "Physical stimulus record.",
        ),
        (
            "timing-report",
            TIMING_REPORT_NAME,
            "timing-report",
            "application/json",
            "Static-combinational nextpnr timing validation.",
        ),
    )
    pairs = tuple(
        _record(
            directory,
            record_id=record_id,
            filename=filename,
            evidence_type=evidence_type,
            media_type=media_type,
            description=description,
        )
        for record_id, filename, evidence_type, media_type, description in (
            specifications
        )
    )
    records = tuple(record for record, _ in pairs)
    paths = {
        record.record_id: path
        for record, path in pairs
    }
    return records, paths


def validate_p1_physical_evidence(
    evidence_directory: Path = EVIDENCE_DIRECTORY,
) -> dict[str, object]:
    """Evaluate P1 evidence completeness without semantic decoding."""

    directory = Path(evidence_directory)
    prepared, _ = build_p1_inputs()
    event = _load_event(directory / EXECUTION_EVENT_NAME)
    programming = _load_programming_record(
        directory / PROGRAMMING_RECORD_NAME
    )
    build = _load_build_manifest(directory / MANIFEST_NAME)
    manifest_bytes = (directory / MANIFEST_NAME).read_bytes()
    manifest = json.loads(manifest_bytes)
    build_report = json.loads((directory / BUILD_REPORT_NAME).read_bytes())
    timing_report = json.loads((directory / TIMING_REPORT_NAME).read_bytes())
    observable_data = json.loads((directory / OBSERVABLE_NAME).read_bytes())
    measurement_bytes = (directory / MEASUREMENT_NAME).read_bytes()
    measurement = json.loads(measurement_bytes)
    stimulus_bytes = (directory / STIMULUS_NAME).read_bytes()
    programming_log_bytes = (directory / PROGRAMMING_LOG_NAME).read_bytes()
    photo_bytes = (directory / PHOTO_NAME).read_bytes()
    bitstream_bytes = (directory / BITSTREAM_NAME).read_bytes()
    verilog_bytes = (directory / VERILOG_NAME).read_bytes()

    for actual, name in (
        (manifest["physical_profile_id"], "build physical profile"),
        (programming.physical_profile_id, "programming physical profile"),
        (event.physical_profile_id, "execution physical profile"),
    ):
        _require_equal(actual, PHYSICAL_FPGA_PROFILE_ID, name)

    _require_equal(
        programming.build_manifest_hash,
        manifest["manifest_hash"],
        "programming to build manifest",
    )
    _require_equal(
        build.prepared_execution_hash,
        prepared_execution_hash(prepared),
        "build manifest to prepared execution",
    )
    _require_equal(
        programming.bitstream_sha256,
        manifest["bitstream"]["sha256"],
        "programming to bitstream",
    )
    _require_equal(
        event.programming_record_hash,
        programming.record_hash,
        "execution to programming record",
    )
    _require_equal(
        event.prepared_execution_hash,
        prepared_execution_hash(prepared),
        "execution event to prepared execution",
    )
    _require_equal(
        event.measurement_record_sha256,
        _sha256(measurement_bytes),
        "execution to measurement record",
    )
    _require_equal(
        event.stimulus_record_sha256,
        _sha256(stimulus_bytes),
        "execution to stimulus record",
    )
    _require_equal(
        programming.programming_log_sha256,
        _sha256(programming_log_bytes),
        "programming record to programming log",
    )
    _require_equal(
        measurement["capture"]["sha256"],
        _sha256(photo_bytes),
        "measurement record to physical observation",
    )
    _require_equal(
        manifest["bitstream"]["sha256"],
        _sha256(bitstream_bytes),
        "build manifest to bitstream bytes",
    )
    _require_equal(
        build_report["status"],
        "built-not-programmed",
        "build report claim boundary",
    )
    for actual, expected, name in (
        (
            build_report["build_manifest_hash"],
            manifest["manifest_hash"],
            "build report to manifest identity",
        ),
        (
            build_report["digests"]["build_manifest"],
            _sha256(manifest_bytes),
            "build report to manifest bytes",
        ),
        (
            build_report["digests"]["bitstream"],
            _sha256(bitstream_bytes),
            "build report to bitstream bytes",
        ),
        (
            build_report["digests"]["physical_verilog"],
            _sha256(verilog_bytes),
            "build report to physical Verilog",
        ),
        (
            build_report["digests"]["timing_report"],
            _sha256((directory / TIMING_REPORT_NAME).read_bytes()),
            "build report to timing report",
        ),
        (
            build_report["artifacts"]["timing_report"],
            TIMING_REPORT_NAME,
            "build report timing artifact name",
        ),
        (
            timing_report["timing_validation_id"],
            LATTICE_UP5K_TIMING_VALIDATION_ID,
            "timing validation identity",
        ),
        (
            timing_report["binding"]["bitstream_sha256"],
            _sha256(bitstream_bytes),
            "timing report to bitstream",
        ),
        (
            timing_report["binding"]["routed_configuration_sha256"],
            build_report["digests"]["routed_configuration"],
            "timing report to routed configuration",
        ),
        (
            timing_report["target"]["device_family"],
            build.device_family,
            "timing report device family",
        ),
        (
            timing_report["target"]["device_part"],
            build.device_part,
            "timing report device part",
        ),
        (
            timing_report["status"],
            "pass-static-combinational-no-interior-paths",
            "timing report status",
        ),
    ):
        _require_equal(actual, expected, name)

    observable = ObservableExecution(
        backend_id=observable_data["backend"]["id"],
        backend_version=observable_data["backend"]["version"],
        observations=tuple(sorted(observable_data["observations"].items())),
        provenance=prepared.provenance,
        metadata=(
            ("execution_engine", "physical-fpga-device"),
            ("execution_engine_version", "lattice-icebreaker-up5k"),
            ("execution_id", "fpga.physical-device.v1"),
        ),
    )
    _require_equal(
        observable_data["observable_execution_hash"],
        event.observable_execution_hash,
        "observable evidence to execution event",
    )
    _require_equal(
        observable_execution_hash(observable),
        event.observable_execution_hash,
        "execution event to observable execution",
    )
    _require_equal(
        observable_data["measurement_record_sha256"],
        event.measurement_record_sha256,
        "observable evidence to measurement record",
    )

    place_route_tools = tuple(
        item
        for item in build.tools
        if item.stage == "place-route"
    )
    if len(place_route_tools) != 1:
        raise ValueError("physical build requires one place-route tool")
    _require_equal(
        timing_report["tool"]["name"],
        place_route_tools[0].tool,
        "timing report tool identity",
    )
    _require_equal(
        timing_report["tool"]["version"],
        place_route_tools[0].version,
        "timing report tool version",
    )

    records, paths = _evidence_records(directory)
    evidence = evidence_from_execution(
        prepared=prepared,
        observable=observable,
        substrate=(
            ("board_id", programming.board_id),
            ("device_family", programming.device_family),
            ("device_id", programming.device_id),
            ("device_part", programming.device_part),
        ),
        instrumentation=(
            ("observation_interface", event.observation_interface),
            ("programming_interface", programming.programming_interface),
            ("stimulus_interface", event.stimulus_interface),
        ),
        calibration=(
            (
                "timing_validation_id",
                timing_report["timing_validation_id"],
            ),
        ),
        records=records,
        metadata=tuple(
            sorted(
                (
                    ("build_manifest_hash", manifest["manifest_hash"]),
                    ("execution_event_hash", event.event_hash),
                    ("physical_profile_id", PHYSICAL_FPGA_PROFILE_ID),
                    ("programming_record_hash", programming.record_hash),
                    ("trust_boundary", measurement["trust_boundary"]),
                )
            )
        ),
    )
    profile = PHYSICAL_FPGA_PROFILE.evidence_profile()
    conformance = evaluate_physical_execution_conformance(
        evidence=evidence,
        prepared=prepared,
        observable=observable,
        profile=profile,
    )
    verification = verify_evidence_set_files(
        evidence=evidence,
        paths=paths,
    )
    checks = {
        "backend_identity_match": conformance.backend_identity_match,
        "calibration_complete": conformance.calibration_complete,
        "evidence_types_complete": conformance.evidence_types_complete,
        "execution_identity_match": conformance.execution_identity_match,
        "external_record_integrity": verification.overall_pass,
        "instrumentation_complete": conformance.instrumentation_complete,
        "lifecycle_binding_match": conformance.lifecycle_binding_match,
        "record_integrity_valid": conformance.record_integrity_valid,
        "substrate_complete": conformance.substrate_complete,
    }
    overall_pass = conformance.overall_pass and verification.overall_pass
    if not overall_pass:
        raise ValueError("P1 RFC-0009 physical evidence is not conformant")

    report: dict[str, object] = {
        "schema": "cpc.p1-physical-evidence-conformance-report.v1",
        "status": "rfc0009-physical-evidence-conformant",
        "profile_id": profile.profile_id,
        "overall_pass": overall_pass,
        "checks": checks,
        "requirements": {
            "calibration_fields": list(profile.required_calibration_fields),
            "evidence_types": list(profile.required_evidence_types),
            "instrumentation_fields": list(
                profile.required_instrumentation_fields
            ),
            "substrate_fields": list(profile.required_substrate_fields),
        },
        "evidence_envelope": EVIDENCE_ENVELOPE_NAME,
        "evidence_hash": evidence.evidence_hash,
        "records": {
            record.record_id: {
                "artifact": paths[record.record_id].name,
                "evidence_type": record.evidence_type,
                "sha256": record.sha256,
            }
            for record in records
        },
        "semantic_correctness_claimed": False,
        "trust_boundary": measurement["trust_boundary"],
    }
    _atomic_write(
        directory / EVIDENCE_ENVELOPE_NAME,
        evidence.to_json().encode("utf-8"),
    )
    _atomic_write(
        directory / CONFORMANCE_REPORT_NAME,
        (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    return report


def main() -> None:
    report = validate_p1_physical_evidence()
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
