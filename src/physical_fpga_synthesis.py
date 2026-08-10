from __future__ import annotations

import hashlib
from dataclasses import dataclass

from src.physical_execution_evidence import (
    prepared_execution_hash,
)
from src.prepared_execution import PreparedExecution


FPGA_SYNTHESIS_PROJECTION_ID = (
    "fpga.remove-simulation-readout.v1"
)

_SIMULATION_READOUT = (
    "\n"
    "  initial begin\n"
    "    #1;\n"
    '    $display("CPC_RESULT=%b", result);\n'
    "    $finish;\n"
    "  end\n"
)


def _sha256_text(value: str) -> str:
    digest = hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()

    return f"sha256:{digest}"


@dataclass(frozen=True)
class FPGASynthesisSource:
    """
    Deterministic physical-synthesis projection of an RFC-0008 FPGA
    PreparedExecution.

    The projection removes only the globally fixed simulation readout block
    emitted by ``fpga.verilog.v1``.  It performs no semantic evaluation and
    introduces no board-, constraint-, or answer-dependent information.
    """

    projection_id: str
    prepared_execution_hash: str
    source: str
    source_sha256: str

    def __post_init__(self) -> None:
        if self.projection_id != FPGA_SYNTHESIS_PROJECTION_ID:
            raise ValueError(
                "unsupported FPGA synthesis projection"
            )

        if not self.prepared_execution_hash.startswith(
            "sha256:"
        ):
            raise ValueError(
                "prepared_execution_hash must be a sha256 digest"
            )

        if not isinstance(self.source, str) or not self.source:
            raise ValueError(
                "source must be non-empty Verilog text"
            )

        expected = _sha256_text(
            self.source
        )

        if self.source_sha256 != expected:
            raise ValueError(
                "source_sha256 does not match source"
            )


def project_fpga_synthesis_source(
    prepared: PreparedExecution,
) -> FPGASynthesisSource:
    """
    Project an RFC-0008 FPGA PreparedExecution into synthesis-only Verilog.

    This operation is intentionally fail-closed.  The exact simulation
    readout block emitted by the accepted ``fpga.verilog.v1`` preparation
    must occur exactly once.  No other source transformation is permitted.
    """

    if prepared.backend_id != "fpga":
        raise ValueError(
            "FPGA synthesis projection requires fpga backend"
        )

    if prepared.backend_version != "1":
        raise ValueError(
            "unsupported FPGA backend version"
        )

    metadata = dict(
        prepared.metadata
    )

    if metadata.get("preparation_id") != "fpga.verilog.v1":
        raise ValueError(
            "unsupported FPGA preparation identity"
        )

    if metadata.get("module_name") != "cpc_fpga_execution":
        raise ValueError(
            "unexpected FPGA module identity"
        )

    if not isinstance(prepared.payload, str):
        raise ValueError(
            "FPGA prepared payload must be Verilog text"
        )

    if prepared.payload.count(_SIMULATION_READOUT) != 1:
        raise ValueError(
            "FPGA prepared payload does not contain exactly one "
            "canonical simulation readout block"
        )

    source = prepared.payload.replace(
        _SIMULATION_READOUT,
        "\n",
        1,
    )

    if "$display" in source or "$finish" in source:
        raise ValueError(
            "simulation system task remains after synthesis projection"
        )

    return FPGASynthesisSource(
        projection_id=FPGA_SYNTHESIS_PROJECTION_ID,
        prepared_execution_hash=prepared_execution_hash(
            prepared
        ),
        source=source,
        source_sha256=_sha256_text(
            source
        ),
    )
