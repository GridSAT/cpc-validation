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


@dataclass(frozen=True)
class BackendCapabilities:
    """
    Declared RFC-0003 capability domain for one backend.
    """

    constraint_families: frozenset[str]
    interface_features: frozenset[str] = frozenset()
    execution_features: frozenset[str] = frozenset()
    artifact_features: frozenset[str] = frozenset()

    def supports_constraint_family(
        self,
        family: str,
    ) -> bool:
        return family in self.constraint_families


class UnsupportedBackendCapabilityError(
    ValueError
):
    """
    Raised when CCIR requires a capability not admitted by the backend.
    """


class Backend(Protocol):
    """
    Canonical RFC-0003 backend compilation interface.
    """

    @property
    def capabilities(
        self,
    ) -> BackendCapabilities:
        ...

    def compile(
        self,
        program: CCIRProgram,
    ) -> ExecutionArtifact:
        ...
