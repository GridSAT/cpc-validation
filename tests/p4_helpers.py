from fractions import Fraction
from src.dyadic_phase_p4_types import identity, parse_phase, canonical, Policy


def phase(N=7, a=3, value=Fraction(1,6), slot=0, intervals=None):
    return {'schema':'cpc-shor-p4-phase/1','N':N,'a':a,'estimate':canonical(value),
            'intervals':canonical(((value,value),) if intervals is None else intervals),'epsilon':[0,1],
            'preparation_id':f'fresh-{slot}','record_sha256':identity('record',slot),
            'inference_sha256':identity('inference',slot),'profile_sha256':identity('profile',slot),
            'acquisition_id':'deterministic-mathematical-fixture'}


def binding(payloads, policy=Policy()):
    vs=[parse_phase(p,policy) for p in payloads]
    b={'schema':'cpc-shor-p4-input-binding/1','N':vs[0].N,'a':vs[0].a,'acquisition_id':vs[0].acquisition_id,
       'preparation_model':'independent-fresh-operational-common-theta',
       'entries':[{'phase_identity':v.identity,'preparation_id':v.preparation_id,'record_sha256':v.record_sha256,
                   'inference_sha256':v.inference_sha256,'profile_sha256':v.profile_sha256} for v in vs]}
    return {'input_binding':b,'expected_binding_identity':identity('input-binding',b)}


def risk(k=1, decoder='POINT', beta=None, limit=Fraction(1,10)):
    beta=beta if beta is not None else [Fraction(0)]*k
    proof={'schema':'cpc-shor-p4-error-proof/1','decoder':decoder,'population':'test mathematical fixtures only',
           'acquisition_id':'deterministic-mathematical-fixture','trials':k,'beta':canonical(beta),'exceptions':[],
           'gamma':[0,1], 'event_definition':'returned_correct_denominator_including_abstention_failure' if decoder=='POINT' else 'true_reduced_fraction_in_complete_set',
           'assumptions':['Test-only exact phase fixture; not an operational P3 guarantee'],
           'derivation_sha256':identity('fixture-derivation','exact fractions'),
           'human_review_receipt_sha256':identity('test-only-review','not a real execution approval')}
    pid=identity('error-proof',proof);registry={pid:proof}
    c={k:proof[k] for k in ('decoder','population','acquisition_id','trials','beta','exceptions','gamma')}
    c.update(schema='cpc-shor-p4-error-contract/1',maximum_wrong_acceptance=canonical(limit),proof_identity=pid,
             risk_type='unconditional_wrong_acceptance_per_run')
    return {'error_contract':c,'expected_contract_identity':identity('error-contract',c),
            'proof_registry':registry,'expected_registry_identity':identity('reviewed-proof-registry',registry)}
