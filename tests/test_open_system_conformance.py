import pytest

from src.open_system_conformance import (
    RFC0010ConformanceEvidence,
    RequirementEvidence,
    validate_rfc0010_conformance,
)
from src.open_system_execution import (
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
        reference_type="microwave-reference",
        calibration_id="calibration-1",
        instrumentation_id="instrument-1",
        calibration_parameters=(
            ("uncertainty", 0.01),
        ),
    )


def make_convergence():
    return ConvergenceSpecification(
        method="penalty-lyapunov",
        penalty_id="penalty-1",
        admitted_state_domain_id="domain-1",
        gamma=0.25,
        positive_penalty_scale=1.0,
    )


def make_readout(
    *,
    error_bound=0.1,
    decision_margin=0.2,
):
    return ReferencedReadoutSpecification(
        measurement_model_id="measurement-1",
        decoder_id="decoder-1",
        reference_id="reference-1",
        decision_regions=(
            ("accept", "signal>=0.5"),
            ("reject", "signal<0.5"),
        ),
        calibration_neighborhood=(
            ("maximum_error", 0.1),
        ),
        declared_error_bound=error_bound,
        decision_margin=decision_margin,
    )


def make_specification(
    *,
    groups=("DC", "OS", "OV", "RR"),
    convergence=None,
    reference=None,
    readout=None,
    resource_accounting=(
        ("runtime_bound", "polynomial"),
    ),
):
    if convergence is None:
        convergence = make_convergence()

    if reference is None:
        reference = make_reference()

    if readout is None:
        readout = make_readout()

    return OpenSystemExecutionSpecification(
        instance_id="instance-1",
        prepared_execution_hash=SHA_A,
        physical_state_space_id="state-space-1",
        protected_manifold_id="protected-1",
        stabilization_generator_hash=SHA_B,
        problem_generator_hash=SHA_C,
        semantic_terminal_sector_id="terminal-1",
        realization_status="simulated",
        conformance_groups=groups,
        external_reference=reference,
        convergence=convergence,
        readout=readout,
        resource_accounting=resource_accounting,
    )


def passing_evidence_for(specification):
    requirements = []

    prefixes = {
        group
        for group in specification.conformance_groups
    }

    for group in sorted(prefixes):
        for number in range(1, 9):
            requirement_id = f"{group}-{number}"

            if group == "DC" and number > 6:
                continue

            if group == "OV" and number > 4:
                continue

            requirements.append(
                RequirementEvidence(
                    requirement_id=requirement_id,
                    evidence_id=(
                        f"evidence-{requirement_id}"
                    ),
                    method="test-certificate",
                    passed=True,
                )
            )

    return RFC0010ConformanceEvidence(
        execution_specification_hash=(
            specification.specification_hash
        ),
        requirements=tuple(
            sorted(
                requirements,
                key=lambda item: item.requirement_id,
            )
        ),
    )


def test_complete_declared_evidence_conforms():
    specification = make_specification()
    evidence = passing_evidence_for(
        specification
    )

    report = validate_rfc0010_conformance(
        specification=specification,
        evidence=evidence,
    )

    assert report.conformant is True
    assert report.failures == ()


def test_missing_required_evidence_fails_closed():
    specification = make_specification(
        groups=("OS",),
    )

    evidence = RFC0010ConformanceEvidence(
        execution_specification_hash=(
            specification.specification_hash
        ),
        requirements=(),
    )

    report = validate_rfc0010_conformance(
        specification=specification,
        evidence=evidence,
    )

    assert report.conformant is False

    failed = {
        failure.requirement_id
        for failure in report.failures
    }

    assert failed == {
        "OS-1",
        "OS-2",
        "OS-3",
        "OS-4",
        "OS-5",
        "OS-6",
        "OS-7",
        "OS-8",
    }


def test_failed_evidence_fails_conformance():
    specification = make_specification(
        groups=("OS",),
    )

    items = []

    for number in range(1, 9):
        requirement_id = f"OS-{number}"

        items.append(
            RequirementEvidence(
                requirement_id=requirement_id,
                evidence_id=f"e-{number}",
                method="test",
                passed=number != 6,
            )
        )

    evidence = RFC0010ConformanceEvidence(
        execution_specification_hash=(
            specification.specification_hash
        ),
        requirements=tuple(items),
    )

    report = validate_rfc0010_conformance(
        specification=specification,
        evidence=evidence,
    )

    assert report.conformant is False
    assert any(
        failure.requirement_id == "OS-6"
        for failure in report.failures
    )


def test_evidence_must_bind_exact_specification():
    specification = make_specification()

    evidence = passing_evidence_for(
        specification
    )

    other = make_specification(
        groups=("OS",),
    )

    report = validate_rfc0010_conformance(
        specification=other,
        evidence=evidence,
    )

    assert report.conformant is False
    assert any(
        failure.requirement_id == "OV-3"
        for failure in report.failures
    )


def test_rr_group_requires_external_reference():
    specification = make_specification(
        groups=("RR",),
        reference=None,
    )

    object.__setattr__(
        specification,
        "external_reference",
        None,
    )

    evidence = passing_evidence_for(
        specification
    )

    report = validate_rfc0010_conformance(
        specification=specification,
        evidence=evidence,
    )

    assert report.conformant is False
    assert any(
        failure.requirement_id == "RR-1"
        for failure in report.failures
    )


def test_rr_group_requires_decision_regions():
    specification = make_specification(
        groups=("RR",),
        readout=ReferencedReadoutSpecification(
            measurement_model_id="measurement-1",
            decoder_id="decoder-1",
            reference_id="reference-1",
            calibration_neighborhood=(
                ("maximum_error", 0.1),
            ),
            declared_error_bound=0.1,
            decision_margin=0.2,
        ),
    )

    evidence = passing_evidence_for(
        specification
    )

    report = validate_rfc0010_conformance(
        specification=specification,
        evidence=evidence,
    )

    assert report.conformant is False
    assert any(
        failure.requirement_id == "RR-5"
        for failure in report.failures
    )


def test_error_budget_must_be_below_margin():
    specification = make_specification(
        groups=("RR",),
        readout=make_readout(
            error_bound=0.2,
            decision_margin=0.2,
        ),
    )

    evidence = passing_evidence_for(
        specification
    )

    report = validate_rfc0010_conformance(
        specification=specification,
        evidence=evidence,
    )

    assert report.conformant is False

    assert any(
        failure.requirement_id == "RR-7"
        and "strictly smaller" in failure.reason
        for failure in report.failures
    )


def test_dc_group_requires_positive_penalty_scale():
    specification = make_specification(
        groups=("DC",),
        convergence=ConvergenceSpecification(
            method="penalty-lyapunov",
            penalty_id="penalty-1",
            admitted_state_domain_id="domain-1",
            gamma=0.25,
        ),
    )

    evidence = passing_evidence_for(
        specification
    )

    report = validate_rfc0010_conformance(
        specification=specification,
        evidence=evidence,
    )

    assert report.conformant is False
    assert any(
        failure.requirement_id == "DC-2"
        for failure in report.failures
    )


def test_dc_group_requires_resource_accounting():
    specification = make_specification(
        groups=("DC",),
        resource_accounting=(),
    )

    evidence = passing_evidence_for(
        specification
    )

    report = validate_rfc0010_conformance(
        specification=specification,
        evidence=evidence,
    )

    assert report.conformant is False
    assert any(
        failure.requirement_id == "DC-6"
        for failure in report.failures
    )


def test_requirement_evidence_rejects_unknown_requirement():
    with pytest.raises(
        ValueError,
        match="unknown RFC-0010 requirement_id",
    ):
        RequirementEvidence(
            requirement_id="XX-1",
            evidence_id="evidence-1",
            method="test",
            passed=True,
        )


def test_requirement_evidence_requires_boolean_result():
    with pytest.raises(
        ValueError,
        match="passed must be a boolean",
    ):
        RequirementEvidence(
            requirement_id="OS-1",
            evidence_id="evidence-1",
            method="test",
            passed=1,
        )


def test_conformance_evidence_requires_unique_requirements():
    requirement = RequirementEvidence(
        requirement_id="OS-1",
        evidence_id="evidence-1",
        method="test",
        passed=True,
    )

    with pytest.raises(
        ValueError,
        match="unique",
    ):
        RFC0010ConformanceEvidence(
            execution_specification_hash=SHA_A,
            requirements=(
                requirement,
                requirement,
            ),
        )


def test_conformance_evidence_requires_sorted_requirements():
    first = RequirementEvidence(
        requirement_id="OS-2",
        evidence_id="evidence-2",
        method="test",
        passed=True,
    )

    second = RequirementEvidence(
        requirement_id="OS-1",
        evidence_id="evidence-1",
        method="test",
        passed=True,
    )

    with pytest.raises(
        ValueError,
        match="sorted",
    ):
        RFC0010ConformanceEvidence(
            execution_specification_hash=SHA_A,
            requirements=(
                first,
                second,
            ),
        )
