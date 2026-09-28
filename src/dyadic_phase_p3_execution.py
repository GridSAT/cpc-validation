"""Seal-gated full-arithmetic P3 execution. No order/sector sampler.

The pure-state engine explicitly samples unobserved Kraus outcomes. Averaging
those labels gives the frozen inefficient homodyne CP map. Hidden labels and
final kets are NEVER operational inference inputs. All labels commute with
base spectral projectors; discarded records may dephase different sectors.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from src.dyadic_phase_p3 import Bank, compile_bank
from src.dyadic_phase_p3_fast import load_filter

FROZEN_SPEC_SHA256 = "dcba439b0401459efebc4cc4a071357ce91e1355adae32b66d8f8615a4c3dfdb"


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def verify_execution_seal(acceptance_path, seal_path):
    """Fail closed before any random records or output files are created."""
    acceptance_path, seal_path = Path(acceptance_path), Path(seal_path)
    acceptance = json.loads(acceptance_path.read_text())
    seal = json.loads(seal_path.read_text())
    if (acceptance.get('schema') != 'cpc-shor-p3-acceptance/1'
            or seal.get('schema') != 'cpc-shor-p3-source-seal/1'):
        raise ValueError('unsupported preregistration/source-seal schema')
    if (acceptance.get('frozen_spec_sha256') != FROZEN_SPEC_SHA256
            or seal.get('frozen_spec_sha256') != FROZEN_SPEC_SHA256
            or sha256(seal['frozen_spec_path']) != FROZEN_SPEC_SHA256):
        raise ValueError('reviewed frozen mathematics identity mismatch')
    if acceptance_path.stat().st_mode & 0o222 or seal_path.stat().st_mode & 0o222:
        raise PermissionError('acceptance and source seal must be read-only')
    if sha256(acceptance_path) != seal['acceptance_sha256']:
        raise ValueError('acceptance identity mismatch')
    if set(acceptance['gates']) != {f'P3-{x}' for x in 'ABCDEFGH'}:
        raise ValueError('all eight numeric acceptance gates required')
    if not all(acceptance['gates'][f'P3-{x}'].get('numeric_definition') for x in 'ABCDEFGH'):
        raise ValueError('missing numeric gate definition')
    if not seal['deterministic_prechecks_passed'] or not seal['power_error_analysis_complete']:
        raise ValueError('prechecks/power analysis incomplete')
    if seal.get('library_path') not in seal['sources']:
        raise ValueError('execution library is not sealed')
    for name, digest in seal['sources'].items():
        if sha256(name) != digest:
            raise ValueError('sealed source mismatch: '+name)
    for name, digest in seal['required_evidence'].items():
        if sha256(name) != digest:
            raise ValueError('sealed prerequisite mismatch: '+name)
    if not seal.get('dependency_manifest') or not seal.get('dependency_manifest_sha256'):
        raise ValueError('dependency provenance is required')
    from src.dyadic_phase_p3_provenance import verify_manifest
    verify_manifest(seal['dependency_manifest'],seal['dependency_manifest_sha256'])
    return acceptance, seal


def _engine(lib):
    real = np.ctypeslib.ndpointer(dtype=np.float64, flags='C_CONTIGUOUS')
    integer = np.ctypeslib.ndpointer(dtype=np.int64, flags='C_CONTIGUOUS')
    complex_array = np.ctypeslib.ndpointer(dtype=np.complex128, flags='C_CONTIGUOUS')
    counts = np.ctypeslib.ndpointer(dtype=np.uint64, flags='C_CONTIGUOUS')
    lib.p3_generate.argtypes = ([ctypes.c_int]*5+[ctypes.c_double]*4
                               +[real, integer, complex_array, ctypes.c_void_p, ctypes.c_void_p,
                                 real, real, complex_array, counts])
    lib.p3_generate.restype = ctypes.c_int
    return lib.p3_generate


def _compiled_profile(model, profile):
    if profile == 'DP-P':
        channels = compile_bank(model)
        dimension = model.dimension
    elif profile in ('DP-S', 'fresh-data-control'):
        channels = tuple(compile_bank(Bank(model.N, model.a, (j,), model.g, model.Gamma))[0]
                         for j in model.scales)
        dimension = 2*model.d
    else:
        raise ValueError('unknown bounded P3 profile')
    permutations = np.ascontiguousarray([c['permutation'] for c in channels], dtype=np.int64)
    return permutations, dimension


def _run_prepared(model, profile, schedule, seed, initial, library_path):
    """Private physics engine; caller must enforce seal and preparation role."""
    permutations, dimension = _compiled_profile(model, profile)
    dt, burn, window = (schedule[k] for k in ('dt', 'burn', 'window'))
    eta = schedule['eta']; chi = np.ascontiguousarray(schedule['transfer_phases'], dtype=float)
    if (not .005 <= dt <= .04 or not 0 <= eta <= 1 or not 0 <= burn <= 32
            or not 0 < window <= 4096 or window/dt > 500000
            or any(abs(v/dt-round(v/dt)) > 1e-8 for v in (burn, window))
            or chi.shape != (len(model.scales),) or not np.isfinite(chi).all()):
        raise ValueError('invalid schedule')
    initial = np.ascontiguousarray(initial, dtype=complex)
    if initial.shape != (dimension,) or not np.isclose(np.vdot(initial, initial), 1, atol=1e-12):
        raise ValueError('invalid initial ket')
    steps, burn_steps = round(window/dt), round(burn/dt)
    signal = np.empty((len(model.scales), 2, steps), dtype=float)
    reference = np.empty_like(signal); final = np.empty(dimension, complex)
    counters = np.empty(8, dtype=np.uint64)
    bitgen = np.random.PCG64(np.random.SeedSequence(seed))
    interface = bitgen.ctypes
    lib = load_filter(library_path)
    status = _engine(lib)({'DP-P': 0, 'DP-S': 1, 'fresh-data-control': 2}[profile],
                         len(model.scales), model.d, steps, burn_steps,
                         model.g, model.Gamma, eta, dt, chi, permutations, initial,
                         interface.state, ctypes.cast(interface.next_double, ctypes.c_void_p),
                         signal, reference, final, counters)
    if status:
        raise ArithmeticError(f'full-register instrument failed: {status}')
    if (not np.isfinite(signal).all() or not np.isfinite(reference).all()
            or not np.isfinite(final).all() or abs(np.vdot(final, final)-1) > 1e-9):
        raise ArithmeticError('invalid generated state/record')
    return signal, reference, final, counters, bitgen.state


def execute_operational(model, profile, trial_id, acceptance_path, seal_path, output_path):
    """Single |1> preparation, with trial choices obtained only from the seal."""
    acceptance, seal = verify_execution_seal(acceptance_path, seal_path)
    require_human_review(acceptance,seal,seal_path)
    trial = next((t for t in acceptance['trials'] if t['trial_id'] == trial_id), None)
    if (trial is None or trial['role'] != 'operational' or trial['profile'] != profile
            or trial['N'] != model.N or trial['a'] != model.a
            or tuple(trial['scales']) != model.scales
            or model.g != acceptance['g'] or model.Gamma != acceptance['Gamma']):
        raise ValueError('trial not admitted by preregistration')
    if any(key in trial for key in ('r', 's', 'order', 'sector', 'truth', 'initial', 'factors', 'expected_phase')):
        raise ValueError('semantic advice is forbidden in operational trial inputs')
    path = Path(output_path)
    if path.resolve() != Path(trial['record_path']).resolve():
        raise ValueError('record destination is not preregistered')
    if path.exists():
        raise FileExistsError(path)
    _, dimension = _compiled_profile(model, profile)
    initial = np.zeros(dimension, complex); initial[1] = 1
    claim = path.with_suffix(path.suffix+'.started.json')
    with claim.open('x') as f:
        json.dump({'trial_id': trial_id, 'acceptance_sha256': seal['acceptance_sha256'],
                   'record_path': str(path), 'status': 'started; never regenerate under this identity'}, f)
    values = _run_prepared(model, profile, acceptance['schedules'][trial['schedule']],
                           trial['seed'], initial, seal['library_path'])
    signal, reference, final, counts, rng_end = values
    # Exclusive creation prevents silent replacement of any partial/failed run.
    with path.open('xb') as f:
        np.savez(f, signal=signal, reference=reference, diagnostic_final_ket=final,
                 counters=counts, rng_end=json.dumps(rng_end))
    return {'trial_id': trial_id, 'sha256': sha256(path), 'data_preparations': int(counts[0]),
            'scope': 'full arithmetic register with explicit hidden-environment unraveling'}


def require_human_review(acceptance,seal,seal_path):
    """Separate post-freeze review receipt; this task must never create it."""
    if acceptance.get('human_review_required_before_execution') is not True:
        raise ValueError('explicit human-review gate required')
    path=Path(seal_path).parent/'EXECUTION-AUTHORIZATION.json'
    receipt=json.loads(path.read_text())
    if path.stat().st_mode&0o222:raise PermissionError('review receipt must be read-only')
    if (receipt.get('schema')!='cpc-shor-p3-human-review/1'
        or receipt.get('acceptance_sha256')!=seal['acceptance_sha256']
        or receipt.get('source_seal_sha256')!=sha256(seal_path)
        or receipt.get('explicit_human_authorization') is not True
        or not receipt.get('review_reference')):
        raise ValueError('review receipt does not authorize this sealed experiment')
