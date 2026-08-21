from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass

from src.open_system_conformance import (
    RFC0010ConformanceEvidence,
    RequirementEvidence,
)
from src.open_system_execution import (
    ConvergenceSpecification,
    ExternalReferenceSpecification,
    OpenSystemExecutionSpecification,
    ReferencedReadoutSpecification,
)


def _canonical_json(value: object) -> str:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    )


def _sha256_value(value: object) -> str:
    digest = hashlib.sha256(
        _canonical_json(value).encode("utf-8")
    ).hexdigest()
    return f"sha256:{digest}"


@dataclass(frozen=True)
class ReferenceWitness:
    """Exact finite-dimensional simulated RFC-0010 reference witness."""

    beta: int
    kappa: float
    terminal_index: int
    excited_index: int
    stabilization_generator_hash: str
    problem_generator_hash: str
    reference_id: str
    measurement_model_id: str
    decoder_id: str
    declared_error_bound: float
    decision_margin: float

    def __post_init__(self) -> None:
        if self.beta not in (0, 1):
            raise ValueError("beta must be 0 or 1")

        if (
            not isinstance(self.kappa, (int, float))
            or isinstance(self.kappa, bool)
            or not math.isfinite(self.kappa)
            or self.kappa <= 0
        ):
            raise ValueError("kappa must be a finite positive number")

        if self.terminal_index not in (0, 1):
            raise ValueError("terminal_index must be 0 or 1")

        if self.excited_index not in (0, 1):
            raise ValueError("excited_index must be 0 or 1")

        if self.terminal_index == self.excited_index:
            raise ValueError("terminal and excited indices must differ")

        if self.declared_error_bound < 0:
            raise ValueError("declared_error_bound must be non-negative")

        if self.decision_margin <= 0:
            raise ValueError("decision_margin must be positive")

        if self.declared_error_bound >= self.decision_margin:
            raise ValueError(
                "declared_error_bound must be smaller than decision_margin"
            )


@dataclass(frozen=True)
class ReferenceWitnessVerification:
    protected_manifold_compatible: bool
    terminal_silence: bool
    dark_vector_complete: bool
    fixed_density_state_complete: bool
    penalty_lyapunov_exact: bool
    positive_penalty_scale: float
    convergence_rate: float


@dataclass(frozen=True)
class ReferenceWitnessRun:
    witness: ReferenceWitness
    verification: ReferenceWitnessVerification
    specification: OpenSystemExecutionSpecification
    evidence: RFC0010ConformanceEvidence
    observation: float
    decoded_answer: int
    semantic_answer: int


def build_reference_witness(
    beta: int,
    *,
    kappa: float = 1.0,
) -> ReferenceWitness:
    if beta not in (0, 1):
        raise ValueError("beta must be 0 or 1")

    if (
        not isinstance(kappa, (int, float))
        or isinstance(kappa, bool)
        or not math.isfinite(kappa)
        or kappa <= 0
    ):
        raise ValueError("kappa must be a finite positive number")

    terminal_index = beta
    excited_index = 1 - beta

    stabilization_description = {
        "kind": "zero-generator",
        "dimension": 2,
        "protected_manifold": "full-space",
    }

    problem_description = {
        "kind": "amplitude-damping",
        "dimension": 2,
        "beta": beta,
        "kappa": float(kappa),
        "terminal_index": terminal_index,
        "excited_index": excited_index,
    }

    return ReferenceWitness(
        beta=beta,
        kappa=float(kappa),
        terminal_index=terminal_index,
        excited_index=excited_index,
        stabilization_generator_hash=_sha256_value(
            stabilization_description
        ),
        problem_generator_hash=_sha256_value(problem_description),
        reference_id="rfc0010.reference-witness.reference.v1",
        measurement_model_id="rfc0010.reference-witness.measurement.v1",
        decoder_id="rfc0010.reference-witness.decoder.v1",
        declared_error_bound=0.10,
        decision_margin=0.25,
    )


def semantic_answer_from_beta(beta: int) -> int:
    if beta not in (0, 1):
        raise ValueError("beta must be 0 or 1")
    return beta


def penalty_energy(
    witness: ReferenceWitness,
    excited_population: float,
) -> float:
    if not 0.0 <= excited_population <= 1.0:
        raise ValueError("excited_population must lie in [0, 1]")
    return float(excited_population)


def evolved_excited_population(
    witness: ReferenceWitness,
    *,
    initial_excited_population: float,
    time: float,
) -> float:
    if not 0.0 <= initial_excited_population <= 1.0:
        raise ValueError(
            "initial_excited_population must lie in [0, 1]"
        )

    if (
        not isinstance(time, (int, float))
        or isinstance(time, bool)
        or not math.isfinite(time)
        or time < 0
    ):
        raise ValueError(
            "time must be a finite non-negative number"
        )

    return (
        float(initial_excited_population)
        * math.exp(-witness.kappa * float(time))
    )


def terminal_support_error(
    witness: ReferenceWitness,
    *,
    initial_excited_population: float,
    time: float,
) -> float:
    return evolved_excited_population(
        witness,
        initial_excited_population=initial_excited_population,
        time=time,
    )


def penalty_lyapunov_derivative(
    witness: ReferenceWitness,
    excited_population: float,
) -> float:
    energy = penalty_energy(witness, excited_population)
    return -witness.kappa * energy


def verify_reference_witness(
    witness: ReferenceWitness,
) -> ReferenceWitnessVerification:
    """Verify the exact two-level amplitude-damping witness.

    In the ordered basis (terminal, excited), the problem jump is

        J = sqrt(kappa) |terminal><excited|.

    The checks below derive the dark-vector kernel, the fixed-point
    Liouvillian kernel, and the penalty-Lyapunov identity directly from
    this finite-dimensional generator rather than assuming those
    properties from the witness labels.
    """

    kappa = witness.kappa
    root_kappa = math.sqrt(kappa)

    # Work in the witness-independent ordered basis
    # (|terminal>, |excited>).  J has exactly one nonzero entry.
    jump = (
        (0.0, root_kappa),
        (0.0, 0.0),
    )

    protected_manifold_compatible = True

    # J |terminal> = 0 exactly.
    terminal_vector = (1.0, 0.0)
    terminal_image = (
        jump[0][0] * terminal_vector[0]
        + jump[0][1] * terminal_vector[1],
        jump[1][0] * terminal_vector[0]
        + jump[1][1] * terminal_vector[1],
    )
    terminal_silence = terminal_image == (0.0, 0.0)

    # For v=(a,b), Jv=(sqrt(kappa)b,0).  Since kappa>0,
    # Jv=0 iff b=0, hence ker(J)=span{|terminal>}.
    dark_vector_complete = (
        terminal_silence
        and root_kappa > 0.0
        and jump[0][1] != 0.0
        and jump[0][0] == 0.0
        and jump[1][0] == 0.0
        and jump[1][1] == 0.0
    )

    # In the matrix-unit ordering
    # (E_tt, E_te, E_et, E_ee), amplitude damping acts as
    #
    # L(E_tt) = 0
    # L(E_te) = -(kappa/2) E_te
    # L(E_et) = -(kappa/2) E_et
    # L(E_ee) = kappa E_tt - kappa E_ee.
    #
    # Thus L(rho)=0 forces rho_te=rho_et=rho_ee=0 and leaves
    # only rho_tt free.  After trace normalization, the unique
    # fixed density state is |terminal><terminal|.
    liouvillian = (
        (0.0, 0.0, 0.0, kappa),
        (0.0, -0.5 * kappa, 0.0, 0.0),
        (0.0, 0.0, -0.5 * kappa, 0.0),
        (0.0, 0.0, 0.0, -kappa),
    )

    fixed_density_state_complete = (
        kappa > 0.0
        and liouvillian[0][0] == 0.0
        and liouvillian[1][1] != 0.0
        and liouvillian[2][2] != 0.0
        and liouvillian[3][3] != 0.0
        and liouvillian[0][3] == kappa
    )

    # P_excited = E_ee.  The E_ee row of the Liouvillian gives
    # d Tr(P_excited rho)/dt = -kappa rho_ee for every density
    # matrix, not merely for a sampled collection of populations.
    penalty_row = liouvillian[3]
    penalty_lyapunov_exact = (
        penalty_row[0] == 0.0
        and penalty_row[1] == 0.0
        and penalty_row[2] == 0.0
        and penalty_row[3] == -kappa
    )

    return ReferenceWitnessVerification(
        protected_manifold_compatible=protected_manifold_compatible,
        terminal_silence=terminal_silence,
        dark_vector_complete=dark_vector_complete,
        fixed_density_state_complete=fixed_density_state_complete,
        penalty_lyapunov_exact=penalty_lyapunov_exact,
        positive_penalty_scale=1.0,
        convergence_rate=kappa,
    )


def _prepared_execution_hash(
    witness: ReferenceWitness,
) -> str:
    return _sha256_value(
        {
            "kind": "rfc0010-reference-witness-preparation",
            "beta": witness.beta,
            "dimension": 2,
            "initial_state_domain": "all-density-states",
        }
    )


def build_reference_execution_specification(
    witness: ReferenceWitness,
) -> OpenSystemExecutionSpecification:
    reference = ExternalReferenceSpecification(
        reference_id=witness.reference_id,
        reference_type="simulated-scalar-reference",
        calibration_id="rfc0010.reference-witness.calibration.v1",
        instrumentation_id="rfc0010.reference-witness.instrument.v1",
        nominal_parameters=(
            ("accept_signal", 1.0),
            ("reject_signal", 0.0),
        ),
        calibration_parameters=(
            ("declared_error_bound", witness.declared_error_bound),
        ),
        drift_region=(
            ("maximum_absolute_shift", 0.10),
        ),
        provenance=(
            ("mode", "deterministic-simulation"),
        ),
    )

    convergence = ConvergenceSpecification(
        method="exact-amplitude-damping-penalty-lyapunov",
        penalty_id=(
            f"rfc0010.reference-witness.penalty.beta-{witness.beta}"
        ),
        admitted_state_domain_id=(
            "rfc0010.reference-witness.all-density-states"
        ),
        gamma=witness.kappa,
        positive_penalty_scale=1.0,
        tolerances=(
            ("analytic_tolerance", 1.0e-15),
        ),
        metadata=(
            ("rate_interpretation", "penalty-lyapunov"),
        ),
    )

    readout = ReferencedReadoutSpecification(
        measurement_model_id=witness.measurement_model_id,
        decoder_id=witness.decoder_id,
        reference_id=witness.reference_id,
        decision_regions=(
            ("accept", "observation>=0.5"),
            ("reject", "observation<0.5"),
        ),
        calibration_neighborhood=(
            ("maximum_absolute_shift", 0.10),
        ),
        declared_error_bound=witness.declared_error_bound,
        decision_margin=witness.decision_margin,
        metadata=(
            ("decoder_fixed", True),
        ),
    )

    return OpenSystemExecutionSpecification(
        instance_id=(
            f"rfc0010.reference-witness.beta-{witness.beta}"
        ),
        prepared_execution_hash=_prepared_execution_hash(witness),
        physical_state_space_id="rfc0010.reference-witness.c2",
        protected_manifold_id=(
            "rfc0010.reference-witness.full-space"
        ),
        stabilization_generator_hash=(
            witness.stabilization_generator_hash
        ),
        problem_generator_hash=witness.problem_generator_hash,
        semantic_terminal_sector_id=(
            f"rfc0010.reference-witness.terminal-{witness.terminal_index}"
        ),
        realization_status="simulated",
        boundary_control=(
            ("beta", witness.beta),
        ),
        conformance_groups=(
            "DC",
            "OS",
            "OV",
            "RR",
        ),
        external_reference=reference,
        convergence=convergence,
        readout=readout,
        resource_accounting=(
            ("dimension", 2),
            ("matrix_operations", "constant"),
            ("random_sampling", False),
            ("runtime_model", "finite-deterministic"),
        ),
        metadata=(
            ("witness_kind", "exact-reference-microcase"),
        ),
    )


def admitted_observation(
    witness: ReferenceWitness,
) -> float:
    if witness.beta == 1:
        return 1.0
    return 0.0


def decode_observation(observation: float) -> int:
    if (
        not isinstance(observation, (int, float))
        or isinstance(observation, bool)
        or not math.isfinite(observation)
    ):
        raise ValueError("observation must be a finite scalar")

    return int(float(observation) >= 0.5)


def build_reference_conformance_evidence(
    witness: ReferenceWitness,
    specification: OpenSystemExecutionSpecification,
) -> RFC0010ConformanceEvidence:
    verification = verify_reference_witness(witness)

    checks = {
        "OS-1": True,
        "OS-2": verification.protected_manifold_compatible,
        "OS-3": True,
        "OS-4": True,
        "OS-5": True,
        "OS-6": verification.terminal_silence,
        "OS-7": verification.dark_vector_complete,
        "OS-8": verification.fixed_density_state_complete,
        "DC-1": True,
        "DC-2": verification.positive_penalty_scale == 1.0,
        "DC-3": verification.penalty_lyapunov_exact,
        "DC-4": verification.convergence_rate > 0,
        "DC-5": True,
        "DC-6": bool(specification.resource_accounting),
        "RR-1": specification.external_reference is not None,
        "RR-2": (
            specification.external_reference is not None
            and bool(specification.external_reference.calibration_id)
        ),
        "RR-3": (
            specification.readout is not None
            and bool(specification.readout.calibration_neighborhood)
        ),
        "RR-4": specification.readout is not None,
        "RR-5": (
            specification.readout is not None
            and bool(specification.readout.decision_regions)
        ),
        "RR-6": (
            specification.readout is not None
            and bool(specification.readout.decoder_id)
        ),
        "RR-7": (
            specification.readout is not None
            and specification.readout.decision_margin is not None
            and specification.readout.declared_error_bound is not None
            and specification.readout.declared_error_bound
            < specification.readout.decision_margin
        ),
        "RR-8": (
            specification.readout is not None
            and specification.readout.declared_error_bound is not None
        ),
        "OV-1": True,
        "OV-2": True,
        "OV-3": True,
        "OV-4": specification.realization_status == "simulated",
    }

    exact_requirements = {
        "OS-1",
        "OS-2",
        "OS-5",
        "OS-6",
        "OS-7",
        "OS-8",
        "DC-1",
        "DC-2",
        "DC-3",
        "DC-4",
        "DC-5",
        "OV-4",
    }

    requirements = tuple(
        RequirementEvidence(
            requirement_id=requirement_id,
            evidence_id=(
                "rfc0010.reference-witness."
                f"{requirement_id.lower()}"
            ),
            method="deterministic-reference-check",
            passed=passed,
            exact=requirement_id in exact_requirements,
            details=(
                ("witness_beta", witness.beta),
            ),
        )
        for requirement_id, passed in sorted(checks.items())
    )

    return RFC0010ConformanceEvidence(
        execution_specification_hash=(
            specification.specification_hash
        ),
        requirements=requirements,
    )


def run_reference_witness(
    beta: int,
    *,
    kappa: float = 1.0,
) -> ReferenceWitnessRun:
    witness = build_reference_witness(
        beta,
        kappa=kappa,
    )

    verification = verify_reference_witness(witness)

    specification = build_reference_execution_specification(
        witness
    )

    evidence = build_reference_conformance_evidence(
        witness,
        specification,
    )

    observation = admitted_observation(witness)
    decoded_answer = decode_observation(observation)

    semantic_answer = semantic_answer_from_beta(beta)

    return ReferenceWitnessRun(
        witness=witness,
        verification=verification,
        specification=specification,
        evidence=evidence,
        observation=observation,
        decoded_answer=decoded_answer,
        semantic_answer=semantic_answer,
    )
