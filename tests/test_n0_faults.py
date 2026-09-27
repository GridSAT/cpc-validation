import math

import pytest

from src.n0_device_adapter import (
    N0TrialCommand,
)
from src.n0_faults import (
    fault_record,
    inject_clipping,
    inject_dropped_sample,
    inject_probe_disabled,
    inject_reference_drift,
    inject_reference_phase_error,
    inject_reset_failure,
    inject_signal_label_swap,
    inject_timestamp_discontinuity,
)
from src.n0_reducer import (
    reduce_n0_records,
)
from src.n0_synthetic_device import (
    SyntheticN0Device,
    SyntheticPreparation,
    opaque_preparation_hash,
)


ROOT_COMMITMENT = (
    "sha256:"
    + "3" * 64
)

PROBE_HASH = (
    "sha256:"
    + "4" * 64
)

PREPARATION_HASH = (
    opaque_preparation_hash(
        "fault-test-pi-over-four"
    )
)


def build_device():
    return SyntheticN0Device(
        root_seed_commitment=ROOT_COMMITMENT,
        preparations=(
            SyntheticPreparation(
                preparation_command_hash=(
                    PREPARATION_HASH
                ),
                theta_rad=math.pi / 4.0,
            ),
        ),
    )


def acquire_pair():
    device = build_device()

    x_record = device.acquire(
        N0TrialCommand(
            experiment_id="N0-FAULT-TEST-v1",
            trial_id="x",
            role="negative_control",
            command_phase_rad=0.0,
            preparation_command_hash=(
                PREPARATION_HASH
            ),
            probe_configuration_hash=(
                PROBE_HASH
            ),
            sample_count=4096,
        )
    )

    y_record = device.acquire(
        N0TrialCommand(
            experiment_id="N0-FAULT-TEST-v1",
            trial_id="y",
            role="negative_control",
            command_phase_rad=math.pi / 2.0,
            preparation_command_hash=(
                PREPARATION_HASH
            ),
            probe_configuration_hash=(
                PROBE_HASH
            ),
            sample_count=4096,
        )
    )

    return (
        device,
        x_record,
        y_record,
    )


def test_probe_disabled_changes_raw_hash():
    _, record, _ = acquire_pair()

    faulted = inject_probe_disabled(
        record
    )

    assert (
        faulted.original_bytes_sha256
        != record.original_bytes_sha256
    )

    assert set(
        faulted.signal_i
    ) == {
        0.0
    }


def test_clipping_causes_record_exclusion():
    device, x_record, y_record = acquire_pair()

    faulted_x = inject_clipping(
        x_record
    )

    result = reduce_n0_records(
        records=(
            faulted_x,
            y_record,
        ),
        calibration=device.calibration,
    )

    assert result.status == "invalid"
    assert result.invalid_record_count == 1


def test_dropped_sample_causes_record_exclusion():
    device, x_record, y_record = acquire_pair()

    faulted_x = inject_dropped_sample(
        x_record
    )

    result = reduce_n0_records(
        records=(
            faulted_x,
            y_record,
        ),
        calibration=device.calibration,
    )

    assert result.status == "invalid"


def test_timestamp_discontinuity_causes_exclusion():
    device, x_record, y_record = acquire_pair()

    faulted_x = inject_timestamp_discontinuity(
        x_record
    )

    result = reduce_n0_records(
        records=(
            faulted_x,
            y_record,
        ),
        calibration=device.calibration,
    )

    assert result.status == "invalid"


def test_reset_failure_causes_record_exclusion():
    device, x_record, y_record = acquire_pair()

    faulted_x = inject_reset_failure(
        x_record
    )

    result = reduce_n0_records(
        records=(
            faulted_x,
            y_record,
        ),
        calibration=device.calibration,
    )

    assert result.status == "invalid"


def test_reference_phase_error_rotates_reference():
    _, record, _ = acquire_pair()

    faulted = inject_reference_phase_error(
        record,
        phase_error_rad=math.pi / 2.0,
    )

    assert (
        faulted.original_bytes_sha256
        != record.original_bytes_sha256
    )

    assert not (
        faulted.reference_i
        == record.reference_i
    )

    assert not (
        faulted.reference_q
        == record.reference_q
    )


def test_reference_drift_changes_reference_mean():
    _, record, _ = acquire_pair()

    faulted = inject_reference_drift(
        record,
        additive_drift=0.5,
    )

    before = sum(
        record.reference_i
    ) / record.sample_count

    after = sum(
        faulted.reference_i
    ) / faulted.sample_count

    assert math.isclose(
        after - before,
        0.5,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )


def test_signal_label_swap_changes_phase_result():
    # Use an asymmetric truth phase. At theta=pi/4 the ideal X and Y
    # quadratures are equal, so exchanging them is nearly symmetry
    # preserving and is not a valid sensitivity test.
    asymmetric_hash = opaque_preparation_hash(
        "fault-test-asymmetric-phase"
    )

    device = SyntheticN0Device(
        root_seed_commitment=ROOT_COMMITMENT,
        preparations=(
            SyntheticPreparation(
                preparation_command_hash=(
                    asymmetric_hash
                ),
                theta_rad=0.20,
            ),
        ),
    )

    x_record = device.acquire(
        N0TrialCommand(
            experiment_id="N0-FAULT-SWAP-TEST-v1",
            trial_id="x",
            role="negative_control",
            command_phase_rad=0.0,
            preparation_command_hash=(
                asymmetric_hash
            ),
            probe_configuration_hash=(
                PROBE_HASH
            ),
            sample_count=4096,
        )
    )

    y_record = device.acquire(
        N0TrialCommand(
            experiment_id="N0-FAULT-SWAP-TEST-v1",
            trial_id="y",
            role="negative_control",
            command_phase_rad=math.pi / 2.0,
            preparation_command_hash=(
                asymmetric_hash
            ),
            probe_configuration_hash=(
                PROBE_HASH
            ),
            sample_count=4096,
        )
    )

    nominal = reduce_n0_records(
        records=(
            x_record,
            y_record,
        ),
        calibration=device.calibration,
    )

    swapped_x, swapped_y = inject_signal_label_swap(
        x_record,
        y_record,
    )

    swapped = reduce_n0_records(
        records=(
            swapped_x,
            swapped_y,
        ),
        calibration=device.calibration,
    )

    assert nominal.status == "ok"
    assert swapped.status == "ok"

    assert nominal.estimated_phase_rad is not None
    assert swapped.estimated_phase_rad is not None

    difference = abs(
        nominal.estimated_phase_rad
        - swapped.estimated_phase_rad
    )

    assert difference > 0.2


def test_probe_disabled_degrades_phase_information():
    device, x_record, y_record = acquire_pair()

    nominal = reduce_n0_records(
        records=(
            x_record,
            y_record,
        ),
        calibration=device.calibration,
    )

    disabled = reduce_n0_records(
        records=(
            inject_probe_disabled(
                x_record
            ),
            inject_probe_disabled(
                y_record
            ),
        ),
        calibration=device.calibration,
    )

    assert nominal.status == "ok"
    assert disabled.status == "ok"

    assert nominal.estimated_phase_rad is not None
    assert disabled.estimated_phase_rad is not None

    nominal_error = abs(
        (
            nominal.estimated_phase_rad
            - math.pi / 4.0
            + math.pi
        )
        % (
            2.0 * math.pi
        )
        - math.pi
    )

    disabled_error = abs(
        (
            disabled.estimated_phase_rad
            - math.pi / 4.0
            + math.pi
        )
        % (
            2.0 * math.pi
        )
        - math.pi
    )

    assert disabled_error > nominal_error


@pytest.mark.parametrize(
    "fault",
    (
        "CLIPPING",
        "DROPPED_SAMPLE",
        "PROBE_DISABLED",
        "REFERENCE_DRIFT",
        "REFERENCE_PHASE_ERROR",
        "RESET_FAILURE",
        "TIMESTAMP_DISCONTINUITY",
    ),
)
def test_fault_dispatch_is_deterministic(fault):
    _, record, _ = acquire_pair()

    first = fault_record(
        record,
        fault=fault,
    )

    second = fault_record(
        record,
        fault=fault,
    )

    assert (
        first.canonical_json
        == second.canonical_json
    )


def test_unknown_fault_is_rejected():
    _, record, _ = acquire_pair()

    with pytest.raises(
        ValueError,
        match="unknown record fault",
    ):
        fault_record(
            record,
            fault="NOT-A-FAULT",
        )


def test_signal_label_swap_requires_pair_api():
    _, record, _ = acquire_pair()

    with pytest.raises(
        ValueError,
        match="requires two records",
    ):
        fault_record(
            record,
            fault="SIGNAL_LABEL_SWAP",
        )
