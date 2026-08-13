from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from src.physical_fpga_output_wrapper import (
    FPGA_PHYSICAL_RESULT_PORT,
)
from src.physical_lattice_up5k_breakout_target import (
    LATTICE_UP5K_BREAKOUT_TARGET_ID,
)


LATTICE_UP5K_P1_CONSTRAINT_ID = (
    "lattice-ice40up5k-b-evn-p1-red-led.v1"
)

LATTICE_UP5K_P1_PCF_PATH = Path(
    "physical/lattice_up5k_breakout/p1.pcf"
)

LATTICE_UP5K_P1_BOARD_NET = "LED_RED"
LATTICE_UP5K_P1_PACKAGE_PIN = "41"

LATTICE_UP5K_P1_SOURCE_DOCUMENT = (
    "FPGA-UG-02001"
)

LATTICE_UP5K_P1_SOURCE_DOCUMENT_VERSION = "1.2"

LATTICE_UP5K_P1_SOURCE_FIGURE = (
    "Figure A.3 DUT Connection"
)


def _sha256_bytes(content: bytes) -> str:
    digest = hashlib.sha256(
        content
    ).hexdigest()

    return f"sha256:{digest}"


@dataclass(frozen=True)
class LatticeUP5KBreakoutConstraint:
    """
    Board-specific physical-output binding for CPC P1.

    The constraint binds the board-neutral physical result port to the
    manufacturer-defined LED_RED net and its SG48 package pin.

    It introduces no semantic transformation, expected result, programming
    record, execution record, or physical observation.
    """

    constraint_id: str = (
        LATTICE_UP5K_P1_CONSTRAINT_ID
    )

    target_id: str = (
        LATTICE_UP5K_BREAKOUT_TARGET_ID
    )

    logical_port: str = (
        FPGA_PHYSICAL_RESULT_PORT
    )

    board_net: str = (
        LATTICE_UP5K_P1_BOARD_NET
    )

    package_pin: str = (
        LATTICE_UP5K_P1_PACKAGE_PIN
    )

    source_document: str = (
        LATTICE_UP5K_P1_SOURCE_DOCUMENT
    )

    source_document_version: str = (
        LATTICE_UP5K_P1_SOURCE_DOCUMENT_VERSION
    )

    source_figure: str = (
        LATTICE_UP5K_P1_SOURCE_FIGURE
    )

    def __post_init__(self) -> None:
        for name, value in (
            ("constraint_id", self.constraint_id),
            ("target_id", self.target_id),
            ("logical_port", self.logical_port),
            ("board_net", self.board_net),
            ("package_pin", self.package_pin),
            (
                "source_document",
                self.source_document,
            ),
            (
                "source_document_version",
                self.source_document_version,
            ),
            (
                "source_figure",
                self.source_figure,
            ),
        ):
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"{name} must be a non-empty string"
                )

    @property
    def pcf_text(self) -> str:
        return (
            f"set_io {self.logical_port} "
            f"{self.package_pin}\n"
        )

    @property
    def pcf_sha256(self) -> str:
        return _sha256_bytes(
            self.pcf_text.encode(
                "utf-8"
            )
        )


LATTICE_UP5K_P1_CONSTRAINT = (
    LatticeUP5KBreakoutConstraint()
)
