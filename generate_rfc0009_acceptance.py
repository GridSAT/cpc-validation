from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent

RFC_PATH = ROOT / (
    "docs/design/"
    "RFC-0009-Physical-Execution-Evidence-and-Substrate-Conformance.md"
)

CONFORMANCE_PATH = ROOT / (
    "tests/test_rfc0009_conformance.py"
)

OUTPUT_DIR = ROOT / "evidence/rfc0009"
OUTPUT_PATH = OUTPUT_DIR / "rfc0009-acceptance-summary.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256(
        path.read_bytes()
    ).hexdigest()

    return f"sha256:{digest}"


def run_pytest(
    *paths: str,
) -> dict[str, object]:
    command = [
        "python",
        "-m",
        "pytest",
        "-q",
        *paths,
    ]

    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    output = completed.stdout.strip()

    return {
        "command": " ".join(command),
        "returncode": completed.returncode,
        "output": output,
        "pass": completed.returncode == 0,
    }


def canonical_json(
    value: object,
) -> str:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    )


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    conformance = run_pytest(
        "tests/test_rfc0009_conformance.py",
    )

    implementation_stack = run_pytest(
        "tests/test_physical_execution_evidence.py",
        "tests/test_physical_execution_evidence_real_backends.py",
        "tests/test_physical_execution_conformance.py",
        "tests/test_physical_evidence_verification.py",
        "tests/test_physical_fpga_profile.py",
        "tests/test_physical_build_provenance.py",
        "tests/test_physical_device_programming.py",
        "tests/test_physical_execution_event.py",
        "tests/test_rfc0009_conformance.py",
    )

    rfc0008_regression = run_pytest(
        "tests/test_fpga_ccir.py",
        "tests/test_fpga_prepare.py",
        "tests/test_fpga_execute.py",
        "tests/test_rfc0008_conformance.py",
    )

    complete_regression = run_pytest()

    data: dict[str, object] = {
        "schema": "cpc.rfc0009-acceptance-summary.v1",
        "rfc": {
            "id": "RFC-0009",
            "title": (
                "Physical Execution Evidence and "
                "Substrate Conformance"
            ),
            "status_at_generation": "Draft",
            "document_sha256": sha256_file(
                RFC_PATH
            ),
        },
        "conformance": {
            "normative_requirement_count": 25,
            "pe_requirement_count": 15,
            "pf_requirement_count": 10,
            "test_file_sha256": sha256_file(
                CONFORMANCE_PATH
            ),
            "pytest": conformance,
        },
        "implementation_stack": (
            implementation_stack
        ),
        "rfc0008_regression": (
            rfc0008_regression
        ),
        "complete_regression": (
            complete_regression
        ),
    }

    data["overall_pass"] = all(
        (
            conformance["pass"],
            implementation_stack["pass"],
            rfc0008_regression["pass"],
            complete_regression["pass"],
        )
    )

    canonical = canonical_json(
        data
    )

    data["acceptance_hash"] = (
        "sha256:"
        + hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            data,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        OUTPUT_PATH.relative_to(ROOT)
    )

    print(
        data["acceptance_hash"]
    )

    if not data["overall_pass"]:
        raise SystemExit(
            "RFC-0009 acceptance generation failed"
        )


if __name__ == "__main__":
    main()
