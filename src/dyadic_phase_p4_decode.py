"""Frozen exact-rational POINT/SET profiles; no order oracle or truth fields."""
from fractions import Fraction
from math import gcd, lcm
from src.dyadic_phase_p4_types import Candidates, Aggregation, validate_phase


def circular_distance(x, y):
    z = abs(x - y) % 1
    return min(z, 1-z)


def convergents(x):
    pm2, pm1, qm2, qm1 = 0, 1, 1, 0
    while True:
        a = x.numerator // x.denominator
        p, q = a*pm1+pm2, a*qm1+qm2
        yield Fraction(p, q)
        remainder = x-a
        if not remainder:
            return
        x = 1/remainder
        pm2, pm1, qm2, qm1 = pm1, p, qm1, q


def expanded_intervals(view):
    intervals = []
    for lo, hi in view.intervals:
        lo, hi = lo-view.epsilon, hi+view.epsilon
        if hi-lo >= 1:
            return ((Fraction(0), Fraction(1)),)
        for shift in (-1, 0, 1):
            left, right = max(Fraction(0), lo+shift), min(Fraction(1), hi+shift)
            if left <= right:
                intervals.append((left, right))
    merged = []
    for lo, hi in sorted(intervals):
        if merged and lo <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(hi, merged[-1][1]))
        else:
            merged.append((lo, hi))
    return tuple(merged)


def contains(intervals, value):
    return any(lo <= value <= hi or (value == 0 and hi == 1) for lo, hi in intervals)


def decode_point(N, a, phase_view, policy):
    validate_phase(phase_view, policy)
    if (N, a) != (phase_view.N, phase_view.a):
        raise ValueError('instance mismatch')
    found = set(); steps = 0
    for shift in (-1, 0, 1):
        for value in convergents(phase_view.estimate+shift):
            steps += 1
            if value.denominator < N and circular_distance(value, phase_view.estimate) < Fraction(1, 2*N*N):
                found.add(value % 1)
    if len(found) > 1:
        raise ArithmeticError('strict-neighborhood uniqueness violated')
    return Candidates(phase_view.identity, 'POINT', True, tuple(sorted(found)),
                      'CANDIDATES' if found else 'INSUFFICIENT_PHASE_RESOLUTION', (('cf_steps', steps),))


def decode_set(N, a, phase_view, policy):
    validate_phase(phase_view, policy)
    if (N, a) != (phase_view.N, phase_view.a):
        raise ValueError('instance mismatch')
    intervals = expanded_intervals(phase_view)
    found = set(); visits = 0
    for q in range(1, N):
        for p in range(q):
            if visits >= policy.max_rational_visits:
                return Candidates(phase_view.identity, 'SET', False, tuple(sorted(found)),
                                  'ENUMERATION_INCOMPLETE', (('rational_visits', visits),))
            visits += 1
            if gcd(p, q) == 1 and contains(intervals, Fraction(p, q)):
                if len(found) >= policy.max_candidates:
                    return Candidates(phase_view.identity, 'SET', False, tuple(sorted(found)),
                                      'ENUMERATION_INCOMPLETE', (('rational_visits', visits),))
                found.add(Fraction(p, q))
    return Candidates(phase_view.identity, 'SET', True, tuple(sorted(found)),
                      'CANDIDATES' if found else 'EMPTY_PHASE_CANDIDATES', (('rational_visits', visits),))


def aggregate(N, a, candidate_views, phase_views, policy):
    if not 1 <= len(phase_views) == len(candidate_views) <= policy.max_trials:
        raise ValueError('trial count')
    for v in phase_views:
        validate_phase(v, policy)
        if (v.N, v.a) != (N, a):
            raise ValueError('instance mismatch')
    if len({v.preparation_id for v in phase_views}) != len(phase_views):
        raise ValueError('same preparation is not a fresh trial')
    if len({v.record_sha256 for v in phase_views}) != len(phase_views):
        raise ValueError('duplicate record is not a fresh trial')
    if any(type(c) is not Candidates for c in candidate_views):
        raise ValueError('candidate type')
    ids = tuple(c.identity for c in candidate_views)
    for c, v in zip(candidate_views, phase_views):
        if type(c) is not Candidates or c.phase_identity != v.identity:
            raise ValueError('candidate identity mismatch')
        if c.decoder not in ('POINT', 'SET'):
            raise ValueError('unknown candidate decoder')
        expected = (decode_point if c.decoder == 'POINT' else decode_set)(N, a, v, policy)
        if c != expected:
            raise ValueError('candidate content/completeness is not decoder output')
        if not c.complete:
            return Aggregation(False, (), (), ids, 'AGGREGATION_INCOMPLETE', 0)
        if any(type(x) is not Fraction or not 0 <= x < 1 or x.denominator >= N for x in c.values):
            raise ValueError('invalid candidate rational')
    states = {1}; stages = []; calls = 0
    for c in candidate_views:
        new = set(); witnesses = {}
        for previous in sorted(states):
            for q in sorted({x.denominator for x in c.values}):
                if calls >= policy.max_lcm_calls:
                    return Aggregation(False, tuple(sorted(new)), tuple(stages), ids, 'AGGREGATION_INCOMPLETE', calls)
                calls += 1
                R = lcm(previous, q)
                if R < N:
                    new.add(R)
                    witnesses.setdefault(R, (previous, q))
        states = new
        stages.append(tuple((R, *witnesses[R]) for R in sorted(states)))
    status = 'CANDIDATE_ORDER' if len(states) == 1 else ('AMBIGUOUS_CANDIDATES' if states else 'VERIFICATION_FAILURE')
    return Aggregation(True, tuple(sorted(states)), tuple(stages), ids, status, calls)
