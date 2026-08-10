from __future__ import annotations

from dataclasses import dataclass

from src.physical_fpga_profile import (
    PHYSICAL_FPGA_PROFILE_ID,
)


ICEBREAKER_TARGET_ID = "icebreaker-up5k-sg48.v1"


@dataclass(frozen=True)
class IceBreakerTarget:
    """
    Concrete physical-build target for the iCEBreaker iCE40UP5K board.

    This target supplies board- and toolchain-specific build parameters for
    the vendor-neutral RFC-0009 physical FPGA profile.

    It defines a build target only.  It does not assert that a bitstream has
    been built, programmed, executed, or physically observed.
    """

    target_id: str = ICEBREAKER_TARGET_ID
    physical_profile_id: str = PHYSICAL_FPGA_PROFILE_ID

    backend_id: str = "fpga"
    backend_version: str = "1"

    board_family: str = "icebreaker"
    device_family: str = "ice40up5k"
    device_part: str = "up5k-sg48"

    synthesis_tool: str = "yosys"
    place_route_tool: str = "nextpnr-ice40"
    bitstream_tool: str = "icepack"
    programmer: str = "iceprog"

    nextpnr_device: str = "up5k"
    nextpnr_package: str = "sg48"

    bitstream_format: str = "ice40-asc-bin"

    def __post_init__(self) -> None:
        for name, value in (
            ("target_id", self.target_id),
            ("physical_profile_id", self.physical_profile_id),
            ("backend_id", self.backend_id),
            ("backend_version", self.backend_version),
            ("board_family", self.board_family),
            ("device_family", self.device_family),
            ("device_part", self.device_part),
            ("synthesis_tool", self.synthesis_tool),
            ("place_route_tool", self.place_route_tool),
            ("bitstream_tool", self.bitstream_tool),
            ("programmer", self.programmer),
            ("nextpnr_device", self.nextpnr_device),
            ("nextpnr_package", self.nextpnr_package),
            ("bitstream_format", self.bitstream_format),
        ):
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"{name} must be a non-empty string"
                )


ICEBREAKER_TARGET = IceBreakerTarget()
