from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import math

from src.n0_calibration import N0Calibration
from src.n0_physical_profile import N0PhysicalProfile
from src.n0_raw_record import (
    N0_RECORD_ROLES,
    N0RawRecord,
)


N0_DEVICE_ADAPTER_SCHEMA = "cpc.shor.n0.device-adapter.v1"

DEVICE_REALIZATION_STATUSES = (
    "physical",
    "simulated",
)


@dataclass(frozen=True)
class N0TrialCommand:
    experiment_id: str
    trial_id: str
    role: str

    command_phase_rad: float

    preparation_command_hash: str
    probe_configuration_hash: str

    sample_count: int

    def __post_init__(self) -> None:
        for name, value in (
            ("experiment_id", self.experiment_id),
            ("trial_id", self.trial_id),
            (
                "preparation_command_hash",
                self.preparation_command_hash,
            ),
            (
                "probe_configuration_hash",
                self.probe_configuration_hash,
            ),
        ):
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"{name} must be a non-empty string"
                )

        if self.role not in N0_RECORD_ROLES:
            raise ValueError(
                "role must be one of: "
                + ", ".join(N0_RECORD_ROLES)
            )

        if (
            not isinstance(
                self.command_phase_rad,
                (int, float),
            )
            or isinstance(
                self.command_phase_rad,
                bool,
            )
            or not math.isfinite(
                self.command_phase_rad
            )
        ):
            raise ValueError(
                "command_phase_rad must be finite"
            )

        if (
            not isinstance(self.sample_count, int)
            or isinstance(self.sample_count, bool)
            or self.sample_count <= 0
        ):
            raise ValueError(
                "sample_count must be a positive integer"
            )


class N0DeviceAdapter(ABC):
    """
    Common N0 acquisition boundary.

    Inference consumes N0RawRecord and N0Calibration only. The reducer must
    not depend on the concrete device-adapter implementation.
    """

    def __init__(
        self,
        *,
        profile: N0PhysicalProfile,
        calibration: N0Calibration,
        device_id: str,
        realization_status: str,
    ) -> None:
        if (
            realization_status
            not in DEVICE_REALIZATION_STATUSES
        ):
            raise ValueError(
                "unknown device realization status"
            )

        if not isinstance(device_id, str) or not device_id:
            raise ValueError(
                "device_id must be a non-empty string"
            )

        if calibration.profile_id != profile.profile_id:
            raise ValueError(
                "calibration/profile identity mismatch"
            )

        if realization_status != profile.realization_status:
            raise ValueError(
                "device/profile realization mismatch"
            )

        if (
            realization_status
            != calibration.realization_status
        ):
            raise ValueError(
                "device/calibration realization mismatch"
            )

        self._profile = profile
        self._calibration = calibration
        self._device_id = device_id
        self._realization_status = realization_status

    @property
    def schema(self) -> str:
        return N0_DEVICE_ADAPTER_SCHEMA

    @property
    def profile(self) -> N0PhysicalProfile:
        return self._profile

    @property
    def calibration(self) -> N0Calibration:
        return self._calibration

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def realization_status(self) -> str:
        return self._realization_status

    @abstractmethod
    def acquire(
        self,
        command: N0TrialCommand,
    ) -> N0RawRecord:
        raise NotImplementedError


def validate_adapter_record(
    *,
    adapter: N0DeviceAdapter,
    command: N0TrialCommand,
    record: N0RawRecord,
) -> None:
    if record.profile_id != adapter.profile.profile_id:
        raise ValueError(
            "record/profile identity mismatch"
        )

    if record.realization_status != adapter.realization_status:
        raise ValueError(
            "record/device realization mismatch"
        )

    if record.apparatus_id != adapter.device_id:
        raise ValueError(
            "record/device identity mismatch"
        )

    if record.calibration_id != (
        adapter.calibration.calibration_id
    ):
        raise ValueError(
            "record/calibration identity mismatch"
        )

    if record.experiment_id != command.experiment_id:
        raise ValueError(
            "record/experiment identity mismatch"
        )

    if record.trial_id != command.trial_id:
        raise ValueError(
            "record/trial identity mismatch"
        )

    if record.role != command.role:
        raise ValueError(
            "record/role mismatch"
        )

    if record.command_phase_rad != (
        command.command_phase_rad
    ):
        raise ValueError(
            "record/command phase mismatch"
        )

    if record.preparation_command_hash != (
        command.preparation_command_hash
    ):
        raise ValueError(
            "record/preparation identity mismatch"
        )

    if record.probe_configuration_hash != (
        command.probe_configuration_hash
    ):
        raise ValueError(
            "record/probe identity mismatch"
        )

    if record.sample_count != command.sample_count:
        raise ValueError(
            "record/sample-count mismatch"
        )
