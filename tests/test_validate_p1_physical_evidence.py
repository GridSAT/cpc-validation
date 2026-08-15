from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from validate_p1_physical_evidence import (
    CONFORMANCE_REPORT_NAME,
    EVIDENCE_ENVELOPE_NAME,
    validate_p1_physical_evidence,
)


SOURCE_EVIDENCE = Path("evidence/p1/physical")


def _copy_evidence(path: Path) -> None:
    for source in SOURCE_EVIDENCE.iterdir():
        if source.is_file():
            shutil.copy2(source, path / source.name)


def test_validate_p1_physical_evidence_satisfies_rfc0009_profile(
    tmp_path: Path,
) -> None:
    _copy_evidence(tmp_path)

    report = validate_p1_physical_evidence(tmp_path)

    assert report["status"] == "rfc0009-physical-evidence-conformant"
    assert report["overall_pass"] is True
    assert all(report["checks"].values())
    assert report["semantic_correctness_claimed"] is False
    assert (tmp_path / EVIDENCE_ENVELOPE_NAME).is_file()
    assert (tmp_path / CONFORMANCE_REPORT_NAME).is_file()


def test_validate_p1_physical_evidence_rejects_timing_substitution(
    tmp_path: Path,
) -> None:
    _copy_evidence(tmp_path)
    timing_path = tmp_path / "p1-timing-report.json"
    timing = json.loads(timing_path.read_text())
    timing["status"] = "not-validated"
    timing_path.write_text(
        json.dumps(timing, indent=2, sort_keys=True) + "\n"
    )

    with pytest.raises(
        ValueError,
        match=(
            "physical evidence binding mismatch: build report to timing report"
        ),
    ):
        validate_p1_physical_evidence(tmp_path)


def test_validate_p1_physical_evidence_rejects_photo_substitution(
    tmp_path: Path,
) -> None:
    _copy_evidence(tmp_path)
    photo_path = tmp_path / "p1-physical-observation.heic"
    photo_path.write_bytes(photo_path.read_bytes() + b"substitution")

    with pytest.raises(
        ValueError,
        match=(
            "physical evidence binding mismatch: measurement record to "
            "physical observation"
        ),
    ):
        validate_p1_physical_evidence(tmp_path)
