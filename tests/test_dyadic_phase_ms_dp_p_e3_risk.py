"""Prospective deterministic tests; synthetic premises are not calibration evidence."""
from copy import deepcopy
from fractions import Fraction as F

import pytest

from p4_helpers import binding, phase
from src import dyadic_phase_ms_dp_p_e3_risk as e3
from src.dyadic_phase_p4 import reconstruct
from src.dyadic_phase_p4_types import Policy, identity


CLASSES = [[0, 1], [1, 6], [1, 4], [1, 3],
           [1, 2], [2, 3], [3, 4], [5, 6]]
ACQUISITION = "synthetic-e3/N15-a2"
ASSUMPTIONS = [
    "sealed finite DP-S equality-in-law simulator and matched-reference estimator",
    "within-phase-class iid diagnostic acquisitions",
    "same exact local phase implies same local finite instrument under the sealed ideal model",
    "fresh operational preparations and innovations independent of calibration",
    "operational local phase laws are among the eight calibrated phase classes",
    "seven-channel union allocation p_local<=1/140",
    "four fresh phase estimates per bundle",
    "correct frozen POINT arithmetic and provenance",
    "no data-selected estimator, schedule, threshold, retry, replacement, or reseeding",
]


def registry():
    plan = {
        "run_identity": "synthetic-e3",
        "fixtures": [{"fixture_id": "N15-a2", "N": 15, "a": 2}],
        "calibration": {"phase_classes": deepcopy(CLASSES)},
        "parents": {"calibration_amendment_sha256": "5" * 64},
    }
    return e3.build_e3_registry(
        plan,
        calibration_primary_sha256="1" * 64,
        calibration_independent_sha256="2" * 64,
        ledger_sha256="3" * 64,
        authorization_sha256="4" * 64,
    )


def resign(value):
    unsigned = {k: v for k, v in value.items() if k != "identity"}
    value["identity"] = identity("ms-dp-p-e3-calibrated-registry", unsigned)
    return value


def validate(value, **changes):
    args = dict(N=15, a=2, acquisition_id=ACQUISITION, trials=4)
    args.update(changes)
    return e3.validate_e3_registry(value, value["identity"], **args)


def payloads(values=(F(0), F(1, 4), F(1, 2), F(3, 4))):
    result = [phase(15, 2, value, slot=i) for i, value in enumerate(values)]
    for item in result:
        item["acquisition_id"] = ACQUISITION
    return result


def wrapped(ps, reg):
    policy = Policy()
    return e3.reconstruct_calibrated_e3(
        15, 2, ps, policy=policy, **binding(ps, policy),
        registry=reg,
        expected_registry_identity=None if reg is None else reg["identity"],
    )


def test_registry_contract_and_exact_allocations():
    r = registry()
    assert r["schema"] == "cpc-shor-ms-dp-p-e3-calibrated-registry/1"
    assert r["run_identity"] == "synthetic-e3"
    assert r["fixtures"] == [{"fixture_id": "N15-a2", "N": 15, "a": 2}]
    assert (r["decoder"], r["k"]) == ("POINT", 4)
    assert r["phase_classes"] == CLASSES
    assert r["per_phase_class_n"] == 1024
    assert r["per_phase_class_max_errors"] == 0
    assert r["local_error_boundary"] == [1, 140]
    assert r["conditional_beta"] == [[1, 20]] * 4
    assert r["exception"] == {
        "event": "false admission of at least one phase-class calibration cell",
        "bound": [1, 100],
    }
    assert r["wrong_acceptance_bound"] == [21, 100]
    assert r["risk_type"] == (
        "unconditional_wrong_acceptance_per_bundle_over_calibration_and_evaluation"
    )
    assert r["conditioning_event"] == (
        "all eight preregistered phase-class calibration cells pass in primary "
        "and independent reductions"
    )
    assert r["assumptions"] == ASSUMPTIONS
    for key, digit in [
        ("calibration_primary_sha256", "1"),
        ("calibration_independent_sha256", "2"),
        ("ledger_sha256", "3"),
        ("authorization_sha256", "4"),
        ("calibration_amendment_sha256", "5"),
    ]:
        assert r[key] == digit * 64
    assert resign(deepcopy(r)) == r == registry()
    assert validate(r) is r
    assert len(r["phase_classes"]) * r["per_phase_class_n"] == 8192
    assert 7 * F(*r["local_error_boundary"]) == F(1, 20)
    beta = sum((F(*x) for x in r["conditional_beta"]), F(0))
    assert beta == F(1, 5)
    assert beta + F(*r["exception"]["bound"]) == F(*r["wrong_acceptance_bound"])


def test_registry_rejects_identity_domain_and_bound_faults():
    r = registry()
    with pytest.raises(ValueError, match="identity"):
        e3.validate_e3_registry(
            r, "f" * 64, N=15, a=2,
            acquisition_id=ACQUISITION, trials=4,
        )
    changed = deepcopy(r)
    changed["ledger_sha256"] = "6" * 64
    with pytest.raises(ValueError, match="identity"):
        validate(changed)
    changed = deepcopy(r)
    changed["identity"] = "f" * 64
    with pytest.raises(ValueError, match="identity"):
        validate(changed)

    faults = [
        ("schema", "wrong", "schema"),
        ("decoder", "SET", "domain"),
        ("k", 3, "domain"),
        ("conditional_beta", [[1, 21]] * 4, "conditional beta"),
        ("wrong_acceptance_bound", [1, 5], "wrong-acceptance"),
        ("exception", {"event": "other", "bound": [1, 100]}, "exception"),
        ("exception", {"event": r["exception"]["event"],
                       "bound": [1, 200]}, "exception"),
        ("fixtures", [], "population"),
        ("fixtures", r["fixtures"] * 2, "population"),
    ]
    for key, value, message in faults:
        changed = deepcopy(r)
        changed[key] = value
        resign(changed)
        with pytest.raises(ValueError, match=message):
            validate(changed)
    for changes, message in [
        ({"trials": 3}, "domain"),
        ({"N": 7}, "population"),
        ({"a": 4}, "population"),
        ({"acquisition_id": "other"}, "population"),
    ]:
        with pytest.raises(ValueError, match=message):
            validate(r, **changes)


def test_calibration_content_is_bound_but_not_independently_verified():
    r = registry()
    changed = deepcopy(r)
    changed["phase_classes"] = [[0, 1]]
    changed["per_phase_class_n"] = 1
    changed["per_phase_class_max_errors"] = 1
    changed["local_error_boundary"] = [1, 2]
    changed["assumptions"] = ["Synthetic changed premise; not scientific approval"]
    with pytest.raises(ValueError, match="identity"):
        validate(changed)
    resign(changed)
    assert changed["identity"] != r["identity"]
    # Supplying a new trusted identity changes the premises. This is not proof
    # of pooling, calibration success, or empirical error probabilities.
    assert validate(changed) is changed


def test_actual_p4_reconstruction_and_registry_promotion():
    ps = payloads()
    policy = Policy()
    b = binding(ps, policy)
    baseline = reconstruct(
        15, 2, ps, decoder="POINT", claim_type="P4-BE",
        policy=policy, **b,
    )
    assert baseline["status"] == "UNVERIFIED_CANDIDATE"
    assert baseline["candidate_R"] == 4 and not baseline["accepted"]
    assert wrapped(ps, None) == baseline
    exact = reconstruct(
        15, 2, ps, decoder="POINT", claim_type="P4-EXACT",
        policy=policy, **b,
    )
    assert exact["status"] == "CERTIFIED_EXACT_ORDER"
    r = registry()
    out = wrapped(ps, r)
    assert out["status"] == "CERTIFIED_BOUNDED_ERROR_ORDER"
    assert out["claim_type"] == "P4-BE"
    assert out["accepted"] is True and out["candidate_R"] == 4
    assert out["modular_residue"] == 1
    assert out["factorization_required"] is False
    assert out["conditional_accepted_output_error_bound"] is None
    assert out["risk_type"] == r["risk_type"]
    assert out["wrong_acceptance_bound"] == [21, 100]
    assert out["conditional_beta"] == r["conditional_beta"]
    assert out["calibration_exception"] == r["exception"]
    assert out["conditioning_event"] == r["conditioning_event"]
    assert out["validity_assumptions"] == r["assumptions"]
    assert out["calibrated_registry_identity"] == r["identity"]
    assert "reason" not in out
    unsigned = {k: v for k, v in out.items() if k != "identity"}
    assert out["identity"] == identity("reconstruction-result", unsigned)

    bad = deepcopy(r)
    bad["conditional_beta"] = [[0, 1]] * 4
    resign(bad)
    with pytest.raises(ValueError, match="conditional beta"):
        wrapped(ps, bad)
    b["input_binding"]["preparation_model"] = "same-sector-copy"
    with pytest.raises(ValueError):
        e3.reconstruct_calibrated_e3(
            15, 2, ps, policy=policy, **b,
            registry=r, expected_registry_identity=r["identity"],
        )


def test_actual_modular_failure_is_not_promoted():
    ps = payloads((F(0),) * 4)
    policy = Policy()
    baseline = reconstruct(
        15, 2, ps, decoder="POINT", claim_type="P4-BE",
        policy=policy, **binding(ps, policy),
    )
    assert baseline["candidate_R"] == 1
    assert pow(2, 1, 15) != 1
    assert baseline["status"] == "VERIFICATION_FAILURE"
    assert not baseline["accepted"]
    assert wrapped(ps, registry()) == baseline


@pytest.mark.parametrize("candidate", [None, True, 0, 15, 3])
def test_defensive_candidate_guard(candidate, monkeypatch):
    # Synthetic upstream fault injection, not a claim about actual P4 output.
    upstream = {
        "status": "UNVERIFIED_CANDIDATE",
        "candidate_R": candidate,
        "accepted": False,
    }
    monkeypatch.setattr(e3, "reconstruct", lambda *args, **kwargs: upstream)
    assert wrapped(payloads(), registry()) is upstream
