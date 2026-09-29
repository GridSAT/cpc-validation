"""Independent retained-record P4 replay; reuses unchanged P3 replay kernel.

No call to operational infer_records, POINT decoder, or primary verdict. The
likelihood assembly/confidence routines are the already preserved independent
P3 routines. No P3 supervisor or P3 authorization is invoked.
"""
from fractions import Fraction
import json
from math import gcd,isfinite
from pathlib import Path
from src.dyadic_phase_p4_runtime import sha256,verify_receipt,write_once,trial_directory


def enumerate_point(estimate,N):
    """Bounded validation-only enumeration, independent of continued fractions."""
    if type(N) is not int or not 2<=N<=256:raise ValueError('bounded independent modulus')
    x=Fraction(estimate);values=[]
    for q in range(1,N):
        for p in range(q):
            if gcd(p,q)!=1:continue
            delta=abs(x-Fraction(p,q))%1
            if min(delta,1-delta)<Fraction(1,2*N*N):values.append((p,q))
    if len(values)>1:raise ArithmeticError('strict POINT uniqueness violated')
    return values


def diagnostic_order(N,a):
    if not 2<=N<=256 or gcd(N,a)!=1:raise ValueError('bounded diagnostic unit')
    x=1
    for r in range(1,N):
        x=x*a%N
        if x==1:return r
    raise ArithmeticError('unit has no bounded order')


def _canonical_intervals(intervals,atol=1e-14):
    # Canonical closed-interval union on [0,1] for representation-independent comparison.
    if not isinstance(intervals,(list,tuple)):raise ValueError('confidence intervals container')
    rows=[]
    for pair in intervals:
        if not isinstance(pair,(list,tuple)) or len(pair)!=2:raise ValueError('confidence interval pair')
        if isinstance(pair[0],bool) or isinstance(pair[1],bool):raise ValueError('confidence interval endpoint')
        try:lo=float(pair[0]);hi=float(pair[1])
        except (TypeError,ValueError):raise ValueError('confidence interval endpoint') from None
        if not isfinite(lo) or not isfinite(hi) or not 0.<=lo<=hi<=1.:raise ValueError('confidence interval bounds')
        rows.append([lo,hi])
    rows.sort()
    merged=[]
    for lo,hi in rows:
        if merged and lo<=merged[-1][1]+atol:merged[-1][1]=max(merged[-1][1],hi)
        else:merged.append([lo,hi])
    return merged


def replay_trial(plan,seal,trial):
    import numpy as np
    from src.dyadic_phase_p3_fast import load_filter
    from validate_dyadic_p3 import independent_curves,independent_confidence
    root=Path(plan['output_root']);path=trial_directory(root,trial)
    verify_receipt(path,trial)
    output=root/'independent'/(trial['trial_id']+'.json')
    claim=output.with_suffix('.claim.json')
    write_once(claim,{'trial_id':trial['trial_id'],'record_sha256':sha256(path/'record.npz'),'no_retry':True})
    summary=json.loads((path/'summary.json').read_bytes());profile=json.loads((path/'profile.json').read_bytes())
    if (summary['trial_id']!=trial['trial_id'] or profile['trial_id']!=trial['trial_id']
        or profile['preparation_role']!=trial['role'] or profile['arithmetic']!={'N':trial['N'],'a':trial['a'],'scales':trial['scales']}):raise ValueError('independent provenance')
    for name,key in [('record.npz','record_sha256'),('inference.npz','inference_sha256'),('profile.json','profile_sha256')]:
        if summary[key]!=sha256(path/name):raise ValueError('independent summary lineage')
    from src.dyadic_phase_p4_instrument import Bank
    from src.dyadic_phase_p3_profile import validate_profile
    model=Bank(trial['N'],trial['a'],tuple(trial['scales']),plan['g'],plan['Gamma'])
    validate_profile(profile,model,plan['schedule'],expected_record_sha256=sha256(path/'record.npz'),
        expected_acceptance_sha256=seal['acceptance_sha256'],expected_source_seal_sha256=sha256(plan['source_seal_path']))
    s=plan['schedule'];steps=round(s['window']/s['dt'])
    with np.load(path/'record.npz',allow_pickle=False) as raw:
        signal,reference=raw['signal'],raw['reference']
    if signal.shape!=(3,2,steps) or reference.shape!=signal.shape or not np.isfinite(signal).all() or not np.isfinite(reference).all():raise ValueError('independent record shape/finiteness')
    settings=dict(g=plan['g'],Gamma=plan['Gamma'],eta=s['eta'],dt=s['dt'],burn_steps=round(s['burn']/s['dt']))
    lib=load_filter(seal['library_path']);M=plan['inference']['fine_grid']
    fine=independent_curves(lib,signal,reference,trial['scales'],M,settings)
    sm=np.asarray(signal,dtype=np.longdouble).sum(axis=2)/s['window'];rm=np.asarray(reference,dtype=np.longdouble).sum(axis=2)/s['window']
    zs=np.asarray(-sm[:,1]+1j*sm[:,0],complex);zr=np.asarray(-rm[:,1]+1j*rm[:,0],complex)
    confidence=independent_confidence(zs,zr,trial['scales'],plan['moment_bounds'],plan['inference']['confidence_alpha'])
    estimate=int(np.argmax(fine['full']))/M
    errors={}
    with np.load(path/'inference.npz',allow_pickle=False) as saved:
        for name,value in [('log_likelihood',fine['full']),('ablated_log_likelihoods',fine['ablated']),('j0_only_log_likelihood',fine['j0'])]:
            if saved[name].shape!=value.shape:raise ValueError('retained inference array shape')
            errors[name]=float(np.max(abs(saved[name]-value)))
    if estimate!=summary['inference']['estimate']:raise ArithmeticError('independent phase estimate disagrees')
    original=_canonical_intervals(summary['inference']['confidence']['intervals'])
    independent=_canonical_intervals(confidence['intervals'])
    if np.shape(original)!=np.shape(independent):raise ArithmeticError('independent enclosure shape')
    errors['confidence']=0. if not original else float(np.max(abs(np.asarray(original)-np.asarray(independent))))
    if max(errors.values())>plan['independent_tolerance']:raise ArithmeticError('independent raw replay disagreement')
    # Decoding before diagnostic truth. A calibration role is never operational.
    values=enumerate_point(Fraction(estimate),trial['N'])
    report={'schema':'cpc-shor-p4-independent-trial/1','trial_id':trial['trial_id'],
        'role':trial['role'],'record_sha256':sha256(path/'record.npz'),
        'receipt_sha256':sha256(path/'RECEIPT.json'),'estimate':[Fraction(estimate).numerator,Fraction(estimate).denominator],
        'POINT':values,'confidence_intervals':independent,'comparison_errors':errors}
    if trial['role']=='fixed-sector-diagnostic':
        r=diagnostic_order(trial['N'],trial['a']);sector=trial['diagnostic_sector']
        if not 0<=sector<r:raise ValueError('invalid calibration sector')
        report['correct_denominator']=bool(len(values)==1 and values[0][1]==r//gcd(sector,r))
    write_once(output,report)
    write_once(output.with_suffix('.receipt.json'),{'trial_id':trial['trial_id'],'output_sha256':sha256(output),'claim_sha256':sha256(claim)})
    return report


def read_replay(root,trial):
    root=Path(root);path=root/'independent'/(trial['trial_id']+'.json')
    receipt=json.loads(path.with_suffix('.receipt.json').read_bytes())
    if receipt['trial_id']!=trial['trial_id'] or receipt['output_sha256']!=sha256(path) or receipt['claim_sha256']!=sha256(path.with_suffix('.claim.json')):raise ValueError('independent receipt')
    report=json.loads(path.read_bytes())
    if report['trial_id']!=trial['trial_id'] or report['role']!=trial['role']:raise ValueError('independent role')
    raw=trial_directory(root,trial);verify_receipt(raw,trial)
    if report['record_sha256']!=sha256(raw/'record.npz') or report['receipt_sha256']!=sha256(raw/'RECEIPT.json'):raise ValueError('independent evidence changed')
    return report
