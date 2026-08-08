from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from src.ccir import CCIRProgram


@dataclass(frozen=True)
class ArtifactProvenance:
    """
    Machine-resolvable provenance for one generated artifact element.

    At least one of ccir_origin or backend_rule must be present.
    """

    ccir_origin: str | None = None
    backend_rule: str | None = None

    def __post_init__(self) -> None:
        if self.ccir_origin is None and self.backend_rule is None:
            raise ValueError(
                "artifact provenance requires a CCIR origin "
                "or backend rule"
            )


@dataclass(frozen=True)
class ExecutionArtifact:
    """
    Canonical backend execution artifact contract.

    Backend-specific realizations may specialize the contents of these
    fields while preserving the RFC-0003 artifact boundary.
    """

    topology: Any
    parameters: Any
    interface: Any
    metadata: Any
    provenance: tuple[
        tuple[str, ArtifactProvenance],
        ...,
    ]


class Backend(Protocol):
    """
    Canonical RFC-0003 backend compilation interface.
    """

    def compile(
        self,
        program: CCIRProgram,
    ) -> ExecutionArtifact:
        ...
