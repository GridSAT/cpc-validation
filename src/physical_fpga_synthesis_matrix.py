from __future__ import annotations

import hashlib
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from src.backends.fpga_ccir import FPGABackend
from src.backends.fpga_prepare import (
    prepare_fpga_execution,
)
from src.ccir_lower_parity import (
    lower_parity_instance_to_ccir,
)
from src.compiler import DEFAULT_XOR_INSTANCE
from src.physical_execution_evidence import (
    prepared_execution_hash,
)
from src.physical_fpga_synthesis import (
    FPGA_SYNTHESIS_PROJECTION_ID,
    project_fpga_synthesis_source,
)


P1_BOUNDARY_CASES = (
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
)


def _sha256_bytes(content: bytes) -> str:
    return (
        "sha256:"
        + hashlib.sha256(
            content
        ).hexdigest()
    )


@dataclass(frozen=True)
class P1SynthesisCase:
    case_id: str
    boundary_values: tuple[tuple[int, int], ...]

    prepared_execution_hash: str
    projection_id: str
    synthesis_source_sha256: str

    synthesis_tool: str
    synthesis_tool_version: str

    synthesized_json_sha256: str
    synthesized_json_size: int

    place_route_complete: bool = False
    bitstream_complete: bool = False
    physical_programming: bool = False
    physical_execution: bool = False

    def __post_init__(self) -> None:
        if not self.case_id:
            raise ValueError(
                "case_id must be non-empty"
            )

        if self.projection_id != (
            FPGA_SYNTHESIS_PROJECTION_ID
        ):
            raise ValueError(
                "unexpected synthesis projection identity"
            )

        for name, value in (
            (
                "prepared_execution_hash",
                self.prepared_execution_hash,
            ),
            (
                "synthesis_source_sha256",
                self.synthesis_source_sha256,
            ),
            (
                "synthesized_json_sha256",
                self.synthesized_json_sha256,
            ),
        ):
            if (
                not isinstance(value, str)
                or not value.startswith("sha256:")
                or len(value) != len("sha256:") + 64
            ):
                raise ValueError(
                    f"{name} must be a sha256 digest"
                )

        if not self.synthesis_tool:
            raise ValueError(
                "synthesis_tool must be non-empty"
            )

        if not self.synthesis_tool_version:
            raise ValueError(
                "synthesis_tool_version must be non-empty"
            )

        if self.synthesized_json_size <= 0:
            raise ValueError(
                "synthesized_json_size must be positive"
            )

        if any(
            (
                self.place_route_complete,
                self.bitstream_complete,
                self.physical_programming,
                self.physical_execution,
            )
        ):
            raise ValueError(
                "P1 synthesis case may not claim later physical stages"
            )


def yosys_version() -> str:
    result = subprocess.run(
        (
            "yosys",
            "-V",
        ),
        check=True,
        capture_output=True,
        text=True,
    )

    version = result.stdout.strip()

    if not version:
        raise RuntimeError(
            "yosys returned empty version identity"
        )

    return version


def synthesize_p1_case(
    x0: int,
    x3: int,
) -> P1SynthesisCase:
    if (
        isinstance(x0, bool)
        or isinstance(x3, bool)
        or x0 not in (0, 1)
        or x3 not in (0, 1)
    ):
        raise ValueError(
            "P1 boundary values must be integer bits"
        )

    program = lower_parity_instance_to_ccir(
        DEFAULT_XOR_INSTANCE
    )

    artifact = FPGABackend().compile(
        program
    )

    prepared = prepare_fpga_execution(
        program,
        artifact,
        {
            0: x0,
            3: x3,
        },
    )

    projected = project_fpga_synthesis_source(
        prepared
    )

    with tempfile.TemporaryDirectory(
        prefix="cpc-p1-synth-"
    ) as tmp:
        root = Path(tmp)

        source_path = root / "cpc_p1.v"
        json_path = root / "cpc_p1.json"

        source_path.write_text(
            projected.source,
            encoding="utf-8",
        )

        # Execute from the temporary build root and use stable relative
        # filenames. Yosys records source locations in its JSON output;
        # absolute TemporaryDirectory paths would therefore make otherwise
        # identical synthesis results bytewise nondeterministic.
        script = (
            "read_verilog -sv cpc_p1.v; "
            "hierarchy -check -top cpc_fpga_execution; "
            "synth_ice40 "
            "-top cpc_fpga_execution "
            "-json cpc_p1.json; "
            "stat"
        )

        subprocess.run(
            (
                "yosys",
                "-q",
                "-p",
                script,
            ),
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )

        if not json_path.is_file():
            raise RuntimeError(
                "yosys did not produce synthesized JSON"
            )

        content = json_path.read_bytes()

    return P1SynthesisCase(
        case_id=f"p1-{x0}{x3}",
        boundary_values=(
            (0, x0),
            (3, x3),
        ),
        prepared_execution_hash=(
            prepared_execution_hash(
                prepared
            )
        ),
        projection_id=(
            projected.projection_id
        ),
        synthesis_source_sha256=(
            projected.source_sha256
        ),
        synthesis_tool="yosys",
        synthesis_tool_version=(
            yosys_version()
        ),
        synthesized_json_sha256=(
            _sha256_bytes(
                content
            )
        ),
        synthesized_json_size=len(
            content
        ),
    )


def synthesize_p1_matrix() -> tuple[
    P1SynthesisCase,
    ...
]:
    return tuple(
        synthesize_p1_case(
            x0,
            x3,
        )
        for x0, x3 in P1_BOUNDARY_CASES
    )
