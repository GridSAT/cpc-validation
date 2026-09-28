"""P3-to-P4 sanitization boundary. Diagnostic values are never interpreted.

This module is not a sampler or inference algorithm. It verifies the already
frozen parent artifacts and creates only their declared operational phase view.
"""
from fractions import Fraction
from math import isfinite
import json
from src.dyadic_phase_p4_types import fields, digest_bytes, parse_phase, canonical

SUMMARY_FIELDS = ('trial_id', 'group', 'record_sha256', 'inference_sha256', 'profile_sha256',
                  'inference', 'diagnostic', 'counters', 'seconds', 'max_RSS_KiB', 'no_P4')


def sanitize_p3(summary_bytes, profile_bytes, *, expected_summary_sha256,
                expected_profile_sha256, acquisition_id, policy):
    if digest_bytes(summary_bytes) != expected_summary_sha256 or digest_bytes(profile_bytes) != expected_profile_sha256:
        raise ValueError('P3 input content mismatch')
    summary = json.loads(summary_bytes); profile = json.loads(profile_bytes)
    fields(summary, SUMMARY_FIELDS)
    if profile.get('schema') != 'cpc-shor-p3-profile/1' or profile.get('preparation_role') != 'operational' or profile.get('profile') not in ('DP-P', 'DP-S'):
        raise ValueError('diagnostic/fresh-data-control is not an operational common-theta trial')
    if summary['trial_id'] != profile['trial_id'] or summary['record_sha256'] != profile['record_sha256'] or summary['profile_sha256'] != expected_profile_sha256:
        raise ValueError('P3 lineage mismatch')
    preparations = [e for e in profile['events'] if e['kind'] == 'data_preparation']
    if len(preparations) != 1 or preparations[0]['state'] != '|1>':
        raise ValueError('one fresh |1> preparation required')
    data_id = preparations[0]['data_register_id']
    if any(c['data_register_id'] != data_id for c in profile['channels'] if c['role'] == 'signal'):
        raise ValueError('all signal scales must share one sector')
    def fraction(x):
        if type(x) not in (float, int) or not isfinite(x):
            raise ValueError('finite stored P3 number required')
        return canonical(Fraction(x))
    infer = summary['inference']
    payload = {'schema': 'cpc-shor-p4-phase/1', 'N': profile['arithmetic']['N'], 'a': profile['arithmetic']['a'],
               'estimate': fraction(infer['estimate']),
               'intervals': [[fraction(lo), fraction(hi)] for lo, hi in infer['confidence']['intervals']],
               'epsilon': [0, 1], 'preparation_id': data_id, 'acquisition_id': acquisition_id,
               'record_sha256': summary['record_sha256'], 'inference_sha256': summary['inference_sha256'],
               'profile_sha256': expected_profile_sha256}
    parse_phase(payload, policy)
    return payload
