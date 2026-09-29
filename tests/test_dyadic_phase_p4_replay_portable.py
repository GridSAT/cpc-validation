"""Prospective synthetic replay checks; no acquisition or native execution."""
import json
import numpy as np
import pytest
from src.dyadic_phase_p4_instrument import Bank
from src.dyadic_phase_p3_profile import make_profile
from src.dyadic_phase_p4_runtime import claim_trial,receipt_trial,write_once,sha256
from src.dyadic_phase_p4_replay import replay_trial,read_replay
from src.dyadic_phase_p4_ledger import build_ledger


def ledger():
    return build_ledger(
        "P4-replay-unit", [{"fixture_id":"N7-a3","N":7,"a":3}],
        calibration_grid={"N7-a3":[0]}, calibration_n=1, bundles=1, k=4,
    )


@pytest.mark.parametrize('corrupt',[False,True])
def test_retained_replay_and_disagreement_without_sampler(tmp_path,monkeypatch,corrupt):
    import validate_dyadic_p3 as independent
    import src.dyadic_phase_p3_fast as fast
    trial=ledger()['trials'][-1]
    for name in ('trials','independent'):(tmp_path/name).mkdir()
    seal_path=tmp_path/'source-fixture.json';write_once(seal_path,{'test_only':True})
    seal_hash=sha256(seal_path);schedule=dict(eta=.8,dt=.04,burn=0.,window=.32,transfer_phases=[.7]*3,reset_time=.25,retune_time=.1,dead_time=.5)
    bounds={'fourth_moment_upper':.1,'template_error_upper':0.,'signed_amplitude':.6}
    plan={'output_root':str(tmp_path),'source_seal_path':str(seal_path),'g':.35,'Gamma':1.,'schedule':schedule,
          'inference':{'fine_grid':8,'confidence_alpha':.05},'moment_bounds':bounds,'independent_tolerance':2e-10}
    seal={'library_path':'never-loaded','acceptance_sha256':'0'*64}
    path=claim_trial(tmp_path,trial,acceptance_sha256='0'*64,source_seal_sha256=seal_hash)
    signal=np.zeros((3,2,8));reference=signal.copy()
    with (path/'record.npz').open('xb') as f:np.savez(f,signal=signal,reference=reference)
    curves={'full':np.arange(8,dtype=float),'ablated':np.zeros((3,8)),'j0':np.zeros(8)}
    with (path/'inference.npz').open('xb') as f:np.savez(f,log_likelihood=curves['full']+(1 if corrupt else 0),ablated_log_likelihoods=curves['ablated'],j0_only_log_likelihood=curves['j0'])
    model=Bank(7,3,(0,1,2),.35,1.)
    profile=make_profile(trial['trial_id'],model,'DP-P',schedule,sha256(path/'record.npz'),'0'*64,seal_hash,'operational')
    write_once(path/'profile.json',profile)
    conf=independent.independent_confidence(np.zeros(3,complex),np.zeros(3,complex),[0,1,2],bounds,.05)
    assert conf['intervals']==[[0.0,1.0]]
    # Production regression: primary inference may encode the same closed set
    # using touching/zero-width pieces at a dyadic boundary.
    primary_intervals=[[0.0,0.5],[0.5,0.5],[0.5,0.5],[0.5,1.0]]
    summary={'trial_id':trial['trial_id'],'record_sha256':sha256(path/'record.npz'),'inference_sha256':sha256(path/'inference.npz'),'profile_sha256':sha256(path/'profile.json'),
             'inference':{'estimate':7/8,'confidence':{'intervals':primary_intervals}}}
    write_once(path/'summary.json',summary);receipt_trial(path,trial)
    monkeypatch.setattr(fast,'load_filter',lambda unused:None)
    monkeypatch.setattr(independent,'independent_curves',lambda *args:curves)
    if corrupt:
        with pytest.raises(ArithmeticError,match='replay disagreement'):replay_trial(plan,seal,trial)
        assert (tmp_path/'independent'/(trial['trial_id']+'.claim.json')).exists()
        assert not (tmp_path/'independent'/(trial['trial_id']+'.receipt.json')).exists()
        assert not (tmp_path/'independent'/(trial['trial_id']+'.json')).exists()
        with pytest.raises(FileExistsError):replay_trial(plan,seal,trial)
    else:
        out=replay_trial(plan,seal,trial)
        assert out['estimate']==[7,8] and read_replay(tmp_path,trial)==out
        report=tmp_path/'independent'/(trial['trial_id']+'.json')
        claim=report.with_suffix('.claim.json')
        receipt=json.loads(report.with_suffix('.receipt.json').read_bytes())
        assert receipt=={'trial_id':trial['trial_id'],'output_sha256':sha256(report),
                         'claim_sha256':sha256(claim)}
        assert out['record_sha256']==sha256(path/'record.npz')
        assert out['receipt_sha256']==sha256(path/'RECEIPT.json')
        with pytest.raises(FileExistsError):replay_trial(plan,seal,trial)


def test_confidence_interval_canonicalization_is_set_semantic():
    from src.dyadic_phase_p4_replay import _canonical_intervals
    # Structural pattern observed in the failed P4-v3 calibration replay.
    assert _canonical_intervals([[.4735,.5],[.5,.5],[.5,.5],[.5,.5179]])==[[.4735,.5179]]
    # Genuine gaps must remain separate components.
    assert _canonical_intervals([[0.,.49],[.51,1.]])==[[0.,.49],[.51,1.]]
    with pytest.raises(ValueError,match='confidence interval bounds'):
        _canonical_intervals([[.6,.4]])
