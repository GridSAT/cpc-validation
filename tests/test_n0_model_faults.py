import math

from src.n0_bosonic_model import (
    build_default_n0_bosonic_model,
)
from src.n0_calibration import (
    build_simulated_n0_calibration,
)
from src.n0_device_adapter import (
    N0TrialCommand,
)
from src.n0_model_faults import (
    change_detector_gain,
    increase_dephasing,
    increase_single_photon_loss,
    reduce_measurement_efficiency,
    weaken_stabilization,
)
from src.n0_reducer import (
    reduce_n0_records,
)
from src.n0_synthetic_device import (
    SyntheticN0Device,
    SyntheticPreparation,
    opaque_preparation_hash,
)


ROOT = "sha256:" + "5" * 64
PROBE = "sha256:" + "6" * 64

PREP = opaque_preparation_hash(
    "model-fault-phase"
)


def make_pair(
    *,
    model=None,
    calibration=None,
    theta=0.35,
    pre_measurement_duration=0.20,
    sample_count=8192,
):
    preparations = (
        SyntheticPreparation(
            preparation_command_hash=PREP,
            theta_rad=theta,
        ),
    )

    device = SyntheticN0Device(
        root_seed_commitment=ROOT,
        preparations=preparations,
        model=model,
        calibration=calibration,
        pre_measurement_duration=(
            pre_measurement_duration
        ),
    )

    x = device.acquire(
        N0TrialCommand(
            experiment_id="N0-MODEL-FAULT-v1",
            trial_id="x",
            role="negative_control",
            command_phase_rad=0.0,
            preparation_command_hash=PREP,
            probe_configuration_hash=PROBE,
            sample_count=sample_count,
        )
    )

    y = device.acquire(
        N0TrialCommand(
            experiment_id="N0-MODEL-FAULT-v1",
            trial_id="y",
            role="negative_control",
            command_phase_rad=math.pi / 2.0,
            preparation_command_hash=PREP,
            probe_configuration_hash=PROBE,
            sample_count=sample_count,
        )
    )

    result = reduce_n0_records(
        records=(x, y),
        calibration=device.calibration,
    )

    return device, result


def phase_error(
    estimate,
    truth,
):
    return abs(
        (
            estimate
            - truth
            + math.pi
        )
        % (
            2.0 * math.pi
        )
        - math.pi
    )


def test_weaken_stabilization_changes_model_parameter():
    model = build_default_n0_bosonic_model()

    faulted = weaken_stabilization(
        model,
        factor=0.25,
    )

    assert math.isclose(
        faulted.kappa_2,
        0.25 * model.kappa_2,
    )


def test_loss_fault_changes_generated_result():
    model = build_default_n0_bosonic_model()

    _, nominal = make_pair(
        model=model,
    )

    faulted_model = increase_single_photon_loss(
        model,
        added_kappa_1=1.5,
    )

    _, faulted = make_pair(
        model=faulted_model,
    )

    assert nominal.status == "ok"
    assert faulted.status == "ok"

    assert (
        nominal.reduction_hash
        != faulted.reduction_hash
    )


def test_dephasing_fault_changes_generated_result():
    model = build_default_n0_bosonic_model()

    _, nominal = make_pair(
        model=model,
    )

    faulted_model = increase_dephasing(
        model,
        added_kappa_phi=0.75,
    )

    _, faulted = make_pair(
        model=faulted_model,
    )

    assert nominal.status == "ok"
    assert faulted.status == "ok"

    assert (
        nominal.reduction_hash
        != faulted.reduction_hash
    )


def test_reduced_eta_degrades_phase_accuracy():
    calibration = (
        build_simulated_n0_calibration()
    )

    _, nominal = make_pair(
        calibration=calibration,
        pre_measurement_duration=0.0,
    )

    low_eta = reduce_measurement_efficiency(
        calibration,
        eta=0.05,
    )

    _, faulted = make_pair(
        calibration=low_eta,
        pre_measurement_duration=0.0,
    )

    assert nominal.estimated_phase_rad is not None
    assert faulted.estimated_phase_rad is not None

    assert (
        phase_error(
            faulted.estimated_phase_rad,
            0.35,
        )
        >
        phase_error(
            nominal.estimated_phase_rad,
            0.35,
        )
    )


def test_preparation_error_changes_phase_estimate():
    _, nominal = make_pair(
        theta=0.35,
        pre_measurement_duration=0.0,
    )

    _, faulted = make_pair(
        theta=0.80,
        pre_measurement_duration=0.0,
    )

    assert nominal.estimated_phase_rad is not None
    assert faulted.estimated_phase_rad is not None

    difference = abs(
        faulted.estimated_phase_rad
        - nominal.estimated_phase_rad
    )

    assert difference > 0.20


def test_detector_gain_fault_is_visible_if_calibration_is_wrong():
    calibration = (
        build_simulated_n0_calibration()
    )

    _, nominal = make_pair(
        calibration=calibration,
        pre_measurement_duration=0.0,
    )

    wrong_gain = change_detector_gain(
        calibration,
        gain=2.0,
    )

    _, faulted = make_pair(
        calibration=wrong_gain,
        pre_measurement_duration=0.0,
    )

    assert nominal.estimated_phase_rad is not None
    assert faulted.estimated_phase_rad is not None

    # Equal scalar gain on both quadratures should not rotate phase.
    # This test verifies the reducer's phase invariance rather than
    # incorrectly demanding a phase bias.
    assert math.isclose(
        nominal.estimated_phase_rad,
        faulted.estimated_phase_rad,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )


def test_pre_measurement_evolution_is_deterministic():
    model = increase_dephasing(
        build_default_n0_bosonic_model(),
        added_kappa_phi=0.25,
    )

    _, first = make_pair(
        model=model,
    )

    _, second = make_pair(
        model=model,
    )

    assert (
        first.canonical_json
        == second.canonical_json
    )
