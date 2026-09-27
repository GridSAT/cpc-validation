import math

import numpy as np
import pytest

from src.n0_bosonic_model import (
    build_default_n0_bosonic_model,
)
from src.n0_effective_measurement import (
    N0MeasurementConfig,
    evolve_deterministic,
    expected_measurement_increment_rate,
    probe_expectation,
    total_deterministic_generator,
    unconditional_measurement_generator,
)


def test_measurement_config_accepts_valid_values():
    config = N0MeasurementConfig(
        beta_rad=0.0,
        measurement_rate_gamma_m=1.0,
        measurement_efficiency_eta=0.8,
    )

    assert config.beta_rad == 0.0
    assert config.measurement_rate_gamma_m == 1.0
    assert config.measurement_efficiency_eta == 0.8


@pytest.mark.parametrize(
    "eta",
    (
        -0.01,
        1.01,
        float("nan"),
        float("inf"),
    ),
)
def test_measurement_efficiency_is_bounded(eta):
    with pytest.raises(
        ValueError,
        match="efficiency",
    ):
        N0MeasurementConfig(
            beta_rad=0.0,
            measurement_rate_gamma_m=1.0,
            measurement_efficiency_eta=eta,
        )


@pytest.mark.parametrize(
    "gamma",
    (
        -1.0,
        float("nan"),
        float("inf"),
    ),
)
def test_measurement_rate_must_be_nonnegative(gamma):
    with pytest.raises(
        ValueError,
        match="measurement_rate",
    ):
        N0MeasurementConfig(
            beta_rad=0.0,
            measurement_rate_gamma_m=gamma,
            measurement_efficiency_eta=0.8,
        )


@pytest.mark.parametrize(
    "theta",
    (
        0.0,
        0.31,
        math.pi / 2.0,
        math.pi,
        1.7 * math.pi,
    ),
)
def test_probe_expectations_follow_phase(theta):
    model = build_default_n0_bosonic_model()

    rho = model.prepared_density_matrix(
        theta
    )

    x_expectation = probe_expectation(
        model=model,
        rho=rho,
        beta_rad=0.0,
    )

    y_expectation = probe_expectation(
        model=model,
        rho=rho,
        beta_rad=math.pi / 2.0,
    )

    assert math.isclose(
        x_expectation,
        math.cos(theta),
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )

    assert math.isclose(
        y_expectation,
        math.sin(theta),
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )


def test_expected_measurement_rate_matches_model_equation():
    model = build_default_n0_bosonic_model()

    rho = model.prepared_density_matrix(
        0.0
    )

    config = N0MeasurementConfig(
        beta_rad=0.0,
        measurement_rate_gamma_m=2.0,
        measurement_efficiency_eta=0.5,
    )

    rate = expected_measurement_increment_rate(
        model=model,
        rho=rho,
        config=config,
    )

    expected = (
        2.0
        * math.sqrt(
            0.5 * 2.0
        )
    )

    assert math.isclose(
        rate,
        expected,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )


def test_measurement_generator_is_trace_preserving():
    model = build_default_n0_bosonic_model()

    rho = model.prepared_density_matrix(
        0.4
    )

    config = N0MeasurementConfig(
        beta_rad=0.0,
        measurement_rate_gamma_m=1.0,
        measurement_efficiency_eta=0.8,
    )

    derivative = (
        unconditional_measurement_generator(
            model=model,
            rho=rho,
            config=config,
        )
    )

    assert abs(
        np.trace(
            derivative
        )
    ) <= 1.0e-12


def test_total_generator_is_trace_preserving():
    model = build_default_n0_bosonic_model()

    rho = model.prepared_density_matrix(
        0.4
    )

    config = N0MeasurementConfig(
        beta_rad=0.0,
        measurement_rate_gamma_m=1.0,
        measurement_efficiency_eta=0.8,
    )

    derivative = (
        total_deterministic_generator(
            model=model,
            rho=rho,
            config=config,
        )
    )

    assert abs(
        np.trace(
            derivative
        )
    ) <= 1.0e-10


def test_zero_measurement_rate_has_zero_measurement_generator():
    model = build_default_n0_bosonic_model()

    rho = model.prepared_density_matrix(
        0.4
    )

    config = N0MeasurementConfig(
        beta_rad=0.0,
        measurement_rate_gamma_m=0.0,
        measurement_efficiency_eta=0.8,
    )

    derivative = (
        unconditional_measurement_generator(
            model=model,
            rho=rho,
            config=config,
        )
    )

    assert np.allclose(
        derivative,
        0.0,
        atol=1.0e-15,
    )


def test_zero_efficiency_removes_observed_mean_not_backaction():
    model = build_default_n0_bosonic_model()

    # Use a state that is not an X_L eigenstate. At theta=0 the
    # prepared state is an X_L eigenstate and D[X_L](rho)=0 exactly,
    # so zero unconditional backaction would be physically correct.
    rho = model.prepared_density_matrix(
        math.pi / 2.0
    )

    config = N0MeasurementConfig(
        beta_rad=0.0,
        measurement_rate_gamma_m=1.0,
        measurement_efficiency_eta=0.0,
    )

    observed = (
        expected_measurement_increment_rate(
            model=model,
            rho=rho,
            config=config,
        )
    )

    generator = (
        unconditional_measurement_generator(
            model=model,
            rho=rho,
            config=config,
        )
    )

    assert observed == 0.0

    assert not np.allclose(
        generator,
        0.0,
        atol=1.0e-15,
    )


def test_short_deterministic_evolution_preserves_density_properties():
    model = build_default_n0_bosonic_model()

    rho = model.prepared_density_matrix(
        0.37
    )

    config = N0MeasurementConfig(
        beta_rad=0.0,
        measurement_rate_gamma_m=0.25,
        measurement_efficiency_eta=0.8,
    )

    result = evolve_deterministic(
        model=model,
        initial_state=rho,
        config=config,
        duration=0.02,
        dt=0.01,
    )

    assert result.step_count == 2

    assert (
        result.final_trace_error
        <= model.trace_tolerance
    )

    assert (
        result.final_hermiticity_error
        <= model.hermiticity_tolerance
    )

    assert (
        result.final_minimum_eigenvalue
        >= -model.positivity_tolerance
    )


def test_evolution_is_deterministic():
    model = build_default_n0_bosonic_model()

    rho = model.prepared_density_matrix(
        0.23
    )

    config = N0MeasurementConfig(
        beta_rad=math.pi / 2.0,
        measurement_rate_gamma_m=0.1,
        measurement_efficiency_eta=0.8,
    )

    first = evolve_deterministic(
        model=model,
        initial_state=rho,
        config=config,
        duration=0.02,
        dt=0.01,
    )

    second = evolve_deterministic(
        model=model,
        initial_state=rho,
        config=config,
        duration=0.02,
        dt=0.01,
    )

    assert np.array_equal(
        first.final_state,
        second.final_state,
    )


def test_duration_must_be_integer_multiple_of_dt():
    model = build_default_n0_bosonic_model()

    rho = model.prepared_density_matrix(
        0.0
    )

    config = N0MeasurementConfig(
        beta_rad=0.0,
        measurement_rate_gamma_m=0.1,
        measurement_efficiency_eta=0.8,
    )

    with pytest.raises(
        ValueError,
        match="integer multiple",
    ):
        evolve_deterministic(
            model=model,
            initial_state=rho,
            config=config,
            duration=0.025,
            dt=0.01,
        )
