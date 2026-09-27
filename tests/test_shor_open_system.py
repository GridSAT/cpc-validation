"""Shor open system regression tests."""
import numpy as np
import pytest
from scipy.linalg import expm
from src.open_system_conformance import validate_rfc0010_conformance
from src.shor_order_finding import ShorInstance
from src.shor_decoder import decode_shor
from src.shor_validation import validate_shor
from src.shor_open_system import compile_shor, prepare_shor, evolve_shor, measure_shor, execution_specification, graph_fidelity, response_class_coherence, fourier_probabilities, lindbladian
from src.shor_conformance import conformance_evidence, verify_dynamics


def prepared(N=15, a=2, Q=16, mode="collective"):
    return prepare_shor(compile_shor(ShorInstance(N, a, Q), mode=mode))



@pytest.mark.parametrize("mode", ["collective", "which_x", "circuit_clock"])
def test_density_evolution_and_certificates(mode):
    p = prepared(Q=4, mode=mode)
    t = evolve_shor(p, (0, 0.7, 3, 16))
    for rho in t.states:
        assert np.trace(rho) == pytest.approx(1, abs=1e-10)
        assert np.allclose(rho, rho.conjugate().T, atol=1e-10)
        assert np.linalg.eigvalsh(rho).min() > -1e-10
    # Independent dense matrix exponential cross-check of the sparse evolution.
    exact = expm(lindbladian(p.payload).toarray() * .7) @ t.states[0].reshape(-1, order="F")
    assert np.allclose(exact.reshape(t.states[1].shape, order="F"), t.states[1], atol=1e-10)
    checks = verify_dynamics(p.payload)
    assert all(checks[key] for key in ("terminal_silence","dark_complete","fixed_complete","lyapunov"))
    spec = execution_specification(p)
    report = validate_rfc0010_conformance(specification=spec, evidence=conformance_evidence(p,spec))
    assert report.conformant
    # Numerical nullity independently verifies the triangular fixed-point certificate.
    singular = np.linalg.svd(lindbladian(p.payload).toarray(), compute_uv=False)
    assert np.count_nonzero(singular < 1e-9) == p.payload.instance.Q**2



def test_coherence_obstruction():
    states = {}
    for mode in ("collective", "which_x", "circuit_clock"):
        p = prepared(mode=mode)
        rho = evolve_shor(p, (20,)).states[-1]
        states[mode] = graph_fidelity(p.payload, rho)
        probabilities = fourier_probabilities(p.payload, rho)
        if mode == "which_x":
            assert response_class_coherence(p.payload, rho) < 1e-10
            assert np.allclose(probabilities, np.full(16, 1/16), atol=1e-7)
        else:
            assert response_class_coherence(p.payload, rho) > .999
            assert probabilities[[0,4,8,12]].sum() > .999
    assert states["collective"] > .999
    assert states["circuit_clock"] > .999
    assert states["which_x"] == pytest.approx(1/16, abs=1e-7)



def test_fourier_nondividing_order_and_bounded_samples():
    p = prepared(21,2,64)
    t = evolve_shor(p, (18,))
    observed = measure_shor(t, shots=512, seed=19)
    result = decode_shor(p.payload.instance, observed)
    validation = validate_shor(p.payload.instance, result)
    assert validation.order_minimal and validation.factors_valid
    assert measure_shor(t, shots=512, seed=19) == observed
    assert dict(observed.metadata)["shots"] == 512



def test_empty_readout_and_herald_accounting():
    p = prepared()
    observed = measure_shor(evolve_shor(p, (0,)), shots=23, seed=1)
    assert dict(observed.metadata)["failed_heralds"] == 23
    assert decode_shor(p.payload.instance, observed).order_candidate is None



def test_resource_limit_and_bad_time():
    with pytest.raises(ValueError, match="budget"):
        compile_shor(ShorInstance(15,2,1024))
    with pytest.raises(ValueError):
        evolve_shor(prepared(), (0,float("nan")))



def test_lyapunov_bound_along_actual_trajectory():
    p = prepared(Q=8,mode="circuit_clock")
    model = p.payload
    h = np.repeat([2**(model.steps-j)-1 for j in range(model.steps+1)],8)
    trajectory = evolve_shor(p,(0,1,4,10))
    for time,rho in zip(trajectory.times,trajectory.states):
        energy = np.dot(h,rho.diagonal().real)
        assert energy <= h[0]*np.exp(-model.kappa*time/2)+1e-9



def test_terminal_stationary_coherences_are_preserved():
    p = prepared(Q=4)
    model = p.payload
    coherence = np.zeros((model.dimension,model.dimension),complex)
    coherence[-1,-2] = 1
    assert np.linalg.norm(lindbladian(model) @ coherence.reshape(-1,order="F")) < 1e-12
