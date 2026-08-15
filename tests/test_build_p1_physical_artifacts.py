from __future__ import annotations

import hashlib
import json
from pathlib import Path

from build_p1_physical_artifacts import (
    BITSTREAM_NAME,
    MANIFEST_NAME,
    REPORT_NAME,
    TIMING_REPORT_NAME,
    VERILOG_NAME,
    write_p1_physical_artifacts,
)


def test_write_p1_physical_artifacts_retains_bound_build(tmp_path: Path) -> None:
    report = write_p1_physical_artifacts(tmp_path)

    bitstream = (tmp_path / BITSTREAM_NAME).read_bytes()
    manifest_bytes = (tmp_path / MANIFEST_NAME).read_bytes()
    manifest = json.loads(manifest_bytes)
    saved_report = json.loads((tmp_path / REPORT_NAME).read_text())
    timing_report_bytes = (tmp_path / TIMING_REPORT_NAME).read_bytes()
    timing_report = json.loads(timing_report_bytes)

    assert bitstream
    assert (tmp_path / VERILOG_NAME).is_file()
    assert report == saved_report
    assert report["status"] == "built-not-programmed"
    assert report["digests"]["bitstream"] == (
        "sha256:" + hashlib.sha256(bitstream).hexdigest()
    )
    assert report["digests"]["build_manifest"] == (
        "sha256:" + hashlib.sha256(manifest_bytes).hexdigest()
    )
    assert manifest["manifest_hash"] == report["build_manifest_hash"]
    assert manifest["bitstream"]["sha256"] == report["digests"]["bitstream"]
    assert report["digests"]["timing_report"] == (
        "sha256:" + hashlib.sha256(timing_report_bytes).hexdigest()
    )
    assert timing_report["status"] == (
        "pass-static-combinational-no-interior-paths"
    )
    assert timing_report["analysis"] == {
        "clock_domains": 0,
        "fmax_available": False,
        "interior_timing_paths_found": False,
        "route_completed": True,
        "tool_completed_normally": True,
    }


def test_write_p1_physical_artifacts_is_deterministic(tmp_path: Path) -> None:
    first = write_p1_physical_artifacts(tmp_path)
    first_bytes = {
        name: (tmp_path / name).read_bytes()
        for name in (
            BITSTREAM_NAME,
            MANIFEST_NAME,
            REPORT_NAME,
            TIMING_REPORT_NAME,
            VERILOG_NAME,
        )
    }

    second = write_p1_physical_artifacts(tmp_path)
    second_bytes = {
        name: (tmp_path / name).read_bytes()
        for name in (
            BITSTREAM_NAME,
            MANIFEST_NAME,
            REPORT_NAME,
            TIMING_REPORT_NAME,
            VERILOG_NAME,
        )
    }

    assert first == second
    assert first_bytes == second_bytes
