"""Registered BE error contracts; content verification is not a proof oracle.

A trusted, reviewed proof registry is an explicit dependency. Its assertions are
not inferred from P3 PASS, software test counts, hashes, or observed outcomes.
"""
from dataclasses import dataclass
from fractions import Fraction
from src.dyadic_phase_p4_types import fields, rational, integer, hash_string, identity

RISK_TYPE = 'unconditional_wrong_acceptance_per_run'
CONTRACT_FIELDS = ('schema', 'decoder', 'population', 'acquisition_id', 'trials',
                   'beta', 'exceptions', 'gamma', 'maximum_wrong_acceptance',
                   'proof_identity', 'risk_type')
PROOF_FIELDS = ('schema', 'decoder', 'population', 'acquisition_id', 'trials',
                'beta', 'exceptions', 'gamma', 'event_definition', 'assumptions',
                'derivation_sha256', 'human_review_receipt_sha256')


@dataclass(frozen=True)
class ErrorContract:
    decoder: str
    population: str
    acquisition_id: str
    trials: int
    beta: tuple
    exceptions: tuple
    gamma: Fraction
    maximum_wrong_acceptance: Fraction
    proof_identity: str
    contract_identity: str
    assumptions: tuple

    @property
    def wrong_acceptance_bound(self):
        return min(Fraction(1), sum(self.beta, Fraction(0))+sum((v for _, v in self.exceptions), Fraction(0)))


def probability(raw):
    v = rational(raw, 4096)
    if v > 1:
        raise ValueError('probability range')
    return v


def load_error_contract(payload, expected_identity, proof_registry, expected_registry_identity, policy):
    fields(payload, CONTRACT_FIELDS)
    if payload['schema'] != 'cpc-shor-p4-error-contract/1' or payload['risk_type'] != RISK_TYPE:
        raise ValueError('risk contract schema/type')
    if identity('error-contract', payload) != hash_string(expected_identity):
        raise ValueError('unregistered error contract')
    if type(proof_registry) is not dict or identity('reviewed-proof-registry', proof_registry) != hash_string(expected_registry_identity):
        raise ValueError('proof registry identity')
    proof_id = hash_string(payload['proof_identity'])
    if proof_id not in proof_registry:
        raise ValueError('missing reviewed proof; abstain rather than assume beta')
    proof = proof_registry[proof_id]; fields(proof, PROOF_FIELDS)
    if identity('error-proof', proof) != proof_id or proof['schema'] != 'cpc-shor-p4-error-proof/1':
        raise ValueError('proof identity')
    for key in ('decoder', 'population', 'acquisition_id', 'trials', 'beta', 'exceptions', 'gamma'):
        if payload[key] != proof[key]:
            raise ValueError('proof does not justify this contract')
    decoder = payload['decoder']
    if decoder not in ('POINT', 'SET'):
        raise ValueError('decoder profile')
    event = 'returned_correct_denominator_including_abstention_failure' if decoder == 'POINT' else 'true_reduced_fraction_in_complete_set'
    if proof['event_definition'] != event:
        raise ValueError('wrong correctness event')
    for name in ('population', 'acquisition_id'):
        if type(payload[name]) is not str or not 1 <= len(payload[name]) <= 256:
            raise ValueError('population identity')
    k = integer(payload['trials'], 1, 32)
    if k > policy.max_trials or type(payload['beta']) is not list or len(payload['beta']) != k:
        raise ValueError('fixed-k budget')
    beta = tuple(probability(v) for v in payload['beta'])
    raw = payload['exceptions']
    if type(raw) is not list or len(raw) > 32:
        raise ValueError('exception budget list')
    exceptions = []
    for row in raw:
        fields(row, ('event_id', 'bound', 'not_in_beta'))
        if type(row['event_id']) is not str or not 1 <= len(row['event_id']) <= 128 or row['not_in_beta'] is not True:
            raise ValueError('explicit nonduplicated exceptional event required')
        exceptions.append((row['event_id'], probability(row['bound'])))
    if len({x for x, _ in exceptions}) != len(exceptions):
        raise ValueError('duplicate exceptional event')
    if type(proof['assumptions']) is not list or not proof['assumptions'] or any(type(x) is not str or not 1 <= len(x) <= 1024 for x in proof['assumptions']):
        raise ValueError('explicit validity assumptions required')
    hash_string(proof['derivation_sha256']); hash_string(proof['human_review_receipt_sha256'])
    limit = probability(payload['maximum_wrong_acceptance'])
    if limit == 1:
        raise ValueError('nontrivial registered wrong-acceptance limit required')
    contract = ErrorContract(decoder, payload['population'], payload['acquisition_id'], k, beta,
                             tuple(exceptions), probability(payload['gamma']), limit, proof_id,
                             expected_identity, tuple(proof['assumptions']))
    if contract.wrong_acceptance_bound > limit:
        raise ValueError('error budget exceeds registered limit')
    return contract


def universal_success_lower_bound(contract):
    """Unconditional ideal-sampling lower bound, conditional on stated model assumptions."""
    ideal_failure = min(Fraction(1), Fraction(3, 2**contract.trials)) if contract.trials >= 2 else Fraction(1)
    return max(Fraction(0), 1-ideal_failure-contract.wrong_acceptance_bound-contract.gamma)


def conditional_wrong_bound(joint_bound, accepted_probability_lower):
    if not 0 <= joint_bound <= 1 or not 0 < accepted_probability_lower <= 1:
        raise ValueError('separate positive acceptance lower bound required')
    return min(Fraction(1), joint_bound/accepted_probability_lower)
