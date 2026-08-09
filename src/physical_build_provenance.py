from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from src.physical_execution_evidence import (
    prepared_execution_hash,
)
from src.prepared_execution import PreparedExecution


PHYSICAL_BUILD_MANIFEST_SCHEMA = (
    "cpc.physical-build-manifest.v1"
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


@dataclass(frozen=True, order=True)
class BuildToolIdentity:
    stage: str
    tool: str
    version: str

    def __post_init__(self) -> None:
        _validate_non_empty(
            "stage",
            self.stage,
        )

        _validate_non_empty(
            "tool",
            self.tool,
        )

        _validate_non_empty(
            "version",
            self.version,
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "stage": self.stage,
            "tool": self.tool,
            "version": self.version,
        }


@dataclass(frozen=True, order=True)
class BuildInputRecord:
    input_id: str
    media_type: str
    sha256: str

    def __post_init__(self) -> None:
        _validate_non_empty(
            "input_id",
            self.input_id,
        )

        _validate_non_empty(
            "media_type",
            self.media_type,
        )

        _validate_sha256(
            "sha256",
            self.sha256,
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "input_id": self.input_id,
            "media_type": self.media_type,
            "sha256": self.sha256,
        }


@dataclass(frozen=True)
class PhysicalBuildManifest:
    """
    RFC-0009 deterministic build-provenance record.

    This manifest binds an RFC-0004 PreparedExecution to the declared
    physical FPGA build configuration and resulting bitstream identity.

    It does not assert that the bitstream was programmed into a device.
    """

    backend_id: str
    backend_version: str

    physical_profile_id: str

    prepared_execution_hash: str

    device_family: str
    device_part: str

    tools: tuple[BuildToolIdentity, ...]

    inputs: tuple[BuildInputRecord, ...]

    bitstream_format: str
    bitstream_sha256: str

    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            (
                "backend_id",
                self.backend_id,
            ),
            (
                "backend_version",
                self.backend_version,
            ),
            (
                "physical_profile_id",
                self.physical_profile_id,
            ),
            (
                "device_family",
                self.device_family,
            ),
            (
                "device_part",
                self.device_part,
            ),
            (
                "bitstream_format",
                self.bitstream_format,
            ),
        ):
            _validate_non_empty(
                name,
                value,
            )

        _validate_sha256(
            "prepared_execution_hash",
            self.prepared_execution_hash,
        )

        _validate_sha256(
            "bitstream_sha256",
            self.bitstream_sha256,
        )

        if any(
            not isinstance(
                item,
                BuildToolIdentity,
            )
            for item in self.tools
        ):
            raise ValueError(
                "tools must contain BuildToolIdentity values"
            )

        stages = tuple(
            item.stage
            for item in self.tools
        )

        if len(set(stages)) != len(stages):
            raise ValueError(
                "build tool stages must be unique"
            )

        if stages != tuple(sorted(stages)):
            raise ValueError(
                "build tools must be sorted by stage"
            )

        if any(
            not isinstance(
                item,
                BuildInputRecord,
            )
            for item in self.inputs
        ):
            raise ValueError(
                "inputs must contain BuildInputRecord values"
            )

        input_ids = tuple(
            item.input_id
            for item in self.inputs
        )

        if len(set(input_ids)) != len(input_ids):
            raise ValueError(
                "build input IDs must be unique"
            )

        if input_ids != tuple(sorted(input_ids)):
            raise ValueError(
                "build inputs must be sorted by input_id"
            )

        metadata_keys = tuple(
            key
            for key, _ in self.metadata
        )

        if any(
            not isinstance(key, str) or not key
            for key in metadata_keys
        ):
            raise ValueError(
                "metadata keys must be non-empty strings"
            )

        if len(set(metadata_keys)) != len(
            metadata_keys
        ):
            raise ValueError(
                "metadata keys must be unique"
            )

        if metadata_keys != tuple(
            sorted(metadata_keys)
        ):
            raise ValueError(
                "metadata keys must be sorted"
            )

    @property
    def schema(self) -> str:
        return PHYSICAL_BUILD_MANIFEST_SCHEMA

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
                "prepared_execution_hash": (
                    self.prepared_execution_hash
                ),
            },
            "device": {
                "family": self.device_family,
                "part": self.device_part,
            },
            "tools": [
                item.to_dict()
                for item in self.tools
            ],
            "inputs": [
                item.to_dict()
                for item in self.inputs
            ],
            "bitstream": {
                "format": self.bitstream_format,
                "sha256": self.bitstream_sha256,
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
    def manifest_hash(self) -> str:
        digest = hashlib.sha256(
            self.canonical_json().encode(
                "utf-8"
            )
        ).hexdigest()

        return f"sha256:{digest}"

    def to_manifest_dict(self) -> dict[str, object]:
        data = self.to_dict()
        data["manifest_hash"] = (
            self.manifest_hash
        )
        return data

    def to_json(
        self,
        *,
        indent: int = 2,
    ) -> str:
        return (
            json.dumps(
                self.to_manifest_dict(),
                indent=indent,
                sort_keys=True,
            )
            + "\n"
        )


def build_manifest_for_prepared_execution(
    *,
    prepared: PreparedExecution,
    physical_profile_id: str,
    device_family: str,
    device_part: str,
    tools: tuple[BuildToolIdentity, ...],
    inputs: tuple[BuildInputRecord, ...],
    bitstream_format: str,
    bitstream_sha256: str,
    metadata: tuple[tuple[str, str], ...] = (),
) -> PhysicalBuildManifest:
    """
    Construct deterministic physical-build provenance for an existing
    PreparedExecution.
    """

    return PhysicalBuildManifest(
        backend_id=prepared.backend_id,
        backend_version=(
            prepared.backend_version
        ),
        physical_profile_id=(
            physical_profile_id
        ),
        prepared_execution_hash=(
            prepared_execution_hash(
                prepared
            )
        ),
        device_family=device_family,
        device_part=device_part,
        tools=tools,
        inputs=inputs,
        bitstream_format=bitstream_format,
        bitstream_sha256=bitstream_sha256,
        metadata=metadata,
    )
