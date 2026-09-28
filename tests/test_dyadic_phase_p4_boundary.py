from fractions import Fraction
from dataclasses import replace
import inspect
import pytest
from src.dyadic_phase_p4_types import Policy, parse_phase, phase_payload
from src.dyadic_phase_p4 import reconstruct
from src.dyadic_phase_p4_decode import decode_point, decode_set, aggregate
from src.dyadic_phase_p4_certify import certify_order
from p4_helpers import phase, binding

@pytest.mark.parametrize('key',['r','s','factors','expected_denominator','expected_convergent','expected_peak','diagnostic_sector','diagnostic_final_ket','order_table'])
def test_schema_rejects_advice(key):
    p=phase();p[key]=6
    with pytest.raises(ValueError):parse_phase(p,Policy())

@pytest.mark.parametrize('fn',[reconstruct,decode_point,decode_set,aggregate,certify_order])
def test_signature_no_truth_advice(fn):
    names=set(inspect.signature(fn).parameters)
    assert not names & {'r','s','factors','expected_denominator','expected_peak','order_table','diagnostic_sector','diagnostic_final_ket'}
    assert not any(p.kind==p.VAR_KEYWORD for p in inspect.signature(fn).parameters.values())

@pytest.mark.parametrize('key,value',[('N',True),('a',0),('N',1),('estimate',[2,2]),('epsilon',[-1,2]),('intervals',[[[1,1],[0,1]]]),('record_sha256','bad')])
def test_invalid_exact_schema(key,value):
    p=phase();p[key]=value
    with pytest.raises(ValueError):parse_phase(p,Policy())

def test_roundtrip_and_phase_precision_cap():
    p=phase();v=parse_phase(p,Policy());assert phase_payload(v)==p
    p['estimate']=[1,2**4097]
    with pytest.raises(ValueError):parse_phase(p,Policy())

def test_duplicate_preparation_and_forged_completeness():
    policy=Policy();vs=[parse_phase(phase(slot=i),policy) for i in range(2)];cs=[decode_point(7,3,v,policy) for v in vs]
    with pytest.raises(ValueError):aggregate(7,3,cs,[vs[0],replace(vs[1],preparation_id=vs[0].preparation_id)],policy)
    forged=replace(cs[0],values=(Fraction(1,3),))
    with pytest.raises(ValueError):aggregate(7,3,[forged],[vs[0]],policy)

def test_binding_tamper_and_no_error_budget():
    ps=[phase()];b=binding(ps)
    out=reconstruct(7,3,ps,decoder='POINT',claim_type='P4-BE',policy=Policy(),**b)
    assert out['status']=='UNVERIFIED_CANDIDATE' and not out['accepted']
    b['input_binding']['preparation_model']='same-sector-copy'
    with pytest.raises(ValueError):reconstruct(7,3,ps,decoder='POINT',claim_type='P4-EXACT',policy=Policy(),**b)
