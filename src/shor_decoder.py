"""Fixed Fourier-sample decoding; no state or semantic oracle access."""
from __future__ import annotations

from dataclasses import dataclass
from math import gcd, lcm

from src.observable_execution import ObservableExecution
from src.shor_order_finding import ShorInstance


@dataclass(frozen=True)
class ShorDecode:
    order_candidate: int | None
    factors: tuple[int, int] | None
    reason: str


def convergent_denominators(numerator: int, denominator: int) -> tuple[int, ...]:
    """Exact continued-fraction convergents, including denominator one."""
    previous, current = 1, 0
    result = []
    while denominator:
        quotient, remainder = divmod(numerator, denominator)
        previous, current = current, quotient * current + previous
        result.append(current)
        numerator, denominator = denominator, remainder
    return tuple(result)


def extract_factors(instance: ShorInstance, order: int) -> ShorDecode:
    """Keep successful order recovery distinct from successful factor extraction."""
    if type(order) is not int or order <= 0 or pow(instance.a, order, instance.N) != 1:
        return ShorDecode(None, None, "invalid-order-candidate")
    if order % 2:
        return ShorDecode(order, None, "odd-order")
    half = pow(instance.a, order // 2, instance.N)
    if half in (1, instance.N - 1):
        return ShorDecode(order, None, "trivial-square-root")
    p, q = sorted((gcd(half - 1, instance.N), gcd(half + 1, instance.N)))
    if not (1 < p < instance.N and 1 < q < instance.N and p*q == instance.N):
        return ShorDecode(order, None, "unsuccessful-factor-extraction")
    return ShorDecode(order, (p, q), "factors-recovered")


def decode_shor(instance: ShorInstance, observed: ObservableExecution) -> ShorDecode:
    """Decode only admitted measured bins; reject malformed or substituted records.

    Candidate denominators are combined by LCM across shots. No trial-order
    search or factorization is performed. Verified candidates may be nonminimal;
    minimality is checked independently by the validation layer.
    """
    if observed.backend_id != "cpc.shor.density" or observed.backend_version != "0.1":
        raise ValueError("unexpected observation backend")
    data = dict(observed.observations)
    if set(data) != {"fourier_bins"}:
        raise ValueError("only Fourier bins are admitted")
    if dict(observed.provenance).get("instance_id") != instance.instance_id:
        raise ValueError("observation instance mismatch")
    bins = data["fourier_bins"]
    if not isinstance(bins, tuple) or any(type(k) is not int or not 0 <= k < instance.Q for k in bins):
        raise ValueError("invalid Fourier bins")
    accumulated = {1}
    for k in bins:
        if k == 0:
            continue
        denominators = {d for d in convergent_denominators(k, instance.Q)
                        if 1 < d < instance.N}
        for old in tuple(accumulated):
            for denominator in denominators:
                candidate = lcm(old, denominator)
                if candidate < instance.N:
                    accumulated.add(candidate)
                if len(accumulated) > 4096:
                    raise ValueError("decoder candidate budget exceeded")
    candidates = sorted(r for r in accumulated if r > 1 and pow(instance.a, r, instance.N) == 1)
    if candidates:
        return extract_factors(instance, candidates[0])
    return ShorDecode(None, None, "insufficient-order-evidence")
