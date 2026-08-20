# Contributing to CPC Validation

Thank you for your interest in contributing to CPC Validation.

The objective of this repository is to provide a scientifically rigorous,
reproducible validation framework for C-Parity Computing (CPC). Every
contribution should improve correctness, reproducibility, engineering
quality, or documentation.

---

# Guiding Principles

Contributions should prioritize:

- Scientific correctness
- Reproducibility
- Transparency
- Deterministic validation
- Independent verification
- Maintainability

Performance improvements are welcome, but correctness always takes
precedence.

---

# Development Workflow

1. Fork the repository.

2. Create a feature branch.

   git checkout -b feature/my-improvement

3. Implement the desired changes.

4. Run the complete validation suite.

5. Commit with a descriptive message.

6. Push your branch.

7. Open a Pull Request.

---

# Repository Structure

src/
    Reference implementation
    SPICE validation
    Circuit generation
    Simulation utilities

tests/
    Unit tests
    Regression tests

docs/
    Project documentation

figures/
    Diagrams
    Architecture figures

baselines/
    Reference validation data

---

# Coding Style

Please follow these guidelines:

- Python 3.12+
- Follow PEP 8
- Use type hints whenever practical
- Document all public functions
- Keep functions small and focused
- Prefer readability over cleverness
- Avoid unnecessary dependencies

---

# Testing

Every contribution must successfully execute

    python -m pytest

Simulation-related changes should additionally execute

    python run_spice.py

and reproduce the expected continuation table.

No Pull Request should introduce failing tests.

---

# Validation Requirements

Changes affecting the validation pipeline should preserve:

- Correct continuation computation
- Deterministic decoding
- Successful ngspice execution
- Passing regression tests
- Reproducible results

Whenever possible, include quantitative validation data.

---

# Commit Discipline

Each commit MUST represent one coherent, independently reviewable change.

A commit MUST leave the repository in a valid state and MUST NOT introduce
failing tests. Unrelated implementation, validation, documentation, metadata,
and release changes SHOULD be committed separately whenever they can be
validated independently.

Before committing, contributors MUST run the validation required for the
affected subsystem. Before a release, the complete validation suite MUST be
run.

A commit that changes normative architecture SHOULD contain only the normative
change and any strictly necessary index or registration update. Implementation,
conformance validation, regression tests, explanatory documentation, release
metadata, and release notes SHOULD follow in separate commits when each forms
an independently validatable unit.

Generated evidence, unpublished research material, and quarantined artifacts
MUST NOT enter a commit unless the commit explicitly freezes them as part of a
declared public evidence or release scope.

Commit messages SHOULD be concise and descriptive and SHOULD state the purpose
of the change.

---

# Commit Messages

Use concise and descriptive commit messages.

Examples:

    Add Monte Carlo validation

    Improve SPICE parser

    Refactor circuit generator

    Fix decoder threshold

    Update documentation

---

# Pull Requests

A Pull Request should include:

- Motivation
- Summary of changes
- Validation performed
- Expected impact
- Known limitations (if any)

Small, focused Pull Requests are preferred.

---

# Reporting Issues

Bug reports should include:

- Operating system
- Python version
- ngspice version
- Reproduction steps
- Expected behavior
- Observed behavior
- Console output
- Screenshots if applicable

---

# Scientific Contributions

New physical models should include:

- Theoretical motivation
- Mathematical description
- Implementation details
- Validation methodology
- Comparison against existing validation
- Reproducibility instructions

Where appropriate, include references to supporting publications.

---

# Documentation

Documentation is considered part of the software.

Please update documentation whenever functionality changes.

Relevant files include:

- README.md
- docs/architecture.md
- docs/validation.md
- docs/roadmap.md
- CHANGELOG.md

---

# Versioning

This repository follows Semantic Versioning.

Versions are tagged as

MAJOR.MINOR.PATCH

Examples:

0.1.0
0.2.0
1.0.0

---

# License

By contributing to CPC Validation, you agree that your contributions
will be distributed under the terms of the MIT License.

Copyright © 2026 GridSAT Stiftung and contributors.


---

# Contributing Benchmarks

Parity benchmarks are stored as JSON files under `benchmarks/`.

A contributed benchmark must contain only:

- schema version;
- benchmark name;
- optional description;
- boundary-variable indices; and
- parity constraints.

It must not contain:

- expected continuation values;
- precomputed completion counts;
- satisfying assignments;
- expected SPICE voltages;
- decoded results; or
- cached truth tables.

Every contributed benchmark must:

1. conform to the schema documented in `docs/benchmarks.md`;
2. load through `src.benchmark_io.load_parity_benchmark`;
3. include every declared boundary variable in at least one constraint;
4. include a clear description of its topology or intended purpose;
5. pass complete-boundary validation;
6. include regression tests when it introduces a new structural family; and
7. preserve the anti-embedding separation between compilation and reference
   evaluation.

Validate a contributed benchmark with:

```bash
python validate_benchmarks.py path/to/benchmark.json
```

# Contributing Benchmark Generators

A benchmark generator must be deterministic for fixed input parameters.

Generators must:

- emit schema-compatible JSON;
- expose an explicit seed for random generation;
- ensure every declared variable occurs in the generated constraint system;
- reject parameter combinations that cannot satisfy coverage requirements;
- avoid writing expected answers or completion data;
- include reproducibility tests;
- include structural validation tests; and
- document the intended topology and size parameters.

Generated corpora should normally remain excluded from Git unless a release
explicitly freezes them as archival data.

# Contributing Compiler Backends

A compiler backend must preserve the separation between:

- instance description;
- boundary assignment;
- physical-model generation;
- physical execution;
- measurement;
- decoding; and
- independent reference comparison.

A backend may not receive independently computed continuation values or
completion tables.

Compiler contributions should include:

- a clearly defined input contract;
- deterministic output for fixed inputs;
- model-size statistics;
- resource accounting;
- answer-independence tests;
- backend-specific regression tests; and
- explicit scope and scaling limitations.
