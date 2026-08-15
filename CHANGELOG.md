# Changelog

All notable changes to this project will be documented in this file.

The format follows **Keep a Changelog** and this project follows
**Semantic Versioning**.

---

## [Unreleased]

### P1 Physical FPGA

- added the fixed `build_p1_physical_artifacts.py` entry point;
- atomically retain the accepted iCEBreaker bitstream, physical Verilog,
  RFC-0009 build manifest, and deterministic build report under
  `evidence/p1/physical/`;
- added deterministic, digest-binding artifact-retention tests; and
- preserve the explicit `built-not-programmed` evidence boundary;
- recorded the explicitly approved 2026-08-15 iCEBreaker SRAM programming
  operation and bound its exact guarded-action log to an RFC-0009
  `DeviceProgrammingRecord`;
- added `record_p1_physical_programming.py` with fail-closed validation of the
  fixed target, bitstream digest, USB identity, successful return code, and
  untruncated output; and
- preserve the separate `programmed-awaiting-physical-observation` boundary:
  programming evidence alone is not a physical-execution or semantic claim.
- retained the original user-supplied HEIC observation with camera metadata and
  a content digest, together with separate stimulus and measurement records;
- bound the programming record, prepared execution, admitted observable,
  stimulus, and measurement into an RFC-0009 `PhysicalExecutionEvent`; and
- independently validated the decoded physical result (`1`) against the CCIR
  continuation result (`1`) for the fixed P1 boundary assignment.

### CCIR

- accepted RFC-0002 for generic constraint IR and the CNF front end;
- added immutable CCIR program and constraint containers;
- added the typed CCIR payload contract;
- added the CCIR parity constraint family; and
- added the CCIR clause constraint family.

### Changed

- RC backend now invokes the extracted RC emitter directly.
- Removed the RC backend dependency on `compile_parity_instance()`.
- Added a regression proving the backend does not call the public compiler entry point.
- Removed the obsolete `src/spice_model_accidental_tests.py`.


### Added

- generic parity-constraint representation;
- generic parity-to-ngspice compiler;
- arbitrary-length XOR-expression generation;
- compiler statistics and inspection runner;
- simulator delegation to the generic compiler;
- external JSON parity-benchmark schema;
- benchmark loader and boundary parser;
- independent generic continuation evaluator;
- recursive benchmark discovery;
- complete-boundary benchmark validation;
- permanent chain and cycle benchmarks;
- deterministic chain, cycle, star, and random benchmark generators;
- generated random-system boundary participation;
- full declared-variable coverage for random systems;
- generated benchmark corpus validation;
- benchmark compilation, netlist-size, and simulation-time accounting;
- compiler documentation;
- benchmark-format documentation; and
- generator documentation.

### Validation

- compiler scaling runner with deterministic benchmark generation;
- per-benchmark scaling CSV aggregation;
- candidate-count and behavioral-source growth figures;
- generated-netlist-size figure;
- compilation-time figure;
- ngspice simulation-time figure;
- verified 12-benchmark smoke study;
- 48 of 48 scaling boundary simulations passed; and
- reduced scaling regression integrated into consolidated validation.

- generic compiler output agrees with the simulator compilation path;
- permanent benchmark suite validates all admitted boundary assignments;
- generated corpus validates 52 of 52 boundary simulations;
- generated corpus spans candidate counts from 4 through 256; and
- compiler, benchmark, generator, and legacy engineering regression tests pass.

### Scope

The current parity backend enumerates every internal assignment and therefore
generates `2^k` candidates for `k` internal variables.

The current work establishes a generic, reproducible, answer-independent
compilation and validation framework. It does not claim efficient scaling or a
passive physical implementation.

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
