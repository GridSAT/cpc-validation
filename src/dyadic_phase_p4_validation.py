"""Bounded validation-only order oracle. Never imported by operational decoding."""
from fractions import Fraction
from math import gcd
from src.dyadic_phase_p4_types import identity, parse_phase


def independent_audit(result, phase_payloads, policy, *, maximum_modulus=256):
    N, a = result['N'], result['a']
    if N > maximum_modulus:
        raise ValueError('independent bounded validation cap')
    if result['identity'] != identity('reconstruction-result', {k:v for k,v in result.items() if k!='identity'}):
        raise ValueError('result changed before validation')
    phases=[parse_phase(p,policy) for p in phase_payloads]
    if tuple(result['phase_identities']) != tuple(p.identity for p in phases):
        raise ValueError('validation phase identity')
    x=1; exact=None
    for exponent in range(1,N):
        x=x*a%N
        if x==1:
            exact=exponent;break
    if exact is None:
        raise ValueError('not an admissible unit')
    if len(result['candidates']) != len(phases):
        raise ValueError('candidate count')
    if result['accepted'] and (not result['aggregation']['complete'] or len(result['aggregation']['values']) != 1):
        raise ArithmeticError('accepted incomplete/ambiguous aggregate')
    expected_states={1}
    for candidate,view in zip(result['candidates'],phases):
        if not candidate['complete']:
            continue
        expected=set()
        for q in range(1,N):
            for p in range(q):
                if gcd(p,q)!=1:continue
                value=Fraction(p,q)
                if result['decoder']=='POINT':
                    delta=abs(view.estimate-value)%1
                    compatible=min(delta,1-delta)<Fraction(1,2*N*N)
                else:
                    compatible=any(lo-view.epsilon<=value+h<=hi+view.epsilon for lo,hi in view.intervals for h in (-1,0,1))
                if compatible:expected.add(value)
        actual={Fraction(*pair) for pair in candidate['values']}
        if actual!=expected:raise ArithmeticError('independent rational-set disagreement')
        expected_states={R*x.denominator//gcd(R,x.denominator) for R in expected_states for x in expected if R*x.denominator//gcd(R,x.denominator)<N}
    if result['aggregation']['complete'] and set(result['aggregation']['values'])!=expected_states:
        raise ArithmeticError('independent LCM disagreement')
    if result['accepted']:
        wanted='CERTIFIED_EXACT_ORDER' if result['claim_type']=='P4-EXACT' else 'CERTIFIED_BOUNDED_ERROR_ORDER'
        if result['status']!=wanted or result['candidate_R'] not in expected_states:
            raise ArithmeticError('claim/status/aggregate mismatch')
        if pow(a,result['candidate_R'],N)!=1:
            raise ArithmeticError('accepted nonmultiple')
    wrong=bool(result['accepted'] and result['candidate_R']!=exact)
    if wrong and result['claim_type']=='P4-EXACT':
        raise ArithmeticError('wrong deterministic exact certificate')
    return {'schema':'cpc-shor-p4-independent-audit/1','result_identity':result['identity'],
            'reference_order':exact,'accepted_wrong_order':wrong,'claim_type':result['claim_type'],
            'scope':'bounded post-inference diagnostic only; a BE wrong output is counted, not reclassified as EXACT'}
