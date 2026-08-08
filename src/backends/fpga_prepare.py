from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Mapping

from src.backend import ExecutionArtifact
from src.ccir import CCIRProgram
from src.ccir_parity import (
    CCIRParityPayload,
    PARITY_CONSTRAINT_FAMILY,
)


@dataclass(frozen=True)
class FPGAPreparedExecution:
    """
    Deterministic Verilog-2001 realization of an FPGA ExecutionArtifact.

    Internal Boolean completions are represented structurally as parallel
    combinational branches. Preparation does not evaluate continuation
    semantics and does not receive an expected result.
    """

    backend_id: str
    backend_version: str
    execution_engine: str
    module_name: str
    boundary_values: tuple[tuple[int, int], ...]
    verilog_source: str


def prepare_fpga_execution(
    program: CCIRProgram,
    artifact: ExecutionArtifact,
    boundary_values: Mapping[int, int],
) -> FPGAPreparedExecution:
    """
    Prepare a hardware-oriented FPGA execution as deterministic Verilog-2001.

    Boundary assignments are admitted execution inputs. Internal assignments
    are expanded into parallel combinational branches whose outputs are ORed
    to produce the continuation result.
    """

    metadata = dict(artifact.metadata)
    parameters = dict(artifact.parameters)

    if metadata.get("backend_id") != "fpga":
        raise ValueError(
            "FPGA preparation requires an fpga ExecutionArtifact"
        )

    if metadata.get("backend_version") != "1":
        raise ValueError(
            "unsupported FPGA backend version"
        )

    if parameters.get("hdl_target") != "verilog-2001":
        raise ValueError(
            "FPGA artifact does not target verilog-2001"
        )

    normalized_boundary = _validate_boundary_values(
        program,
        boundary_values,
    )

    parity_constraints: list[CCIRParityPayload] = []

    for constraint in program.constraints:
        if constraint.family != PARITY_CONSTRAINT_FAMILY:
            raise ValueError(
                "FPGA v1 supports only parity constraints"
            )

        if not isinstance(
            constraint.payload,
            CCIRParityPayload,
        ):
            raise ValueError(
                "parity constraint requires CCIRParityPayload"
            )

        parity_constraints.append(
            constraint.payload
        )

    internal_variables = tuple(
        program.internal_variables
    )

    completions = tuple(
        product(
            (0, 1),
            repeat=len(internal_variables),
        )
    )

    lines: list[str] = [
        "// CPC FPGA backend prepared execution",
        "// backend: fpga/1",
        "// target: Verilog-2001",
        "//",
        "// Internal completions are instantiated structurally.",
        "// No expected continuation value is embedded.",
        "",
        "module cpc_fpga_execution(",
        "    output wire result",
        ");",
        "",
    ]

    for variable in program.boundary_variables:
        value = normalized_boundary[variable]

        lines.extend(
            [
                f"  wire x{variable};",
                f"  assign x{variable} = 1'b{value};",
            ]
        )

    if program.boundary_variables:
        lines.append("")

    completion_names: list[str] = []

    for completion_index, values in enumerate(
        completions
    ):
        completion_name = (
            f"completion_{completion_index}"
        )
        completion_names.append(
            completion_name
        )

        assignment = dict(
            zip(
                internal_variables,
                values,
                strict=True,
            )
        )

        lines.append(
            f"  // Internal completion {completion_index}"
        )

        for variable in internal_variables:
            lines.append(
                f"  wire {completion_name}_x{variable};"
            )
            lines.append(
                f"  assign {completion_name}_x{variable} = "
                f"1'b{assignment[variable]};"
            )

        match_names: list[str] = []

        for constraint_index, payload in enumerate(
            parity_constraints
        ):
            parity_name = (
                f"{completion_name}_parity_"
                f"{constraint_index}"
            )
            match_name = (
                f"{completion_name}_match_"
                f"{constraint_index}"
            )

            match_names.append(match_name)

            terms = [
                _signal_for_variable(
                    variable,
                    completion_name,
                    normalized_boundary,
                )
                for variable in payload.variables
            ]

            xor_expression = (
                " ^ ".join(terms)
                if terms
                else "1'b0"
            )

            lines.append(
                f"  wire {parity_name};"
            )
            lines.append(
                f"  assign {parity_name} = "
                f"{xor_expression};"
            )
            lines.append(
                f"  wire {match_name};"
            )
            lines.append(
                f"  assign {match_name} = "
                f"({parity_name} == 1'b{payload.parity});"
            )

        lines.append(
            f"  wire {completion_name};"
        )

        if match_names:
            lines.append(
                f"  assign {completion_name} = "
                + " & ".join(match_names)
                + ";"
            )
        else:
            lines.append(
                f"  assign {completion_name} = 1'b1;"
            )

        lines.append("")

    if completion_names:
        lines.append(
            "  assign result = "
            + " | ".join(completion_names)
            + ";"
        )
    else:
        lines.append(
            "  assign result = 1'b0;"
        )

    lines.extend(
        [
            "",
            "endmodule",
            "",
        ]
    )

    return FPGAPreparedExecution(
        backend_id="fpga",
        backend_version="1",
        execution_engine="verilog-2001",
        module_name="cpc_fpga_execution",
        boundary_values=tuple(
            sorted(
                normalized_boundary.items()
            )
        ),
        verilog_source="\n".join(lines),
    )


def _signal_for_variable(
    variable: int,
    completion_name: str,
    boundary_values: Mapping[int, int],
) -> str:
    if variable in boundary_values:
        return f"x{variable}"

    return f"{completion_name}_x{variable}"


def _validate_boundary_values(
    program: CCIRProgram,
    boundary_values: Mapping[int, int],
) -> dict[int, int]:
    required = set(
        program.boundary_variables
    )
    supplied = set(
        boundary_values
    )

    missing = required - supplied
    unexpected = supplied - required

    if missing:
        raise ValueError(
            "missing boundary values for: "
            + ", ".join(
                str(variable)
                for variable in sorted(missing)
            )
        )

    if unexpected:
        raise ValueError(
            "unexpected boundary values for: "
            + ", ".join(
                str(variable)
                for variable in sorted(unexpected)
            )
        )

    normalized = dict(
        boundary_values
    )

    for variable, value in normalized.items():
        if isinstance(value, bool) or value not in (0, 1):
            raise ValueError(
                f"boundary variable {variable} "
                "must be assigned integer 0 or 1"
            )

    return normalized
