from __future__ import annotations

import hashlib
import json
from pathlib import Path

from build_p1_physical_artifacts import build_p1_inputs
from record_p1_physical_programming import (
    EVIDENCE_DIRECTORY,
    PROGRAMMING_RECORD_NAME,
)
from src.backends.fpga_decode import decode_fpga
from src.observable_execution import ObservableExecution
from src.physical_device_programming import DeviceProgrammingRecord
from src.physical_execution_event import execution_event_from_records
from src.physical_execution_evidence import prepared_execution_hash


BUILD_MANIFEST_NAME = "p1-physical-build-manifest.json"
PHOTO_NAME = "p1-physical-observation.heic"
STIMULUS_NAME = "p1-stimulus-record.json"
MEASUREMENT_NAME = "p1-measurement-record.json"
OBSERVABLE_NAME = "p1-observable-execution.json"
EXECUTION_EVENT_NAME = "p1-physical-execution-event.json"


def _sha256(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def _atomic_write(path: Path, content: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def _load_programming_record(path: Path) -> DeviceProgrammingRecord:
    data = json.loads(path.read_text())
    record = DeviceProgrammingRecord(
        backend_id=data["backend"]["id"],
        backend_version=data["backend"]["version"],
        physical_profile_id=data["physical_profile_id"],
        build_manifest_hash=data["binding"]["build_manifest_hash"],
        bitstream_sha256=data["binding"]["bitstream_sha256"],
        board_id=data["device"]["board_id"],
        device_family=data["device"]["device_family"],
        device_part=data["device"]["device_part"],
        device_id=data["device"]["device_id"],
        programming_interface=data["programming"]["interface"],
        programmer=data["programming"]["programmer"],
        programmer_version=data["programming"]["programmer_version"],
        programming_log_sha256=data["programming"]["programming_log_sha256"],
        metadata=tuple(sorted(data["metadata"].items())),
    )
    if data["record_hash"] != record.record_hash:
        raise ValueError("programming record hash mismatch")
    return record


def record_p1_physical_execution(
    evidence_directory: Path = EVIDENCE_DIRECTORY,
) -> dict[str, object]:
    """Bind the admitted P1 photograph to one physical execution event."""
    evidence_directory = Path(evidence_directory)
    programming = _load_programming_record(
        evidence_directory / PROGRAMMING_RECORD_NAME
    )
    build_manifest = json.loads(
        (evidence_directory / BUILD_MANIFEST_NAME).read_text()
    )
    stimulus_path = evidence_directory / STIMULUS_NAME
    measurement_path = evidence_directory / MEASUREMENT_NAME
    photo_path = evidence_directory / PHOTO_NAME
    stimulus_bytes = stimulus_path.read_bytes()
    measurement_bytes = measurement_path.read_bytes()
    measurement = json.loads(measurement_bytes)

    if measurement["capture"]["sha256"] != _sha256(photo_path.read_bytes()):
        raise ValueError("physical observation photograph hash mismatch")
    if measurement["observation"]["led_red_illuminated"] is not False:
        raise ValueError("P1 measurement must record LED_RED not illuminated")
    if measurement["interpretation"]["electrical_polarity"] != "active-low":
        raise ValueError("P1 measurement requires the admitted active-low mapping")
    if measurement["interpretation"]["logical_result_bit"] != 1:
        raise ValueError("P1 measurement does not decode to result_bit 1")

    prepared, _ = build_p1_inputs()
    if prepared_execution_hash(prepared) != (
        build_manifest["binding"]["prepared_execution_hash"]
    ):
        raise ValueError("prepared execution does not match physical build")

    observable = ObservableExecution(
        backend_id="fpga",
        backend_version="1",
        observations=(("result_bit", 1),),
        provenance=prepared.provenance,
        metadata=(
            ("execution_engine", "physical-fpga-device"),
            ("execution_engine_version", "lattice-icebreaker-up5k"),
            ("execution_id", "fpga.physical-device.v1"),
        ),
    )
    decoded = decode_fpga(observable, prepared.decoder_specification)

    event = execution_event_from_records(
        programming=programming,
        prepared=prepared,
        observable=observable,
        stimulus_interface="synthesis-bound-constants",
        observation_interface="LED_RED visual photograph",
        stimulus_record_sha256=_sha256(stimulus_bytes),
        measurement_record_sha256=_sha256(measurement_bytes),
        metadata=(
            ("capture_time", measurement["capture"]["recorded_at_camera_local"]),
            ("mode", "single-shot-static-output"),
        ),
    )

    observable_data = {
        "schema": "cpc.p1-observable-execution.v1",
        "backend": {"id": "fpga", "version": "1"},
        "observations": {"result_bit": decoded},
        "observable_execution_hash": event.observable_execution_hash,
        "measurement_record_sha256": event.measurement_record_sha256,
    }
    result: dict[str, object] = {
        "schema": "cpc.p1-physical-execution-recording.v1",
        "status": "physical-execution-observed",
        "artifacts": {
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
        "trust_boundary": measurement["trust_boundary"],
    }
    _atomic_write(
        evidence_directory / OBSERVABLE_NAME,
        (json.dumps(observable_data, indent=2, sort_keys=True) + "\n").encode(),
    )
    _atomic_write(
        evidence_directory / EXECUTION_EVENT_NAME,
        event.to_json().encode(),
    )
    return result


def main() -> None:
    result = record_p1_physical_execution()
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
