"""New P4 acquisition wrapper over immutable P3 physics/inference.

Importing or deterministic prechecking this module generates no records. Every
public acquisition call requires the later P4-specific human GO and final seal.
Diagnostic state preparation lives in a separate adapter.
"""
import json
from pathlib import Path
import resource
import time
from src.dyadic_phase_p4_runtime import (admitted_trial,claim_trial,load_execution_contract,
    receipt_trial,sha256,write_once)
from src.dyadic_phase_p4_types import fields

CAP_FIELDS=('worker_memory_bytes','record_bytes','worker_seconds')


def validate_worker_contract(plan,seal,trial):
    """Cheap deterministic cap/schedule precheck, before any claim or RNG."""
    caps=plan['worker_caps'];fields(caps,CAP_FIELDS)
    for name in CAP_FIELDS:
        if type(caps[name]) is not int or caps[name]<=0:raise ValueError('positive worker caps')
    schedule=plan['schedule']
    fields(schedule,('eta','dt','burn','window','transfer_phases','reset_time','retune_time','dead_time'))
    from math import isfinite
    for name in ('eta','dt','burn','window','reset_time','retune_time','dead_time'):
        if type(schedule[name]) not in (int,float) or not isfinite(schedule[name]):raise ValueError('finite schedule')
    dt,burn,window=schedule['dt'],schedule['burn'],schedule['window']
    if not .005<=dt<=.04 or not 0<=burn<=32 or not 0<window<=4096 or not 0<=schedule['eta']<=1 or window/dt>500000:
        raise ValueError('P3 finite-instrument domain')
    if any(abs(x/dt-round(x/dt))>1e-8 for x in (burn,window)):raise ValueError('integral instrument steps')
    if len(schedule['transfer_phases'])!=len(trial['scales']) or any(type(x) not in (int,float) or not isfinite(x) for x in schedule['transfer_phases']):raise ValueError('reference phases')
    for name in ('g','Gamma'):
        if type(plan[name]) not in (float,int) or not isfinite(plan[name]) or plan[name]<=0:raise ValueError('finite positive generator parameter')
    if trial['profile']!='DP-P' or trial['scales']!=[0,1,2]:raise ValueError('bounded frozen P4 profile')
    fields(plan['inference'],('coarse_grid','fine_grid','confidence_alpha'))
    if (type(plan['inference']['coarse_grid']) is not int or type(plan['inference']['fine_grid']) is not int
            or not 8<=plan['inference']['coarse_grid']<=plan['inference']['fine_grid']<=4096
            or not 0<plan['inference']['confidence_alpha']<1):raise ValueError('bounded inference grid')
    # Uncompressed NPZ: four scalar streams per scale plus state and fixed
    # metadata overhead. Enforce the actual file byte cap again after writing.
    d=2**((trial['N']-1).bit_length()+len(trial['scales']))
    record_bound=4*len(trial['scales'])*round(window/dt)*8+d*16+65536
    if record_bound>caps['record_bytes']:raise MemoryError('declared record cap below deterministic storage bound')
    if caps['record_bytes']>caps['worker_memory_bytes']:raise MemoryError('record cap exceeds worker address-space cap')
    return {'record_storage_upper_bound_bytes':record_bound,'full_register_dimension':d}


def _context(trial_id,role,acceptance_path,acceptance_sha256,seal_path,seal_sha256,authorization_path):
    plan,seal,ledger=load_execution_contract(acceptance_path,acceptance_sha256,seal_path,seal_sha256,authorization_path)
    trial=admitted_trial(ledger,trial_id,role)
    validate_worker_contract(plan,seal,trial)
    return plan,seal,trial


def _complete_trial(plan,seal,trial,path,model,initial,acceptance_sha256,seal_sha256):
    """Private common instrument path; initial state is never an inference input."""
    import numpy as np
    from src.dyadic_phase_p4_instrument import _run_prepared
    from src.dyadic_phase_p3_inference import infer_records
    from src.dyadic_phase_p3_profile import make_profile,validate_profile
    schedule=plan['schedule'];started=time.monotonic()
    signal,reference,final,counts,rng=_run_prepared(model,trial['profile'],schedule,trial['seed'],initial,seal['library_path'])
    record=path/'record.npz'
    with record.open('xb') as f:np.savez(f,signal=signal,reference=reference,diagnostic_final_ket=final,counters=counts,rng_end=json.dumps(rng))
    if record.stat().st_size>plan['worker_caps']['record_bytes']:raise MemoryError('record byte cap exceeded; partial evidence retained')
    # Truth, initial state, N/a and diagnostic ket are deliberately absent.
    inference,arrays=infer_records(signal,reference,tuple(trial['scales']),library_path=seal['library_path'],
        g=plan['g'],Gamma=plan['Gamma'],eta=schedule['eta'],dt=schedule['dt'],
        burn_steps=round(schedule['burn']/schedule['dt']),moment_bounds=plan['moment_bounds'],**plan['inference'])
    with (path/'inference.npz').open('xb') as f:np.savez(f,**arrays)
    sidecar=make_profile(trial['trial_id'],model,trial['profile'],schedule,sha256(record),acceptance_sha256,seal_sha256,trial['role'])
    validate_profile(sidecar,model,schedule,expected_record_sha256=sha256(record),expected_acceptance_sha256=acceptance_sha256,expected_source_seal_sha256=seal_sha256)
    write_once(path/'profile.json',sidecar)
    # This is the unchanged P3 summary shape describing only acquisition and
    # inference. P4 reconstruction comes later. No diagnostic truth is embedded.
    summary={'trial_id':trial['trial_id'],'group':trial['group'],'record_sha256':sha256(record),
             'inference_sha256':sha256(path/'inference.npz'),'profile_sha256':sha256(path/'profile.json'),
             'inference':inference,'diagnostic':{},'counters':counts.tolist(),
             'seconds':time.monotonic()-started,'max_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'no_P4':True}
    write_once(path/'summary.json',summary)
    return receipt_trial(path,trial)


def execute_operational_trial(trial_id,*,acceptance_path,acceptance_sha256,seal_path,seal_sha256,authorization_path):
    """Only a fresh |1> preparation. No caller-provided sector/state/truth."""
    plan,seal,trial=_context(trial_id,'operational',acceptance_path,acceptance_sha256,seal_path,seal_sha256,authorization_path)
    memory=plan['worker_caps']['worker_memory_bytes']
    resource.setrlimit(resource.RLIMIT_AS,(memory,memory))
    import numpy as np
    from src.dyadic_phase_p4_instrument import Bank
    from src.dyadic_phase_p4_instrument import _compiled_profile
    model=Bank(trial['N'],trial['a'],tuple(trial['scales']),plan['g'],plan['Gamma'])
    _,dimension=_compiled_profile(model,trial['profile'])
    initial=np.zeros(dimension,complex);initial[1]=1
    path=claim_trial(plan['output_root'],trial,acceptance_sha256=acceptance_sha256,source_seal_sha256=seal_sha256)
    return _complete_trial(plan,seal,trial,path,model,initial,acceptance_sha256,seal_sha256)
