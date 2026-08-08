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

**Status:** In progress

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

### Current verified generated corpus

- generated benchmark families: 4;
- generated benchmarks: 13;
- boundary simulations: 52;
- passed: 52;
- failed: 0;
- largest variable count: 10;
- largest internal-variable count: 8; and
- largest candidate count: 256.

### Remaining

- compiler scaling runner;
- per-benchmark aggregation;
- candidate-growth figure;
- behavioral-source growth figure;
- netlist-size figure;
- compilation-time figure;
- ngspice simulation-time figure;
- scaling methodology documentation;
- consolidated scaling-validation stage; and
- v0.3 release preparation.

## Version 0.4 — Compiler Scaling and Statistics

**Status:** Planned

- systematic family-by-family size studies;
- repeated compilation measurements;
- repeated simulation measurements;
- growth-model comparison;
- publication-quality scaling figures;
- documented backend limits; and
- archived scaling dataset.

The scaling results will characterize the current exhaustive backend. They will
not be presented as evidence of efficient general-purpose computation.

## Version 0.5 — CNF and DIMACS Front End

**Status:** Planned

- strict DIMACS parser;
- CNF instance representation;
- independent CNF continuation evaluator;
- CNF benchmark schema;
- small canonical SAT families;
- CNF backend compilation; and
- complete reference-to-physical validation.

## Version 0.6 — General Boolean Constraint IR

**Status:** Planned

- typed logical intermediate representation;
- AND constraints;
- OR constraints;
- NOT constraints;
- XOR constraints;
- mixed systems;
- modular compilation; and
- backend-independent validation.

## Version 0.7 — Response-Class and Physical-Backend Validation

**Status:** Planned

- multiple preparation states;
- transient-history variation;
- reset studies;
- response-equivalence statistics;
- passive-network experiments;
- transistor-level models;
- failure classification; and
- hardware-oriented interfaces.

## Version 1.0 — CPC Validation Research Release

**Status:** Planned

- complete reproducibility package;
- archived compiler datasets;
- archived simulation datasets;
- stable benchmark schema;
- stable compiler interface;
- CPC white-paper integration;
- release DOI;
- documented experimental results; and
- external reproduction instructions.
