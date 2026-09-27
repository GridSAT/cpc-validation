from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


N0_BOSONIC_MODEL_SCHEMA = "cpc.shor.n0.bosonic-model.v1"


def annihilation_operator(
    cutoff: int,
) -> np.ndarray:
    if (
        not isinstance(cutoff, int)
        or isinstance(cutoff, bool)
        or cutoff < 2
    ):
        raise ValueError(
            "cutoff must be an integer >= 2"
        )

    a = np.zeros(
        (cutoff, cutoff),
        dtype=np.complex128,
    )

    for n in range(1, cutoff):
        a[n - 1, n] = math.sqrt(n)

    return a


def creation_operator(
    cutoff: int,
) -> np.ndarray:
    return annihilation_operator(
        cutoff
    ).conjugate().T


def number_operator(
    cutoff: int,
) -> np.ndarray:
    a = annihilation_operator(
        cutoff
    )

    return a.conjugate().T @ a


def coherent_state(
    cutoff: int,
    alpha: complex,
) -> np.ndarray:
    if (
        not isinstance(alpha, (int, float, complex))
        or isinstance(alpha, bool)
    ):
        raise ValueError(
            "alpha must be numeric"
        )

    coeffs = np.zeros(
        cutoff,
        dtype=np.complex128,
    )

    coeffs[0] = 1.0 + 0.0j

    for n in range(1, cutoff):
        coeffs[n] = (
            coeffs[n - 1]
            * complex(alpha)
            / math.sqrt(n)
        )

    coeffs *= math.exp(
        -0.5 * abs(complex(alpha)) ** 2
    )

    norm = np.linalg.norm(
        coeffs
    )

    if norm == 0.0:
        raise ValueError(
            "coherent-state truncation has zero norm"
        )

    return coeffs / norm


def normalized_state(
    vector: np.ndarray,
) -> np.ndarray:
    if (
        not isinstance(vector, np.ndarray)
        or vector.ndim != 1
    ):
        raise ValueError(
            "vector must be a one-dimensional ndarray"
        )

    norm = np.linalg.norm(
        vector
    )

    if (
        not np.isfinite(norm)
        or norm <= 0.0
    ):
        raise ValueError(
            "vector must have finite nonzero norm"
        )

    return vector / norm


def density_matrix(
    vector: np.ndarray,
) -> np.ndarray:
    state = normalized_state(
        vector
    )

    return np.outer(
        state,
        state.conjugate(),
    )


def cat_basis(
    cutoff: int,
    alpha: complex,
) -> tuple[np.ndarray, np.ndarray]:
    plus_alpha = coherent_state(
        cutoff,
        alpha,
    )

    minus_alpha = coherent_state(
        cutoff,
        -complex(alpha),
    )

    even = normalized_state(
        plus_alpha + minus_alpha
    )

    odd = normalized_state(
        plus_alpha - minus_alpha
    )

    overlap = np.vdot(
        even,
        odd,
    )

    if not np.isclose(
        overlap,
        0.0 + 0.0j,
        rtol=0.0,
        atol=1.0e-12,
    ):
        raise ArithmeticError(
            "cat basis is not numerically orthogonal"
        )

    return even, odd


def logical_phase_state(
    *,
    cutoff: int,
    alpha: complex,
    theta_rad: float,
) -> np.ndarray:
    if (
        not isinstance(theta_rad, (int, float))
        or isinstance(theta_rad, bool)
        or not math.isfinite(theta_rad)
    ):
        raise ValueError(
            "theta_rad must be a finite number"
        )

    logical_zero, logical_one = cat_basis(
        cutoff,
        alpha,
    )

    vector = (
        logical_zero
        + np.exp(
            1.0j * float(theta_rad)
        ) * logical_one
    ) / math.sqrt(2.0)

    return normalized_state(
        vector
    )


def projector(
    vector: np.ndarray,
) -> np.ndarray:
    state = normalized_state(
        vector
    )

    return np.outer(
        state,
        state.conjugate(),
    )


def protected_projector(
    *,
    cutoff: int,
    alpha: complex,
) -> np.ndarray:
    logical_zero, logical_one = cat_basis(
        cutoff,
        alpha,
    )

    return (
        projector(logical_zero)
        + projector(logical_one)
    )


def logical_pauli_x(
    *,
    cutoff: int,
    alpha: complex,
) -> np.ndarray:
    logical_zero, logical_one = cat_basis(
        cutoff,
        alpha,
    )

    return (
        np.outer(
            logical_zero,
            logical_one.conjugate(),
        )
        + np.outer(
            logical_one,
            logical_zero.conjugate(),
        )
    )


def logical_pauli_y(
    *,
    cutoff: int,
    alpha: complex,
) -> np.ndarray:
    logical_zero, logical_one = cat_basis(
        cutoff,
        alpha,
    )

    return (
        -1.0j
        * np.outer(
            logical_zero,
            logical_one.conjugate(),
        )
        + 1.0j
        * np.outer(
            logical_one,
            logical_zero.conjugate(),
        )
    )


def logical_probe_operator(
    *,
    cutoff: int,
    alpha: complex,
    beta_rad: float,
) -> np.ndarray:
    if (
        not isinstance(beta_rad, (int, float))
        or isinstance(beta_rad, bool)
        or not math.isfinite(beta_rad)
    ):
        raise ValueError(
            "beta_rad must be finite"
        )

    return (
        math.cos(beta_rad)
        * logical_pauli_x(
            cutoff=cutoff,
            alpha=alpha,
        )
        + math.sin(beta_rad)
        * logical_pauli_y(
            cutoff=cutoff,
            alpha=alpha,
        )
    )


def dissipator(
    jump: np.ndarray,
    rho: np.ndarray,
) -> np.ndarray:
    if (
        jump.ndim != 2
        or rho.ndim != 2
        or jump.shape[0] != jump.shape[1]
        or rho.shape[0] != rho.shape[1]
        or jump.shape != rho.shape
    ):
        raise ValueError(
            "jump and rho must be same-size square matrices"
        )

    jump_dagger = jump.conjugate().T
    gram = jump_dagger @ jump

    return (
        jump @ rho @ jump_dagger
        - 0.5 * (
            gram @ rho
            + rho @ gram
        )
    )


def cat_stabilization_generator(
    *,
    cutoff: int,
    alpha: complex,
    kappa_2: float,
    kappa_1: float,
    kappa_phi: float,
    rho: np.ndarray,
) -> np.ndarray:
    for name, value in (
        ("kappa_2", kappa_2),
        ("kappa_1", kappa_1),
        ("kappa_phi", kappa_phi),
    ):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or value < 0
        ):
            raise ValueError(
                f"{name} must be finite and non-negative"
            )

    if rho.shape != (cutoff, cutoff):
        raise ValueError(
            "rho dimension does not match cutoff"
        )

    a = annihilation_operator(
        cutoff
    )

    n = number_operator(
        cutoff
    )

    identity = np.eye(
        cutoff,
        dtype=np.complex128,
    )

    two_photon_jump = (
        a @ a
        - complex(alpha) ** 2
        * identity
    )

    return (
        float(kappa_2)
        * dissipator(
            two_photon_jump,
            rho,
        )
        + float(kappa_1)
        * dissipator(
            a,
            rho,
        )
        + float(kappa_phi)
        * dissipator(
            n,
            rho,
        )
    )


def trace_error(
    rho: np.ndarray,
) -> float:
    return abs(
        complex(np.trace(rho))
        - 1.0
    )


def hermiticity_error(
    rho: np.ndarray,
) -> float:
    return float(
        np.max(
            np.abs(
                rho
                - rho.conjugate().T
            )
        )
    )


def minimum_eigenvalue(
    rho: np.ndarray,
) -> float:
    hermitian = (
        rho
        + rho.conjugate().T
    ) / 2.0

    eigenvalues = np.linalg.eigvalsh(
        hermitian
    )

    return float(
        np.min(eigenvalues)
    )


def protected_manifold_leakage(
    *,
    rho: np.ndarray,
    cutoff: int,
    alpha: complex,
) -> float:
    p = protected_projector(
        cutoff=cutoff,
        alpha=alpha,
    )

    retained = float(
        np.real(
            np.trace(
                p @ rho
            )
        )
    )

    leakage = 1.0 - retained

    if abs(leakage) < 1.0e-15:
        leakage = 0.0

    return leakage


@dataclass(frozen=True)
class N0BosonicModel:
    cutoff: int
    alpha: float

    kappa_2: float
    kappa_1: float
    kappa_phi: float

    integration_dt: float
    integration_duration: float

    trace_tolerance: float = 1.0e-10
    hermiticity_tolerance: float = 1.0e-10
    positivity_tolerance: float = 1.0e-10

    def __post_init__(self) -> None:
        if (
            not isinstance(self.cutoff, int)
            or isinstance(self.cutoff, bool)
            or self.cutoff < 2
        ):
            raise ValueError(
                "cutoff must be an integer >= 2"
            )

        for name, value in (
            ("alpha", self.alpha),
            ("kappa_2", self.kappa_2),
            ("kappa_1", self.kappa_1),
            ("kappa_phi", self.kappa_phi),
            ("integration_dt", self.integration_dt),
            (
                "integration_duration",
                self.integration_duration,
            ),
            (
                "trace_tolerance",
                self.trace_tolerance,
            ),
            (
                "hermiticity_tolerance",
                self.hermiticity_tolerance,
            ),
            (
                "positivity_tolerance",
                self.positivity_tolerance,
            ),
        ):
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(value)
            ):
                raise ValueError(
                    f"{name} must be finite"
                )

        if self.alpha <= 0:
            raise ValueError(
                "alpha must be positive"
            )

        if any(
            value < 0
            for value in (
                self.kappa_2,
                self.kappa_1,
                self.kappa_phi,
            )
        ):
            raise ValueError(
                "kappa values must be non-negative"
            )

        if self.integration_dt <= 0:
            raise ValueError(
                "integration_dt must be positive"
            )

        if self.integration_duration <= 0:
            raise ValueError(
                "integration_duration must be positive"
            )

        if any(
            value <= 0
            for value in (
                self.trace_tolerance,
                self.hermiticity_tolerance,
                self.positivity_tolerance,
            )
        ):
            raise ValueError(
                "numerical tolerances must be positive"
            )

    @property
    def schema(self) -> str:
        return N0_BOSONIC_MODEL_SCHEMA

    def prepared_density_matrix(
        self,
        theta_rad: float,
    ) -> np.ndarray:
        return density_matrix(
            logical_phase_state(
                cutoff=self.cutoff,
                alpha=self.alpha,
                theta_rad=theta_rad,
            )
        )

    def generator(
        self,
        rho: np.ndarray,
    ) -> np.ndarray:
        return cat_stabilization_generator(
            cutoff=self.cutoff,
            alpha=self.alpha,
            kappa_2=self.kappa_2,
            kappa_1=self.kappa_1,
            kappa_phi=self.kappa_phi,
            rho=rho,
        )

    def diagnostics(
        self,
        rho: np.ndarray,
    ) -> dict[str, float]:
        return {
            "trace_error": trace_error(
                rho
            ),
            "hermiticity_error": (
                hermiticity_error(
                    rho
                )
            ),
            "minimum_eigenvalue": (
                minimum_eigenvalue(
                    rho
                )
            ),
            "protected_manifold_leakage": (
                protected_manifold_leakage(
                    rho=rho,
                    cutoff=self.cutoff,
                    alpha=self.alpha,
                )
            ),
        }

    def validate_density_matrix(
        self,
        rho: np.ndarray,
    ) -> None:
        diagnostics = self.diagnostics(
            rho
        )

        if (
            diagnostics["trace_error"]
            > self.trace_tolerance
        ):
            raise ArithmeticError(
                "density matrix violates trace tolerance"
            )

        if (
            diagnostics["hermiticity_error"]
            > self.hermiticity_tolerance
        ):
            raise ArithmeticError(
                "density matrix violates hermiticity tolerance"
            )

        if (
            diagnostics["minimum_eigenvalue"]
            < -self.positivity_tolerance
        ):
            raise ArithmeticError(
                "density matrix violates positivity tolerance"
            )


def build_default_n0_bosonic_model() -> N0BosonicModel:
    return N0BosonicModel(
        cutoff=16,
        alpha=1.5,
        kappa_2=1.0,
        kappa_1=0.0,
        kappa_phi=0.0,
        integration_dt=0.01,
        integration_duration=1.0,
    )
