import copy
import pytest
from src.dyadic_phase_p3 import Bank
from src.dyadic_phase_p3_profile import make_profile, validate_profile

SCHEDULE = dict(burn=16., window=512., reset_time=.25, retune_time=.1, dead_time=.5)


@pytest.mark.parametrize('profile', ['DP-P', 'DP-S', 'fresh-data-control'])
def test_profile_data_continuity_and_declared_resource_difference(profile):
    model = Bank(7, 3)
    p = make_profile('trial-1', model, profile, SCHEDULE, 'a'*64, 'b'*64, 'c'*64, 'operational')
    assert validate_profile(p, model, SCHEDULE, expected_record_sha256='a'*64,
                             expected_acceptance_sha256='b'*64, expected_source_seal_sha256='c'*64)
    ids = {c['data_register_id'] for c in p['channels'] if c['role'] == 'signal'}
    assert len(ids) == (3 if profile == 'fresh-data-control' else 1)
    assert p['cost']['data_preparations'] == len(ids)
    assert p['cost']['wall_duration'] == pytest.approx(1056 if profile == 'DP-P' else 3169.7)
    changed = copy.deepcopy(p); changed['channels'][0]['data_register_id'] = 'reprepared'
    with pytest.raises(ValueError):
        validate_profile(changed, model, SCHEDULE, expected_record_sha256='a'*64,
                          expected_acceptance_sha256='b'*64, expected_source_seal_sha256='c'*64)


def test_profile_rejects_record_and_cost_tampering():
    model = Bank(7, 3)
    p = make_profile('trial-1', model, 'DP-P', SCHEDULE, 'a'*64, 'b'*64, 'c'*64, 'operational')
    p['cost']['data_preparations'] = 2
    with pytest.raises(ValueError):
        validate_profile(p, model, SCHEDULE, expected_record_sha256='a'*64,
                          expected_acceptance_sha256='b'*64, expected_source_seal_sha256='c'*64)
