import json
import pytest
import src.dyadic_phase_p4_seal as sealmod
from src.dyadic_phase_p4_types import digest_bytes
from src.dyadic_phase_p4_seal import verify_execution_authorization,verify_source_seal


def test_no_stochastic_authorization_from_implementation_GO(tmp_path):
    with pytest.raises(PermissionError):
        verify_execution_authorization(
            None,
            acceptance_sha256='a'*64,
            source_seal_sha256='b'*64,
            dependency_manifest_sha256='c'*64)
    p=tmp_path/'implementation.json';p.write_text(json.dumps({'schema':'implementation-GO'}))
    with pytest.raises((ValueError,PermissionError)):
        verify_execution_authorization(
            p,
            acceptance_sha256='a'*64,
            source_seal_sha256='b'*64,
            dependency_manifest_sha256='c'*64)


def test_bound_execution_receipt_and_source_tamper(tmp_path,monkeypatch):
    src=tmp_path/'code.py';src.write_text('pass\n')
    dep=tmp_path/'deps.json';dep.write_text(json.dumps({'synthetic':'runtime fixture'}))
    dep_hash=digest_bytes(dep.read_bytes())

    calls=[]
    def synthetic_runtime_verify(path,expected):
        assert str(path)==str(dep)
        assert expected==dep_hash
        calls.append((str(path),expected))
        return {'synthetic':True}

    monkeypatch.setattr(sealmod,'verify_manifest',synthetic_runtime_verify)

    seal={'schema':'cpc-shor-p4-source-seal/1','sources':{str(src):digest_bytes(src.read_bytes())},'dependency_manifest':str(dep),'dependency_manifest_sha256':dep_hash}
    p=tmp_path/'seal.json';p.write_text(json.dumps(seal));h=digest_bytes(p.read_bytes())
    verify_source_seal(p,h)
    assert calls

    auth=tmp_path/'GO.json';auth.write_text(json.dumps({
        'schema':'cpc-shor-p4-execution-authorization/2',
        'explicit_human_execution_GO':True,
        'acceptance_sha256':'a'*64,
        'source_seal_sha256':h,
        'dependency_manifest_sha256':dep_hash,
        'review_reference':'test-only synthetic receipt'}))
    verify_execution_authorization(
        auth,
        acceptance_sha256='a'*64,
        source_seal_sha256=h,
        dependency_manifest_sha256=dep_hash)
    with pytest.raises(PermissionError):
        verify_execution_authorization(
            auth,
            acceptance_sha256='b'*64,
            source_seal_sha256=h,
            dependency_manifest_sha256=dep_hash)

    src.write_text('changed\n')
    with pytest.raises(ValueError):verify_source_seal(p,h)


def test_runtime_dependency_verifier_failure_is_fatal(tmp_path,monkeypatch):
    src=tmp_path/'code.py';src.write_text('pass\n')
    dep=tmp_path/'deps.json';dep.write_text('{}')
    dep_hash=digest_bytes(dep.read_bytes())
    seal={'schema':'cpc-shor-p4-source-seal/1','sources':{str(src):digest_bytes(src.read_bytes())},'dependency_manifest':str(dep),'dependency_manifest_sha256':dep_hash}
    p=tmp_path/'seal.json';p.write_text(json.dumps(seal));h=digest_bytes(p.read_bytes())

    def fail_runtime(*args,**kwargs):
        raise ValueError('synthetic runtime mismatch')

    monkeypatch.setattr(sealmod,'verify_manifest',fail_runtime)

    with pytest.raises(ValueError,match='runtime mismatch'):
        verify_source_seal(p,h)


def test_v1_execution_authorization_is_rejected(tmp_path):
    auth=tmp_path/'OLD-GO.json'
    auth.write_text(json.dumps({
        'schema':'cpc-shor-p4-execution-authorization/1',
        'explicit_human_execution_GO':True,
        'acceptance_sha256':'a'*64,
        'source_seal_sha256':'b'*64,
        'dependency_manifest_sha256':'c'*64,
        'review_reference':'obsolete schema'}))
    with pytest.raises(PermissionError):
        verify_execution_authorization(
            auth,
            acceptance_sha256='a'*64,
            source_seal_sha256='b'*64,
            dependency_manifest_sha256='c'*64)

def test_verification_only_import_does_not_load_numpy_or_scipy():
    import subprocess,sys,json

    code=r'''
import json,sys
from pathlib import Path
import src.dyadic_phase_p4_runtime
mods=set(sys.modules)
vm=None
for line in Path("/proc/self/status").read_text().splitlines():
    if line.startswith("VmSize:"):
        vm=int(line.split()[1])*1024
        break
print(json.dumps({
    "numpy": "numpy" in mods,
    "scipy": "scipy" in mods,
    "vm_size": vm
}))
'''
    result=subprocess.run(
        [sys.executable,'-c',code],
        check=True,
        capture_output=True,
        text=True)

    row=json.loads(result.stdout)

    assert row["numpy"] is False
    assert row["scipy"] is False
    assert row["vm_size"] < 512*1024**2
