from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PreparedExecution:
    """
    RFC-0004 prepared execution state.

    A PreparedExecution is produced after backend compilation and before
    substrate execution. It contains only information admitted by the
    execution artifact, backend specification, and preparation inputs.

    It must not contain independently computed semantic reference results.
    """

    backend_id: str
    backend_version: str
    payload: Any
    interface: Any
    decoder_specification: Any
    metadata: tuple[tuple[str, object], ...] = ()

    def __post_init__(self) -> None:
        if not self.backend_id:
            raise ValueError(
                "prepared execution backend_id must be non-empty"
            )

        if not self.backend_version:
            raise ValueError(
                "prepared execution backend_version must be non-empty"
            )

        keys = [
            key
            for key, _ in self.metadata
        ]

        if any(
            not isinstance(key, str) or not key
            for key in keys
        ):
            raise ValueError(
                "prepared execution metadata keys must be non-empty strings"
            )

        if len(set(keys)) != len(keys):
            raise ValueError(
                "prepared execution metadata keys must be unique"
            )

        if tuple(keys) != tuple(sorted(keys)):
            raise ValueError(
                "prepared execution metadata keys must be sorted"
            )
