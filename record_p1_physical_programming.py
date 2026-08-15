from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.physical_build_provenance import (
    BuildInputRecord,
    BuildToolIdentity,
    PhysicalBuildManifest,
)
from src.physical_device_programming import programming_record_from_build


EVIDENCE_DIRECTORY = Path("evidence/p1/physical")
MANIFEST_NAME = "p1-physical-build-manifest.json"
PROGRAMMING_LOG_NAME = "p1-programming-log.json"
PROGRAMMING_RECORD_NAME = "p1-device-programming-record.json"
PROGRAMMING_REPORT_NAME = "p1-programming-report.json"

EXPECTED_ACTION = "program_cpc_icebreaker_sram"
EXPECTED_TARGET = "lattice-icebreaker-up5k"
EXPECTED_PROFILE = "cpc"
EXPECTED_BITSTREAM = "evidence/p1/physical/p1-icebreaker.bin"
EXPECTED_USB_ID = "0403:6010"
PROGRAMMER = "/usr/bin/iceprog"
PROGRAMMER_VERSION = "fpga-icestorm 0~20230218gitd20a5e9-1"


def _sha256(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def _atomic_write(path: Path, content: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def _load_build_manifest(path: Path) -> PhysicalBuildManifest:
    data = json.loads(path.read_text())
    manifest = PhysicalBuildManifest(
        backend_id=data["backend"]["id"],
        backend_version=data["backend"]["version"],
        physical_profile_id=data["physical_profile_id"],
        prepared_execution_hash=data["binding"]["prepared_execution_hash"],
        device_family=data["device"]["family"],
        device_part=data["device"]["part"],
        tools=tuple(
            BuildToolIdentity(
                stage=item["stage"],
                tool=item["tool"],
                version=item["version"],
            )
            for item in data["tools"]
        ),
        inputs=tuple(
            BuildInputRecord(
                input_id=item["input_id"],
                media_type=item["media_type"],
                sha256=item["sha256"],
            )
            for item in data["inputs"]
        ),
        bitstream_format=data["bitstream"]["format"],
        bitstream_sha256=data["bitstream"]["sha256"],
        metadata=tuple(sorted(data["metadata"].items())),
    )
    if data["manifest_hash"] != manifest.manifest_hash:
        raise ValueError("build manifest hash mismatch")
    return manifest


def _validate_programming_log(
    data: dict[str, object],
    *,
    expected_bitstream_sha256: str,
) -> None:
    expected = {
        "action": EXPECTED_ACTION,
        "target": EXPECTED_TARGET,
        "profile": EXPECTED_PROFILE,
        "bitstream": EXPECTED_BITSTREAM,
        "bitstream_sha256": expected_bitstream_sha256.removeprefix("sha256:"),
        "usb_id": EXPECTED_USB_ID,
        "return_code": 0,
        "passed": True,
        "output_truncated": False,
    }
    for name, value in expected.items():
        if data.get(name) != value:
            raise ValueError(f"unexpected programming result field: {name}")

    selector = data.get("usb_selector")
    if not isinstance(selector, str) or not selector.startswith("d:"):
        raise ValueError("unexpected programming result field: usb_selector")

    timestamp = data.get("timestamp")
    if not isinstance(timestamp, str) or not timestamp:
        raise ValueError("unexpected programming result field: timestamp")


def record_p1_programming_evidence(
    evidence_directory: Path = EVIDENCE_DIRECTORY,
) -> dict[str, object]:
    """Bind an already captured guarded programming result to the P1 build."""
    evidence_directory = Path(evidence_directory)
    manifest = _load_build_manifest(evidence_directory / MANIFEST_NAME)
    log_path = evidence_directory / PROGRAMMING_LOG_NAME
    log_bytes = log_path.read_bytes()
    log = json.loads(log_bytes)
    _validate_programming_log(
        log,
        expected_bitstream_sha256=manifest.bitstream_sha256,
    )

    record = programming_record_from_build(
        build=manifest,
        board_id=EXPECTED_TARGET,
        device_id=f"usb:{EXPECTED_USB_ID}:{log['usb_selector']}",
        programming_interface="ftdi-mpsse-spi-sram",
        programmer=PROGRAMMER,
        programmer_version=PROGRAMMER_VERSION,
        programming_log_sha256=_sha256(log_bytes),
        metadata=(
            ("mode", "volatile-sram"),
            ("programmed_at", str(log["timestamp"])),
            ("usb_selector", str(log["usb_selector"])),
        ),
    )
    record_bytes = record.to_json().encode("utf-8")
    report: dict[str, object] = {
        "schema": "cpc.p1-programming-report.v1",
        "status": "programmed-awaiting-physical-observation",
        "programming_passed": True,
        "artifacts": {
            "build_manifest": MANIFEST_NAME,
            "programming_log": PROGRAMMING_LOG_NAME,
            "programming_record": PROGRAMMING_RECORD_NAME,
        },
        "bindings": {
            "bitstream_sha256": manifest.bitstream_sha256,
            "build_manifest_hash": manifest.manifest_hash,
            "programming_log_sha256": _sha256(log_bytes),
            "programming_record_hash": record.record_hash,
        },
        "physical_observation_recorded": False,
        "physical_execution_claimed": False,
        "semantic_correctness_claimed": False,
    }
    report_bytes = (
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    _atomic_write(evidence_directory / PROGRAMMING_RECORD_NAME, record_bytes)
    _atomic_write(evidence_directory / PROGRAMMING_REPORT_NAME, report_bytes)
    return report


def main() -> None:
    report = record_p1_programming_evidence()
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
