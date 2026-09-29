"""Independent P3 recomputation from immutable raw records, after primary freeze.

Reuses the sealed finite-instrument C replay kernel, but independently assembles
joint likelihoods, confidence sets, diagnostics, features and acceptance tests.
Predeclared full temporal audits additionally use complex-density Python replay.
"""
from __future__ import annotations
import argparse,hashlib,json,math,os,resource,subprocess,sys,time
from pathlib import Path
import numpy as np
from scipy.special import logsumexp
from scipy.stats import beta,binom
from src.dyadic_phase_p3_execution import verify_execution_seal,sha256
from src.dyadic_phase_p3_fast import load_filter,replay
from src.dyadic_phase_p3 import local_loglikelihood

ROOT=Path('results/shor/p3-experiment-v1')


def independent_curves(lib,sig,ref,scales,M,settings):
    phases=2*np.pi*np.arange(M)/M
    sl=np.array([replay(lib,x,phases,**settings) for x in sig])
    rl=np.array([replay(lib,x,phases,**settings) for x in ref])
    # Per-channel conditional-on-reference law. This assembles the factorization
    # independently of the operational full joint/ablation implementation.
    factors=[]
    for slot,j in enumerate(scales):
        values=[]
        for q in range(M):
            values.append(logsumexp(rl[slot]+np.roll(sl[slot],-(2**j*q)%M))-logsumexp(rl[slot]))
        factors.append(values)
    factors=np.asarray(factors)
    constant=float(sum(logsumexp(x)-math.log(M) for x in rl))
    full=factors.sum(axis=0)+constant
    ablated=np.asarray([np.delete(factors,k,axis=0).sum(axis=0)+constant for k in range(len(scales))])
    j0=factors[tuple(scales).index(0)]+constant
    return dict(full=full,ablated=ablated,j0=j0,sl=sl,rl=rl,factors=factors)


def merge_intervals(intervals):
    merged=[]
    for lo,hi in sorted(intervals):
        if merged and lo<=merged[-1][1]+1e-14:merged[-1][1]=max(hi,merged[-1][1])
        else:merged.append([lo,hi])
    return merged


def independent_confidence(zs,zr,scales,bounds,alpha):
    radius=(2*len(scales)*bounds['fourth_moment_upper']/alpha)**.25+bounds['template_error_upper']
    A=bounds['signed_amplitude'];regions=[[0.,1.]]
    for signal,reference,j in zip(zs,zr,scales):
        arcs=[]
        for z in (signal,reference):
            if A==0:
                arcs.append((0.,.5) if abs(z)<=radius else None);continue
            z=z*np.sign(A);norm=abs(z)
            if norm==0:
                arcs.append((0.,.5) if abs(A)<=radius else None);continue
            cosine=(norm*norm+A*A-radius*radius)/(2*norm*abs(A))
            if cosine>1:arcs.append(None)
            else:arcs.append((math.atan2(z.imag,z.real)/(2*math.pi),math.acos(max(-1.,cosine))/(2*math.pi)))
        if any(x is None for x in arcs):return dict(intervals=[],span=0.,length=0.,empty=True)
        center=(arcs[0][0]-arcs[1][0])%1;half=min(.5,arcs[0][1]+arcs[1][1])
        candidates=[]
        for shift in range(-1,2**j+1):
            lo=(center-half+shift)/2**j;hi=(center+half+shift)/2**j
            if hi>=0 and lo<=1:candidates.append([max(0.,lo),min(1.,hi)])
        pieces=[]
        for lo,hi in regions:
            for left,right in candidates:
                if max(lo,left)<=min(hi,right):pieces.append([max(lo,left),min(hi,right)])
        regions=merge_intervals(pieces)
    if not regions:return dict(intervals=[],span=0.,length=0.,empty=True)
    gaps=[regions[i+1][0]-regions[i][1] for i in range(len(regions)-1)]
    gaps.append(1+regions[0][0]-regions[-1][1])
    return dict(intervals=regions,span=1-max(gaps),length=sum(b-a for a,b in regions),empty=False)


def independent_diagnostic(ket,trial,estimate,regions):
    r={(7,3):6,(7,2):3,(5,2):4}[(trial['N'],trial['a'])]
    d=1<<(trial['N']-1).bit_length();blocks=ket.reshape(-1,d);positions=[];x=1
    for _ in range(r):positions.append(x);x=x*trial['a']%trial['N']
    weights=[]
    for s in range(r):
        amplitudes=blocks[:,positions]@np.exp(2j*np.pi*s*np.arange(r)/r)/math.sqrt(r)
        weights.append(float(np.sum(abs(amplitudes)**2)))
    weights=np.asarray(weights);leak=max(0.,float(np.vdot(ket,ket).real-weights.sum()));weights/=weights.sum()
    if trial['role']=='fixed-sector-diagnostic':s=trial['diagnostic_sector']
    else:
        u=float(np.random.Generator(np.random.PCG64(np.random.SeedSequence(trial['diagnostic_seed']))).random())
        s=min(r-1,int(np.searchsorted(np.cumsum(weights),u)))
    theta=s/r
    return dict(diagnostic_sector=s,diagnostic_theta=theta,
                circular_error_cycles=abs((estimate-theta+.5)%1-.5),
                covered=any(a<=theta<=b for a,b in regions),leakage=leak,
                fixed_sector_loss=float(1-weights[s]) if trial['role']=='fixed-sector-diagnostic' else 0.)


def recompute_trial(trial):
    plan,seal=verify_execution_seal(ROOT/'P3-ACCEPTANCE.json',ROOT/'SOURCE-SEAL.json')
    cap=plan['caps']['memory_bytes'];resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    tid=trial['trial_id'];schedule=plan['schedules'][trial['schedule']]
    output=ROOT/'independent'/f'{tid}.json'
    if output.exists():raise FileExistsError('independent output already exists')
    claim=output.with_suffix('.started.json')
    with claim.open('x') as f:json.dump({'trial_id':tid,'acceptance_sha256':seal['acceptance_sha256'],'status':'started; no regeneration under this identity'},f)
    claim.chmod(0o444)
    with np.load(trial['record_path'],allow_pickle=False) as raw:
        sig,ref,ket,counts=raw['signal'],raw['reference'],raw['diagnostic_final_ket'],raw['counters']
    settings=dict(g=plan['g'],Gamma=plan['Gamma'],eta=schedule['eta'],dt=schedule['dt'],burn_steps=round(schedule['burn']/schedule['dt']))
    lib=load_filter(seal['library_path']);low=plan['inference']['coarse_grid'];high=plan['inference']['fine_grid']
    coarse=independent_curves(lib,sig,ref,trial['scales'],low,settings)
    fine=independent_curves(lib,sig,ref,trial['scales'],high,settings)
    window=schedule['window']
    sm=np.asarray(sig,dtype=np.longdouble).sum(axis=2)/window
    rm=np.asarray(ref,dtype=np.longdouble).sum(axis=2)/window
    zs=np.asarray(-sm[:,1]+1j*sm[:,0],complex);zr=np.asarray(-rm[:,1]+1j*rm[:,0],complex)
    W=zs*zr.conj();confidence=independent_confidence(zs,zr,trial['scales'],plan['moment_bounds'][trial['schedule']],plan['inference']['confidence_alpha'])
    j0conf=independent_confidence(zs[:1],zr[:1],[0],plan['moment_bounds'][trial['schedule']],plan['inference']['confidence_alpha'])
    estimate=float(np.argmax(fine['full'])/high)
    errors=[float(np.ptp(coarse['full']-fine['full'][::2])),float(np.ptp(coarse['j0']-fine['j0'][::2]))]
    errors.extend(float(np.ptp(coarse['ablated'][j]-fine['ablated'][j,::2])) for j in range(3))
    report={'trial_id':tid,'group':trial['group'],'counters':counts.tolist(),
      'inference':{'estimate':estimate,'identifiable':schedule['eta']>0,
        'confidence':{'intervals':confidence['intervals'],'minimum_covering_arc_cycles':confidence['span'],
                      'total_length_cycles':confidence['length'],'empty':confidence['empty']},
        'j0_confidence':{'minimum_covering_arc_cycles':j0conf['span']},
        'maximizer_grid_change_cycles':float(abs((np.argmax(coarse['full'])/low-estimate+.5)%1-.5)),
        'quadrature_errors':{str(k):v for k,v in enumerate(errors)},
        'conditional_factor_error':float(np.max(abs(fine['full'][None,:]-fine['ablated']-fine['factors']))),
        'j1_j2_half_turn_alias_error':float(np.max(abs(fine['ablated'][0]-np.roll(fine['ablated'][0],high//2)))),
        'eta0_loglaw_range':float(np.ptp(fine['full'])),
        'eta0_working_prior_deviation':float(np.max(abs(np.exp(fine['full']-logsumexp(fine['full']))-1/high))),
        'referenced_real':W.real.tolist(),'referenced_imag':W.imag.tolist(),
        'fresh_data_feature':float(np.real(W[0]**2*W[1].conj())),
        'wrong_sign_feature':float(np.imag(zs[0]*zr[0]-W[0])),
        'wrong_offset_feature':float(np.imag((np.exp(.7j)-1)*W[0]))},
      'diagnostic':independent_diagnostic(ket,trial,estimate,confidence['intervals'])}
    original=json.loads((ROOT/'trials'/f'{tid}.json').read_text())
    discrepancies={}
    with np.load(ROOT/'trials'/f'{tid}-inference.npz',allow_pickle=False) as saved:
        for key,array in [('log_likelihood',fine['full']),('ablated_log_likelihoods',fine['ablated']),('j0_only_log_likelihood',fine['j0'])]:
            discrepancies[key]=float(np.max(abs(saved[key]-array)))
    for key in ('minimum_covering_arc_cycles','total_length_cycles'):
        discrepancies[key]=abs(original['inference']['confidence'][key]-report['inference']['confidence'][key])
    if original['diagnostic']['diagnostic_sector']!=report['diagnostic']['diagnostic_sector']:raise ArithmeticError('post-inference sector mismatch')
    if original['diagnostic']['covered']!=report['diagnostic']['covered']:raise ArithmeticError('confidence coverage mismatch')
    if max(discrepancies.values())>plan['independent_validation']['recomputation_tolerance']:raise ArithmeticError('independent recomputation mismatch: '+tid)
    # Reuse only OS-measured process memory for the resource check, explicitly
    # not pretending it is a recomputed physical or numerical quantity.
    report['max_RSS_KiB']=original['max_RSS_KiB']
    report['comparison_errors']=discrepancies
    audit=[]
    if tid in plan['independent_validation']['density_audit_trials']:
        indices=np.asarray(plan['independent_validation']['density_audit_phase_indices'])
        for slot in range(3):
            for raw,law in ((sig[slot],fine['sl'][slot]),(ref[slot],fine['rl'][slot])):
                independent=local_loglikelihood(raw,2*np.pi*indices/high,**settings)
                audit.append(float(np.max(abs(independent-law[indices]))))
        if max(audit)>plan['gates']['P3-B']['numeric_definition']['source_replay_loglaw_tolerance']:
            raise ArithmeticError('complex-density temporal audit mismatch')
    report['complex_density_audit_errors']=audit
    path=ROOT/'independent'/f'{tid}.json'
    with path.open('x') as f:json.dump(report,f,indent=2,allow_nan=False);f.write('\n')
    path.chmod(0o444)
    receipt=path.with_suffix('.sha256')
    with receipt.open('x') as f:f.write(sha256(path)+'\n')
    receipt.chmod(0o444)
    return tid


def independent_decisions(plan,reports):
    if len(reports)!=len(plan['trials']) or {r['trial_id'] for r in reports}!={t['trial_id'] for t in plan['trials']}:raise ValueError('independent trial identity mismatch')
    groups={g['id']:[r for r in reports if r['group']==g['id']] for g in plan['groups']}
    out={}
    def put(gate,key,condition):out[(gate,key)]=bool(condition)
    for group in plan['groups']:
        if len(groups[group['id']])!=group['n']:raise ValueError('independent group count')
    lookup={t['trial_id']:t for t in plan['trials']};g=plan['gates'];a=g['P3-A']['numeric_definition'];b=g['P3-B']['numeric_definition']
    put('P3-A','single-preparation',all(r['counters'][0]==(3 if lookup[r['trial_id']]['profile']=='fresh-data-control' else 1) for r in reports))
    def counts_ok(r):
        t=lookup[r['trial_id']];s=plan['schedules'][t['schedule']]
        return r['counters'][4]==(0 if t['profile']=='DP-P' else 2) and r['counters'][3]==12*round((s['burn']+s['window'])/s['dt'])
    put('P3-A','reset-and-arithmetic-bookkeeping',all(counts_ok(r) for r in reports))
    put('P3-A','residue-leakage',max(r['diagnostic']['leakage'] for r in reports)<=a['final_norm_and_residue_tolerance'])
    put('P3-A','fixed-sector-preservation',max(r['diagnostic']['fixed_sector_loss'] for r in reports)<=a['commutator_and_fixed_sector_transfer_tolerance'])
    put('P3-B','nested-quadrature',max(max(r['inference']['quadrature_errors'].values()) for r in reports)<=b['coarse_fine_centered_loglaw_tolerance'])
    put('P3-B','grid-maximizer',max(r['inference']['maximizer_grid_change_cycles'] for r in reports)<=b['coarse_fine_maximizer_change_cycles'])
    put('P3-B','worker-memory',max(r['max_RSS_KiB'] for r in reports)*1024<=plan['caps']['memory_bytes'])
    put('P3-H','same-theta-conditional-factors',max(r['inference']['conditional_factor_error'] for r in reports)<=g['P3-H']['numeric_definition']['conditional_factor_audit_tolerance'])
    put('P3-D','j1-j2-half-turn-alias',max(r['inference']['j1_j2_half_turn_alias_error'] for r in reports)<=g['P3-D']['numeric_definition']['alias_equality_tolerance'])
    c=g['P3-C']['numeric_definition']
    for group in plan['groups']:
        if group['eta']==0 or group['profile']=='fresh-data-control':continue
        rs=groups[group['id']];n=len(rs)
        conf=sum(r['diagnostic']['covered'] and not r['inference']['confidence']['empty'] and r['inference']['confidence']['minimum_covering_arc_cycles']<=c['covering_arc_cycles_max'] for r in rs)
        acc=sum(r['diagnostic']['circular_error_cycles']<=c['phase_error_cycles_max'] for r in rs)
        for name,k in [('global-confidence-and-concentration',conf),('circular-estimator-accuracy',acc)]:
            put('P3-C',group['id']+'/'+name,float(binom.sf(k-1,n,c['empirical_success_lower_bound_min']))<=c['one_sided_alpha_per_test'])
    def mean(group,key,slot=None):
        vals=[r['inference'][key] if slot is None else r['inference'][key][slot] for r in groups[group]]
        return math.fsum(vals)/len(vals)
    put('P3-E','retained-vs-fresh-record-correlation',mean('operational-N7-a3','fresh_data_feature')-mean('fresh-N7-a3','fresh_data_feature')>g['P3-E']['numeric_definition']['threshold'])
    for row in g['P3-H']['numeric_definition']['higher_scale_tests']:
        j=row['scale'];put('P3-H',f'j{j}-nonzero-record-information',mean('fixed-N7-a3-s0','referenced_real',j)-mean('fixed-N7-a3-s1','referenced_real',j)>row['threshold'])
    for key,feature in [('wrong_sign','wrong_sign_feature'),('wrong_correction_offset','wrong_offset_feature')]:
        put('P3-G',key,mean('fixed-N7-a3-s0',feature)>g['P3-G']['numeric_definition'][key]['threshold'])
    zero=groups['zero-efficiency-N7-a3'];f=g['P3-F']['numeric_definition']
    put('P3-F','zero-efficiency-flat-likelihood',max(r['inference']['eta0_loglaw_range'] for r in zero)<=f['eta0_loglaw_range_max'])
    put('P3-F','zero-efficiency-working-prior',max(r['inference']['eta0_working_prior_deviation'] for r in zero)<=f['eta0_Haar_weight_max_deviation'])
    put('P3-F','zero-efficiency-abstains',all(not r['inference']['identifiable'] and (r['inference']['confidence']['empty'] or abs(r['inference']['confidence']['total_length_cycles']-1)<1e-12) for r in zero))
    return out


def main():
    plan,seal=verify_execution_seal(ROOT/'P3-ACCEPTANCE.json',ROOT/'SOURCE-SEAL.json')
    primary_path=ROOT/'PRIMARY.json';primary=json.loads(primary_path.read_text())
    if sha256(primary_path)!=(ROOT/'PRIMARY-SHA256.txt').read_text().strip():raise ValueError('primary identity changed')
    if (ROOT/'INDEPENDENT.json').exists():raise FileExistsError('independent report already frozen')
    for p,h in primary['evidence_manifest'].items():
        if sha256(p)!=h:raise ValueError('primary evidence changed: '+p)
    for trial in plan['trials']:
        saved=ROOT/'independent'/f"{trial['trial_id']}.json"
        if saved.exists():
            if sha256(saved)!=saved.with_suffix('.sha256').read_text().strip():raise ValueError('independent receipt mismatch')
            report=json.loads(saved.read_text())
            if report['trial_id']!=trial['trial_id']:raise ValueError('independent identity mismatch')
        elif saved.with_suffix('.started.json').exists():raise RuntimeError('incomplete independent claim; cannot regenerate: '+trial['trial_id'])
    pending=[t for t in plan['trials'] if not (ROOT/'independent'/f"{t['trial_id']}.json").exists()]
    cap=plan['caps']['supervisor_memory_bytes'];resource.setrlimit(resource.RLIMIT_AS,(cap,cap))
    epoch=json.loads((ROOT/'RUN-START.json').read_text())['epoch']
    active={};position=0;lock=ROOT/'INDEPENDENT.lock'
    with lock.open('x') as f:f.write(str(os.getpid()))
    try:
        while active or position<len(pending):
            if time.time()-epoch>plan['caps']['runtime_seconds']:raise TimeoutError('total run runtime cap')
            if sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())>plan['caps']['storage_bytes']:raise MemoryError('run storage cap')
            while position<len(pending) and len(active)<plan['caps']['parallel_workers']:
                tid=pending[position]['trial_id'];position+=1
                out=(ROOT/'logs'/f'{tid}-independent.log').open('x')
                try:
                    proc=subprocess.Popen([sys.executable,__file__,'--trial',tid],stdout=out,stderr=subprocess.STDOUT,
                        env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1'})
                except BaseException:
                    out.close();raise
                active[tid]=(proc,out,time.monotonic())
            for tid,(proc,out,started) in list(active.items()):
                if time.monotonic()-started>plan['caps']['independent_worker_seconds']:raise TimeoutError('independent worker cap: '+tid)
                status=proc.poll()
                if status is None:continue
                out.close();del active[tid]
                if status:raise RuntimeError('independent worker failed: '+tid)
                print(json.dumps({'independent_complete':tid}),flush=True)
            if active:time.sleep(.5)
    except BaseException as error:
        with (ROOT/f'INDEPENDENT-FAILURE-{time.time_ns()}.json').open('x') as f:json.dump({'error':repr(error),'evidence_preserved':True},f)
        raise
    finally:
        for proc,out,_ in active.values():
            if proc.poll() is None:proc.terminate()
        for proc,out,_ in active.values():
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
            out.close()
        if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()
    reports=[json.loads((ROOT/'independent'/f"{t['trial_id']}.json").read_text()) for t in plan['trials']]
    decisions=independent_decisions(plan,reports)
    original={(x['gate'],x['criterion']):x['passed'] for x in primary['criteria']}
    if decisions!=original:raise ArithmeticError('independent acceptance outcomes differ')
    result={'classification':'independent recomputation MATCH' if decisions==original else 'MISMATCH',
            'primary_sha256':sha256(primary_path),'acceptance_sha256':seal['acceptance_sha256'],
            'trial_count':len(reports),'criteria_matched':len(decisions),
            'P3_pass':all(decisions.values()),'kernel_scope':'shared sealed instrument kernel; independent assembly/confidence/statistics; predeclared Python complex-density full-record audits',
            'max_recomputation_error':max(max(r['comparison_errors'].values()) for r in reports),
            'max_complex_density_error':max([v for r in reports for v in r['complex_density_audit_errors']] or [0.]),
            'independent_manifest':{str(p):sha256(p) for p in sorted((ROOT/'independent').glob('*.json')) if not p.name.endswith('.started.json')},
            'no_P4':True}
    with (ROOT/'INDEPENDENT.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    (ROOT/'INDEPENDENT.json').chmod(0o444);print(json.dumps(result),flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--trial');args=parser.parse_args()
    if args.trial:
        plan,_=verify_execution_seal(ROOT/'P3-ACCEPTANCE.json',ROOT/'SOURCE-SEAL.json')
        recompute_trial(next(t for t in plan['trials'] if t['trial_id']==args.trial))
    else:main()
