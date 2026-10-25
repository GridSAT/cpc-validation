# CPC Validation Architecture

CPC Validation implements the compilation, execution and evidence boundaries
specified by [RFC-0001 through RFC-0010](design/README.md). It supports three
qualified general execution-backend families: **RC, Digital and FPGA**, each
within its declared capability and qualification scope. CPC-Shor/N0 is a
research and validation line; it is not a fourth qualified general backend.

## Canonical execution and validation boundary

```text
Source instance / frontend
  -> canonical CCIR
  -> backend compilation
  -> ExecutionArtifact
  -> preparation
  -> PreparedExecution
  -> execution and restricted observation
  -> ObservableExecution
  -> fixed decoding
  -> independent semantic validation
```

The source instance supplies constraints and admitted boundary inputs, not
precomputed answers. Frontends lower supported source forms into the canonical
Core Constraint Intermediate Representation (CCIR). Backend compilation uses
CCIR and globally fixed backend rules to construct an `ExecutionArtifact`:
topology, parameters, interface, metadata and machine-resolvable provenance.
The compiler must not receive independent continuation values or truth tables.

Preparation produces `PreparedExecution`, including the admitted executable
payload, interface and decoder specification. Execution consumes that prepared
state. Restricted observation yields `ObservableExecution`, which contains
admitted observations and provenance, not semantic reference answers. A fixed
decoder interprets those observations. Independent validation compares the
decoded result with the mathematical specification outside the execution path.

The relevant software contracts are `src/ccir.py`, `src/backend.py`,
`src/prepared_execution.py` and `src/observable_execution.py`. The legacy
parity-oriented IR remains part of the implemented compiler history; it does
not replace CCIR as the canonical cross-backend contract. See
[compiler documentation](compiler.md) for the implemented lowering paths.

## Three general backend families

| Family | Execution/observation scope | Boundary |
|---|---|---|
| RC | Generated RC/SPICE models, transient observations and fixed decoding | Circuit simulation and RC engineering sweeps are backend-specific evidence, not the universal execution pipeline. |
| Digital | Deterministic digital realization and admitted digital observations | Qualification applies to the declared supported constraint domain. |
| FPGA | FPGA compilation and simulation, with a separate physical evidence lifecycle | Simulation, synthesis, programming, physical observation and semantic agreement are distinct claims. |

[RFC-0005 through RFC-0008](design/README.md) define cross-backend comparison,
benchmark validation, reproducibility and qualification. Backend agreement
supports the tested semantic comparison; it does not substitute for independent
reference validation or prove physical realization.

## Physical FPGA evidence: RFC-0009

RFC-0009 adds a lifecycle for physical build, programming, execution,
measurement and evidence conformance. Build inputs and constraints, tool
identities, bitstream hashes, programming records, observation records and
independent validation must be bound to the declared device and profile.

The retained [P1 physical FPGA evidence](../evidence/p1/physical/README.md)
records programming and a restricted static LED observation on a Lattice
iCE40 UltraPlus Breakout Board. Its RFC-0009 conformance and semantic result
remain bounded by the recorded observation and provenance trust boundary.
That evidence is not a superconducting/bosonic CPC experiment and does not
qualify a scientific ADC/DAC acquisition chain.

## Parallel bounded classical UP5K/Pico milestone

The [Area-v3/Pico milestone](shor/classical-up5k-physical-milestone.md) records
three independently audited physical seeded probability/PRNG oracle matches.
It is a completed bounded classical component, separate from P1's static
observation, general backend qualification and the N0 bosonic apparatus.
Its SEED/PROB output is not a quantum Fourier observation. Known error-path
exceptions and host-log/electrical trust boundaries remain explicit.

## Open-system architecture: RFC-0010

RFC-0010 is accepted and implemented as a driven-dissipative open-system
software and evidence architecture. It describes stabilization/protected
manifold structure, problem-dependent dynamics, convergence and leakage
obligations, admitted observation and referenced readout. Evidence must identify
the requirement, method, model and realization scope to which it applies.

A finite software witness, numerical certificate or conformance result does not
establish a physical open-system realization. The current repository evidence
does not establish physical superconducting, bosonic or open-system CPC
execution. Robust referenced readout, native synthesis, physical resource
scaling and advantage require their own evidence; they do not follow from
acceptance of the RFC.

The bounded dyadic layer includes P3 models/compiler, inference/analysis and
host filtering, followed by P4 deterministic reconstruction, distinct EXACT
and bounded-error contracts, retained-record replay, guarded acquisition
adapters, diagnostic-state construction and per-trial artifact scoring.
The P4 C kernel is classical host simulation. These libraries do not constitute
the complete historical autonomous P4 workflow or a stochastic acceptance
result.

## CPC-Shor and N0 research line

The [CPC-Shor overview](shor/README.md) separates finite model validation,
historical research checkpoints and current N0 preparation. Finite arithmetic,
open-system witnesses, phase-sensitive coherence controls, observation and
independent order/factor validation support the tested finite software/model
scope. They do not establish native scalable Shor or computational advantage.

N0 is a narrower physical measurement-validation milestone for a known or
prepared physical eigenphase. Its present stack includes software schemas,
synthetic rehearsal, finite/effective models, independent reduction,
preregistration machinery and controller boundary checks. These are pre-physical
results. The current apparatus concept retains a stabilized cat/bosonic carrier
and parity-phase rotation plus fixed-axis logical measurement; physical
integration and required numerical device parameters remain unresolved.
See [N0 status](shor/n0-status.md) for the authoritative public summary.

The N0 FPGA/controller is deterministic control/acquisition only. It may
sequence admitted controls and preserve timestamped raw records once the
required interfaces are implemented and qualified. It is not the bosonic state,
CPC interaction, semantic inference engine or truth/order/factor oracle.
`theta_truth` or equivalent semantic answer information must not enter the
controller as execution input. Published N0 controller RTL simulation and synthesis checks validate software
and toolchain boundaries. They do not establish N0 place-and-route, timing
closure, bitstream generation, programming or physical acquisition, and do not
authorize those actions.

Current boundaries remain: software freeze candidate **yes**; physical N0
validated **no**; physical execution authorized **no**; FPGA programming
authorized **no**; physical acquisition performed **no**. The next scientific
step is to define the physical N0 apparatus and profile. See the
[native claim boundary](shor/native-boundary.md).

## Provenance and claim separation

Hashes identify bytes; they do not by themselves authenticate a physical event.
Keep compiler conformance, execution conformance, semantic correctness,
qualification, physical evidence and statistical acceptance separate. Record
scope, failures, uncertainty, resource costs and independent validation alongside
the result. Historical failed runs and separately labeled recovery analyses
retain their original identities and classifications.

The [validation methodology](validation.md) explains these checks. The
[roadmap](roadmap.md) distinguishes established software/evidence architecture
from open physical and scaling work.
