from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass

from src.n0_claim_firewall import (
    validate_simulation_only_decision,
)
from src.n0_device_adapter import (
    N0TrialCommand,
)
from src.n0_faults import (
    inject_clipping,
)
from src.n0_reducer import (
    N0ReductionResult,
    reduce_n0_records,
)
from src.n0_statistics import (
    summarize_phase_estimates,
    wrap_phase_error,
)
from src.n0_synthetic_device import (
    SyntheticN0Device,
    SyntheticPreparation,
    opaque_preparation_hash,
)


N0_SYNTHETIC_REHEARSAL_SCHEMA = (
    "cpc.shor.n0.synthetic-rehearsal.v1"
)

N0_SYNTHETIC_REHEARSAL_ID = (
    "N0-SYNTHETIC-REHEARSAL-v1"
)

# This is a software-rehearsal gate only.
# It is NOT a physical preregistration margin.
SYNTHETIC_PHASE_ERROR_GATE_RAD = 0.40


def canonical_json_value(
    value: object,
) -> str:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    )


def canonical_sha256_value(
    value: object,
) -> str:
    digest = hashlib.sha256(
        canonical_json_value(
            value
        ).encode("utf-8")
    ).hexdigest()

    return f"sha256:{digest}"


@dataclass(frozen=True)
class RehearsalLedgerEntry:
    preparation_command_hash: str
    truth_phase_rad: float

    def __post_init__(self) -> None:
        if (
            not isinstance(
                self.preparation_command_hash,
                str,
            )
            or not self.preparation_command_hash.startswith(
                "sha256:"
            )
        ):
            raise ValueError(
                "preparation_command_hash must be sha256"
            )

        if (
            not isinstance(
                self.truth_phase_rad,
                (int, float),
            )
            or isinstance(
                self.truth_phase_rad,
                bool,
            )
            or not math.isfinite(
                self.truth_phase_rad
            )
        ):
            raise ValueError(
                "truth_phase_rad must be finite"
            )

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "preparation_command_hash": (
                self.preparation_command_hash
            ),
            "truth_phase_rad": (
                self.truth_phase_rad
            ),
        }


@dataclass(frozen=True)
class BlindReduction:
    preparation_command_hash: str
    reduction: N0ReductionResult

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "preparation_command_hash": (
                self.preparation_command_hash
            ),
            "reduction": (
                self.reduction.to_dict()
            ),
        }


@dataclass(frozen=True)
class TruthComparison:
    preparation_command_hash: str
    truth_phase_rad: float
    estimated_phase_rad: float
    wrapped_error_rad: float
    passed_synthetic_gate: bool

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "preparation_command_hash": (
                self.preparation_command_hash
            ),
            "truth_phase_rad": (
                self.truth_phase_rad
            ),
            "estimated_phase_rad": (
                self.estimated_phase_rad
            ),
            "wrapped_error_rad": (
                self.wrapped_error_rad
            ),
            "passed_synthetic_gate": (
                self.passed_synthetic_gate
            ),
        }


@dataclass(frozen=True)
class N0SyntheticRehearsalReport:
    rehearsal_id: str

    preparation_ledger_hash: str
    blind_reduction_hash: str

    comparisons: tuple[
        TruthComparison,
        ...
    ]

    negative_control_status: str

    terminal_decision: str

    physical_evidence_present: bool
    native_claim_permitted: bool

    def __post_init__(
        self,
    ) -> None:
        if (
            self.physical_evidence_present
            is not False
        ):
            raise ValueError(
                "synthetic rehearsal cannot contain physical evidence"
            )

        if (
            self.native_claim_permitted
            is not False
        ):
            raise ValueError(
                "synthetic rehearsal cannot permit native claim"
            )

        validate_simulation_only_decision(
            self.terminal_decision
        )

    @property
    def schema(
        self,
    ) -> str:
        return (
            N0_SYNTHETIC_REHEARSAL_SCHEMA
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "schema": self.schema,
            "rehearsal_id": (
                self.rehearsal_id
            ),
            "preparation_ledger_hash": (
                self.preparation_ledger_hash
            ),
            "blind_reduction_hash": (
                self.blind_reduction_hash
            ),
            "comparisons": [
                comparison.to_dict()
                for comparison
                in self.comparisons
            ],
            "negative_control_status": (
                self.negative_control_status
            ),
            "terminal_decision": (
                self.terminal_decision
            ),
            "physical_evidence_present": (
                self.physical_evidence_present
            ),
            "native_claim_permitted": (
                self.native_claim_permitted
            ),
        }

    @property
    def canonical_json(
        self,
    ) -> str:
        return canonical_json_value(
            self.to_dict()
        )

    @property
    def report_hash(
        self,
    ) -> str:
        return canonical_sha256_value(
            self.to_dict()
        )


def build_default_rehearsal_ledger(
) -> tuple[
    RehearsalLedgerEntry,
    ...
]:
    entries = (
        RehearsalLedgerEntry(
            preparation_command_hash=(
                opaque_preparation_hash(
                    "rehearsal-phase-zero"
                )
            ),
            truth_phase_rad=0.0,
        ),
        RehearsalLedgerEntry(
            preparation_command_hash=(
                opaque_preparation_hash(
                    "rehearsal-phase-pi-over-four"
                )
            ),
            truth_phase_rad=(
                math.pi / 4.0
            ),
        ),
        RehearsalLedgerEntry(
            preparation_command_hash=(
                opaque_preparation_hash(
                    "rehearsal-phase-pi-over-two"
                )
            ),
            truth_phase_rad=(
                math.pi / 2.0
            ),
        ),
    )

    return tuple(
        sorted(
            entries,
            key=lambda item: (
                item.preparation_command_hash
            ),
        )
    )


def _build_device_from_ledger(
    *,
    ledger: tuple[
        RehearsalLedgerEntry,
        ...
    ],
    root_seed_commitment: str,
) -> SyntheticN0Device:
    preparations = tuple(
        SyntheticPreparation(
            preparation_command_hash=(
                entry.preparation_command_hash
            ),
            theta_rad=(
                entry.truth_phase_rad
            ),
        )
        for entry in ledger
    )

    return SyntheticN0Device(
        root_seed_commitment=(
            root_seed_commitment
        ),
        preparations=preparations,
    )


def _blind_acquire_and_reduce(
    *,
    ledger: tuple[
        RehearsalLedgerEntry,
        ...
    ],
    root_seed_commitment: str,
    sample_count: int,
) -> tuple[
    tuple[
        BlindReduction,
        ...
    ],
    SyntheticN0Device,
]:
    """
    Acquisition/reduction stage.

    The reducer is never passed truth_phase_rad. Truth remains confined to
    the preparation authority represented by the ledger/device catalog.
    """
    device = _build_device_from_ledger(
        ledger=ledger,
        root_seed_commitment=(
            root_seed_commitment
        ),
    )

    reductions: list[
        BlindReduction
    ] = []

    for index, entry in enumerate(
        ledger
    ):
        x_record = device.acquire(
            N0TrialCommand(
                experiment_id=(
                    N0_SYNTHETIC_REHEARSAL_ID
                ),
                trial_id=(
                    f"prep-{index:03d}-x"
                ),
                role="operational",
                command_phase_rad=0.0,
                preparation_command_hash=(
                    entry.preparation_command_hash
                ),
                probe_configuration_hash=(
                    "sha256:"
                    + "7" * 64
                ),
                sample_count=sample_count,
            )
        )

        y_record = device.acquire(
            N0TrialCommand(
                experiment_id=(
                    N0_SYNTHETIC_REHEARSAL_ID
                ),
                trial_id=(
                    f"prep-{index:03d}-y"
                ),
                role="operational",
                command_phase_rad=(
                    math.pi / 2.0
                ),
                preparation_command_hash=(
                    entry.preparation_command_hash
                ),
                probe_configuration_hash=(
                    "sha256:"
                    + "7" * 64
                ),
                sample_count=sample_count,
            )
        )

        reduction = reduce_n0_records(
            records=(
                x_record,
                y_record,
            ),
            calibration=(
                device.calibration
            ),
        )

        reductions.append(
            BlindReduction(
                preparation_command_hash=(
                    entry.preparation_command_hash
                ),
                reduction=reduction,
            )
        )

    return (
        tuple(
            reductions
        ),
        device,
    )


def _truth_reveal(
    *,
    ledger: tuple[
        RehearsalLedgerEntry,
        ...
    ],
    reductions: tuple[
        BlindReduction,
        ...
    ],
) -> tuple[
    TruthComparison,
    ...
]:
    truth_by_hash = {
        entry.preparation_command_hash:
        entry.truth_phase_rad
        for entry in ledger
    }

    comparisons: list[
        TruthComparison
    ] = []

    for item in reductions:
        result = item.reduction

        if (
            result.status != "ok"
            or result.estimated_phase_rad
            is None
        ):
            continue

        truth = truth_by_hash[
            item.preparation_command_hash
        ]

        error = wrap_phase_error(
            result.estimated_phase_rad,
            truth,
        )

        comparisons.append(
            TruthComparison(
                preparation_command_hash=(
                    item.preparation_command_hash
                ),
                truth_phase_rad=truth,
                estimated_phase_rad=(
                    result.estimated_phase_rad
                ),
                wrapped_error_rad=error,
                passed_synthetic_gate=(
                    abs(error)
                    <= SYNTHETIC_PHASE_ERROR_GATE_RAD
                ),
            )
        )

    return tuple(
        comparisons
    )


def _run_negative_control(
    *,
    ledger: tuple[
        RehearsalLedgerEntry,
        ...
    ],
    root_seed_commitment: str,
    sample_count: int,
) -> str:
    entry = ledger[0]

    device = _build_device_from_ledger(
        ledger=ledger,
        root_seed_commitment=(
            root_seed_commitment
        ),
    )

    x_record = device.acquire(
        N0TrialCommand(
            experiment_id=(
                "N0-SYNTHETIC-NEGATIVE-CONTROL-v1"
            ),
            trial_id="negative-x",
            role="negative_control",
            command_phase_rad=0.0,
            preparation_command_hash=(
                entry.preparation_command_hash
            ),
            probe_configuration_hash=(
                "sha256:"
                + "8" * 64
            ),
            sample_count=sample_count,
        )
    )

    y_record = device.acquire(
        N0TrialCommand(
            experiment_id=(
                "N0-SYNTHETIC-NEGATIVE-CONTROL-v1"
            ),
            trial_id="negative-y",
            role="negative_control",
            command_phase_rad=(
                math.pi / 2.0
            ),
            preparation_command_hash=(
                entry.preparation_command_hash
            ),
            probe_configuration_hash=(
                "sha256:"
                + "8" * 64
            ),
            sample_count=sample_count,
        )
    )

    faulted_x = inject_clipping(
        x_record,
        index=0,
    )

    result = reduce_n0_records(
        records=(
            faulted_x,
            y_record,
        ),
        calibration=device.calibration,
    )

    if result.status == "invalid":
        return (
            "NEGATIVE_CONTROL_DETECTED"
        )

    return (
        "NEGATIVE_CONTROL_NOT_DETECTED"
    )


def run_n0_synthetic_rehearsal(
    *,
    root_seed_commitment: str,
    sample_count: int = 4096,
) -> N0SyntheticRehearsalReport:
    if (
        not isinstance(
            sample_count,
            int,
        )
        or isinstance(
            sample_count,
            bool,
        )
        or sample_count <= 0
    ):
        raise ValueError(
            "sample_count must be a positive integer"
        )

    ledger = (
        build_default_rehearsal_ledger()
    )

    ledger_payload = [
        entry.to_dict()
        for entry in ledger
    ]

    ledger_hash = (
        canonical_sha256_value(
            ledger_payload
        )
    )

    reductions, _ = (
        _blind_acquire_and_reduce(
            ledger=ledger,
            root_seed_commitment=(
                root_seed_commitment
            ),
            sample_count=sample_count,
        )
    )

    blind_payload = [
        item.to_dict()
        for item in reductions
    ]

    blind_hash = (
        canonical_sha256_value(
            blind_payload
        )
    )

    comparisons = _truth_reveal(
        ledger=ledger,
        reductions=reductions,
    )

    negative_control_status = (
        _run_negative_control(
            ledger=ledger,
            root_seed_commitment=(
                root_seed_commitment
            ),
            sample_count=sample_count,
        )
    )

    all_reductions_ok = (
        len(reductions)
        == len(ledger)
        and all(
            item.reduction.status
            == "ok"
            for item in reductions
        )
    )

    all_comparisons_present = (
        len(comparisons)
        == len(ledger)
    )

    all_phase_gates_pass = (
        all_comparisons_present
        and all(
            comparison.passed_synthetic_gate
            for comparison in comparisons
        )
    )

    negative_control_pass = (
        negative_control_status
        == "NEGATIVE_CONTROL_DETECTED"
    )

    if (
        all_reductions_ok
        and all_phase_gates_pass
        and negative_control_pass
    ):
        decision = (
            "SIMULATED_PROFILE_PASS"
        )
    else:
        decision = (
            "SIMULATED_PROFILE_FAIL"
        )

    decision = (
        validate_simulation_only_decision(
            decision
        )
    )

    return N0SyntheticRehearsalReport(
        rehearsal_id=(
            N0_SYNTHETIC_REHEARSAL_ID
        ),
        preparation_ledger_hash=(
            ledger_hash
        ),
        blind_reduction_hash=(
            blind_hash
        ),
        comparisons=comparisons,
        negative_control_status=(
            negative_control_status
        ),
        terminal_decision=decision,
        physical_evidence_present=False,
        native_claim_permitted=False,
    )
