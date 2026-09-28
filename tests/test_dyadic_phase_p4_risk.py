from fractions import Fraction as F
from copy import deepcopy
import pytest
from src.dyadic_phase_p4_types import Policy, identity
from src.dyadic_phase_p4_risk import load_error_contract, conditional_wrong_bound, universal_success_lower_bound
from p4_helpers import risk


def load(kwargs):
    return load_error_contract(kwargs['error_contract'],kwargs['expected_contract_identity'],kwargs['proof_registry'],kwargs['expected_registry_identity'],Policy())

def test_missing_registry_and_posthoc_contract_rejected():
    k=risk();k['proof_registry']={};k['expected_registry_identity']=identity('reviewed-proof-registry',{})
    with pytest.raises(ValueError):load(k)
    k=risk();k['error_contract']['beta']=[[1,100]]
    with pytest.raises(ValueError):load(k)

@pytest.mark.parametrize('field,value',[('risk_type','conditional_wrong_given_acceptance'),('decoder','TRUE_PEAK'),('trials',2),('maximum_wrong_acceptance',[1,1])])
def test_semantic_contract_tampering(field,value):
    k=risk();k['error_contract'][field]=value;k['expected_contract_identity']=identity('error-contract',k['error_contract'])
    with pytest.raises(ValueError):load(k)

def test_budget_overrun_and_conditional_risk_distinction():
    with pytest.raises(ValueError):load(risk(beta=[F(1,5)],limit=F(1,10)))
    c=load(risk(k=8,beta=[F(1,1000)]*8))
    assert c.wrong_acceptance_bound==F(1,125)
    assert universal_success_lower_bound(c)==1-F(3,256)-F(1,125)
    assert conditional_wrong_bound(F(1,100),F(1,10))==F(1,10)
    with pytest.raises(ValueError):conditional_wrong_bound(F(1,100),F(0))

def test_proof_binding_cannot_be_reused_for_other_population():
    k=risk();k['error_contract']['population']='new population';k['expected_contract_identity']=identity('error-contract',k['error_contract'])
    with pytest.raises(ValueError):load(k)
