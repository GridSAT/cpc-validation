"""Prospective acquisition boundary checks; no generator or records."""
import inspect

import pytest

import src.dyadic_phase_p4_acquisition as acquisition


def contract():
    return {
        "g": .35355339059327373, "Gamma": 1.,
        "schedule": {
            "eta": .8, "dt": .04, "burn": 16., "window": 2048.,
            "transfer_phases": [.7] * 3,
            "reset_time": .25, "retune_time": .1, "dead_time": .5,
        },
        "worker_caps": {
            "worker_memory_bytes": 536870912,
            "record_bytes": 8000000, "worker_seconds": 600,
        },
        "inference": {
            "coarse_grid": 256, "fine_grid": 512, "confidence_alpha": .05,
        },
    }


def trial():
    return {"N": 7, "profile": "DP-P", "scales": [0, 1, 2]}


def test_storage_contract():
    result = acquisition.validate_worker_contract(contract(), {}, trial())
    assert result == {
        "record_storage_upper_bound_bytes": 4981760,
        "full_register_dimension": 64,
    }


@pytest.mark.parametrize("damage", [
    "small-record", "small-memory", "dt", "grid", "reference",
])
def test_invalid_contract_rejected(damage):
    plan = contract()
    if damage == "small-record":
        plan["worker_caps"]["record_bytes"] = 1
    elif damage == "small-memory":
        plan["worker_caps"]["worker_memory_bytes"] = 1
    elif damage == "dt":
        plan["schedule"]["dt"] = .1
    elif damage == "grid":
        plan["inference"]["fine_grid"] = 1000000
    else:
        plan["schedule"]["transfer_phases"] = [.7]
    with pytest.raises((ValueError, MemoryError)):
        acquisition.validate_worker_contract(plan, {}, trial())


def test_missing_authorization_precedes_execution(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("execution reached before authorization")

    monkeypatch.setattr(acquisition, "claim_trial", forbidden)
    monkeypatch.setattr(acquisition, "_complete_trial", forbidden)
    monkeypatch.setattr(acquisition.resource, "setrlimit", forbidden)
    with pytest.raises(PermissionError, match="human execution GO"):
        acquisition.execute_operational_trial(
            "synthetic-trial",
            acceptance_path=tmp_path / "absent-acceptance.json",
            acceptance_sha256="0" * 64,
            seal_path=tmp_path / "absent-seal.json",
            seal_sha256="1" * 64,
            authorization_path=None,
        )
    assert list(tmp_path.iterdir()) == []


def test_operational_signature_excludes_preparation_advice():
    assert set(inspect.signature(acquisition.execute_operational_trial).parameters) == {
        "trial_id", "acceptance_path", "acceptance_sha256",
        "seal_path", "seal_sha256", "authorization_path",
    }
