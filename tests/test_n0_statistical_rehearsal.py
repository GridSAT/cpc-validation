import inspect

import pytest

from src.n0_claim_firewall import (
    N0_FORBIDDEN_NATIVE_OR_PHYSICAL_DECISIONS,
)
from src.n0_statistical_rehearsal import (
    N0_STATISTICAL_REHEARSAL_ID,
    build_synthetic_statistical_preregistration,
    run_n0_statistical_rehearsal,
)


ROOT = (
    "sha256:"
    + "d" * 64
)


@pytest.fixture(scope="module")
def report():
    return run_n0_statistical_rehearsal(
        root_seed_commitment=ROOT,
        repetitions_per_phase=24,
        samples_per_quadrature=1024,
    )


def test_statistical_rehearsal_identity(report):
    assert (
        report.rehearsal_id
        == N0_STATISTICAL_REHEARSAL_ID
    )


def test_repeated_heldout_statistical_gate_passes(report):
    assert (
        report.statistical_decision.status
        == "EQUIVALENCE_ESTABLISHED"
    )

    assert len(
        report.statistical_decision.cells
    ) >= 3

    assert all(
        cell.valid_count == 24
        for cell
        in report.statistical_decision.cells
    )


def test_statistical_negative_control_fails_equivalence(report):
    assert (
        report.negative_statistical_decision.status
        == "EQUIVALENCE_NOT_ESTABLISHED"
    )

    assert (
        report.negative_control_status
        == "NEGATIVE_STATISTICAL_CONTROL_DETECTED"
    )


def test_rehearsal_remains_simulation_only(report):
    assert (
        report.terminal_decision
        == "SIMULATED_PROFILE_PASS"
    )

    assert (
        report.physical_evidence_present
        is False
    )

    assert (
        report.native_claim_permitted
        is False
    )

    assert (
        report.statistical_decision
        .physical_claim_permitted
        is False
    )


def test_no_forbidden_physical_or_native_claim(report):
    assert (
        report.terminal_decision
        not in
        N0_FORBIDDEN_NATIVE_OR_PHYSICAL_DECISIONS
    )


def test_blind_reduction_hash_is_bound(report):
    assert (
        report.blind_reduction_hash.startswith(
            "sha256:"
        )
    )

    assert len(
        report.blind_reduction_hash
    ) == (
        len("sha256:")
        + 64
    )


def test_synthetic_preregistration_is_explicit():
    preregistration = (
        build_synthetic_statistical_preregistration(
            repetitions_per_phase=24
        )
    )

    assert (
        preregistration.is_complete_for_physical_decision
        is True
    )

    # Completeness here means numerically resolved only.
    # The IDs explicitly identify this as a synthetic rehearsal.
    assert (
        "SYNTHETIC"
        in preregistration.preregistration_id
    )

    assert (
        "SYNTHETIC"
        in preregistration.calibration_gate_id
    )

    assert (
        "SYNTHETIC"
        in preregistration.operational_gate_id
    )


def test_public_api_exposes_no_truth_parameter():
    parameters = set(
        inspect.signature(
            run_n0_statistical_rehearsal
        ).parameters
    )

    forbidden = {
        "theta",
        "theta_truth",
        "truth",
        "truth_phase",
        "expected_phase",
        "expected_order",
        "semantic_answer",
    }

    assert forbidden.isdisjoint(
        parameters
    )


def test_statistical_rehearsal_is_deterministic(report):
    second = (
        run_n0_statistical_rehearsal(
            root_seed_commitment=ROOT,
            repetitions_per_phase=24,
            samples_per_quadrature=1024,
        )
    )

    assert (
        report.report_hash
        == second.report_hash
    )

    assert (
        report.to_dict()
        == second.to_dict()
    )


@pytest.mark.parametrize(
    "repetitions",
    (
        0,
        1,
    ),
)
def test_repetition_count_fails_closed(repetitions):
    with pytest.raises(
        ValueError,
        match="repetitions_per_phase",
    ):
        run_n0_statistical_rehearsal(
            root_seed_commitment=ROOT,
            repetitions_per_phase=(
                repetitions
            ),
            samples_per_quadrature=32,
        )
