from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass


N0_CALIBRATION_SCHEMA = "cpc.shor.n0.calibration.v1"

CALIBRATION_VALUE_CLASSES = (
    "CALIBRATED",
    "DIRECTLY_MEASURABLE",
    "INFERRED",
    "MODEL_DEPENDENT",
    "UNKNOWN",
)

CALIBRATION_REALIZATION_STATUSES = (
    "physical",
    "simulated",
)

REQUIRED_MAPPING_KEYS = (
    "command_phase_rad",
    "detector_gain",
    "detector_offset",
    "measurement_efficiency_eta",
    "measurement_rate_gamma_m",
    "model_time_scale",
    "probe_strength",
    "reference_amplitude",
    "reference_frequency_hz",
    "reference_phase_rad",
    "sample_period_s",
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


def _validate_nonempty_string(
    value: str,
    field_name: str,
) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(
            f"{field_name} must be a non-empty string"
        )


def _validate_optional_finite(
    value: float | None,
    field_name: str,
) -> None:
    if value is None:
        return

    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(value)
    ):
        raise ValueError(
            f"{field_name} must be finite or None"
        )


@dataclass(frozen=True)
class CalibrationValue:
    name: str
    classification: str
    units: str
    method: str
    evidence_id: str

    nominal_value: float | None = None
    uncertainty: float | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("name", self.name),
            ("units", self.units),
            ("method", self.method),
            ("evidence_id", self.evidence_id),
        ):
            _validate_nonempty_string(
                value,
                name,
            )

        if self.classification not in (
            CALIBRATION_VALUE_CLASSES
        ):
            raise ValueError(
                "classification must be one of: "
                + ", ".join(CALIBRATION_VALUE_CLASSES)
            )

        _validate_optional_finite(
            self.nominal_value,
            "nominal_value",
        )

        _validate_optional_finite(
            self.uncertainty,
            "uncertainty",
        )

        if (
            self.uncertainty is not None
            and self.uncertainty < 0
        ):
            raise ValueError(
                "uncertainty must be non-negative"
            )

        if (
            self.classification == "UNKNOWN"
            and self.nominal_value is not None
        ):
            raise ValueError(
                "UNKNOWN calibration value must not "
                "declare a nominal value"
            )

        if (
            self.classification != "UNKNOWN"
            and self.nominal_value is None
        ):
            raise ValueError(
                "resolved calibration value must "
                "declare a nominal value"
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "classification": self.classification,
            "units": self.units,
            "method": self.method,
            "evidence_id": self.evidence_id,
            "nominal_value": self.nominal_value,
            "uncertainty": self.uncertainty,
        }


@dataclass(frozen=True)
class N0Calibration:
    calibration_id: str
    profile_id: str
    realization_status: str

    valid_from: str
    valid_until: str

    values: tuple[CalibrationValue, ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("calibration_id", self.calibration_id),
            ("profile_id", self.profile_id),
            ("valid_from", self.valid_from),
            ("valid_until", self.valid_until),
        ):
            _validate_nonempty_string(
                value,
                name,
            )

        if self.realization_status not in (
            CALIBRATION_REALIZATION_STATUSES
        ):
            raise ValueError(
                "realization_status must be one of: "
                + ", ".join(
                    CALIBRATION_REALIZATION_STATUSES
                )
            )

        if any(
            not isinstance(value, CalibrationValue)
            for value in self.values
        ):
            raise ValueError(
                "values must contain CalibrationValue objects"
            )

        names = tuple(
            value.name
            for value in self.values
        )

        if len(set(names)) != len(names):
            raise ValueError(
                "calibration value names must be unique"
            )

        if names != tuple(sorted(names)):
            raise ValueError(
                "calibration values must be sorted by name"
            )

        missing = sorted(
            set(REQUIRED_MAPPING_KEYS)
            - set(names)
        )

        if missing:
            raise ValueError(
                "missing required calibration mapping(s): "
                + ", ".join(missing)
            )

        if self.realization_status == "physical":
            bad = [
                value.name
                for value in self.values
                if (
                    value.classification != "UNKNOWN"
                    and (
                        not value.evidence_id
                        or value.evidence_id.startswith(
                            "simulated:"
                        )
                    )
                )
            ]

            if bad:
                raise ValueError(
                    "physical calibration contains "
                    "non-physical evidence binding(s): "
                    + ", ".join(sorted(bad))
                )

    @property
    def schema(self) -> str:
        return N0_CALIBRATION_SCHEMA

    @property
    def unresolved_parameters(self) -> tuple[str, ...]:
        return tuple(
            value.name
            for value in self.values
            if value.classification == "UNKNOWN"
        )

    @property
    def is_complete(self) -> bool:
        return not self.unresolved_parameters

    def require_complete_for_physical_decision(
        self,
    ) -> None:
        unresolved = self.unresolved_parameters

        if unresolved:
            raise RuntimeError(
                "physical decision blocked by unresolved "
                "calibration parameter(s): "
                + ", ".join(unresolved)
            )

        if self.realization_status != "physical":
            raise RuntimeError(
                "physical decision requires physical calibration"
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "calibration_id": self.calibration_id,
            "profile_id": self.profile_id,
            "realization_status": self.realization_status,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
            "values": [
                value.to_dict()
                for value in self.values
            ],
            "unresolved_parameters": (
                self.unresolved_parameters
            ),
        }

    @property
    def canonical_json(self) -> str:
        return canonical_json_value(
            self.to_dict()
        )

    @property
    def calibration_hash(self) -> str:
        return canonical_sha256_value(
            self.to_dict()
        )


def build_simulated_n0_calibration() -> N0Calibration:
    raw_values = (
        CalibrationValue(
            name="command_phase_rad",
            classification="DIRECTLY_MEASURABLE",
            units="rad",
            method="simulated-command-register",
            evidence_id="simulated:command-phase-v1",
            nominal_value=0.0,
            uncertainty=0.0,
        ),
        CalibrationValue(
            name="detector_gain",
            classification="CALIBRATED",
            units="dimensionless",
            method="simulated-gain-calibration",
            evidence_id="simulated:detector-gain-v1",
            nominal_value=1.0,
            uncertainty=0.0,
        ),
        CalibrationValue(
            name="detector_offset",
            classification="CALIBRATED",
            units="dimensionless",
            method="simulated-offset-calibration",
            evidence_id="simulated:detector-offset-v1",
            nominal_value=0.0,
            uncertainty=0.0,
        ),
        CalibrationValue(
            name="measurement_efficiency_eta",
            classification="MODEL_DEPENDENT",
            units="dimensionless",
            method="simulated-model-parameter",
            evidence_id="simulated:eta-v1",
            nominal_value=0.8,
            uncertainty=0.0,
        ),
        CalibrationValue(
            name="measurement_rate_gamma_m",
            classification="MODEL_DEPENDENT",
            units="inverse_model_time",
            method="simulated-model-parameter",
            evidence_id="simulated:gamma-m-v1",
            nominal_value=1.0,
            uncertainty=0.0,
        ),
        CalibrationValue(
            name="model_time_scale",
            classification="MODEL_DEPENDENT",
            units="model_time_per_second",
            method="simulated-time-map",
            evidence_id="simulated:time-scale-v1",
            nominal_value=1.0,
            uncertainty=0.0,
        ),
        CalibrationValue(
            name="probe_strength",
            classification="MODEL_DEPENDENT",
            units="dimensionless",
            method="simulated-model-parameter",
            evidence_id="simulated:probe-strength-v1",
            nominal_value=1.0,
            uncertainty=0.0,
        ),
        CalibrationValue(
            name="reference_amplitude",
            classification="CALIBRATED",
            units="dimensionless",
            method="simulated-reference",
            evidence_id="simulated:reference-amplitude-v1",
            nominal_value=1.0,
            uncertainty=0.0,
        ),
        CalibrationValue(
            name="reference_frequency_hz",
            classification="CALIBRATED",
            units="Hz",
            method="simulated-reference",
            evidence_id="simulated:reference-frequency-v1",
            nominal_value=5.0e9,
            uncertainty=0.0,
        ),
        CalibrationValue(
            name="reference_phase_rad",
            classification="CALIBRATED",
            units="rad",
            method="simulated-reference",
            evidence_id="simulated:reference-phase-v1",
            nominal_value=0.0,
            uncertainty=0.0,
        ),
        CalibrationValue(
            name="sample_period_s",
            classification="DIRECTLY_MEASURABLE",
            units="s",
            method="simulated-sample-clock",
            evidence_id="simulated:sample-period-v1",
            nominal_value=0.01,
            uncertainty=0.0,
        ),
    )

    return N0Calibration(
        calibration_id="SIMULATED-CALIBRATION-v1",
        profile_id="CPC-SHOR-N0-PHYSICAL-PROFILE-v1",
        realization_status="simulated",
        valid_from="SIMULATED-BEGIN",
        valid_until="SIMULATED-END",
        values=tuple(
            sorted(
                raw_values,
                key=lambda item: item.name,
            )
        ),
    )
