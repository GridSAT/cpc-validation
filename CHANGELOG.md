# Changelog

All notable changes to this project will be documented in this file.

The format follows **Keep a Changelog** and this project follows
**Semantic Versioning**.

---

## [0.2.0] - 2026-08-05

### Added

- reproducible 1,000-sample Monte Carlo validation;
- deterministic decoder-threshold validation;
- deterministic supply-voltage validation;
- transient waveform extraction;
- deterministic resistance and capacitance timing validation;
- first-order RC theory comparisons;
- deterministic imposed temperature-drift validation;
- quick and full consolidated validation profiles;
- generated Markdown validation report; and
- generated machine-readable validation summary.

### Validation

- ten of ten full-profile validation stages passed;
- all 4,000 Monte Carlo boundary simulations passed;
- all 136 temperature-conditioned boundary simulations passed;
- all deterministic parameter-sweep simulations passed; and
- measured transient timing remained consistent with first-order RC theory.

### Scope

The temperature study uses explicitly imposed linear component-drift
coefficients. It is not a calibrated physical-device temperature model.

## [0.1.0] - 2026-08-05

### Added

- Initial CPC Validation repository.
- Independent reference continuation computation.
- Boundary-response verification framework.
- ngspice transient simulation pipeline.
- Automatic decoder verification against reference continuation.
- Unit test suite.
- Python project structure.
- GitHub citation metadata.
- MIT licensing.
- Initial project documentation.

### Verified

- All four boundary assignments reproduce the expected continuation values.
- Software-to-SPICE validation pipeline completed successfully.

---

## Future

### Planned

- Monte Carlo component variation.
- Passive compiled RC networks.
- Larger constraint systems.
- Automatic circuit generation.
- Statistical validation.
- Hardware demonstrator.
- PCB implementation.
- Coherent carrier experiments.
- Publication-quality benchmark suite.

