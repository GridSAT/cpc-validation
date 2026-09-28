from __future__ import annotations

from fractions import Fraction
import hashlib
import inspect
import json
import math
from pathlib import Path

import pytest

from src.dyadic_phase_ms_dp_p import canonical_cycle, required_highest_scale
from src.dyadic_phase_ms_dp_p_e3 import (
    IntegrationError,
    LocalPhaseEvidence,
    decode_with_frozen_point,
    make_p4_phase_payload,
)

ROOT=Path(__file__).resolve().parents[1]
POLICY_FIXTURE=ROOT/"tests/fixtures/ms_dp_p/e3/arithmetic-policy.json"
P4_DECODE=ROOT/"src/dyadic_phase_p4_decode.py"
P4_TYPES=ROOT/"src/dyadic_phase_p4_types.py"

EXPECTED_DECODE="0a00d976d0db9de95916c17fe6215885fec677a7966dac7fa6b2c01f26669d7d"
EXPECTED_TYPES="5880d13a5d6175847fd3c289de7d36446694d2516705825136ce9920202e55a4"


def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()


def policy():
    from src.dyadic_phase_p4_types import Policy
    plan=json.loads(POLICY_FIXTURE.read_text())
    return Policy(**plan["arithmetic_policy"])


def order(N,a):
    x=1
    for r in range(1,N):
        x=x*a%N
        if x==1:return r
    raise AssertionError("order")


def rows_for(N,a,theta,errors=None):
    J=required_highest_scale(N)
    if errors is None: errors=[Fraction(0)]*(J+1)
    out=[]
    for j in range(J+1):
        est=canonical_cycle((1<<j)*theta+errors[j])
        tag=hashlib.sha256(f"{N}:{a}:{theta}:{j}".encode()).hexdigest()
        out.append(LocalPhaseEvidence(
            scale=j,estimate=est,data_register_id=f"T-{N}-{a}/data",
            trial_id=f"T-{N}-{a}",channel_id=f"T-{N}-{a}/signal/j{j}",
            record_sha256=tag,inference_sha256=tag,profile_sha256=tag,
        ))
    return tuple(out)


def bundle_hash(label):
    return hashlib.sha256(label.encode()).hexdigest()


@pytest.mark.parametrize("N,a",[(5,2),(7,2),(7,3),(15,2)])
def test_exact_all_sectors_serialize_and_decode_with_unchanged_point(N,a):
    p=policy()
    r=order(N,a)
    for s in range(r):
        theta=Fraction(s,r)
        payload,audit=make_p4_phase_payload(
            N,a,rows_for(N,a,theta),
            acquisition_id=f"E3/test/{N}/{a}",
            bundle_record_sha256=bundle_hash(f"r/{N}/{a}/{s}"),
            bundle_inference_sha256=bundle_hash(f"i/{N}/{a}/{s}"),
            bundle_profile_sha256=bundle_hash(f"p/{N}/{a}/{s}"),
        )
        view,candidate=decode_with_frozen_point(payload,p)
        assert candidate.complete is True
        assert candidate.values==(theta,)
        assert view.estimate==theta
        assert audit["truth_inputs_used"] is False
        assert audit["p4_decoder_changed"] is False


@pytest.mark.parametrize("N,a",[(5,2),(7,2),(7,3),(15,2)])
def test_adversarial_local_errors_still_enter_point_neighborhood(N,a):
    p=policy()
    r=order(N,a)
    D=Fraction(1,8)
    eps=Fraction(1,4096)
    J=required_highest_scale(N)
    patterns=[
        tuple((D-eps) if j%2==0 else -(D-eps) for j in range(J+1)),
        tuple(-(D-eps) if j%3==0 else (D-eps) for j in range(J+1)),
    ]
    for s in range(r):
        theta=Fraction(s,r)
        for k,errors in enumerate(patterns):
            payload,_=make_p4_phase_payload(
                N,a,rows_for(N,a,theta,errors),
                acquisition_id=f"E3/test/{N}/{a}",
                bundle_record_sha256=bundle_hash(f"r/{N}/{a}/{s}/{k}"),
                bundle_inference_sha256=bundle_hash(f"i/{N}/{a}/{s}/{k}"),
                bundle_profile_sha256=bundle_hash(f"p/{N}/{a}/{s}/{k}"),
            )
            _,candidate=decode_with_frozen_point(payload,p)
            assert candidate.complete is True
            assert candidate.values==(theta,)


def test_same_data_register_enforced():
    rows=list(rows_for(15,2,Fraction(1,4)))
    rows[3]=LocalPhaseEvidence(
        scale=rows[3].scale,estimate=rows[3].estimate,
        data_register_id="different/data",trial_id=rows[3].trial_id,
        channel_id=rows[3].channel_id,record_sha256=rows[3].record_sha256,
        inference_sha256=rows[3].inference_sha256,profile_sha256=rows[3].profile_sha256,
    )
    with pytest.raises(IntegrationError,match="data-register"):
        make_p4_phase_payload(
            15,2,rows,acquisition_id="E3/test",
            bundle_record_sha256=bundle_hash("r"),
            bundle_inference_sha256=bundle_hash("i"),
            bundle_profile_sha256=bundle_hash("p"),
        )


def test_missing_or_duplicate_scale_fails_closed():
    rows=list(rows_for(15,2,Fraction(1,4)))
    with pytest.raises(IntegrationError):
        make_p4_phase_payload(
            15,2,rows[:-1],acquisition_id="E3/test",
            bundle_record_sha256=bundle_hash("r"),
            bundle_inference_sha256=bundle_hash("i"),
            bundle_profile_sha256=bundle_hash("p"),
        )
    rows[2]=LocalPhaseEvidence(
        scale=1,estimate=rows[2].estimate,data_register_id=rows[2].data_register_id,
        trial_id=rows[2].trial_id,channel_id=rows[2].channel_id,
        record_sha256=rows[2].record_sha256,inference_sha256=rows[2].inference_sha256,
        profile_sha256=rows[2].profile_sha256,
    )
    with pytest.raises(IntegrationError,match="scales"):
        make_p4_phase_payload(
            15,2,rows,acquisition_id="E3/test",
            bundle_record_sha256=bundle_hash("r2"),
            bundle_inference_sha256=bundle_hash("i2"),
            bundle_profile_sha256=bundle_hash("p2"),
        )


def test_truth_fields_rejected_by_mapping_constructor():
    base={
        "scale":0,"estimate":Fraction(0),"data_register_id":"d","trial_id":"t","channel_id":"c",
        "record_sha256":"0"*64,"inference_sha256":"1"*64,"profile_sha256":"2"*64,
        "true_phase":Fraction(0),
    }
    with pytest.raises(IntegrationError,match="truth"):
        LocalPhaseEvidence.from_mapping(base)


def test_frozen_p4_decoder_and_types_are_byte_identical():
    assert sha(P4_DECODE)==EXPECTED_DECODE
    assert sha(P4_TYPES)==EXPECTED_TYPES


def test_operational_interface_has_no_truth_parameters():
    import src.dyadic_phase_ms_dp_p_e3 as mod
    sig=inspect.signature(mod.make_p4_phase_payload)
    forbidden={"r","s","order","factor","true_phase","expected_phase","expected_denominator","expected_branch"}
    assert not (forbidden & set(sig.parameters))


def test_p4_v4_remains_unconsumed():
    assert not (ROOT/"results/shor/p4-experiment-v5").exists()
    assert not (ROOT/"results/shor/p4-execution-v8").exists()
