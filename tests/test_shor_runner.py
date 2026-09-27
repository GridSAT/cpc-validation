"""Shor runner regression tests."""
import pytest


@pytest.mark.parametrize("N,a,Q", [(15,2,16),(21,2,64),(21,4,64),(15,14,16),(35,2,64),(9,2,64)])
def test_corpus_end_to_end(N,a,Q):
    from run_shor import run_case
    report = run_case(dict(N=N,a=a,Q=Q), shots=256,seed=0)
    assert report["validation"]["order_minimal"]
    assert report["conformance"]["conformant"]
    assert report["physical_TTS"] is None



def test_cli_reproducible_output(tmp_path):
    from run_shor import main
    import json
    destination = tmp_path / "report.json"
    assert main(["--corpus","examples/shor/tiny.json","--output",str(destination)]) == 0
    result = json.loads(destination.read_text())[0]
    assert result["decoded"]["factors"] == [3,5]
    assert result["specification"]["realization_status"] == "simulated"



@pytest.mark.parametrize("mode,scope", [
    ("collective", "semantic_reference_only"),
    ("which_x", "which_x_decoherence_negative_control"),
    ("circuit_clock", "dissipative-circuit-baseline"),
])
def test_report_witness_scope_and_candidate_boundaries(mode, scope):
    from run_shor import run_case
    from src.shor_open_system import compile_shor
    from src.shor_order_finding import ShorInstance

    report = run_case(dict(N=15, a=2, Q=16), mode=mode)
    artifact = compile_shor(ShorInstance(15, 2, 16), mode=mode)
    assert artifact.metadata["scope"] == scope
    assert report["witness_scope"] == scope
    assert report["specification"]["metadata"]["scope"] == scope
    assert all(dict(item["details"])["witness_scope"] == scope
               for item in report["evidence"]["requirements"])
    assert "native_tree" not in report
    candidate = report["multiplication_tree_candidate"]
    assert candidate["status"] == "constraint-description-only"
    assert candidate["coherence"] == "unproved"
    assert candidate["mixing_bound"] == "unknown"
    assert report["physical_TTS"] is None
    assert report["matched_confidence_advantage"] is None
    assert report["specification"]["realization_status"] == "simulated"
    assert "RR" not in report["specification"]["conformance_groups"]
