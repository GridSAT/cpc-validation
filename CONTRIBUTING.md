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

