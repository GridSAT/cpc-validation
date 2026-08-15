from __future__ import annotations

import json
from pathlib import Path

import pytest

from build_p1_physical_artifacts import write_p1_physical_artifacts
from record_p1_physical_programming import (
    PROGRAMMING_LOG_NAME,
    PROGRAMMING_RECORD_NAME,
    PROGRAMMING_REPORT_NAME,
    record_p1_programming_evidence,
)


def _programming_log(bitstream_sha256: str) -> dict[str, object]:
    return {
        "timestamp": "2026-08-15T15:48:14.780890+00:00",
        "action": "program_cpc_icebreaker_sram",
        "target": "lattice-icebreaker-up5k",
        "profile": "cpc",
        "bitstream": "evidence/p1/physical/p1-icebreaker.bin",
        "bitstream_bytes": 104090,
        "bitstream_sha256": bitstream_sha256.removeprefix("sha256:"),
        "usb_id": "0403:6010",
        "usb_selector": "d:001/008",
        "return_code": 0,
        "passed": True,
        "duration_seconds": 0.41584969696123153,
        "stdout": "",
        "stderr": "init..\ncdone: high\nreset..\ncdone: low\nprogramming..\ncdone: low\nBye.\n",
        "stdout_bytes": 0,
        "stderr_bytes": 68,
        "output_truncated": False,
    }


def test_record_p1_programming_evidence_binds_guarded_result(
    tmp_path: Path,
) -> None:
    build = write_p1_physical_artifacts(tmp_path)
    log = _programming_log(build["digests"]["bitstream"])
    (tmp_path / PROGRAMMING_LOG_NAME).write_text(
        json.dumps(log, indent=2, sort_keys=True) + "\n"
    )

    report = record_p1_programming_evidence(tmp_path)
    record = json.loads((tmp_path / PROGRAMMING_RECORD_NAME).read_text())

    assert report["status"] == "programmed-awaiting-physical-observation"
    assert report["programming_passed"] is True
    assert report["physical_observation_recorded"] is False
    assert report["physical_execution_claimed"] is False
    assert record["binding"]["bitstream_sha256"] == (
        build["digests"]["bitstream"]
    )
    assert record["programming"]["programming_log_sha256"] == (
        report["bindings"]["programming_log_sha256"]
    )
    assert (tmp_path / PROGRAMMING_REPORT_NAME).is_file()


def test_record_p1_programming_evidence_rejects_failed_result(
    tmp_path: Path,
) -> None:
    build = write_p1_physical_artifacts(tmp_path)
    log = _programming_log(build["digests"]["bitstream"])
    log["passed"] = False
    (tmp_path / PROGRAMMING_LOG_NAME).write_text(
        json.dumps(log, indent=2, sort_keys=True) + "\n"
    )

    with pytest.raises(ValueError, match="passed"):
        record_p1_programming_evidence(tmp_path)
