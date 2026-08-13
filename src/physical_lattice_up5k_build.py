from __future__ import annotations

import hashlib
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

    bitstream: bytes
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

        if self.bitstream_sha256 != _sha256_bytes(
            self.bitstream
        ):
            raise ValueError(
                "bitstream_sha256 does not match bitstream"
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

        _run_checked(
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
        bitstream=bitstream,
        manifest=manifest,
    )
