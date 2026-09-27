"""Bounded density-matrix witnesses for the Shor RFC-0010 profile.

The simulator uses an explicitly enumerated reachable basis |clock,x,y_clock(x)>.
This is an isometric compression, not a polynomial physical synthesis. The
collective graph witness is semantic_reference_only; the clock witness retains
the controlled-multiplier circuit history. Neither solves the native research
problem.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import expm_multiply

from src.backend import (
    ArtifactProvenance, BackendRuleOrigin, CCIROrigin, ExecutionArtifact,
    validate_execution_artifact,
)
from src.prepared_execution import PreparedExecution
from src.observable_execution import ObservableExecution
from src.open_system_execution import (
    ConvergenceSpecification, OpenSystemExecutionSpecification,
    ReferencedReadoutSpecification,
)
from src.shor_order_finding import ShorInstance, digest, multiplier_constants
from src.shor_ccir import SHOR_BACKEND_SPECIFICATION, instance_from_program, shor_program

BACKEND = "cpc.shor.density"
VERSION = "0.1"
MODES = ("collective", "which_x", "circuit_clock")
WITNESS_SCOPES = {
    "collective": "semantic_reference_only",
    "which_x": "which_x_decoherence_negative_control",
    "circuit_clock": "dissipative-circuit-baseline",
}
MAX_DIMENSION = 512


@dataclass(frozen=True)
class ShorModel:
    instance: ShorInstance
    mode: str
    kappa: float
    work_labels: tuple[tuple[int, ...], ...]

    @property
    def witness_scope(self) -> str:
        """Identify the witness role separately from simulated realization status."""
        return WITNESS_SCOPES[self.mode]

    @property
    def steps(self) -> int:
        return len(self.work_labels) - 1

    @property
    def dimension(self) -> int:
        return len(self.work_labels) * self.instance.Q

    def description(self) -> dict:
        return {"instance": asdict(self.instance), "mode": self.mode,
                "kappa": self.kappa, "work_labels": self.work_labels,
                "basis": "clock,x,work_labels[clock][x]",
                "jump_rule": "sqrt(kappa)*sum_x|j+1,x><j,x|",
                "which_x": self.mode == "which_x", "hamiltonian": "zero"}

    @property
    def generator_hash(self) -> str:
        return digest(self.description())


def compile_shor(instance: ShorInstance, *, mode: str = "collective",
                 kappa: float = 1.0) -> ExecutionArtifact:
    """Compile from N,a,Q and fixed rules only; enumerate tiny witness labels."""
    if not isinstance(instance, ShorInstance) or mode not in MODES:
        raise ValueError("invalid Shor instance or witness mode")
    if isinstance(kappa, bool) or not isinstance(kappa, (int, float)) or not math.isfinite(kappa) or kappa <= 0:
        raise ValueError("kappa must be finite and positive")
    steps = instance.Q.bit_length() - 1 if mode == "circuit_clock" else 1
    if (steps + 1) * instance.Q > MAX_DIMENSION:
        raise ValueError("tiny density witness exceeds dimension budget")
    labels = [tuple(1 if mode == "circuit_clock" else 0 for _ in range(instance.Q))]
    if mode == "circuit_clock":
        for j, constant in enumerate(multiplier_constants(instance)):
            labels.append(tuple(y * (constant if (x >> j) & 1 else 1) % instance.N
                                for x, y in enumerate(labels[-1])))
    else:
        labels.append(tuple(instance.response(x) for x in range(instance.Q)))
    model = ShorModel(instance, mode, float(kappa), tuple(labels))
    artifact = ExecutionArtifact(
        topology=model, parameters=("kappa", model.kappa),
        interface=("fourier_bins",),
        metadata={"realization_status": "simulated",
                  "scope": model.witness_scope,
                  "generator_hash": model.generator_hash},
        provenance=(("generator", ArtifactProvenance(
            ccir_origins=(CCIROrigin("constraint", "0"),), backend_rules=(
            BackendRuleOrigin("shor.reachable-clock.v1"),))),))
    validate_execution_artifact(shor_program(instance), artifact,
                               SHOR_BACKEND_SPECIFICATION, ("generator",))
    return artifact


def compile_shor_program(program, *, mode="collective", kappa=1.0):
    """Compile the typed CCIR Shor profile through the same audited rules."""
    return compile_shor(instance_from_program(program), mode=mode, kappa=kappa)


def prepare_shor(artifact: ExecutionArtifact) -> PreparedExecution:
    """Freeze the instance, generator, initial state rule and decoder interface."""
    model = artifact.topology
    if not isinstance(model, ShorModel) or artifact.metadata.get("generator_hash") != model.generator_hash:
        raise ValueError("artifact generator identity mismatch")
    # Recompile to reject mutated/advice-dependent label descriptions.
    canonical = compile_shor(model.instance, mode=model.mode, kappa=model.kappa)
    if canonical != artifact:
        raise ValueError("artifact is not the canonical answer-independent compilation")
    return PreparedExecution(BACKEND, VERSION, model, ("fourier_bins",),
        "continued-fractions-lcm-v1",
        provenance=(("artifact_hash", digest(model.description())),),
        metadata=(("initial_state", "uniform-x,clock-zero"),))


def prepared_hash(prepared: PreparedExecution) -> str:
    """Bind every preparation field to the RFC-0010 record."""
    return digest({"backend_id": prepared.backend_id,
        "backend_version": prepared.backend_version,
        "payload": prepared.payload.description(), "interface": prepared.interface,
        "decoder": prepared.decoder_specification,
        "provenance": prepared.provenance, "metadata": prepared.metadata})


def jump_operators(model: ShorModel) -> tuple[sparse.csr_matrix, ...]:
    """Construct collective or deliberately which-x-resolving Lindblad jumps."""
    q, d = model.instance.Q, model.dimension
    jumps = []
    for stage in range(model.steps):
        groups = [(x,) for x in range(q)] if model.mode == "which_x" else [range(q)]
        for group in groups:
            columns = np.array(tuple(group)) + stage*q
            rows = columns + q
            jumps.append(sparse.csr_matrix((np.full(len(columns), math.sqrt(model.kappa)),
                                           (rows, columns)), shape=(d, d)))
    return tuple(jumps)


def lindbladian(model: ShorModel) -> sparse.csr_matrix:
    """Actual column-vectorized GKSL generator, with zero stabilization term."""
    d = model.dimension
    identity = sparse.eye(d, format="csr")
    generator = sparse.csr_matrix((d*d, d*d), dtype=complex)
    for jump in jump_operators(model):
        loss = jump.getH() @ jump
        generator += sparse.kron(jump.conjugate(), jump, format="csr")
        generator -= 0.5 * (sparse.kron(identity, loss, format="csr")
                           + sparse.kron(loss.T, identity, format="csr"))
    return generator


@dataclass(frozen=True)
class ShorTrajectory:
    prepared: PreparedExecution
    times: tuple[float, ...]
    states: tuple[np.ndarray, ...]
    solver: str = "scipy.sparse.linalg.expm_multiply"


def evolve_shor(prepared: PreparedExecution, times: tuple[float, ...]) -> ShorTrajectory:
    """Evolve rho with exp(t L), never substitute an assumed decay curve."""
    canonical = prepare_shor(compile_shor(prepared.payload.instance,
        mode=prepared.payload.mode, kappa=prepared.payload.kappa))
    if canonical != prepared:
        raise ValueError("noncanonical preparation")
    if not times or any(isinstance(t, bool) or not isinstance(t, (int, float))
                        or not math.isfinite(t) or t < 0 for t in times):
        raise ValueError("times must be nonempty finite nonnegative values")
    if any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("times must strictly increase")
    model = prepared.payload
    vector = np.zeros(model.dimension, complex)
    vector[:model.instance.Q] = 1 / math.sqrt(model.instance.Q)
    initial = np.outer(vector, vector.conjugate()).reshape(-1, order="F")
    generator = lindbladian(model)
    states = tuple(expm_multiply(generator * t, initial).reshape(
        (model.dimension, model.dimension), order="F") for t in times)
    return ShorTrajectory(prepared, tuple(float(t) for t in times), states)


def terminal_block(model: ShorModel, rho: np.ndarray) -> np.ndarray:
    """Project onto the terminal clock without renormalizing."""
    if rho.shape != (model.dimension, model.dimension) or not np.isfinite(rho).all():
        raise ValueError("invalid density matrix")
    return rho[-model.instance.Q:, -model.instance.Q:]


def graph_fidelity(model: ShorModel, rho: np.ndarray) -> float:
    """Unconditional overlap with the uniform coherent modular-response graph."""
    return float(np.real(terminal_block(model, rho).sum()) / model.instance.Q)


def response_class_coherence(model: ShorModel, rho: np.ndarray) -> float:
    """Mean normalized coherence between distinct x with equal responses.

    Returns zero if no repeated response exists in the sampled window.
    """
    block = terminal_block(model, rho)
    labels = np.asarray(model.work_labels[-1])
    mask = (labels[:, None] == labels[None, :]) & ~np.eye(len(labels), dtype=bool)
    if not mask.any():
        return 0.0
    weights = np.sqrt(np.maximum(0, block.diagonal().real)[:, None]
                      * np.maximum(0, block.diagonal().real)[None, :])
    return float(np.abs(block[mask]).sum() / weights[mask].sum()) if weights[mask].sum() else 0.0


def fourier_probabilities(model: ShorModel, rho: np.ndarray) -> np.ndarray:
    """Measure X after inverse Fourier transform and tracing out the work register.

    Subnormalized probabilities include terminal-heralding probability. The
    readout uses simulated phase-referenced Fourier control, not energy shifts.
    """
    block = terminal_block(model, rho)
    labels = np.asarray(model.work_labels[-1])
    reduced = block * (labels[:, None] == labels[None, :])
    q = model.instance.Q
    fourier = np.exp(-2j*np.pi*np.outer(np.arange(q), np.arange(q))/q)/math.sqrt(q)
    probabilities = np.real(np.diag(fourier @ reduced @ fourier.conjugate().T))
    if probabilities.min() < -1e-9 or probabilities.sum() > 1 + 1e-9:
        raise ValueError("invalid measurement probabilities")
    return np.maximum(0, probabilities)


def measure_shor(trajectory: ShorTrajectory, *, shots: int, seed: int) -> ObservableExecution:
    """Sample actual readout probabilities; account for unsuccessful heralds."""
    if type(shots) is not int or not 1 <= shots <= 1_000_000:
        raise ValueError("shots must be in [1,1000000]")
    if type(seed) is not int or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    model = trajectory.prepared.payload
    probabilities = fourier_probabilities(model, trajectory.states[-1])
    probabilities = np.append(probabilities, max(0, 1 - probabilities.sum()))
    probabilities /= probabilities.sum()
    values = np.random.default_rng(seed).choice(model.instance.Q + 1, size=shots, p=probabilities)
    bins = tuple(int(k) for k in values if k < model.instance.Q)
    return ObservableExecution(BACKEND, VERSION, (("fourier_bins", bins),),
        provenance=(("instance_id", model.instance.instance_id),
                    ("prepared_hash", prepared_hash(trajectory.prepared))),
        metadata=(("failed_heralds", shots - len(bins)), ("seed", seed),
                  ("shots", shots), ("time", trajectory.times[-1])))


def execution_specification(prepared: PreparedExecution) -> OpenSystemExecutionSpecification:
    """Reuse RFC-0010 contracts without claiming robust RR or scalable synthesis."""
    model = prepared.payload
    return OpenSystemExecutionSpecification(
        instance_id=model.instance.instance_id,
        prepared_execution_hash=prepared_hash(prepared),
        physical_state_space_id=f"shor.reachable-basis.dimension-{model.dimension}",
        protected_manifold_id="shor.reachable-basis.full-space",
        stabilization_generator_hash=digest({"stabilization": "zero", "dimension": model.dimension}),
        problem_generator_hash=model.generator_hash,
        semantic_terminal_sector_id="shor.terminal-clock.modular-response-graph-subspace",
        realization_status="simulated", conformance_groups=("DC", "OS", "OV"),
        boundary_control=tuple(sorted(asdict(model.instance).items())),
        convergence=ConvergenceSpecification(
            method="adjoint-generator-weighted-clock-penalty",
            penalty_id="H_j=2**(steps-j)-1", admitted_state_domain_id="all-density-matrices-in-reachable-basis",
            gamma=model.kappa / 2, positive_penalty_scale=1.0,
            tolerances=(("numerical_certificate_atol", 1e-9),)),
        readout=ReferencedReadoutSpecification(
            measurement_model_id="ideal-inverse-fourier-and-terminal-herald",
            decoder_id="continued-fractions-lcm-v1",
            metadata=(("robustness", "not-claimed"),)),
        resource_accounting=tuple(sorted({
            "Q": model.instance.Q, "dimension": model.dimension,
            "density_entries": model.dimension**2,
            "jump_count": len(jump_operators(model)),
            "clock_steps": model.steps,
            "decoder_candidate_budget": 4096,
            "compilation": "explicit O(Q*log(Q)) reachable-label enumeration",
            "physical_synthesis": "unknown", "physical_precision": "unknown",
            "efficiency_claim": False, "leakage_in_compressed_model": 0,
            "fourier_readout": "dense O(Q^3) simulator; conventional readout retained",
            "calibration": "ideal numerical phase convention; physical calibration unknown",
        }.items())),
        metadata=(("scope", model.witness_scope),))
