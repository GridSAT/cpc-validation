from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _write_summary(
    path: Path,
    *,
    schema: str = "cpc.cross-backend-summary.v1",
    overall_pass: bool = True,
) -> None:
    path.write_text(
        json.dumps(
            {
                "schema": schema,
                "benchmark_count": 16,
                "boundary_case_count": 64,
                "backend_agreement_passed": (
                    64 if overall_pass else 63
                ),
                "backend_agreement_failed": (
                    0 if overall_pass else 1
                ),
                "rc_semantic_passed": (
                    64 if overall_pass else 63
                ),
                "rc_semantic_failed": (
                    0 if overall_pass else 1
                ),
                "digital_semantic_passed": (
                    64 if overall_pass else 63
                ),
                "digital_semantic_failed": (
                    0 if overall_pass else 1
                ),
                "overall_passed": (
                    64 if overall_pass else 63
                ),
                "overall_failed": (
                    0 if overall_pass else 1
                ),
                "overall_pass": overall_pass,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def test_qualification_cli_writes_backend_manifests(
    tmp_path: Path,
) -> None:
    summary = tmp_path / "summary.json"
    output = tmp_path / "qualification"

    _write_summary(summary)

    completed = subprocess.run(
        [
            sys.executable,
            "qualify_backends.py",
            "--summary",
            str(summary),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0

    rc_path = (
        output
        / "rc.backend-qualification.json"
    )

    digital_path = (
        output
        / "digital.backend-qualification.json"
    )

    assert rc_path.exists()
    assert digital_path.exists()

    rc = json.loads(
        rc_path.read_text(
            encoding="utf-8"
        )
    )

    digital = json.loads(
        digital_path.read_text(
            encoding="utf-8"
        )
    )

    assert rc["schema"] == (
        "cpc.backend-qualification.v1"
    )

    assert digital["schema"] == (
        "cpc.backend-qualification.v1"
    )

    assert rc["backend"] == {
        "id": "rc",
        "version": "1",
    }

    assert digital["backend"] == {
        "id": "digital",
        "version": "1",
    }

    assert rc["corpus"]["benchmark_count"] == 16
    assert rc["corpus"]["boundary_case_count"] == 64
    assert rc["corpus"]["overall_pass"] is True

    assert (
        digital["corpus"]
        ==
        rc["corpus"]
    )

    assert rc["manifest_hash"].startswith(
        "sha256:"
    )

    assert digital["manifest_hash"].startswith(
        "sha256:"
    )

    assert (
        rc["manifest_hash"]
        != digital["manifest_hash"]
    )

    assert "qualification: PASS" in completed.stdout


def test_qualification_cli_rejects_failed_corpus(
    tmp_path: Path,
) -> None:
    summary = tmp_path / "summary.json"

    _write_summary(
        summary,
        overall_pass=False,
    )

    completed = subprocess.run(
        [
            sys.executable,
            "qualify_backends.py",
            "--summary",
            str(summary),
            "--output",
            str(
                tmp_path
                / "qualification"
            ),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0

    assert (
        "backend qualification requires a passing "
        "RFC-0006 corpus summary"
        in completed.stderr
    )


def test_qualification_cli_rejects_wrong_summary_schema(
    tmp_path: Path,
) -> None:
    summary = tmp_path / "summary.json"

    _write_summary(
        summary,
        schema="wrong.schema",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "qualify_backends.py",
            "--summary",
            str(summary),
            "--output",
            str(
                tmp_path
                / "qualification"
            ),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0

    assert (
        "unsupported RFC-0006 summary schema"
        in completed.stderr
    )


def test_qualification_cli_is_deterministic_for_digital_manifest(
    tmp_path: Path,
) -> None:
    summary = tmp_path / "summary.json"

    _write_summary(summary)

    first = tmp_path / "first"
    second = tmp_path / "second"

    for output in (
        first,
        second,
    ):
        completed = subprocess.run(
            [
                sys.executable,
                "qualify_backends.py",
                "--summary",
                str(summary),
                "--output",
                str(output),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        assert completed.returncode == 0

    first_manifest = (
        first
        / "digital.backend-qualification.json"
    ).read_text(
        encoding="utf-8"
    )

    second_manifest = (
        second
        / "digital.backend-qualification.json"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        first_manifest
        ==
        second_manifest
    )
