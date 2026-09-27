from __future__ import annotations

from dataclasses import dataclass


N0_CONTROLLER_PROTOCOL_SCHEMA = (
    "cpc.shor.n0.controller-protocol.v1"
)

N0_CONTROLLER_PROTOCOL_ID = (
    "CPC-SHOR-N0-CONTROLLER-PROTOCOL-v1"
)

N0_CONTROLLER_RTL_TOP = (
    "cpc_shor_n0_controller"
)

N0_CONTROLLER_EVENT_CODES = {
    "IDLE": 0x0,
    "ARMED": 0x1,
    "PROBE": 0x2,
    "ACQUIRE": 0x3,
    "DONE": 0x4,
    "ERROR": 0xF,
}

N0_CONTROLLER_STATES = tuple(
    N0_CONTROLLER_EVENT_CODES
)

N0_CONTROLLER_INPUTS = (
    "clk",
    "reset_n",
    "arm_i",
    "start_i",
    "device_ready_i",
    "sample_done_i",
    "fault_i",
)

N0_CONTROLLER_OUTPUTS = (
    "probe_enable_o",
    "acquire_enable_o",
    "busy_o",
    "done_o",
    "error_o",
    "event_code_o",
)

FORBIDDEN_CONTROLLER_ROLES = (
    "adc_sample_interpretation",
    "cpc_dynamics_simulation",
    "expected_answer_access",
    "measurement_decoding",
    "phase_estimation",
    "probe_waveform_synthesis",
    "semantic_decision",
    "truth_access",
)


@dataclass(frozen=True)
class N0ControllerProtocol:
    protocol_id: str = (
        N0_CONTROLLER_PROTOCOL_ID
    )

    schema: str = (
        N0_CONTROLLER_PROTOCOL_SCHEMA
    )

    rtl_top: str = (
        N0_CONTROLLER_RTL_TOP
    )

    reset_state: str = "IDLE"

    probe_cycles_parameter: str = (
        "PROBE_CYCLES"
    )

    acquire_timeout_parameter: str = (
        "ACQUIRE_TIMEOUT_CYCLES"
    )

    counter_width_parameter: str = (
        "COUNTER_WIDTH"
    )

    clock_semantics: str = (
        "abstract-controller-cycle; "
        "no physical frequency claimed"
    )

    reset_semantics: str = (
        "asynchronous-active-low"
    )

    terminal_semantics: str = (
        "DONE and ERROR latch until reset"
    )

    controller_role: str = (
        "deterministic sequencing, interlock, "
        "timeout, and event framing only"
    )

    physical_pin_binding: str = (
        "UNRESOLVED"
    )

    physical_clock_binding: str = (
        "UNRESOLVED"
    )

    physical_adc_dac_binding: str = (
        "UNRESOLVED"
    )

    physical_programming_authorized: bool = False

    def __post_init__(self) -> None:
        if (
            self.protocol_id
            != N0_CONTROLLER_PROTOCOL_ID
        ):
            raise ValueError(
                "unsupported controller protocol identity"
            )

        if (
            self.schema
            != N0_CONTROLLER_PROTOCOL_SCHEMA
        ):
            raise ValueError(
                "unsupported controller protocol schema"
            )

        if (
            self.rtl_top
            != N0_CONTROLLER_RTL_TOP
        ):
            raise ValueError(
                "unsupported controller RTL top"
            )

        if self.reset_state != "IDLE":
            raise ValueError(
                "controller reset state must be IDLE"
            )

        for value in (
            self.physical_pin_binding,
            self.physical_clock_binding,
            self.physical_adc_dac_binding,
        ):
            if value != "UNRESOLVED":
                raise ValueError(
                    "v1 logical protocol may not bind "
                    "unverified physical hardware"
                )

        if (
            self.physical_programming_authorized
            is not False
        ):
            raise ValueError(
                "logical protocol may not authorize "
                "physical FPGA programming"
            )

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "schema": self.schema,
            "protocol_id": self.protocol_id,
            "rtl_top": self.rtl_top,
            "states": list(
                N0_CONTROLLER_STATES
            ),
            "event_codes": dict(
                N0_CONTROLLER_EVENT_CODES
            ),
            "inputs": list(
                N0_CONTROLLER_INPUTS
            ),
            "outputs": list(
                N0_CONTROLLER_OUTPUTS
            ),
            "probe_cycles_parameter": (
                self.probe_cycles_parameter
            ),
            "acquire_timeout_parameter": (
                self.acquire_timeout_parameter
            ),
            "counter_width_parameter": (
                self.counter_width_parameter
            ),
            "clock_semantics": (
                self.clock_semantics
            ),
            "reset_semantics": (
                self.reset_semantics
            ),
            "terminal_semantics": (
                self.terminal_semantics
            ),
            "controller_role": (
                self.controller_role
            ),
            "forbidden_controller_roles": list(
                FORBIDDEN_CONTROLLER_ROLES
            ),
            "physical_pin_binding": (
                self.physical_pin_binding
            ),
            "physical_clock_binding": (
                self.physical_clock_binding
            ),
            "physical_adc_dac_binding": (
                self.physical_adc_dac_binding
            ),
            "physical_programming_authorized": (
                self.physical_programming_authorized
            ),
        }


def build_n0_controller_protocol(
) -> N0ControllerProtocol:
    return N0ControllerProtocol()
