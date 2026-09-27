from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


N0_CONTROLLER_SYNTHESIS_SCHEMA = (
    "cpc.shor.n0.controller-synthesis.v1"
)

N0_CONTROLLER_SYNTHESIS_ID = (
    "CPC-SHOR-N0-CONTROLLER-SYNTHESIS-v1"
)

N0_CONTROLLER_TOP = (
    "cpc_shor_n0_controller"
)

EXPECTED_PORTS = {
    "clk": ("input", 1),
    "reset_n": ("input", 1),
    "arm_i": ("input", 1),
    "start_i": ("input", 1),
    "device_ready_i": ("input", 1),
    "sample_done_i": ("input", 1),
    "fault_i": ("input", 1),
    "probe_enable_o": ("output", 1),
    "acquire_enable_o": ("output", 1),
    "busy_o": ("output", 1),
    "done_o": ("output", 1),
    "error_o": ("output", 1),
    "event_code_o": ("output", 4),
}


def _sha256_bytes(
    content: bytes,
) -> str:
    return (
        "sha256:"
        + hashlib.sha256(
            content
        ).hexdigest()
    )


def yosys_version() -> str:
    completed = subprocess.run(
        (
            "yosys",
            "-V",
        ),
        check=True,
        capture_output=True,
        text=True,
    )

    version = (
        completed.stdout.strip()
        or completed.stderr.strip()
    )

    if not version:
        raise RuntimeError(
            "yosys returned empty version identity"
        )

    return version.splitlines()[0]


@dataclass(frozen=True)
class N0ControllerSynthesisResult:
    synthesis_id: str
    source_sha256: str
    synthesized_json_sha256: str
    synthesized_json_size: int
    yosys_version: str

    top_module: str
    port_count: int
    cell_count: int

    rtl_simulation_complete: bool = True
    synthesis_complete: bool = True

    physical_constraints_complete: bool = False
    place_route_complete: bool = False
    bitstream_complete: bool = False
    physical_programming: bool = False
    physical_execution: bool = False

    def __post_init__(
        self,
    ) -> None:
        if (
            self.synthesis_id
            != N0_CONTROLLER_SYNTHESIS_ID
        ):
            raise ValueError(
                "unsupported synthesis identity"
            )

        for name, value in (
            (
                "source_sha256",
                self.source_sha256,
            ),
            (
                "synthesized_json_sha256",
                self.synthesized_json_sha256,
            ),
        ):
            if (
                not isinstance(value, str)
                or not value.startswith(
                    "sha256:"
                )
                or len(value)
                != len("sha256:") + 64
            ):
                raise ValueError(
                    f"{name} must be a sha256 digest"
                )

        if (
            self.synthesized_json_size
            <= 0
        ):
            raise ValueError(
                "synthesized JSON size must be positive"
            )

        if (
            self.top_module
            != N0_CONTROLLER_TOP
        ):
            raise ValueError(
                "unexpected synthesized top module"
            )

        if (
            self.port_count
            != len(
                EXPECTED_PORTS
            )
        ):
            raise ValueError(
                "unexpected synthesized port count"
            )

        if self.cell_count <= 0:
            raise ValueError(
                "synthesized controller must contain cells"
            )

        if not (
            self.rtl_simulation_complete
            and self.synthesis_complete
        ):
            raise ValueError(
                "synthesis record requires prior RTL simulation "
                "and successful synthesis"
            )

        if any(
            (
                self.physical_constraints_complete,
                self.place_route_complete,
                self.bitstream_complete,
                self.physical_programming,
                self.physical_execution,
            )
        ):
            raise ValueError(
                "board-independent synthesis may not claim "
                "later physical stages"
            )

    @property
    def schema(
        self,
    ) -> str:
        return (
            N0_CONTROLLER_SYNTHESIS_SCHEMA
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "schema": self.schema,
            "synthesis_id": self.synthesis_id,
            "source_sha256": (
                self.source_sha256
            ),
            "synthesized_json_sha256": (
                self.synthesized_json_sha256
            ),
            "synthesized_json_size": (
                self.synthesized_json_size
            ),
            "yosys_version": (
                self.yosys_version
            ),
            "top_module": (
                self.top_module
            ),
            "port_count": (
                self.port_count
            ),
            "cell_count": (
                self.cell_count
            ),
            "rtl_simulation_complete": (
                self.rtl_simulation_complete
            ),
            "synthesis_complete": (
                self.synthesis_complete
            ),
            "physical_constraints_complete": (
                self.physical_constraints_complete
            ),
            "place_route_complete": (
                self.place_route_complete
            ),
            "bitstream_complete": (
                self.bitstream_complete
            ),
            "physical_programming": (
                self.physical_programming
            ),
            "physical_execution": (
                self.physical_execution
            ),
        }


def audit_synthesized_json(
    content: bytes,
) -> tuple[
    str,
    int,
    int,
]:
    data = json.loads(
        content.decode(
            "utf-8"
        )
    )

    modules = data.get(
        "modules"
    )

    if not isinstance(
        modules,
        dict,
    ):
        raise ValueError(
            "Yosys JSON has no modules mapping"
        )

    if N0_CONTROLLER_TOP not in modules:
        raise ValueError(
            "controller top module missing from Yosys JSON"
        )

    module = modules[
        N0_CONTROLLER_TOP
    ]

    ports = module.get(
        "ports"
    )

    if not isinstance(
        ports,
        dict,
    ):
        raise ValueError(
            "controller top has no ports mapping"
        )

    if set(ports) != set(
        EXPECTED_PORTS
    ):
        raise ValueError(
            "synthesized controller port set does not "
            "match logical protocol"
        )

    for name, (
        expected_direction,
        expected_width,
    ) in EXPECTED_PORTS.items():
        port = ports[
            name
        ]

        if (
            port.get("direction")
            != expected_direction
        ):
            raise ValueError(
                f"unexpected direction for port {name}"
            )

        bits = port.get(
            "bits"
        )

        if (
            not isinstance(bits, list)
            or len(bits)
            != expected_width
        ):
            raise ValueError(
                f"unexpected width for port {name}"
            )

    cells = module.get(
        "cells",
        {},
    )

    if not isinstance(
        cells,
        dict,
    ):
        raise ValueError(
            "controller cells must be a mapping"
        )

    if not cells:
        raise ValueError(
            "controller synthesis produced no cells"
        )

    text = json.dumps(
        data,
        sort_keys=True,
    ).lower()

    forbidden = (
        "$display",
        "$finish",
        "iceprog",
        "nextpnr",
        "expected_answer",
        "truth_phase",
        "semantic_answer",
    )

    for token in forbidden:
        if token in text:
            raise ValueError(
                "forbidden token in synthesized controller: "
                + token
            )

    return (
        N0_CONTROLLER_TOP,
        len(
            ports
        ),
        len(
            cells
        ),
    )


def synthesize_n0_controller(
    *,
    rtl_path: Path,
) -> tuple[
    N0ControllerSynthesisResult,
    bytes,
]:
    rtl_path = Path(
        rtl_path
    )

    if not rtl_path.is_file():
        raise ValueError(
            "controller RTL file does not exist"
        )

    source = rtl_path.read_bytes()

    with tempfile.TemporaryDirectory(
        prefix="cpc-n0-controller-synth-"
    ) as temporary_directory:
        root = Path(
            temporary_directory
        )

        local_source = (
            root
            / "n0_controller.v"
        )

        json_path = (
            root
            / "n0_controller.json"
        )

        local_source.write_bytes(
            source
        )

        script = (
            "read_verilog -sv n0_controller.v; "
            "hierarchy -check "
            "-top cpc_shor_n0_controller; "
            "synth_ice40 "
            "-top cpc_shor_n0_controller "
            "-json n0_controller.json; "
            "stat"
        )

        completed = subprocess.run(
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

        if (
            completed.returncode
            != 0
        ):
            raise RuntimeError(
                "Yosys synthesis failed"
            )

        if not json_path.is_file():
            raise RuntimeError(
                "Yosys did not produce synthesized JSON"
            )

        synthesized = (
            json_path.read_bytes()
        )

    (
        top_module,
        port_count,
        cell_count,
    ) = audit_synthesized_json(
        synthesized
    )

    result = (
        N0ControllerSynthesisResult(
            synthesis_id=(
                N0_CONTROLLER_SYNTHESIS_ID
            ),
            source_sha256=(
                _sha256_bytes(
                    source
                )
            ),
            synthesized_json_sha256=(
                _sha256_bytes(
                    synthesized
                )
            ),
            synthesized_json_size=len(
                synthesized
            ),
            yosys_version=(
                yosys_version()
            ),
            top_module=top_module,
            port_count=port_count,
            cell_count=cell_count,
        )
    )

    return (
        result,
        synthesized,
    )
