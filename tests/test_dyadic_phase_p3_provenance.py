"""Cryptographic provenance guard faults without stochastic execution."""
import json,sys
from pathlib import Path
import pytest
from src import dyadic_phase_p3_provenance as p

@pytest.mark.parametrize('fault',[None,'source','native','interpreter','link','manifest','loader','missing','mapped'])
def test_dependency_mutations_fail_closed(tmp_path,monkeypatch,fault):
    exe=tmp_path/'python';exe.write_text('interpreter')
    source=tmp_path/'source.py';source.write_text('source')
    native=tmp_path/'library.so';native.write_text('library')
    alias=tmp_path/'link';alias.symlink_to(source)
    monkeypatch.setattr(sys,'executable',str(exe))
    monkeypatch.setattr(p,'loaded_native_paths',lambda:{str(native)})
    monkeypatch.delenv('LD_LIBRARY_PATH',raising=False);monkeypatch.delenv('LD_PRELOAD',raising=False)
    files=p.file_manifest([exe,source,native,alias])
    m={'schema':'cpc-shor-p3-dependencies/1','python_executable':str(exe),'python_build':sys.version,'loader_environment':{'LD_LIBRARY_PATH':'','LD_PRELOAD':''},'files':files}
    path=tmp_path/'manifest.json';path.write_text(json.dumps(m));h=p.digest(path)
    if fault in ('source','native','interpreter'):{'source':source,'native':native,'interpreter':exe}[fault].write_text('changed')
    elif fault=='link':alias.unlink();alias.symlink_to(native)
    elif fault=='manifest':path.write_text('{}')
    elif fault=='loader':monkeypatch.setenv('LD_LIBRARY_PATH','/unexpected')
    elif fault=='missing':native.unlink()
    elif fault=='mapped':monkeypatch.setattr(p,'loaded_native_paths',lambda:{'/unsealed.so'})
    if fault is None:p.verify_manifest(path,h)
    else:
        with pytest.raises((ValueError,FileNotFoundError)):p.verify_manifest(path,h)

@pytest.mark.parametrize('fault',[None,'missing','writable','acceptance','seal','unreviewed','no-reference'])
def test_post_freeze_human_review_gate(tmp_path,fault):
    from src.dyadic_phase_p3_execution import require_human_review,sha256
    seal=tmp_path/'seal.json';seal.write_text('sealed fixture')
    receipt={'schema':'cpc-shor-p3-human-review/1','acceptance_sha256':'accepted','source_seal_sha256':sha256(seal),'explicit_human_authorization':True,'review_reference':'synthetic test fixture only'}
    if fault=='acceptance':receipt['acceptance_sha256']='wrong'
    elif fault=='seal':receipt['source_seal_sha256']='wrong'
    elif fault=='unreviewed':receipt['explicit_human_authorization']=False
    elif fault=='no-reference':receipt['review_reference']=''
    path=tmp_path/'EXECUTION-AUTHORIZATION.json'
    if fault!='missing':path.write_text(json.dumps(receipt));path.chmod(0o644 if fault=='writable' else 0o444)
    args=({'human_review_required_before_execution':True},{'acceptance_sha256':'accepted'},seal)
    if fault is None:require_human_review(*args)
    else:
        with pytest.raises((ValueError,PermissionError,FileNotFoundError)):require_human_review(*args)
