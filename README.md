# CPC Validation

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![ngspice](https://img.shields.io/badge/ngspice-42%2B-blue.svg)](https://ngspice.sourceforge.io/)
[![Status](https://img.shields.io/badge/status-research%20prototype-orange.svg)](#project-status)

Reference implementation and SPICE validation framework for **C-Parity
Computing (CPC)**, a constraint-to-carrier architecture for physical
computation.

CPC Validation independently computes logical continuation values and verifies
that a physical model reproduces those values through preparation, evolution,
restricted readout, and semantic decoding.

The current release establishes a reproducible
**reference → SPICE → measurement → decoder → validation** pipeline using
ngspice. It provides the baseline for Monte Carlo robustness studies, compiled
physical networks, hardware demonstrators, and later coherent-carrier
experiments.

Every reported validation result is intended to be reproducible from a clean
repository checkout using the documented software versions.

## Validation pipeline

<p align="center">
  <img src="figures/pipeline.svg" width="100%" alt="CPC validation pipeline">
</p>

---

## Quick start

    git clone https://github.com/GridSAT/cpc-validation.git
    cd cpc-validation

    python3 -m venv .venv
    source .venv/bin/activate

    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

    python -m pytest -q
    python run_spice.py

Expected SPICE result:

    CPC ngspice boundary-response verification

    x0=0 x3=0 expected=0 vout=0.000000 V decoded=0 PASS
    x0=0 x3=1 expected=1 vout=4.999950 V decoded=1 PASS
    x0=1 x3=0 expected=1 vout=4.999950 V decoded=1 PASS
    x0=1 x3=1 expected=0 vout=0.000000 V decoded=0 PASS

    Complete continuation table: PASS

---

## Contents

- [Why this repository exists](#why-this-repository-exists)
- [CPC overview](#cpc-overview)
- [Validation functions](#validation-functions)
- [Current benchmark](#current-benchmark)
- [Reference continuation table](#reference-continuation-table)
- [Current SPICE result](#current-spice-result)
- [Current scope](#current-scope)
- [Installation](#installation)
- [Running the project](#running-the-project)
- [Generic parity compiler](#generic-parity-compiler)
- [External JSON benchmarks](#external-json-benchmarks)
- [Reproducible benchmark generation](#reproducible-benchmark-generation)
- [Compiler scaling study](#compiler-scaling-study)
- [Tests](#tests)
- [Repository structure](#repository-structure)
- [Validation principles](#validation-principles)
- [Project status](#project-status)
- [Roadmap](#roadmap)
- [Related CPC research](#related-cpc-research)
- [Citation](#citation)
- [Contributing](#contributing)
- [License](#license)
- [Organization](#organization)

---

## Why this repository exists

Circuit simulators establish the electrical behavior of a model, but they do
not independently establish that the measured response has the intended
logical meaning.

CPC Validation separates:

1. the mathematical reference function;
2. the generated physical model;
3. physical evolution;
4. restricted measurement;
5. semantic decoding; and
6. independent comparison.

This separation makes it possible to test whether a physical implementation
reproduces a represented continuation function without using the independently
computed answers during compilation.

---

## CPC overview

CPC treats physical computation as a complete and independently validated
pipeline:

    constraint instance
            |
            v
    representation compiler
            |
            v
    physical program
            |
            v
    preparation and evolution
            |
            v
    restricted readout
            |
            v
    semantic decoder
            |
            v
    continuation value

For an admitted instance $X$, let

$$
\mathrm{Eval}_X:
\mathcal{B}_X
\longrightarrow
\mathcal{E}_X
$$

be an independently defined continuation function over the admitted boundary
or interface conditions $b\in\mathcal{B}_X$.

A physical realization is validated by requiring

    Pr[Decode_X(M_X(U_X,tau_X(p), b)) = Eval_X(b) | p ~ Prep_X(b)]
        >= 1 - epsilon_X

The compiler and physical program may depend on the instance and the admitted
boundary condition. The independently computed continuation values remain
reserved for validation.

A full architectural treatment is provided in
[`docs/architecture.md`](docs/architecture.md).

---

## Validation functions

The repository separates five operational functions.

### 1. Reference evaluation

Compute the exact continuation value directly from the logical constraint
system.

### 2. Physical-model generation

Generate an ngspice circuit from the admitted instance and boundary values.

### 3. Physical evolution

Simulate the transient electrical response.

### 4. Restricted readout and decoding

Read a designated output node and apply a fixed decoding rule.

### 5. Independent validation

Compare the decoded physical response with the independently computed
continuation value.

The detailed validation methodology is documented in
[`docs/validation.md`](docs/validation.md).

---

## Current benchmark

The initial benchmark is the XOR constraint system

$$
x_0\oplus x_1\oplus x_2=0,
$$

$$
x_1\oplus x_2\oplus x_3=1.
$$

The boundary variables are $x_0$ and $x_3$. The internal variables are
$x_1$ and $x_2$.

Eliminating the shared quantity $x_1\oplus x_2$ gives

$$
x_0\oplus x_3=1.
$$

The continuation function is therefore

$$
\mathrm{Eval}(x_0,x_3)=x_0\oplus x_3.
$$

A boundary assignment receives continuation value $1$ exactly when the
residual system has at least one completion of its internal variables.

---

## Reference continuation table

| `x0` | `x3` | Continuation value | Internal completions |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 |
| 0 | 1 | 1 | 2 |
| 1 | 0 | 1 | 2 |
| 1 | 1 | 0 | 0 |

The machine-readable reference data are stored in:

- [`baselines/continuation_table.csv`](baselines/continuation_table.csv)
- [`baselines/xor_reference.json`](baselines/xor_reference.json)

The exact internal completions are generated by
[`src/reference.py`](src/reference.py).

---

## Current SPICE result

Run:

    python run_spice.py

Expected output:

    CPC ngspice boundary-response verification

    x0=0 x3=0 expected=0 vout=0.000000 V decoded=0 PASS
    x0=0 x3=1 expected=1 vout=4.999950 V decoded=1 PASS
    x0=1 x3=0 expected=1 vout=4.999950 V decoded=1 PASS
    x0=1 x3=1 expected=0 vout=0.000000 V decoded=0 PASS

    Complete continuation table: PASS

### Initial RC demonstrator

<p align="center">
  <img src="figures/rc-demo.svg" width="80%" alt="Initial CPC RC demonstrator">
</p>

The present SPICE model uses a controlled behavioral response followed by an RC
output stage. It verifies the complete
reference-to-SPICE-to-readout-to-decoder execution path.

---

## Current scope

The current release establishes that the repository can:

- define the logical constraint system independently of the circuit;
- enumerate its exact continuation table;
- generate boundary-conditioned ngspice netlists;
- execute transient simulation in ngspice batch mode;
- extract a restricted analog output;
- decode that output with a fixed rule;
- validate every admitted boundary condition;
- report complete continuation-table agreement; and
- run automated regression tests.

The behavioral response element is the initial verification baseline. The next
engineering stage replaces direct response realization with a network generated
from the constraint description under the anti-embedding rule.

The current result therefore validates the complete execution and measurement
pipeline. It provides the starting point for:

- parameter variation;
- Monte Carlo analysis;
- compiled physical networks;
- response-class invariance tests;
- hardware validation; and
- later coherent-carrier studies.

---

## Installation

### System requirements

The current development environment uses:

- Ubuntu Linux;
- Python 3.12 or later;
- ngspice 42 or later;
- NumPy;
- SciPy;
- pandas;
- matplotlib;
- pytest; and
- PySpice for supporting circuit construction and analysis.

The principal simulation path invokes ngspice directly in batch mode.

### Install Ubuntu packages

    sudo apt update

    sudo apt install -y \
        git \
        python3 \
        python3-venv \
        python3-pip \
        ngspice \
        libngspice0-dev

Verify ngspice:

    ngspice --version

### Clone the repository

    git clone https://github.com/GridSAT/cpc-validation.git
    cd cpc-validation

### Create the Python environment

    python3 -m venv .venv
    source .venv/bin/activate

### Install dependencies

    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

For exact reproduction of the tested environment:

    python -m pip install -r requirements-lock.txt

---

## Running the project

### Print the exact reference continuation table

    python -m src.reference

Expected logical output:

    CPC reference continuation table

    Constraints:
      x0 XOR x1 XOR x2 = 0
      x1 XOR x2 XOR x3 = 1

    Boundary variables: x0, x3

    x0=0 x3=0 -> Eval=0, completions=0: []
    x0=0 x3=1 -> Eval=1, completions=2: [(0, 0, 0, 1), (0, 1, 1, 1)]
    x0=1 x3=0 -> Eval=1, completions=2: [(1, 0, 1, 0), (1, 1, 0, 0)]
    x0=1 x3=1 -> Eval=0, completions=0: []

### Run the SPICE verification

    python run_spice.py

The command:

1. enumerates the four admitted boundary assignments;
2. computes the independent continuation value;
3. generates one ngspice netlist for each assignment;
4. invokes ngspice in batch mode;
5. reads the final output voltage;
6. applies the fixed threshold decoder;
7. compares the decoded result with the independent reference value; and
8. reports the complete validation result.

---

## Consolidated validation

Run the reduced development profile:

```bash
python validate.py --quick
```

Run the complete reproducibility profile:

```bash
python validate.py --full
```

Both commands generate:

- `reports/validation_report.md`
- `reports/validation_summary.csv`
- profile-specific CSV files under `results/`
- profile-specific figures under `results/`

The full profile executes:

1. the complete automated test suite;
2. independent reference continuation generation;
3. nominal four-condition SPICE validation;
4. transient waveform and RC timing validation;
5. the reproducible 1,000-sample Monte Carlo study;
6. the decoder-threshold sweep;
7. the supply-voltage sweep;
8. the resistance and RC timing sweep;
9. the capacitance and RC timing sweep; and
10. the imposed temperature-drift sweep.

The verified full-profile validation (5 August 2026) completed with:

| Quantity | Result |
|---|---:|
| Validation stages | 10 |
| Stages passed | 10 |
| Stages failed | 0 |
| Automated tests | 85 passed |
| Monte Carlo parameter samples | 1,000 |
| Monte Carlo boundary simulations | 4,000 |
| Temperature points | 34 |
| Temperature-conditioned boundary simulations | 136 |
| Overall validation | PASS |

Generated reports are reproducible build artifacts and are intentionally
excluded from normal Git history.

---

## External JSON benchmarks

The `v0.3-dev` branch supports externally defined parity-constraint
benchmarks.

Compile and simulate one admitted boundary assignment:

```bash
python run_benchmark.py \
    benchmarks/default_xor.json \
    --boundary 'x0=0,x3=1'
```

Validate every boundary assignment for every JSON benchmark discovered under
the benchmark directory:

```bash
python validate_benchmarks.py benchmarks/
```

Explicit benchmark files may also be supplied:

```bash
python validate_benchmarks.py \
    benchmarks/default_xor.json \
    benchmarks/parity_chain_5.json
```

For each admitted boundary assignment, the validator records:

- the independently computed continuation value;
- the internal-completion count;
- the decoded SPICE response;
- the output voltage;
- the constraint and variable counts;
- the candidate count;
- the generated-netlist size;
- the compilation time; and
- the simulation time.

The benchmark schema and anti-embedding contract are documented in
[`docs/benchmarks.md`](docs/benchmarks.md).

The current compiler enumerates all internal assignments and uses behavioral
sources for candidate validity and existential aggregation. This milestone
establishes generic instance loading, compilation, simulation, and independent
validation. It does not claim scalable passive-network realization.

---

## Generic parity compiler

The `v0.3-dev` branch introduces a generic compiler for Boolean parity
constraint systems.

A parity constraint is represented as data:

```python
ParityConstraint(
    variables=(0, 1, 2),
    parity=0,
)
```

A complete instance declares:

- one or more parity constraints;
- the admitted boundary variables; and
- physical-interface parameters such as supply voltage, resistance,
  capacitance, and transient duration.

Every variable appearing in a constraint but not declared as a boundary
variable is treated as an internal variable.

The compilation path is:

```text
parity instance
        |
        v
internal-assignment enumeration
        |
        v
candidate-validity sources
        |
        v
existential aggregation
        |
        v
restricted RC interface
        |
        v
ngspice netlist
```

The generic compiler is implemented in:

- `src/compiler.py`

Inspect the built-in reference instance:

```bash
python run_compiler.py
```

The simulator delegates netlist generation to this generic compiler. The
compiler is therefore the single source of truth for parity-to-SPICE
translation.

The current backend is intentionally explicit and auditable. It enumerates all
internal assignments and uses behavioral sources for candidate validity and
existential aggregation. For `k` internal variables, it generates `2^k`
candidate assignments.

This establishes a generic constraint-compilation interface. It does not claim
polynomial scaling or a passive physical realization.

## Reproducible benchmark generation

The development branch includes a deterministic benchmark generator:

```bash
python generate_parity_benchmarks.py \
    --family chain \
    --variables 4:10:2 \
    --output-directory benchmarks/generated/chain
```

Supported families are:

- `chain`;
- `cycle`;
- `star`; and
- `random`.

The `--variables` argument accepts either one size or an inclusive range:

```text
8
4:10:2
```

A reproducible random family can be generated with:

```bash
python generate_parity_benchmarks.py \
    --family random \
    --variables 4:8:2 \
    --constraints 4 \
    --arity 3 \
    --seed 20260806 \
    --output-directory benchmarks/generated/random
```

Generated random benchmarks guarantee that every declared variable occurs in
the constraint system. This keeps requested variable counts, compiled variable
counts, internal-variable counts, and candidate counts aligned.

The generated corpus is a reproducible build artifact and is excluded from Git.
It can be regenerated and validated with:

```bash
python validate_benchmarks.py benchmarks/generated/
```

The verified development corpus currently contains:

| Quantity | Result |
|---|---:|
| Generated benchmark families | 4 |
| Generated benchmarks | 13 |
| Boundary simulations | 52 |
| Passed | 52 |
| Failed | 0 |
| Largest variable count | 10 |
| Largest internal-variable count | 8 |
| Largest candidate count | 256 |
| Overall result | PASS |

The generator is implemented in:

- `generate_parity_benchmarks.py`

Its regression tests are in:

- `tests/test_benchmark_generator.py`

## Compiler scaling study

The current exhaustive parity backend can be characterized across generated
benchmark families with:

```bash
python run_scaling_study.py \
    --families chain,cycle,star,random \
    --variables 4:8:2 \
    --seed 20260806
```

The study generates each benchmark deterministically, independently evaluates
every admitted boundary assignment, compiles the corresponding ngspice
netlists, executes the simulations, applies the fixed decoder, and aggregates
one result row per benchmark.

The verified smoke profile contains:

| Quantity | Result |
|---|---:|
| Families | 4 |
| Variable counts | 4, 6, 8 |
| Benchmarks | 12 |
| Boundary simulations | 48 |
| Passed | 48 |
| Failed | 0 |
| Largest candidate count | 64 |
| Overall result | PASS |

The study records:

- variable and constraint counts;
- internal-variable count;
- candidate count;
- behavioral-source count;
- generated-netlist size;
- compilation time;
- ngspice simulation time;
- output-voltage range; and
- complete validation success.

Generated figures:

- `figures/scaling_candidates.png`;
- `figures/scaling_sources.png`;
- `figures/scaling_netlist_size.png`;
- `figures/scaling_compile_time.png`; and
- `figures/scaling_simulation_time.png`.

The current backend enumerates all internal assignments. The scaling results
therefore characterize an explicit exhaustive backend and do not constitute a
claim of polynomial scaling.

See [`docs/scaling.md`](docs/scaling.md) for the full methodology,
measurements, interpretation, and limitations.

---

## Tests

Run all tests:

    python -m pytest -q

The current test suite verifies the logical reference model.

The test program will be extended to cover:

- continuation-evaluator correctness;
- baseline-data consistency;
- generated-netlist structure;
- ngspice integration;
- Monte Carlo tolerance experiments;
- anti-embedding compliance;
- response-class invariance; and
- regression comparisons.

---

## Repository structure

```text
cpc-validation/
├── README.md
├── LICENSE
├── CITATION.cff
├── CHANGELOG.md
├── CONTRIBUTING.md
├── .gitignore
├── pytest.ini
├── requirements.txt
├── requirements-lock.txt
│
├── run_spice.py
├── run_compiler.py
├── run_benchmark.py
├── validate_benchmarks.py
├── generate_parity_benchmarks.py
├── run_monte_carlo.py
├── run_threshold_sweep.py
├── run_supply_sweep.py
├── run_resistance_sweep.py
├── run_capacitance_sweep.py
├── run_temperature_sweep.py
├── run_transient_smoke.py
├── validate.py
│
├── baselines/
│   ├── continuation_table.csv
│   └── xor_reference.json
│
├── benchmarks/
│   ├── default_xor.json
│   ├── parity_chain_5.json
│   ├── parity_cycle_6.json
│   └── generated/                 # reproducible, ignored corpus
│
├── docs/
│   ├── architecture.md
│   ├── benchmarks.md
│   ├── compiler.md
│   ├── generator.md
│   ├── validation.md
│   └── roadmap.md
│
├── figures/
│   ├── pipeline.svg
│   ├── rc-demo.svg
│   └── validation figures
│
├── src/
│   ├── __init__.py
│   ├── benchmark_io.py
│   ├── compiler.py
│   ├── generic_reference.py
│   ├── reference.py
│   ├── spice_model.py
│   └── transient_analysis.py
│
└── tests/
    ├── test_benchmark_generator.py
    ├── test_benchmark_io.py
    ├── test_compiler.py
    ├── test_generic_reference.py
    ├── test_monte_carlo.py
    ├── test_reference.py
    ├── test_spice_model.py
    └── parameter-sweep tests
```

Generated netlists, reports, result CSV files, validation figures written under
`results/`, and generated benchmark corpora are intentionally excluded from
normal Git history.

## Validation principles

### Independent reference evaluation

The continuation function is derived from the logical constraints independently
of the physical model.

The reference evaluator and the SPICE implementation remain separate validation
layers.

### Anti-embedding

Reference answers and precomputed completion tables are reserved for independent
validation.

A physical compiler may use:

- the admitted instance description;
- the admitted boundary condition;
- fixed family-wide compilation rules; and
- calibration data obtained independently of the continuation answers.

It may not use the independently computed continuation value when constructing
the physical program.

### Restricted readout

The physical response is extracted through a specified observable rather than
through complete reconstruction of all internal state variables.

In the current baseline, the restricted observable is the final voltage at the
designated output node.

### Fixed decoder

The decoder is selected before validation and remains fixed across the admitted
boundary conditions.

In the current benchmark, the output voltage is decoded using a fixed voltage
threshold.

### Response-class invariance

Later releases will test whether distinct initial conditions, transient
histories, parameter perturbations, or microscopic states assigned to one
response class produce the same decoded response.

Validation therefore extends beyond truth-table agreement. It also tests
whether physically distinct realizations preserve the same admitted semantic
response.

### Complete resource accounting

Validation will report:

- compilation cost;
- physical-program size;
- preparation cost;
- convergence time;
- readout cost;
- decoding cost;
- component precision;
- calibration cost;
- reset overhead;
- repeated-run statistics; and
- failure and non-convergence rates.

---

## Project status

**Released baseline:** v0.2.0

**Development branch:** `v0.3-dev`

**Status:** Generic parity compiler and benchmark framework under active
development

### Released v0.2.0 research prototype

The immutable v0.2.0 release provides:

- the independently evaluated XOR continuation benchmark;
- nominal ngspice validation;
- transient waveform extraction;
- Monte Carlo robustness validation;
- decoder-threshold validation;
- supply-voltage validation;
- resistance and capacitance timing validation;
- imposed temperature-drift validation; and
- ten-stage consolidated quick and full validation profiles.

### Current v0.3 development milestone

Completed on `v0.3-dev`:

- generic parity-constraint representation;
- generic parity-to-ngspice compiler;
- single-source compiler delegation from the simulator;
- arbitrary-length XOR-expression generation;
- compilation statistics;
- external JSON benchmark schema;
- benchmark loader and boundary parser;
- generic independent continuation evaluator;
- complete-boundary benchmark validation;
- recursive benchmark discovery;
- permanent chain and cycle benchmark families;
- deterministic benchmark generation;
- generated chain, cycle, star, and random families;
- full declared-variable coverage for generated random systems;
- generated corpus validation; and
- compiler and benchmark regression tests.

The current backend remains exhaustive in the number of internal variables and
uses behavioral sources. The present work establishes correctness,
reproducibility, generality of instance representation, and measurable compiler
output. It does not establish scalable passive-network realization.

## v0.4 Compiler Architecture

The v0.4 development line separates logical compilation from physical
netlist emission.

```text
ParityInstance
      |
      v
compile_parity_instance_to_ir()
      |
      v
IRProgram
      |
      v
compile_ir_to_rc()
      |
      v
emit_parity_rc_netlist()
      |
      v
RC/ngspice netlist
```

`src/ir_compiler.py` constructs the backend-independent intermediate
representation. `src/backends/rc.py` consumes that representation and
invokes the extracted RC emitter directly.

The RC backend no longer calls the legacy public
`compile_parity_instance()` entry point. This preserves a distinct
backend boundary while maintaining byte-compatible RC/netlist output.

## Roadmap

### Version 0.1 — Reference validation baseline

**Status:** completed

- independently evaluated XOR continuation function;
- generated ngspice model;
- fixed decoder; and
- complete four-condition validation.

### Version 0.2 — Engineering robustness validation

**Status:** completed and released

- Monte Carlo robustness validation;
- deterministic threshold and supply sweeps;
- resistance and capacitance timing studies;
- imposed temperature-drift study;
- transient waveform extraction;
- RC-theory comparison; and
- consolidated quick and full validation reports.

### Version 0.3 — Generic parity compiler and benchmark framework

**Status:** in progress

Completed:

- generic parity constraint representation;
- generic parity-to-SPICE compiler;
- external JSON benchmark schema;
- independent generic reference evaluator;
- recursive benchmark discovery;
- complete-boundary validation;
- permanent chain and cycle benchmarks;
- deterministic chain, cycle, star, and random generators;
- generated corpus validation;
- compiler resource accounting;
- formal compiler scaling study;
- per-benchmark scaling CSV aggregation;
- candidate-growth figure;
- behavioral-source growth figure;
- netlist-size figure;
- compilation-time figure;
- simulation-time figure;
- reduced scaling regression in consolidated validation; and
- scaling methodology documentation.

Current verified scaling milestone:

- four benchmark families;
- variable counts 4, 6, and 8;
- 12 generated scaling benchmarks;
- 48 boundary simulations;
- 48 passed;
- 0 failed; and
- candidate counts from 4 through 64.

Remaining:

- size-10 characterization across all supported families;
- repeated timing trials and statistical intervals;
- final v0.3 release validation;
- release notes; and
- v0.3.0 tag preparation.

### Version 0.4 — Compiler scaling and statistics

**Status:** planned

- systematic topology-family scaling studies;
- compiler-output growth characterization;
- simulation-cost characterization;
- publication-quality scaling figures;
- documented limits of the exhaustive backend; and
- consolidated scaling report.

### Version 0.5 — CNF and DIMACS front end

**Status:** planned

- DIMACS parser;
- CNF instance representation;
- independent CNF continuation evaluator;
- CNF-to-physical-backend compilation;
- small canonical SAT benchmarks; and
- complete boundary-validation workflow.

### Version 0.6 — General Boolean constraints

**Status:** planned

- mixed AND, OR, NOT, and XOR constraints;
- typed intermediate representation;
- backend-independent logical modules; and
- additional physical backends.

### Version 0.7 — Response-class and physical-backend validation

**Status:** planned

- multiple initial states;
- transient-history variation;
- reset experiments;
- response-equivalence statistics;
- passive or transistor-level backend experiments; and
- failure-mode classification.

### Version 1.0 — CPC validation research release

**Status:** planned

- complete reproducibility package;
- archived simulation data;
- compiler and backend documentation;
- release DOI;
- CPC white-paper integration;
- documented experimental results; and
- external reproduction instructions.

See [`docs/roadmap.md`](docs/roadmap.md) for the detailed development plan.

## Related CPC research

This repository is an engineering companion to the C-Parity Computing research
program, which develops:

- configuration identity and quotient dynamics;
- canonical quotient-state representations;
- exact semantic carriers;
- physical carrier-computing architectures;
- response quotients;
- bounded-arithmetic exactness criteria;
- conditional unprovability of carrier separation; and
- representation-relative physical computation.

The repository supplies the staged validation framework through which these
formal ideas can be translated into testable physical models.

Persistent identifiers for the CPC papers will be added after publication on
arXiv and Zenodo.

---

## Citation

Citation metadata are provided in [`CITATION.cff`](CITATION.cff).

Until a release DOI is available, cite the repository as:

> Karim Daghbouche. *CPC Validation: Reference Implementation and SPICE
> Validation Framework for C-Parity Computing*. GridSAT Stiftung, 2026.  
> https://github.com/GridSAT/cpc-validation

A Zenodo DOI will be added to a future archived release.

---

## Contributing

Research and engineering contributions are welcome.

Before proposing a substantial change, open a GitHub issue describing:

- the proposed physical or computational model;
- its relation to the CPC validation contract;
- its anti-embedding status;
- its expected validation data;
- its resource-accounting requirements; and
- the accompanying tests and documentation.

All contributions should preserve reproducibility and maintain a clear
separation between reference evaluation, physical-model generation, physical
execution, readout, decoding, and validation.

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## License

Copyright © 2026 GridSAT Stiftung and contributors.

This project is released under the [MIT License](LICENSE).

---

## Organization

**GridSAT Stiftung**  
Georgstr. 11  
30159 Hannover  
Germany

GridSAT Stiftung is a German non-profit foundation established on 1 July 2021.

**Repository**

https://github.com/GridSAT/cpc-validation

**CPC research program**

https://gridsat.eth.link
