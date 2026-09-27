from __future__ import annotations

import math
from dataclasses import dataclass

from src.n0_claim_firewall import (
    validate_simulation_only_decision,
)
from src.n0_device_adapter import (
    N0TrialCommand,
)
from src.n0_reducer import (
    N0ReductionResult,
    reduce_n0_records,
)
from src.n0_rehearsal import (
    RehearsalLedgerEntry,
    build_default_rehearsal_ledger,
    canonical_sha256_value,
)
from src.n0_statistics import (
    N0_PHASE_VALIDATION_MULTIPLICITY_RULE,
    N0PhaseValidationDecision,
    N0Preregistration,
    PhaseValidationCell,
    PreregisteredParameter,
    evaluate_preregistered_phase_validation,
)
from src.n0_synthetic_device import (
    SyntheticN0Device,
    SyntheticPreparation,
)


N0_STATISTICAL_REHEARSAL_SCHEMA = (
    "cpc.shor.n0.statistical-rehearsal.v1"
)

N0_STATISTICAL_REHEARSAL_ID = (
    "CPC-SHOR-N0-STATISTICAL-REHEARSAL-v1"
)

# These are deliberately software-rehearsal values.
# They are NOT proposed physical N0 thresholds.
SYNTHETIC_STATISTICAL_ALPHA = 0.05
SYNTHETIC_STATISTICAL_MARGIN_RAD = 2.0
SYNTHETIC_STATISTICAL_POWER_TARGET = 0.80
SYNTHETIC_STATISTICAL_MAX_INVALID_FRACTION = 0.05


@dataclass(frozen=True)
class RepeatedBlindReduction:
    validation_trial_id: str
    preparation_command_hash: str
    reduction: N0ReductionResult

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "validation_trial_id": (
                self.validation_trial_id
            ),
            "preparation_command_hash": (
                self.preparation_command_hash
            ),
            "reduction": (
                self.reduction.to_dict()
            ),
        }


@dataclass(frozen=True)
class N0StatisticalRehearsalReport:
    rehearsal_id: str

    repetitions_per_phase: int
    samples_per_quadrature: int

    blind_reduction_hash: str

    statistical_decision: (
        N0PhaseValidationDecision
    )

    negative_statistical_decision: (
        N0PhaseValidationDecision
    )

    negative_control_status: str

    terminal_decision: str

    physical_evidence_present: bool = False
    native_claim_permitted: bool = False

    def __post_init__(self) -> None:
        if (
            self.rehearsal_id
            != N0_STATISTICAL_REHEARSAL_ID
        ):
            raise ValueError(
                "unexpected statistical rehearsal identity"
            )

        if (
            self.physical_evidence_present
            is not False
        ):
            raise ValueError(
                "synthetic statistical rehearsal "
                "cannot contain physical evidence"
            )

        if (
            self.native_claim_permitted
            is not False
        ):
            raise ValueError(
                "synthetic statistical rehearsal "
                "cannot permit native claim"
            )

        validate_simulation_only_decision(
            self.terminal_decision
        )

    @property
    def schema(self) -> str:
        return (
            N0_STATISTICAL_REHEARSAL_SCHEMA
        )

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "schema": self.schema,
            "rehearsal_id": (
                self.rehearsal_id
            ),
            "repetitions_per_phase": (
                self.repetitions_per_phase
            ),
            "samples_per_quadrature": (
                self.samples_per_quadrature
            ),
            "blind_reduction_hash": (
                self.blind_reduction_hash
            ),
            "statistical_decision": (
                self.statistical_decision.to_dict()
            ),
            "negative_statistical_decision": (
                self.negative_statistical_decision.to_dict()
            ),
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
    def report_hash(self) -> str:
        return canonical_sha256_value(
            self.to_dict()
        )


def _build_device(
    *,
    ledger: tuple[
        RehearsalLedgerEntry,
        ...
    ],
    root_seed_commitment: str,
) -> SyntheticN0Device:
    return SyntheticN0Device(
        root_seed_commitment=(
            root_seed_commitment
        ),
        preparations=tuple(
            SyntheticPreparation(
                preparation_command_hash=(
                    entry.preparation_command_hash
                ),
                theta_rad=(
                    entry.truth_phase_rad
                ),
            )
            for entry in ledger
        ),
    )


def build_synthetic_statistical_preregistration(
    *,
    repetitions_per_phase: int,
) -> N0Preregistration:
    if (
        not isinstance(
            repetitions_per_phase,
            int,
        )
        or isinstance(
            repetitions_per_phase,
            bool,
        )
        or repetitions_per_phase < 2
    ):
        raise ValueError(
            "repetitions_per_phase must be an integer >= 2"
        )

    def resolved(
        name: str,
        value: float | int,
        units: str,
    ) -> PreregisteredParameter:
        return PreregisteredParameter(
            name=name,
            status="RESOLVED",
            value=value,
            units=units,
        )

    return N0Preregistration(
        preregistration_id=(
            "CPC-SHOR-N0-SYNTHETIC-STATISTICAL-PREREG-v1"
        ),
        alpha=resolved(
            "alpha",
            SYNTHETIC_STATISTICAL_ALPHA,
            "probability",
        ),
        equivalence_margin_rad=resolved(
            "equivalence_margin_rad",
            SYNTHETIC_STATISTICAL_MARGIN_RAD,
            "rad",
        ),
        power_target=resolved(
            "power_target",
            SYNTHETIC_STATISTICAL_POWER_TARGET,
            "probability",
        ),
        minimum_valid_samples=resolved(
            "minimum_valid_samples",
            repetitions_per_phase,
            "count",
        ),
        maximum_invalid_fraction=resolved(
            "maximum_invalid_fraction",
            SYNTHETIC_STATISTICAL_MAX_INVALID_FRACTION,
            "fraction",
        ),
        calibration_gate_id=(
            "SYNTHETIC-CALIBRATION-PARTITION-v1"
        ),
        operational_gate_id=(
            "SYNTHETIC-HELDOUT-VALIDATION-PARTITION-v1"
        ),
        multiplicity_rule=(
            N0_PHASE_VALIDATION_MULTIPLICITY_RULE
        ),
    )


def _blind_repeated_acquisition(
    *,
    ledger: tuple[
        RehearsalLedgerEntry,
        ...
    ],
    root_seed_commitment: str,
    repetitions_per_phase: int,
    samples_per_quadrature: int,
) -> tuple[
    RepeatedBlindReduction,
    ...
]:
    """
    Repeated held-out acquisition/reduction.

    The reducer receives only raw records and calibration.
    No truth phase is passed into reduce_n0_records.
    """

    device = _build_device(
        ledger=ledger,
        root_seed_commitment=(
            root_seed_commitment
        ),
    )

    reductions: list[
        RepeatedBlindReduction
    ] = []

    for phase_index, entry in enumerate(
        ledger
    ):
        for repetition in range(
            repetitions_per_phase
        ):
            validation_trial_id = (
                f"heldout-phase-{phase_index:03d}"
                f"-rep-{repetition:04d}"
            )

            x_record = device.acquire(
                N0TrialCommand(
                    experiment_id=(
                        N0_STATISTICAL_REHEARSAL_ID
                    ),
                    trial_id=(
                        validation_trial_id
                        + "-x"
                    ),
                    role="operational",
                    command_phase_rad=0.0,
                    preparation_command_hash=(
                        entry.preparation_command_hash
                    ),
                    probe_configuration_hash=(
                        "sha256:"
                        + "c" * 64
                    ),
                    sample_count=(
                        samples_per_quadrature
                    ),
                )
            )

            y_record = device.acquire(
                N0TrialCommand(
                    experiment_id=(
                        N0_STATISTICAL_REHEARSAL_ID
                    ),
                    trial_id=(
                        validation_trial_id
                        + "-y"
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
                        + "c" * 64
                    ),
                    sample_count=(
                        samples_per_quadrature
                    ),
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
                RepeatedBlindReduction(
                    validation_trial_id=(
                        validation_trial_id
                    ),
                    preparation_command_hash=(
                        entry.preparation_command_hash
                    ),
                    reduction=reduction,
                )
            )

    return tuple(
        reductions
    )


def _build_validation_cells_after_truth_reveal(
    *,
    ledger: tuple[
        RehearsalLedgerEntry,
        ...
    ],
    reductions: tuple[
        RepeatedBlindReduction,
        ...
    ],
) -> tuple[
    PhaseValidationCell,
    ...
]:
    """
    Truth is introduced only after all blind reductions exist.
    """

    results_by_preparation: dict[
        str,
        list[RepeatedBlindReduction],
    ] = {
        entry.preparation_command_hash: []
        for entry in ledger
    }

    for item in reductions:
        results_by_preparation[
            item.preparation_command_hash
        ].append(
            item
        )

    cells: list[
        PhaseValidationCell
    ] = []

    for phase_index, entry in enumerate(
        ledger
    ):
        items = tuple(
            results_by_preparation[
                entry.preparation_command_hash
            ]
        )

        valid_trial_ids: list[str] = []
        estimates: list[float] = []
        invalid_trial_ids: list[str] = []

        for item in items:
            result = item.reduction

            if (
                result.status == "ok"
                and result.estimated_phase_rad
                is not None
            ):
                valid_trial_ids.append(
                    item.validation_trial_id
                )

                estimates.append(
                    result.estimated_phase_rad
                )
            else:
                invalid_trial_ids.append(
                    item.validation_trial_id
                )

        cells.append(
            PhaseValidationCell(
                cell_id=(
                    f"synthetic-phase-cell-{phase_index:03d}"
                ),

                # In this rehearsal this field labels the
                # prepared target phase cell. The actual probe
                # commands remain X=0 and Y=pi/2 in the blind
                # acquisition stage above.
                command_phase_rad=(
                    entry.truth_phase_rad
                ),

                truth_phase_rad=(
                    entry.truth_phase_rad
                ),

                valid_trial_ids=tuple(
                    valid_trial_ids
                ),

                estimates_rad=tuple(
                    estimates
                ),

                invalid_trial_ids=tuple(
                    invalid_trial_ids
                ),
            )
        )

    return tuple(
        cells
    )


def _build_negative_statistical_cells(
    cells: tuple[
        PhaseValidationCell,
        ...
    ],
) -> tuple[
    PhaseValidationCell,
    ...
]:
    """
    Deterministic post-reduction statistical negative control.

    The first held-out cell is replaced by maximally wrong
    pi-displaced estimates. Raw acquisition is not rewritten.
    """

    result: list[
        PhaseValidationCell
    ] = []

    for index, cell in enumerate(
        cells
    ):
        if index == 0:
            corrupted_estimates = tuple(
                cell.truth_phase_rad
                + math.pi
                for _ in cell.estimates_rad
            )

            result.append(
                PhaseValidationCell(
                    cell_id=cell.cell_id,
                    command_phase_rad=(
                        cell.command_phase_rad
                    ),
                    truth_phase_rad=(
                        cell.truth_phase_rad
                    ),
                    valid_trial_ids=(
                        cell.valid_trial_ids
                    ),
                    estimates_rad=(
                        corrupted_estimates
                    ),
                    invalid_trial_ids=(
                        cell.invalid_trial_ids
                    ),
                )
            )
        else:
            result.append(
                cell
            )

    return tuple(
        result
    )


def run_n0_statistical_rehearsal(
    *,
    root_seed_commitment: str,
    repetitions_per_phase: int = 24,
    samples_per_quadrature: int = 1024,
) -> N0StatisticalRehearsalReport:
    if (
        not isinstance(
            repetitions_per_phase,
            int,
        )
        or isinstance(
            repetitions_per_phase,
            bool,
        )
        or repetitions_per_phase < 2
    ):
        raise ValueError(
            "repetitions_per_phase must be an integer >= 2"
        )

    if (
        not isinstance(
            samples_per_quadrature,
            int,
        )
        or isinstance(
            samples_per_quadrature,
            bool,
        )
        or samples_per_quadrature <= 0
    ):
        raise ValueError(
            "samples_per_quadrature must be positive"
        )

    ledger = (
        build_default_rehearsal_ledger()
    )

    reductions = (
        _blind_repeated_acquisition(
            ledger=ledger,
            root_seed_commitment=(
                root_seed_commitment
            ),
            repetitions_per_phase=(
                repetitions_per_phase
            ),
            samples_per_quadrature=(
                samples_per_quadrature
            ),
        )
    )

    blind_reduction_hash = (
        canonical_sha256_value(
            [
                item.to_dict()
                for item in reductions
            ]
        )
    )

    cells = (
        _build_validation_cells_after_truth_reveal(
            ledger=ledger,
            reductions=reductions,
        )
    )

    preregistration = (
        build_synthetic_statistical_preregistration(
            repetitions_per_phase=(
                repetitions_per_phase
            )
        )
    )

    # Reserved synthetic calibration identities.
    #
    # These are intentionally disjoint from all held-out validation
    # identities. This rehearses the partition contract; it does not
    # pretend that these identifiers are physical calibration records.
    calibration_trial_ids = tuple(
        f"synthetic-calibration-reserved-{index:04d}"
        for index in range(8)
    )

    statistical_decision = (
        evaluate_preregistered_phase_validation(
            preregistration=(
                preregistration
            ),
            cells=cells,
            calibration_trial_ids=(
                calibration_trial_ids
            ),
        )
    )

    negative_cells = (
        _build_negative_statistical_cells(
            cells
        )
    )

    negative_decision = (
        evaluate_preregistered_phase_validation(
            preregistration=(
                preregistration
            ),
            cells=negative_cells,
            calibration_trial_ids=(
                calibration_trial_ids
            ),
        )
    )

    negative_control_status = (
        "NEGATIVE_STATISTICAL_CONTROL_DETECTED"
        if (
            negative_decision.status
            == "EQUIVALENCE_NOT_ESTABLISHED"
        )
        else "NEGATIVE_STATISTICAL_CONTROL_NOT_DETECTED"
    )

    if (
        statistical_decision.status
        == "EQUIVALENCE_ESTABLISHED"
        and negative_control_status
        == "NEGATIVE_STATISTICAL_CONTROL_DETECTED"
    ):
        terminal_decision = (
            "SIMULATED_PROFILE_PASS"
        )
    else:
        terminal_decision = (
            "SIMULATED_PROFILE_FAIL"
        )

    terminal_decision = (
        validate_simulation_only_decision(
            terminal_decision
        )
    )

    return N0StatisticalRehearsalReport(
        rehearsal_id=(
            N0_STATISTICAL_REHEARSAL_ID
        ),
        repetitions_per_phase=(
            repetitions_per_phase
        ),
        samples_per_quadrature=(
            samples_per_quadrature
        ),
        blind_reduction_hash=(
            blind_reduction_hash
        ),
        statistical_decision=(
            statistical_decision
        ),
        negative_statistical_decision=(
            negative_decision
        ),
        negative_control_status=(
            negative_control_status
        ),
        terminal_decision=(
            terminal_decision
        ),
        physical_evidence_present=False,
        native_claim_permitted=False,
    )
