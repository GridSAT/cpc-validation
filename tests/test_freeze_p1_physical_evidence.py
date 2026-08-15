from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from freeze_p1_physical_evidence import (
    ARTIFACTS,
    INDEX_NAME,
    freeze_p1_physical_evidence,
)


SOURCE_EVIDENCE = Path("evidence/p1/physical")


def _copy_evidence(path: Path) -> None:
    for source in SOURCE_EVIDENCE.iterdir():
        if source.is_file():
            shutil.copy2(source, path / source.name)


def test_freeze_p1_physical_evidence_indexes_every_digest(
    tmp_path: Path,
) -> None:
    _copy_evidence(tmp_path)

    content = freeze_p1_physical_evidence(tmp_path)

    assert content == (tmp_path / INDEX_NAME).read_text()
    for filename, _, _ in ARTIFACTS:
        digest = "sha256:" + hashlib.sha256(
            (tmp_path / filename).read_bytes()
        ).hexdigest()
        assert f"`{filename}`" in content
        assert f"`{digest}`" in content


def test_freeze_p1_physical_evidence_is_deterministic(
    tmp_path: Path,
) -> None:
    _copy_evidence(tmp_path)

    first = freeze_p1_physical_evidence(tmp_path)
    second = freeze_p1_physical_evidence(tmp_path)

    assert first == second
