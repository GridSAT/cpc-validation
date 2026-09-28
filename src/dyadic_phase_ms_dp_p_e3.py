"""MS-DP-P E3-Ia: truth-free integration from local phase estimates to frozen P4 POINT.

No record generation occurs here. E3-Ib supplies the future acquisition adapter.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from typing import Iterable, Mapping

from src.dyadic_phase_ms_dp_p import (
    DEFAULT_DELTA,
    canonical_cycle,
    required_highest_scale,
    unwrap_local_phases,
)


class IntegrationError(ValueError):
    pass


def _hash_string(value: str) -> str:
    if type(value) is not str or len(value) != 64:
        raise IntegrationError("sha256 identity must be 64 hex characters")
    try:
        int(value, 16)
    except ValueError as exc:
        raise IntegrationError("invalid sha256 identity") from exc
    return value.lower()


@dataclass(frozen=True)
class LocalPhaseEvidence:
    scale: int
    estimate: Fraction
    data_register_id: str
    trial_id: str
    channel_id: str
    record_sha256: str
    inference_sha256: str
    profile_sha256: str

    def __post_init__(self):
        if type(self.scale) is not int or self.scale < 0:
            raise IntegrationError("nonnegative integer scale required")
        object.__setattr__(self, "estimate", canonical_cycle(self.estimate))
        for name in ("data_register_id", "trial_id", "channel_id"):
            value=getattr(self,name)
            if type(value) is not str or not value or len(value)>256:
                raise IntegrationError("bounded nonempty identity required: "+name)
        for name in ("record_sha256","inference_sha256","profile_sha256"):
            object.__setattr__(self,name,_hash_string(getattr(self,name)))

    @classmethod
    def from_mapping(cls, value: Mapping):
        allowed={
            "scale","estimate","data_register_id","trial_id","channel_id",
            "record_sha256","inference_sha256","profile_sha256",
        }
        if set(value)!=allowed:
            forbidden=set(value)-allowed
            if forbidden:
                raise IntegrationError("unexpected/truth field(s): "+",".join(sorted(forbidden)))
            raise IntegrationError("incomplete local evidence")
        return cls(**value)


def canonical_bundle_identity(rows: Iterable[LocalPhaseEvidence], label: str) -> str:
    """Deterministic identity for the integration bundle; not a replacement for raw-file hashes."""
    material=[]
    for row in rows:
        material.append({
            "scale":row.scale,
            "estimate":[row.estimate.numerator,row.estimate.denominator],
            "data_register_id":row.data_register_id,
            "trial_id":row.trial_id,
            "channel_id":row.channel_id,
            "record_sha256":row.record_sha256,
            "inference_sha256":row.inference_sha256,
            "profile_sha256":row.profile_sha256,
        })
    data=json.dumps({"label":label,"rows":material},sort_keys=True,separators=(",",":"),allow_nan=False).encode()
    return hashlib.sha256(data).hexdigest()


def validate_local_evidence(N: int, rows: Iterable[LocalPhaseEvidence], delta=DEFAULT_DELTA):
    rows=tuple(rows)
    J=required_highest_scale(N,delta)
    if len(rows)!=J+1:
        raise IntegrationError(f"expected exactly {J+1} local evidence rows")
    if tuple(row.scale for row in rows)!=tuple(range(J+1)):
        raise IntegrationError("local evidence scales must be exactly 0..J in order")
    trial_ids={row.trial_id for row in rows}
    data_ids={row.data_register_id for row in rows}
    channels={row.channel_id for row in rows}
    if len(trial_ids)!=1:
        raise IntegrationError("one phase-estimation trial identity required")
    if len(data_ids)!=1:
        raise IntegrationError("all scales must retain one data-register identity")
    if len(channels)!=len(rows):
        raise IntegrationError("scale channels must be distinct")
    return rows


def make_p4_phase_payload(
    N: int,
    a: int,
    rows: Iterable[LocalPhaseEvidence],
    *,
    acquisition_id: str,
    bundle_record_sha256: str,
    bundle_inference_sha256: str,
    bundle_profile_sha256: str,
    delta=DEFAULT_DELTA,
):
    """Unwrap local estimates and serialize one phase into the unchanged P4 schema."""
    rows=validate_local_evidence(N,rows,delta)
    if type(a) is not int or not 1<=a<N:
        raise IntegrationError("admissible arithmetic a required")
    if type(acquisition_id) is not str or not acquisition_id or len(acquisition_id)>256:
        raise IntegrationError("bounded acquisition identity required")
    for h in (bundle_record_sha256,bundle_inference_sha256,bundle_profile_sha256):
        _hash_string(h)

    result=unwrap_local_phases(N,(row.estimate for row in rows),delta)
    payload={
        "schema":"cpc-shor-p4-phase/1",
        "N":N,
        "a":a,
        "estimate":[result.estimate.numerator,result.estimate.denominator],
        "intervals":[],
        "epsilon":[0,1],
        "preparation_id":rows[0].data_register_id,
        "record_sha256":bundle_record_sha256,
        "inference_sha256":bundle_inference_sha256,
        "profile_sha256":bundle_profile_sha256,
        "acquisition_id":acquisition_id,
    }
    audit={
        "schema":"cpc-shor-ms-dp-p-e3ia-audit/1",
        "trial_id":rows[0].trial_id,
        "data_register_id":rows[0].data_register_id,
        "highest_scale":result.highest_scale,
        "channel_count":result.channel_count,
        "branch_margins":[[q.numerator,q.denominator] for q in result.branch_margins],
        "integration_bundle_identity":canonical_bundle_identity(rows,"ms-dp-p-e3ia"),
        "truth_inputs_used":False,
        "p4_decoder_changed":False,
    }
    return payload,audit


def decode_with_frozen_point(payload, policy):
    """Call the existing frozen P4 parser and POINT decoder without changing them."""
    from src.dyadic_phase_p4_types import parse_phase
    from src.dyadic_phase_p4_decode import decode_point
    view=parse_phase(payload,policy)
    candidate=decode_point(view.N,view.a,view,policy)
    return view,candidate
