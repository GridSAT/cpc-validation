from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Protocol

from src.ccir import CCIRProgram


@dataclass(frozen=True, order=True)
class CCIROrigin:
    """
    Machine-resolvable reference to admitted CCIR data.
    """

    kind: str
    identifier: str

    def __post_init__(self) -> None:
        if not self.kind:
            raise ValueError(
                "CCIR origin kind must be non-empty"
            )

        if not self.identifier:
            raise ValueError(
                "CCIR origin identifier must be non-empty"
            )


@dataclass(frozen=True, order=True)
class BackendRuleOrigin:
    """
    Machine-resolvable reference to a globally fixed backend rule.
    """

    rule_id: str

    def __post_init__(self) -> None:
        if not self.rule_id:
            raise ValueError(
                "backend rule identifier must be non-empty"
            )


@dataclass(frozen=True)
class ArtifactProvenance:
    """
    Machine-resolvable provenance for one generated artifact element.

    At least one CCIR origin or backend-rule origin must be present.
    """

    ccir_origins: tuple[CCIROrigin, ...] = ()
    backend_rules: tuple[BackendRuleOrigin, ...] = ()

    def __post_init__(self) -> None:
        if not self.ccir_origins and not self.backend_rules:
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


def validate_artifact_backend_rules(
    artifact: ExecutionArtifact,
    specification: BackendSpecification,
) -> None:
    """
    Verify that every provenance backend rule is registered in Theta_backend.
    """

    unknown_rules = sorted(
        {
            rule.rule_id
            for _, provenance in artifact.provenance
            for rule in provenance.backend_rules
            if not specification.has_rule(
                rule.rule_id
            )
        }
    )

    if unknown_rules:
        raise ValueError(
            "artifact provenance references unregistered backend rules: "
            + ", ".join(unknown_rules)
        )


def validate_artifact_provenance(
    artifact: ExecutionArtifact,
    required_elements: Iterable[str],
) -> None:
    """
    Verify exact provenance coverage for generated artifact elements.

    The backend supplies the complete machine-resolvable element inventory.
    RFC-0003 requires one provenance entry for every generated element and
    forbids provenance entries for elements outside that inventory.
    """

    required = tuple(required_elements)

    if any(
        not isinstance(element, str) or not element
        for element in required
    ):
        raise ValueError(
            "artifact element identifiers must be non-empty strings"
        )

    if len(set(required)) != len(required):
        raise ValueError(
            "artifact element inventory contains duplicate identifiers"
        )

    provenance_elements = tuple(
        element
        for element, provenance in artifact.provenance
    )

    if any(
        not isinstance(element, str) or not element
        for element in provenance_elements
    ):
        raise ValueError(
            "provenance element identifiers must be non-empty strings"
        )

    if len(set(provenance_elements)) != len(provenance_elements):
        raise ValueError(
            "artifact provenance contains duplicate element identifiers"
        )

    if any(
        not isinstance(provenance, ArtifactProvenance)
        for _, provenance in artifact.provenance
    ):
        raise ValueError(
            "artifact provenance entries must be ArtifactProvenance"
        )

    required_set = set(required)
    provenance_set = set(provenance_elements)

    missing = sorted(
        required_set - provenance_set
    )

    unexpected = sorted(
        provenance_set - required_set
    )

    if missing:
        raise ValueError(
            "artifact provenance missing elements: "
            + ", ".join(missing)
        )

    if unexpected:
        raise ValueError(
            "artifact provenance contains unknown elements: "
            + ", ".join(unexpected)
        )


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


@dataclass(frozen=True, order=True)
class BackendRuleDefinition:
    """
    One globally fixed rule admitted by Theta_backend.
    """

    rule_id: str

    def __post_init__(self) -> None:
        if not self.rule_id:
            raise ValueError(
                "backend rule identifier must be non-empty"
            )


@dataclass(frozen=True)
class BackendSpecification:
    """
    Machine-visible representation of Theta_backend.

    Every quantity capable of influencing compilation outside CCIR must
    be fixed here before compilation begins.
    """

    backend_id: str
    backend_version: str
    capabilities: BackendCapabilities
    rules: tuple[BackendRuleDefinition, ...] = ()
    fixed_parameters: tuple[
        tuple[str, object],
        ...,
    ] = ()

    def __post_init__(self) -> None:
        if not self.backend_id:
            raise ValueError(
                "backend identifier must be non-empty"
            )

        if not self.backend_version:
            raise ValueError(
                "backend version must be non-empty"
            )

        rule_ids = tuple(
            rule.rule_id
            for rule in self.rules
        )

        if len(set(rule_ids)) != len(rule_ids):
            raise ValueError(
                "backend rule identifiers must be unique"
            )

        parameter_names = tuple(
            name
            for name, value in self.fixed_parameters
        )

        if any(
            not isinstance(name, str) or not name
            for name in parameter_names
        ):
            raise ValueError(
                "backend parameter names must be non-empty strings"
            )

        if len(set(parameter_names)) != len(parameter_names):
            raise ValueError(
                "backend parameter names must be unique"
            )

    def has_rule(
        self,
        rule_id: str,
    ) -> bool:
        return any(
            rule.rule_id == rule_id
            for rule in self.rules
        )

    def get_fixed_parameter(
        self,
        name: str,
    ) -> object:
        for parameter_name, value in self.fixed_parameters:
            if parameter_name == name:
                return value

        raise KeyError(name)


class UnsupportedBackendCapabilityError(
    ValueError
):
    """
    Raised when CCIR requires a capability not admitted by the backend.
    """


def validate_backend_capabilities(
    program: CCIRProgram,
    capabilities: BackendCapabilities,
) -> None:
    """
    Reject CCIR programs requiring unsupported backend capabilities.
    """

    unsupported_families = sorted(
        {
            constraint.family
            for constraint in program.constraints
            if not capabilities.supports_constraint_family(
                constraint.family
            )
        }
    )

    if unsupported_families:
        raise UnsupportedBackendCapabilityError(
            "unsupported CCIR constraint families: "
            + ", ".join(unsupported_families)
        )


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
