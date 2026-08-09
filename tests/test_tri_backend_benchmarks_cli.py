from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_tri_backend_benchmark_cli_writes_reports(
    tmp_path: Path,
) -> None:
    csv_path = (
        tmp_path
        / "validation.csv"
    )

    json_path = (
        tmp_path
        / "summary.json"
    )

    completed = subprocess.run(
        [
            sys.executable,
            "validate_tri_backend_benchmarks.py",
            "benchmarks/default_xor.json",
            "--csv",
            str(csv_path),
            "--json",
            str(json_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0

    assert (
        "OVERALL:                PASS"
        in completed.stdout
    )

    assert csv_path.exists()
    assert json_path.exists()

    summary = json.loads(
        json_path.read_text(
            encoding="utf-8"
        )
    )

    assert summary["schema"] == (
        "cpc.tri-backend-summary.v1"
    )

    assert summary["benchmark_count"] == 1
    assert summary["boundary_case_count"] == 4
    assert summary["overall_pass"] is True


def test_tri_backend_benchmark_cli_reports_validation_counts(
    tmp_path: Path,
) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "validate_tri_backend_benchmarks.py",
            "benchmarks/default_xor.json",
            "--csv",
            str(
                tmp_path
                / "validation.csv"
            ),
            "--json",
            str(
                tmp_path
                / "summary.json"
            ),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0

    assert "Benchmarks:             1" in completed.stdout
    assert "Boundary cases:         4" in completed.stdout

    assert (
        "Backend agreement:      4/4 PASS"
        in completed.stdout
    )

    assert (
        "RC semantic match:      4/4 PASS"
        in completed.stdout
    )

    assert (
        "Digital semantic match: 4/4 PASS"
        in completed.stdout
    )

    assert (
        "FPGA semantic match:    4/4 PASS"
        in completed.stdout
    )
