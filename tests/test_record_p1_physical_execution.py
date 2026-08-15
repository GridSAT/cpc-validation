from __future__ import annotations

import json
from pathlib import Path

import pytest

from build_p1_physical_artifacts import write_p1_physical_artifacts
from record_p1_physical_execution import (
    EXECUTION_EVENT_NAME,
    MEASUREMENT_NAME,
    OBSERVABLE_NAME,
    PHOTO_NAME,
    STIMULUS_NAME,
    record_p1_physical_execution,
)
from record_p1_physical_programming import (
    PROGRAMMING_LOG_NAME,
    record_p1_programming_evidence,
)


PHOTO = b"synthetic physical observation"


def _write_prerequisites(path: Path) -> None:
    import hashlib

    build = write_p1_physical_artifacts(path)
    programming = {
        "timestamp": "2026-08-15T15:48:14.780890+00:00",
        "action": "program_cpc_icebreaker_sram",
        "target": "lattice-icebreaker-up5k",
        "profile": "cpc",
        "bitstream": "evidence/p1/physical/p1-icebreaker.bin",
        "bitstream_bytes": 104090,
        "bitstream_sha256": build["digests"]["bitstream"].removeprefix(
            "sha256:"
        ),
        "usb_id": "0403:6010",
        "usb_selector": "d:001/008",
        "return_code": 0,
        "passed": True,
        "duration_seconds": 0.4,
        "stdout": "",
        "stderr": "programming completed\n",
        "stdout_bytes": 0,
        "stderr_bytes": 22,
        "output_truncated": False,
    }
    (path / PROGRAMMING_LOG_NAME).write_text(
        json.dumps(programming, indent=2, sort_keys=True) + "\n"
    )
    record_p1_programming_evidence(path)

    (path / PHOTO_NAME).write_bytes(PHOTO)
    (path / STIMULUS_NAME).write_text(
        json.dumps(
            {
                "schema": "cpc.p1-physical-stimulus.v1",
                "boundary_values": {"x0": 0, "x3": 1},
                "delivery": "constants embedded in the retained PreparedExecution",
                "interface": "synthesis-bound-constants",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    (path / MEASUREMENT_NAME).write_text(
        json.dumps(
            {
                "schema": "cpc.p1-physical-measurement.v1",
                "capture": {
                    "recorded_at_camera_local": "2026-08-15T18:02:38",
                    "sha256": "sha256:" + hashlib.sha256(PHOTO).hexdigest(),
                },
                "observation": {"led_red_illuminated": False},
                "interpretation": {
                    "electrical_polarity": "active-low",
                    "logical_result_bit": 1,
                },
                "trust_boundary": "synthetic test evidence",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def test_record_p1_physical_execution_closes_bound_event(
    tmp_path: Path,
) -> None:
    _write_prerequisites(tmp_path)

    result = record_p1_physical_execution(tmp_path)

    assert result["status"] == "physical-execution-observed"
    assert (tmp_path / EXECUTION_EVENT_NAME).is_file()
    assert (tmp_path / OBSERVABLE_NAME).is_file()


def test_record_p1_physical_execution_rejects_photo_mismatch(
    tmp_path: Path,
) -> None:
    _write_prerequisites(tmp_path)
    (tmp_path / PHOTO_NAME).write_bytes(b"different photograph")

    with pytest.raises(ValueError, match="photograph hash mismatch"):
        record_p1_physical_execution(tmp_path)
