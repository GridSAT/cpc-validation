import inspect
import math

import pytest

from src.n0_calibration import (
    build_simulated_n0_calibration,
)
from src.n0_raw_record import (
    N0RawRecord,
    synthetic_sample_payload_hash,
)
from src.n0_reducer import (
    FORBIDDEN_REDUCER_PARAMETER_NAMES,
    reduce_n0_records,
)


SHA_A = "sha256:" + "a" * 64
SHA_B = "sha256:" + "b" * 64


def make_record(
    *,
    trial_id,
    phase,
    signal,
    invalid=False,
):
    n = 4

    signal_i = (signal,) * n
    signal_q = (0.0,) * n
    reference_i = (1.0,) * n
    reference_q = (0.0,) * n

    flags = (
        (False, True, False, False)
        if invalid
        else (False,) * n
    )

    return N0RawRecord(
        experiment_id="N0-SYNTHETIC-REHEARSAL-v1",
        trial_id=trial_id,
        profile_id="CPC-SHOR-N0-PHYSICAL-PROFILE-v1",
        apparatus_id="SIMULATED-CAT-DEVICE-v1",
        controller_id="SIMULATED-N0-CONTROLLER-v1",
        firmware_control_id="SIMULATED-CONTROL-v1",
        calibration_id="SIMULATED-CALIBRATION-v1",
        reference_id="SIMULATED-REFERENCE-v1",
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
        clipping_flags=flags,
        saturation_flags=(False,) * n,
        dropped_sample_flags=(False,) * n,
        timestamp_discontinuity_flags=(False,) * n,
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


def test_reducer_public_api_contains_no_truth_parameters():
    parameters = set(
        inspect.signature(
            reduce_n0_records
        ).parameters
    )

    assert (
        parameters
        & FORBIDDEN_REDUCER_PARAMETER_NAMES
        == set()
    )


def test_reducer_recovers_zero_phase():
    calibration = build_simulated_n0_calibration()

    records = (
        make_record(
            trial_id="x",
            phase=0.0,
            signal=1.0,
        ),
        make_record(
            trial_id="y",
            phase=math.pi / 2.0,
            signal=0.0,
        ),
    )

    result = reduce_n0_records(
        records=records,
        calibration=calibration,
    )

    assert result.status == "ok"
    assert math.isclose(
        result.estimated_phase_rad,
        0.0,
        abs_tol=1.0e-15,
    )


def test_reducer_recovers_pi_over_two():
    calibration = build_simulated_n0_calibration()

    records = (
        make_record(
            trial_id="x",
            phase=0.0,
            signal=0.0,
        ),
        make_record(
            trial_id="y",
            phase=math.pi / 2.0,
            signal=1.0,
        ),
    )

    result = reduce_n0_records(
        records=records,
        calibration=calibration,
    )

    assert result.status == "ok"
    assert math.isclose(
        result.estimated_phase_rad,
        math.pi / 2.0,
        abs_tol=1.0e-15,
    )


def test_reducer_recovers_quadrant_phase():
    calibration = build_simulated_n0_calibration()

    root = math.sqrt(0.5)

    records = (
        make_record(
            trial_id="x",
            phase=0.0,
            signal=root,
        ),
        make_record(
            trial_id="y",
            phase=math.pi / 2.0,
            signal=root,
        ),
    )

    result = reduce_n0_records(
        records=records,
        calibration=calibration,
    )

    assert result.status == "ok"
    assert math.isclose(
        result.estimated_phase_rad,
        math.pi / 4.0,
        abs_tol=1.0e-15,
    )


def test_invalid_record_is_excluded_and_counted():
    calibration = build_simulated_n0_calibration()

    records = (
        make_record(
            trial_id="x-good",
            phase=0.0,
            signal=1.0,
        ),
        make_record(
            trial_id="x-bad",
            phase=0.0,
            signal=-100.0,
            invalid=True,
        ),
        make_record(
            trial_id="y",
            phase=math.pi / 2.0,
            signal=0.0,
        ),
    )

    result = reduce_n0_records(
        records=records,
        calibration=calibration,
    )

    assert result.status == "ok"
    assert result.invalid_record_count == 1
    assert result.valid_record_count == 2
    assert math.isclose(
        result.estimated_phase_rad,
        0.0,
        abs_tol=1.0e-15,
    )


def test_missing_valid_quadrature_fails_closed():
    calibration = build_simulated_n0_calibration()

    records = (
        make_record(
            trial_id="x",
            phase=0.0,
            signal=1.0,
        ),
    )

    result = reduce_n0_records(
        records=records,
        calibration=calibration,
    )

    assert result.status == "invalid"
    assert result.estimated_phase_rad is None


def test_reduction_is_deterministic():
    calibration = build_simulated_n0_calibration()

    records = (
        make_record(
            trial_id="x",
            phase=0.0,
            signal=0.3,
        ),
        make_record(
            trial_id="y",
            phase=math.pi / 2.0,
            signal=0.4,
        ),
    )

    first = reduce_n0_records(
        records=records,
        calibration=calibration,
    )

    second = reduce_n0_records(
        records=records,
        calibration=calibration,
    )

    assert (
        first.reduction_hash
        == second.reduction_hash
    )

    assert (
        first.canonical_json
        == second.canonical_json
    )


def test_profile_mismatch_is_rejected():
    calibration = build_simulated_n0_calibration()

    record = make_record(
        trial_id="x",
        phase=0.0,
        signal=1.0,
    )

    bad = N0RawRecord(
        **{
            **record.__dict__,
            "profile_id": "wrong-profile",
        }
    )

    with pytest.raises(
        ValueError,
        match="profile mismatch",
    ):
        reduce_n0_records(
            records=(bad,),
            calibration=calibration,
        )
