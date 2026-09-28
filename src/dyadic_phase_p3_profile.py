"""P3 versioned profile sidecar: explicit retained-data and channel chronology.

Carries evidence alongside RFC-0010; does not amend its normative schema.
"""
from __future__ import annotations
import hashlib
import json
import math


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def make_profile(trial_id, model, profile, schedule, record_sha256, acceptance_sha256,
                 source_seal_sha256, preparation_role):
    """Bind one declared trial to actual record identity and deterministic cost."""
    if preparation_role not in ('operational', 'fixed-sector-diagnostic'):
        raise ValueError('explicit preparation role required')
    if profile not in ('DP-P', 'DP-S', 'fresh-data-control'):
        raise ValueError('unknown profile')
    m = len(model.scales)
    duration = 2*(schedule['burn']+schedule['window'])
    gap = 0. if profile == 'DP-P' else sum(schedule[k] for k in ('reset_time', 'retune_time', 'dead_time'))
    if any(not math.isfinite(x) or x < 0 for x in (duration, gap)):
        raise ValueError('invalid chronology')
    retained_id = trial_id+'/data'
    channels, events = [], []
    for slot, j in enumerate(model.scales):
        start = 0. if profile == 'DP-P' else slot*(duration+gap)
        data_id = retained_id if profile != 'fresh-data-control' else retained_id+f'/fresh-{slot}'
        if slot == 0 or profile == 'fresh-data-control':
            events.append({'kind': 'data_preparation', 'time': start, 'data_register_id': data_id,
                           'state': '|1>' if preparation_role == 'operational' else 'diagnostic-only eigenstate'})
        if slot and profile != 'DP-P':
            before = start-gap
            for kind, length in (('probe_reset', schedule['reset_time']),
                                 ('arithmetic_retune', schedule['retune_time']),
                                 ('identity_data_dead_time', schedule['dead_time'])):
                events.append({'kind': kind, 'time': before, 'end': before+length,
                               'data_register_id': data_id, 'coupling_disconnected': True})
                before += length
        for role in ('signal', 'reference'):
            events.append({'kind': role+'_ground_preparation', 'time': start,
                           'probe_id': f'{trial_id}/{role}/'+(f'j{j}' if profile == 'DP-P' else 'reused')})
            channels.append({'channel_id': f'{trial_id}/{role}/j{j}', 'role': role, 'scale': j,
                             'data_register_id': data_id if role == 'signal' else None,
                             'probe_id': f'{trial_id}/{role}/'+(f'j{j}' if profile == 'DP-P' else 'reused'),
                             'reference_for': f'{trial_id}/signal/j{j}' if role == 'reference' else None,
                             'relative_schedule': [
                                 {'command': 0., 'burn': [start, start+schedule['burn']],
                                  'retained': [start+schedule['burn'], start+duration/2]},
                                 {'command': math.pi/2,
                                  'burn': [start+duration/2, start+duration/2+schedule['burn']],
                                  'retained': [start+duration/2+schedule['burn'], start+duration]}]})
    sidecar = {'schema': 'cpc-shor-p3-profile/1', 'trial_id': trial_id, 'profile': profile,
               'preparation_role': preparation_role, 'arithmetic': {'N': model.N, 'a': model.a, 'scales': list(model.scales)},
               'record_sha256': record_sha256, 'acceptance_sha256': acceptance_sha256,
               'source_seal_sha256': source_seal_sha256, 'events': events, 'channels': channels,
               'record_model': 'independent-output finite homodyne collision instruments',
               'burn_policy': 'discarded; likelihood uses averaged channel',
               'hidden_environment': 'inefficient Kraus labels and reset outcomes discarded, not operational inputs',
               'reference_bundle': 'profile sidecar; RFC-0010 optional external_reference remains singular',
               'cost': {'data_qubits': (model.N-1).bit_length(),
                        'signal_probes': m if profile == 'DP-P' else 1,
                        'reference_probes': m if profile == 'DP-P' else 1,
                        'channels': 2*m, 'signal_norm': m*model.g if profile == 'DP-P' else model.g,
                        'reference_norm': m*model.g if profile == 'DP-P' else model.g,
                        'wall_duration': duration if profile == 'DP-P' else m*duration+(m-1)*gap,
                        'data_preparations': m if profile == 'fresh-data-control' else 1,
                        'probe_resets': 0 if profile == 'DP-P' else m-1,
                        'retunes': 0 if profile == 'DP-P' else m-1},
               'classification': 'bounded simulated QND profile; native synthesis remains unresolved'}
    sidecar['GKSL_id'] = identity({'arithmetic': sidecar['arithmetic'],
                                    'g': model.g, 'Gamma': model.Gamma,
                                    'profile': profile, 'jumps': 'local signal/reference lowering'})
    sidecar['instrument_id'] = identity({'GKSL_id': sidecar['GKSL_id'],
                                         'dt': schedule.get('dt'), 'eta': schedule.get('eta'),
                                         'channels': channels, 'map': 'symmetric finite homodyne collision'})
    sidecar['likelihood_id'] = source_seal_sha256+'/full-temporal-common-theta'
    sidecar['estimator_id'] = acceptance_sha256+'/fixed-full-circle-maximizer'
    sidecar['confidence_id'] = acceptance_sha256+'/global-moment-disc-intersection'
    sidecar['nuisance_id'] = acceptance_sha256+'/declared-reference-prior'
    sidecar['record_alignment_id'] = identity({'record_sha256': record_sha256, 'channels': channels})
    sidecar['requirement_evidence'] = {
        'OS-1': {'evidence_id': trial_id+'/arithmetic-generator', 'method': 'compiled-permutation-and-source-identity'},
        'OS-2': {'evidence_id': trial_id+'/base-sector', 'method': 'independent-QND-projector-diagnostic'},
        'DC-5': {'evidence_id': trial_id+'/residue-leakage', 'method': 'post-inference-full-register-residue-check'},
        'DC-6': {'evidence_id': trial_id+'/profile-cost', 'method': 'explicit-clock-channel-and-reset-accounting'},
        'OV-1': {'evidence_id': trial_id+'/retained-record', 'method': 'raw-record-and-channel-alignment-hashes'},
        'OV-4': {'evidence_id': trial_id+'/simulation-boundary', 'method': 'separate-inference-and-independent-diagnostics'}
    }
    sidecar['evidence_status'] = 'identities only; empirical outcomes require separate validation'
    sidecar['events'].sort(key=lambda event: (event['time'], event['kind']))
    sidecar['identity'] = identity(sidecar)
    return sidecar


def validate_profile(sidecar, model, schedule, *, expected_record_sha256,
                     expected_acceptance_sha256, expected_source_seal_sha256):
    """Reconstruct chronology and resource fields; reject arbitrary metadata."""
    expected = make_profile(sidecar['trial_id'], model, sidecar['profile'], schedule,
                            expected_record_sha256, expected_acceptance_sha256,
                            expected_source_seal_sha256, sidecar['preparation_role'])
    if sidecar != expected:
        raise ValueError('profile record/chronology/resource identity mismatch')
    return True
