from __future__ import annotations

from dataclasses import replace
import math

from src.n0_bosonic_model import N0BosonicModel
from src.n0_calibration import (
    CalibrationValue,
    N0Calibration,
)


def weaken_stabilization(
    model: N0BosonicModel,
    *,
    factor: float,
) -> N0BosonicModel:
    if (
        not isinstance(factor, (int, float))
        or isinstance(factor, bool)
        or not math.isfinite(factor)
        or not (0.0 <= factor <= 1.0)
    ):
        raise ValueError(
            "factor must lie in [0, 1]"
        )

    return replace(
        model,
        kappa_2=(
            model.kappa_2
            * float(factor)
        ),
    )


def increase_single_photon_loss(
    model: N0BosonicModel,
    *,
    added_kappa_1: float,
) -> N0BosonicModel:
    if (
        not isinstance(
            added_kappa_1,
            (int, float),
        )
        or isinstance(
            added_kappa_1,
            bool,
        )
        or not math.isfinite(
            added_kappa_1
        )
        or added_kappa_1 < 0
    ):
        raise ValueError(
            "added_kappa_1 must be finite and non-negative"
        )

    return replace(
        model,
        kappa_1=(
            model.kappa_1
            + float(added_kappa_1)
        ),
    )


def increase_dephasing(
    model: N0BosonicModel,
    *,
    added_kappa_phi: float,
) -> N0BosonicModel:
    if (
        not isinstance(
            added_kappa_phi,
            (int, float),
        )
        or isinstance(
            added_kappa_phi,
            bool,
        )
        or not math.isfinite(
            added_kappa_phi
        )
        or added_kappa_phi < 0
    ):
        raise ValueError(
            "added_kappa_phi must be finite and non-negative"
        )

    return replace(
        model,
        kappa_phi=(
            model.kappa_phi
            + float(added_kappa_phi)
        ),
    )


def _replace_calibration_value(
    calibration: N0Calibration,
    *,
    name: str,
    value: float,
    evidence_id: str,
) -> N0Calibration:
    found = False
    replaced: list[CalibrationValue] = []

    for item in calibration.values:
        if item.name != name:
            replaced.append(
                item
            )
            continue

        found = True

        replaced.append(
            CalibrationValue(
                name=item.name,
                classification=item.classification,
                units=item.units,
                method=(
                    item.method
                    + "+fault-injection"
                ),
                evidence_id=evidence_id,
                nominal_value=float(value),
                uncertainty=item.uncertainty,
            )
        )

    if not found:
        raise ValueError(
            f"calibration value not found: {name}"
        )

    return N0Calibration(
        calibration_id=(
            calibration.calibration_id
            + "-FAULTED"
        ),
        profile_id=calibration.profile_id,
        realization_status=(
            calibration.realization_status
        ),
        valid_from=calibration.valid_from,
        valid_until=calibration.valid_until,
        values=tuple(
            sorted(
                replaced,
                key=lambda item: item.name,
            )
        ),
    )


def reduce_measurement_efficiency(
    calibration: N0Calibration,
    *,
    eta: float,
) -> N0Calibration:
    if (
        not isinstance(eta, (int, float))
        or isinstance(eta, bool)
        or not math.isfinite(eta)
        or not (0.0 <= eta <= 1.0)
    ):
        raise ValueError(
            "eta must lie in [0, 1]"
        )

    return _replace_calibration_value(
        calibration,
        name="measurement_efficiency_eta",
        value=float(eta),
        evidence_id=(
            "simulated:fault-reduced-eta-v1"
        ),
    )


def change_detector_gain(
    calibration: N0Calibration,
    *,
    gain: float,
) -> N0Calibration:
    if (
        not isinstance(gain, (int, float))
        or isinstance(gain, bool)
        or not math.isfinite(gain)
        or gain == 0.0
    ):
        raise ValueError(
            "gain must be finite and nonzero"
        )

    return _replace_calibration_value(
        calibration,
        name="detector_gain",
        value=float(gain),
        evidence_id=(
            "simulated:fault-detector-gain-v1"
        ),
    )
