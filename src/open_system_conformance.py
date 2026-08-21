from __future__ import annotations

import math
from dataclasses import dataclass

from src.open_system_execution import (
    OpenSystemExecutionSpecification,
)


RFC0010_CONFORMANCE_SCHEMA = "cpc.rfc0010-conformance.v1"

RFC0010_REQUIREMENTS = (
    "OS-1",
    "OS-2",
    "OS-3",
    "OS-4",
    "OS-5",
    "OS-6",
    "OS-7",
    "OS-8",
    "DC-1",
    "DC-2",
    "DC-3",
    "DC-4",
    "DC-5",
    "DC-6",
    "RR-1",
    "RR-2",
    "RR-3",
    "RR-4",
    "RR-5",
    "RR-6",
    "RR-7",
    "RR-8",
    "OV-1",
    "OV-2",
    "OV-3",
    "OV-4",
)


def _validate_nonempty_string(
    value: str,
    field_name: str,
) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(
            f"{field_name} must be a non-empty string"
        )


def _validate_pairs(
    pairs: tuple[tuple[str, object], ...],
    field_name: str,
) -> None:
    keys = tuple(
        key
        for key, _ in pairs
    )

    if any(
        not isinstance(key, str) or not key
        for key in keys
    ):
        raise ValueError(
            f"{field_name} keys must be non-empty strings"
        )

    if len(set(keys)) != len(keys):
        raise ValueError(
            f"{field_name} keys must be unique"
        )

    if keys != tuple(sorted(keys)):
        raise ValueError(
            f"{field_name} keys must be sorted"
        )


@dataclass(frozen=True)
class RequirementEvidence:
    """
    Evidence declaration for one RFC-0010 conformance requirement.

    This object records the claimed evidence identity and result. It does not
    independently prove the physical or mathematical claim.
    """

    requirement_id: str
    evidence_id: str
    method: str
    passed: bool

    exact: bool = False

    details: tuple[
        tuple[str, object],
        ...
    ] = ()

    def __post_init__(self) -> None:
        if self.requirement_id not in RFC0010_REQUIREMENTS:
            raise ValueError(
                "unknown RFC-0010 requirement_id"
            )

        _validate_nonempty_string(
            self.evidence_id,
            "evidence_id",
        )

        _validate_nonempty_string(
            self.method,
            "method",
        )

        if not isinstance(self.passed, bool):
            raise ValueError(
                "passed must be a boolean"
            )

        if not isinstance(self.exact, bool):
            raise ValueError(
                "exact must be a boolean"
            )

        _validate_pairs(
            self.details,
            "details",
        )


@dataclass(frozen=True)
class RFC0010ConformanceEvidence:
    """
    Complete declared RFC-0010 conformance evidence for one execution.

    Missing required evidence fails closed.
    """

    execution_specification_hash: str

    requirements: tuple[
        RequirementEvidence,
        ...
    ] = ()

    def __post_init__(self) -> None:
        _validate_nonempty_string(
            self.execution_specification_hash,
            "execution_specification_hash",
        )

        if not self.execution_specification_hash.startswith(
            "sha256:"
        ):
            raise ValueError(
                "execution_specification_hash must be a sha256 digest"
            )

        digest = self.execution_specification_hash[
            len("sha256:"):
        ]

        if (
            len(digest) != 64
            or any(
                character
                not in "0123456789abcdef"
                for character in digest
            )
        ):
            raise ValueError(
                "execution_specification_hash must be "
                "a lowercase sha256 digest"
            )

        if any(
            not isinstance(
                item,
                RequirementEvidence,
            )
            for item in self.requirements
        ):
            raise ValueError(
                "requirements must contain "
                "RequirementEvidence values"
            )

        ids = tuple(
            item.requirement_id
            for item in self.requirements
        )

        if len(set(ids)) != len(ids):
            raise ValueError(
                "requirement evidence IDs must be unique"
            )

        if ids != tuple(sorted(ids)):
            raise ValueError(
                "requirement evidence must be sorted "
                "by requirement_id"
            )


@dataclass(frozen=True)
class ConformanceFailure:
    requirement_id: str
    reason: str

    def __post_init__(self) -> None:
        _validate_nonempty_string(
            self.requirement_id,
            "requirement_id",
        )

        _validate_nonempty_string(
            self.reason,
            "reason",
        )


@dataclass(frozen=True)
class RFC0010ConformanceReport:
    """
    Fail-closed conformance result.

    `conformant` is true only when every required condition for every claimed
    group has explicit passing evidence and all structural cross-checks pass.
    """

    conformant: bool
    required_requirements: tuple[str, ...]
    failures: tuple[ConformanceFailure, ...]

    @property
    def schema(self) -> str:
        return RFC0010_CONFORMANCE_SCHEMA


def _requirements_for_groups(
    groups: tuple[str, ...],
) -> tuple[str, ...]:
    required: list[str] = []

    for group in groups:
        required.extend(
            requirement
            for requirement in RFC0010_REQUIREMENTS
            if requirement.startswith(
                f"{group}-"
            )
        )

    return tuple(sorted(required))


def _evidence_map(
    evidence: RFC0010ConformanceEvidence,
) -> dict[str, RequirementEvidence]:
    return {
        item.requirement_id: item
        for item in evidence.requirements
    }


def _append_failure(
    failures: list[ConformanceFailure],
    requirement_id: str,
    reason: str,
) -> None:
    failures.append(
        ConformanceFailure(
            requirement_id=requirement_id,
            reason=reason,
        )
    )


def validate_rfc0010_conformance(
    *,
    specification: OpenSystemExecutionSpecification,
    evidence: RFC0010ConformanceEvidence,
) -> RFC0010ConformanceReport:
    """
    Validate RFC-0010 conformance declarations against one execution model.

    The validator checks structural consistency and explicit evidence
    completeness. It does not independently prove externally supplied
    mathematical or physical evidence.
    """

    failures: list[ConformanceFailure] = []

    if (
        evidence.execution_specification_hash
        != specification.specification_hash
    ):
        _append_failure(
            failures,
            "OV-3",
            "conformance evidence is not bound to "
            "the supplied execution specification",
        )

    required = _requirements_for_groups(
        specification.conformance_groups
    )

    declared = _evidence_map(
        evidence
    )

    for requirement_id in required:
        item = declared.get(
            requirement_id
        )

        if item is None:
            _append_failure(
                failures,
                requirement_id,
                "required evidence is missing",
            )
            continue

        if not item.passed:
            _append_failure(
                failures,
                requirement_id,
                "declared evidence does not pass",
            )

    _validate_structural_requirements(
        specification=specification,
        required=required,
        failures=failures,
    )

    failures_tuple = tuple(
        sorted(
            failures,
            key=lambda failure: (
                failure.requirement_id,
                failure.reason,
            ),
        )
    )

    return RFC0010ConformanceReport(
        conformant=not failures_tuple,
        required_requirements=required,
        failures=failures_tuple,
    )


def _validate_structural_requirements(
    *,
    specification: OpenSystemExecutionSpecification,
    required: tuple[str, ...],
    failures: list[ConformanceFailure],
) -> None:
    required_set = set(
        required
    )

    if "DC-3" in required_set:
        if specification.convergence is None:
            _append_failure(
                failures,
                "DC-3",
                "penalty-Lyapunov claim requires "
                "a convergence specification",
            )

    if "DC-4" in required_set:
        convergence = specification.convergence

        if convergence is None:
            _append_failure(
                failures,
                "DC-4",
                "convergence-rate claim requires "
                "a convergence specification",
            )
        elif (
            not math.isfinite(convergence.gamma)
            or convergence.gamma <= 0
        ):
            _append_failure(
                failures,
                "DC-4",
                "convergence rate must be finite "
                "and positive",
            )

    if "DC-2" in required_set:
        convergence = specification.convergence

        if (
            convergence is None
            or convergence.positive_penalty_scale
            is None
        ):
            _append_failure(
                failures,
                "DC-2",
                "positive penalty-scale claim requires "
                "positive_penalty_scale",
            )

    if "DC-6" in required_set:
        if not specification.resource_accounting:
            _append_failure(
                failures,
                "DC-6",
                "runtime/resource claim requires "
                "resource_accounting",
            )

    rr_required = any(
        requirement.startswith("RR-")
        for requirement in required_set
    )

    if rr_required and specification.readout is None:
        _append_failure(
            failures,
            "RR-4",
            "referenced-readout conformance requires "
            "a readout specification",
        )

    if "RR-1" in required_set:
        if specification.external_reference is None:
            _append_failure(
                failures,
                "RR-1",
                "claimed referenced readout requires "
                "an external reference",
            )

    if "RR-2" in required_set:
        reference = specification.external_reference

        if reference is None:
            _append_failure(
                failures,
                "RR-2",
                "reference calibration requires "
                "an external reference",
            )
        elif not reference.calibration_id:
            _append_failure(
                failures,
                "RR-2",
                "external reference has no "
                "calibration identity",
            )

    if "RR-3" in required_set:
        readout = specification.readout

        if (
            readout is None
            or not readout.calibration_neighborhood
        ):
            _append_failure(
                failures,
                "RR-3",
                "robust referenced readout requires "
                "a calibration neighborhood",
            )

    if "RR-5" in required_set:
        readout = specification.readout

        if (
            readout is None
            or not readout.decision_regions
        ):
            _append_failure(
                failures,
                "RR-5",
                "decoder conformance requires "
                "declared decision regions",
            )

    if "RR-6" in required_set:
        readout = specification.readout

        if (
            readout is None
            or not readout.decoder_id
        ):
            _append_failure(
                failures,
                "RR-6",
                "fixed-decoder conformance requires "
                "a decoder identity",
            )

    if "RR-7" in required_set:
        readout = specification.readout

        if (
            readout is None
            or readout.decision_margin is None
        ):
            _append_failure(
                failures,
                "RR-7",
                "robust-separation claim requires "
                "a decision margin",
            )

    if "RR-8" in required_set:
        readout = specification.readout

        if (
            readout is None
            or readout.declared_error_bound is None
        ):
            _append_failure(
                failures,
                "RR-8",
                "measurement-error claim requires "
                "a declared error bound",
            )

    if (
        "RR-7" in required_set
        or "RR-8" in required_set
    ):
        readout = specification.readout

        if (
            readout is not None
            and readout.declared_error_bound is not None
            and readout.decision_margin is not None
            and readout.declared_error_bound
            >= readout.decision_margin
        ):
            _append_failure(
                failures,
                "RR-7",
                "declared error bound must be strictly "
                "smaller than the decision margin",
            )

    if "OV-4" in required_set:
        if specification.realization_status not in (
            "abstract",
            "simulated",
            "physical_approximate",
            "physical_exact",
        ):
            _append_failure(
                failures,
                "OV-4",
                "realization status is not explicit",
            )
