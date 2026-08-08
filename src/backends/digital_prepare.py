from __future__ import annotations

from typing import Mapping

from src.backend import (
    BackendSpecification,
    ExecutionArtifact,
)
from src.ccir import CCIRProgram
from src.prepared_execution import PreparedExecution


DIGITAL_PREPARATION_ID = "digital.program.v1"


def prepare_digital_execution(
    program: CCIRProgram,
    artifact: ExecutionArtifact,
    boundary_values: Mapping[int, int],
    specification: BackendSpecification,
) -> PreparedExecution:
    """
    Prepare one deterministic digital execution.

    Boundary values enter here, after canonical RFC-0003 compilation.

    This function performs no independent semantic evaluation.
    """

    artifact_metadata = dict(
        artifact.metadata
    )

    if artifact_metadata.get(
        "backend_id"
    ) != specification.backend_id:
        raise ValueError(
            "execution artifact backend does not match "
            "the supplied backend specification"
        )

    if artifact_metadata.get(
        "program_name"
    ) != program.name:
        raise ValueError(
            "execution artifact program does not match CCIR input"
        )

    if dict(
        artifact.parameters
    ) != dict(
        specification.fixed_parameters
    ):
        raise ValueError(
            "execution artifact parameters do not match "
            "the supplied backend specification"
        )

    normalized_boundary = _validate_boundary_values(
        program,
        boundary_values,
    )

    topology = tuple(
        artifact.topology
    )

    payload = (
        (
            "boundary_values",
            tuple(
                sorted(
                    normalized_boundary.items()
                )
            ),
        ),
        (
            "program",
            topology,
        ),
    )

    decoder_specification = (
        (
            "readout_register",
            "result",
        ),
    )

    metadata = (
        (
            "boundary_values",
            tuple(
                sorted(
                    normalized_boundary.items()
                )
            ),
        ),
        (
            "preparation_id",
            DIGITAL_PREPARATION_ID,
        ),
    )

    return PreparedExecution(
        backend_id=specification.backend_id,
        backend_version=specification.backend_version,
        payload=payload,
        interface=tuple(
            artifact.interface
        ),
        decoder_specification=decoder_specification,
        provenance=artifact.provenance,
        metadata=metadata,
    )


def _validate_boundary_values(
    program: CCIRProgram,
    boundary_values: Mapping[int, int],
) -> dict[int, int]:
    required = set(
        program.boundary_variables
    )

    supplied = set(
        boundary_values
    )

    missing = required - supplied
    unexpected = supplied - required

    if missing:
        raise ValueError(
            "missing boundary values for: "
            + ", ".join(
                str(variable)
                for variable in sorted(missing)
            )
        )

    if unexpected:
        raise ValueError(
            "unexpected boundary values for: "
            + ", ".join(
                str(variable)
                for variable in sorted(unexpected)
            )
        )

    normalized = dict(
        boundary_values
    )

    for variable, value in normalized.items():
        if isinstance(
            value,
            bool,
        ) or value not in (
            0,
            1,
        ):
            raise ValueError(
                f"boundary variable {variable} "
                "must be assigned integer 0 or 1"
            )

    return normalized
