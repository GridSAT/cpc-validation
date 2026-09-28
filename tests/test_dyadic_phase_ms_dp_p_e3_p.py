from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

import pytest

from src.dyadic_phase_ms_dp_p_e3_risk import (
    build_e3_registry, reconstruct_calibrated_e3, validate_e3_registry,
)
from src.dyadic_phase_ms_dp_p_e3 import LocalPhaseEvidence, make_p4_phase_payload
from src.dyadic_phase_ms_dp_p import required_highest_scale
from p4_helpers import binding as input_binding
from src.dyadic_phase_p4_types import Policy
from src.dyadic_phase_p4 import reconstruct
from src.dyadic_phase_p4_validation import independent_audit

ROOT = Path(__file__).resolve().parents[1]
POLICY_FIXTURE = ROOT/"tests/fixtures/ms_dp_p/e3/arithmetic-policy.json"


def H(x):
    return hashlib.sha256(x.encode()).hexdigest()


def policy():
    d=json.loads(POLICY_FIXTURE.read_text())
    return Policy(**d["arithmetic_policy"])


def rows(N, a, theta, trial):
    J=required_highest_scale(N)
    out=[]
    for j in range(J+1):
        q=((1<<j)*theta)%1
        out.append(LocalPhaseEvidence(
            scale=j, estimate=q, data_register_id=trial+"/data",
            trial_id=trial, channel_id=trial+f"/j{j}",
            record_sha256=H(f"r{j}"), inference_sha256=H("i"),
            profile_sha256=H("p"),
        ))
    return out


def payload(N,a,theta,trial):
    p,_=make_p4_phase_payload(
        N,a,rows(N,a,theta,trial),
        acquisition_id="MS-DP-P-E3-v1/N15-a2",
        bundle_record_sha256=H("record"+trial),
        bundle_inference_sha256=H("infer"+trial),
        bundle_profile_sha256=H("profile"+trial),
    )
    return p


def plan():
    return {
        "run_identity":"MS-DP-P-E3-v1",
        "fixtures":[{"fixture_id":"N15-a2","N":15,"a":2}],
        "calibration":{"phase_classes":[[0,1],[1,6],[1,4],[1,3],[1,2],[2,3],[3,4],[5,6]]},
        "parents":{"calibration_amendment_sha256":"0"*64},
    }


def test_registry_exact_risk_budget():
    r=build_e3_registry(
        plan(), calibration_primary_sha256=H("cp"),
        calibration_independent_sha256=H("ci"),
        ledger_sha256=H("l"), authorization_sha256=H("a"),
    )
    validate_e3_registry(
        r,r["identity"],N=15,a=2,
        acquisition_id="MS-DP-P-E3-v1/N15-a2",trials=4,
    )
    assert r["wrong_acceptance_bound"]==[21,100]
    assert r["conditional_beta"]==[[1,20]]*4
    assert r["exception"]["bound"]==[1,100]


def test_frozen_point_bundle_reconstructs_order4_and_e3_be_wraps():
    ps=[
        payload(15,2,Fraction(0), "t0"),
        payload(15,2,Fraction(1,4), "t1"),
        payload(15,2,Fraction(1,2), "t2"),
        payload(15,2,Fraction(3,4), "t3"),
    ]
    pol=policy()
    binding_pair=input_binding(ps,pol)
    assert set(binding_pair)=={"input_binding","expected_binding_identity"}
    bind=binding_pair["input_binding"]
    bid=binding_pair["expected_binding_identity"]
    assert isinstance(bind,dict)
    assert isinstance(bid,str) and len(bid)==64
    exact=reconstruct(
        15,2,ps,decoder="POINT",claim_type="P4-EXACT",
        policy=pol,input_binding=bind,expected_binding_identity=bid,
        error_contract=None,expected_contract_identity=None,
        proof_registry=None,expected_registry_identity=None,
    )
    assert exact["candidate_R"]==4
    assert exact["accepted"] is True
    assert exact["status"]=="CERTIFIED_EXACT_ORDER"
    independent_audit(exact,ps,pol,maximum_modulus=15)
    reg=build_e3_registry(
        plan(), calibration_primary_sha256=H("cp"),
        calibration_independent_sha256=H("ci"),
        ledger_sha256=H("l"), authorization_sha256=H("a"),
    )
    out=reconstruct_calibrated_e3(
        15,2,ps,policy=pol,input_binding=bind,
        expected_binding_identity=bid,
        registry=reg,expected_registry_identity=reg["identity"],
    )
    assert out["candidate_R"]==4
    assert out["accepted"] is True
    assert out["status"]=="CERTIFIED_BOUNDED_ERROR_ORDER"
    assert out["wrong_acceptance_bound"]==[21,100]


def test_registry_rejects_wrong_population():
    r=build_e3_registry(
        plan(), calibration_primary_sha256=H("cp"),
        calibration_independent_sha256=H("ci"),
        ledger_sha256=H("l"), authorization_sha256=H("a"),
    )
    with pytest.raises(ValueError):
        validate_e3_registry(
            r,r["identity"],N=7,a=2,
            acquisition_id="MS-DP-P-E3-v1/N7-a2",trials=4,
        )
