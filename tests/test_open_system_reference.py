import inspect
import math

import pytest

from src.open_system_conformance import (
    validate_rfc0010_conformance,
)
from src.open_system_reference import (
    admitted_observation,
    build_reference_execution_specification,
    build_reference_witness,
    decode_observation,
    evolved_excited_population,
    penalty_energy,
    penalty_lyapunov_derivative,
    run_reference_witness,
    semantic_answer_from_beta,
    terminal_support_error,
    verify_reference_witness,
)


@pytest.mark.parametrize("beta", (0, 1))
def test_build_reference_witness(beta):
    witness = build_reference_witness(beta, kappa=2.0)

    assert witness.beta == beta
    assert witness.terminal_index == beta
    assert witness.excited_index == 1 - beta
    assert witness.kappa == 2.0


def test_generator_identities_are_distinct():
    witness = build_reference_witness(0)

    assert (
        witness.stabilization_generator_hash
        != witness.problem_generator_hash
    )


def test_problem_generator_changes_with_beta():
    first = build_reference_witness(0)
    second = build_reference_witness(1)

    assert (
        first.problem_generator_hash
        != second.problem_generator_hash
    )
    assert (
        first.stabilization_generator_hash
        == second.stabilization_generator_hash
    )


def test_generator_builder_accepts_no_semantic_answer_argument():
    signature = inspect.signature(build_reference_witness)

    forbidden = {
        "expected_answer",
        "semantic_answer",
        "expected_output",
        "satisfying_assignment",
    }

    assert forbidden.isdisjoint(signature.parameters)


@pytest.mark.parametrize("beta", (0, 1))
def test_exact_witness_verification(beta):
    witness = build_reference_witness(beta, kappa=1.5)
    verification = verify_reference_witness(witness)

    assert verification.protected_manifold_compatible
    assert verification.terminal_silence
    assert verification.dark_vector_complete
    assert verification.fixed_density_state_complete
    assert verification.penalty_lyapunov_exact
    assert verification.positive_penalty_scale == 1.0
    assert verification.convergence_rate == 1.5


@pytest.mark.parametrize(
    "population",
    (0.0, 0.125, 0.5, 1.0),
)
def test_penalty_lyapunov_relation(population):
    witness = build_reference_witness(0, kappa=2.0)

    energy = penalty_energy(witness, population)
    derivative = penalty_lyapunov_derivative(
        witness,
        population,
    )

    assert math.isclose(
        derivative,
        -2.0 * energy,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )


def test_exact_exponential_decay():
    witness = build_reference_witness(0, kappa=2.0)

    value = evolved_excited_population(
        witness,
        initial_excited_population=0.75,
        time=1.25,
    )

    expected = 0.75 * math.exp(-2.0 * 1.25)

    assert math.isclose(
        value,
        expected,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )


def test_terminal_support_bound_matches_exact_population():
    witness = build_reference_witness(1, kappa=0.75)

    error = terminal_support_error(
        witness,
        initial_excited_population=0.6,
        time=2.0,
    )

    bound = 0.6 * math.exp(-0.75 * 2.0)

    assert math.isclose(
        error,
        bound,
        rel_tol=0.0,
        abs_tol=1.0e-15,
    )


@pytest.mark.parametrize("beta", (0, 1))
def test_execution_specification_is_simulated(beta):
    witness = build_reference_witness(beta)

    specification = (
        build_reference_execution_specification(witness)
    )

    assert specification.realization_status == "simulated"
    assert specification.realization_status not in (
        "physical_exact",
        "physical_approximate",
    )


def test_reference_and_decoder_are_declared():
    witness = build_reference_witness(0)

    specification = (
        build_reference_execution_specification(witness)
    )

    assert specification.external_reference is not None
    assert specification.readout is not None

    assert (
        specification.readout.reference_id
        == specification.external_reference.reference_id
    )
    assert specification.readout.decoder_id == witness.decoder_id
    assert specification.readout.calibration_neighborhood
    assert (
        specification.readout.declared_error_bound
        < specification.readout.decision_margin
    )


@pytest.mark.parametrize(
    ("beta", "expected_observation"),
    (
        (0, 0.0),
        (1, 1.0),
    ),
)
def test_admitted_observation(beta, expected_observation):
    witness = build_reference_witness(beta)

    assert (
        admitted_observation(witness)
        == expected_observation
    )


@pytest.mark.parametrize(
    ("observation", "expected"),
    (
        (0.0, 0),
        (0.49, 0),
        (0.5, 1),
        (1.0, 1),
    ),
)
def test_decoder_uses_only_admitted_scalar(
    observation,
    expected,
):
    assert decode_observation(observation) == expected


@pytest.mark.parametrize("beta", (0, 1))
def test_nominal_decoding_matches_independent_semantics(beta):
    run = run_reference_witness(beta)

    assert (
        run.decoded_answer
        == semantic_answer_from_beta(beta)
    )
    assert (
        run.semantic_answer
        == semantic_answer_from_beta(beta)
    )


@pytest.mark.parametrize("beta", (0, 1))
def test_conformance_validator_passes(beta):
    run = run_reference_witness(beta)

    report = validate_rfc0010_conformance(
        specification=run.specification,
        evidence=run.evidence,
    )

    assert report.conformant is True
    assert report.failures == ()


def test_conformance_evidence_binds_exact_specification():
    first = run_reference_witness(0)
    second = run_reference_witness(1)

    report = validate_rfc0010_conformance(
        specification=second.specification,
        evidence=first.evidence,
    )

    assert report.conformant is False


def test_invalid_beta_rejected():
    with pytest.raises(
        ValueError,
        match="beta must be 0 or 1",
    ):
        build_reference_witness(2)


@pytest.mark.parametrize(
    "kappa",
    (
        0.0,
        -1.0,
        float("inf"),
        float("nan"),
        True,
    ),
)
def test_invalid_kappa_rejected(kappa):
    with pytest.raises(
        ValueError,
        match="kappa",
    ):
        build_reference_witness(0, kappa=kappa)


@pytest.mark.parametrize("beta", (0, 1))
def test_exact_kernel_properties_hold_for_both_terminal_labels(beta):
    witness = build_reference_witness(beta, kappa=2.0)
    verification = verify_reference_witness(witness)

    assert witness.terminal_index == beta
    assert witness.excited_index == 1 - beta
    assert verification.terminal_silence is True
    assert verification.dark_vector_complete is True
    assert verification.fixed_density_state_complete is True


@pytest.mark.parametrize(
    ("beta", "kappa"),
    (
        (0, 0.125),
        (0, 1.0),
        (0, 8.0),
        (1, 0.125),
        (1, 1.0),
        (1, 8.0),
    ),
)
def test_exact_generator_verification_is_rate_independent(beta, kappa):
    witness = build_reference_witness(beta, kappa=kappa)
    verification = verify_reference_witness(witness)

    assert verification.dark_vector_complete is True
    assert verification.fixed_density_state_complete is True
    assert verification.penalty_lyapunov_exact is True
    assert verification.convergence_rate == kappa
