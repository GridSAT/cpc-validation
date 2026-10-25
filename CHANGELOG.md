# Changelog

All notable changes to this project will be documented in this file.

The format follows **Keep a Changelog** and this project follows
**Semantic Versioning**.

---

## [Unreleased]

### Bounded classical UP5K/Pico physical milestone

- Froze the completed Area-v3/Pico classical probability/PRNG milestone:
  seeded physical oracle records 2, 68 and 194, with independently verified
  six response frames, 132 words, six request/response CRC pairs and 18 snapshots.
- Added a privacy-reviewed numerical evidence subset, exact fixture/source pins,
  a read-only verifier and tampering tests; original sealed reports preserved.
- Retained unseeded record 217's 0022/0002 divergence and five unmatched physical
  error-path records. No complete-corpus physical conformance claim.
- Made atomic, fully validated commits mandatory, including documentation.
- Documented outstanding WP-B1 conformance and an unsent Alice & Bob co-design
  brief. Physical N0, native Shor, scalable quantum computation and advantage
  remain unproven; P1 and other historical evidence retain their scope.

### Bounded Shor and dyadic software

- Added the finite RFC-0010 Shor prototype, modular-response and modular-node
  models, open-system witnesses, decoding and independent validation.
- Added the bounded P3 Python foundation, inference/analysis, host-native
  filtering, and guarded execution/provenance infrastructure.
- Added P4 deterministic reconstruction and distinct EXACT/bounded-error
  certification and risk contracts.
- Added retained-record replay, guarded acquisition adapters, deterministic
  diagnostic-state construction and retained-artifact per-trial calibration
  scoring.
- Added the bounded P4 classical host C simulation kernel and portable tests.

### N0 pre-physical software

- Added profile/raw-record contracts, models, calibration/device boundaries,
  synthetic rehearsal, statistics, faults, reduction, claim gates and
  preregistration/readiness infrastructure.
- Added N0 controller RTL, host-side protocol/synthesis software and simulation
  tests.
- Retained the pre-physical software-freeze-candidate boundary. Physical N0
  validation, physical execution, FPGA programming and physical acquisition
  remain unestablished or unauthorized as specified by the readiness gates.

### Documentation and historical research

- Added current software-scope, N0-readiness and native-boundary documentation.
- Published historical prototype, single-node, two-node and cleanup/locality
  notes with explicit archival framing and preserved scientific bodies.
- Historical research-note publication does not publish the uncommitted
  two-node/cleanup executable workflows or their archived results.

### Exclusions and claim boundary

This release does not publish the complete historical autonomous P4 workflow,
the deferred calibrated-population/evidence/reducer/supervisor modules, or the
historical P4 launchers. Per-trial scoring is not a calibration PASS.
Zero local errors per phase class remains an acceptance criterion, not an
observed result established by this release.

E5-v1 remains consumed, non-retryable and INCOMPLETE_OR_INVALID_GRID. E5-R1
remains a post hoc recovery analysis and does not establish an E5 grid PASS.

Host-native C is classical host simulation. Software, RTL and toolchain
validation establish neither physical N0 validation nor native quantum
implementation, physical TTS, scalable QC or computational advantage.

## [0.6.0] - 2026-08-21

### Architecture

- accepted RFC-0010 for driven-dissipative open-system execution and
  referenced readout;
- separated stabilization dynamics from the instance-dependent problem
  generator;
- specified admissibility, terminal silence, fixed-point, convergence,
  referenced-readout, calibration, and evidence obligations; and
- integrated RFC-0010 into the combined RFC-0001 through RFC-0010
  architectural baseline.

### Implementation

- added the RFC-0010 execution-specification model;
- added independent RFC-0010 conformance validation;
- added a simulated reference witness exercising the declared execution and
  readout contracts; and
- documented atomic commit discipline and corrected CPC project terminology.

### Validation

- complete repository regression: **1010 tests passed**;
- RFC-0010 execution-specification tests: **PASS**;
- RFC-0010 conformance tests: **PASS**; and
- RFC-0010 reference-witness tests: **PASS**.

### Scope

This release establishes an accepted and executable software specification for
RFC-0010 and a simulated reference witness. It does not establish physical
superconducting, bosonic, driven-dissipative, or other open-system execution.
The RFC-0009 P1 FPGA evidence remains the repository's concrete physical
execution milestone.

## [0.5.0] - 2026-08-16

### Architecture

- accepted RFC-0002 through RFC-0009 on top of the RFC-0001 baseline;
- established canonical CCIR parity and clause constraints with CNF lowering;
- introduced the execution-backend compilation contract, explicit
  `ExecutionArtifact`, `PreparedExecution`, and `ObservableExecution` states;
- enforced answer independence, provenance, restricted observation, fixed
  decoding, and independent semantic validation;
- added cross-backend equivalence, benchmark reproducibility, deterministic
  backend qualification, and persistent acceptance evidence;
- qualified the RC, Digital, and FPGA backends; and
- defined RFC-0009 physical-execution evidence, build provenance, device
  programming, execution-event binding, and substrate-profile conformance.

### P1 Physical FPGA

- retained the accepted iCEBreaker bitstream, physical Verilog, RFC-0009 build
  manifest, deterministic build report, and normalized nextpnr timing report;
- recorded the explicitly approved 2026-08-15 SRAM programming operation and
  bound its guarded-action log to an RFC-0009 `DeviceProgrammingRecord`;
- retained the original HEIC observation, camera metadata, fixed stimulus,
  restricted LED measurement, admitted observable, and
  `PhysicalExecutionEvent`;
- constructed the concrete RFC-0009 `PhysicalExecutionEvidence` envelope and
  verified every external digest and `fpga.physical-device.v1` requirement;
- independently decoded result `1` and validated it against CCIR reference
  result `1` for the fixed `x0=0, x3=1` boundary assignment; and
- added a deterministic physical-evidence index with artifact roles, digests,
  claim dimensions, trust boundary, and non-programming reproduction order.

### Validation

- complete regression: **899 tests passed**;
- RFC-0008 tri-backend corpus: **16 benchmarks and 64 boundary cases passed**;
- concrete P1 RFC-0009 evidence conformance: **PASS**;
- P1 physical semantic validation: **PASS**; and
- non-programming evidence regeneration reproduced the frozen directory
  byte-for-byte.

### Scope

This release establishes a concrete, auditable physical FPGA execution under
the declared RFC-0009 trust boundary. It makes no claim of authenticated
capture, measured Fmax, efficient asymptotic scaling, complexity-class change,
or superiority over conventional computation.

## [0.5.0-frontend.1] - 2026-08-06

### Added

- canonical backend-independent CCIR containers and typed payloads;
- parity and clause constraint families;
- strict DIMACS parsing and CNF source representation;
- parity-to-CCIR and CNF-to-CCIR lowering; and
- independent assignment-semantic equivalence tests.

### Validation

- **359 automated tests passed**; and
- existing parity SPICE validation remained passing.

## [0.3.0] - 2026-08-05

### Added

- generic parity-to-ngspice compilation and independent continuation semantics;
- deterministic benchmark generation, discovery, loading, and validation;
- compiler, netlist-size, and simulator resource accounting; and
- scaling reports and figures for the admitted benchmark families.

### Scope

The parity backend enumerates every internal assignment and therefore produces
`2^k` candidates for `k` internal variables. The release did not claim
efficient general-purpose scaling.

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

- additional physical execution substrates;
- authenticated evidence and signed manifests;
- broader benchmark and scaling studies;
- independently replicated physical experiments; and
- publication-quality research artifacts.
