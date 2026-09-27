from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.linalg import expm

from src.n0_bosonic_model import (
    N0BosonicModel,
    dissipator,
    hermiticity_error,
    logical_probe_operator,
    minimum_eigenvalue,
    trace_error,
)


N0_EFFECTIVE_MEASUREMENT_SCHEMA = (
    "cpc.shor.n0.effective-measurement.v1"
)


@dataclass(frozen=True)
class N0MeasurementConfig:
    beta_rad: float
    measurement_rate_gamma_m: float
    measurement_efficiency_eta: float

    def __post_init__(self) -> None:
        if (
            not isinstance(self.beta_rad, (int, float))
            or isinstance(self.beta_rad, bool)
            or not math.isfinite(self.beta_rad)
        ):
            raise ValueError(
                "beta_rad must be finite"
            )

        if (
            not isinstance(
                self.measurement_rate_gamma_m,
                (int, float),
            )
            or isinstance(
                self.measurement_rate_gamma_m,
                bool,
            )
            or not math.isfinite(
                self.measurement_rate_gamma_m
            )
            or self.measurement_rate_gamma_m < 0
        ):
            raise ValueError(
                "measurement_rate_gamma_m must be "
                "finite and non-negative"
            )

        if (
            not isinstance(
                self.measurement_efficiency_eta,
                (int, float),
            )
            or isinstance(
                self.measurement_efficiency_eta,
                bool,
            )
            or not math.isfinite(
                self.measurement_efficiency_eta
            )
            or not (
                0.0
                <= self.measurement_efficiency_eta
                <= 1.0
            )
        ):
            raise ValueError(
                "measurement_efficiency_eta must lie "
                "in [0, 1]"
            )

    @property
    def schema(self) -> str:
        return N0_EFFECTIVE_MEASUREMENT_SCHEMA


@dataclass(frozen=True)
class DeterministicEvolutionResult:
    final_state: np.ndarray
    step_count: int

    initial_trace_error: float
    final_trace_error: float

    initial_hermiticity_error: float
    final_hermiticity_error: float

    initial_minimum_eigenvalue: float
    final_minimum_eigenvalue: float


def probe_expectation(
    *,
    model: N0BosonicModel,
    rho: np.ndarray,
    beta_rad: float,
) -> float:
    operator = logical_probe_operator(
        cutoff=model.cutoff,
        alpha=model.alpha,
        beta_rad=beta_rad,
    )

    value = np.trace(
        operator @ rho
    )

    if abs(float(np.imag(value))) > 1.0e-10:
        raise ArithmeticError(
            "probe expectation has non-negligible "
            "imaginary component"
        )

    return float(
        np.real(value)
    )


def expected_measurement_increment_rate(
    *,
    model: N0BosonicModel,
    rho: np.ndarray,
    config: N0MeasurementConfig,
) -> float:
    expectation = probe_expectation(
        model=model,
        rho=rho,
        beta_rad=config.beta_rad,
    )

    return (
        2.0
        * math.sqrt(
            config.measurement_efficiency_eta
            * config.measurement_rate_gamma_m
        )
        * expectation
    )


def unconditional_measurement_generator(
    *,
    model: N0BosonicModel,
    rho: np.ndarray,
    config: N0MeasurementConfig,
) -> np.ndarray:
    operator = logical_probe_operator(
        cutoff=model.cutoff,
        alpha=model.alpha,
        beta_rad=config.beta_rad,
    )

    return (
        config.measurement_rate_gamma_m
        * dissipator(
            operator,
            rho,
        )
    )


def total_deterministic_generator(
    *,
    model: N0BosonicModel,
    rho: np.ndarray,
    config: N0MeasurementConfig,
) -> np.ndarray:
    return (
        model.generator(
            rho
        )
        + unconditional_measurement_generator(
            model=model,
            rho=rho,
            config=config,
        )
    )


def _liouvillian_superoperator(
    *,
    model: N0BosonicModel,
    config: N0MeasurementConfig,
) -> np.ndarray:
    """
    Construct the exact finite-dimensional matrix representation of the
    declared time-independent Lindblad generator.

    Column k is L(E_k) in row-major vectorization. This avoids generic
    Runge-Kutta stepping, which need not preserve complete positivity.
    """
    dimension = model.cutoff
    operator_dimension = dimension * dimension

    superoperator = np.zeros(
        (
            operator_dimension,
            operator_dimension,
        ),
        dtype=np.complex128,
    )

    for row in range(dimension):
        for column in range(dimension):
            basis = np.zeros(
                (dimension, dimension),
                dtype=np.complex128,
            )

            basis[row, column] = 1.0

            image = total_deterministic_generator(
                model=model,
                rho=basis,
                config=config,
            )

            basis_index = (
                row * dimension
                + column
            )

            superoperator[
                :,
                basis_index,
            ] = image.reshape(
                operator_dimension,
                order="C",
            )

    return superoperator


def _semigroup_propagator(
    *,
    model: N0BosonicModel,
    config: N0MeasurementConfig,
    dt: float,
) -> np.ndarray:
    liouvillian = _liouvillian_superoperator(
        model=model,
        config=config,
    )

    return expm(
        float(dt)
        * liouvillian
    )


def _semigroup_step(
    *,
    rho: np.ndarray,
    propagator: np.ndarray,
) -> np.ndarray:
    dimension = rho.shape[0]

    vector = rho.reshape(
        dimension * dimension,
        order="C",
    )

    evolved = (
        propagator
        @ vector
    )

    return evolved.reshape(
        (dimension, dimension),
        order="C",
    )


def evolve_deterministic(
    *,
    model: N0BosonicModel,
    initial_state: np.ndarray,
    config: N0MeasurementConfig,
    duration: float | None = None,
    dt: float | None = None,
) -> DeterministicEvolutionResult:
    if initial_state.shape != (
        model.cutoff,
        model.cutoff,
    ):
        raise ValueError(
            "initial_state dimension does not match model"
        )

    model.validate_density_matrix(
        initial_state
    )

    if duration is None:
        duration = model.integration_duration

    if dt is None:
        dt = model.integration_dt

    for name, value in (
        ("duration", duration),
        ("dt", dt),
    ):
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
            or value <= 0
        ):
            raise ValueError(
                f"{name} must be finite and positive"
            )

    ratio = float(duration) / float(dt)

    step_count = int(
        round(ratio)
    )

    if step_count <= 0:
        raise ValueError(
            "duration must contain at least one step"
        )

    if not math.isclose(
        step_count * float(dt),
        float(duration),
        rel_tol=0.0,
        abs_tol=1.0e-12,
    ):
        raise ValueError(
            "duration must be an integer multiple of dt"
        )

    rho = np.array(
        initial_state,
        dtype=np.complex128,
        copy=True,
    )

    initial_trace = trace_error(
        rho
    )

    initial_hermiticity = hermiticity_error(
        rho
    )

    initial_minimum = minimum_eigenvalue(
        rho
    )

    propagator = _semigroup_propagator(
        model=model,
        config=config,
        dt=float(dt),
    )

    for _ in range(step_count):
        rho = _semigroup_step(
            rho=rho,
            propagator=propagator,
        )

        model.validate_density_matrix(
            rho
        )

    return DeterministicEvolutionResult(
        final_state=rho,
        step_count=step_count,
        initial_trace_error=initial_trace,
        final_trace_error=trace_error(
            rho
        ),
        initial_hermiticity_error=(
            initial_hermiticity
        ),
        final_hermiticity_error=(
            hermiticity_error(
                rho
            )
        ),
        initial_minimum_eigenvalue=(
            initial_minimum
        ),
        final_minimum_eigenvalue=(
            minimum_eigenvalue(
                rho
            )
        ),
    )
