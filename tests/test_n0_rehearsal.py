import inspect

from src.n0_claim_firewall import (
    N0_FORBIDDEN_NATIVE_OR_PHYSICAL_DECISIONS,
)
from src.n0_rehearsal import (
    N0_SYNTHETIC_REHEARSAL_ID,
    SYNTHETIC_PHASE_ERROR_GATE_RAD,
    build_default_rehearsal_ledger,
    run_n0_synthetic_rehearsal,
)


ROOT = (
    "sha256:"
    + "9" * 64
)


def test_default_ledger_contains_multiple_phases():
    ledger = (
        build_default_rehearsal_ledger()
    )

    assert len(
        ledger
    ) >= 3

    truths = {
        entry.truth_phase_rad
        for entry in ledger
    }

    assert len(
        truths
    ) >= 3


def test_rehearsal_passes_simulation_only():
    report = (
        run_n0_synthetic_rehearsal(
            root_seed_commitment=ROOT,
            sample_count=4096,
        )
    )

    assert (
        report.rehearsal_id
        == N0_SYNTHETIC_REHEARSAL_ID
    )

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


def test_all_truth_comparisons_pass_software_gate():
    report = (
        run_n0_synthetic_rehearsal(
            root_seed_commitment=ROOT,
            sample_count=4096,
        )
    )

    assert report.comparisons

    assert all(
        comparison.passed_synthetic_gate
        for comparison
        in report.comparisons
    )

    assert all(
        abs(
            comparison.wrapped_error_rad
        )
        <= SYNTHETIC_PHASE_ERROR_GATE_RAD
        for comparison
        in report.comparisons
    )


def test_negative_control_is_detected():
    report = (
        run_n0_synthetic_rehearsal(
            root_seed_commitment=ROOT,
            sample_count=4096,
        )
    )

    assert (
        report.negative_control_status
        == "NEGATIVE_CONTROL_DETECTED"
    )


def test_rehearsal_is_byte_deterministic():
    first = (
        run_n0_synthetic_rehearsal(
            root_seed_commitment=ROOT,
            sample_count=4096,
        )
    )

    second = (
        run_n0_synthetic_rehearsal(
            root_seed_commitment=ROOT,
            sample_count=4096,
        )
    )

    assert (
        first.canonical_json
        == second.canonical_json
    )

    assert (
        first.report_hash
        == second.report_hash
    )


def test_rehearsal_never_emits_forbidden_claim():
    report = (
        run_n0_synthetic_rehearsal(
            root_seed_commitment=ROOT,
            sample_count=4096,
        )
    )

    assert (
        report.terminal_decision
        not in
        N0_FORBIDDEN_NATIVE_OR_PHYSICAL_DECISIONS
    )


def test_public_rehearsal_api_has_no_truth_argument():
    parameters = set(
        inspect.signature(
            run_n0_synthetic_rehearsal
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


def test_blind_reduction_hash_is_bound():
    report = (
        run_n0_synthetic_rehearsal(
            root_seed_commitment=ROOT,
            sample_count=4096,
        )
    )

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


def test_preparation_ledger_hash_is_bound():
    report = (
        run_n0_synthetic_rehearsal(
            root_seed_commitment=ROOT,
            sample_count=4096,
        )
    )

    assert (
        report.preparation_ledger_hash.startswith(
            "sha256:"
        )
    )

    assert len(
        report.preparation_ledger_hash
    ) == (
        len("sha256:")
        + 64
    )
