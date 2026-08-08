from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cross_backend_cli_passes_default_xor() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "validate_cross_backend.py",
            "benchmarks/default_xor.json",
            "--boundary",
            "0=0",
            "--boundary",
            "3=1",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0

    assert (
        "CPC Cross-Backend Validation"
        in completed.stdout
    )

    assert (
        "RC Reference Backend"
        in completed.stdout
    )

    assert (
        "Digital Backend"
        in completed.stdout
    )

    assert (
        "Independent Reference"
        in completed.stdout
    )

    assert (
        "Backend agreement:    PASS"
        in completed.stdout
    )

    assert (
        "RC semantic match:    PASS"
        in completed.stdout
    )

    assert (
        "Digital semantic:     PASS"
        in completed.stdout
    )

    assert (
        "OVERALL:              PASS"
        in completed.stdout
    )


def test_cross_backend_cli_rejects_invalid_boundary() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "validate_cross_backend.py",
            "benchmarks/default_xor.json",
            "--boundary",
            "0=2",
            "--boundary",
            "3=1",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 2

    assert (
        "boundary value must be 0 or 1"
        in completed.stderr
    )
