from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from src.physical_build_provenance import (
    PhysicalBuildManifest,
)


DEVICE_PROGRAMMING_RECORD_SCHEMA = (
    "cpc.device-programming-record.v1"
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
class DeviceProgrammingRecord:
    """
    RFC-0009 immutable record of one physical device-programming event.

    The record binds one PhysicalBuildManifest and its bitstream identity
    to one declared physical device and programming interface.

    It does not establish that subsequent substrate execution occurred or
    that any observed or decoded result is semantically correct.
    """

    backend_id: str
    backend_version: str
    physical_profile_id: str

    build_manifest_hash: str
    bitstream_sha256: str

    board_id: str
    device_family: str
    device_part: str
    device_id: str

    programming_interface: str
    programmer: str
    programmer_version: str

    programming_log_sha256: str

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
            ("device_family", self.device_family),
            ("device_part", self.device_part),
            ("device_id", self.device_id),
            (
                "programming_interface",
                self.programming_interface,
            ),
            ("programmer", self.programmer),
            (
                "programmer_version",
                self.programmer_version,
            ),
        ):
            _validate_non_empty(
                name,
                value,
            )

        for name, value in (
            (
                "build_manifest_hash",
                self.build_manifest_hash,
            ),
            (
                "bitstream_sha256",
                self.bitstream_sha256,
            ),
            (
                "programming_log_sha256",
                self.programming_log_sha256,
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

        for _, value in self.metadata:
            if not isinstance(value, str):
                raise ValueError(
                    "metadata values must be strings"
                )

    @property
    def schema(self) -> str:
        return DEVICE_PROGRAMMING_RECORD_SCHEMA

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
                "build_manifest_hash": (
                    self.build_manifest_hash
                ),
                "bitstream_sha256": (
                    self.bitstream_sha256
                ),
            },
            "device": {
                "board_id": self.board_id,
                "device_family": (
                    self.device_family
                ),
                "device_part": self.device_part,
                "device_id": self.device_id,
            },
            "programming": {
                "interface": (
                    self.programming_interface
                ),
                "programmer": self.programmer,
                "programmer_version": (
                    self.programmer_version
                ),
                "programming_log_sha256": (
                    self.programming_log_sha256
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
    def record_hash(self) -> str:
        digest = hashlib.sha256(
            self.canonical_json().encode(
                "utf-8"
            )
        ).hexdigest()

        return f"sha256:{digest}"

    def to_record_dict(self) -> dict[str, object]:
        data = self.to_dict()
        data["record_hash"] = self.record_hash
        return data

    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        return (
            json.dumps(
                self.to_record_dict(),
                indent=indent,
                sort_keys=True,
            )
            + "\n"
        )


def programming_record_from_build(
    *,
    build: PhysicalBuildManifest,
    board_id: str,
    device_id: str,
    programming_interface: str,
    programmer: str,
    programmer_version: str,
    programming_log_sha256: str,
    metadata: tuple[tuple[str, str], ...] = (),
) -> DeviceProgrammingRecord:
    """
    Bind one declared programming event to an existing physical build.
    """

    return DeviceProgrammingRecord(
        backend_id=build.backend_id,
        backend_version=build.backend_version,
        physical_profile_id=(
            build.physical_profile_id
        ),
        build_manifest_hash=(
            build.manifest_hash
        ),
        bitstream_sha256=(
            build.bitstream_sha256
        ),
        board_id=board_id,
        device_family=build.device_family,
        device_part=build.device_part,
        device_id=device_id,
        programming_interface=(
            programming_interface
        ),
        programmer=programmer,
        programmer_version=(
            programmer_version
        ),
        programming_log_sha256=(
            programming_log_sha256
        ),
        metadata=metadata,
    )
