import json
from copy import deepcopy
import pytest
from src.dyadic_phase_p4_ingest import sanitize_p3
from src.dyadic_phase_p4_types import Policy,digest_bytes


def parents():
    profile={'schema':'cpc-shor-p3-profile/1','preparation_role':'operational','profile':'DP-P','trial_id':'trial',
             'record_sha256':'a'*64,'arithmetic':{'N':7,'a':3},
             'events':[{'kind':'data_preparation','state':'|1>','data_register_id':'fresh-0'}],
             'channels':[{'role':'signal','data_register_id':'fresh-0'}]}
    pb=json.dumps(profile).encode()
    summary={'trial_id':'trial','group':'operational','record_sha256':'a'*64,'inference_sha256':'b'*64,
             'profile_sha256':digest_bytes(pb),'inference':{'estimate':0.5,'confidence':{'intervals':[[0.4,0.6]]}},
             'diagnostic':{'diagnostic_sector':3,'true_order':6},'counters':[],'seconds':1,'max_RSS_KiB':1,'no_P4':True}
    return summary,profile

def sanitize(summary,profile):
    pb=json.dumps(profile).encode();summary=deepcopy(summary);summary['profile_sha256']=digest_bytes(pb);sb=json.dumps(summary).encode()
    return sanitize_p3(sb,pb,expected_summary_sha256=digest_bytes(sb),expected_profile_sha256=digest_bytes(pb),acquisition_id='registered-P3',policy=Policy())

def test_diagnostic_truth_does_not_cross_boundary():
    s,p=parents();before=sanitize(s,p);s['diagnostic']={'diagnostic_sector':-999,'order_table':'malicious','diagnostic_final_ket':[666]}
    assert sanitize(s,p)==before
    assert not {'diagnostic','r','s','factors'} & set(before)

@pytest.mark.parametrize('role,profile',[('fixed-sector-diagnostic','DP-P'),('operational','fresh-data-control')])
def test_nonoperational_profiles_rejected(role,profile):
    s,p=parents();p.update(preparation_role=role,profile=profile)
    with pytest.raises(ValueError):sanitize(s,p)

def test_corrupted_identity_and_split_sector_rejected():
    s,p=parents();p['channels'].append({'role':'signal','data_register_id':'another-sector'})
    with pytest.raises(ValueError):sanitize(s,p)
    s,p=parents();s['expected_denominator']=6
    with pytest.raises(ValueError):sanitize(s,p)
