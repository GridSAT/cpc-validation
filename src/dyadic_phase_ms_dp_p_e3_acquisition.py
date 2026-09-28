"""MS-DP-P E3-Ib acquisition adapter.

Bounded DP-S equality-in-law simulator for the MS-DP-P stochastic candidate.
DP-P remains the primary physical architecture. This module does not authorize
execution; final stochastic use requires a later sealed E3 prerecord.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import ctypes
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np

from src.dyadic_phase_ms_dp_p import DEFAULT_DELTA, required_highest_scale
from src.dyadic_phase_p3_execution import _engine
from src.dyadic_phase_p3_fast import load_filter


class AcquisitionError(ValueError):
    pass


@dataclass(frozen=True)
class SequentialBank:
    N: int
    a: int
    scales: tuple[int, ...] | None = None
    g: float = 1 / math.sqrt(8)
    Gamma: float = 1.0

    def __post_init__(self):
        if type(self.N) is not int or not 2 <= self.N <= 15:
            raise AcquisitionError("bounded E3 domain requires integer 2 <= N <= 15")
        if type(self.a) is not int or not 1 <= self.a < self.N or math.gcd(self.a, self.N) != 1:
            raise AcquisitionError("coprime arithmetic input required")
        expected = tuple(range(required_highest_scale(self.N, DEFAULT_DELTA) + 1))
        actual = expected if self.scales is None else self.scales
        if actual != expected:
            raise AcquisitionError("E3 requires the exact frozen multiscale set 0..J")
        object.__setattr__(self, "scales", actual)
        if not all(type(x) in (int, float) and math.isfinite(x) and x > 0
                   for x in (self.g, self.Gamma)):
            raise AcquisitionError("positive finite rates required")

    @property
    def d(self) -> int:
        return 1 << (self.N - 1).bit_length()

    @property
    def dimension(self) -> int:
        return 2 * self.d


def compile_dp_s_permutations(model: SequentialBank) -> np.ndarray:
    """Compile one single-probe modular permutation per dyadic scale."""
    d = model.d
    D = model.dimension
    rows = []
    for j in model.scales:
        c = pow(model.a, 1 << j, model.N)
        inverse = pow(c, -1, model.N)
        perm = np.array([
            (probe ^ 1) * d
            + ((inverse if probe else c) * y % model.N if y < model.N else y)
            for probe in (0, 1)
            for y in range(d)
        ], dtype=np.int64)
        if len(perm) != D or len(set(map(int, perm))) != D:
            raise ArithmeticError("compiled local Hamiltonian map is not a permutation")
        if not np.array_equal(perm[perm], np.arange(D, dtype=np.int64)):
            raise ArithmeticError("compiled local Hamiltonian map is not involutive")
        rows.append(perm)
    return np.ascontiguousarray(rows, dtype=np.int64)


def validate_schedule(model: SequentialBank, schedule: dict) -> dict:
    required = {
        "dt", "burn", "window", "eta", "transfer_phases",
        "reset_time", "retune_time", "dead_time",
    }
    if set(schedule) != required:
        raise AcquisitionError("exact E3 schedule fields required")
    dt = float(schedule["dt"])
    burn = float(schedule["burn"])
    window = float(schedule["window"])
    eta = float(schedule["eta"])
    gaps = tuple(float(schedule[k]) for k in ("reset_time", "retune_time", "dead_time"))
    chi = np.asarray(schedule["transfer_phases"], dtype=float)
    if (not .005 <= dt <= .04 or not 0 <= eta <= 1 or not 0 <= burn <= 32
            or not 0 < window <= 4096 or window / dt > 500000
            or any(abs(v / dt - round(v / dt)) > 1e-8 for v in (burn, window))
            or chi.shape != (len(model.scales),) or not np.isfinite(chi).all()
            or any(not math.isfinite(x) or x < 0 for x in gaps)):
        raise AcquisitionError("invalid E3 DP-S schedule")
    return {
        "dt": dt,
        "burn": burn,
        "window": window,
        "eta": eta,
        "transfer_phases": np.ascontiguousarray(chi, dtype=float),
        "reset_time": gaps[0],
        "retune_time": gaps[1],
        "dead_time": gaps[2],
        "steps": round(window / dt),
        "burn_steps": round(burn / dt),
    }


def structural_resource_profile(model: SequentialBank, schedule: dict) -> dict:
    s = validate_schedule(model, schedule)
    m = len(model.scales)
    steps = s["steps"]
    record_bytes = 2 * m * 2 * steps * np.dtype(np.float64).itemsize
    duration = 2 * (s["burn"] + s["window"])
    gap = s["reset_time"] + s["retune_time"] + s["dead_time"]
    return {
        "schema": "cpc-shor-ms-dp-p-e3ib-resource/1",
        "profile": "DP-S-equality-in-law-simulator",
        "N": model.N,
        "a": model.a,
        "highest_scale": model.scales[-1],
        "scale_count": m,
        "data_dimension": model.d,
        "state_dimension": model.dimension,
        "data_preparations": 1,
        "signal_probes": 1,
        "reference_probes": 1,
        "probe_resets": m - 1,
        "retunes": m - 1,
        "record_float64_values": 2 * m * 2 * steps,
        "record_buffer_bytes": record_bytes,
        "permutation_bytes": m * model.dimension * np.dtype(np.int64).itemsize,
        "final_state_bytes": model.dimension * np.dtype(np.complex128).itemsize,
        "physical_wall_duration_Gamma_inverse": m * duration + (m - 1) * gap,
        "native_dimension_independent_of_scale_count": True,
        "DP_P_physical_resource_equivalence_claimed": False,
    }


def local_referenced_phase(signal_record, reference_record, dt: float) -> Fraction:
    """Record-only E1-A matched-reference vector estimator, in phase cycles."""
    sig = np.asarray(signal_record, dtype=float)
    ref = np.asarray(reference_record, dtype=float)
    if (sig.shape != ref.shape or sig.ndim != 2 or sig.shape[0] != 2
            or sig.shape[1] < 1 or not np.isfinite(sig).all()
            or not np.isfinite(ref).all() or not math.isfinite(dt) or dt <= 0):
        raise AcquisitionError("invalid local referenced records")
    window = sig.shape[1] * dt
    sigmean = sig.sum(axis=1) / window
    refmean = ref.sum(axis=1) / window
    zs = -sigmean[1] + 1j * sigmean[0]
    zr = -refmean[1] + 1j * refmean[0]
    w = zs * zr.conjugate()
    if not math.isfinite(w.real) or not math.isfinite(w.imag) or abs(w) == 0:
        raise AcquisitionError("undefined referenced phase")
    phase = (math.atan2(w.imag, w.real) / (2 * math.pi)) % 1.0
    return Fraction.from_float(phase)


def local_phases_from_records(signal, reference, dt: float) -> tuple[Fraction, ...]:
    sig = np.asarray(signal, dtype=float)
    ref = np.asarray(reference, dtype=float)
    if sig.shape != ref.shape or sig.ndim != 3 or sig.shape[1] != 2:
        raise AcquisitionError("expected records shaped (scales,2,steps)")
    return tuple(local_referenced_phase(s, r, dt) for s, r in zip(sig, ref))


def channel_record_sha256(scale: int, signal_record, reference_record) -> str:
    sig = np.ascontiguousarray(signal_record, dtype="<f8")
    ref = np.ascontiguousarray(reference_record, dtype="<f8")
    if sig.shape != ref.shape or sig.ndim != 2 or sig.shape[0] != 2:
        raise AcquisitionError("invalid local record shape")
    h = hashlib.sha256()
    meta = json.dumps({
        "schema": "cpc-shor-ms-dp-p-e3ib-channel-record/1",
        "scale": int(scale),
        "shape": list(sig.shape),
        "dtype": "<f8",
    }, sort_keys=True, separators=(",", ":")).encode()
    h.update(meta)
    h.update(sig.tobytes(order="C"))
    h.update(ref.tobytes(order="C"))
    return h.hexdigest()


def _native_call(model: SequentialBank, schedule: dict, initial, library_path,
                 rng_state, next_double_ptr):
    s = validate_schedule(model, schedule)
    perms = compile_dp_s_permutations(model)
    D = model.dimension
    initial = np.ascontiguousarray(initial, dtype=np.complex128)
    if initial.shape != (D,) or not np.isclose(np.vdot(initial, initial), 1, atol=1e-12):
        raise AcquisitionError("invalid initial ket")
    signal = np.empty((len(model.scales), 2, s["steps"]), dtype=np.float64)
    reference = np.empty_like(signal)
    final = np.empty(D, dtype=np.complex128)
    counters = np.empty(8, dtype=np.uint64)
    lib = load_filter(library_path)
    status = _engine(lib)(
        1, len(model.scales), model.d, s["steps"], s["burn_steps"],
        model.g, model.Gamma, s["eta"], s["dt"], s["transfer_phases"],
        perms, initial, rng_state, next_double_ptr,
        signal, reference, final, counters,
    )
    if status:
        raise ArithmeticError(f"E3 DP-S native instrument failed: {status}")
    if (not np.isfinite(signal).all() or not np.isfinite(reference).all()
            or not np.isfinite(final).all()
            or abs(np.vdot(final, final) - 1) > 1e-9):
        raise ArithmeticError("invalid E3 generated state/record")
    return signal, reference, final, counters


def run_operational(model: SequentialBank, schedule: dict, seed_words, library_path):
    """Stochastic primitive. Final prerecord/authorization must gate every call."""
    words = tuple(seed_words)
    if len(words) != 8 or any(type(x) is not int or not 0 <= x < 2**32 for x in words):
        raise AcquisitionError("exactly eight uint32 seed words required")
    initial = np.zeros(model.dimension, dtype=np.complex128)
    initial[1] = 1
    bitgen = np.random.PCG64(np.random.SeedSequence(words))
    interface = bitgen.ctypes
    values = _native_call(
        model, schedule, initial, library_path,
        interface.state, ctypes.cast(interface.next_double, ctypes.c_void_p),
    )
    signal, reference, final, counters = values
    if int(counters[0]) != 1 or int(counters[4]) != len(model.scales) - 1:
        raise ArithmeticError("DP-S preparation/reset counters violate contract")
    return signal, reference, final, counters, bitgen.state


def profile_fixed_callback(model: SequentialBank, schedule: dict, library_path,
                           callback_value: float = 0.125):
    """Deterministic resource dry-run: fixed callback, no PRNG, outputs discarded."""
    if not 0 < callback_value < 1:
        raise AcquisitionError("profiling callback must lie in (0,1)")
    initial = np.zeros(model.dimension, dtype=np.complex128)
    initial[1] = 1
    CALLBACK = ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_void_p)

    @CALLBACK
    def fixed(_):
        return callback_value

    t0 = time.perf_counter()
    signal, reference, final, counters = _native_call(
        model, schedule, initial, library_path,
        None, ctypes.cast(fixed, ctypes.c_void_p),
    )
    seconds = time.perf_counter() - t0
    shape = list(signal.shape)
    del signal, reference, final
    return {
        "schema": "cpc-shor-ms-dp-p-e3ib-fixed-callback-profile/1",
        "classification": "deterministic fixed-callback dry-run; no PRNG; arrays discarded",
        "N": model.N,
        "a": model.a,
        "scale_count": len(model.scales),
        "record_shape": shape,
        "counters": [int(x) for x in counters],
        "seconds": seconds,
        "callback_value": callback_value,
        "stochastic_records_generated": 0,
    }
