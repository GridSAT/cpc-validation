import pytest

from src.n0_claim_firewall import (
    N0_FORBIDDEN_NATIVE_OR_PHYSICAL_DECISIONS,
    N0_SIMULATION_ONLY_ALLOWED_DECISIONS,
    validate_simulation_only_decision,
)


@pytest.mark.parametrize(
    "decision",
    N0_SIMULATION_ONLY_ALLOWED_DECISIONS,
)
def test_allowed_simulation_decisions_pass(decision):
    assert (
        validate_simulation_only_decision(decision)
        == decision
    )


@pytest.mark.parametrize(
    "decision",
    N0_FORBIDDEN_NATIVE_OR_PHYSICAL_DECISIONS,
)
def test_native_or_physical_decisions_are_blocked(decision):
    with pytest.raises(
        RuntimeError,
        match="cannot produce",
    ):
        validate_simulation_only_decision(
            decision
        )


def test_unknown_decision_is_rejected():
    with pytest.raises(
        ValueError,
        match="unknown",
    ):
        validate_simulation_only_decision(
            "MAYBE_PASS"
        )
