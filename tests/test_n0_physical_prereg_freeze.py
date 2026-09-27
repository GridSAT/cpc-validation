from dataclasses import replace

import pytest

from src.n0_physical_prereg_freeze import (
    N0_CONFIDENCE_METHOD_ID,
    N0_NEGATIVE_CONTROL_REQUIREMENTS,
    N0_PHYSICAL_PREREG_FREEZE_ID,
    N0_REQUIRED_RAW_PAYLOAD_PROVENANCE,
    N0PhysicalBindings,
    N0PhysicalPreregistrationFreeze,
    SIMULATION_ONLY_PROFILE_ID,
    build_unresolved_n0_physical_preregistration_freeze,
)
from src.n0_statistics import (
    N0_PHASE_VALIDATION_MULTIPLICITY_RULE,
    N0Preregistration,
    PreregisteredParameter,
)


SHA_A = "sha256:" + "a" * 64
SHA_B = "sha256:" + "b" * 64


def resolved_parameter(
    name,
    value,
    units,
):
    return PreregisteredParameter(
        name=name,
        status="RESOLVED",
        value=value,
        units=units,
    )


def resolved_statistics():
    return N0Preregistration(
        preregistration_id=(
            "CPC-SHOR-N0-PHYSICAL-PREREGISTRATION-v1"
        ),
        alpha=resolved_parameter(
            "alpha",
            0.05,
            "probability",
        ),
        equivalence_margin_rad=resolved_parameter(
            "equivalence_margin_rad",
            0.30,
            "rad",
        ),
        power_target=resolved_parameter(
            "power_target",
            0.80,
            "probability",
        ),
        minimum_valid_samples=resolved_parameter(
            "minimum_valid_samples",
            100,
            "count",
        ),
        maximum_invalid_fraction=resolved_parameter(
            "maximum_invalid_fraction",
            0.10,
            "fraction",
        ),
        calibration_gate_id=(
            "N0-PHYSICAL-CALIBRATION-GATE-v1"
        ),
        operational_gate_id=(
            "N0-PHYSICAL-OPERATIONAL-GATE-v1"
        ),
        multiplicity_rule=(
            N0_PHASE_VALIDATION_MULTIPLICITY_RULE
        ),
    )


def resolved_bindings():
    return N0PhysicalBindings(
        physical_profile_id=(
            "CPC-SHOR-N0-NATIVE-MEASUREMENT-PROFILE-v1"
        ),
        apparatus_id=(
            "LAB-N0-APPARATUS-v1"
        ),
        calibration_id=(
            "LAB-N0-CALIBRATION-v1"
        ),
        probe_realization_id=(
            "LAB-N0-CPC-PROBE-v1"
        ),
        reference_id=(
            "LAB-N0-REFERENCE-v1"
        ),
        timebase_id=(
            "LAB-N0-TIMEBASE-v1"
        ),
        raw_transport_encoding_id=(
            "LAB-N0-IQ-RAW-ENCODING-v1"
        ),
        controller_constraint_id=(
            "LAB-N0-CONTROLLER-CONSTRAINTS-v1"
        ),
        controller_place_route_id=(
            "LAB-N0-CONTROLLER-PNR-v1"
        ),
        controller_clock_binding_id=(
            "LAB-N0-CLOCK-BINDING-v1"
        ),
        controller_pin_binding_id=(
            "LAB-N0-PIN-BINDING-v1"
        ),
        controller_adc_dac_binding_id=(
            "LAB-N0-ADC-DAC-BINDING-v1"
        ),
        negative_control_protocol_id=(
            "LAB-N0-NEGATIVE-CONTROL-v1"
        ),
        source_manifest_sha256=SHA_A,
        physical_evidence_manifest_sha256=SHA_B,
    )


def test_unresolved_freeze_fails_closed():
    freeze = (
        build_unresolved_n0_physical_preregistration_freeze()
    )

    assert (
        freeze.freeze_id
        == N0_PHYSICAL_PREREG_FREEZE_ID
    )

    assert (
        freeze.status
        == "DRAFT_UNRESOLVED"
    )

    assert (
        freeze.material_complete
        is False
    )

    assert (
        freeze.execution_authorized
        is False
    )

    assert (
        freeze.unresolved_fields
    )


def test_statistical_method_is_frozen_while_numbers_are_unresolved():
    freeze = (
        build_unresolved_n0_physical_preregistration_freeze()
    )

    assert (
        freeze.statistics.multiplicity_rule
        == N0_PHASE_VALIDATION_MULTIPLICITY_RULE
    )

    assert (
        freeze.methodology[
            "confidence_method_id"
        ]
        == N0_CONFIDENCE_METHOD_ID
    )

    assert (
        freeze.statistics.unresolved_parameters
    )


def test_native_instrument_byte_provenance_is_mandatory():
    bindings = resolved_bindings()

    assert (
        bindings.raw_payload_provenance
        == N0_REQUIRED_RAW_PAYLOAD_PROVENANCE
    )

    with pytest.raises(
        ValueError,
        match="native instrument-byte",
    ):
        replace(
            bindings,
            raw_payload_provenance=(
                "synthetic-canonical-sample-payload"
            ),
        )


def test_simulation_only_profile_cannot_be_bound_as_physical():
    with pytest.raises(
        ValueError,
        match="simulation-only",
    ):
        replace(
            resolved_bindings(),
            physical_profile_id=(
                SIMULATION_ONLY_PROFILE_ID
            ),
        )


def test_simulated_identity_cannot_enter_resolved_physical_binding():
    with pytest.raises(
        ValueError,
        match="simulated identity",
    ):
        replace(
            resolved_bindings(),
            apparatus_id=(
                "SIMULATED-CAT-DEVICE-v1"
            ),
        )


def test_material_completion_does_not_imply_execution_go():
    freeze = N0PhysicalPreregistrationFreeze(
        bindings=resolved_bindings(),
        statistics=resolved_statistics(),
    )

    freeze.require_material_complete()

    assert (
        freeze.status
        == "MATERIAL_COMPLETE_AWAITING_HUMAN_GO"
    )

    assert (
        freeze.material_complete
        is True
    )

    assert (
        freeze.human_go_present
        is False
    )

    assert (
        freeze.execution_authorized
        is False
    )


def test_execution_requires_separate_explicit_human_go():
    freeze = N0PhysicalPreregistrationFreeze(
        bindings=resolved_bindings(),
        statistics=resolved_statistics(),
    )

    with pytest.raises(
        RuntimeError,
        match="explicit human GO",
    ):
        freeze.require_execution_authorized()


def test_explicit_human_go_can_open_execution_gate_only_after_completion():
    freeze = N0PhysicalPreregistrationFreeze(
        bindings=resolved_bindings(),
        statistics=resolved_statistics(),
        human_go_id=(
            "HUMAN-GO:CPC-SHOR-N0-TEST-v1"
        ),
    )

    freeze.require_execution_authorized()

    assert (
        freeze.status
        == "EXECUTION_AUTHORIZED"
    )

    assert (
        freeze.execution_authorized
        is True
    )


def test_human_go_does_not_authorize_fpga_programming_or_physical_pass():
    freeze = N0PhysicalPreregistrationFreeze(
        bindings=resolved_bindings(),
        statistics=resolved_statistics(),
        human_go_id=(
            "HUMAN-GO:CPC-SHOR-N0-TEST-v1"
        ),
    )

    assert (
        freeze.fpga_programming_authorized
        is False
    )

    assert (
        freeze.physical_pass_authorized
        is False
    )


def test_unresolved_material_cannot_be_bypassed_by_human_go():
    base = (
        build_unresolved_n0_physical_preregistration_freeze()
    )

    freeze = replace(
        base,
        human_go_id=(
            "HUMAN-GO:CPC-SHOR-N0-TEST-v1"
        ),
    )

    assert (
        freeze.execution_authorized
        is False
    )

    assert (
        freeze.status
        == "DRAFT_UNRESOLVED"
    )

    with pytest.raises(
        RuntimeError,
        match="preregistration incomplete",
    ):
        freeze.require_execution_authorized()


def test_negative_controls_are_frozen_requirements():
    freeze = (
        build_unresolved_n0_physical_preregistration_freeze()
    )

    requirements = set(
        freeze.methodology[
            "negative_control_requirements"
        ]
    )

    assert set(
        N0_NEGATIVE_CONTROL_REQUIREMENTS
    ) == requirements

    assert (
        "negative-control-failure-blocks-physical-pass"
        in requirements
    )


def test_freeze_is_canonically_deterministic():
    first = (
        build_unresolved_n0_physical_preregistration_freeze()
    )

    second = (
        build_unresolved_n0_physical_preregistration_freeze()
    )

    assert (
        first.canonical_json
        == second.canonical_json
    )

    assert (
        first.freeze_hash
        == second.freeze_hash
    )


def test_invalid_source_manifest_is_rejected():
    with pytest.raises(
        ValueError,
        match="source_manifest_sha256",
    ):
        replace(
            resolved_bindings(),
            source_manifest_sha256="not-a-hash",
        )


def test_random_string_is_not_human_go():
    freeze = N0PhysicalPreregistrationFreeze(
        bindings=resolved_bindings(),
        statistics=resolved_statistics(),
        human_go_id="approval",
    )

    assert (
        freeze.human_go_present
        is False
    )

    assert (
        freeze.execution_authorized
        is False
    )


def test_freeze_methodology_preserves_truth_blind_boundary():
    freeze = (
        build_unresolved_n0_physical_preregistration_freeze()
    )

    assert (
        freeze.methodology[
            "truth_blind_reduction_required"
        ]
        is True
    )

    assert (
        freeze.methodology[
            "heldout_validation_required"
        ]
        is True
    )

    assert (
        freeze.methodology[
            "calibration_validation_id_disjointness_required"
        ]
        is True
    )
