from __future__ import annotations

import hashlib
import json
from pathlib import Path

from record_p1_physical_execution import _atomic_write
from record_p1_physical_programming import EVIDENCE_DIRECTORY
from validate_p1_physical_evidence import CONFORMANCE_REPORT_NAME
from validate_p1_physical_execution import EXECUTION_REPORT_NAME


INDEX_NAME = "README.md"

ARTIFACTS: tuple[tuple[str, str, str], ...] = (
    (
        "p1-device-programming-record.json",
        "programming binding",
        "provenance",
    ),
    ("p1-icebreaker.bin", "programmed bitstream", "identity"),
    ("p1-measurement-record.json", "LED measurement", "observation"),
    ("p1-observable-execution.json", "admitted observable", "observation"),
    ("p1-physical-build-manifest.json", "build manifest", "provenance"),
    ("p1-physical-build-report.json", "build report", "provenance"),
    (
        "p1-physical-evidence-conformance-report.json",
        "RFC-0009 profile result",
        "conformance",
    ),
    (
        "p1-physical-execution-evidence.json",
        "RFC-0009 evidence envelope",
        "conformance",
    ),
    ("p1-physical-execution-event.json", "execution event", "provenance"),
    (
        "p1-physical-execution-report.json",
        "independent CCIR result",
        "semantic validation",
    ),
    ("p1-physical-observation.heic", "original photograph", "observation"),
    ("p1-physical-top.v", "physical Verilog", "build input"),
    ("p1-programming-log.json", "guarded action log", "programming"),
    ("p1-programming-report.json", "programming status", "programming"),
    ("p1-stimulus-record.json", "fixed boundary stimulus", "stimulus"),
    ("p1-timing-report.json", "static timing report", "timing"),
)


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def freeze_p1_physical_evidence(
    evidence_directory: Path = EVIDENCE_DIRECTORY,
) -> str:
    """Write the deterministic human-readable index for frozen P1 evidence."""

    directory = Path(evidence_directory)
    conformance = json.loads((directory / CONFORMANCE_REPORT_NAME).read_text())
    execution = json.loads((directory / EXECUTION_REPORT_NAME).read_text())
    if conformance.get("overall_pass") is not True:
        raise ValueError("physical evidence conformance must pass before freeze")
    if execution.get("semantic_validation", {}).get("passed") is not True:
        raise ValueError("semantic validation must pass before freeze")

    rows = []
    for filename, role, claim in ARTIFACTS:
        path = directory / filename
        if not path.is_file():
            raise ValueError(f"missing P1 evidence artifact: {filename}")
        rows.append(
            f"| `{filename}` | `{_sha256(path)}` | {role} | {claim} |"
        )

    content = "\n".join(
        (
            "# P1 physical FPGA evidence",
            "",
            (
                "This directory freezes the evidence for the 2026-08-15 CPC "
                "P1 execution on the Lattice iCE40 UltraPlus Breakout Board. "
                "The RFC-0009 `fpga.physical-device.v1` evidence-profile "
                "evaluation passes, and the separately decoded result `1` "
                "matches the CCIR reference result `1` for `x0=0, x3=1`."
            ),
            "",
            (
                "These remain distinct claims: digests establish byte "
                "identity; the evidence envelope establishes declared "
                "lifecycle conformance; the photograph supports physical "
                "observation within its stated trust boundary; and the "
                "execution report establishes semantic agreement."
            ),
            "",
            "## Artifact index",
            "",
            "| Artifact | SHA-256 | Role | Claim dimension |",
            "|---|---|---|---|",
            *rows,
            "",
            "## Timing scope",
            "",
            (
                "P1 is a static combinational output with synthesis-bound "
                "constants, no clock domain, and no interior timing path. The "
                "retained nextpnr report records successful routing under the "
                "admitted single-shot static observation conditions. It makes "
                "no Fmax, latency, scaling, or computational-complexity claim."
            ),
            "",
            "## Reproduction order",
            "",
            "The derived records are reproduced without reprogramming the board:",
            "",
            "```text",
            "python3 build_p1_physical_artifacts.py",
            "python3 record_p1_physical_programming.py",
            "python3 record_p1_physical_execution.py",
            "python3 validate_p1_physical_evidence.py",
            "python3 validate_p1_physical_execution.py",
            "python3 freeze_p1_physical_evidence.py",
            "```",
            "",
            (
                "The guarded programming action is intentionally absent from "
                "this sequence. Reprogramming is a separate consequential "
                "operation that requires explicit approval."
            ),
            "",
            "## Trust boundary",
            "",
            str(conformance["trust_boundary"]),
            "",
        )
    )
    _atomic_write(directory / INDEX_NAME, content.encode("utf-8"))
    return content


def main() -> None:
    freeze_p1_physical_evidence()
    print(f"wrote {EVIDENCE_DIRECTORY / INDEX_NAME}")


if __name__ == "__main__":
    main()
