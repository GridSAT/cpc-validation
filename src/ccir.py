from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping


CCIR_SCHEMA_VERSION = 1


class CCIRPayload(ABC):
    """
    Base contract for one immutable typed constraint-family payload.
    """

    @abstractmethod
    def to_dict(self) -> Mapping[str, Any]:
        """Return a deterministic serializable representation."""
        raise NotImplementedError


@dataclass(frozen=True)
class CCIRConstraint:
    """
    One typed CCIR constraint container.

    Constraint-family payload types are introduced separately.
    This container records only the family identifier and immutable payload.
    """

    family: str
    payload: CCIRPayload

    def __post_init__(self) -> None:
        if not isinstance(self.family, str):
            raise ValueError(
                "CCIR constraint family must be a string"
            )

        if not self.family.strip():
            raise ValueError(
                "CCIR constraint family may not be empty"
            )

        if not isinstance(self.payload, CCIRPayload):
            raise ValueError(
                "CCIR constraint payload must implement CCIRPayload"
            )


@dataclass(frozen=True)
class CCIRProgram:
    """
    Canonical backend-independent constraint program.

    This initial container defines program identity, declared variables,
    optional variable roles, and typed constraints. It performs no lowering,
    semantic evaluation, optimization, backend compilation, or emission.
    """

    name: str
    variable_count: int
    boundary_variables: tuple[int, ...]
    constraints: tuple[CCIRConstraint, ...]
    metadata: tuple[tuple[str, object], ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise ValueError(
                "CCIR program name must be a string"
            )

        if not self.name.strip():
            raise ValueError(
                "CCIR program name may not be empty"
            )

        if isinstance(self.variable_count, bool) or not isinstance(
            self.variable_count,
            int,
        ):
            raise ValueError(
                "CCIR variable_count must be an integer"
            )

        if self.variable_count < 0:
            raise ValueError(
                "CCIR variable_count must be non-negative"
            )

        if any(
            isinstance(variable, bool)
            or not isinstance(variable, int)
            for variable in self.boundary_variables
        ):
            raise ValueError(
                "CCIR boundary variables must be integers"
            )

        if any(
            variable < 0
            or variable >= self.variable_count
            for variable in self.boundary_variables
        ):
            raise ValueError(
                "CCIR boundary variable lies outside declared range"
            )

        if len(set(self.boundary_variables)) != len(
            self.boundary_variables
        ):
            raise ValueError(
                "CCIR boundary variables must be unique"
            )

        if tuple(sorted(self.boundary_variables)) != (
            self.boundary_variables
        ):
            raise ValueError(
                "CCIR boundary variables must be sorted"
            )

        if any(
            not isinstance(constraint, CCIRConstraint)
            for constraint in self.constraints
        ):
            raise ValueError(
                "every CCIR program constraint must be a CCIRConstraint"
            )

        metadata_keys: list[str] = []

        for key, _ in self.metadata:
            if not isinstance(key, str) or not key:
                raise ValueError(
                    "CCIR metadata keys must be nonempty strings"
                )

            metadata_keys.append(key)

        if len(set(metadata_keys)) != len(metadata_keys):
            raise ValueError(
                "CCIR metadata keys must be unique"
            )

        if tuple(sorted(metadata_keys)) != tuple(metadata_keys):
            raise ValueError(
                "CCIR metadata keys must be sorted"
            )

    @property
    def internal_variables(self) -> tuple[int, ...]:
        boundary_set = set(self.boundary_variables)

        return tuple(
            variable
            for variable in range(self.variable_count)
            if variable not in boundary_set
        )

    @property
    def metadata_dict(self) -> dict[str, object]:
        return dict(self.metadata)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": CCIR_SCHEMA_VERSION,
            "name": self.name,
            "variable_count": self.variable_count,
            "boundary_variables": list(
                self.boundary_variables
            ),
            "constraints": [
                {
                    "family": constraint.family,
                    "payload": constraint.payload.to_dict(),
                }
                for constraint in self.constraints
            ],
            "metadata": {
                key: value
                for key, value in self.metadata
            },
        }
