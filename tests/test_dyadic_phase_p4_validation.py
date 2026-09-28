from fractions import Fraction as F
from src.dyadic_phase_p4 import reconstruct
from src.dyadic_phase_p4_types import Policy
from src.dyadic_phase_p4_validation import independent_audit
from p4_helpers import phase,binding,risk


def test_independent_oracle_checks_both_profiles():
    for N,a,value in [(7,3,F(1,6)),(7,2,F(1,3)),(5,2,F(1,4)),(15,2,F(1,4))]:
        ps=[phase(N,a,value)]
        for claim in ('P4-EXACT','P4-BE'):
            out=reconstruct(N,a,ps,decoder='POINT',claim_type=claim,policy=Policy(),**binding(ps),**(risk() if claim=='P4-BE' else {}))
            assert not independent_audit(out,ps,Policy())['accepted_wrong_order']


def test_wrong_BE_control_counted_not_disguised():
    ps=[phase(7,2,F(1,6))]
    out=reconstruct(7,2,ps,decoder='POINT',claim_type='P4-BE',policy=Policy(),**binding(ps),**risk())
    assert independent_audit(out,ps,Policy())['accepted_wrong_order']


def test_exported_json_remains_independently_auditable():
    import json
    ps=[phase()]
    out=reconstruct(7,3,ps,decoder='POINT',claim_type='P4-EXACT',policy=Policy(),**binding(ps))
    restored=json.loads(json.dumps(out))
    assert not independent_audit(restored,ps,Policy())['accepted_wrong_order']
