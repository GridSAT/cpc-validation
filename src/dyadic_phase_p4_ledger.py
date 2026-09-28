"""Deterministic pre-record trial identities; no order oracle or sampling."""
import hashlib
from math import gcd
from src.dyadic_phase_p4_types import fields

ARTIFACTS=['record.npz','inference.npz','profile.json','summary.json']
BASE=('trial_id','fixture_id','N','a','profile','scales','role','group','index',
      'bundle','slot','seed','acquisition_id','decoder','acceptance_role',
      'output_directory','expected_artifacts')


def seed_for(run_identity,trial_id):
    raw=hashlib.sha256(('cpc-shor-p4-seed/1\0'+run_identity+'\0'+trial_id).encode()).digest()
    return [int.from_bytes(raw[i:i+4],'big') for i in range(0,32,4)]


def build_ledger(run_identity, fixtures, *, calibration_grid, calibration_n=256,
                 bundles=128, k=4):
    """Calibration sectors are explicit diagnostic design, never operational advice.

    `calibration_grid` maps fixture IDs to a bounded list of diagnostic sector
    indices. Its completeness is a separate precheck; this module has no order
    lookup. Operational rows carry no order/sector labels.
    """
    if type(run_identity) is not str or not run_identity or '/' in run_identity:
        raise ValueError('run identity')
    if any(type(x) is not int or not 1<=x<=4096 for x in (calibration_n,bundles,k)):
        raise ValueError('bounded ledger counts')
    trials=[]
    for fixture in fixtures:
        fields(fixture,('fixture_id','N','a'))
        fid,N,a=fixture['fixture_id'],fixture['N'],fixture['a']
        if type(fid) is not str or not fid or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-' for c in fid):raise ValueError('fixture ID')
        if type(N) is not int or type(a) is not int or not 2<=N<=256 or not 1<=a<N or gcd(a,N)!=1:raise ValueError('bounded unit fixture')
        def row(tid,role,group,index,bundle,slot):
            return {'trial_id':tid,'fixture_id':fid,'N':N,'a':a,'profile':'DP-P','scales':[0,1,2],
                    'role':role,'group':group,'index':index,'bundle':bundle,'slot':slot,
                    'seed':seed_for(run_identity,tid),'acquisition_id':run_identity+'/'+fid,
                    'decoder':'POINT','acceptance_role':'calibration' if role=='fixed-sector-diagnostic' else 'order-evaluation',
                    'output_directory':'trials/'+tid,'expected_artifacts':list(ARTIFACTS)}
        sectors=calibration_grid[fid]
        if type(sectors) is not list or not sectors or len(set(sectors))!=len(sectors) or any(type(s) is not int or not 0<=s<N for s in sectors):raise ValueError('diagnostic grid')
        for sector in sectors:
            group=f'{fid}-cal-s{sector}'
            for i in range(calibration_n):
                tid=f'{group}-{i:04d}';r=row(tid,'fixed-sector-diagnostic',group,i,None,None)
                r['diagnostic_sector']=sector;trials.append(r)
        for bundle in range(bundles):
            for slot in range(k):
                tid=f'{fid}-eval-b{bundle:04d}-i{slot:03d}'
                trials.append(row(tid,'operational',fid+'-eval',bundle*k+slot,bundle,slot))
    ledger={'schema':'cpc-shor-p4-ledger/1','run_identity':run_identity,'calibration_n':calibration_n,
            'bundles_per_fixture':bundles,'k':k,'fixtures':fixtures,'trials':trials,
            'seed_rule':'SHA256(cpc-shor-p4-seed/1 NUL run_identity NUL trial_id), eight big-endian uint32 words for PCG64 SeedSequence'}
    validate_ledger(ledger)
    return ledger


def validate_ledger(ledger):
    fields(ledger,('schema','run_identity','calibration_n','bundles_per_fixture','k','fixtures','trials','seed_rule'))
    if ledger['schema']!='cpc-shor-p4-ledger/1' or not 1<=len(ledger['trials'])<=10000:raise ValueError('ledger schema/cap')
    if type(ledger['run_identity']) is not str or not ledger['run_identity'] or '/' in ledger['run_identity']:raise ValueError('run identity')
    for key in ('calibration_n','bundles_per_fixture','k'):
        if type(ledger[key]) is not int or not 1<=ledger[key]<=4096:raise ValueError('bounded counts')
    for fixture in ledger['fixtures']:
        fields(fixture,('fixture_id','N','a'))
        N,a=fixture['N'],fixture['a']
        if type(N) is not int or type(a) is not int or not 2<=N<=256 or not 1<=a<N or gcd(a,N)!=1:raise ValueError('bounded unit fixture')
    fixtures={x['fixture_id']:(x['N'],x['a']) for x in ledger['fixtures']}
    if len(fixtures)!=len(ledger['fixtures']):raise ValueError('duplicate fixture')
    seen=set();seeds=set();operational={};calibration={}
    for row in ledger['trials']:
        role=row.get('role');extra=('diagnostic_sector',) if role=='fixed-sector-diagnostic' else ()
        fields(row,BASE+extra)
        if role not in ('fixed-sector-diagnostic','operational'):raise ValueError('role')
        tid=row['trial_id']
        if type(tid) is not str or not tid or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-' for c in tid):raise ValueError('trial ID')
        if tid in seen or tuple(row['seed']) in seeds:raise ValueError('duplicate identity/seed')
        seen.add(tid);seeds.add(tuple(row['seed']))
        if row['seed']!=seed_for(ledger['run_identity'],tid):raise ValueError('seed rule mismatch')
        fid=row['fixture_id']
        if fixtures.get(fid)!=(row['N'],row['a']) or row['acquisition_id']!=ledger['run_identity']+'/'+fid:raise ValueError('fixture/population')
        if row['profile']!='DP-P' or row['scales']!=[0,1,2] or row['decoder']!='POINT':raise ValueError('frozen acquisition/decoder')
        if row['output_directory']!='trials/'+tid or row['expected_artifacts']!=ARTIFACTS:raise ValueError('artifact contract')
        if role=='operational':
            if row['acceptance_role']!='order-evaluation' or type(row['bundle']) is not int or type(row['slot']) is not int or not 0<=row['bundle']<ledger['bundles_per_fixture'] or not 0<=row['slot']<ledger['k']:raise ValueError('operational bundle')
            if row['index']!=row['bundle']*ledger['k']+row['slot'] or row['group']!=fid+'-eval':raise ValueError('evaluation index')
            key=(fid,row['bundle'],row['slot'])
            if key in operational:raise ValueError('duplicate fresh-trial slot')
            operational[key]=tid
        else:
            if row['acceptance_role']!='calibration' or row['bundle'] is not None or row['slot'] is not None:raise ValueError('calibration cannot count as fresh operational slot')
            if type(row['diagnostic_sector']) is not int or not 0<=row['diagnostic_sector']<row['N'] or type(row['index']) is not int:raise ValueError('diagnostic grid/index')
            key=(fid,row['diagnostic_sector']);calibration.setdefault(key,set())
            if row['index'] in calibration[key]:raise ValueError('duplicate calibration slot')
            calibration[key].add(row['index'])
    if len(operational)!=len(fixtures)*ledger['bundles_per_fixture']*ledger['k']:raise ValueError('incomplete operational ledger')
    if set(fid for fid,_ in calibration)!=set(fixtures) or any(v!=set(range(ledger['calibration_n'])) for v in calibration.values()):raise ValueError('incomplete calibration ledger')
    return ledger
