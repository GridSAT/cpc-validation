"""Full-register single-node reset experiments; no native/local synthesis claim.

See docs/shor-single-node-research.md for the pre-implementation derivation.
This module neither imports order validation nor computes periods/factors.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import expm_multiply

CANDIDATES = ("output_reset", "input_output_reset")
MAX_DIMENSION = 64


def content_hash(value: object) -> str:
    """Canonical model/evidence identity, with no nonfinite JSON values."""
    return "sha256:" + hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()).hexdigest()


def array_hash(array: np.ndarray) -> str:
    """Bind shape and complex128 values in a fixed byte order."""
    canonical = np.asarray(array, dtype="<c16", order="C")
    payload = json.dumps(canonical.shape).encode() + canonical.tobytes()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class ModularNode:
    """Total binary-domain extension of z=u*v mod N on three n-qubit registers."""

    N: int
    candidate: str = "output_reset"
    kappa: float = 1.0

    def __post_init__(self) -> None:
        if type(self.N) is not int or self.N < 2:
            raise ValueError("N must be an integer >= 2")
        if self.candidate not in CANDIDATES:
            raise ValueError("unknown reset candidate")
        if isinstance(self.kappa, bool) or not isinstance(self.kappa, (int, float)) or not math.isfinite(self.kappa) or self.kappa <= 0:
            raise ValueError("kappa must be finite and positive")
        if self.dimension > MAX_DIMENSION:
            raise ValueError("full tensor-product simulator dimension budget exceeded")

    @property
    def n(self) -> int:
        return (self.N - 1).bit_length()

    @property
    def d(self) -> int:
        return 1 << self.n

    @property
    def dimension(self) -> int:
        return self.d**3

    @property
    def model_hash(self) -> str:
        return content_hash(self.description())

    def description(self) -> dict:
        return {**asdict(self), "schema": "cpc.shor.modular-node.v1",
                "registers": ["U", "V", "Z"], "qubits_each": self.n,
                "basis": "((u*d)+v)*d+z; big-endian qubits",
                "arithmetic": "z XOR ((u mod N)*(v mod N) mod N)",
                "hamiltonian": "zero", "realization": "simulated",
                "jump_rule": "A (one-qubit reset) A-adjoint",
                "input_reset": "plus" if self.candidate == "input_output_reset" else "none",
                "output_reset": "zero", "rate_convention": "each jump norm sqrt(kappa)",
                "scope": "arithmetic-unitary-conjugated-single-node-research"}


def arithmetic_unitary(model: ModularNode) -> sparse.csr_matrix:
    """Enumerate an actual permutation on ALL U,V,Z basis states, not an oracle."""
    d = model.d
    columns = np.arange(model.dimension)
    rows = []
    for u in range(d):
        for v in range(d):
            product = (u % model.N) * (v % model.N) % model.N
            rows.extend(((u*d + v)*d + (z ^ product)) for z in range(d))
    return sparse.csr_matrix((np.ones(model.dimension), (rows, columns)),
                             shape=(model.dimension, model.dimension))


def _bit_operator(matrix: np.ndarray, bit: int, total: int) -> sparse.csr_matrix:
    result = sparse.csr_matrix([[1.0]])
    for position in range(total):
        result = sparse.kron(result, matrix if position == bit else np.eye(2), format="csr")
    return result


def bare_jumps(model: ModularNode) -> tuple[sparse.csr_matrix, ...]:
    """Reset frame: plus resets on inputs when enabled, zero resets on output."""
    zero_reset = np.array([[0, 1], [0, 0]], dtype=float)
    plus_reset = np.array([[1, -1], [1, -1]], dtype=float)/2
    jumps = []
    for bit in range(3*model.n):
        if bit < 2*model.n and model.candidate == "output_reset":
            continue
        local = plus_reset if bit < 2*model.n else zero_reset
        jumps.append(math.sqrt(model.kappa)*_bit_operator(local, bit, 3*model.n))
    return tuple(jumps)


def node_jumps(model: ModularNode) -> tuple[sparse.csr_matrix, ...]:
    """Explicit arithmetic-dressed matrices, generally supported across the node."""
    unitary = arithmetic_unitary(model)
    return tuple((unitary @ jump @ unitary.getH()).tocsr() for jump in bare_jumps(model))


def gksl(jumps: tuple[sparse.csr_matrix, ...]) -> sparse.csr_matrix:
    """Column-vectorized GKSL generator for the supplied full matrices."""
    if not jumps:
        raise ValueError("nonempty jump family required")
    dimension = jumps[0].shape[0]
    identity = sparse.eye(dimension, format="csr")
    generator = sparse.csr_matrix((dimension**2, dimension**2), dtype=complex)
    for jump in jumps:
        loss = jump.getH() @ jump
        generator += sparse.kron(jump.conjugate(), jump, format="csr")
        generator -= .5*(sparse.kron(identity, loss, format="csr")
                          + sparse.kron(loss.T, identity, format="csr"))
    return generator


def node_generator(model: ModularNode) -> sparse.csr_matrix:
    """Return the actual full density-operator generator."""
    return gksl(node_jumps(model))


def blank_preparation(model: ModularNode) -> np.ndarray:
    """Known uniform binary inputs and blank output; no answer-dependent advice."""
    vector = np.zeros(model.dimension, dtype=complex)
    vector[::model.d] = 1/model.d
    return np.outer(vector, vector.conjugate())


def uniform_graph(model: ModularNode) -> np.ndarray:
    """Independent mathematical diagnostic target, not a generator input."""
    vector = np.zeros(model.dimension, dtype=complex)
    for u in range(model.d):
        for v in range(model.d):
            vector[(u*model.d+v)*model.d + (u*v) % model.N] = 1/model.d
    return np.outer(vector, vector.conjugate())


def graph_projector(model: ModularNode) -> np.ndarray:
    """Whole relation-valid subspace, kept distinct from the uniform graph state."""
    diagonal = np.zeros(model.dimension)
    for u in range(model.d):
        for v in range(model.d):
            diagonal[(u*model.d+v)*model.d + (u*v) % model.N] = 1
    return np.diag(diagonal)


def trace_output(model: ModularNode, operator: np.ndarray) -> np.ndarray:
    """Partial trace over Z; works on all operators including matrix units."""
    b, d = model.d**2, model.d
    return np.trace(np.asarray(operator).reshape(b, d, b, d), axis1=1, axis2=3)


def syndrome_kraus(model: ModularNode) -> tuple[np.ndarray, ...]:
    """Explicit extraction/correction/reset channel, independently indexed by s."""
    matrices = []
    for syndrome in range(model.d):
        matrix = np.zeros((model.dimension, model.dimension), complex)
        for u in range(model.d):
            for v in range(model.d):
                product = (u*v) % model.N
                offset = (u*model.d+v)*model.d
                matrix[offset+product, offset+(syndrome ^ product)] = 1
        matrices.append(matrix)
    return tuple(matrices)


def apply_syndrome_channel(model: ModularNode, operator: np.ndarray) -> np.ndarray:
    """Full channel of candidate A; do not confuse it with pure graph preparation."""
    return sum((k @ operator @ k.conjugate().T for k in syndrome_kraus(model)),
               np.zeros_like(operator, dtype=complex))


def asymptotic_channel(model: ModularNode, operator: np.ndarray) -> np.ndarray:
    """Analytically derived limit, used only as an audit of actual evolution."""
    if model.candidate == "input_output_reset":
        return np.trace(operator)*uniform_graph(model)
    unitary = arithmetic_unitary(model).toarray()
    decoded = unitary.conjugate().T @ operator @ unitary
    zero = np.zeros((model.d, model.d)); zero[0, 0] = 1
    return unitary @ np.kron(trace_output(model, decoded), zero) @ unitary.conjugate().T


def evolve_node(model: ModularNode, initial: np.ndarray,
                times: tuple[float, ...]) -> tuple[np.ndarray, ...]:
    """Evolve full density matrices with exp(t L); no substituted decay formula."""
    initial = np.asarray(initial, dtype=complex)
    if initial.shape != (model.dimension, model.dimension) or not np.isfinite(initial).all():
        raise ValueError("invalid initial density shape or entries")
    if not np.allclose(initial, initial.conjugate().T, atol=1e-10, rtol=0) or not np.isclose(np.trace(initial), 1, atol=1e-10, rtol=0) or np.linalg.eigvalsh(initial).min() < -1e-10:
        raise ValueError("initial operator must be a density matrix")
    if not times or any(isinstance(t, bool) or not isinstance(t, (float, int)) or not math.isfinite(t) or t < 0 for t in times) or any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("times must be strictly increasing finite nonnegative values")
    generator = node_generator(model)
    vector = initial.reshape(-1, order="F")
    return tuple(expm_multiply(t*generator, vector).reshape(initial.shape, order="F")
                 for t in times)


def fourier_input_probabilities(model: ModularNode, operator: np.ndarray) -> np.ndarray:
    """Retained conventional joint-input Fourier diagnostic; no order decoder."""
    reduced = trace_output(model, operator)
    size = model.d**2
    fourier = np.exp(-2j*np.pi*np.outer(np.arange(size), np.arange(size))/size)/np.sqrt(size)
    return np.real(np.diag(fourier @ reduced @ fourier.conjugate().T))


def node_certificate(model: ModularNode) -> dict:
    """Return bound numerical residuals, not a hard-coded conformance decision."""
    unitary = arithmetic_unitary(model).toarray()
    jumps = node_jumps(model)
    bare = bare_jumps(model)
    dimension = model.dimension
    target, valid = uniform_graph(model), graph_projector(model)
    penalty = sum((jump.getH() @ jump/model.kappa for jump in jumps),
                  sparse.csr_matrix((dimension, dimension))).toarray()
    adjoint = sum((jump.getH() @ penalty @ jump -
                   ((jump.getH() @ jump) @ penalty + penalty @ (jump.getH() @ jump))/2
                   for jump in jumps), np.zeros_like(penalty))
    positive = np.linalg.eigvalsh(penalty)
    residuals = {
        "unitarity_fro": float(np.linalg.norm(unitary.conjugate().T@unitary-np.eye(dimension))),
        "jump_conjugation_fro_max": max(float(np.linalg.norm(jump.toarray()-unitary@b.toarray()@unitary.conjugate().T)) for jump,b in zip(jumps,bare)),
        "target_silence_fro_max": max(float(np.linalg.norm(jump@target)) for jump in jumps),
        "valid_sector_leakage_fro_max": max(float(np.linalg.norm((np.eye(dimension)-valid)@jump@valid)) for jump in jumps),
        "valid_sector_silence_fro_max": max(float(np.linalg.norm(jump@valid)) for jump in jumps),
        "lyapunov_identity_fro": float(np.linalg.norm(adjoint+model.kappa*penalty)),
        "positive_penalty_scale": float(positive[positive>1e-9].min()),
    }
    matrix_hashes = tuple(array_hash(jump.toarray()) for jump in jumps)
    certificate = {"model_hash": model.model_hash, "jump_matrix_hashes": matrix_hashes,
        "unitary_hash": array_hash(unitary), "penalty_hash": array_hash(penalty),
        "method": "full-register-matrix-residuals-and-derived-tensor-reset-similarity",
        "atol": 1e-9, "residuals": residuals,
        "derived_fixed_operator_dimension": model.d**4 if model.candidate == "output_reset" else 1,
        "derived_spectral_real_part_gap": model.kappa/2,
        "derived_penalty_decay_rate": model.kappa,
        "physical_synthesis_established": False,
        "tree_composition_established": False,
        "rfc0010_conformance_claim": None}
    return {**certificate, "certificate_hash": content_hash(certificate)}


def resource_record(model: ModularNode) -> dict:
    """Separate symbolic bounds, classical simulation and unresolved synthesis."""
    count = model.n if model.candidate == "output_reset" else 3*model.n
    return {"modulus_bits": model.n, "exponent_width": None,
        "input_domain": "full-binary-u-v-with-total-modular-extension",
        "system_qubits": 3*model.n, "density_entries": model.dimension**2,
        "hilbert_dimension": model.dimension, "generator_terms": count,
        "maximum_term_support_qubits": 3*model.n,
        "each_jump_norm": math.sqrt(model.kappa), "total_squared_jump_norm": count*model.kappa,
        "syndrome_channel_extra_qubits": model.n,
        "arithmetic_clean_ancillas": "A_mul(n), unimplemented",
        "arithmetic_gate_count": "G_mul(n), unimplemented",
        "arithmetic_depth": "D_mul(n), unimplemented",
        "description": "symbolic conjugation compact; simulation enumerates d^3 states",
        "physical_local_synthesis": None, "physical_parallel_controls": None,
        "physical_preparation_reset_cost": None, "physical_precision_calibration": None,
        "physical_energy": None, "physical_observation_duration": None,
        "physical_TTS": None, "matched_confidence_advantage": None,
        "shots": 0, "sampling": "exact-density-diagnostics-only",
        "heralds": "none; no postselection", "order_decoder": "none",
        "simulator_dtype": "complex128", "realization": "simulated"}
