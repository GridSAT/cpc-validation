from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ObservableExecution:
    """
    RFC-0004 observable result of substrate execution.

    This object contains only observations admitted by the prepared
    execution interface together with execution metadata.

    It contains no semantic reference result and performs no decoding.
    """

    backend_id: str
    backend_version: str
    observations: tuple[tuple[str, Any], ...]
    provenance: tuple[tuple[str, object], ...] = ()
    metadata: tuple[tuple[str, object], ...] = ()

    def __post_init__(self) -> None:
        if not self.backend_id:
            raise ValueError(
                "observable execution backend_id must be non-empty"
            )

        if not self.backend_version:
            raise ValueError(
                "observable execution backend_version must be non-empty"
            )

        self._validate_pairs(
            self.observations,
            "observation",
        )

        self._validate_pairs(
            self.metadata,
            "metadata",
        )

    @staticmethod
    def _validate_pairs(
        pairs: tuple[tuple[str, object], ...],
        kind: str,
    ) -> None:
        keys = [
            key
            for key, _ in pairs
        ]

        if any(
            not isinstance(key, str) or not key
            for key in keys
        ):
            raise ValueError(
                f"observable execution {kind} keys "
                "must be non-empty strings"
            )

        if len(set(keys)) != len(keys):
            raise ValueError(
                f"observable execution {kind} keys "
                "must be unique"
            )

        if tuple(keys) != tuple(sorted(keys)):
            raise ValueError(
                f"observable execution {kind} keys "
                "must be sorted"
            )
