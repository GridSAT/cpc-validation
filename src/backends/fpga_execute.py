from __future__ import annotations

import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from src.observable_execution import ObservableExecution
from src.prepared_execution import PreparedExecution


FPGA_EXECUTION_ID = "fpga.icarus-verilog.v1"

_RESULT_PATTERN = re.compile(
    r"^CPC_RESULT=([01])$"
)


def execute_fpga(
    prepared: PreparedExecution,
) -> ObservableExecution:
    """
    Execute one RFC-0008 prepared FPGA computation using Icarus Verilog.

    Execution consumes only PreparedExecution.

    No CCIR program, ExecutionArtifact, source representation, reference
    evaluator, boundary assignment, or expected semantic result participates
    in this stage.
    """

    if prepared.backend_id != "fpga":
        raise ValueError(
            "FPGA execution requires an FPGA prepared execution"
        )

    if not isinstance(
        prepared.payload,
        str,
    ):
        raise ValueError(
            "FPGA prepared execution payload must be Verilog source"
        )

    interface = dict(
        prepared.interface
    )

    if interface.get(
        "readout_signal"
    ) != "result":
        raise ValueError(
            "FPGA execution requires admitted readout signal 'result'"
        )

    with TemporaryDirectory(
        prefix="cpc-fpga-execution-"
    ) as directory:
        root = Path(directory)

        design_path = (
            root / "execution.v"
        )

        executable_path = (
            root / "execution.vvp"
        )

        design_path.write_text(
            prepared.payload,
            encoding="utf-8",
        )

        compile_result = subprocess.run(
            [
                "iverilog",
                "-g2012",
                "-o",
                str(executable_path),
                str(design_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if compile_result.returncode != 0:
            detail = (
                compile_result.stderr.strip()
                or compile_result.stdout.strip()
                or "unknown Icarus Verilog compilation error"
            )

            raise RuntimeError(
                "FPGA Verilog compilation failed: "
                + detail
            )

        execution_result = subprocess.run(
            [
                "vvp",
                str(executable_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if execution_result.returncode != 0:
            detail = (
                execution_result.stderr.strip()
                or execution_result.stdout.strip()
                or "unknown Icarus Verilog execution error"
            )

            raise RuntimeError(
                "FPGA Verilog execution failed: "
                + detail
            )

        result_bit = _extract_result_bit(
            execution_result.stdout
        )

        execution_engine_version = (
            _iverilog_version()
        )

    return ObservableExecution(
        backend_id=prepared.backend_id,
        backend_version=prepared.backend_version,
        observations=(
            (
                "result_bit",
                result_bit,
            ),
        ),
        provenance=prepared.provenance,
        metadata=(
            (
                "execution_engine",
                "iverilog/vvp",
            ),
            (
                "execution_engine_version",
                execution_engine_version,
            ),
            (
                "execution_id",
                FPGA_EXECUTION_ID,
            ),
        ),
    )


def _extract_result_bit(
    stdout: str,
) -> int:
    matches: list[int] = []

    for line in stdout.splitlines():
        stripped = line.strip()

        match = _RESULT_PATTERN.fullmatch(
            stripped
        )

        if match is not None:
            matches.append(
                int(
                    match.group(1)
                )
            )
            continue

        if stripped.startswith(
            "CPC_RESULT="
        ):
            raise RuntimeError(
                "FPGA execution produced malformed CPC_RESULT observation"
            )

    if not matches:
        raise RuntimeError(
            "FPGA execution produced no CPC_RESULT observation"
        )

    if len(matches) != 1:
        raise RuntimeError(
            "FPGA execution produced multiple CPC_RESULT observations"
        )

    return matches[0]


def _iverilog_version() -> str:
    result = subprocess.run(
        [
            "iverilog",
            "-V",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    text = "\n".join(
        part
        for part in (
            result.stdout,
            result.stderr,
        )
        if part
    )

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith(
            "Icarus Verilog version "
        ):
            version = stripped.removeprefix(
                "Icarus Verilog version "
            ).strip()

            if version:
                return version

    raise RuntimeError(
        "unable to determine Icarus Verilog version"
    )
