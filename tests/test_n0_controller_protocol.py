from src.n0_controller_protocol import (
    FORBIDDEN_CONTROLLER_ROLES,
    N0_CONTROLLER_EVENT_CODES,
    N0_CONTROLLER_INPUTS,
    N0_CONTROLLER_OUTPUTS,
    N0_CONTROLLER_PROTOCOL_ID,
    N0_CONTROLLER_PROTOCOL_SCHEMA,
    N0_CONTROLLER_RTL_TOP,
    build_n0_controller_protocol,
)


def test_protocol_identity_is_frozen():
    protocol = (
        build_n0_controller_protocol()
    )

    assert (
        protocol.protocol_id
        == "CPC-SHOR-N0-CONTROLLER-PROTOCOL-v1"
    )

    assert (
        protocol.schema
        == "cpc.shor.n0.controller-protocol.v1"
    )

    assert (
        protocol.rtl_top
        == "cpc_shor_n0_controller"
    )

    assert (
        protocol.protocol_id
        == N0_CONTROLLER_PROTOCOL_ID
    )

    assert (
        protocol.schema
        == N0_CONTROLLER_PROTOCOL_SCHEMA
    )

    assert (
        protocol.rtl_top
        == N0_CONTROLLER_RTL_TOP
    )


def test_event_codes_are_unique_and_fail_closed():
    values = tuple(
        N0_CONTROLLER_EVENT_CODES.values()
    )

    assert len(values) == len(
        set(values)
    )

    assert (
        N0_CONTROLLER_EVENT_CODES["ERROR"]
        == 0xF
    )


def test_interface_is_narrow_control_only():
    assert N0_CONTROLLER_INPUTS == (
        "clk",
        "reset_n",
        "arm_i",
        "start_i",
        "device_ready_i",
        "sample_done_i",
        "fault_i",
    )

    assert N0_CONTROLLER_OUTPUTS == (
        "probe_enable_o",
        "acquire_enable_o",
        "busy_o",
        "done_o",
        "error_o",
        "event_code_o",
    )


def test_truth_and_semantic_roles_are_forbidden():
    roles = set(
        FORBIDDEN_CONTROLLER_ROLES
    )

    assert {
        "truth_access",
        "expected_answer_access",
        "measurement_decoding",
        "phase_estimation",
        "semantic_decision",
        "cpc_dynamics_simulation",
        "probe_waveform_synthesis",
    }.issubset(
        roles
    )


def test_physical_bindings_remain_unresolved():
    protocol = (
        build_n0_controller_protocol()
    )

    assert (
        protocol.physical_pin_binding
        == "UNRESOLVED"
    )

    assert (
        protocol.physical_clock_binding
        == "UNRESOLVED"
    )

    assert (
        protocol.physical_adc_dac_binding
        == "UNRESOLVED"
    )

    assert (
        protocol.physical_programming_authorized
        is False
    )


def test_clock_semantics_make_no_frequency_claim():
    protocol = (
        build_n0_controller_protocol()
    )

    text = (
        protocol.clock_semantics.lower()
    )

    assert "abstract" in text
    assert "no physical frequency" in text
