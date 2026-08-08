from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.ccir import CCIRPayload


PARITY_CONSTRAINT_FAMILY = "parity"


@dataclass(frozen=True)
class CCIRParityPayload(CCIRPayload):
    """
    Typed CCIR payload for one Boolean parity constraint.

    The constraint is satisfied exactly when the XOR of ``variables``
    equals ``parity``.
    """

    variables: tuple[int, ...]
    parity: int

    def __post_init__(self) -> None:
        if not self.variables:
            raise ValueError(
                "CCIR parity payload must contain at least one variable"
            )

        if any(
            isinstance(variable, bool)
            or not isinstance(variable, int)
            for variable in self.variables
        ):
            raise ValueError(
                "CCIR parity variables must be integers"
            )

        if any(
            variable < 0
            for variable in self.variables
        ):
            raise ValueError(
                "CCIR parity variables must be non-negative"
            )

        if len(set(self.variables)) != len(self.variables):
            raise ValueError(
                "CCIR parity variables must be unique"
            )

        if tuple(sorted(self.variables)) != self.variables:
            raise ValueError(
                "CCIR parity variables must be sorted"
            )

        if isinstance(self.parity, bool) or self.parity not in (0, 1):
            raise ValueError(
                "CCIR parity value must be integer 0 or 1"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "variables": list(self.variables),
            "parity": self.parity,
        }
