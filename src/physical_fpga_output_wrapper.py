from __future__ import annotations

import hashlib
from dataclasses import dataclass

from src.physical_fpga_synthesis import (
    FPGASynthesisSource,
)


FPGA_PHYSICAL_WRAPPER_ID = (
    "fpga.physical-output-wrapper.v1"
)

FPGA_PHYSICAL_TOP_MODULE = "cpc_physical_top"
FPGA_PHYSICAL_RESULT_PORT = "result_out"

_WRAPPER = """
module cpc_physical_top(
    output wire result_out
);

  wire result;

  cpc_fpga_execution execution (
      .result(result)
  );

  assign result_out = result;

endmodule
"""


def _sha256_text(value: str) -> str:
    digest = hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()

    return f"sha256:{digest}"


@dataclass(frozen=True)
class FPGAPhysicalSource:
    """
    Deterministic physical-top adaptation of an FPGA synthesis source.

    The wrapper preserves the semantic result without inversion or board
    binding.  It introduces only a top-level output port suitable for later
    physical constraint binding.

    This object does not assert place-and-route, bitstream generation,
    programming, execution, or physical observation.
    """

    wrapper_id: str
    synthesis_source_sha256: str

    top_module: str
    result_port: str

    source: str
    source_sha256: str

    def __post_init__(self) -> None:
        if self.wrapper_id != FPGA_PHYSICAL_WRAPPER_ID:
            raise ValueError(
                "unsupported FPGA physical wrapper"
            )

        if (
            not isinstance(
                self.synthesis_source_sha256,
                str,
            )
            or not self.synthesis_source_sha256.startswith(
                "sha256:"
            )
        ):
            raise ValueError(
                "synthesis_source_sha256 must be a sha256 digest"
            )

        if self.top_module != FPGA_PHYSICAL_TOP_MODULE:
            raise ValueError(
                "unexpected physical top module"
            )

        if self.result_port != FPGA_PHYSICAL_RESULT_PORT:
            raise ValueError(
                "unexpected physical result port"
            )

        if not isinstance(self.source, str) or not self.source:
            raise ValueError(
                "source must be non-empty Verilog text"
            )

        if self.source_sha256 != _sha256_text(
            self.source
        ):
            raise ValueError(
                "source_sha256 does not match source"
            )


def wrap_fpga_physical_output(
    synthesis: FPGASynthesisSource,
) -> FPGAPhysicalSource:
    """
    Add the globally fixed physical output-retention wrapper.

    The accepted synthesis source is preserved byte-for-byte as a prefix.
    No board, package, pin, polarity, expected answer, or physical evidence
    is introduced by this operation.
    """

    if "module cpc_fpga_execution(" not in synthesis.source:
        raise ValueError(
            "synthesis source lacks canonical FPGA execution module"
        )

    if synthesis.source.count(
        "module cpc_fpga_execution("
    ) != 1:
        raise ValueError(
            "synthesis source must contain exactly one canonical "
            "FPGA execution module"
        )

    if "output wire result" not in synthesis.source:
        raise ValueError(
            "synthesis source lacks canonical result output"
        )

    source = (
        synthesis.source.rstrip()
        + "\n"
        + _WRAPPER
    )

    return FPGAPhysicalSource(
        wrapper_id=FPGA_PHYSICAL_WRAPPER_ID,
        synthesis_source_sha256=(
            synthesis.source_sha256
        ),
        top_module=FPGA_PHYSICAL_TOP_MODULE,
        result_port=FPGA_PHYSICAL_RESULT_PORT,
        source=source,
        source_sha256=_sha256_text(
            source
        ),
    )
