# Contributing to CPC Validation

Thank you for your interest in contributing to CPC Validation.

The objective of this repository is to provide a scientifically rigorous,
reproducible validation framework for Constraint Physical Computing (CPC). Every
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

Every contribution, including documentation-only changes, must execute the
complete consolidated reproducibility profile before commit:

    .venv/bin/python validate.py --full

This includes the complete pytest suite, independent reference table, nominal
SPICE check, transient smoke test, engineering sweeps, benchmark validation
and compiler-scaling regression. All twelve steps must pass. Preserve its
logs, summary and the exact tested tree at every commit boundary.

For development, targeted checks, pytest and run_spice.py may assist diagnosis;
they do not replace the complete profile. Do not commit when it is failing,
incomplete or unexecuted.

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

**Atomic rule: one logically coherent, independently validatable change per commit, with the complete validation suite green at every commit boundary. Commits are concise and descriptive; no bundling unrelated work merely to reduce commit count.**

Every commit MUST represent one coherent, independently reviewable and independently validatable change. Before creating **each commit**, the contributor MUST run the complete repository validation suite against the exact prospective committed content and achieve an entirely green result. This includes documentation-only, metadata-only and release-related changes. After commit creation, verify that the commit contains exactly the tested content and leaves a valid, complete-suite-green repository state. Targeted or subsystem tests are useful preliminary checks but never replace the complete suite.

If the clean baseline or prospective commit fails the complete suite, no commit may be created. Record the precise failure and resolve it without suppressing, weakening, skipping or altering scientific acceptance tests to manufacture a PASS. Toolchain prerequisites and test environment changes must be recorded. If an obligatory suite cannot be executed, the commit boundary is **not qualified**.

Unrelated implementation, validation, documentation, metadata, and release changes MUST remain separate commits unless technically inseparable for an independently validatable repository state. Changes to normative architecture SHOULD contain only the normative change and strictly necessary registration or index changes. Tests and implementation may share a commit only when needed for one coherent independently validating behavior change.

Generated evidence, unpublished research material, and quarantined artifacts MUST NOT enter a commit unless the commit explicitly freezes them as part of a declared and reviewed public evidence or release scope. Check sensitive content before publishing raw physical device logs. Do not amend frozen originals or change oracle expectations.

Commit messages MUST be concise, descriptive and reflect the single logical purpose. Maintain per-commit validation records with exact commands, exit codes, versions, and source/commit identifiers. Before any push or release also perform the documented isolated publication snapshot and GitHub Pages/source checks; preserve every tracked parent file.

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
