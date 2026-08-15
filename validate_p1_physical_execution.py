from __future__ import annotations

import json
from pathlib import Path

from build_p1_physical_artifacts import build_p1_inputs
from record_p1_physical_execution import (
    EVIDENCE_DIRECTORY,
    EXECUTION_EVENT_NAME,
    MEASUREMENT_NAME,
    OBSERVABLE_NAME,
    PHOTO_NAME,
    PROGRAMMING_RECORD_NAME,
    STIMULUS_NAME,
    _atomic_write,
)
from src.backends.fpga_decode import decode_fpga
from src.ccir_lower_parity import lower_parity_instance_to_ccir
from src.compiler import DEFAULT_XOR_INSTANCE
from src.observable_execution import ObservableExecution
from src.physical_execution_event import PhysicalExecutionEvent
from src.physical_execution_evidence import (
    observable_execution_hash,
    prepared_execution_hash,
)
from src.physical_validation import validate_decoded_result


EXECUTION_REPORT_NAME = "p1-physical-execution-report.json"


def _load_event(path: Path) -> PhysicalExecutionEvent:
    data = json.loads(path.read_text())
    event = PhysicalExecutionEvent(
        backend_id=data["backend"]["id"],
        backend_version=data["backend"]["version"],
        physical_profile_id=data["physical_profile_id"],
        programming_record_hash=data["binding"]["programming_record_hash"],
        prepared_execution_hash=data["binding"]["prepared_execution_hash"],
        observable_execution_hash=data["binding"]["observable_execution_hash"],
        board_id=data["device"]["board_id"],
        device_id=data["device"]["device_id"],
        stimulus_interface=data["execution"]["stimulus_interface"],
        observation_interface=data["execution"]["observation_interface"],
        stimulus_record_sha256=data["execution"]["stimulus_record_sha256"],
        measurement_record_sha256=data["execution"]["measurement_record_sha256"],
        metadata=tuple(sorted(data["metadata"].items())),
    )
    if data["event_hash"] != event.event_hash:
        raise ValueError("physical execution event hash mismatch")
    return event


def validate_p1_physical_execution(
    evidence_directory: Path = EVIDENCE_DIRECTORY,
) -> dict[str, object]:
    """Independently validate the recorded P1 observable against CCIR."""
    evidence_directory = Path(evidence_directory)
    event = _load_event(evidence_directory / EXECUTION_EVENT_NAME)
    observable_data = json.loads(
        (evidence_directory / OBSERVABLE_NAME).read_text()
    )
    measurement = json.loads(
        (evidence_directory / MEASUREMENT_NAME).read_text()
    )
    prepared, _ = build_p1_inputs()
    observable = ObservableExecution(
        backend_id=observable_data["backend"]["id"],
        backend_version=observable_data["backend"]["version"],
        observations=(("result_bit", observable_data["observations"]["result_bit"]),),
        provenance=prepared.provenance,
        metadata=(
            ("execution_engine", "physical-fpga-device"),
            ("execution_engine_version", "lattice-icebreaker-up5k"),
            ("execution_id", "fpga.physical-device.v1"),
        ),
    )
    if prepared_execution_hash(prepared) != event.prepared_execution_hash:
        raise ValueError("prepared execution hash mismatch")
    if observable_execution_hash(observable) != event.observable_execution_hash:
        raise ValueError("observable execution hash mismatch")
    if observable_data["observable_execution_hash"] != event.observable_execution_hash:
        raise ValueError("observable evidence binding mismatch")

    decoded = decode_fpga(observable, prepared.decoder_specification)
    ccir = lower_parity_instance_to_ccir(DEFAULT_XOR_INSTANCE)
    validation = validate_decoded_result(ccir, {0: 0, 3: 1}, decoded)
    if not validation.passed:
        raise ValueError("physical observation failed semantic validation")

    report: dict[str, object] = {
        "schema": "cpc.p1-physical-execution-report.v1",
        "status": "physical-execution-observed-and-validated",
        "artifacts": {
            "execution_event": EXECUTION_EVENT_NAME,
            "measurement_record": MEASUREMENT_NAME,
            "observable_execution": OBSERVABLE_NAME,
            "physical_observation": PHOTO_NAME,
            "programming_record": PROGRAMMING_RECORD_NAME,
            "stimulus_record": STIMULUS_NAME,
        },
        "bindings": {
            "execution_event_hash": event.event_hash,
            "measurement_record_sha256": event.measurement_record_sha256,
            "observable_execution_hash": event.observable_execution_hash,
            "programming_record_hash": event.programming_record_hash,
            "stimulus_record_sha256": event.stimulus_record_sha256,
        },
        "semantic_validation": {
            "boundary_values": {"x0": 0, "x3": 1},
            "decoded": validation.decoded,
            "passed": validation.passed,
            "reference": validation.reference,
        },
        "trust_boundary": measurement["trust_boundary"],
    }
    _atomic_write(
        evidence_directory / EXECUTION_REPORT_NAME,
        (json.dumps(report, indent=2, sort_keys=True) + "\n").encode(),
    )
    return report


def main() -> None:
    report = validate_p1_physical_execution()
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
