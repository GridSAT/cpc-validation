"""P4 deterministic orchestration. No sampler, order oracle, or P5 factoring."""
from src.dyadic_phase_p4_types import fields, hash_string, identity, parse_phase, canonical
from src.dyadic_phase_p4_decode import decode_point, decode_set, aggregate
from src.dyadic_phase_p4_certify import certify_order, verify_order_certificate
from src.dyadic_phase_p4_risk import load_error_contract, RISK_TYPE


def verify_binding(payload, expected_identity, views):
    fields(payload, ('schema', 'N', 'a', 'acquisition_id', 'preparation_model', 'entries'))
    if payload['schema'] != 'cpc-shor-p4-input-binding/1' or identity('input-binding', payload) != hash_string(expected_identity):
        raise ValueError('input binding identity')
    if payload['preparation_model'] != 'independent-fresh-operational-common-theta':
        raise ValueError('not fresh operational common-theta trials')
    if type(payload['entries']) is not list or len(payload['entries']) != len(views):
        raise ValueError('binding trial count')
    for row, v in zip(payload['entries'], views):
        fields(row, ('phase_identity', 'preparation_id', 'record_sha256', 'inference_sha256', 'profile_sha256'))
        if any(row[k] != getattr(v, k) for k in ('preparation_id', 'record_sha256', 'inference_sha256', 'profile_sha256')):
            raise ValueError('record/provenance mismatch')
        if row['phase_identity'] != v.identity or (payload['N'], payload['a'], payload['acquisition_id']) != (v.N, v.a, v.acquisition_id):
            raise ValueError('phase/population mismatch')
    # The trusted input binding attests provenance. A digest alone is not a
    # physical proof of preparation independence; that remains an explicit assumption.


def reconstruct(N, a, phase_payloads, *, decoder, claim_type, policy,
                input_binding, expected_binding_identity, error_contract=None,
                expected_contract_identity=None, proof_registry=None,
                expected_registry_identity=None):
    if decoder not in ('POINT', 'SET') or claim_type not in ('P4-EXACT', 'P4-BE'):
        raise ValueError('explicit decoder and claim type required')
    if type(phase_payloads) is not list or not 1 <= len(phase_payloads) <= policy.max_trials:
        raise ValueError('bounded nonempty input trial list')
    views = tuple(parse_phase(p, policy) for p in phase_payloads)
    verify_binding(input_binding, expected_binding_identity, views)
    candidates = tuple((decode_point if decoder == 'POINT' else decode_set)(N, a, v, policy) for v in views)
    combined = aggregate(N, a, candidates, views, policy)
    result = {'schema': 'cpc-shor-p4-result/1', 'N': N, 'a': a,
              'claim_type': claim_type, 'decoder': decoder, 'status': combined.status,
              'accepted': False, 'candidate_R': None,
              'policy_identity': policy.identity, 'input_binding_identity': expected_binding_identity,
              'phase_identities': tuple(v.identity for v in views),
              'candidates': canonical(candidates), 'aggregation': canonical(combined),
              'aggregation_identity': combined.identity,
              'scope': 'classical semantic reconstruction; no native/physical/RR claim',
              'cost': {'fresh_trials': len(views), 'lcm_calls': combined.lcm_calls,
                       'decoder_work_upper_bound_including_completeness_audit': tuple(tuple((k, 2*n) for k, n in c.work) for c in candidates)},
              'P5_authorized': False}
    if combined.complete and len(combined.values) == 1:
        candidate_R = combined.values[0]; result['candidate_R'] = candidate_R
        if claim_type == 'P4-EXACT':
            certificate = certify_order(N, a, candidate_R, policy)
            result['certificate'] = canonical(certificate)
            result['status'] = certificate['status']
            result['accepted'] = certificate['status'] == 'CERTIFIED_EXACT_ORDER'
        elif pow(a, candidate_R, N) != 1:
            result['status'] = 'VERIFICATION_FAILURE'
            result['reason'] = 'not an order multiple'
        elif error_contract is None:
            result['status'] = 'UNVERIFIED_CANDIDATE'
            result['reason'] = 'no registered reconstruction error guarantee'
        else:
            contract = load_error_contract(error_contract, expected_contract_identity, proof_registry,
                                           expected_registry_identity, policy)
            if contract.decoder != decoder or contract.trials != len(views) or any(v.acquisition_id != contract.acquisition_id for v in views):
                raise ValueError('error contract population/trial mismatch')
            result.update(status='CERTIFIED_BOUNDED_ERROR_ORDER', accepted=True,
                          risk_type=RISK_TYPE, wrong_acceptance_bound=canonical(contract.wrong_acceptance_bound),
                          error_contract_identity=contract.contract_identity, error_proof_identity=contract.proof_identity,
                          validity_assumptions=contract.assumptions, conditional_accepted_output_error_bound=None,
                          modular_residue=1, factorization_required=False)
    result['identity'] = identity('reconstruction-result', result)
    return result


def require_exact_order(result, policy):
    """Typed downstream boundary only; performs no P5 arithmetic."""
    if result.get('claim_type') != 'P4-EXACT' or result.get('status') != 'CERTIFIED_EXACT_ORDER' or result.get('accepted') is not True:
        raise ValueError('EXACT-only consumer rejects bounded-error or unverified output')
    unsigned = {k: v for k, v in result.items() if k != 'identity'}
    if identity('reconstruction-result', unsigned) != result.get('identity'):
        raise ValueError('result identity mismatch')
    factors = tuple(tuple(x) for x in result.get('certificate', {}).get('factors', ()))
    verified = verify_order_certificate(result['N'], result['a'], result['candidate_R'], factors, policy)
    if verified['status'] != 'CERTIFIED_EXACT_ORDER':
        raise ValueError('invalid exact-order certificate')
    return result['candidate_R']
