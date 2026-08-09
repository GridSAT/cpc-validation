from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from src.observable_execution import (
    ObservableExecution,
)
from src.physical_device_programming import (
    DeviceProgrammingRecord,
)
from src.physical_execution_evidence import (
    observable_execution_hash,
    prepared_execution_hash,
)
from src.prepared_execution import (
    PreparedExecution,
)


PHYSICAL_EXECUTION_EVENT_SCHEMA = (
    "cpc.physical-execution-event.v1"
)


def _validate_non_empty(
    name: str,
    value: str,
) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(
            f"{name} must be a non-empty string"
        )


def _validate_sha256(
    name: str,
    value: str,
) -> None:
    prefix = "sha256:"

    if (
        not isinstance(value, str)
        or not value.startswith(prefix)
    ):
        raise ValueError(
            f"{name} must be a sha256 digest"
        )

    digest = value[len(prefix):]

    if len(digest) != 64:
        raise ValueError(
            f"{name} must be a sha256 digest"
        )

    if any(
        character not in "0123456789abcdef"
        for character in digest
    ):
        raise ValueError(
            f"{name} must be a lowercase sha256 digest"
        )


@dataclass(frozen=True)
class PhysicalExecutionEvent:
    """
    RFC-0009 immutable binding for one physical execution event.

    The event binds one device-programming record, one PreparedExecution,
    and one ObservableExecution to declared physical stimulus and
    observation interfaces.

    It does not establish semantic correctness.
    """

    backend_id: str
    backend_version: str
    physical_profile_id: str

    programming_record_hash: str
    prepared_execution_hash: str
    observable_execution_hash: str

    board_id: str
    device_id: str

    stimulus_interface: str
    observation_interface: str

    stimulus_record_sha256: str
    measurement_record_sha256: str

    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("backend_id", self.backend_id),
            ("backend_version", self.backend_version),
            (
                "physical_profile_id",
                self.physical_profile_id,
            ),
            ("board_id", self.board_id),
            ("device_id", self.device_id),
            (
                "stimulus_interface",
                self.stimulus_interface,
            ),
            (
                "observation_interface",
                self.observation_interface,
            ),
        ):
            _validate_non_empty(
                name,
                value,
            )

        for name, value in (
            (
                "programming_record_hash",
                self.programming_record_hash,
            ),
            (
                "prepared_execution_hash",
                self.prepared_execution_hash,
            ),
            (
                "observable_execution_hash",
                self.observable_execution_hash,
            ),
            (
                "stimulus_record_sha256",
                self.stimulus_record_sha256,
            ),
            (
                "measurement_record_sha256",
                self.measurement_record_sha256,
            ),
        ):
            _validate_sha256(
                name,
                value,
            )

        keys = tuple(
            key
            for key, _ in self.metadata
        )

        if any(
            not isinstance(key, str) or not key
            for key in keys
        ):
            raise ValueError(
                "metadata keys must be non-empty strings"
            )

        if len(set(keys)) != len(keys):
            raise ValueError(
                "metadata keys must be unique"
            )

        if keys != tuple(sorted(keys)):
            raise ValueError(
                "metadata keys must be sorted"
            )

        if any(
            not isinstance(value, str)
            for _, value in self.metadata
        ):
            raise ValueError(
                "metadata values must be strings"
            )

    @property
    def schema(self) -> str:
        return PHYSICAL_EXECUTION_EVENT_SCHEMA

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "backend": {
                "id": self.backend_id,
                "version": self.backend_version,
            },
            "physical_profile_id": (
                self.physical_profile_id
            ),
            "binding": {
                "programming_record_hash": (
                    self.programming_record_hash
                ),
                "prepared_execution_hash": (
                    self.prepared_execution_hash
                ),
                "observable_execution_hash": (
                    self.observable_execution_hash
                ),
            },
            "device": {
                "board_id": self.board_id,
                "device_id": self.device_id,
            },
            "execution": {
                "stimulus_interface": (
                    self.stimulus_interface
                ),
                "observation_interface": (
                    self.observation_interface
                ),
                "stimulus_record_sha256": (
                    self.stimulus_record_sha256
                ),
                "measurement_record_sha256": (
                    self.measurement_record_sha256
                ),
            },
            "metadata": {
                key: value
                for key, value in self.metadata
            },
        }

    def canonical_json(self) -> str:
        return (
            json.dumps(
                self.to_dict(),
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        )

    @property
    def event_hash(self) -> str:
        digest = hashlib.sha256(
            self.canonical_json().encode(
                "utf-8"
            )
        ).hexdigest()

        return f"sha256:{digest}"

    def to_event_dict(self) -> dict[str, object]:
        data = self.to_dict()
        data["event_hash"] = self.event_hash
        return data

    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        return (
            json.dumps(
                self.to_event_dict(),
                indent=indent,
                sort_keys=True,
            )
            + "\n"
        )


def execution_event_from_records(
    *,
    programming: DeviceProgrammingRecord,
    prepared: PreparedExecution,
    observable: ObservableExecution,
    stimulus_interface: str,
    observation_interface: str,
    stimulus_record_sha256: str,
    measurement_record_sha256: str,
    metadata: tuple[tuple[str, str], ...] = (),
) -> PhysicalExecutionEvent:
    """
    Construct one physical execution-event binding from existing records.
    """

    if (
        programming.backend_id
        != prepared.backend_id
        or programming.backend_id
        != observable.backend_id
    ):
        raise ValueError(
            "physical execution backend IDs do not match"
        )

    if (
        programming.backend_version
        != prepared.backend_version
        or programming.backend_version
        != observable.backend_version
    ):
        raise ValueError(
            "physical execution backend versions do not match"
        )

    return PhysicalExecutionEvent(
        backend_id=programming.backend_id,
        backend_version=(
            programming.backend_version
        ),
        physical_profile_id=(
            programming.physical_profile_id
        ),
        programming_record_hash=(
            programming.record_hash
        ),
        prepared_execution_hash=(
            prepared_execution_hash(
                prepared
            )
        ),
        observable_execution_hash=(
            observable_execution_hash(
                observable
            )
        ),
        board_id=programming.board_id,
        device_id=programming.device_id,
        stimulus_interface=(
            stimulus_interface
        ),
        observation_interface=(
            observation_interface
        ),
        stimulus_record_sha256=(
            stimulus_record_sha256
        ),
        measurement_record_sha256=(
            measurement_record_sha256
        ),
        metadata=metadata,
    )
