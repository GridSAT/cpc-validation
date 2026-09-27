from __future__ import annotations

import hashlib
import inspect
import json
import math
from dataclasses import dataclass

from src.n0_calibration import N0Calibration
from src.n0_raw_record import N0RawRecord


N0_REDUCER_SCHEMA = "cpc.shor.n0.reducer.v1"

REDUCTION_STATUSES = (
    "invalid",
    "ok",
)

FORBIDDEN_REDUCER_PARAMETER_NAMES = frozenset(
    {
        "expected_class",
        "expected_order",
        "expected_output",
        "expected_phase",
        "semantic_answer",
        "theta",
        "theta_truth",
        "truth",
        "truth_phase",
    }
)


def canonical_json_value(value: object) -> str:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    )


def canonical_sha256_value(value: object) -> str:
    digest = hashlib.sha256(
        canonical_json_value(value).encode("utf-8")
    ).hexdigest()
    return f"sha256:{digest}"


def _calibration_lookup(
    calibration: N0Calibration,
) -> dict[str, float]:
    result: dict[str, float] = {}

    for item in calibration.values:
        if item.nominal_value is None:
            continue

        result[item.name] = float(
            item.nominal_value
        )

    return result


def _validate_reducer_signature() -> None:
    parameters = set(
        inspect.signature(
            reduce_n0_records
        ).parameters
    )

    forbidden = (
        parameters
        & FORBIDDEN_REDUCER_PARAMETER_NAMES
    )

    if forbidden:
        raise RuntimeError(
            "reducer API contains forbidden truth parameter(s): "
            + ", ".join(sorted(forbidden))
        )


@dataclass(frozen=True)
class QuadratureReduction:
    command_phase_rad: float
    valid_record_count: int
    invalid_record_count: int

    signal_mean: float
    reference_mean: float
    corrected_mean: float

    def to_dict(self) -> dict[str, object]:
        return {
            "command_phase_rad": self.command_phase_rad,
            "valid_record_count": self.valid_record_count,
            "invalid_record_count": self.invalid_record_count,
            "signal_mean": self.signal_mean,
            "reference_mean": self.reference_mean,
            "corrected_mean": self.corrected_mean,
        }


@dataclass(frozen=True)
class N0ReductionResult:
    reducer_id: str
    calibration_id: str

    input_record_hashes: tuple[str, ...]

    status: str

    x_quadrature: QuadratureReduction | None
    y_quadrature: QuadratureReduction | None

    estimated_phase_rad: float | None

    invalid_record_count: int
    valid_record_count: int

    audit: tuple[
        tuple[str, object],
        ...
    ]

    def __post_init__(self) -> None:
        if self.status not in REDUCTION_STATUSES:
            raise ValueError(
                "unknown reduction status"
            )

        if (
            self.status == "ok"
            and self.estimated_phase_rad is None
        ):
            raise ValueError(
                "ok reduction requires phase estimate"
            )

        if (
            self.status == "invalid"
            and self.estimated_phase_rad is not None
        ):
            raise ValueError(
                "invalid reduction must not expose phase estimate"
            )

    @property
    def schema(self) -> str:
        return N0_REDUCER_SCHEMA

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "reducer_id": self.reducer_id,
            "calibration_id": self.calibration_id,
            "input_record_hashes": (
                self.input_record_hashes
            ),
            "status": self.status,
            "x_quadrature": (
                None
                if self.x_quadrature is None
                else self.x_quadrature.to_dict()
            ),
            "y_quadrature": (
                None
                if self.y_quadrature is None
                else self.y_quadrature.to_dict()
            ),
            "estimated_phase_rad": (
                self.estimated_phase_rad
            ),
            "invalid_record_count": (
                self.invalid_record_count
            ),
            "valid_record_count": (
                self.valid_record_count
            ),
            "audit": {
                key: value
                for key, value in self.audit
            },
        }

    @property
    def canonical_json(self) -> str:
        return canonical_json_value(
            self.to_dict()
        )

    @property
    def reduction_hash(self) -> str:
        return canonical_sha256_value(
            self.to_dict()
        )


def _record_is_valid(
    record: N0RawRecord,
) -> bool:
    if record.acquisition_status != "complete":
        return False

    if not record.reset_valid:
        return False

    quality_vectors = (
        record.clipping_flags,
        record.saturation_flags,
        record.dropped_sample_flags,
        record.timestamp_discontinuity_flags,
    )

    return not any(
        any(flags)
        for flags in quality_vectors
    )


def _retained_signal_mean(
    record: N0RawRecord,
) -> float:
    start = record.burn_in_end_index

    retained = record.signal_i[start:]

    if not retained:
        raise ValueError(
            "record contains no retained signal samples"
        )

    return sum(retained) / len(retained)


def _retained_reference_mean(
    record: N0RawRecord,
) -> float:
    start = record.burn_in_end_index

    retained = record.reference_i[start:]

    if not retained:
        raise ValueError(
            "record contains no retained reference samples"
        )

    return sum(retained) / len(retained)


def _reduce_quadrature(
    *,
    records: tuple[N0RawRecord, ...],
    command_phase_rad: float,
    gain: float,
    offset: float,
) -> QuadratureReduction:
    selected = tuple(
        record
        for record in records
        if math.isclose(
            record.command_phase_rad,
            command_phase_rad,
            rel_tol=0.0,
            abs_tol=1.0e-15,
        )
    )

    valid = tuple(
        record
        for record in selected
        if _record_is_valid(record)
    )

    invalid_count = len(selected) - len(valid)

    if not valid:
        raise ValueError(
            "quadrature has no valid records"
        )

    signal_mean = sum(
        _retained_signal_mean(record)
        for record in valid
    ) / len(valid)

    reference_mean = sum(
        _retained_reference_mean(record)
        for record in valid
    ) / len(valid)

    if gain == 0.0:
        raise ValueError(
            "detector gain must be nonzero"
        )

    corrected_mean = (
        signal_mean
        - offset
    ) / gain

    return QuadratureReduction(
        command_phase_rad=command_phase_rad,
        valid_record_count=len(valid),
        invalid_record_count=invalid_count,
        signal_mean=signal_mean,
        reference_mean=reference_mean,
        corrected_mean=corrected_mean,
    )


def reduce_n0_records(
    *,
    records: tuple[N0RawRecord, ...],
    calibration: N0Calibration,
    reducer_id: str = (
        "cpc.shor.n0.independent-phase-reducer.v1"
    ),
) -> N0ReductionResult:
    if not records:
        raise ValueError(
            "records must not be empty"
        )

    if (
        not isinstance(reducer_id, str)
        or not reducer_id
    ):
        raise ValueError(
            "reducer_id must be non-empty"
        )

    if any(
        not isinstance(record, N0RawRecord)
        for record in records
    ):
        raise ValueError(
            "records must contain N0RawRecord values"
        )

    profile_ids = {
        record.profile_id
        for record in records
    }

    calibration_ids = {
        record.calibration_id
        for record in records
    }

    if profile_ids != {
        calibration.profile_id
    }:
        raise ValueError(
            "record/calibration profile mismatch"
        )

    if calibration_ids != {
        calibration.calibration_id
    }:
        raise ValueError(
            "record/calibration identity mismatch"
        )

    params = _calibration_lookup(
        calibration
    )

    required = (
        "detector_gain",
        "detector_offset",
    )

    missing = [
        name
        for name in required
        if name not in params
    ]

    if missing:
        raise ValueError(
            "missing reducer calibration value(s): "
            + ", ".join(sorted(missing))
        )

    x_phase = 0.0
    y_phase = math.pi / 2.0

    try:
        x_result = _reduce_quadrature(
            records=records,
            command_phase_rad=x_phase,
            gain=params["detector_gain"],
            offset=params["detector_offset"],
        )

        y_result = _reduce_quadrature(
            records=records,
            command_phase_rad=y_phase,
            gain=params["detector_gain"],
            offset=params["detector_offset"],
        )

    except ValueError:
        valid_count = sum(
            int(_record_is_valid(record))
            for record in records
        )

        invalid_count = (
            len(records)
            - valid_count
        )

        return N0ReductionResult(
            reducer_id=reducer_id,
            calibration_id=calibration.calibration_id,
            input_record_hashes=tuple(
                record.record_hash
                for record in records
            ),
            status="invalid",
            x_quadrature=None,
            y_quadrature=None,
            estimated_phase_rad=None,
            invalid_record_count=invalid_count,
            valid_record_count=valid_count,
            audit=(
                (
                    "reason",
                    "missing-valid-quadrature",
                ),
                (
                    "truth_available_to_reducer",
                    False,
                ),
            ),
        )

    phase = math.atan2(
        y_result.corrected_mean,
        x_result.corrected_mean,
    )

    if phase < 0.0:
        phase += 2.0 * math.pi

    valid_count = (
        x_result.valid_record_count
        + y_result.valid_record_count
    )

    invalid_count = (
        x_result.invalid_record_count
        + y_result.invalid_record_count
    )

    return N0ReductionResult(
        reducer_id=reducer_id,
        calibration_id=calibration.calibration_id,
        input_record_hashes=tuple(
            record.record_hash
            for record in records
        ),
        status="ok",
        x_quadrature=x_result,
        y_quadrature=y_result,
        estimated_phase_rad=phase,
        invalid_record_count=invalid_count,
        valid_record_count=valid_count,
        audit=(
            (
                "phase_method",
                "atan2-y-over-x",
            ),
            (
                "record_realization_status_used_for_inference",
                False,
            ),
            (
                "truth_available_to_reducer",
                False,
            ),
        ),
    )


_validate_reducer_signature()
