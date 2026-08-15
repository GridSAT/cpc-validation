from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.backends.fpga_ccir import FPGABackend
from src.backends.fpga_prepare import prepare_fpga_execution
from src.ccir_lower_parity import lower_parity_instance_to_ccir
from src.compiler import DEFAULT_XOR_INSTANCE
from src.physical_fpga_output_wrapper import wrap_fpga_physical_output
from src.physical_fpga_synthesis import project_fpga_synthesis_source
from src.physical_lattice_up5k_build import build_lattice_up5k_bitstream


OUTPUT_DIRECTORY = Path("evidence/p1/physical")
BITSTREAM_NAME = "p1-icebreaker.bin"
MANIFEST_NAME = "p1-physical-build-manifest.json"
REPORT_NAME = "p1-physical-build-report.json"
VERILOG_NAME = "p1-physical-top.v"


def _sha256(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def _atomic_write(path: Path, content: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def build_p1_inputs():
    """Return the fixed accepted P1 prepared execution and physical source."""
    program = lower_parity_instance_to_ccir(DEFAULT_XOR_INSTANCE)
    artifact = FPGABackend().compile(program)
    prepared = prepare_fpga_execution(program, artifact, {0: 0, 3: 1})
    synthesis = project_fpga_synthesis_source(prepared)
    return prepared, wrap_fpga_physical_output(synthesis)


def write_p1_physical_artifacts(
    output_directory: Path = OUTPUT_DIRECTORY,
) -> dict[str, object]:
    """Build and atomically retain the fixed pre-programming P1 artifacts."""
    output_directory = Path(output_directory)
    output_directory.mkdir(mode=0o750, parents=True, exist_ok=True)

    prepared, physical_source = build_p1_inputs()
    build = build_lattice_up5k_bitstream(
        prepared=prepared,
        physical_source=physical_source,
    )

    bitstream = build.bitstream
    manifest = build.manifest.to_json().encode("utf-8")
    verilog = physical_source.source.encode("utf-8")

    report: dict[str, object] = {
        "schema": "cpc.p1-physical-build-report.v1",
        "build_id": build.build_id,
        "status": "built-not-programmed",
        "artifacts": {
            "bitstream": BITSTREAM_NAME,
            "build_manifest": MANIFEST_NAME,
            "physical_verilog": VERILOG_NAME,
        },
        "digests": {
            "bitstream": build.bitstream_sha256,
            "build_manifest": _sha256(manifest),
            "physical_verilog": build.verilog_sha256,
            "physical_constraints": build.pcf_sha256,
            "routed_configuration": build.asc_sha256,
        },
        "build_manifest_hash": build.manifest.manifest_hash,
    }
    report_bytes = (
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")

    _atomic_write(output_directory / BITSTREAM_NAME, bitstream)
    _atomic_write(output_directory / MANIFEST_NAME, manifest)
    _atomic_write(output_directory / VERILOG_NAME, verilog)
    _atomic_write(output_directory / REPORT_NAME, report_bytes)
    return report


def main() -> None:
    report = write_p1_physical_artifacts()
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
