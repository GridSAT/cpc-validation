"""Prospective deterministic ledger tests; no execution or record generation."""
import hashlib

import pytest

from src.dyadic_phase_p4_ledger import build_ledger, validate_ledger


def make_ledger():
    return build_ledger(
        "P4-ledger-unit",
        [{"fixture_id": "N7-a3", "N": 7, "a": 3}],
        calibration_grid={"N7-a3": [0, 1]},
        calibration_n=2,
        bundles=2,
        k=4,
    )


def test_deterministic_population_roles_and_seed_contract():
    ledger = make_ledger()
    assert ledger == make_ledger()
    assert validate_ledger(ledger) is ledger
    rows = ledger["trials"]
    calibration = [r for r in rows if r["role"] == "fixed-sector-diagnostic"]
    operational = [r for r in rows if r["role"] == "operational"]
    assert len(rows) == 12
    assert {(r["diagnostic_sector"], r["index"]) for r in calibration} == {
        (0, 0), (0, 1), (1, 0), (1, 1)
    }
    assert {(r["bundle"], r["slot"]) for r in operational} == {
        (bundle, slot) for bundle in range(2) for slot in range(4)
    }
    assert all("diagnostic_sector" not in r for r in operational)
    assert len({r["trial_id"] for r in rows}) == len(rows)
    assert len({tuple(r["seed"]) for r in rows}) == len(rows)
    for row in rows:
        message = "\0".join(
            ("cpc-shor-p4-seed/1", "P4-ledger-unit", row["trial_id"])
        ).encode("utf-8")
        encoded = b"".join(word.to_bytes(4, "big") for word in row["seed"])
        assert encoded == hashlib.sha256(message).digest()
        assert row["output_directory"] == "trials/" + row["trial_id"]
        assert row["expected_artifacts"] == [
            "record.npz", "inference.npz", "profile.json", "summary.json"
        ]


@pytest.mark.parametrize(
    "damage", ["duplicate", "seed", "missing", "advice", "slot", "role", "path", "fixture"]
)
def test_malformed_ledger_rejected(damage):
    ledger = make_ledger()
    row = ledger["trials"][-1]
    if damage == "duplicate":
        ledger["trials"].append(dict(row))
    elif damage == "seed":
        row["seed"][0] ^= 1
    elif damage == "missing":
        ledger["trials"].pop()
    elif damage == "advice":
        row["r"] = 6
    elif damage == "slot":
        row["slot"] = 0
    elif damage == "role":
        row["role"] = "fixed-sector-diagnostic"
    elif damage == "path":
        row["output_directory"] = "../escaped"
    else:
        row["N"] = 15
    with pytest.raises((ValueError, TypeError)):
        validate_ledger(ledger)
