from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _write_summary(
    path: Path,
    *,
    schema: str = "cpc.tri-backend-summary.v1",
    boundary_case_count: int = 64,
    fpga_failed: int = 0,
    overall_failed: int = 0,
    overall_pass: bool = True,
) -> None:
    fpga_passed = (
        boundary_case_count
        - fpga_failed
    )

    overall_passed = (
        boundary_case_count
        - overall_failed
    )

    path.write_text(
        json.dumps(
            {
                "schema": schema,
                "benchmark_count": 16,
                "boundary_case_count": (
                    boundary_case_count
                ),
                "backend_agreement_passed": (
                    overall_passed
                ),
                "backend_agreement_failed": (
                    overall_failed
                ),
                "rc_semantic_passed": (
                    overall_passed
                ),
                "rc_semantic_failed": (
                    overall_failed
                ),
                "digital_semantic_passed": (
                    overall_passed
                ),
                "digital_semantic_failed": (
                    overall_failed
                ),
                "fpga_semantic_passed": (
                    fpga_passed
                ),
                "fpga_semantic_failed": (
                    fpga_failed
                ),
                "overall_passed": (
                    overall_passed
                ),
                "overall_failed": (
                    overall_failed
                ),
                "overall_pass": overall_pass,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def test_fpga_qualification_cli_writes_manifest(
    tmp_path: Path,
) -> None:
    summary = (
        tmp_path
        / "summary.json"
    )

    output = (
        tmp_path
        / "qualification"
    )

    _write_summary(
        summary
    )

    completed = subprocess.run(
        [
            sys.executable,
            "qualify_fpga_backend.py",
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

    path = (
        output
        / "fpga.backend-qualification.json"
    )

    assert path.exists()

    manifest = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert manifest["schema"] == (
        "cpc.backend-qualification.v1"
    )

    assert manifest["backend"] == {
        "id": "fpga",
        "version": "1",
    }

    assert manifest["execution"]["execution_engine"] == (
        "iverilog/vvp"
    )

    assert (
        manifest["execution"]["execution_engine_version"]
    )

    assert manifest["corpus"] == {
        "benchmark_count": 16,
        "boundary_case_count": 64,
        "overall_pass": True,
        "report_schema": (
            "cpc.tri-backend-summary.v1"
        ),
    }

    assert manifest["manifest_hash"].startswith(
        "sha256:"
    )

    assert (
        "qualification: PASS"
        in completed.stdout
    )


def test_fpga_qualification_cli_rejects_wrong_schema(
    tmp_path: Path,
) -> None:
    summary = (
        tmp_path
        / "summary.json"
    )

    _write_summary(
        summary,
        schema="wrong.schema",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "qualify_fpga_backend.py",
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
        "unsupported RFC-0008 tri-backend summary schema"
        in completed.stderr
    )


def test_fpga_qualification_cli_rejects_fpga_semantic_failure(
    tmp_path: Path,
) -> None:
    summary = (
        tmp_path
        / "summary.json"
    )

    _write_summary(
        summary,
        fpga_failed=1,
        overall_failed=1,
        overall_pass=False,
    )

    completed = subprocess.run(
        [
            sys.executable,
            "qualify_fpga_backend.py",
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
        "every FPGA semantic case to pass"
        in completed.stderr
    )


def test_fpga_qualification_cli_rejects_aggregate_failure(
    tmp_path: Path,
) -> None:
    summary = (
        tmp_path
        / "summary.json"
    )

    _write_summary(
        summary,
        fpga_failed=0,
        overall_failed=1,
        overall_pass=False,
    )

    completed = subprocess.run(
        [
            sys.executable,
            "qualify_fpga_backend.py",
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
        "fully passing tri-backend corpus"
        in completed.stderr
    )


def test_fpga_qualification_cli_is_deterministic(
    tmp_path: Path,
) -> None:
    summary = (
        tmp_path
        / "summary.json"
    )

    _write_summary(
        summary
    )

    first = tmp_path / "first"
    second = tmp_path / "second"

    for output in (
        first,
        second,
    ):
        completed = subprocess.run(
            [
                sys.executable,
                "qualify_fpga_backend.py",
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
        / "fpga.backend-qualification.json"
    ).read_text(
        encoding="utf-8"
    )

    second_manifest = (
        second
        / "fpga.backend-qualification.json"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        first_manifest
        ==
        second_manifest
    )
