from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SpiceResponse:
    x0: int
    x3: int
    expected: int
    output_voltage: float
    decoded: int
    netlist_path: Path
    log_path: Path


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
    threshold_voltage: float = 2.5,
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
    Compile the two XOR constraints into candidate-validity sources.

    Normalized Boolean XOR is represented algebraically by

        XOR(a,b) = a + b - 2ab

    for a,b in {0,1}. Three-input XOR is obtained by composition.

    Each candidate source is high exactly when its fixed internal assignment
    (x1,x2) satisfies both constraints. The existential output is high when
    at least one candidate source is high.
    """
    candidate_lines: list[str] = []
    candidate_nodes: list[str] = []

    x0_expr = f"(v(x0)/{supply_voltage})"
    x3_expr = f"(v(x3)/{supply_voltage})"

    for x1 in (0, 1):
        for x2 in (0, 1):
            node = f"cand{x1}{x2}"
            candidate_nodes.append(node)

            parity_1 = _xor3_expression(x0_expr, str(x1), str(x2))
            parity_2 = _xor3_expression(str(x1), str(x2), x3_expr)

            # Constraint 1 requires parity_1 = 0.
            constraint_1_valid = f"(1-({parity_1}))"

            # Constraint 2 requires parity_2 = 1.
            constraint_2_valid = f"({parity_2})"

            candidate_valid = (
                f"({constraint_1_valid})"
                f"*({constraint_2_valid})"
            )

            candidate_lines.append(
                f"B{node} {node} 0 "
                f"V={{{supply_voltage}*({candidate_valid})}}"
            )

    # Boolean OR over normalized candidate voltages:
    #
    #   OR(c1,...,cn) = 1 - product_i(1-ci)
    #
    no_candidate_products = "*".join(
        f"(1-v({node})/{supply_voltage})"
        for node in candidate_nodes
    )
    existential_expression = (
        f"{supply_voltage}*(1-({no_candidate_products}))"
    )

    lines = [
        "* CPC constraint-compiled existential continuation circuit",
        "*",
        "* Source constraints:",
        "*   x0 XOR x1 XOR x2 = 0",
        "*   x1 XOR x2 XOR x3 = 1",
        "*",
        "* Python supplies only x0, x3 and the constraint structure.",
        "* The continuation answer is not inserted into this netlist.",
        "",
        f"Vx0 x0 0 {x0 * supply_voltage}",
        f"Vx3 x3 0 {x3 * supply_voltage}",
        "",
        "* One candidate-validity source per internal assignment (x1,x2)",
        *candidate_lines,
        "",
        "* Existential aggregation: high iff at least one completion exists",
        f"Bexist logic 0 V={{{existential_expression}}}",
        "",
        "* Restricted RC interface",
        f"Rout logic vout {resistance_kohm}k",
        f"Cout vout 0 {capacitance_uf}u",
        "Rleak vout 0 1G",
        "",
        f".tran 0.1m {end_time_ms}m",
        f".meas tran vout_final FIND v(vout) AT={end_time_ms}m",
        ".end",
        "",
    ]

    return "\n".join(lines)


def _xor2_expression(a: str, b: str) -> str:
    return f"(({a})+({b})-2*({a})*({b}))"


def _xor3_expression(a: str, b: str, c: str) -> str:
    xor_ab = _xor2_expression(a, b)
    return _xor2_expression(xor_ab, c)


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
