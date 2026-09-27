from dataclasses import replace

import pytest

from src.n0_physical_prereg_freeze import (
    build_unresolved_n0_physical_preregistration_freeze,
)
from src.n0_readiness import (
    N0ReadinessAssessment,
    SOFTWARE_COMPONENTS,
    apply_physical_preregistration_freeze,
    build_current_pre_controller_assessment,
    build_current_repository_assessment,
    build_post_logical_controller_assessment,
    complete_software_components,
)


def base():
    return build_post_logical_controller_assessment()


def material_complete_without_go():
    return replace(
        base(),
        physical_profile_defined=True,
        physical_apparatus_identity_present=True,
        physical_calibration_values_present=True,
        physical_cpc_probe_realized=True,
        raw_transport_encoding_defined=True,
        physical_timebase_present=True,
        controller_clock_binding_complete=True,
        controller_pin_binding_complete=True,
        controller_adc_dac_binding_complete=True,
        controller_physical_constraints_complete=True,
        controller_place_route_complete=True,
        controller_bitstream_complete=True,
        source_manifest_present=True,
        physical_evidence_manifest_present=True,
        physical_preregistration_material_complete=True,
    )


def test_current_repository_waits_for_real_physical_profile():
    assessment = (
        build_current_repository_assessment()
    )

    assert (
        assessment.software_profile_complete
        is True
    )

    assert (
        assessment.controller_logical_stack_complete
        is True
    )

    assert (
        assessment.status
        == "PHYSICAL_PROFILE_PENDING"
    )


def test_precontroller_state_is_still_representable():
    assessment = (
        build_current_pre_controller_assessment()
    )

    assert (
        assessment.status
        == "CONTROLLER_LOGICAL_PROTOCOL_PENDING"
    )


def test_post_logical_state_has_no_physical_claim():
    assessment = (
        build_post_logical_controller_assessment()
    )

    assert (
        assessment.execution_authorized
        is False
    )

    assert (
        assessment.acquisition_ready
        is False
    )


def test_raw_records_are_not_preexecution_material_requirement():
    assessment = (
        build_current_repository_assessment()
    )

    assert (
        "PHYSICAL_RAW_RECORDS"
        not in
        assessment.unresolved_material_requirements
    )


def test_unresolved_freeze_does_not_advance_current_state():
    freeze = (
        build_unresolved_n0_physical_preregistration_freeze()
    )

    assessment = (
        apply_physical_preregistration_freeze(
            assessment=(
                build_current_repository_assessment()
            ),
            freeze=freeze,
        )
    )

    assert (
        assessment.status
        == "PHYSICAL_PROFILE_PENDING"
    )

    assert (
        assessment.physical_preregistration_material_complete
        is False
    )

    assert (
        assessment.human_go_present
        is False
    )


def test_place_route_cannot_precede_constraints():
    with pytest.raises(
        ValueError,
        match="cannot precede physical constraints",
    ):
        replace(
            base(),
            controller_place_route_complete=True,
        )


def test_bitstream_cannot_precede_place_route():
    assessment = replace(
        base(),
        controller_clock_binding_complete=True,
        controller_pin_binding_complete=True,
        controller_physical_constraints_complete=True,
    )

    with pytest.raises(
        ValueError,
        match="cannot precede place-and-route",
    ):
        replace(
            assessment,
            controller_bitstream_complete=True,
        )


def test_constraints_require_clock_binding():
    with pytest.raises(
        ValueError,
        match="clock binding",
    ):
        replace(
            base(),
            controller_pin_binding_complete=True,
            controller_physical_constraints_complete=True,
        )


def test_constraints_require_pin_binding():
    with pytest.raises(
        ValueError,
        match="pin binding",
    ):
        replace(
            base(),
            controller_clock_binding_complete=True,
            controller_physical_constraints_complete=True,
        )


def test_material_preregistration_requires_all_bound_material():
    with pytest.raises(
        ValueError,
        match="requires all bound physical material",
    ):
        replace(
            base(),
            physical_preregistration_material_complete=True,
        )


def test_material_complete_state_waits_for_human_go():
    assessment = (
        material_complete_without_go()
    )

    assert (
        assessment.status
        == "HUMAN_GO_PENDING"
    )

    assert (
        assessment.execution_authorized
        is False
    )


def test_human_go_cannot_precede_complete_preregistration():
    with pytest.raises(
        ValueError,
        match="cannot precede material-complete",
    ):
        replace(
            base(),
            human_go_present=True,
        )


def test_human_go_does_not_authorize_fpga_programming():
    assessment = replace(
        material_complete_without_go(),
        human_go_present=True,
    )

    assert (
        assessment.execution_authorized
        is True
    )

    assert (
        assessment.fpga_programming_authorized
        is False
    )

    assert (
        assessment.status
        == "FPGA_PROGRAMMING_AUTHORIZATION_PENDING"
    )


def test_programming_authorization_requires_human_go():
    with pytest.raises(
        ValueError,
        match="cannot precede human GO",
    ):
        replace(
            material_complete_without_go(),
            fpga_programming_authorized=True,
        )


def test_programming_completion_requires_authorization():
    assessment = replace(
        material_complete_without_go(),
        human_go_present=True,
    )

    with pytest.raises(
        ValueError,
        match="cannot precede programming authorization",
    ):
        replace(
            assessment,
            fpga_programmed=True,
        )


def test_programmed_authorized_stack_is_ready_for_acquisition():
    assessment = replace(
        material_complete_without_go(),
        human_go_present=True,
        fpga_programming_authorized=True,
        fpga_programmed=True,
    )

    assert (
        assessment.acquisition_ready
        is True
    )

    assert (
        assessment.status
        == "EXECUTION_AUTHORIZED_AWAITING_PHYSICAL_ACQUISITION"
    )

    assessment.require_acquisition_ready()


def test_physical_raw_records_are_postexecution_evidence():
    assessment = replace(
        material_complete_without_go(),
        human_go_present=True,
        fpga_programming_authorized=True,
        fpga_programmed=True,
        physical_raw_records_present=True,
    )

    assert (
        assessment.status
        == "PHYSICAL_EVIDENCE_PRESENT_VALIDATION_PENDING"
    )

    with pytest.raises(
        RuntimeError,
        match="already produced raw records",
    ):
        assessment.require_acquisition_ready()


def test_raw_records_cannot_exist_before_human_go():
    with pytest.raises(
        ValueError,
        match="cannot precede human GO",
    ):
        replace(
            base(),
            physical_raw_records_present=True,
        )


def test_missing_software_component_blocks_every_later_state():
    components = tuple(
        item
        for item in SOFTWARE_COMPONENTS
        if item
        != "physical_prereg_freeze"
    )

    assessment = N0ReadinessAssessment(
        completed_software_components=components,
        controller_logical_protocol_complete=False,
        controller_rtl_simulation_complete=False,
        controller_synthesis_complete=False,
        physical_profile_defined=False,
        physical_apparatus_identity_present=False,
        physical_calibration_values_present=False,
        physical_cpc_probe_realized=False,
        raw_transport_encoding_defined=False,
        physical_timebase_present=False,
        controller_clock_binding_complete=False,
        controller_pin_binding_complete=False,
        controller_adc_dac_binding_complete=False,
        controller_physical_constraints_complete=False,
        controller_place_route_complete=False,
        controller_bitstream_complete=False,
        source_manifest_present=False,
        physical_evidence_manifest_present=False,
        physical_preregistration_material_complete=False,
        human_go_present=False,
        fpga_programming_authorized=False,
        fpga_programmed=False,
        physical_raw_records_present=False,
    )

    assert (
        assessment.status
        == "SOFTWARE_PROFILE_INCOMPLETE"
    )


def test_complete_software_component_set_is_exact():
    assert set(
        complete_software_components()
    ) == set(
        SOFTWARE_COMPONENTS
    )
