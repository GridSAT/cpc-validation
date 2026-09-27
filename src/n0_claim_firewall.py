from __future__ import annotations


N0_SIMULATION_ONLY_ALLOWED_DECISIONS = (
    "INVALID_SIMULATED_EVIDENCE",
    "SIMULATED_PROFILE_FAIL",
    "SIMULATED_PROFILE_PASS",
    "SOFTWARE_INFRASTRUCTURE_ABORT",
)

N0_FORBIDDEN_NATIVE_OR_PHYSICAL_DECISIONS = (
    "ADVANTAGE_EVIDENCE",
    "NATIVE_CPC_VALIDATED",
    "NATIVE_SHOR",
    "PHYSICAL_CPC_VALIDATED",
    "PHYSICAL_N0_PASS",
    "SCALING_EVIDENCE",
)


def validate_simulation_only_decision(
    decision: str,
) -> str:
    if decision in (
        N0_FORBIDDEN_NATIVE_OR_PHYSICAL_DECISIONS
    ):
        raise RuntimeError(
            "simulation-only N0 evidence cannot produce "
            "a physical/native claim"
        )

    if decision not in (
        N0_SIMULATION_ONLY_ALLOWED_DECISIONS
    ):
        raise ValueError(
            "unknown simulation-only N0 decision"
        )

    return decision
