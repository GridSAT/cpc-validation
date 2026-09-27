"""Reproducible simulation runner for the finite Shor RFC-0010 profile."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import math
import platform
import numpy as np
import scipy
from pathlib import Path
from time import perf_counter

from src.open_system_conformance import validate_rfc0010_conformance
from src.shor_ccir import shor_program
from src.shor_conformance import conformance_evidence
from src.shor_decoder import decode_shor
from src.shor_open_system import (
    compile_shor_program, prepare_shor, evolve_shor, measure_shor,
    execution_specification, graph_fidelity, response_class_coherence,
)
from src.shor_order_finding import load_instance, multiplication_tree
from src.shor_orbit_spectrum import reference_resolution_diagnostic
from src.shor_validation import validate_shor


def run_case(data, *, mode="collective", time=20.0, shots=256, seed=0):
    """Freeze artifacts before evolution; run semantic reference last."""
    timings = {}
    start = perf_counter()
    instance = load_instance(data)
    artifact = compile_shor_program(shor_program(instance), mode=mode)
    timings["compile"] = perf_counter() - start
    start = perf_counter()
    prepared = prepare_shor(artifact)
    specification = execution_specification(prepared)
    timings["prepare"] = perf_counter() - start
    frozen_hash = specification.specification_hash
    start = perf_counter()
    trajectory = evolve_shor(prepared, (0, time))
    timings["evolve"] = perf_counter() - start
    start = perf_counter()
    observed = measure_shor(trajectory, shots=shots, seed=seed)
    timings["readout"] = perf_counter() - start
    start = perf_counter()
    decoded = decode_shor(instance, observed)
    timings["decode"] = perf_counter() - start
    start = perf_counter()
    evidence = conformance_evidence(prepared, specification)
    conformance = validate_rfc0010_conformance(specification=specification,evidence=evidence)
    validation = validate_shor(instance, decoded)
    timings["validate"] = perf_counter() - start
    model = prepared.payload
    return {"schema": "cpc.shor-prototype-run.v1", "input": data, "mode": mode,
        "witness_scope": model.witness_scope,
        "specification": specification.to_dict(), "frozen_specification_hash": frozen_hash,
        "observation": asdict(observed), "decoded": asdict(decoded),
        "validation": asdict(validation), "conformance": asdict(conformance),
        "evidence": asdict(evidence),
        "graph_fidelity": graph_fidelity(model, trajectory.states[-1]),
        "response_class_coherence": response_class_coherence(model, trajectory.states[-1]),
        "solver": trajectory.solver, "simulation_times": trajectory.times,
        "software_versions": {"python": platform.python_version(),
                              "numpy": np.__version__, "scipy": scipy.__version__},
        "finite_time_support_bound": min(1, (2**model.steps-1)*math.exp(-model.kappa*time/2)),
        "numerics": {"dtype": "complex128", "certificate_atol": 1e-9,
                     "solver_tolerance": "SciPy expm_multiply internal floating-point criterion"},
        "simulation_wall_seconds": timings, "simulation_total_seconds": sum(timings.values()),
        "physical_TTS": None, "matched_confidence_advantage": None,
        "multiplication_tree_candidate": multiplication_tree(instance),
        "orbit_reference_diagnostic": reference_resolution_diagnostic(validation.reference_order)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--N", type=int, default=15)
    parser.add_argument("--a", type=int, default=2)
    parser.add_argument("--Q", type=int, default=16)
    parser.add_argument("--mode", choices=("collective","which_x","circuit_clock"), default="collective")
    parser.add_argument("--time", type=float, default=20)
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--corpus", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    cases = json.loads(args.corpus.read_text()) if args.corpus else [dict(N=args.N,a=args.a,Q=args.Q)]
    try:
        reports = [run_case(case, mode=args.mode,time=args.time,shots=args.shots,seed=args.seed) for case in cases]
    except (ValueError, TypeError) as error:
        parser.error(str(error))
    text = json.dumps(reports, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(text)
    else:
        print(text,end="")
    return 0 if all(report["conformance"]["conformant"] for report in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
