"""Independent, deliberately exhaustive tiny-instance semantic reference.

No compiler, preparation, execution, measurement or decoder module imports this.
"""
from dataclasses import dataclass

from src.shor_order_finding import ShorInstance
from src.shor_decoder import ShorDecode


def reference_order(instance: ShorInstance) -> int:
    """Find the minimal order by independent repeated modular multiplication."""
    value = 1
    for r in range(1, instance.N):
        value = value * instance.a % instance.N
        if value == 1:
            return r
    raise ValueError("no multiplicative order in the admitted domain")


@dataclass(frozen=True)
class ShorValidation:
    reference_order: int
    order_valid: bool
    order_minimal: bool
    factors_valid: bool


def validate_shor(instance: ShorInstance, decoded: ShorDecode) -> ShorValidation:
    """Validate minimality separately from modular identity and factor recovery."""
    r = decoded.order_candidate
    expected = reference_order(instance)
    factors = decoded.factors
    return ShorValidation(expected,
        r is not None and r > 0 and pow(instance.a, r, instance.N) == 1,
        r == expected,
        factors is not None and all(1 < f < instance.N for f in factors)
        and factors[0] * factors[1] == instance.N)
