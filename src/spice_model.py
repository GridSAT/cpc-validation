from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from src.compiler import (
    DEFAULT_XOR_INSTANCE,
    compile_parity_instance,
)


DECODE_THRESHOLD_V = 2.5


@dataclass(frozen=True)
class SpiceResponse:
    x0: int
    x3: int
    expected: int
    output_voltage: float
    decoded: int
    netlist_path: Path
    log_path: Path

    @property
    def final_voltage(self) -> float:
        """Backward-compatible alias for the final simulated output voltage."""
        return self.output_voltage

    @property
    def decoded_value(self) -> int:
        """Backward-compatible alias for the decoded continuation value."""
        return self.decoded


def expected_continuation(x0: int, x3: int) -> int:
    """
    Independent reference evaluator used only after simulation.

    Original constraints:

        x0 XOR x1 XOR x2 = 0
        x1 XOR x2 XOR x3 = 1

    A completion exists exactly when x0 XOR x3 = 1.
    """
    _validate_bit(x0, "x0")
    _validate_bit(x3, "x3")
    return x0 ^ x3


def simulate_response(
    x0: int,
    x3: int,
    *,
    supply_voltage: float = 5.0,
    resistance_kohm: float = 10.0,
    capacitance_uf: float = 1.0,
    threshold_voltage: float = DECODE_THRESHOLD_V,
    end_time_ms: float = 50.0,
) -> SpiceResponse:
    """
    Compile the original constraint system into an ngspice circuit.

    The generated netlist does not use expected_continuation() or the
    continuation truth table. It is generated solely from:

        x0 XOR x1 XOR x2 = 0
        x1 XOR x2 XOR x3 = 1

    For each internal assignment (x1, x2), the circuit creates a candidate
    response. The final source performs existential aggregation over the four
    candidates.
    """
    _validate_bit(x0, "x0")
    _validate_bit(x3, "x3")

    netlist_path = Path(f"/tmp/cpc_constraints_{x0}_{x3}.cir")
    log_path = Path(f"/tmp/cpc_constraints_{x0}_{x3}.out")

    netlist = _build_constraint_netlist(
        x0=x0,
        x3=x3,
        supply_voltage=supply_voltage,
        resistance_kohm=resistance_kohm,
        capacitance_uf=capacitance_uf,
        end_time_ms=end_time_ms,
    )

    netlist_path.write_text(netlist, encoding="utf-8")
    _run_ngspice(netlist_path, log_path)

    output_voltage = _read_measured_voltage(log_path)
    decoded = int(output_voltage >= threshold_voltage)

    # Reference evaluation occurs only after the physical simulation.
    expected = expected_continuation(x0, x3)

    return SpiceResponse(
        x0=x0,
        x3=x3,
        expected=expected,
        output_voltage=output_voltage,
        decoded=decoded,
        netlist_path=netlist_path,
        log_path=log_path,
    )


def _build_constraint_netlist(
    *,
    x0: int,
    x3: int,
    supply_voltage: float,
    resistance_kohm: float,
    capacitance_uf: float,
    end_time_ms: float,
) -> str:
    """
    Compile the default XOR benchmark through the generic parity compiler.

    This compatibility wrapper preserves the existing private interface used
    by the baseline simulator and transient-analysis module. The generic
    compiler in ``src.compiler`` is now the single source of truth for
    constraint-to-netlist generation.
    """
    compiled = compile_parity_instance(
        DEFAULT_XOR_INSTANCE,
        {
            0: x0,
            3: x3,
        },
        supply_voltage=supply_voltage,
        resistance_kohm=resistance_kohm,
        capacitance_uf=capacitance_uf,
        end_time_ms=end_time_ms,
    )

    return compiled.netlist

def _run_ngspice(netlist_path: Path, log_path: Path) -> None:
    completed = subprocess.run(
        [
            "ngspice",
            "-b",
            "-o",
            str(log_path),
            str(netlist_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if completed.returncode != 0:
        log_text = (
            log_path.read_text(encoding="utf-8", errors="replace")
            if log_path.exists()
            else ""
        )
        raise RuntimeError(
            f"ngspice failed with exit status {completed.returncode}.\n"
            f"Netlist: {netlist_path}\n"
            f"Standard output:\n{completed.stdout}\n"
            f"Standard error:\n{completed.stderr}\n"
            f"ngspice log:\n{log_text}"
        )


def _read_measured_voltage(log_path: Path) -> float:
    text = log_path.read_text(encoding="utf-8", errors="replace")

    match = re.search(
        r"vout_final\s*=\s*"
        r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)",
        text,
        flags=re.IGNORECASE,
    )

    if match is None:
        raise RuntimeError(
            "Could not locate vout_final in ngspice output.\n"
            f"Log file: {log_path}\n"
            f"Contents:\n{text}"
        )

    return float(match.group(1))


def _validate_bit(value: int, name: str) -> None:
    if value not in (0, 1):
        raise ValueError(f"{name} must be 0 or 1, received {value!r}")
