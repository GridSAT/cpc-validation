import dataclasses
import json

import pytest

from src.n0_raw_record import (
    N0RawRecord,
    canonical_json_value,
    synthetic_sample_payload_hash,
)


SHA_A = "sha256:" + "a" * 64
SHA_B = "sha256:" + "b" * 64


def make_record(**overrides):
    signal_i = (0.1, 0.2, 0.3, 0.4)
    signal_q = (0.0, 0.1, 0.0, -0.1)
    reference_i = (1.0, 1.0, 1.0, 1.0)
    reference_q = (0.0, 0.0, 0.0, 0.0)

    values = {
        "experiment_id": "N0-SYNTHETIC-REHEARSAL-v1",
        "trial_id": "trial-000001",
        "profile_id": "CPC-SHOR-N0-PHYSICAL-PROFILE-v1",
        "apparatus_id": "SIMULATED-CAT-DEVICE-v1",
        "controller_id": "SIMULATED-N0-CONTROLLER-v1",
        "firmware_control_id": "SIMULATED-CONTROL-v1",
        "calibration_id": "SIMULATED-CALIBRATION-v1",
        "reference_id": "SIMULATED-REFERENCE-v1",
        "role": "operational",
        "sample_period_s": 0.01,
        "sample_count": 4,
        "acquisition_start_s": 0.0,
        "acquisition_end_s": 0.04,
        "burn_in_start_index": 0,
        "burn_in_end_index": 1,
        "command_phase_rad": 0.0,
        "preparation_command_hash": SHA_A,
        "probe_configuration_hash": SHA_B,
        "signal_i": signal_i,
        "signal_q": signal_q,
        "reference_i": reference_i,
        "reference_q": reference_q,
        "clipping_flags": (False, False, False, False),
        "saturation_flags": (False, False, False, False),
        "dropped_sample_flags": (False, False, False, False),
        "timestamp_discontinuity_flags": (
            False,
            False,
            False,
            False,
        ),
        "reset_status": "ok",
        "acquisition_status": "complete",
        "realization_status": "simulated",
        "timebase_id": "SIMULATED-MODEL-TIMEBASE-v1",
        "raw_payload_provenance": (
            "synthetic-canonical-sample-payload"
        ),
        "original_bytes_sha256": (
            synthetic_sample_payload_hash(
                signal_i=signal_i,
                signal_q=signal_q,
                reference_i=reference_i,
                reference_q=reference_q,
            )
        ),
        "metadata": (
            ("mode", "deterministic-test-fixture"),
        ),
    }

    values.update(overrides)
    return N0RawRecord(**values)


def test_valid_record_is_immutable():
    record = make_record()

    with pytest.raises(
        dataclasses.FrozenInstanceError
    ):
        record.trial_id = "changed"


def test_record_hash_is_deterministic():
    first = make_record()
    second = make_record()

    assert first.record_hash == second.record_hash
    assert first.canonical_json == second.canonical_json


def test_record_contains_no_truth_field():
    data = json.loads(
        make_record().canonical_json
    )

    forbidden = {
        "theta",
        "theta_truth",
        "truth_phase",
        "expected_phase",
        "semantic_answer",
        "expected_order",
    }

    assert forbidden.isdisjoint(data)


@pytest.mark.parametrize(
    "key",
    (
        "theta",
        "truth_phase",
        "expected_phase",
        "semantic_answer",
        "expected_order",
    ),
)
def test_metadata_rejects_truth_fields(key):
    with pytest.raises(
        ValueError,
        match="forbidden truth",
    ):
        make_record(
            metadata=(
                (key, 1),
            )
        )


def test_preparation_identity_is_opaque_hash():
    with pytest.raises(
        ValueError,
        match="sha256",
    ):
        make_record(
            preparation_command_hash="theta=0.25"
        )


def test_sample_lengths_must_match_sample_count():
    with pytest.raises(
        ValueError,
        match="length",
    ):
        make_record(
            signal_i=(0.1, 0.2),
        )


def test_flag_lengths_must_match_sample_count():
    with pytest.raises(
        ValueError,
        match="length",
    ):
        make_record(
            clipping_flags=(False,),
        )


def test_nan_samples_are_rejected():
    with pytest.raises(
        ValueError,
        match="finite",
    ):
        make_record(
            signal_i=(0.1, float("nan"), 0.3, 0.4),
        )


def test_invalid_burn_in_bounds_are_rejected():
    with pytest.raises(
        ValueError,
        match="burn-in",
    ):
        make_record(
            burn_in_start_index=0,
            burn_in_end_index=5,
        )


def test_canonical_semantics_ignore_tuple_list_representation():
    tuple_form = {
        "samples": (1.0, 2.0),
        "flags": (False, True),
    }

    list_form = {
        "samples": [1.0, 2.0],
        "flags": [False, True],
    }

    assert (
        canonical_json_value(tuple_form)
        == canonical_json_value(list_form)
    )
