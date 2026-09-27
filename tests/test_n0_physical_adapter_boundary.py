import dataclasses
import math

import pytest

from src.n0_calibration import (
    N0Calibration,
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
    SIMULATED_TIMEBASE_ID,
    native_instrument_bytes_hash,
    synthetic_sample_payload_hash,
)
from src.n0_reducer import (
    reduce_n0_records,
)


SHA_A = "sha256:" + "a" * 64
SHA_B = "sha256:" + "b" * 64


def make_record(
    *,
    trial_id="trial",
    phase=0.0,
    signal=1.0,
    realization_status="simulated",
    profile_id="CPC-SHOR-N0-PHYSICAL-PROFILE-v1",
    calibration_id="SIMULATED-CALIBRATION-v1",
    apparatus_id="SIMULATED-CAT-DEVICE-v1",
    timebase_id=SIMULATED_TIMEBASE_ID,
    raw_payload_provenance=(
        "synthetic-canonical-sample-payload"
    ),
    reset_status="ok",
):
    n = 4

    signal_i = (signal,) * n
    signal_q = (0.0,) * n
    reference_i = (1.0,) * n
    reference_q = (0.0,) * n

    if raw_payload_provenance == (
        "native-instrument-bytes"
    ):
        raw_hash = native_instrument_bytes_hash(
            (
                f"{trial_id}|{phase}|{signal}"
            ).encode("ascii")
        )
    else:
        raw_hash = synthetic_sample_payload_hash(
            signal_i=signal_i,
            signal_q=signal_q,
            reference_i=reference_i,
            reference_q=reference_q,
        )

    return N0RawRecord(
        experiment_id="N0-BOUNDARY-TEST-v1",
        trial_id=trial_id,
        profile_id=profile_id,
        apparatus_id=apparatus_id,
        controller_id="CONTROLLER-v1",
        firmware_control_id="CONTROL-v1",
        calibration_id=calibration_id,
        reference_id="REFERENCE-v1",
        role="operational",
        sample_period_s=0.01,
        sample_count=n,
        acquisition_start_s=0.0,
        acquisition_end_s=0.04,
        burn_in_start_index=0,
        burn_in_end_index=0,
        command_phase_rad=phase,
        preparation_command_hash=SHA_A,
        probe_configuration_hash=SHA_B,
        signal_i=signal_i,
        signal_q=signal_q,
        reference_i=reference_i,
        reference_q=reference_q,
        clipping_flags=(False,) * n,
        saturation_flags=(False,) * n,
        dropped_sample_flags=(False,) * n,
        timestamp_discontinuity_flags=(False,) * n,
        reset_status=reset_status,
        acquisition_status="complete",
        realization_status=realization_status,
        timebase_id=timebase_id,
        raw_payload_provenance=(
            raw_payload_provenance
        ),
        original_bytes_sha256=raw_hash,
    )


def build_physical_calibration(
    *,
    profile_id=(
        "CPC-SHOR-N0-FUTURE-PHYSICAL-PROFILE-v1"
    ),
):
    simulated = (
        build_simulated_n0_calibration()
    )

    physical_values = tuple(
        dataclasses.replace(
            value,
            evidence_id=(
                "physical:test:"
                + value.name
            ),
        )
        for value in simulated.values
    )

    return N0Calibration(
        calibration_id="PHYSICAL-CALIBRATION-TEST-v1",
        profile_id=profile_id,
        realization_status="physical",
        valid_from="PHYSICAL-TEST-BEGIN",
        valid_until="PHYSICAL-TEST-END",
        values=physical_values,
    )


class NoopAdapter(N0DeviceAdapter):
    def acquire(self, command):
        raise NotImplementedError


def test_reset_validity_is_source_independent():
    good = make_record(
        reset_status="ok"
    )

    bad = make_record(
        reset_status="failed"
    )

    assert good.reset_valid is True
    assert bad.reset_valid is False


def test_unknown_reset_status_is_rejected():
    with pytest.raises(
        ValueError,
        match="reset_status",
    ):
        make_record(
            reset_status="simulated-reset-ok"
        )


def test_trial_command_rejects_unknown_role():
    with pytest.raises(
        ValueError,
        match="role must be one of",
    ):
        N0TrialCommand(
            experiment_id="experiment",
            trial_id="trial",
            role="secret_truth_trial",
            command_phase_rad=0.0,
            preparation_command_hash=SHA_A,
            probe_configuration_hash=SHA_B,
            sample_count=4,
        )


def test_simulated_record_cannot_claim_native_bytes():
    with pytest.raises(
        ValueError,
        match="synthetic payload provenance",
    ):
        make_record(
            raw_payload_provenance=(
                "native-instrument-bytes"
            ),
        )


def test_physical_record_requires_native_bytes():
    with pytest.raises(
        ValueError,
        match="native instrument-byte provenance",
    ):
        make_record(
            realization_status="physical",
            profile_id="FUTURE-PHYSICAL-PROFILE-v1",
            calibration_id="PHYSICAL-CAL-v1",
            apparatus_id="PHYSICAL-DEVICE-v1",
            timebase_id="PHYSICAL-TIMEBASE-v1",
            raw_payload_provenance=(
                "synthetic-canonical-sample-payload"
            ),
        )


def test_physical_record_rejects_simulated_timebase():
    with pytest.raises(
        ValueError,
        match="simulated timebase",
    ):
        make_record(
            realization_status="physical",
            profile_id="FUTURE-PHYSICAL-PROFILE-v1",
            calibration_id="PHYSICAL-CAL-v1",
            apparatus_id="PHYSICAL-DEVICE-v1",
            timebase_id=SIMULATED_TIMEBASE_ID,
            raw_payload_provenance=(
                "native-instrument-bytes"
            ),
        )


def test_native_instrument_hash_is_exact_byte_hash():
    first = native_instrument_bytes_hash(
        b"\x00\x01\x02\x03"
    )

    second = native_instrument_bytes_hash(
        b"\x00\x01\x02\x03"
    )

    changed = native_instrument_bytes_hash(
        b"\x00\x01\x02\x04"
    )

    assert first == second
    assert first != changed


def test_simulated_adapter_rejects_physical_record():
    profile = (
        build_default_n0_physical_profile()
    )

    calibration = (
        build_simulated_n0_calibration()
    )

    adapter = NoopAdapter(
        profile=profile,
        calibration=calibration,
        device_id="SIMULATED-CAT-DEVICE-v1",
        realization_status="simulated",
    )

    command = N0TrialCommand(
        experiment_id="N0-BOUNDARY-TEST-v1",
        trial_id="trial",
        role="operational",
        command_phase_rad=0.0,
        preparation_command_hash=SHA_A,
        probe_configuration_hash=SHA_B,
        sample_count=4,
    )

    physical_record = make_record(
        trial_id="trial",
        realization_status="physical",
        profile_id=profile.profile_id,
        calibration_id=calibration.calibration_id,
        apparatus_id=adapter.device_id,
        timebase_id="PHYSICAL-TIMEBASE-v1",
        raw_payload_provenance=(
            "native-instrument-bytes"
        ),
    )

    with pytest.raises(
        ValueError,
        match="realization mismatch",
    ):
        validate_adapter_record(
            adapter=adapter,
            command=command,
            record=physical_record,
        )


def test_physical_adapter_cannot_reuse_simulation_only_profile():
    profile = (
        build_default_n0_physical_profile()
    )

    calibration = build_physical_calibration(
        profile_id=profile.profile_id
    )

    with pytest.raises(
        ValueError,
        match="device/profile realization mismatch",
    ):
        NoopAdapter(
            profile=profile,
            calibration=calibration,
            device_id="PHYSICAL-DEVICE-v1",
            realization_status="physical",
        )


def test_same_reducer_accepts_future_physical_record_contract():
    profile_id = (
        "CPC-SHOR-N0-FUTURE-PHYSICAL-PROFILE-v1"
    )

    calibration = build_physical_calibration(
        profile_id=profile_id
    )

    records = (
        make_record(
            trial_id="physical-x",
            phase=0.0,
            signal=1.0,
            realization_status="physical",
            profile_id=profile_id,
            calibration_id=calibration.calibration_id,
            apparatus_id="PHYSICAL-DEVICE-v1",
            timebase_id="PHYSICAL-TIMEBASE-v1",
            raw_payload_provenance=(
                "native-instrument-bytes"
            ),
        ),
        make_record(
            trial_id="physical-y",
            phase=math.pi / 2.0,
            signal=0.0,
            realization_status="physical",
            profile_id=profile_id,
            calibration_id=calibration.calibration_id,
            apparatus_id="PHYSICAL-DEVICE-v1",
            timebase_id="PHYSICAL-TIMEBASE-v1",
            raw_payload_provenance=(
                "native-instrument-bytes"
            ),
        ),
    )

    result = reduce_n0_records(
        records=records,
        calibration=calibration,
    )

    assert result.status == "ok"
    assert result.estimated_phase_rad is not None

    assert math.isclose(
        result.estimated_phase_rad,
        0.0,
        abs_tol=1.0e-15,
    )
