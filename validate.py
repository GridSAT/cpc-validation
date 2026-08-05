from __future__ import annotations

import argparse
import csv
import platform
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPORT_DIRECTORY = Path("reports")
RESULT_DIRECTORY = Path("results")

REPORT_PATH = REPORT_DIRECTORY / "validation_report.md"
SUMMARY_PATH = REPORT_DIRECTORY / "validation_summary.csv"


@dataclass(frozen=True)
class ValidationStep:
    name: str
    command: tuple[str, ...]
    description: str


@dataclass(frozen=True)
class StepResult:
    name: str
    command: tuple[str, ...]
    description: str
    passed: bool
    return_code: int
    duration_seconds: float
    standard_output: str
    standard_error: str


def run_command(
    step: ValidationStep,
) -> StepResult:
    print(f"[RUN ] {step.name}")
    print(f"      {' '.join(step.command)}")

    started = time.perf_counter()

    completed = subprocess.run(
        step.command,
        capture_output=True,
        text=True,
        check=False,
    )

    duration = time.perf_counter() - started
    passed = completed.returncode == 0

    print(
        f"[{'PASS' if passed else 'FAIL'}] "
        f"{step.name} "
        f"({duration:.3f} s)"
    )
    print()

    return StepResult(
        name=step.name,
        command=step.command,
        description=step.description,
        passed=passed,
        return_code=completed.returncode,
        duration_seconds=duration,
        standard_output=completed.stdout,
        standard_error=completed.stderr,
    )


def build_steps(
    *,
    profile: str,
    monte_carlo_seed: int,
) -> list[ValidationStep]:
    if profile == "quick":
        monte_carlo_samples = 25
        threshold_step = "0.5"
        supply_step = "0.5"
        resistance_step = "5.0"
        capacitance_step = "0.25"
        temperature_step = "25.0"
    elif profile == "full":
        monte_carlo_samples = 1000
        threshold_step = "0.1"
        supply_step = "0.1"
        resistance_step = "1.0"
        capacitance_step = "0.125"
        temperature_step = "5.0"
    else:
        raise ValueError(f"Unknown validation profile: {profile}")

    return [
        ValidationStep(
            name="Automated test suite",
            command=(
                sys.executable,
                "-m",
                "pytest",
                "-q",
            ),
            description=(
                "Run the complete Python and ngspice regression-test suite."
            ),
        ),
        ValidationStep(
            name="Reference continuation table",
            command=(
                sys.executable,
                "-m",
                "src.reference",
            ),
            description=(
                "Generate the independent logical continuation table."
            ),
        ),
        ValidationStep(
            name="Nominal SPICE validation",
            command=(
                sys.executable,
                "run_spice.py",
            ),
            description=(
                "Validate all four boundary conditions under nominal "
                "SPICE parameters."
            ),
        ),
        ValidationStep(
            name="Transient-analysis smoke test",
            command=(
                sys.executable,
                "run_transient_smoke.py",
            ),
            description=(
                "Verify waveform extraction, rise time, and settling time."
            ),
        ),
        ValidationStep(
            name="Monte Carlo validation",
            command=(
                sys.executable,
                "run_monte_carlo.py",
                "--samples",
                str(monte_carlo_samples),
                "--seed",
                str(monte_carlo_seed),
                "--output",
                str(
                    RESULT_DIRECTORY
                    / f"validation_monte_carlo_{profile}.csv"
                ),
            ),
            description=(
                f"Run the reproducible {monte_carlo_samples}-sample "
                "Monte Carlo parameter study."
            ),
        ),
        ValidationStep(
            name="Decoder-threshold sweep",
            command=(
                sys.executable,
                "run_threshold_sweep.py",
                "--step",
                threshold_step,
                "--detail-output",
                str(
                    RESULT_DIRECTORY
                    / f"validation_threshold_{profile}.csv"
                ),
                "--summary-output",
                str(
                    RESULT_DIRECTORY
                    / f"validation_threshold_summary_{profile}.csv"
                ),
                "--success-figure",
                str(
                    RESULT_DIRECTORY
                    / f"validation_threshold_success_{profile}.png"
                ),
                "--margin-figure",
                str(
                    RESULT_DIRECTORY
                    / f"validation_threshold_margin_{profile}.png"
                ),
            ),
            description=(
                "Characterize decoder correctness and signed margin "
                "over the tested threshold interval."
            ),
        ),
        ValidationStep(
            name="Supply-voltage sweep",
            command=(
                sys.executable,
                "run_supply_sweep.py",
                "--step",
                supply_step,
                "--detail-output",
                str(
                    RESULT_DIRECTORY
                    / f"validation_supply_{profile}.csv"
                ),
                "--summary-output",
                str(
                    RESULT_DIRECTORY
                    / f"validation_supply_summary_{profile}.csv"
                ),
                "--success-figure",
                str(
                    RESULT_DIRECTORY
                    / f"validation_supply_success_{profile}.png"
                ),
                "--response-figure",
                str(
                    RESULT_DIRECTORY
                    / f"validation_supply_response_{profile}.png"
                ),
                "--margin-figure",
                str(
                    RESULT_DIRECTORY
                    / f"validation_supply_margin_{profile}.png"
                ),
            ),
            description=(
                "Characterize decoder correctness and output response "
                "over the tested supply-voltage interval."
            ),
        ),
        ValidationStep(
            name="Resistance and RC-timing sweep",
            command=(
                sys.executable,
                "run_resistance_sweep.py",
                "--step",
                resistance_step,
                "--detail-output",
                str(
                    RESULT_DIRECTORY
                    / f"validation_resistance_{profile}.csv"
                ),
                "--summary-output",
                str(
                    RESULT_DIRECTORY
                    / f"validation_resistance_summary_{profile}.csv"
                ),
                "--timing-figure",
                str(
                    RESULT_DIRECTORY
                    / f"validation_resistance_timing_{profile}.png"
                ),
                "--error-figure",
                str(
                    RESULT_DIRECTORY
                    / f"validation_resistance_error_{profile}.png"
                ),
                "--success-figure",
                str(
                    RESULT_DIRECTORY
                    / f"validation_resistance_success_{profile}.png"
                ),
            ),
            description=(
                "Verify resistance-dependent rise and settling times "
                "against first-order RC theory."
            ),
        ),
        ValidationStep(
            name="Capacitance and RC-timing sweep",
            command=(
                sys.executable,
                "run_capacitance_sweep.py",
                "--step",
                capacitance_step,
                "--detail-output",
                str(
                    RESULT_DIRECTORY
                    / f"validation_capacitance_{profile}.csv"
                ),
                "--summary-output",
                str(
                    RESULT_DIRECTORY
                    / f"validation_capacitance_summary_{profile}.csv"
                ),
                "--timing-figure",
                str(
                    RESULT_DIRECTORY
                    / f"validation_capacitance_timing_{profile}.png"
                ),
                "--error-figure",
                str(
                    RESULT_DIRECTORY
                    / f"validation_capacitance_error_{profile}.png"
                ),
                "--success-figure",
                str(
                    RESULT_DIRECTORY
                    / f"validation_capacitance_success_{profile}.png"
                ),
            ),
            description=(
                "Verify capacitance-dependent rise and settling times "
                "against first-order RC theory."
            ),
        ),
        ValidationStep(
            name="Imposed temperature-drift sweep",
            command=(
                sys.executable,
                "run_temperature_sweep.py",
                "--step",
                temperature_step,
                "--detail-output",
                str(
                    RESULT_DIRECTORY
                    / f"validation_temperature_{profile}.csv"
                ),
                "--summary-output",
                str(
                    RESULT_DIRECTORY
                    / f"validation_temperature_summary_{profile}.csv"
                ),
                "--component-figure",
                str(
                    RESULT_DIRECTORY
                    / f"validation_temperature_components_{profile}.png"
                ),
                "--timing-figure",
                str(
                    RESULT_DIRECTORY
                    / f"validation_temperature_timing_{profile}.png"
                ),
                "--margin-figure",
                str(
                    RESULT_DIRECTORY
                    / f"validation_temperature_margin_{profile}.png"
                ),
                "--success-figure",
                str(
                    RESULT_DIRECTORY
                    / f"validation_temperature_success_{profile}.png"
                ),
            ),
            description=(
                "Verify decoding and RC timing under an explicitly imposed "
                "linear resistor and capacitor temperature-drift model."
            ),
        ),

    ]


def command_version(
    command: tuple[str, ...],
    *,
    preferred_pattern: str | None = None,
) -> str:
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as error:
        return f"unavailable: {error}"

    output = "\n".join(
        part
        for part in (
            completed.stdout.strip(),
            completed.stderr.strip(),
        )
        if part
    )

    if not output:
        return f"return code {completed.returncode}"

    lines = [
        line.strip()
        for line in output.splitlines()
        if line.strip()
    ]

    if preferred_pattern is not None:
        pattern = preferred_pattern.lower()

        for line in lines:
            if pattern in line.lower():
                return line

    return lines[0]


def git_metadata() -> tuple[str, str]:
    commit = command_version(
        (
            "git",
            "rev-parse",
            "HEAD",
        )
    )

    completed = subprocess.run(
        (
            "git",
            "status",
            "--short",
            "--",
            ".",
            ":(exclude)reports/**",
        ),
        capture_output=True,
        text=True,
        check=False,
    )

    if completed.returncode != 0:
        status = f"unavailable: return code {completed.returncode}"
    else:
        status = completed.stdout.strip() or "clean"

    return commit, status


def write_summary_csv(
    path: Path,
    results: list[StepResult],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.writer(handle)

        writer.writerow(
            (
                "step",
                "passed",
                "return_code",
                "duration_seconds",
                "command",
            )
        )

        for result in results:
            writer.writerow(
                (
                    result.name,
                    int(result.passed),
                    result.return_code,
                    f"{result.duration_seconds:.6f}",
                    " ".join(result.command),
                )
            )


def fenced_block(
    text: str,
) -> str:
    cleaned = text.rstrip()

    if not cleaned:
        cleaned = "(no output)"

    return f"```text\n{cleaned}\n```"


def write_markdown_report(
    *,
    path: Path,
    profile: str,
    seed: int,
    results: list[StepResult],
    started_at: datetime,
    finished_at: datetime,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    passed_count = sum(result.passed for result in results)
    failed_count = len(results) - passed_count
    total_duration = sum(
        result.duration_seconds
        for result in results
    )

    overall_status = "PASS" if failed_count == 0 else "FAIL"

    git_commit, git_status = git_metadata()

    python_version = platform.python_version()
    operating_system = platform.platform()
    ngspice_version = command_version(
        (
            "ngspice",
            "--version",
        ),
        preferred_pattern="ngspice-",
    )

    lines: list[str] = [
        "# CPC Validation Report",
        "",
        "## Overall result",
        "",
        f"**Status:** {overall_status}",
        "",
        f"**Validation profile:** `{profile}`",
        "",
        f"**Monte Carlo seed:** `{seed}`",
        "",
        f"**Steps passed:** {passed_count}/{len(results)}",
        "",
        f"**Steps failed:** {failed_count}",
        "",
        f"**Total measured runtime:** {total_duration:.3f} seconds",
        "",
        "## Execution metadata",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Started | {started_at.isoformat()} |",
        f"| Finished | {finished_at.isoformat()} |",
        f"| Git commit | `{git_commit}` |",
        f"| Git source tree | `{git_status}` |",
        f"| Python | `{python_version}` |",
        f"| Operating system | `{operating_system}` |",
        f"| ngspice | `{ngspice_version}` |",
        "",
        "## Validation summary",
        "",
        "| Step | Result | Return code | Duration |",
        "|---|---:|---:|---:|",
    ]

    for result in results:
        lines.append(
            "| "
            f"{result.name} | "
            f"{'PASS' if result.passed else 'FAIL'} | "
            f"{result.return_code} | "
            f"{result.duration_seconds:.3f} s |"
        )

    lines.extend(
        [
            "",
            "## Scope statement",
            "",
            (
                "This report validates the current constraint-compiled "
                "existential-response circuit and its RC output interface. "
                "It verifies logical agreement, SPICE execution, parameter "
                "variation, transient extraction, and first-order RC timing."
            ),
            "",
            (
                "The report does not establish the behavior of a future "
                "passive carrier network, a coherent physical carrier, or "
                "real hardware. The temperature stage uses explicitly "
                "imposed linear component-drift coefficients; it is a "
                "parameter-sensitivity study, not a calibrated device model."
            ),
            "",
            "## Detailed step output",
            "",
        ]
    )

    for result in results:
        lines.extend(
            [
                f"### {result.name}",
                "",
                result.description,
                "",
                f"**Command:** `{' '.join(result.command)}`",
                "",
                f"**Result:** {'PASS' if result.passed else 'FAIL'}",
                "",
                f"**Duration:** {result.duration_seconds:.3f} seconds",
                "",
                "**Standard output**",
                "",
                fenced_block(result.standard_output),
                "",
            ]
        )

        if result.standard_error.strip():
            lines.extend(
                [
                    "**Standard error**",
                    "",
                    fenced_block(result.standard_error),
                    "",
                ]
            )

    path.write_text(
        "\n".join(lines).rstrip() + "\n",
        encoding="utf-8",
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the complete CPC validation pipeline and generate "
            "a machine-readable summary and Markdown report."
        )
    )

    profile_group = parser.add_mutually_exclusive_group()

    profile_group.add_argument(
        "--quick",
        action="store_true",
        help="Run the reduced development validation profile.",
    )

    profile_group.add_argument(
        "--full",
        action="store_true",
        help="Run the complete reproducibility validation profile.",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=20260805,
        help="Monte Carlo random seed.",
    )

    parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        help=(
            "Run all remaining validation steps after a failed step."
        ),
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    profile = "full" if arguments.full else "quick"

    if shutil.which("ngspice") is None:
        raise SystemExit(
            "ERROR: ngspice is not available on PATH"
        )

    REPORT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )
    RESULT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    steps = build_steps(
        profile=profile,
        monte_carlo_seed=arguments.seed,
    )

    started_at = datetime.now(timezone.utc)
    results: list[StepResult] = []

    print("CPC consolidated validation")
    print()
    print(f"Profile: {profile}")
    print(f"Seed:    {arguments.seed}")
    print()

    for step in steps:
        result = run_command(step)
        results.append(result)

        if (
            not result.passed
            and not arguments.continue_on_failure
        ):
            print(
                "Stopping after failed validation step. "
                "Use --continue-on-failure to run every step."
            )
            print()
            break

    finished_at = datetime.now(timezone.utc)

    write_summary_csv(
        SUMMARY_PATH,
        results,
    )

    write_markdown_report(
        path=REPORT_PATH,
        profile=profile,
        seed=arguments.seed,
        results=results,
        started_at=started_at,
        finished_at=finished_at,
    )

    failed = [
        result
        for result in results
        if not result.passed
    ]

    print("Validation artifacts")
    print()
    print(f"Markdown report: {REPORT_PATH}")
    print(f"Summary CSV:     {SUMMARY_PATH}")
    print()

    if failed:
        print("Consolidated validation: FAIL")
        raise SystemExit(1)

    if len(results) != len(steps):
        print("Consolidated validation: INCOMPLETE")
        raise SystemExit(1)

    print("Consolidated validation: PASS")


if __name__ == "__main__":
    main()
