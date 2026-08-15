from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from validate_p1_physical_execution import (
    EXECUTION_REPORT_NAME,
    validate_p1_physical_execution,
)


SOURCE_EVIDENCE = Path("evidence/p1/physical")


def _copy_evidence(path: Path) -> None:
    for source in SOURCE_EVIDENCE.iterdir():
        if source.is_file():
            shutil.copy2(source, path / source.name)


def test_validate_p1_physical_execution_matches_independent_ccir(
    tmp_path: Path,
) -> None:
    _copy_evidence(tmp_path)

    report = validate_p1_physical_execution(tmp_path)

    assert report["status"] == "physical-execution-observed-and-validated"
    assert report["semantic_validation"] == {
        "boundary_values": {"x0": 0, "x3": 1},
        "decoded": 1,
        "passed": True,
        "reference": 1,
    }
    assert (tmp_path / EXECUTION_REPORT_NAME).is_file()


def test_validate_p1_physical_execution_rejects_observable_substitution(
    tmp_path: Path,
) -> None:
    _copy_evidence(tmp_path)
    observable_path = tmp_path / "p1-observable-execution.json"
    observable = json.loads(observable_path.read_text())
    observable["observations"]["result_bit"] = 0
    observable_path.write_text(
        json.dumps(observable, indent=2, sort_keys=True) + "\n"
    )

    with pytest.raises(ValueError, match="observable execution hash mismatch"):
        validate_p1_physical_execution(tmp_path)
