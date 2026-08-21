import json

import pytest

from src.open_system_execution import (
    OPEN_SYSTEM_EXECUTION_SCHEMA,
    ConvergenceSpecification,
    ExternalReferenceSpecification,
    OpenSystemExecutionSpecification,
    ReferencedReadoutSpecification,
)


SHA_A = "sha256:" + "a" * 64
SHA_B = "sha256:" + "b" * 64
SHA_C = "sha256:" + "c" * 64


def make_reference():
    return ExternalReferenceSpecification(
        reference_id="reference-1",
        reference_type="microwave-local-oscillator",
        calibration_id="calibration-1",
        instrumentation_id="instrument-1",
        nominal_parameters=(
            ("frequency_hz", 5.0e9),
            ("phase_rad", 0.0),
        ),
        calibration_parameters=(
            ("frequency_tolerance_hz", 1000.0),
        ),
        drift_region=(
            ("maximum_frequency_drift_hz", 500.0),
        ),
        provenance=(
            ("source", "test-fixture"),
        ),
    )


def make_convergence():
    return ConvergenceSpecification(
        method="penalty-lyapunov",
        penalty_id="penalty-1",
        admitted_state_domain_id="domain-1",
        gamma=0.25,
        positive_penalty_scale=1.0,
        tolerances=(
            ("trace_tolerance", 1.0e-9),
        ),
        metadata=(
            ("interpretation", "lyapunov-rate"),
        ),
    )


def make_readout(reference_id="reference-1"):
    return ReferencedReadoutSpecification(
        measurement_model_id="measurement-1",
        decoder_id="decoder-1",
        reference_id=reference_id,
        decision_regions=(
            ("accept", "signal>=0.5"),
            ("reject", "signal<0.5"),
        ),
        calibration_neighborhood=(
            ("maximum_error", 0.1),
        ),
        declared_error_bound=0.1,
        decision_margin=0.2,
        metadata=(
            ("decoder_fixed", True),
        ),
    )


def make_execution(**overrides):
    values = {
        "instance_id": "instance-1",
        "prepared_execution_hash": SHA_A,
        "physical_state_space_id": "state-space-1",
        "protected_manifold_id": "protected-1",
        "stabilization_generator_hash": SHA_B,
        "problem_generator_hash": SHA_C,
        "semantic_terminal_sector_id": "terminal-1",
        "realization_status": "simulated",
        "boundary_control": (
            ("beta", "boundary-1"),
        ),
        "conformance_groups": (
            "DC",
            "OS",
            "RR",
        ),
        "external_reference": make_reference(),
        "convergence": make_convergence(),
        "readout": make_readout(),
        "resource_accounting": (
            ("runtime_bound", "polynomial"),
        ),
        "metadata": (
            ("fixture", "unit-test"),
        ),
    }
    values.update(overrides)
    return OpenSystemExecutionSpecification(**values)


def test_external_reference_serializes_declared_fields():
    reference = make_reference()

    data = reference.to_dict()

    assert data["reference_id"] == "reference-1"
    assert data["reference_type"] == "microwave-local-oscillator"
    assert data["calibration_id"] == "calibration-1"
    assert data["instrumentation_id"] == "instrument-1"
    assert data["nominal_parameters"]["frequency_hz"] == 5.0e9


@pytest.mark.parametrize(
    "field",
    (
        "reference_id",
        "reference_type",
        "calibration_id",
        "instrumentation_id",
    ),
)
def test_external_reference_rejects_empty_identity_fields(field):
    values = {
        "reference_id": "reference-1",
        "reference_type": "microwave-local-oscillator",
        "calibration_id": "calibration-1",
        "instrumentation_id": "instrument-1",
    }
    values[field] = ""

    with pytest.raises(ValueError):
        ExternalReferenceSpecification(**values)


def test_pair_metadata_must_be_sorted():
    with pytest.raises(ValueError, match="sorted"):
        ExternalReferenceSpecification(
            reference_id="reference-1",
            reference_type="type-1",
            calibration_id="calibration-1",
            instrumentation_id="instrument-1",
            nominal_parameters=(
                ("z", 1),
                ("a", 2),
            ),
        )


def test_pair_metadata_keys_must_be_unique():
    with pytest.raises(ValueError, match="unique"):
        ExternalReferenceSpecification(
            reference_id="reference-1",
            reference_type="type-1",
            calibration_id="calibration-1",
            instrumentation_id="instrument-1",
            nominal_parameters=(
                ("a", 1),
                ("a", 2),
            ),
        )


@pytest.mark.parametrize(
    "gamma",
    (
        0.0,
        -1.0,
        float("inf"),
        float("-inf"),
        float("nan"),
        True,
    ),
)
def test_convergence_requires_finite_positive_gamma(gamma):
    with pytest.raises(ValueError, match="gamma"):
        ConvergenceSpecification(
            method="penalty-lyapunov",
            penalty_id="penalty-1",
            admitted_state_domain_id="domain-1",
            gamma=gamma,
        )


@pytest.mark.parametrize(
    "scale",
    (
        0.0,
        -1.0,
        float("inf"),
        float("nan"),
        True,
    ),
)
def test_positive_penalty_scale_must_be_finite_and_positive(scale):
    with pytest.raises(ValueError, match="positive_penalty_scale"):
        ConvergenceSpecification(
            method="penalty-lyapunov",
            penalty_id="penalty-1",
            admitted_state_domain_id="domain-1",
            gamma=0.5,
            positive_penalty_scale=scale,
        )


@pytest.mark.parametrize(
    "error_bound",
    (
        -1.0,
        float("inf"),
        float("nan"),
        True,
    ),
)
def test_readout_error_bound_must_be_finite_and_nonnegative(
    error_bound,
):
    with pytest.raises(ValueError, match="declared_error_bound"):
        ReferencedReadoutSpecification(
            measurement_model_id="measurement-1",
            decoder_id="decoder-1",
            declared_error_bound=error_bound,
        )


@pytest.mark.parametrize(
    "margin",
    (
        0.0,
        -1.0,
        float("inf"),
        float("nan"),
        True,
    ),
)
def test_readout_margin_must_be_finite_and_positive(margin):
    with pytest.raises(ValueError, match="decision_margin"):
        ReferencedReadoutSpecification(
            measurement_model_id="measurement-1",
            decoder_id="decoder-1",
            decision_margin=margin,
        )


@pytest.mark.parametrize(
    "field",
    (
        "prepared_execution_hash",
        "stabilization_generator_hash",
        "problem_generator_hash",
    ),
)
@pytest.mark.parametrize(
    "bad_hash",
    (
        "",
        "abc",
        "sha256:abc",
        "sha256:" + "A" * 64,
        "sha256:" + "g" * 64,
    ),
)
def test_execution_rejects_malformed_sha256_fields(
    field,
    bad_hash,
):
    with pytest.raises(ValueError):
        make_execution(**{field: bad_hash})


@pytest.mark.parametrize(
    "status",
    (
        "abstract",
        "simulated",
        "physical_approximate",
        "physical_exact",
    ),
)
def test_execution_accepts_declared_realization_statuses(status):
    execution = make_execution(
        realization_status=status,
    )

    assert execution.realization_status == status


def test_execution_rejects_unknown_realization_status():
    with pytest.raises(ValueError, match="realization_status"):
        make_execution(
            realization_status="magic",
        )


def test_conformance_groups_must_be_known():
    with pytest.raises(ValueError, match="unknown"):
        make_execution(
            conformance_groups=("OS", "ZZ"),
        )


def test_conformance_groups_must_be_unique():
    with pytest.raises(ValueError, match="unique"):
        make_execution(
            conformance_groups=("OS", "OS"),
        )


def test_conformance_groups_must_be_sorted():
    with pytest.raises(ValueError, match="sorted"):
        make_execution(
            conformance_groups=("RR", "OS"),
        )


def test_readout_reference_must_match_external_reference():
    with pytest.raises(ValueError, match="reference_id"):
        make_execution(
            readout=make_readout(
                reference_id="different-reference",
            ),
        )


def test_readout_may_omit_reference_identity():
    execution = make_execution(
        readout=make_readout(
            reference_id=None,
        ),
    )

    assert execution.readout is not None
    assert execution.readout.reference_id is None


def test_execution_schema_is_explicit():
    execution = make_execution()

    assert execution.schema == OPEN_SYSTEM_EXECUTION_SCHEMA
    assert (
        execution.to_dict()["schema"]
        == OPEN_SYSTEM_EXECUTION_SCHEMA
    )


def test_canonical_json_is_deterministic_and_parseable():
    first = make_execution()
    second = make_execution()

    assert first.canonical_json() == second.canonical_json()
    assert first.canonical_json().endswith("\n")

    decoded = json.loads(first.canonical_json())

    assert decoded == first.to_dict()


def test_specification_hash_is_deterministic():
    first = make_execution()
    second = make_execution()

    assert first.specification_hash == second.specification_hash
    assert first.specification_hash.startswith("sha256:")
    assert len(first.specification_hash) == len("sha256:") + 64


def test_specification_hash_changes_with_semantic_identity():
    first = make_execution()
    second = make_execution(
        semantic_terminal_sector_id="terminal-2",
    )

    assert first.specification_hash != second.specification_hash


def test_complete_execution_serialization_contains_nested_models():
    execution = make_execution()

    data = execution.to_dict()

    assert data["external_reference"]["reference_id"] == "reference-1"
    assert data["convergence"]["gamma"] == 0.25
    assert data["readout"]["decoder_id"] == "decoder-1"
    assert data["boundary_control"] == {
        "beta": "boundary-1",
    }
    assert data["resource_accounting"] == {
        "runtime_bound": "polynomial",
    }
