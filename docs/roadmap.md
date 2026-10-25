# CPC Validation Development Roadmap

## Version 0.1 — Reference Validation Baseline

**Status:** Completed

- independent XOR continuation evaluator;
- four-condition reference table;
- generated ngspice model;
- fixed voltage decoder;
- regression tests; and
- machine-readable baseline data.

## Version 0.2 — Engineering Robustness Validation

**Status:** Completed and released as `v0.2.0`

- reproducible Monte Carlo validation;
- deterministic decoder-threshold sweep;
- deterministic supply-voltage sweep;
- transient waveform extraction;
- resistance and capacitance timing studies;
- first-order RC theory comparisons;
- imposed temperature-drift study;
- consolidated quick and full validation profiles;
- Markdown validation report; and
- machine-readable validation summary.

The temperature stage uses declared linear component-drift coefficients. It is
a parameter-sensitivity study rather than a calibrated physical-device model.

## Version 0.3 — Generic Parity Compiler and Benchmark Framework

**Status:** Completed and released as `v0.3.0`

### Completed

- generic parity constraint representation;
- generic parity-instance validation;
- arbitrary-length XOR-expression generation;
- generic parity-to-ngspice compiler;
- compiler statistics;
- simulator delegation to the generic compiler;
- JSON benchmark schema;
- benchmark loader;
- boundary-assignment parser;
- independent generic continuation evaluator;
- recursive benchmark discovery;
- complete-boundary benchmark validation;
- permanent XOR, chain, and cycle benchmarks;
- deterministic chain generator;
- deterministic cycle generator;
- deterministic star generator;
- seeded random generator;
- full declared-variable coverage for random systems;
- generated-corpus validation;
- benchmark resource accounting; and
- extensive compiler and benchmark regression tests.

### Historical verified generated corpus

- generated benchmark families: 4;
- generated benchmarks: 13;
- boundary simulations: 52;
- passed: 52;
- failed: 0;
- largest variable count: 10;
- largest internal-variable count: 8; and
- largest candidate count: 256.

The released milestone also includes deterministic scaling aggregation,
resource figures, methodology documentation, and consolidated validation.

## Version 0.4 — Compiler Scaling and Statistics

**Status:** Completed and incorporated into `v0.5.0`

- systematic family-by-family size studies;
- repeated compilation measurements;
- repeated simulation measurements;
- growth-model comparison;
- publication-quality scaling figures;
- documented backend limits; and
- archived scaling dataset.

The scaling results characterize the current exhaustive backend. They are not
presented as evidence of efficient general-purpose computation.

## Version 0.5 — CNF and DIMACS Front End

**Status:** Completed and released as `v0.5.0`

- strict DIMACS parser;
- CNF instance representation;
- independent CNF continuation evaluator;
- CNF benchmark schema;
- small canonical SAT families;
- CNF backend compilation; and
- complete reference-to-physical validation;
- RFC-0003 through RFC-0009 execution, qualification, and evidence contracts;
- qualified RC, Digital, and FPGA backends; and
- first concrete P1 physical FPGA execution evidence.

## RFC-0010 — Driven-Dissipative Open-System Execution

**Status:** Completed and released as `v0.6.0`

RFC-0010 is accepted as the software/evidence architecture for
driven-dissipative open-system execution and referenced readout.

The released RFC-0010 baseline establishes an executable software specification,
conformance validation, and a simulated reference witness. It does not establish
a physical superconducting, bosonic, or other driven-dissipative CPC execution
substrate.

## Bounded UP5K/Pico Classical Hardware Milestone

**Status:** Completed and frozen at its declared three-record scope (2026-10-25)

The [Area-v3/Pico physical evidence](shor/classical-up5k-physical-milestone.md)
independently matches seeded oracle records 2, 68 and 194, covering take=1,
take=0 and nonzero numerical/PRNG output. The frozen milestone includes exact
six-frame CRC/word verification and a read-only public evidence audit.

Record 217's unseeded status divergence and five physically unmatched
error-path records remain open. This bounded closure does not claim complete
physical corpus conformance, quantum measurement, Shor or advantage.
Any physical extension requires separate authorization.

Two parallel workstreams continue:

- [WP-B1](shor/wp-b1-conformance-checklist.md): implement and independently
  qualify the complete bosonic/vendor-abstraction software chain; not yet PASS.
- [Alice & Bob co-design preparation](shor/alice-bob-collaboration-brief.md):
  unsent draft for WP-B2/WP-B3 compatibility and known-phase N0; vendor
  capabilities, apparatus/profile and raw-data contracts require confirmation.

## Current Research Milestone — CPC-Shor / N0

**Status:** In progress; pre-physical software boundary reached

Completed within the current finite/software research scope:

- finite RFC-0010 Shor/order-finding prototype;
- typed modular-response and modular-node models;
- finite open-system and coherence-sensitive witness studies;
- historical single-node, two-node and cleanup/locality research documentation,
  separate from the executable software published in this release;
- independent order/factor validation;

- bounded P3 models/compiler, inference/analysis and host filtering;
- P4 deterministic EXACT/bounded-error contracts and retained-record replay;
- guarded P4 acquisition adapters, diagnostic-state construction and per-trial
  artifact scoring; and
- bounded P4 classical host C simulation.
- N0 physical-profile and raw-record contracts;
- calibration and device-adapter boundaries;
- finite bosonic and effective logical-measurement models;
- synthetic-device and statistical rehearsal;
- fault-injection and claim-firewall coverage;
- statistical-decision and repeated held-out synthetic rehearsal;
- physical-preregistration freeze and readiness gates; and
- deterministic N0 controller protocol, RTL, and synthesis checks.

Current physical boundary:

- integrated physical N0 apparatus: not established;
- physical N0 validation: not performed;
- physical N0 acquisition: not performed;
- physical N0 execution authorization: not granted;
- N0 FPGA programming authorization: not granted; and
- native scalable CPC-Shor: not established.

The immediate next milestone is to define and bind a specific physical N0
apparatus/profile while preserving the preregistered acquisition and claim
boundaries.

The complete historical autonomous P4 workflow and deferred population
registry/reducer/supervisor modules are outside this publication. Their
possible future publication would require its own dependency and provenance
audit; it would not authorize historical execution or establish calibration
acceptance.

## N0 Physical Integration

**Status:** Planned / apparatus-definition stage

Required before a physical N0 claim:

- identify a specific integrated apparatus implementing the required bosonic
  logical state and CPC measurement interaction;
- bind physical preparation, control, calibration, timing, acquisition, and raw
  record interfaces;
- establish independently auditable measurement/timebase access;
- freeze numerical preregistration parameters before acquisition;
- qualify deterministic controller/acquisition behavior independently of the
  quantum/CPC dynamics;
- retain negative controls and multiplicity-corrected statistical decision
  rules; and
- perform physical acquisition only after explicit authorization.

A successful N0 experiment would validate the specified physical measurement
primitive. It would not by itself establish full Shor, scalable quantum
computing, or computational advantage.

## Native CPC-Shor Research

**Status:** Research

Further work must address:

- multi-node/native composition;
- physical locality of the required interactions;
- coherent cleanup and environment distinguishability;
- scalable synthesis of modular arithmetic dynamics;
- Liouvillian/mixing behavior;
- physical resource accounting;
- control, calibration, energy, precision, and readout costs;
- fault/error models; and
- scaling evidence sufficient to support any future native-efficiency claim.

Finite simulator behavior is not used as a substitute for these physical and
resource obligations.

## Additional CPC Substrates and Front Ends

**Status:** Planned

- additional typed constraint families;
- AND, OR, NOT, XOR, and mixed constraint systems;
- graph-oriented execution substrates;
- additional physical execution substrates;
- modular compilation;
- broader backend qualification;
- expanded benchmark collections; and
- expanded backend-independent validation coverage.

## Future CPC Validation Research Release

**Status:** Planned

- complete reproducibility package;
- archived compiler, simulation, and physical-validation datasets;
- stable benchmark and execution interfaces;
- broader cross-substrate evidence;
- cryptographic signing and attestation;
- CPC research-program integration;
- release DOI;
- documented experimental results; and
- external reproduction instructions.
