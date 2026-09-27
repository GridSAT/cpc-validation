import math

import numpy as np
import pytest

from src.n0_bosonic_model import (
    annihilation_operator,
    build_default_n0_bosonic_model,
    cat_basis,
    coherent_state,
    density_matrix,
    dissipator,
    logical_pauli_x,
    logical_pauli_y,
    logical_phase_state,
    logical_probe_operator,
    protected_manifold_leakage,
    protected_projector,
)


def test_annihilation_operator_has_expected_entries():
    a = annihilation_operator(4)

    assert a.shape == (4, 4)
    assert a[0, 1] == 1.0
    assert math.isclose(
        a[1, 2],
        math.sqrt(2.0),
    )
    assert math.isclose(
        a[2, 3],
        math.sqrt(3.0),
    )


def test_coherent_state_is_normalized():
    state = coherent_state(
        16,
        1.5,
    )

    assert math.isclose(
        float(
            np.real(
                np.vdot(
                    state,
                    state,
                )
            )
        ),
        1.0,
        rel_tol=0.0,
        abs_tol=1.0e-14,
    )


def test_cat_basis_is_orthonormal():
    even, odd = cat_basis(
        16,
        1.5,
    )

    assert np.isclose(
        np.vdot(even, even),
        1.0,
        atol=1.0e-14,
    )

    assert np.isclose(
        np.vdot(odd, odd),
        1.0,
        atol=1.0e-14,
    )

    assert np.isclose(
        np.vdot(even, odd),
        0.0,
        atol=1.0e-12,
    )


@pytest.mark.parametrize(
    "theta",
    (
        0.0,
        math.pi / 4.0,
        math.pi / 2.0,
        math.pi,
        1.75 * math.pi,
    ),
)
def test_logical_phase_state_is_normalized(theta):
    state = logical_phase_state(
        cutoff=16,
        alpha=1.5,
        theta_rad=theta,
    )

    assert np.isclose(
        np.vdot(state, state),
        1.0,
        atol=1.0e-14,
    )


def test_prepared_density_matrix_is_valid():
    model = build_default_n0_bosonic_model()

    rho = model.prepared_density_matrix(
        math.pi / 3.0
    )

    model.validate_density_matrix(
        rho
    )

    diagnostics = model.diagnostics(
        rho
    )

    assert (
        diagnostics["trace_error"]
        <= model.trace_tolerance
    )

    assert (
        diagnostics["hermiticity_error"]
        <= model.hermiticity_tolerance
    )

    assert (
        diagnostics["minimum_eigenvalue"]
        >= -model.positivity_tolerance
    )


def test_prepared_state_lies_in_declared_protected_manifold():
    model = build_default_n0_bosonic_model()

    rho = model.prepared_density_matrix(
        0.73
    )

    leakage = protected_manifold_leakage(
        rho=rho,
        cutoff=model.cutoff,
        alpha=model.alpha,
    )

    assert abs(leakage) <= 1.0e-12


def test_protected_projector_is_projector():
    p = protected_projector(
        cutoff=16,
        alpha=1.5,
    )

    assert np.allclose(
        p @ p,
        p,
        atol=1.0e-12,
    )

    assert np.allclose(
        p.conjugate().T,
        p,
        atol=1.0e-12,
    )

    assert math.isclose(
        float(
            np.real(
                np.trace(p)
            )
        ),
        2.0,
        abs_tol=1.0e-12,
    )


def test_logical_paulis_are_hermitian():
    x = logical_pauli_x(
        cutoff=16,
        alpha=1.5,
    )

    y = logical_pauli_y(
        cutoff=16,
        alpha=1.5,
    )

    assert np.allclose(
        x,
        x.conjugate().T,
        atol=1.0e-12,
    )

    assert np.allclose(
        y,
        y.conjugate().T,
        atol=1.0e-12,
    )


def test_probe_operator_matches_x_at_zero_phase():
    x = logical_pauli_x(
        cutoff=16,
        alpha=1.5,
    )

    probe = logical_probe_operator(
        cutoff=16,
        alpha=1.5,
        beta_rad=0.0,
    )

    assert np.allclose(
        probe,
        x,
        atol=1.0e-12,
    )


def test_probe_operator_matches_y_at_pi_over_two():
    y = logical_pauli_y(
        cutoff=16,
        alpha=1.5,
    )

    probe = logical_probe_operator(
        cutoff=16,
        alpha=1.5,
        beta_rad=math.pi / 2.0,
    )

    assert np.allclose(
        probe,
        y,
        atol=1.0e-12,
    )


def test_logical_phase_expectations_follow_cos_sin():
    theta = 0.37

    state = logical_phase_state(
        cutoff=16,
        alpha=1.5,
        theta_rad=theta,
    )

    rho = density_matrix(
        state
    )

    x = logical_pauli_x(
        cutoff=16,
        alpha=1.5,
    )

    y = logical_pauli_y(
        cutoff=16,
        alpha=1.5,
    )

    x_expectation = float(
        np.real(
            np.trace(
                x @ rho
            )
        )
    )

    y_expectation = float(
        np.real(
            np.trace(
                y @ rho
            )
        )
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


def test_dissipator_is_trace_preserving():
    model = build_default_n0_bosonic_model()

    rho = model.prepared_density_matrix(
        0.2
    )

    a = annihilation_operator(
        model.cutoff
    )

    derivative = dissipator(
        a,
        rho,
    )

    assert abs(
        np.trace(
            derivative
        )
    ) <= 1.0e-12


def test_default_generator_is_trace_preserving_on_prepared_state():
    model = build_default_n0_bosonic_model()

    rho = model.prepared_density_matrix(
        0.4
    )

    derivative = model.generator(
        rho
    )

    assert abs(
        np.trace(
            derivative
        )
    ) <= 1.0e-11


def test_model_rejects_negative_rates():
    model = build_default_n0_bosonic_model()

    with pytest.raises(
        ValueError,
        match="kappa values",
    ):
        type(model)(
            cutoff=model.cutoff,
            alpha=model.alpha,
            kappa_2=-1.0,
            kappa_1=0.0,
            kappa_phi=0.0,
            integration_dt=model.integration_dt,
            integration_duration=(
                model.integration_duration
            ),
        )


def test_preparation_truth_is_not_embedded_in_density_matrix_type():
    model = build_default_n0_bosonic_model()

    rho = model.prepared_density_matrix(
        0.42
    )

    assert isinstance(
        rho,
        np.ndarray,
    )

    assert not hasattr(
        rho,
        "theta_truth",
    )
