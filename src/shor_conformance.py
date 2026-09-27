"""Computed finite-model certificates bound to the existing RFC-0010 schema."""
from __future__ import annotations

import numpy as np
from scipy import sparse

from src.open_system_conformance import RFC0010ConformanceEvidence, RequirementEvidence
from src.shor_open_system import (
    ShorModel, compile_shor, execution_specification, jump_operators, lindbladian,
    prepare_shor,
)


# Each entry names the actual finite-model check or declaration. A canonical
# declaration is not upgraded to an independent numerical/physical proof.
REQUIREMENT_METHODS = {
    "OS-1": ("generator-separation", "canonical-zero-stabilization-and-problem-generator-declaration"),
    "OS-2": ("protected-manifold", "canonical-reachable-basis-manifold-identity"),
    "OS-3": ("uniform-synthesis", "canonical-instance-and-fixed-rule-recompilation"),
    "OS-4": ("answer-independence", "canonical-admitted-input-artifact-comparison"),
    "OS-5": ("correction-family", "canonical-forward-clock-jump-family-declaration"),
    "OS-6": ("terminal-silence", "numerical-terminal-superoperator-column-check"),
    "OS-7": ("dark-vector-sector", "numerical-jump-loss-kernel-check"),
    "OS-8": ("fixed-operator-space", "numerical-triangular-superoperator-kernel-certificate"),
    "DC-1": ("semantic-penalty", "canonical-weighted-clock-penalty-declaration"),
    "DC-2": ("positive-penalty-scale", "numerical-minimum-positive-clock-weight"),
    "DC-3": ("penalty-lyapunov", "numerical-adjoint-penalty-inequality"),
    "DC-4": ("convergence-rate", "declared-kappa-half-rate-backed-by-adjoint-inequality"),
    "DC-5": ("leakage-accounting", "canonical-closed-reachable-basis-leakage-declaration"),
    "DC-6": ("resource-accounting", "canonical-finite-simulator-resource-record"),
    "OV-1": ("admitted-observations", "canonical-fourier-bin-interface-declaration"),
    "OV-2": ("validation-separation", "canonical-backend-validation-boundary-declaration"),
    "OV-3": ("evidence-binding", "canonical-preparation-and-specification-hash-binding"),
    "OV-4": ("realization-status", "canonical-simulated-realization-status-check"),
}


def verify_dynamics(model: ShorModel) -> dict[str, bool | float]:
    """Check a triangular-generator certificate, not only pure dark vectors.

    Every nonterminal operator diagonal has strictly negative decay. The
    terminal Q^2 columns vanish. A triangular operator with these properties
    has exactly the full terminal operator space as kernel. This includes
    stationary coherences, independently of the common pure-dark-space check.
    """
    q, d = model.instance.Q, model.dimension
    jumps = jump_operators(model)
    generator = lindbladian(model)
    loss = sum((j.getH() @ j for j in jumps), sparse.csr_matrix((d, d)))
    expected_loss = np.r_[np.full(d-q, model.kappa), np.zeros(q)]
    dark_complete = np.allclose(loss.toarray(), np.diag(expected_loss), atol=1e-9, rtol=0)
    terminal_indices = np.array([i + d*j for j in range(d-q, d) for i in range(d-q, d)])
    other = np.ones(d*d, bool)
    other[terminal_indices] = False
    upper = sparse.triu(generator, k=1)
    triangular = upper.nnz == 0 or np.max(np.abs(upper.data)) < 1e-9
    terminal_zero = generator[:, terminal_indices].nnz == 0
    fixed_complete = triangular and terminal_zero and bool(np.all(generator.diagonal().real[other] < 0))
    h = np.repeat([2**(model.steps-j)-1 for j in range(model.steps+1)], q).astype(float)
    penalty = sparse.diags(h, format="csr")
    adjoint = sparse.csr_matrix((d, d))
    for jump in jumps:
        jj = jump.getH() @ jump
        adjoint += jump.getH() @ penalty @ jump - (jj @ penalty + penalty @ jj)/2
    residual = adjoint + model.kappa/2 * penalty
    largest = float(np.linalg.eigvalsh(residual.toarray()).max())
    return {"terminal_silence": terminal_zero,
            "dark_complete": bool(dark_complete),
            "fixed_complete": bool(fixed_complete),
            "lyapunov": largest <= 1e-9,
            "lyapunov_max_eigenvalue": largest,
            "positive_penalty_scale": float(h[h > 0].min())}


def conformance_evidence(prepared, specification) -> RFC0010ConformanceEvidence:
    """Fail closed on substituted specification/preparation or failed certificates.

    These are numerical finite-model certificates, not physical evidence or
    proofs of efficient/native synthesis. Coherent graph preparation is tested
    separately; the terminal *subspace* alone does not guarantee coherence.
    """
    model = prepared.payload
    checks = verify_dynamics(model)
    canonical = prepare_shor(compile_shor(model.instance, mode=model.mode, kappa=model.kappa))
    binding = prepared == canonical and specification == execution_specification(canonical)
    values = {
        "OS-1": binding, "OS-2": binding, "OS-3": binding, "OS-4": binding,
        "OS-5": binding, "OS-6": checks["terminal_silence"],
        "OS-7": checks["dark_complete"], "OS-8": checks["fixed_complete"],
        "DC-1": binding, "DC-2": checks["positive_penalty_scale"] == 1,
        "DC-3": checks["lyapunov"], "DC-4": checks["lyapunov"],
        "DC-5": binding, "DC-6": binding,
        "OV-1": binding, "OV-2": binding, "OV-3": binding, "OV-4": binding,
    }
    return RFC0010ConformanceEvidence(specification.specification_hash, tuple(
        RequirementEvidence(key, "shor.finite-model." + key + "." + REQUIREMENT_METHODS[key][0],
            REQUIREMENT_METHODS[key][1], bool(value and binding),
            exact=False, details=(("generator_hash", model.generator_hash),
                                  ("scope", "simulated-finite-model"),
                                  ("witness_scope", model.witness_scope)))
        for key, value in sorted(values.items())))
