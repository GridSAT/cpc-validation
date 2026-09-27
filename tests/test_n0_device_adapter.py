import pytest

from src.n0_calibration import (
    build_simulated_n0_calibration,
)
from src.n0_device_adapter import (
    N0DeviceAdapter,
    N0TrialCommand,
    validate_adapter_record,
)
from src.n0_physical_profile import (
    build_default_n0_physical_profile,
)
from src.n0_raw_record import (
    N0RawRecord,
    synthetic_sample_payload_hash,
)


SHA_A = "sha256:" + "a" * 64
SHA_B = "sha256:" + "b" * 64


class FixtureAdapter(N0DeviceAdapter):
    def acquire(
        self,
        command: N0TrialCommand,
    ) -> N0RawRecord:
        n = command.sample_count

        signal_i = tuple(
            0.1 * index
            for index in range(n)
        )
        signal_q = tuple(
            0.0
            for _ in range(n)
        )
        reference_i = tuple(
            1.0
            for _ in range(n)
        )
        reference_q = tuple(
            0.0
            for _ in range(n)
        )

        record = N0RawRecord(
            experiment_id=command.experiment_id,
            trial_id=command.trial_id,
            profile_id=self.profile.profile_id,
            apparatus_id=self.device_id,
            controller_id="SIMULATED-N0-CONTROLLER-v1",
            firmware_control_id="SIMULATED-CONTROL-v1",
            calibration_id=(
                self.calibration.calibration_id
            ),
            reference_id="SIMULATED-REFERENCE-v1",
            role=command.role,
            sample_period_s=0.01,
            sample_count=n,
            acquisition_start_s=0.0,
            acquisition_end_s=0.01 * n,
            burn_in_start_index=0,
            burn_in_end_index=0,
            command_phase_rad=command.command_phase_rad,
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
            clipping_flags=(False,) * n,
            saturation_flags=(False,) * n,
            dropped_sample_flags=(False,) * n,
            timestamp_discontinuity_flags=(
                (False,) * n
            ),
            reset_status="ok",
            acquisition_status="complete",
            realization_status="simulated",
            timebase_id="SIMULATED-MODEL-TIMEBASE-v1",
            raw_payload_provenance=(
                "synthetic-canonical-sample-payload"
            ),
            original_bytes_sha256=(
                synthetic_sample_payload_hash(
                    signal_i=signal_i,
                    signal_q=signal_q,
                    reference_i=reference_i,
                    reference_q=reference_q,
                )
            ),
        )

        validate_adapter_record(
            adapter=self,
            command=command,
            record=record,
        )

        return record


def build_adapter():
    return FixtureAdapter(
        profile=build_default_n0_physical_profile(),
        calibration=build_simulated_n0_calibration(),
        device_id="SIMULATED-CAT-DEVICE-v1",
        realization_status="simulated",
    )


def build_command():
    return N0TrialCommand(
        experiment_id="N0-SYNTHETIC-REHEARSAL-v1",
        trial_id="trial-000001",
        role="operational",
        command_phase_rad=0.0,
        preparation_command_hash=SHA_A,
        probe_configuration_hash=SHA_B,
        sample_count=4,
    )


def test_common_adapter_returns_raw_record():
    adapter = build_adapter()
    command = build_command()

    record = adapter.acquire(command)

    assert isinstance(record, N0RawRecord)
    assert record.trial_id == command.trial_id
    assert record.profile_id == adapter.profile.profile_id


def test_adapter_rejects_profile_calibration_mismatch():
    profile = build_default_n0_physical_profile()
    calibration = build_simulated_n0_calibration()

    bad = type(calibration)(
        calibration_id=calibration.calibration_id,
        profile_id="other-profile",
        realization_status=calibration.realization_status,
        valid_from=calibration.valid_from,
        valid_until=calibration.valid_until,
        values=calibration.values,
    )

    with pytest.raises(
        ValueError,
        match="calibration/profile",
    ):
        FixtureAdapter(
            profile=profile,
            calibration=bad,
            device_id="device",
            realization_status="simulated",
        )


def test_adapter_rejects_realization_mismatch():
    profile = build_default_n0_physical_profile()
    calibration = build_simulated_n0_calibration()

    with pytest.raises(
        ValueError,
        match="realization mismatch",
    ):
        FixtureAdapter(
            profile=profile,
            calibration=calibration,
            device_id="device",
            realization_status="physical",
        )


def test_record_binding_detects_trial_substitution():
    adapter = build_adapter()
    command = build_command()
    record = adapter.acquire(command)

    wrong = N0TrialCommand(
        experiment_id=command.experiment_id,
        trial_id="trial-999999",
        role=command.role,
        command_phase_rad=command.command_phase_rad,
        preparation_command_hash=(
            command.preparation_command_hash
        ),
        probe_configuration_hash=(
            command.probe_configuration_hash
        ),
        sample_count=command.sample_count,
    )

    with pytest.raises(
        ValueError,
        match="trial identity",
    ):
        validate_adapter_record(
            adapter=adapter,
            command=wrong,
            record=record,
        )


def test_record_binding_detects_phase_substitution():
    adapter = build_adapter()
    command = build_command()
    record = adapter.acquire(command)

    wrong = N0TrialCommand(
        experiment_id=command.experiment_id,
        trial_id=command.trial_id,
        role=command.role,
        command_phase_rad=1.0,
        preparation_command_hash=(
            command.preparation_command_hash
        ),
        probe_configuration_hash=(
            command.probe_configuration_hash
        ),
        sample_count=command.sample_count,
    )

    with pytest.raises(
        ValueError,
        match="command phase",
    ):
        validate_adapter_record(
            adapter=adapter,
            command=wrong,
            record=record,
        )


def test_adapter_interface_has_no_truth_argument():
    import inspect

    parameters = set(
        inspect.signature(
            N0DeviceAdapter.acquire
        ).parameters
    )

    forbidden = {
        "expected_order",
        "expected_phase",
        "semantic_answer",
        "theta_truth",
        "truth_phase",
    }

    assert forbidden.isdisjoint(parameters)
