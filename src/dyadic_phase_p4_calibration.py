"""Calibration-only preparation/scoring adapter. Never imported by decoder."""
from fractions import Fraction
import json
import resource
from src.dyadic_phase_p4_acquisition import _context,_complete_trial
from src.dyadic_phase_p4_runtime import claim_trial,verify_receipt,sha256
from src.dyadic_phase_p4_types import canonical,parse_phase
from src.dyadic_phase_p4_decode import decode_point


def execute_calibration_trial(trial_id,*,acceptance_path,acceptance_sha256,seal_path,seal_sha256,authorization_path):
    plan,seal,trial=_context(trial_id,'fixed-sector-diagnostic',acceptance_path,acceptance_sha256,seal_path,seal_sha256,authorization_path)
    memory=plan['worker_caps']['worker_memory_bytes'];resource.setrlimit(resource.RLIMIT_AS,(memory,memory))
    from src.dyadic_phase_p4_instrument import Bank
    model=Bank(trial['N'],trial['a'],tuple(trial['scales']),plan['g'],plan['Gamma'])
    initial=diagnostic_initial(model,trial['diagnostic_sector'])
    path=claim_trial(plan['output_root'],trial,acceptance_sha256=acceptance_sha256,source_seal_sha256=seal_sha256)
    return _complete_trial(plan,seal,trial,path,model,initial,acceptance_sha256,seal_sha256)


def score_calibration_trial(path,trial,policy):
    """Decode first, then compute diagnostic truth, never forge |1> provenance.

    Calibration outputs cannot enter operational fresh-trial aggregation.
    Abstention counts as denominator reconstruction failure.
    """
    from pathlib import Path
    from math import gcd,isfinite
    path=Path(path)
    if trial['role']!='fixed-sector-diagnostic':raise ValueError('calibration role required')
    verify_receipt(path,trial)
    summary=json.loads((path/'summary.json').read_bytes());profile=json.loads((path/'profile.json').read_bytes())
    if (profile['preparation_role']!='fixed-sector-diagnostic' or profile['trial_id']!=trial['trial_id']
            or summary['trial_id']!=trial['trial_id'] or summary['profile_sha256']!=sha256(path/'profile.json')
            or summary['record_sha256']!=sha256(path/'record.npz') or summary['inference_sha256']!=sha256(path/'inference.npz')
            or profile['arithmetic']!={'N':trial['N'],'a':trial['a'],'scales':trial['scales']}):raise ValueError('calibration lineage')
    estimate=summary['inference']['estimate']
    if type(estimate) not in (int,float) or not isfinite(estimate):raise ValueError('finite calibration estimate')
    payload={'schema':'cpc-shor-p4-phase/1','N':trial['N'],'a':trial['a'],
             'estimate':canonical(Fraction(estimate)),'intervals':[],'epsilon':[0,1],
             'preparation_id':'calibration-only/'+trial['trial_id'],'acquisition_id':trial['acquisition_id'],
             'record_sha256':summary['record_sha256'],'inference_sha256':summary['inference_sha256'],'profile_sha256':summary['profile_sha256']}
    view=parse_phase(payload,policy);candidate=decode_point(trial['N'],trial['a'],view,policy)
    # Diagnostic order/sector are accessed only after the decoder returns.
    x=1;r=None
    for exponent in range(1,trial['N']):
        x=x*trial['a']%trial['N']
        if x==1:r=exponent;break
    s=trial['diagnostic_sector']
    if r is None or type(s) is not int or not 0<=s<r:raise ValueError('invalid diagnostic sector')
    expected=r//gcd(s,r)
    correct=candidate.complete and len(candidate.values)==1 and candidate.values[0].denominator==expected
    return {'schema':'cpc-shor-p4-calibration-score/1','trial_id':trial['trial_id'],
            'receipt_sha256':sha256(path/'RECEIPT.json'),'candidate_identity':candidate.identity,
            'diagnostic_order':r,'diagnostic_sector':s,'correct_denominator':bool(correct),
            'role':'post-inference calibration diagnostic only'}


def diagnostic_initial(model,sector):
    """Calibration-only bounded orbit state; no lookup table or operational import."""
    import numpy as np
    positions=[];x=1
    while x not in positions:
        positions.append(x);x=x*model.a%model.N
    if x!=1 or type(sector) is not int or not 0<=sector<len(positions):raise ValueError('diagnostic orbit/sector')
    initial=np.zeros(model.dimension,complex)
    for k,y in enumerate(positions):initial[y]=np.exp(-2j*np.pi*sector*k/len(positions))/np.sqrt(len(positions))
    return initial
