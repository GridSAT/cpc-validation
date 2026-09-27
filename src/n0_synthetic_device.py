from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

import numpy as np

from src.n0_bosonic_model import (
    N0BosonicModel,
    build_default_n0_bosonic_model,
)
from src.n0_calibration import (
    N0Calibration,
    build_simulated_n0_calibration,
)
from src.n0_device_adapter import (
    N0DeviceAdapter,
    N0TrialCommand,
    validate_adapter_record,
)
from src.n0_effective_measurement import (
    N0MeasurementConfig,
    evolve_deterministic,
    expected_measurement_increment_rate,
)
from src.n0_physical_profile import (
    N0PhysicalProfile,
    build_default_n0_physical_profile,
)
from src.n0_raw_record import (
    N0RawRecord,
    SIMULATED_TIMEBASE_ID,
    synthetic_sample_payload_hash,
)


N0_SYNTHETIC_DEVICE_SCHEMA = (
    "cpc.shor.n0.synthetic-device.v1"
)

SIMULATED_DEVICE_ID = "SIMULATED-CAT-DEVICE-v1"
SIMULATED_CONTROLLER_ID = "SIMULATED-N0-CONTROLLER-v1"
SIMULATED_FIRMWARE_ID = "SIMULATED-CONTROL-v1"
SIMULATED_REFERENCE_ID = "SIMULATED-REFERENCE-v1"


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


def opaque_preparation_hash(
    preparation_identity: str,
) -> str:
    if (
        not isinstance(preparation_identity, str)
        or not preparation_identity
    ):
        raise ValueError(
            "preparation_identity must be non-empty"
        )

    digest = hashlib.sha256(
        (
            "CPC-SHOR-N0-PREPARATION-v1|"
            + preparation_identity
        ).encode("utf-8")
    ).hexdigest()

    return f"sha256:{digest}"


def derive_trial_seed(
    *,
    root_seed_commitment: str,
    experiment_id: str,
    trial_id: str,
    command_phase_rad: float,
) -> int:
    _validate_sha256(
        root_seed_commitment,
        "root_seed_commitment",
    )

    if (
        not isinstance(experiment_id, str)
        or not experiment_id
    ):
        raise ValueError(
            "experiment_id must be non-empty"
        )

    if (
        not isinstance(trial_id, str)
        or not trial_id
    ):
        raise ValueError(
            "trial_id must be non-empty"
        )

    if (
        not isinstance(command_phase_rad, (int, float))
        or isinstance(command_phase_rad, bool)
        or not math.isfinite(command_phase_rad)
    ):
        raise ValueError(
            "command_phase_rad must be finite"
        )

    material = (
        "CPC-SHOR-N0-TRIAL-SEED-v1|"
        + root_seed_commitment
        + "|"
        + experiment_id
        + "|"
        + trial_id
        + "|"
        + format(float(command_phase_rad), ".17g")
    )

    digest = hashlib.sha256(
        material.encode("utf-8")
    ).digest()

    return int.from_bytes(
        digest[:8],
        byteorder="big",
        signed=False,
    )


@dataclass(frozen=True)
class SyntheticPreparation:
    preparation_command_hash: str
    theta_rad: float

    def __post_init__(self) -> None:
        _validate_sha256(
            self.preparation_command_hash,
            "preparation_command_hash",
        )

        if (
            not isinstance(self.theta_rad, (int, float))
            or isinstance(self.theta_rad, bool)
            or not math.isfinite(self.theta_rad)
        ):
            raise ValueError(
                "theta_rad must be finite"
            )


class SyntheticN0Device(N0DeviceAdapter):
    """
    Simulation-only N0 source.

    The private preparation catalog may contain simulation truth. That truth
    is used only to generate the synthetic physical state. It is never
    inserted into N0RawRecord and is never supplied to the reducer.
    """

    def __init__(
        self,
        *,
        root_seed_commitment: str,
        preparations: tuple[
            SyntheticPreparation,
            ...
        ],
        profile: N0PhysicalProfile | None = None,
        calibration: N0Calibration | None = None,
        model: N0BosonicModel | None = None,
        pre_measurement_duration: float = 0.0,
    ) -> None:
        _validate_sha256(
            root_seed_commitment,
            "root_seed_commitment",
        )

        if profile is None:
            profile = build_default_n0_physical_profile()

        if calibration is None:
            calibration = build_simulated_n0_calibration()

        if model is None:
            model = build_default_n0_bosonic_model()

        if (
            not isinstance(
                pre_measurement_duration,
                (int, float),
            )
            or isinstance(
                pre_measurement_duration,
                bool,
            )
            or not math.isfinite(
                pre_measurement_duration
            )
            or pre_measurement_duration < 0
        ):
            raise ValueError(
                "pre_measurement_duration must be "
                "finite and non-negative"
            )

        if not preparations:
            raise ValueError(
                "preparations must not be empty"
            )

        hashes = tuple(
            preparation.preparation_command_hash
            for preparation in preparations
        )

        if len(set(hashes)) != len(hashes):
            raise ValueError(
                "preparation hashes must be unique"
            )

        super().__init__(
            profile=profile,
            calibration=calibration,
            device_id=SIMULATED_DEVICE_ID,
            realization_status="simulated",
        )

        self._root_seed_commitment = (
            root_seed_commitment
        )

        self._model = model
        self._pre_measurement_duration = float(
            pre_measurement_duration
        )

        self._preparation_catalog = {
            preparation.preparation_command_hash:
            preparation.theta_rad
            for preparation in preparations
        }

        self._consumed_trial_ids: set[
            tuple[str, str]
        ] = set()

    @property
    def synthetic_schema(self) -> str:
        return N0_SYNTHETIC_DEVICE_SCHEMA

    @property
    def root_seed_commitment(self) -> str:
        return self._root_seed_commitment

    def _lookup_calibration_value(
        self,
        name: str,
    ) -> float:
        for item in self.calibration.values:
            if item.name == name:
                if item.nominal_value is None:
                    raise RuntimeError(
                        f"unresolved simulated calibration: {name}"
                    )

                return float(
                    item.nominal_value
                )

        raise RuntimeError(
            f"missing simulated calibration: {name}"
        )

    def acquire(
        self,
        command: N0TrialCommand,
    ) -> N0RawRecord:
        trial_key = (
            command.experiment_id,
            command.trial_id,
        )

        if trial_key in self._consumed_trial_ids:
            raise RuntimeError(
                "trial identity already consumed; "
                "retry/reseed is prohibited"
            )

        # Consume before stochastic generation. A failed acquisition remains
        # consumed within this device instance.
        self._consumed_trial_ids.add(
            trial_key
        )

        if command.preparation_command_hash not in (
            self._preparation_catalog
        ):
            raise ValueError(
                "unknown preparation command hash"
            )

        if command.command_phase_rad not in (
            self.profile.permitted_command_phases_rad
        ):
            raise ValueError(
                "command phase not permitted by profile"
            )

        theta = self._preparation_catalog[
            command.preparation_command_hash
        ]

        rho = self._model.prepared_density_matrix(
            theta
        )

        eta = self._lookup_calibration_value(
            "measurement_efficiency_eta"
        )

        gamma_m = self._lookup_calibration_value(
            "measurement_rate_gamma_m"
        )

        sample_period = self._lookup_calibration_value(
            "sample_period_s"
        )

        reference_amplitude = (
            self._lookup_calibration_value(
                "reference_amplitude"
            )
        )

        reference_phase = (
            self._lookup_calibration_value(
                "reference_phase_rad"
            )
        )

        config = N0MeasurementConfig(
            beta_rad=command.command_phase_rad,
            measurement_rate_gamma_m=gamma_m,
            measurement_efficiency_eta=eta,
        )

        if self._pre_measurement_duration > 0.0:
            evolution = evolve_deterministic(
                model=self._model,
                initial_state=rho,
                config=config,
                duration=self._pre_measurement_duration,
                dt=self._model.integration_dt,
            )

            rho = evolution.final_state

        mean_current = (
            expected_measurement_increment_rate(
                model=self._model,
                rho=rho,
                config=config,
            )
        )

        seed = derive_trial_seed(
            root_seed_commitment=(
                self._root_seed_commitment
            ),
            experiment_id=command.experiment_id,
            trial_id=command.trial_id,
            command_phase_rad=(
                command.command_phase_rad
            ),
        )

        rng = np.random.default_rng(
            seed
        )

        # Discrete version of:
        #
        #   dY = mu dt + dW
        #
        # storing the current dY/dt:
        #
        #   I_k = mu + xi_k / sqrt(dt)
        #
        # This is explicitly a simulated normalized measurement current.
        noise_scale = 1.0 / math.sqrt(
            sample_period
        )

        signal_i_array = (
            mean_current
            + rng.normal(
                loc=0.0,
                scale=noise_scale,
                size=command.sample_count,
            )
        )

        signal_q_array = rng.normal(
            loc=0.0,
            scale=noise_scale,
            size=command.sample_count,
        )

        # Simulated external reference. Reference noise is generated
        # independently from the signal draws but from the same immutable
        # trial RNG stream.
        reference_i_mean = (
            reference_amplitude
            * math.cos(
                reference_phase
            )
        )

        reference_q_mean = (
            reference_amplitude
            * math.sin(
                reference_phase
            )
        )

        reference_noise_scale = 0.01

        reference_i_array = (
            reference_i_mean
            + rng.normal(
                loc=0.0,
                scale=reference_noise_scale,
                size=command.sample_count,
            )
        )

        reference_q_array = (
            reference_q_mean
            + rng.normal(
                loc=0.0,
                scale=reference_noise_scale,
                size=command.sample_count,
            )
        )

        signal_i = tuple(
            float(value)
            for value in signal_i_array
        )

        signal_q = tuple(
            float(value)
            for value in signal_q_array
        )

        reference_i = tuple(
            float(value)
            for value in reference_i_array
        )

        reference_q = tuple(
            float(value)
            for value in reference_q_array
        )

        raw_hash = synthetic_sample_payload_hash(
            signal_i=signal_i,
            signal_q=signal_q,
            reference_i=reference_i,
            reference_q=reference_q,
        )

        record = N0RawRecord(
            experiment_id=command.experiment_id,
            trial_id=command.trial_id,
            profile_id=self.profile.profile_id,
            apparatus_id=self.device_id,
            controller_id=SIMULATED_CONTROLLER_ID,
            firmware_control_id=SIMULATED_FIRMWARE_ID,
            calibration_id=(
                self.calibration.calibration_id
            ),
            reference_id=SIMULATED_REFERENCE_ID,
            role=command.role,
            sample_period_s=sample_period,
            sample_count=command.sample_count,
            acquisition_start_s=0.0,
            acquisition_end_s=(
                sample_period
                * command.sample_count
            ),
            burn_in_start_index=0,
            burn_in_end_index=0,
            command_phase_rad=(
                command.command_phase_rad
            ),
            preparation_command_hash=(
                command.preparation_command_hash
            ),
            probe_configuration_hash=(
                command.probe_configuration_hash
            ),
            signal_i=signal_i,
            signal_q=signal_q,
            reference_i=reference_i,
            reference_q=reference_q,
            clipping_flags=(
                (False,)
                * command.sample_count
            ),
            saturation_flags=(
                (False,)
                * command.sample_count
            ),
            dropped_sample_flags=(
                (False,)
                * command.sample_count
            ),
            timestamp_discontinuity_flags=(
                (False,)
                * command.sample_count
            ),
            reset_status="ok",
            acquisition_status="complete",
            realization_status="simulated",
            timebase_id=SIMULATED_TIMEBASE_ID,
            raw_payload_provenance=(
                "synthetic-canonical-sample-payload"
            ),
            original_bytes_sha256=raw_hash,
            metadata=(
                (
                    "source_classification",
                    "SIMULATED",
                ),
                (
                    "stochastic_model",
                    "normalized-dY-over-dt-v1",
                ),
            ),
        )

        validate_adapter_record(
            adapter=self,
            command=command,
            record=record,
        )

        return record
