import inspect
import math

import pytest

from src.n0_device_adapter import (
    N0TrialCommand,
)
from src.n0_reducer import (
    reduce_n0_records,
)
from src.n0_synthetic_device import (
    SyntheticN0Device,
    SyntheticPreparation,
    derive_trial_seed,
    opaque_preparation_hash,
)


ROOT_COMMITMENT = (
    "sha256:"
    + "1" * 64
)

PROBE_HASH = (
    "sha256:"
    + "2" * 64
)


def build_preparations():
    return (
        SyntheticPreparation(
            preparation_command_hash=(
                opaque_preparation_hash(
                    "phase-zero"
                )
            ),
            theta_rad=0.0,
        ),
        SyntheticPreparation(
            preparation_command_hash=(
                opaque_preparation_hash(
                    "phase-pi-over-two"
                )
            ),
            theta_rad=math.pi / 2.0,
        ),
        SyntheticPreparation(
            preparation_command_hash=(
                opaque_preparation_hash(
                    "phase-pi-over-four"
                )
            ),
            theta_rad=math.pi / 4.0,
        ),
    )


def build_device():
    return SyntheticN0Device(
        root_seed_commitment=ROOT_COMMITMENT,
        preparations=build_preparations(),
    )


def make_command(
    *,
    trial_id,
    beta,
    preparation_hash,
    sample_count=4096,
):
    return N0TrialCommand(
        experiment_id="N0-SYNTHETIC-REHEARSAL-v1",
        trial_id=trial_id,
        role="operational",
        command_phase_rad=beta,
        preparation_command_hash=(
            preparation_hash
        ),
        probe_configuration_hash=(
            PROBE_HASH
        ),
        sample_count=sample_count,
    )


def test_trial_seed_is_deterministic():
    first = derive_trial_seed(
        root_seed_commitment=ROOT_COMMITMENT,
        experiment_id="experiment",
        trial_id="trial",
        command_phase_rad=0.0,
    )

    second = derive_trial_seed(
        root_seed_commitment=ROOT_COMMITMENT,
        experiment_id="experiment",
        trial_id="trial",
        command_phase_rad=0.0,
    )

    assert first == second


def test_trial_seed_changes_with_trial_identity():
    first = derive_trial_seed(
        root_seed_commitment=ROOT_COMMITMENT,
        experiment_id="experiment",
        trial_id="trial-a",
        command_phase_rad=0.0,
    )

    second = derive_trial_seed(
        root_seed_commitment=ROOT_COMMITMENT,
        experiment_id="experiment",
        trial_id="trial-b",
        command_phase_rad=0.0,
    )

    assert first != second


def test_trial_seed_changes_with_command_phase():
    first = derive_trial_seed(
        root_seed_commitment=ROOT_COMMITMENT,
        experiment_id="experiment",
        trial_id="trial",
        command_phase_rad=0.0,
    )

    second = derive_trial_seed(
        root_seed_commitment=ROOT_COMMITMENT,
        experiment_id="experiment",
        trial_id="trial",
        command_phase_rad=math.pi / 2.0,
    )

    assert first != second


def test_same_commitment_fresh_devices_reproduce_record():
    preparation_hash = (
        opaque_preparation_hash(
            "phase-zero"
        )
    )

    command = make_command(
        trial_id="trial-x",
        beta=0.0,
        preparation_hash=preparation_hash,
        sample_count=64,
    )

    first_device = build_device()
    second_device = build_device()

    first = first_device.acquire(
        command
    )

    second = second_device.acquire(
        command
    )

    assert (
        first.canonical_json
        == second.canonical_json
    )

    assert (
        first.record_hash
        == second.record_hash
    )


def test_trial_identity_cannot_be_retried():
    device = build_device()

    preparation_hash = (
        opaque_preparation_hash(
            "phase-zero"
        )
    )

    command = make_command(
        trial_id="trial-once",
        beta=0.0,
        preparation_hash=preparation_hash,
        sample_count=16,
    )

    device.acquire(
        command
    )

    with pytest.raises(
        RuntimeError,
        match="already consumed",
    ):
        device.acquire(
            command
        )


def test_unknown_preparation_consumes_trial_identity():
    device = build_device()

    command = make_command(
        trial_id="bad-preparation",
        beta=0.0,
        preparation_hash=(
            "sha256:"
            + "f" * 64
        ),
        sample_count=16,
    )

    with pytest.raises(
        ValueError,
        match="unknown preparation",
    ):
        device.acquire(
            command
        )

    with pytest.raises(
        RuntimeError,
        match="already consumed",
    ):
        device.acquire(
            command
        )


def test_raw_record_contains_no_theta_truth():
    device = build_device()

    preparation_hash = (
        opaque_preparation_hash(
            "phase-pi-over-four"
        )
    )

    command = make_command(
        trial_id="truth-firewall",
        beta=0.0,
        preparation_hash=preparation_hash,
        sample_count=32,
    )

    record = device.acquire(
        command
    )

    serialized = record.canonical_json.lower()

    assert "theta_truth" not in serialized
    assert "truth_phase" not in serialized
    assert "expected_phase" not in serialized
    assert "semantic_answer" not in serialized


def test_synthetic_device_is_simulated_only():
    device = build_device()

    assert (
        device.realization_status
        == "simulated"
    )

    assert (
        device.profile.realization_status
        == "simulated"
    )

    assert (
        device.calibration.realization_status
        == "simulated"
    )


def test_acquire_api_contains_no_truth_argument():
    parameters = set(
        inspect.signature(
            SyntheticN0Device.acquire
        ).parameters
    )

    forbidden = {
        "theta",
        "theta_truth",
        "truth_phase",
        "expected_phase",
        "semantic_answer",
        "expected_order",
    }

    assert forbidden.isdisjoint(
        parameters
    )


def test_zero_phase_reduces_near_zero():
    device = build_device()

    preparation_hash = (
        opaque_preparation_hash(
            "phase-zero"
        )
    )

    x_record = device.acquire(
        make_command(
            trial_id="phase-zero-x",
            beta=0.0,
            preparation_hash=(
                preparation_hash
            ),
        )
    )

    y_record = device.acquire(
        make_command(
            trial_id="phase-zero-y",
            beta=math.pi / 2.0,
            preparation_hash=(
                preparation_hash
            ),
        )
    )

    result = reduce_n0_records(
        records=(
            x_record,
            y_record,
        ),
        calibration=device.calibration,
    )

    assert result.status == "ok"

    phase = result.estimated_phase_rad

    assert phase is not None

    circular_error = min(
        abs(phase),
        abs(
            phase
            - 2.0 * math.pi
        ),
    )

    assert circular_error < 0.35


def test_pi_over_two_phase_reduces_near_pi_over_two():
    device = build_device()

    preparation_hash = (
        opaque_preparation_hash(
            "phase-pi-over-two"
        )
    )

    x_record = device.acquire(
        make_command(
            trial_id="phase-pi2-x",
            beta=0.0,
            preparation_hash=(
                preparation_hash
            ),
        )
    )

    y_record = device.acquire(
        make_command(
            trial_id="phase-pi2-y",
            beta=math.pi / 2.0,
            preparation_hash=(
                preparation_hash
            ),
        )
    )

    result = reduce_n0_records(
        records=(
            x_record,
            y_record,
        ),
        calibration=device.calibration,
    )

    assert result.status == "ok"

    phase = result.estimated_phase_rad

    assert phase is not None

    assert abs(
        phase
        - math.pi / 2.0
    ) < 0.35


def test_pi_over_four_phase_reduces_near_pi_over_four():
    device = build_device()

    preparation_hash = (
        opaque_preparation_hash(
            "phase-pi-over-four"
        )
    )

    x_record = device.acquire(
        make_command(
            trial_id="phase-pi4-x",
            beta=0.0,
            preparation_hash=(
                preparation_hash
            ),
        )
    )

    y_record = device.acquire(
        make_command(
            trial_id="phase-pi4-y",
            beta=math.pi / 2.0,
            preparation_hash=(
                preparation_hash
            ),
        )
    )

    result = reduce_n0_records(
        records=(
            x_record,
            y_record,
        ),
        calibration=device.calibration,
    )

    assert result.status == "ok"

    phase = result.estimated_phase_rad

    assert phase is not None

    assert abs(
        phase
        - math.pi / 4.0
    ) < 0.35
