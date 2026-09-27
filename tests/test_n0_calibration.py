import dataclasses

import pytest

from src.n0_calibration import (
    CalibrationValue,
    N0Calibration,
    REQUIRED_MAPPING_KEYS,
    build_simulated_n0_calibration,
)


def test_simulated_calibration_is_complete():
    calibration = build_simulated_n0_calibration()

    assert calibration.realization_status == "simulated"
    assert calibration.is_complete
    assert calibration.unresolved_parameters == ()

    names = {
        value.name
        for value in calibration.values
    }

    assert set(REQUIRED_MAPPING_KEYS).issubset(names)


def test_calibration_is_immutable():
    calibration = build_simulated_n0_calibration()

    with pytest.raises(
        dataclasses.FrozenInstanceError
    ):
        calibration.calibration_id = "changed"


def test_unknown_value_must_not_have_nominal_value():
    with pytest.raises(
        ValueError,
        match="must not declare",
    ):
        CalibrationValue(
            name="x",
            classification="UNKNOWN",
            units="arb",
            method="unknown",
            evidence_id="unknown:x",
            nominal_value=1.0,
        )


def test_resolved_value_requires_nominal_value():
    with pytest.raises(
        ValueError,
        match="must declare",
    ):
        CalibrationValue(
            name="x",
            classification="CALIBRATED",
            units="arb",
            method="test",
            evidence_id="physical:test",
        )


def test_missing_required_mapping_fails_closed():
    calibration = build_simulated_n0_calibration()

    values = tuple(
        value
        for value in calibration.values
        if value.name != "measurement_efficiency_eta"
    )

    with pytest.raises(
        ValueError,
        match="missing required",
    ):
        N0Calibration(
            calibration_id="test",
            profile_id=calibration.profile_id,
            realization_status="simulated",
            valid_from="a",
            valid_until="b",
            values=values,
        )


def test_simulated_calibration_cannot_authorize_physical_decision():
    calibration = build_simulated_n0_calibration()

    with pytest.raises(
        RuntimeError,
        match="requires physical calibration",
    ):
        calibration.require_complete_for_physical_decision()


def test_physical_calibration_rejects_simulated_evidence():
    calibration = build_simulated_n0_calibration()

    with pytest.raises(
        ValueError,
        match="non-physical evidence",
    ):
        N0Calibration(
            calibration_id="physical-calibration",
            profile_id=calibration.profile_id,
            realization_status="physical",
            valid_from="a",
            valid_until="b",
            values=calibration.values,
        )


def test_hash_is_deterministic():
    first = build_simulated_n0_calibration()
    second = build_simulated_n0_calibration()

    assert (
        first.calibration_hash
        == second.calibration_hash
    )
