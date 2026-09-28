"""P4-only authorization and immutable receipts. No acquisition on import."""
import hashlib
import json
import os
from pathlib import Path
from src.dyadic_phase_p4_seal import verify_source_seal
from src.dyadic_phase_p4_types import fields, hash_string


def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def write_once(path, value):
    """Partial write remains evidence on any failure; never replace or resume."""
    data=(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o444)
    try:
        with os.fdopen(fd,'wb',closefd=False) as f:f.write(data);f.flush();os.fsync(fd)
    finally:os.close(fd)
    return hashlib.sha256(data).hexdigest()


def readonly_json(path, expected):
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o222:
        raise PermissionError('frozen regular read-only file required: '+str(path))
    if sha256(path)!=hash_string(expected):raise ValueError('frozen identity mismatch: '+str(path))
    return json.loads(path.read_bytes())


def load_execution_contract(acceptance_path, acceptance_sha256, seal_path,
                            seal_sha256, authorization_path):
    """Verify a NEW P4 human GO before any trial claim or random-engine load.

    Positive authorization is deliberately absent from the prerecord package.
    P3 authorization and the earlier P4 draft gate cannot satisfy this schema.
    """
    if authorization_path is None or not Path(authorization_path).is_file():
        raise PermissionError('separate P4 human execution GO required')
    auth_path=Path(authorization_path)
    if auth_path.is_symlink() or auth_path.stat().st_mode & 0o222:
        raise PermissionError('P4 authorization must be read-only')
    auth=json.loads(auth_path.read_bytes())
    fields(auth,('schema','explicit_human_execution_GO','acceptance_sha256',
                 'source_seal_sha256','dependency_manifest_sha256','review_reference'))
    if (auth['schema']!='cpc-shor-p4-execution-authorization/2'
            or auth['explicit_human_execution_GO'] is not True
            or auth['acceptance_sha256']!=acceptance_sha256
            or auth['source_seal_sha256']!=seal_sha256
            or type(auth['review_reference']) is not str or not auth['review_reference'].strip()):
        raise PermissionError('P4 review does not authorize these identities')
    plan=readonly_json(acceptance_path,acceptance_sha256)
    seal=readonly_json(seal_path,seal_sha256)
    if (plan.get('schema')!='cpc-shor-p4-acceptance/1'
            or plan.get('status')!='FINAL_PRE_RECORD'
            or plan.get('human_review_required_before_execution') is not True
            or seal.get('acceptance_sha256')!=acceptance_sha256
            or seal.get('deterministic_prechecks_passed') is not True
            or seal.get('power_error_analysis_complete') is not True
            or auth['dependency_manifest_sha256']!=seal.get('dependency_manifest_sha256')):
        raise PermissionError('incomplete P4 prerecord/review contract')
    verify_source_seal(seal_path,seal_sha256)
    lib=seal.get('library_path')
    kernel=seal.get('kernel_path')
    kernel_sha256=seal.get('kernel_sha256')
    if not lib or lib not in seal['sources']:
        raise ValueError('P4 native library must be source-sealed')
    if not kernel or kernel not in seal['sources']:
        raise ValueError('P4 kernel must be source-sealed')
    if lib != kernel:
        raise ValueError('P4 library_path must equal sealed kernel_path')
    if kernel_sha256 != seal['sources'][kernel]:
        raise ValueError('P4 kernel seal identity mismatch')
    if sha256(kernel) != kernel_sha256:
        raise ValueError('P4 kernel on-disk identity mismatch')
    ledger=readonly_json(plan['ledger_path'],plan['ledger_sha256'])
    from src.dyadic_phase_p4_ledger import validate_ledger
    validate_ledger(ledger)
    if ledger['run_identity']!=plan['run_identity']:
        raise ValueError('ledger population mismatch')
    return plan,seal,ledger


def admitted_trial(ledger, trial_id, role):
    rows=[row for row in ledger['trials'] if row['trial_id']==trial_id]
    if len(rows)!=1 or rows[0]['role']!=role:raise ValueError('trial role/identity not admitted')
    return rows[0]


def trial_directory(root, trial):
    root=Path(root).resolve()
    relative=Path(trial['output_directory'])
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('trial destination escapes run')
    path=root/relative
    if path.resolve()!=path or path.parent.resolve()!=root/'trials':
        raise ValueError('trial destination must be direct non-symlink trial child')
    return path


def claim_trial(root, trial, *, acceptance_sha256, source_seal_sha256):
    path=trial_directory(root,trial)
    path.mkdir(exist_ok=False)
    write_once(path/'CLAIM.json',{'schema':'cpc-shor-p4-trial-claim/1','trial_id':trial['trial_id'],
        'role':trial['role'],'acceptance_sha256':hash_string(acceptance_sha256),
        'source_seal_sha256':hash_string(source_seal_sha256),'status':'claimed; partial or failed trial may never be regenerated'})
    return path


def receipt_trial(path, trial):
    path=Path(path)
    expected=trial['expected_artifacts']
    if set(p.name for p in path.iterdir())!=set(expected)|{'CLAIM.json'}:
        raise ValueError('trial incomplete or unexpected evidence')
    for name in ['CLAIM.json']+expected:
        if Path(name).name!=name or (path/name).is_symlink() or not (path/name).is_file():raise ValueError('regular trial artifacts required')
    files={name:sha256(path/name) for name in ['CLAIM.json']+expected}
    for name in files:(path/name).chmod(0o444)
    result={'schema':'cpc-shor-p4-trial-receipt/1','trial_id':trial['trial_id'],'files':files}
    write_once(path/'RECEIPT.json',result)
    return result


def verify_receipt(path, trial):
    path=Path(path)
    if (path/'RECEIPT.json').is_symlink() or (path/'RECEIPT.json').stat().st_mode & 0o222:raise ValueError('immutable receipt required')
    receipt=json.loads((path/'RECEIPT.json').read_bytes())
    fields(receipt,('schema','trial_id','files'))
    expected=set(trial['expected_artifacts'])|{'CLAIM.json'}
    if receipt['schema']!='cpc-shor-p4-trial-receipt/1' or receipt['trial_id']!=trial['trial_id'] or set(receipt['files'])!=expected:
        raise ValueError('receipt schema/identity/inventory')
    if set(p.name for p in path.iterdir())!=expected|{'RECEIPT.json'}:
        raise ValueError('extra or missing trial evidence')
    for name,h in receipt['files'].items():
        p=path/name
        if p.is_symlink() or p.stat().st_mode & 0o222 or sha256(p)!=h:
            raise ValueError('immutable trial artifact changed: '+name)
    return receipt
