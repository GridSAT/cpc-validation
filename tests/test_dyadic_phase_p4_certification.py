from fractions import Fraction as F
from math import gcd
import pytest
from src.dyadic_phase_p4_types import Policy, identity
from src.dyadic_phase_p4_certify import certify_order, verify_order_certificate
from src.dyadic_phase_p4 import reconstruct, require_exact_order
from p4_helpers import phase, binding, risk

@pytest.mark.parametrize('N',[2,5,7,9,15,21,25])
def test_exact_certificates_against_independent_enumeration(N):
    for a in range(1,N):
        if gcd(N,a)!=1:continue
        true_order=next(k for k in range(1,N) if pow(a,k,N)==1)
        for R in range(1,N):
            out=certify_order(N,a,R,Policy())
            assert (out['status']=='CERTIFIED_EXACT_ORDER')==(R==true_order)

@pytest.mark.parametrize('certificate',[((6,1),),((2,1),),((2,0),(3,1)),((3,1),(2,1)),((2,2),(3,1))])
def test_malformed_or_incomplete_factor_certificate(certificate):
    try:out=verify_order_certificate(7,3,6,certificate,Policy())
    except ValueError:return
    assert out['status']!='CERTIFIED_EXACT_ORDER'

def test_factor_and_independent_primality_caps():
    assert certify_order(7,3,6,Policy(max_factor_divisions=0))['status']=='CERTIFICATION_INCOMPLETE'
    assert verify_order_certificate(23,2,11,((11,1),),Policy(max_certificate_divisions=0))['status']=='CERTIFICATION_INCOMPLETE'

@pytest.mark.parametrize('claim,status',[('P4-EXACT','CERTIFIED_EXACT_ORDER'),('P4-BE','CERTIFIED_BOUNDED_ERROR_ORDER')])
def test_distinct_end_to_end_claims(claim,status):
    ps=[phase(value=F(1,3),slot=0),phase(value=F(1,2),slot=1)]
    out=reconstruct(7,3,ps,decoder='POINT',claim_type=claim,policy=Policy(),**binding(ps),**(risk(2) if claim=='P4-BE' else {}))
    assert out['accepted'] and out['candidate_R']==6 and out['status']==status
    if claim=='P4-EXACT':assert require_exact_order(out,Policy())==6
    else:
        assert out['risk_type']=='unconditional_wrong_acceptance_per_run'
        assert out['conditional_accepted_output_error_bound'] is None and 'factors' not in out
        with pytest.raises(ValueError):require_exact_order(out,Policy())

@pytest.mark.parametrize('N,a,R',[(7,2,6),(15,2,8),(21,2,12)])
def test_corrupted_denominator_modular_pass_is_not_deterministic_soundness(N,a,R,monkeypatch):
    ps=[phase(N,a,F(1,R))]
    def forbidden(*args,**kwargs):raise AssertionError('BE must not factor')
    monkeypatch.setattr('src.dyadic_phase_p4.certify_order',forbidden)
    # An intentionally false test-only premise illustrates why the reviewed
    # registry is a mathematical trust boundary, not a proof-by-hashing mechanism.
    out=reconstruct(N,a,ps,decoder='POINT',claim_type='P4-BE',policy=Policy(),**binding(ps),**risk())
    assert out['accepted'] and out['candidate_R']==R
    assert certify_order(N,a,R,Policy())['status']=='VERIFICATION_FAILURE'
    assert out['claim_type']=='P4-BE'

def test_zero_sector_does_not_fake_order():
    ps=[phase(value=F(0))]
    out=reconstruct(7,3,ps,decoder='POINT',claim_type='P4-EXACT',policy=Policy(),**binding(ps))
    assert not out['accepted']
    ps=[phase(7,1,F(0))]
    out=reconstruct(7,1,ps,decoder='POINT',claim_type='P4-EXACT',policy=Policy(),**binding(ps))
    assert out['accepted'] and out['candidate_R']==1
