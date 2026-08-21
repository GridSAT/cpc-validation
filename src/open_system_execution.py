from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Mapping


OPEN_SYSTEM_EXECUTION_SCHEMA = "cpc.open-system-execution.v1"

REALIZATION_STATUSES = (
    "abstract",
    "simulated",
    "physical_approximate",
    "physical_exact",
)

CONFORMANCE_GROUPS = (
    "OS",
    "DC",
    "RR",
    "OV",
)


def _validate_nonempty_string(
    value: str,
    field_name: str,
) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(
            f"{field_name} must be a non-empty string"
        )


def _validate_sha256(
    value: str,
    field_name: str,
) -> None:
    prefix = "sha256:"

    if (
        not isinstance(value, str)
        or not value.startswith(prefix)
    ):
        raise ValueError(
            f"{field_name} must be a sha256 digest"
        )

    digest = value[len(prefix):]

    if len(digest) != 64:
        raise ValueError(
            f"{field_name} must be a sha256 digest"
        )

    if any(
        character not in "0123456789abcdef"
        for character in digest
    ):
        raise ValueError(
            f"{field_name} must be a lowercase sha256 digest"
        )


def _validate_pairs(
    pairs: tuple[tuple[str, object], ...],
    field_name: str,
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
            f"{field_name} keys must be non-empty strings"
        )

    if len(set(keys)) != len(keys):
        raise ValueError(
            f"{field_name} keys must be unique"
        )

    if tuple(keys) != tuple(sorted(keys)):
        raise ValueError(
            f"{field_name} keys must be sorted"
        )


def _pairs_dict(
    pairs: tuple[tuple[str, object], ...],
) -> dict[str, object]:
    return {
        key: value
        for key, value in pairs
    }


def _canonical_json(
    value: Mapping[str, object],
) -> str:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    )


def _sha256_text(text: str) -> str:
    digest = hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()

    return f"sha256:{digest}"


@dataclass(frozen=True)
class ExternalReferenceSpecification:
    """
    RFC-0010 operational-reference identity and calibration declaration.

    The object contains reference and calibration metadata only. It must not
    contain independently computed semantic answers or answer-dependent
    decoder tuning.
    """

    reference_id: str
    reference_type: str
    calibration_id: str
    instrumentation_id: str

    nominal_parameters: tuple[
        tuple[str, object],
        ...
    ] = ()

    calibration_parameters: tuple[
        tuple[str, object],
        ...
    ] = ()

    drift_region: tuple[
        tuple[str, object],
        ...
    ] = ()

    provenance: tuple[
        tuple[str, object],
        ...
    ] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("reference_id", self.reference_id),
            ("reference_type", self.reference_type),
            ("calibration_id", self.calibration_id),
            (
                "instrumentation_id",
                self.instrumentation_id,
            ),
        ):
            _validate_nonempty_string(
                value,
                name,
            )

        for name, value in (
            (
                "nominal_parameters",
                self.nominal_parameters,
            ),
            (
                "calibration_parameters",
                self.calibration_parameters,
            ),
            (
                "drift_region",
                self.drift_region,
            ),
            (
                "provenance",
                self.provenance,
            ),
        ):
            _validate_pairs(
                value,
                name,
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "reference_id": self.reference_id,
            "reference_type": self.reference_type,
            "calibration_id": self.calibration_id,
            "instrumentation_id": (
                self.instrumentation_id
            ),
            "nominal_parameters": _pairs_dict(
                self.nominal_parameters
            ),
            "calibration_parameters": _pairs_dict(
                self.calibration_parameters
            ),
            "drift_region": _pairs_dict(
                self.drift_region
            ),
            "provenance": _pairs_dict(
                self.provenance
            ),
        }


@dataclass(frozen=True)
class ConvergenceSpecification:
    """
    RFC-0010 declared convergence evidence for one open-system execution.

    gamma is a declared Lyapunov or convergence rate. This type deliberately
    does not identify gamma with a Liouvillian spectral gap.
    """

    method: str
    penalty_id: str
    admitted_state_domain_id: str
    gamma: float

    positive_penalty_scale: float | None = None

    tolerances: tuple[
        tuple[str, object],
        ...
    ] = ()

    metadata: tuple[
        tuple[str, object],
        ...
    ] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("method", self.method),
            ("penalty_id", self.penalty_id),
            (
                "admitted_state_domain_id",
                self.admitted_state_domain_id,
            ),
        ):
            _validate_nonempty_string(
                value,
                name,
            )

        if (
            not isinstance(self.gamma, (int, float))
            or isinstance(self.gamma, bool)
            or not math.isfinite(self.gamma)
            or self.gamma <= 0
        ):
            raise ValueError(
                "gamma must be a finite positive number"
            )

        if self.positive_penalty_scale is not None:
            value = self.positive_penalty_scale

            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(value)
                or value <= 0
            ):
                raise ValueError(
                    "positive_penalty_scale must be "
                    "a finite positive number"
                )

        _validate_pairs(
            self.tolerances,
            "tolerances",
        )

        _validate_pairs(
            self.metadata,
            "metadata",
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "method": self.method,
            "penalty_id": self.penalty_id,
            "admitted_state_domain_id": (
                self.admitted_state_domain_id
            ),
            "gamma": self.gamma,
            "positive_penalty_scale": (
                self.positive_penalty_scale
            ),
            "tolerances": _pairs_dict(
                self.tolerances
            ),
            "metadata": _pairs_dict(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class ReferencedReadoutSpecification:
    """
    RFC-0010 admitted physical measurement and fixed decoder declaration.
    """

    measurement_model_id: str
    decoder_id: str

    reference_id: str | None = None

    decision_regions: tuple[
        tuple[str, object],
        ...
    ] = ()

    calibration_neighborhood: tuple[
        tuple[str, object],
        ...
    ] = ()

    declared_error_bound: float | None = None
    decision_margin: float | None = None

    metadata: tuple[
        tuple[str, object],
        ...
    ] = ()

    def __post_init__(self) -> None:
        _validate_nonempty_string(
            self.measurement_model_id,
            "measurement_model_id",
        )

        _validate_nonempty_string(
            self.decoder_id,
            "decoder_id",
        )

        if self.reference_id is not None:
            _validate_nonempty_string(
                self.reference_id,
                "reference_id",
            )

        for name, value in (
            (
                "decision_regions",
                self.decision_regions,
            ),
            (
                "calibration_neighborhood",
                self.calibration_neighborhood,
            ),
            (
                "metadata",
                self.metadata,
            ),
        ):
            _validate_pairs(
                value,
                name,
            )

        if self.declared_error_bound is not None:
            value = self.declared_error_bound

            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(value)
                or value < 0
            ):
                raise ValueError(
                    "declared_error_bound must be "
                    "a finite non-negative number"
                )

        if self.decision_margin is not None:
            value = self.decision_margin

            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(value)
                or value <= 0
            ):
                raise ValueError(
                    "decision_margin must be "
                    "a finite positive number"
                )

    def to_dict(self) -> dict[str, object]:
        return {
            "measurement_model_id": (
                self.measurement_model_id
            ),
            "decoder_id": self.decoder_id,
            "reference_id": self.reference_id,
            "decision_regions": _pairs_dict(
                self.decision_regions
            ),
            "calibration_neighborhood": _pairs_dict(
                self.calibration_neighborhood
            ),
            "declared_error_bound": (
                self.declared_error_bound
            ),
            "decision_margin": self.decision_margin,
            "metadata": _pairs_dict(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class OpenSystemExecutionSpecification:
    """
    Canonical RFC-0010 execution specification.

    This type records declared architecture and evidence identities. It does
    not itself establish fixed-point correctness, convergence, physical
    authenticity, or semantic correctness.
    """

    instance_id: str
    prepared_execution_hash: str

    physical_state_space_id: str
    protected_manifold_id: str

    stabilization_generator_hash: str
    problem_generator_hash: str

    semantic_terminal_sector_id: str

    realization_status: str

    boundary_control: tuple[
        tuple[str, object],
        ...
    ] = ()

    conformance_groups: tuple[str, ...] = ()

    external_reference: (
        ExternalReferenceSpecification | None
    ) = None

    convergence: (
        ConvergenceSpecification | None
    ) = None

    readout: (
        ReferencedReadoutSpecification | None
    ) = None

    resource_accounting: tuple[
        tuple[str, object],
        ...
    ] = ()

    metadata: tuple[
        tuple[str, object],
        ...
    ] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("instance_id", self.instance_id),
            (
                "physical_state_space_id",
                self.physical_state_space_id,
            ),
            (
                "protected_manifold_id",
                self.protected_manifold_id,
            ),
            (
                "semantic_terminal_sector_id",
                self.semantic_terminal_sector_id,
            ),
        ):
            _validate_nonempty_string(
                value,
                name,
            )

        for name, value in (
            (
                "prepared_execution_hash",
                self.prepared_execution_hash,
            ),
            (
                "stabilization_generator_hash",
                self.stabilization_generator_hash,
            ),
            (
                "problem_generator_hash",
                self.problem_generator_hash,
            ),
        ):
            _validate_sha256(
                value,
                name,
            )

        if self.realization_status not in (
            REALIZATION_STATUSES
        ):
            raise ValueError(
                "realization_status must be one of: "
                + ", ".join(REALIZATION_STATUSES)
            )

        if any(
            group not in CONFORMANCE_GROUPS
            for group in self.conformance_groups
        ):
            raise ValueError(
                "conformance_groups contains "
                "an unknown RFC-0010 group"
            )

        if len(set(self.conformance_groups)) != len(
            self.conformance_groups
        ):
            raise ValueError(
                "conformance_groups must be unique"
            )

        if self.conformance_groups != tuple(
            sorted(self.conformance_groups)
        ):
            raise ValueError(
                "conformance_groups must be sorted"
            )

        for name, value in (
            (
                "boundary_control",
                self.boundary_control,
            ),
            (
                "resource_accounting",
                self.resource_accounting,
            ),
            (
                "metadata",
                self.metadata,
            ),
        ):
            _validate_pairs(
                value,
                name,
            )

        if (
            self.external_reference is not None
            and not isinstance(
                self.external_reference,
                ExternalReferenceSpecification,
            )
        ):
            raise ValueError(
                "external_reference must be an "
                "ExternalReferenceSpecification"
            )

        if (
            self.convergence is not None
            and not isinstance(
                self.convergence,
                ConvergenceSpecification,
            )
        ):
            raise ValueError(
                "convergence must be a "
                "ConvergenceSpecification"
            )

        if (
            self.readout is not None
            and not isinstance(
                self.readout,
                ReferencedReadoutSpecification,
            )
        ):
            raise ValueError(
                "readout must be a "
                "ReferencedReadoutSpecification"
            )

        if (
            self.external_reference is not None
            and self.readout is not None
            and self.readout.reference_id is not None
            and self.readout.reference_id
            != self.external_reference.reference_id
        ):
            raise ValueError(
                "readout reference_id does not match "
                "external reference identity"
            )

    @property
    def schema(self) -> str:
        return OPEN_SYSTEM_EXECUTION_SCHEMA

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "instance_id": self.instance_id,
            "prepared_execution_hash": (
                self.prepared_execution_hash
            ),
            "boundary_control": _pairs_dict(
                self.boundary_control
            ),
            "physical_state_space_id": (
                self.physical_state_space_id
            ),
            "protected_manifold_id": (
                self.protected_manifold_id
            ),
            "stabilization_generator_hash": (
                self.stabilization_generator_hash
            ),
            "problem_generator_hash": (
                self.problem_generator_hash
            ),
            "semantic_terminal_sector_id": (
                self.semantic_terminal_sector_id
            ),
            "realization_status": (
                self.realization_status
            ),
            "conformance_groups": list(
                self.conformance_groups
            ),
            "external_reference": (
                None
                if self.external_reference is None
                else self.external_reference.to_dict()
            ),
            "convergence": (
                None
                if self.convergence is None
                else self.convergence.to_dict()
            ),
            "readout": (
                None
                if self.readout is None
                else self.readout.to_dict()
            ),
            "resource_accounting": _pairs_dict(
                self.resource_accounting
            ),
            "metadata": _pairs_dict(
                self.metadata
            ),
        }

    def canonical_json(self) -> str:
        return _canonical_json(
            self.to_dict()
        )

    @property
    def specification_hash(self) -> str:
        return _sha256_text(
            self.canonical_json()
        )
