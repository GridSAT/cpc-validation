from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from src.physical_build_provenance import (
    BuildInputRecord,
    BuildToolIdentity,
    PhysicalBuildManifest,
    build_manifest_for_prepared_execution,
)
from src.physical_fpga_output_wrapper import (
    FPGAPhysicalSource,
)
from src.physical_fpga_profile import (
    PHYSICAL_FPGA_PROFILE_ID,
)
from src.physical_lattice_up5k_breakout_constraints import (
    LATTICE_UP5K_P1_CONSTRAINT,
    LATTICE_UP5K_P1_PCF_PATH,
)
from src.physical_lattice_up5k_breakout_target import (
    LATTICE_UP5K_BREAKOUT_TARGET,
)
from src.prepared_execution import PreparedExecution


LATTICE_UP5K_BUILD_ID = (
    "lattice-ice40up5k-open-toolchain-build.v1"
)

LATTICE_UP5K_TIMING_VALIDATION_ID = (
    "nextpnr-ice40-static-combinational-timing.v1"
)


def _sha256_bytes(content: bytes) -> str:
    return (
        "sha256:"
        + hashlib.sha256(content).hexdigest()
    )


def _run_checked(
    arguments: list[str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        check=True,
        capture_output=True,
        text=True,
    )


def _tool_version(
    arguments: list[str],
) -> str:
    completed = _run_checked(
        arguments
    )

    text = (
        completed.stdout.strip()
        or completed.stderr.strip()
    )

    if not text:
        raise RuntimeError(
            "tool returned empty version identity"
        )

    return text.splitlines()[0]


def _debian_package_version(
    package_name: str,
) -> str:
    """
    Return the exact installed Debian package identity.

    IceStorm's ``icepack`` does not provide a successful version-query
    command on the reference Ubuntu toolchain, so its version is bound to
    the installed ``fpga-icestorm`` package instead.
    """

    completed = _run_checked(
        [
            "dpkg-query",
            "-W",
            "-f=${Package} ${Version}",
            package_name,
        ]
    )

    version = completed.stdout.strip()

    if not version:
        raise RuntimeError(
            "package manager returned empty version identity"
        )

    return version


def _build_timing_report(
    *,
    nextpnr_result: subprocess.CompletedProcess[str],
    nextpnr_version: str,
    routed_configuration_sha256: str,
    bitstream_sha256: str,
) -> bytes:
    """Return deterministic timing evidence for the static P1 design."""

    diagnostic = nextpnr_result.stderr
    required_diagnostics = (
        "Annotating ports with timing budgets for target frequency 12.00 MHz",
        "No Fmax available; no interior timing paths found in design.",
        "Routing complete.",
        "Program finished normally.",
    )

    missing = tuple(
        item
        for item in required_diagnostics
        if item not in diagnostic
    )
    if missing:
        raise RuntimeError(
            "nextpnr-ice40 timing diagnostics are incomplete: "
            + ", ".join(missing)
        )

    target = LATTICE_UP5K_BREAKOUT_TARGET
    report: dict[str, object] = {
        "schema": "cpc.fpga-timing-report.v1",
        "timing_validation_id": LATTICE_UP5K_TIMING_VALIDATION_ID,
        "build_id": LATTICE_UP5K_BUILD_ID,
        "tool": {
            "name": target.place_route_tool,
            "version": nextpnr_version,
        },
        "target": {
            "device_family": target.device_family,
            "device_part": target.device_part,
            "package": target.nextpnr_package,
        },
        "binding": {
            "bitstream_sha256": bitstream_sha256,
            "routed_configuration_sha256": routed_configuration_sha256,
        },
        "admitted_timing_conditions": {
            "design_class": "static-combinational-output",
            "stimulus_mode": "synthesis-bound-constants",
            "observation_mode": "single-shot-static-output",
            "nextpnr_port_budget_frequency_mhz": 12.0,
        },
        "analysis": {
            "clock_domains": 0,
            "fmax_available": False,
            "interior_timing_paths_found": False,
            "route_completed": True,
            "tool_completed_normally": True,
        },
        "status": "pass-static-combinational-no-interior-paths",
        "diagnostics": list(required_diagnostics),
        "scope": (
            "The P1 realization is a static combinational output with no "
            "clock domain or interior timing path. This report establishes "
            "successful routing under the declared static observation "
            "conditions; it makes no Fmax, latency, or complexity claim."
        ),
    }
    return (
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


@dataclass(frozen=True)
class LatticeUP5KBuild:
    """
    Deterministic pre-programming build result for the Lattice
    iCE40 UltraPlus Breakout Board.

    This object records generated build artifacts and RFC-0009 build
    provenance.  It does not assert device programming, execution,
    physical observation, decoding, or semantic correctness.
    """

    build_id: str

    verilog_sha256: str
    pcf_sha256: str
    asc_sha256: str
    bitstream_sha256: str
    timing_report_sha256: str

    bitstream: bytes
    timing_report: bytes
    manifest: PhysicalBuildManifest

    def __post_init__(self) -> None:
        if self.build_id != LATTICE_UP5K_BUILD_ID:
            raise ValueError(
                "unsupported Lattice UP5K build identity"
            )

        for name, value in (
            ("verilog_sha256", self.verilog_sha256),
            ("pcf_sha256", self.pcf_sha256),
            ("asc_sha256", self.asc_sha256),
            ("bitstream_sha256", self.bitstream_sha256),
            ("timing_report_sha256", self.timing_report_sha256),
        ):
            if (
                not isinstance(value, str)
                or not value.startswith("sha256:")
                or len(value) != len("sha256:") + 64
            ):
                raise ValueError(
                    f"{name} must be a sha256 digest"
                )

        if not isinstance(self.bitstream, bytes):
            raise ValueError(
                "bitstream must be bytes"
            )

        if not self.bitstream:
            raise ValueError(
                "bitstream must be non-empty"
            )

        if not isinstance(self.timing_report, bytes):
            raise ValueError(
                "timing_report must be bytes"
            )

        if not self.timing_report:
            raise ValueError(
                "timing_report must be non-empty"
            )

        if self.bitstream_sha256 != _sha256_bytes(
            self.bitstream
        ):
            raise ValueError(
                "bitstream_sha256 does not match bitstream"
            )

        if self.timing_report_sha256 != _sha256_bytes(
            self.timing_report
        ):
            raise ValueError(
                "timing_report_sha256 does not match timing report"
            )

        if (
            self.manifest.bitstream_sha256
            != self.bitstream_sha256
        ):
            raise ValueError(
                "manifest bitstream identity does not match build"
            )


def build_lattice_up5k_bitstream(
    *,
    prepared: PreparedExecution,
    physical_source: FPGAPhysicalSource,
    pcf_path: Path = LATTICE_UP5K_P1_PCF_PATH,
) -> LatticeUP5KBuild:
    """
    Build one physical FPGA bitstream with the fixed open-source UP5K
    toolchain.

    The operation stops after bitstream generation.  No programmer is
    invoked and no physical-execution evidence is created.
    """

    target = LATTICE_UP5K_BREAKOUT_TARGET
    constraint = LATTICE_UP5K_P1_CONSTRAINT

    if prepared.backend_id != target.backend_id:
        raise ValueError(
            "prepared execution backend does not match target"
        )

    if prepared.backend_version != target.backend_version:
        raise ValueError(
            "prepared execution backend version does not match target"
        )

    if physical_source.top_module != "cpc_physical_top":
        raise ValueError(
            "unexpected physical top module"
        )

    if physical_source.result_port != constraint.logical_port:
        raise ValueError(
            "physical result port does not match constraint"
        )

    pcf_path = Path(
        pcf_path
    )

    if not pcf_path.is_file():
        raise ValueError(
            "physical constraint file does not exist"
        )

    pcf_bytes = pcf_path.read_bytes()

    if pcf_bytes != constraint.pcf_text.encode(
        "utf-8"
    ):
        raise ValueError(
            "physical constraint file does not match accepted constraint"
        )

    verilog_bytes = physical_source.source.encode(
        "utf-8"
    )

    yosys_version = _tool_version(
        ["yosys", "-V"]
    )

    nextpnr_version = _tool_version(
        ["nextpnr-ice40", "--version"]
    )

    icepack_version = _debian_package_version(
        "fpga-icestorm"
    )

    with tempfile.TemporaryDirectory(
        prefix="cpc-lattice-up5k-"
    ) as temporary_directory:
        directory = Path(
            temporary_directory
        )

        verilog_path = directory / "physical-top.v"
        json_path = directory / "synth.json"
        asc_path = directory / "routed.asc"
        bitstream_path = directory / "physical.bin"

        verilog_path.write_bytes(
            verilog_bytes
        )

        _run_checked(
            [
                "yosys",
                "-q",
                "-p",
                (
                    "synth_ice40 "
                    "-top cpc_physical_top "
                    f"-json {json_path}"
                ),
                str(verilog_path),
            ]
        )

        if not json_path.is_file():
            raise RuntimeError(
                "yosys did not produce synthesized JSON"
            )

        nextpnr_result = _run_checked(
            [
                "nextpnr-ice40",
                "--up5k",
                "--package",
                target.nextpnr_package,
                "--json",
                str(json_path),
                "--pcf",
                str(pcf_path.resolve()),
                "--asc",
                str(asc_path),
            ]
        )

        if not asc_path.is_file():
            raise RuntimeError(
                "nextpnr-ice40 did not produce routed ASC"
            )

        asc_bytes = asc_path.read_bytes()

        _run_checked(
            [
                "icepack",
                str(asc_path),
                str(bitstream_path),
            ]
        )

        if not bitstream_path.is_file():
            raise RuntimeError(
                "icepack did not produce bitstream"
            )

        bitstream = bitstream_path.read_bytes()

    if not bitstream:
        raise RuntimeError(
            "generated bitstream is empty"
        )

    verilog_sha256 = _sha256_bytes(
        verilog_bytes
    )

    pcf_sha256 = _sha256_bytes(
        pcf_bytes
    )

    asc_sha256 = _sha256_bytes(
        asc_bytes
    )

    bitstream_sha256 = _sha256_bytes(
        bitstream
    )

    timing_report = _build_timing_report(
        nextpnr_result=nextpnr_result,
        nextpnr_version=nextpnr_version,
        routed_configuration_sha256=asc_sha256,
        bitstream_sha256=bitstream_sha256,
    )

    timing_report_sha256 = _sha256_bytes(
        timing_report
    )

    tools = tuple(
        sorted(
            (
                BuildToolIdentity(
                    stage="bitstream-generation",
                    tool=target.bitstream_tool,
                    version=icepack_version,
                ),
                BuildToolIdentity(
                    stage="place-route",
                    tool=target.place_route_tool,
                    version=nextpnr_version,
                ),
                BuildToolIdentity(
                    stage="synthesis",
                    tool=target.synthesis_tool,
                    version=yosys_version,
                ),
            )
        )
    )

    inputs = tuple(
        sorted(
            (
                BuildInputRecord(
                    input_id="physical-constraints",
                    media_type="text/plain",
                    sha256=pcf_sha256,
                ),
                BuildInputRecord(
                    input_id="physical-verilog",
                    media_type="text/x-verilog",
                    sha256=verilog_sha256,
                ),
            )
        )
    )

    manifest = build_manifest_for_prepared_execution(
        prepared=prepared,
        physical_profile_id=(
            PHYSICAL_FPGA_PROFILE_ID
        ),
        device_family=target.device_family,
        device_part=target.device_part,
        tools=tools,
        inputs=inputs,
        bitstream_format=target.bitstream_format,
        bitstream_sha256=bitstream_sha256,
        metadata=(
            ("build_id", LATTICE_UP5K_BUILD_ID),
            (
                "constraint_id",
                constraint.constraint_id,
            ),
            ("target_id", target.target_id),
        ),
    )

    return LatticeUP5KBuild(
        build_id=LATTICE_UP5K_BUILD_ID,
        verilog_sha256=verilog_sha256,
        pcf_sha256=pcf_sha256,
        asc_sha256=asc_sha256,
        bitstream_sha256=bitstream_sha256,
        timing_report_sha256=timing_report_sha256,
        bitstream=bitstream,
        timing_report=timing_report,
        manifest=manifest,
    )
