"""Exact, bounded P4 input schemas. No diagnostic order or sector inputs."""
from dataclasses import dataclass, asdict
from fractions import Fraction
import hashlib
import json


def canonical(value):
    if isinstance(value, Fraction):
        return [value.numerator, value.denominator]
    if hasattr(value, '__dataclass_fields__'):
        return canonical(asdict(value))
    if isinstance(value, dict):
        return {str(k): canonical(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [canonical(v) for v in value]
    if value is None or type(value) in (str, int, bool):
        return value
    raise ValueError('noncanonical value')


def identity(kind, value):
    data = {'schema': 'cpc-shor-p4-identity/1', 'kind': kind, 'value': canonical(value)}
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def fields(value, expected):
    if type(value) is not dict or set(value) != set(expected):
        raise ValueError('unknown or missing fields; semantic advice forbidden')


def integer(value, lower=0, bits=4096):
    if type(value) is not int or value < lower or value.bit_length() > bits:
        raise ValueError('invalid or oversized integer')
    return value


def hash_string(value):
    if type(value) is not str or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('invalid SHA256 identity')
    return value


def rational(value, bits):
    if type(value) is not list or len(value) != 2:
        raise ValueError('rational requires numerator/denominator pair')
    n, d = value
    integer(n, bits=bits); integer(d, 1, bits)
    result = Fraction(n, d)
    if [result.numerator, result.denominator] != value:
        raise ValueError('rational must be reduced')
    return result


@dataclass(frozen=True)
class Policy:
    max_integer_bits: int = 256
    max_phase_bits: int = 4096
    max_intervals: int = 1024
    max_trials: int = 128
    max_rational_visits: int = 100000
    max_candidates: int = 50000
    max_lcm_calls: int = 100000
    max_factor_divisions: int = 100000
    max_certificate_divisions: int = 100000

    def __post_init__(self):
        for name, value in asdict(self).items():
            integer(value, 0 if name.startswith('max_') else 1, 32)
        if min(self.max_integer_bits, self.max_phase_bits, self.max_intervals, self.max_trials) < 1:
            raise ValueError('positive schema limits required')

    @property
    def identity(self):
        return identity('resource-policy', self)


@dataclass(frozen=True)
class PhaseView:
    N: int
    a: int
    estimate: Fraction
    intervals: tuple
    epsilon: Fraction
    preparation_id: str
    record_sha256: str
    inference_sha256: str
    profile_sha256: str
    acquisition_id: str

    @property
    def identity(self):
        return identity('phase-view', self)


PHASE_FIELDS = ('schema', 'N', 'a', 'estimate', 'intervals', 'epsilon',
                'preparation_id', 'record_sha256', 'inference_sha256',
                'profile_sha256', 'acquisition_id')


def parse_phase(payload, policy):
    from math import gcd
    fields(payload, PHASE_FIELDS)
    if payload['schema'] != 'cpc-shor-p4-phase/1':
        raise ValueError('phase schema')
    N = integer(payload['N'], 2, policy.max_integer_bits)
    a = integer(payload['a'], 1, policy.max_integer_bits)
    if a >= N or gcd(a, N) != 1:
        raise ValueError('admissible unit required')
    estimate = rational(payload['estimate'], policy.max_phase_bits)
    epsilon = rational(payload['epsilon'], policy.max_phase_bits)
    if estimate >= 1 or epsilon > Fraction(1, 2):
        raise ValueError('phase/epsilon range')
    arcs = payload['intervals']
    if type(arcs) is not list or len(arcs) > policy.max_intervals:
        raise ValueError('interval limit')
    intervals = []
    for arc in arcs:
        if type(arc) is not list or len(arc) != 2:
            raise ValueError('arc format')
        lo, hi = (rational(x, policy.max_phase_bits) for x in arc)
        if not 0 <= lo <= hi <= 1:
            raise ValueError('split circular arcs at fixed cut')
        intervals.append((lo, hi))
    for name in ('preparation_id', 'acquisition_id'):
        if type(payload[name]) is not str or not 1 <= len(payload[name]) <= 256:
            raise ValueError('bounded preparation/acquisition identity required')
    for name in ('record_sha256', 'inference_sha256', 'profile_sha256'):
        hash_string(payload[name])
    return PhaseView(N, a, estimate, tuple(intervals), epsilon,
                     payload['preparation_id'], payload['record_sha256'],
                     payload['inference_sha256'], payload['profile_sha256'], payload['acquisition_id'])


def phase_payload(view):
    result = canonical(view)
    result['schema'] = 'cpc-shor-p4-phase/1'
    return result


def validate_phase(view, policy):
    if type(view) is not PhaseView or parse_phase(phase_payload(view), policy) != view:
        raise ValueError('invalid phase object')


@dataclass(frozen=True)
class Candidates:
    phase_identity: str
    decoder: str
    complete: bool
    values: tuple
    status: str
    work: tuple

    @property
    def identity(self):
        return identity('candidate-set', self)


@dataclass(frozen=True)
class Aggregation:
    complete: bool
    values: tuple
    stages: tuple
    candidate_identities: tuple
    status: str
    lcm_calls: int

    @property
    def identity(self):
        return identity('aggregation', self)
