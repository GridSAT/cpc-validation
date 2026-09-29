"""Prospective deterministic calibration checks; no acquisition or PASS claim."""
import numpy as np
import pytest

import src.dyadic_phase_p4_acquisition as acquisition
import src.dyadic_phase_p4_calibration as calibration
from src.dyadic_phase_p4_instrument import Bank
from src.dyadic_phase_p4_ledger import build_ledger
from src.dyadic_phase_p4_runtime import claim_trial, receipt_trial, sha256, write_once
from src.dyadic_phase_p4_types import Policy


def ledger():
    return build_ledger(
        "synthetic-calibration", [{"fixture_id": "N7-a3", "N": 7, "a": 3}],
        calibration_grid={"N7-a3": [1]}, calibration_n=1, bundles=1, k=1,
    )


@pytest.mark.parametrize("N,a,orbit", [(7, 3, [1, 3, 2, 6, 4, 5]),
                                      (15, 2, [1, 2, 4, 8])])
def test_diagnostic_state(N, a, orbit):
    model = Bank(N, a)
    ket = calibration.diagnostic_initial(model, 1)
    expected = np.zeros(model.dimension, complex)
    expected[orbit] = np.exp(-2j * np.pi * np.arange(len(orbit)) / len(orbit)) / np.sqrt(len(orbit))
    np.testing.assert_allclose(ket, expected, rtol=0, atol=1e-14)
    assert abs(np.vdot(ket, ket) - 1) < 1e-14
    moved = np.zeros_like(ket)
    for y in range(N):
        moved[a * y % N] = ket[y]
    np.testing.assert_allclose(moved, np.exp(2j * np.pi / len(orbit)) * ket,
                               rtol=0, atol=1e-14)
    assert np.array_equal(ket, calibration.diagnostic_initial(model, 1))


@pytest.mark.parametrize("sector", [-1, 6, True])
def test_invalid_sector(sector):
    with pytest.raises(ValueError, match="diagnostic orbit/sector"):
        calibration.diagnostic_initial(Bank(7, 3), sector)


def retained(tmp_path, estimate):
    trial = ledger()["trials"][0]
    (tmp_path / "trials").mkdir()
    path = claim_trial(tmp_path, trial, acceptance_sha256="0" * 64,
                       source_seal_sha256="1" * 64)
    for name in ("record.npz", "inference.npz"):
        write_once(path / name, {"synthetic_filesystem_fixture": True})
    write_once(path / "profile.json", {
        "trial_id": trial["trial_id"], "preparation_role": trial["role"],
        "arithmetic": {"N": 7, "a": 3, "scales": [0, 1, 2]},
    })
    write_once(path / "summary.json", {
        "trial_id": trial["trial_id"],
        "profile_sha256": sha256(path / "profile.json"),
        "record_sha256": sha256(path / "record.npz"),
        "inference_sha256": sha256(path / "inference.npz"),
        "inference": {"estimate": estimate},
    })
    receipt_trial(path, trial)
    return path, trial


@pytest.mark.parametrize("estimate,correct", [(1 / 6, True), (0., False), (.125, False)])
def test_retained_score_is_read_only(tmp_path, estimate, correct):
    path, trial = retained(tmp_path, estimate)
    before = {p.name: (p.read_bytes(), p.stat().st_mode) for p in path.iterdir()}
    score = calibration.score_calibration_trial(path, trial, Policy())
    assert score["correct_denominator"] is correct
    assert (score["diagnostic_order"], score["diagnostic_sector"]) == (6, 1)
    assert score["receipt_sha256"] == sha256(path / "RECEIPT.json")
    assert score["role"] == "post-inference calibration diagnostic only"
    assert {p.name: (p.read_bytes(), p.stat().st_mode) for p in path.iterdir()} == before


def test_changed_retained_artifact_rejected(tmp_path):
    path, trial = retained(tmp_path, 1 / 6)
    record = path / "record.npz"
    record.chmod(0o644)
    record.write_bytes(b"changed synthetic fixture")
    record.chmod(0o444)
    with pytest.raises(ValueError, match="immutable trial artifact changed"):
        calibration.score_calibration_trial(path, trial, Policy())


@pytest.mark.parametrize("guard", ["missing-GO", "wrong-role"])
def test_execution_stops_before_preparation_or_generation(tmp_path, monkeypatch, guard):
    def forbidden(*args, **kwargs):
        pytest.fail("execution reached beyond guard")

    for name in ("diagnostic_initial", "claim_trial", "_complete_trial"):
        monkeypatch.setattr(calibration, name, forbidden)
    monkeypatch.setattr(calibration.resource, "setrlimit", forbidden)
    trial_id = "synthetic-trial"
    error = PermissionError
    if guard == "wrong-role":
        population = ledger()
        trial_id = population["trials"][-1]["trial_id"]
        monkeypatch.setattr(acquisition, "load_execution_contract",
                            lambda *args: ({}, {}, population))
        error = ValueError
    with pytest.raises(error):
        calibration.execute_calibration_trial(
            trial_id, acceptance_path=tmp_path / "absent-plan.json",
            acceptance_sha256="0" * 64, seal_path=tmp_path / "absent-seal.json",
            seal_sha256="1" * 64, authorization_path=None,
        )
    assert list(tmp_path.iterdir()) == []
