"""Shor semantics regression tests."""
import numpy as np
import pytest
from src.shor_order_finding import ShorInstance, load_instance, multiplication_tree
from src.shor_decoder import extract_factors
from src.shor_validation import reference_order, validate_shor
from src.shor_open_system import compile_shor
from src.shor_orbit_spectrum import orbit_hamiltonian, reference_resolution_diagnostic


@pytest.mark.parametrize("N,a,r", [(15,2,4), (21,2,6), (21,4,3), (15,14,2), (35,2,12), (9,2,6)])
def test_semantics(N, a, r):
    instance = ShorInstance(N,a,16)
    assert reference_order(instance) == r
    for x in range(16):
        for y in range(16):
            assert (instance.response(x) == instance.response(y)) == ((x-y) % r == 0)



@pytest.mark.parametrize("data", [dict(N=15,a=2,Q=16,r=4), dict(N=15,a=2,Q=16,p=3),
    dict(N=15,a=2,Q=16,expected_peaks=[0,4,8,12]), dict(N=15,a=2,Q=16,calibration={"answer":4})])
def test_reject_advice(data):
    with pytest.raises(ValueError, match="advice"):
        load_instance(data)



@pytest.mark.parametrize("args", [(15,3,16), (14,3,16), (15,2,15), (15,True,16), (1,2,16)])
def test_invalid_domain(args):
    with pytest.raises(ValueError):
        ShorInstance(*args)



@pytest.mark.parametrize("N,a,r,reason", [(21,4,3,"odd-order"), (15,14,2,"trivial-square-root"),
                                        (9,2,6,"trivial-square-root")])
def test_order_success_is_not_factoring_success(N,a,r,reason):
    instance = ShorInstance(N,a,64)
    result = extract_factors(instance,r)
    assert result.reason == reason and result.factors is None
    assert validate_shor(instance,result).order_minimal



def test_nonminimal_order_is_detected():
    instance = ShorInstance(15,2,16)
    report = validate_shor(instance, extract_factors(instance,8))
    assert report.order_valid and not report.order_minimal



def test_circuit_and_tree_arithmetic():
    instance = ShorInstance(21,2,32)
    model = compile_shor(instance,mode="circuit_clock").topology
    tree = multiplication_tree(instance)
    for x in range(instance.Q):
        values = [leaf.get("constant", leaf.get("one") if (x >> leaf.get("bit",0)) & 1 else leaf.get("zero"))
                  for leaf in tree["leaves"]]
        for pairs in tree["layers"]:
            values = [values[i]*values[j] % instance.N for i,j in pairs]
        assert values[0] == instance.response(x) == model.work_labels[-1][x]
    assert tree["mixing_bound"] == "unknown"



def test_orbit_spectrum_and_resolution_cost():
    instance = ShorInstance(15,2,16)
    h = orbit_hamiltonian(instance)
    assert np.allclose(h,h.T)
    orbit = [1,2,4,8]
    assert np.allclose(np.linalg.eigvalsh(h[np.ix_(orbit,orbit)]),[-2,0,0,2], atol=1e-10)
    small = reference_resolution_diagnostic(32)
    large = reference_resolution_diagnostic(64)
    assert 3.9 < large["inverse_spacing_time"]/small["inverse_spacing_time"] < 4.1
