"""Admitted order-finding inputs and answer-independent arithmetic descriptions."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from math import gcd


def digest(value: object) -> str:
    """Hash a canonical JSON description, rejecting nonfinite values."""
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         allow_nan=False).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class ShorInstance:
    """Order-finding domain; primality is deliberately not tested by compilation."""

    N: int
    a: int
    Q: int

    def __post_init__(self) -> None:
        if any(type(v) is not int for v in (self.N, self.a, self.Q)):
            raise ValueError("N, a and Q must be integers")
        if self.N < 3 or self.N % 2 == 0:
            raise ValueError("N must be odd and at least 3")
        if not 1 < self.a < self.N or gcd(self.a, self.N) != 1:
            raise ValueError("a must satisfy 1 < a < N and gcd(a,N)=1")
        if self.Q < 2 or self.Q & (self.Q - 1):
            raise ValueError("Q must be a power of two >= 2")

    @property
    def instance_id(self) -> str:
        return digest(asdict(self))

    def response(self, x: int) -> int:
        """Evaluate the admitted response, without recovering its period."""
        if type(x) is not int or x < 0:
            raise ValueError("x must be a nonnegative integer")
        return pow(self.a, x, self.N)


def load_instance(data: dict) -> ShorInstance:
    """Reject extra advice fields rather than silently ignoring them."""
    if set(data) != {"N", "a", "Q"}:
        raise ValueError("only N, a, Q are admitted; answer advice is forbidden")
    return ShorInstance(**data)


def multiplier_constants(instance: ShorInstance) -> tuple[int, ...]:
    """Repeated-squaring constants for the circuit baseline and tree network."""
    values = [instance.a]
    for _ in range(1, instance.Q.bit_length() - 1):
        values.append(values[-1] ** 2 % instance.N)
    return tuple(values)


def multiplication_tree(instance: ShorInstance) -> dict:
    """Polynomial-description native candidate; no dissipative generator claim."""
    constants = multiplier_constants(instance)
    width = 1 << (len(constants) - 1).bit_length()
    leaves = [{"bit": j, "zero": 1, "one": c}
              for j, c in enumerate(constants)]
    leaves.extend({"constant": 1} for _ in range(width - len(leaves)))
    layers = []
    while width > 1:
        layers.append(tuple((2*j, 2*j+1) for j in range(width // 2)))
        width //= 2
    return {"N": instance.N, "leaves": leaves, "layers": layers,
            "status": "constraint-description-only",
            "coherence": "unproved", "mixing_bound": "unknown"}
