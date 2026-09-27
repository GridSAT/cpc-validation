"""Witness O: full modular permutation, with no supplied orbit length."""
import math

import numpy as np

from src.shor_order_finding import ShorInstance


def orbit_hamiltonian(instance: ShorInstance, g: float = 1.0) -> np.ndarray:
    """Compile g(U+U†) from modular multiplication, without orbit traversal."""
    if isinstance(g, bool) or not isinstance(g, (int, float)) or not math.isfinite(g) or g <= 0:
        raise ValueError("g must be finite and positive")
    if instance.N > 512:
        raise ValueError("orbit-spectrum witness exceeds dense matrix budget")
    permutation = np.zeros((instance.N, instance.N))
    for y in range(instance.N):
        permutation[instance.a*y % instance.N, y] = 1
    return g * (permutation + permutation.T)


def orbit_spectral_measure(instance: ShorInstance, g: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """Numerically observe spectrum weighted by the prepared |1> state."""
    energies, vectors = np.linalg.eigh(orbit_hamiltonian(instance, g))
    return energies, np.abs(vectors[1, :])**2


def reference_resolution_diagnostic(order: int, g: float = 1.0) -> dict:
    """Reference-only scaling diagnostic; never an input to compilation.

    The characteristic time 1/delta is a resolution scale, not a measured
    complete time-to-solution or a universal instrumentation bound.
    """
    if type(order) is not int or order < 2 or not math.isfinite(g) or g <= 0:
        raise ValueError("order >= 2 and positive finite g are required")
    spacing = 4*g*math.sin(math.pi/order)**2
    return {"reference_order": order, "band_edge_spacing": spacing,
            "inverse_spacing_time": 1/spacing,
            "efficiency_claim": False, "scope": "reference-only"}
