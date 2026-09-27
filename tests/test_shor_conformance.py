"""Shor conformance regression tests."""
import ast
from dataclasses import replace
from pathlib import Path
import pytest
from src.open_system_conformance import validate_rfc0010_conformance
from src.shor_order_finding import ShorInstance
from src.shor_decoder import decode_shor
from src.shor_open_system import compile_shor, prepare_shor, evolve_shor, measure_shor, execution_specification
from src.shor_conformance import conformance_evidence
from src.shor_ccir import shor_program
from src.shor_open_system import compile_shor_program


def prepared(N=15, a=2, Q=16, mode="collective"):
    return prepare_shor(compile_shor(ShorInstance(N, a, Q), mode=mode))



def test_no_reference_dependency_and_no_oracle_calls(monkeypatch):
    import src.shor_validation as reference
    monkeypatch.setattr(reference, "reference_order", lambda *_: pytest.fail("oracle used"))
    for name in ("shor_order_finding", "shor_open_system", "shor_conformance", "shor_orbit_spectrum", "shor_decoder"):
        tree = ast.parse((Path("src") / (name + ".py")).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                assert "validation" not in (node.module or "")
    p = prepared()
    t = evolve_shor(p, (0, 8))
    assert decode_shor(p.payload.instance, measure_shor(t, shots=100, seed=2)).factors == (3,5)



def test_substitution_rejected():
    artifact = compile_shor(ShorInstance(15,2,16))
    model = replace(artifact.topology, work_labels=((0,)*16,(1,)*16))
    bad = replace(artifact, topology=model, metadata={**artifact.metadata, "generator_hash": model.generator_hash})
    with pytest.raises(ValueError, match="canonical"):
        prepare_shor(bad)



def test_readout_interface_rejects_internal_state():
    p = prepared()
    observed = measure_shor(evolve_shor(p,(5,)), shots=5, seed=1)
    bad = replace(observed, observations=(("rho", [1]),))
    with pytest.raises(ValueError, match="only Fourier"):
        decode_shor(p.payload.instance,bad)
    with pytest.raises(ValueError, match="mismatch"):
        decode_shor(ShorInstance(21,2,16), observed)



def test_conformance_fails_on_missing_evidence_and_substituted_generator():
    p = prepared(Q=4)
    spec = execution_specification(p)
    evidence = conformance_evidence(p,spec)
    bad = replace(evidence, requirements=evidence.requirements[:-1])
    assert not validate_rfc0010_conformance(specification=spec,evidence=bad).conformant
    badspec = replace(spec, problem_generator_hash="sha256:"+"0"*64)
    assert not validate_rfc0010_conformance(specification=badspec,
        evidence=conformance_evidence(p,badspec)).conformant
    rrspec = replace(spec, conformance_groups=("DC","OS","OV","RR"))
    assert not validate_rfc0010_conformance(specification=rrspec,evidence=evidence).conformant



def test_ccir_entry_and_metadata_advice_rejection():
    instance = ShorInstance(15,2,16)
    program = shor_program(instance)
    assert compile_shor_program(program) == compile_shor(instance)
    with pytest.raises(ValueError, match="metadata"):
        compile_shor_program(replace(program, metadata=(("r",4),)))



@pytest.mark.parametrize("module_name,function_name,admitted", [
    ("shor_open_system", "compile_shor", ("instance", "mode", "kappa")),
    ("shor_open_system", "compile_shor_program", ("program", "mode", "kappa")),
    ("shor_open_system", "prepare_shor", ("artifact",)),
    ("shor_open_system", "evolve_shor", ("prepared", "times")),
    ("shor_open_system", "measure_shor", ("trajectory", "shots", "seed")),
    ("shor_open_system", "execution_specification", ("prepared",)),
    ("shor_open_system", "jump_operators", ("model",)),
    ("shor_open_system", "lindbladian", ("model",)),
    ("shor_open_system", "fourier_probabilities", ("model", "rho")),
    ("shor_open_system", "prepared_hash", ("prepared",)),
    ("shor_ccir", "shor_program", ("instance",)),
    ("shor_ccir", "instance_from_program", ("program",)),
    ("shor_order_finding", "load_instance", ("data",)),
    ("shor_order_finding", "multiplier_constants", ("instance",)),
    ("shor_order_finding", "multiplication_tree", ("instance",)),
    ("shor_orbit_spectrum", "orbit_hamiltonian", ("instance", "g")),
    ("shor_orbit_spectrum", "orbit_spectral_measure", ("instance", "g")),
    ("shor_decoder", "decode_shor", ("instance", "observed")),
])
def test_boundary_signatures_forbid_semantic_advice(module_name, function_name, admitted):
    """Lock the admitted public signatures, including rejection of **kwargs.

    This guards API changes; typed payload/canonical-artifact and dependency
    checks remain necessary and are exercised separately.
    """
    import importlib
    import inspect

    function = getattr(importlib.import_module("src." + module_name), function_name)
    signature = inspect.signature(function)
    assert tuple(signature.parameters) == admitted
    assert all(parameter.kind not in (inspect.Parameter.VAR_POSITIONAL,
                                      inspect.Parameter.VAR_KEYWORD)
               for parameter in signature.parameters.values())
    forbidden = (
        "r", "p", "q", "order", "period", "factors", "factorization",
        "expected_order", "expected_period", "expected_factors", "expected_peaks",
        "fourier_peaks", "expected_fourier_peaks", "expected_output",
        "expected_decoded_output", "semantic_answer", "reference_order",
        "reference_answer", "semantic_oracle", "semantic_advice", "solution_advice",
        "continuation_values", "completion_table", "satisfying_assignments",
    )
    for name in forbidden:
        assert name not in signature.parameters
        with pytest.raises(TypeError):
            signature.bind_partial(**{name: object()})


def test_requirement_specific_evidence_preserves_claim_boundaries():
    from src.shor_conformance import REQUIREMENT_METHODS
    p = prepared(Q=4)
    spec = execution_specification(p)
    evidence = conformance_evidence(p, spec)
    assert {item.requirement_id for item in evidence.requirements} == set(REQUIREMENT_METHODS)
    assert len({item.method for item in evidence.requirements}) == 18
    assert len({item.evidence_id for item in evidence.requirements}) == 18
    for item in evidence.requirements:
        identity, method = REQUIREMENT_METHODS[item.requirement_id]
        assert item.evidence_id == f"shor.finite-model.{item.requirement_id}.{identity}"
        assert item.method == method
        assert not item.exact
        assert item.passed
        assert dict(item.details)["scope"] == "simulated-finite-model"
        assert dict(item.details)["witness_scope"] == p.payload.witness_scope
    assert spec.conformance_groups == ("DC", "OS", "OV")
    assert spec.realization_status == "simulated"
    assert spec.readout.declared_error_bound is None
    assert spec.readout.decision_margin is None


@pytest.mark.parametrize("check,failed_ids", [
    ("terminal_silence", {"OS-6"}),
    ("dark_complete", {"OS-7"}),
    ("fixed_complete", {"OS-8"}),
    ("lyapunov", {"DC-3", "DC-4"}),
])
def test_requirement_specific_failures_are_not_relabelled(monkeypatch, check, failed_ids):
    import src.shor_conformance as conformance
    p = prepared(Q=4)
    checks = conformance.verify_dynamics(p.payload)
    checks[check] = False
    monkeypatch.setattr(conformance, "verify_dynamics", lambda model: checks)
    evidence = conformance.conformance_evidence(p, execution_specification(p))
    assert {item.requirement_id for item in evidence.requirements if not item.passed} == failed_ids
