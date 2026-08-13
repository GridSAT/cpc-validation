from __future__ import annotations

from dataclasses import dataclass

from src.physical_fpga_profile import (
    PHYSICAL_FPGA_PROFILE_ID,
)


LATTICE_UP5K_BREAKOUT_TARGET_ID = (
    "lattice-ice40up5k-b-evn-sg48.v1"
)


@dataclass(frozen=True)
class LatticeUP5KBreakoutTarget:
    """
    Physical-build target for the Lattice iCE40 UltraPlus Breakout Board.

    This target records only board, FPGA, package, and open-toolchain build
    identity established independently of any physical pin assignment.

    It does not assert a constraint-file identity, programming method,
    bitstream, device programming event, physical execution, or observation.
    """

    target_id: str = LATTICE_UP5K_BREAKOUT_TARGET_ID
    physical_profile_id: str = PHYSICAL_FPGA_PROFILE_ID

    backend_id: str = "fpga"
    backend_version: str = "1"

    manufacturer: str = "Lattice Semiconductor"
    board_name: str = "iCE40 UltraPlus Breakout Board"
    ordering_part_number: str = "iCE40UP5K-B-EVN"

    device_family: str = "ice40up5k"
    device_part: str = "iCE40UP5K"
    package: str = "sg48"

    synthesis_tool: str = "yosys"
    place_route_tool: str = "nextpnr-ice40"
    bitstream_tool: str = "icepack"

    nextpnr_device: str = "up5k"
    nextpnr_package: str = "sg48"

    bitstream_format: str = "ice40-asc-bin"

    def __post_init__(self) -> None:
        for name, value in (
            ("target_id", self.target_id),
            ("physical_profile_id", self.physical_profile_id),
            ("backend_id", self.backend_id),
            ("backend_version", self.backend_version),
            ("manufacturer", self.manufacturer),
            ("board_name", self.board_name),
            (
                "ordering_part_number",
                self.ordering_part_number,
            ),
            ("device_family", self.device_family),
            ("device_part", self.device_part),
            ("package", self.package),
            ("synthesis_tool", self.synthesis_tool),
            ("place_route_tool", self.place_route_tool),
            ("bitstream_tool", self.bitstream_tool),
            ("nextpnr_device", self.nextpnr_device),
            ("nextpnr_package", self.nextpnr_package),
            ("bitstream_format", self.bitstream_format),
        ):
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"{name} must be a non-empty string"
                )


LATTICE_UP5K_BREAKOUT_TARGET = (
    LatticeUP5KBreakoutTarget()
)
