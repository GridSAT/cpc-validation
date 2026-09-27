"""Typed modular-response CCIR profile, separate from Boolean continuation."""
from dataclasses import dataclass

from src.backend import BackendCapabilities, BackendRuleDefinition, BackendSpecification
from src.ccir import CCIRConstraint, CCIRPayload, CCIRProgram
from src.shor_order_finding import ShorInstance


@dataclass(frozen=True)
class ModularResponsePayload(CCIRPayload):
    """Declarative y = a**x mod N; no period or factor supplied."""

    instance: ShorInstance
    exponent_bits: tuple[int, ...]
    response_bits: tuple[int, ...]

    def to_dict(self):
        return {"N": self.instance.N, "a": self.instance.a, "Q": self.instance.Q,
                "exponent_bits": self.exponent_bits, "response_bits": self.response_bits}


def shor_program(instance: ShorInstance) -> CCIRProgram:
    """Lower admitted arithmetic inputs into one typed response relation."""
    m, n = instance.Q.bit_length()-1, (instance.N-1).bit_length()
    return CCIRProgram(name="shor-" + instance.instance_id,
        variable_count=m+n, boundary_variables=tuple(range(m)),
        constraints=(CCIRConstraint("modular_response", ModularResponsePayload(
            instance, tuple(range(m)), tuple(range(m,m+n)))),))


def instance_from_program(program: CCIRProgram) -> ShorInstance:
    """Accept only the canonical Shor profile; reject metadata/advice additions."""
    if len(program.constraints) != 1 or not isinstance(program.constraints[0].payload, ModularResponsePayload):
        raise ValueError("expected one modular-response constraint")
    instance = program.constraints[0].payload.instance
    if program != shor_program(instance):
        raise ValueError("noncanonical Shor program or unadmitted metadata")
    return instance


SHOR_BACKEND_SPECIFICATION = BackendSpecification(
    "cpc.shor.density", "0.1",
    BackendCapabilities(frozenset({"modular_response"})),
    rules=(BackendRuleDefinition("shor.reachable-clock.v1"),))
