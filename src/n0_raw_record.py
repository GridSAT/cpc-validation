from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass


N0_RAW_RECORD_SCHEMA = "cpc.shor.n0.raw-record.v2"

N0_RECORD_ROLES = (
    "calibration",
    "diagnostic",
    "negative_control",
    "operational",
)

N0_ACQUISITION_STATUSES = (
    "complete",
    "invalid",
)

N0_RECORD_REALIZATION_STATUSES = (
    "physical",
    "simulated",
)

N0_RESET_STATUSES = (
    "failed",
    "ok",
)

N0_RAW_PAYLOAD_PROVENANCE = (
    "native-instrument-bytes",
    "synthetic-canonical-sample-payload",
)

SIMULATED_TIMEBASE_ID = "SIMULATED-MODEL-TIMEBASE-v1"

FORBIDDEN_METADATA_KEYS = frozenset(
    {
        "expected_class",
        "expected_order",
        "expected_output",
        "expected_phase",
        "satisfying_assignment",
        "semantic_answer",
        "theta",
        "theta_truth",
        "truth",
        "truth_phase",
    }
)


def canonical_json_value(value: object) -> str:
    """
    Canonical semantic JSON.

    Python tuples and lists intentionally serialize identically as JSON
    arrays. This avoids representation-only tuple/list mismatches.
    """
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    )


def canonical_sha256_value(value: object) -> str:
    digest = hashlib.sha256(
        canonical_json_value(value).encode("utf-8")
    ).hexdigest()
    return f"sha256:{digest}"


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

    if (
        len(digest) != 64
        or any(
            character not in "0123456789abcdef"
            for character in digest
        )
    ):
        raise ValueError(
            f"{field_name} must be a lowercase sha256 digest"
        )


def _validate_finite_samples(
    values: tuple[float, ...],
    field_name: str,
    sample_count: int,
) -> None:
    if len(values) != sample_count:
        raise ValueError(
            f"{field_name} length must equal sample_count"
        )

    if any(
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(value)
        for value in values
    ):
        raise ValueError(
            f"{field_name} must contain finite numeric samples"
        )


def _validate_boolean_samples(
    values: tuple[bool, ...],
    field_name: str,
    sample_count: int,
) -> None:
    if len(values) != sample_count:
        raise ValueError(
            f"{field_name} length must equal sample_count"
        )

    if any(
        not isinstance(value, bool)
        for value in values
    ):
        raise ValueError(
            f"{field_name} must contain booleans"
        )


def _validate_metadata(
    metadata: tuple[tuple[str, object], ...],
) -> None:
    keys = tuple(
        key
        for key, _ in metadata
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

    forbidden = {
        key.lower()
        for key in keys
        if key.lower() in FORBIDDEN_METADATA_KEYS
    }

    if forbidden:
        raise ValueError(
            "metadata contains forbidden truth field(s): "
            + ", ".join(sorted(forbidden))
        )


@dataclass(frozen=True)
class N0RawRecord:
    experiment_id: str
    trial_id: str
    profile_id: str

    apparatus_id: str
    controller_id: str
    firmware_control_id: str
    calibration_id: str
    reference_id: str

    role: str

    sample_period_s: float
    sample_count: int

    acquisition_start_s: float
    acquisition_end_s: float

    burn_in_start_index: int
    burn_in_end_index: int

    command_phase_rad: float

    preparation_command_hash: str
    probe_configuration_hash: str

    signal_i: tuple[float, ...]
    signal_q: tuple[float, ...]
    reference_i: tuple[float, ...]
    reference_q: tuple[float, ...]

    clipping_flags: tuple[bool, ...]
    saturation_flags: tuple[bool, ...]
    dropped_sample_flags: tuple[bool, ...]
    timestamp_discontinuity_flags: tuple[bool, ...]

    reset_status: str
    acquisition_status: str

    realization_status: str
    timebase_id: str
    raw_payload_provenance: str

    original_bytes_sha256: str

    metadata: tuple[
        tuple[str, object],
        ...
    ] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("experiment_id", self.experiment_id),
            ("trial_id", self.trial_id),
            ("profile_id", self.profile_id),
            ("apparatus_id", self.apparatus_id),
            ("controller_id", self.controller_id),
            (
                "firmware_control_id",
                self.firmware_control_id,
            ),
            ("calibration_id", self.calibration_id),
            ("reference_id", self.reference_id),
            ("reset_status", self.reset_status),
            ("timebase_id", self.timebase_id),
        ):
            _validate_nonempty_string(
                value,
                name,
            )

        if self.role not in N0_RECORD_ROLES:
            raise ValueError(
                "role must be one of: "
                + ", ".join(N0_RECORD_ROLES)
            )

        if self.reset_status not in N0_RESET_STATUSES:
            raise ValueError(
                "reset_status must be one of: "
                + ", ".join(N0_RESET_STATUSES)
            )

        if self.realization_status not in (
            N0_RECORD_REALIZATION_STATUSES
        ):
            raise ValueError(
                "realization_status must be one of: "
                + ", ".join(N0_RECORD_REALIZATION_STATUSES)
            )

        if self.raw_payload_provenance not in (
            N0_RAW_PAYLOAD_PROVENANCE
        ):
            raise ValueError(
                "raw_payload_provenance must be one of: "
                + ", ".join(N0_RAW_PAYLOAD_PROVENANCE)
            )

        if self.acquisition_status not in (
            N0_ACQUISITION_STATUSES
        ):
            raise ValueError(
                "acquisition_status must be one of: "
                + ", ".join(N0_ACQUISITION_STATUSES)
            )

        if self.realization_status == "simulated":
            if (
                self.raw_payload_provenance
                != "synthetic-canonical-sample-payload"
            ):
                raise ValueError(
                    "simulated record requires synthetic payload provenance"
                )

            if self.timebase_id != SIMULATED_TIMEBASE_ID:
                raise ValueError(
                    "simulated record requires simulated timebase identity"
                )

        if self.realization_status == "physical":
            if (
                self.raw_payload_provenance
                != "native-instrument-bytes"
            ):
                raise ValueError(
                    "physical record requires native instrument-byte provenance"
                )

            if self.timebase_id.startswith("SIMULATED"):
                raise ValueError(
                    "physical record may not use simulated timebase identity"
                )

        if (
            not isinstance(self.sample_count, int)
            or isinstance(self.sample_count, bool)
            or self.sample_count <= 0
        ):
            raise ValueError(
                "sample_count must be a positive integer"
            )

        if (
            not isinstance(self.sample_period_s, (int, float))
            or isinstance(self.sample_period_s, bool)
            or not math.isfinite(self.sample_period_s)
            or self.sample_period_s <= 0
        ):
            raise ValueError(
                "sample_period_s must be finite and positive"
            )

        for name, value in (
            (
                "acquisition_start_s",
                self.acquisition_start_s,
            ),
            (
                "acquisition_end_s",
                self.acquisition_end_s,
            ),
            (
                "command_phase_rad",
                self.command_phase_rad,
            ),
        ):
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(value)
            ):
                raise ValueError(
                    f"{name} must be a finite number"
                )

        if self.acquisition_end_s <= self.acquisition_start_s:
            raise ValueError(
                "acquisition_end_s must be greater than "
                "acquisition_start_s"
            )

        for name, value in (
            (
                "burn_in_start_index",
                self.burn_in_start_index,
            ),
            (
                "burn_in_end_index",
                self.burn_in_end_index,
            ),
        ):
            if (
                not isinstance(value, int)
                or isinstance(value, bool)
            ):
                raise ValueError(
                    f"{name} must be an integer"
                )

        if not (
            0
            <= self.burn_in_start_index
            <= self.burn_in_end_index
            <= self.sample_count
        ):
            raise ValueError(
                "burn-in bounds must lie within sample range"
            )

        _validate_sha256(
            self.preparation_command_hash,
            "preparation_command_hash",
        )

        _validate_sha256(
            self.probe_configuration_hash,
            "probe_configuration_hash",
        )

        _validate_sha256(
            self.original_bytes_sha256,
            "original_bytes_sha256",
        )

        for name, values in (
            ("signal_i", self.signal_i),
            ("signal_q", self.signal_q),
            ("reference_i", self.reference_i),
            ("reference_q", self.reference_q),
        ):
            _validate_finite_samples(
                values,
                name,
                self.sample_count,
            )

        for name, values in (
            (
                "clipping_flags",
                self.clipping_flags,
            ),
            (
                "saturation_flags",
                self.saturation_flags,
            ),
            (
                "dropped_sample_flags",
                self.dropped_sample_flags,
            ),
            (
                "timestamp_discontinuity_flags",
                self.timestamp_discontinuity_flags,
            ),
        ):
            _validate_boolean_samples(
                values,
                name,
                self.sample_count,
            )

        _validate_metadata(
            self.metadata
        )

    @property
    def reset_valid(self) -> bool:
        return self.reset_status == "ok"

    @property
    def has_native_instrument_bytes(self) -> bool:
        return (
            self.raw_payload_provenance
            == "native-instrument-bytes"
        )

    @property
    def schema(self) -> str:
        return N0_RAW_RECORD_SCHEMA

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "experiment_id": self.experiment_id,
            "trial_id": self.trial_id,
            "profile_id": self.profile_id,
            "apparatus_id": self.apparatus_id,
            "controller_id": self.controller_id,
            "firmware_control_id": self.firmware_control_id,
            "calibration_id": self.calibration_id,
            "reference_id": self.reference_id,
            "role": self.role,
            "sample_period_s": self.sample_period_s,
            "sample_count": self.sample_count,
            "acquisition_start_s": self.acquisition_start_s,
            "acquisition_end_s": self.acquisition_end_s,
            "burn_in_start_index": self.burn_in_start_index,
            "burn_in_end_index": self.burn_in_end_index,
            "command_phase_rad": self.command_phase_rad,
            "preparation_command_hash": (
                self.preparation_command_hash
            ),
            "probe_configuration_hash": (
                self.probe_configuration_hash
            ),
            "signal_i": self.signal_i,
            "signal_q": self.signal_q,
            "reference_i": self.reference_i,
            "reference_q": self.reference_q,
            "clipping_flags": self.clipping_flags,
            "saturation_flags": self.saturation_flags,
            "dropped_sample_flags": (
                self.dropped_sample_flags
            ),
            "timestamp_discontinuity_flags": (
                self.timestamp_discontinuity_flags
            ),
            "reset_status": self.reset_status,
            "acquisition_status": self.acquisition_status,
            "realization_status": self.realization_status,
            "timebase_id": self.timebase_id,
            "raw_payload_provenance": (
                self.raw_payload_provenance
            ),
            "original_bytes_sha256": (
                self.original_bytes_sha256
            ),
            "metadata": {
                key: value
                for key, value in self.metadata
            },
        }

    @property
    def canonical_json(self) -> str:
        return canonical_json_value(
            self.to_dict()
        )

    @property
    def record_hash(self) -> str:
        return canonical_sha256_value(
            self.to_dict()
        )


def native_instrument_bytes_hash(
    payload: bytes,
) -> str:
    if not isinstance(payload, bytes):
        raise ValueError(
            "native instrument payload must be bytes"
        )

    if not payload:
        raise ValueError(
            "native instrument payload must not be empty"
        )

    return (
        "sha256:"
        + hashlib.sha256(payload).hexdigest()
    )


def synthetic_sample_payload(
    *,
    signal_i: tuple[float, ...],
    signal_q: tuple[float, ...],
    reference_i: tuple[float, ...],
    reference_q: tuple[float, ...],
) -> dict[str, object]:
    return {
        "reference_i": reference_i,
        "reference_q": reference_q,
        "signal_i": signal_i,
        "signal_q": signal_q,
    }


def synthetic_sample_payload_hash(
    *,
    signal_i: tuple[float, ...],
    signal_q: tuple[float, ...],
    reference_i: tuple[float, ...],
    reference_q: tuple[float, ...],
) -> str:
    return canonical_sha256_value(
        synthetic_sample_payload(
            signal_i=signal_i,
            signal_q=signal_q,
            reference_i=reference_i,
            reference_q=reference_q,
        )
    )
