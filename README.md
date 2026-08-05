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
    ├── run_spice.py
    │
    ├── baselines/
    │   ├── continuation_table.csv
    │   └── xor_reference.json
    │
    ├── docs/
    │   ├── architecture.md
    │   ├── validation.md
    │   └── roadmap.md
    │
    ├── figures/
    │   ├── pipeline.svg
    │   └── rc-demo.svg
    │
    ├── src/
    │   ├── __init__.py
    │   ├── reference.py
    │   └── spice_model.py
    │
    └── tests/
        ├── test_reference.py
        └── test_spice.py

Files shown above may be introduced progressively as the validation framework
develops.

---

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

**Version:** 0.1.0

**Status:** Research prototype

**Completed**

- independent continuation evaluator;
- complete four-condition XOR reference table;
- ngspice transient validation;
- fixed output decoder;
- automated logical regression tests;
- reproducible dependency metadata;
- project documentation and citation metadata;
- reproducible 1,000-sample Monte Carlo validation; and
- deterministic 41-point decoder-threshold sweep.

**Next milestone**

- deterministic supply-voltage, resistance, and capacitance sweeps.

The current SPICE implementation is intentionally small and auditable. It
provides the reference execution pipeline from which compiled-network
experiments will be developed.

---

## Roadmap

### Version 0.1 — Reference validation baseline

**Status: completed**

- exact continuation evaluator;
- XOR boundary benchmark;
- generated ngspice netlists;
- transient output decoding;
- automated tests;
- machine-readable reference data;
- reproducible four-condition validation.

### Version 0.2 — Engineering robustness validation

**Status: in progress**

Completed:

- reproducible 1,000-sample Monte Carlo validation;
- 4,000 successful boundary simulations;
- deterministic 41-point decoder-threshold sweep;
- detailed and summary CSV output;
- decoder success-rate figure;
- decoder-margin figure.

Remaining:

- deterministic supply-voltage sweep;
- deterministic resistance sweep;
- deterministic capacitance sweep;
- temperature sweep;
- consolidated validation report.

### Version 0.3 — Compiled network model

**Status: planned**

- replace direct behavioral response realization;
- generate network topology from constraint data;
- generate component settings from fixed compilation rules;
- enforce the anti-embedding contract;
- validate multiple parity instances;
- audit generated netlists for answer independence.

### Version 0.4 — Response-class validation

**Status: planned**

- multiple initial states;
- different transient histories;
- power-up sequence variation;
- parameter perturbation classes;
- repeated reset experiments;
- response-equivalence statistics;
- failure-mode classification.

### Version 0.5 — Hardware demonstrator

**Status: planned**

- component selection;
- PCB or programmable analog implementation;
- measurement protocol;
- calibration protocol;
- physical reset procedure;
- comparison with SPICE predictions;
- hardware-to-reference validation.

### Version 1.0 — CPC validation research release

**Status: planned**

- complete reproducibility package;
- archived simulation data;
- archived hardware data;
- release DOI;
- CPC white-paper integration;
- documented experimental results;
- external reproduction instructions.

See [`docs/roadmap.md`](docs/roadmap.md) for the detailed development plan.

---

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
