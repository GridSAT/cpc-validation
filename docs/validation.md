# Validation Methodology

CPC validation separates compilation, execution, observation, decoding,
independent semantics and evidence. The methodology applies across the declared
RC, Digital and FPGA backend domains and the separately scoped RFC-0010
research models. A voltage threshold is an RC readout choice, not a universal
validation rule. See the [architecture](architecture.md) and
[accepted RFC index](design/README.md).

## Compiler validation

Check frontend lowering and canonical CCIR structure, backend capability
admission, deterministic compilation and complete artifact provenance. Generated
elements must resolve to admitted CCIR data or fixed backend rules. Reject
unsupported domains and embedded semantic answers. Compilation and preparation
must not consume independently computed continuation tables, expected orders,
factors or truth phases.

## Execution and observation validation

Check the `ExecutionArtifact` to `PreparedExecution` boundary and execution
against the prepared interface. `ObservableExecution` must contain only admitted
observations and provenance. Decode with the fixed declared decoder; do not
recover answers from forbidden internal state or tune decoding after seeing the
reference. Substrate-specific failures, incomplete observations and invalid
records must remain visible rather than becoming silent successful trials.

RC tests include SPICE/transient and threshold behavior. Digital and FPGA tests
use their admitted digital observations. Physical acquisition requires additional
device, calibration, timing and raw-record evidence.

## Independent semantic validation

Compare decoded output with a separately implemented mathematical reference for
the admitted instance and tested boundary assignments. For the original parity
example, eliminating internal variables yields `x0 XOR x3 = 1`; that reference
must not be supplied to the compiler or execution backend.

Correctness statements must specify the tested domain, decoder, comparison and
failure handling. Agreement between backends is a useful cross-check but is not
an independent truth source. A structural conformance PASS is not automatically
a semantic or scientific PASS.

## Qualification and reproducibility

RFC-0005 through RFC-0008 distinguish cross-backend equivalence, benchmark
coverage, reproducibility and backend qualification. Report the supported
constraint families, interfaces, corpus, complete-boundary coverage, resource
limits and qualification evidence. The three qualified general families are
RC, Digital and FPGA. CPC-Shor/N0 is not a fourth qualified general backend.

## Physical evidence validation: RFC-0009

Verify the physical lifecycle bindings: prepared artifact, build and constraint
inputs, tools, bitstream, device/programming record, execution event, measurement,
restricted observation and independent semantic result. Evidence conformance,
byte integrity and physical observation each have their own scope.

The retained [P1 records](../evidence/p1/physical/README.md) support a physical
FPGA programming event and restricted static LED observation under their stated
trust boundary. They do not establish quantum/CPC dynamics or scientific
measurement-chain performance. Programming, acquisition and calibration are
separate actions and are not implied by a software test result.

## Open-system validation: RFC-0010

Validate the declared open-system specification, stabilization/problem-dynamics
separation, protected manifold, convergence and leakage obligations, admitted
observation and requirement-specific evidence. Distinguish declarations,
finite-model numerical checks and independently supported physical claims.
A finite-time residual does not prove uniqueness or general mixing. Referenced
readout robustness requires an explicit reference/calibration uncertainty
contract; it must not be inferred from magnitude agreement alone.

RFC-0010 acceptance and software conformance do not establish physical
superconducting/bosonic/open-system CPC execution. Current evidence remains
within the declared finite software/model scope.

### P3/P4 software evidence

Validate deterministic software boundaries separately from stochastic
scientific acceptance and physical validation. The published P4 library covers
arithmetic/reconstruction, exact and bounded-error contracts, retained-record
replay, guarded acquisition interfaces, diagnostic-state construction,
per-trial artifact scoring and bounded classical host simulation.

EXACT certification and bounded-error certification have distinct guarantees.
For BE, correctness of every reconstructed denominator implies that their LCM
divides the order; the modular return check then establishes equality on that
correct-reconstruction event. Outside it, wrong accepted order remains a
bounded semantic-error event. The stated risk bounds
P(accept AND wrong order), not automatically P(wrong order | accept).
BE does not require factorization of the candidate order.

Diagnostic truth/sector labels must remain separate from operational
inference. Per-trial scoring is not aggregate calibration acceptance.
Zero local errors per phase class is an acceptance criterion, not an observed
result established by software tests. Retained-record replay does not reopen
a consumed execution identity.

The C kernels perform classical host simulation. Neither those tests nor N0
RTL/protocol/synthesis checks establish physical realization, physical TTS,
native quantum implementation, hardware scaling or computational advantage.

## Finite Shor validation

The [Shor research line](shor/README.md) tests finite modular arithmetic,
phase-sensitive response-class coherence, open-system models, observation,
decoding and independent order/factor validation. Positive references and
negative controls have distinct scopes. Report tested instances, model caps,
preparation assumptions, failures, abstentions and resource costs.

Preserve historical execution status separately from later recovery evidence.
In particular, E5-v1 remains consumed, non-retryable and
`INCOMPLETE_OR_INVALID_GRID`; accepted E5-R1 is a deterministic post hoc recovery
of frozen S8192 records. The future-lineage reducer fix corrects JSON-semantic
comparison only. Recovery does not retroactively establish an E5 grid PASS.
None of these finite results establishes native scalable Shor, scalable quantum
computing or computational advantage.

## N0 pre-physical and physical methodology

[N0](shor/n0-status.md) targets physical CPC measurement for a known/prepared
physical eigenphase. The software stack checks schemas, calibration/device
adapter boundaries, immutable raw records, claim separation, finite models,
synthetic measurement/rehearsal, statistical decisions and preregistration gates.
Synthetic data and controller simulations must remain labeled as such.

Before physical trials, define the integrated apparatus, device-to-model mapping,
signal/reference chain, calibration uncertainty, exact estimator inputs,
phase classes, sample sizes, numerical acceptance/power/error criteria, resource
caps and abort rules. Seal those decisions before records are acquired. Retain
failed attempts; do not silently retry, replace, postselect or relax thresholds.
Known-phase diagnostics remain separate from operational inference and evidence.

The controller accepts deterministic control/acquisition inputs, not
`theta_truth`, order, factors or equivalent answers. Physical raw records must
come from the qualified physical chain. FPGA programming and physical N0
acquisition remain unauthorized. Current software readiness does not establish
physical validation; the next step is physical apparatus/profile definition.

## Regression and archival discipline

Use the repository environment for current regression:

```bash
.venv/bin/python -m pytest
```

Run targeted subsystem tests before the full suite. Simulation-related changes
also require the SPICE continuation check:

```bash
.venv/bin/python run_spice.py
```

Capture the exact commands, exit status, test counts, relevant tool/source hashes
and scope. Classify a nonzero result before any rerun. Never change scientific
tolerances just to obtain PASS. Historical release counts (including 899 at
v0.5.0/P1 and 1010 at v0.6.0) remain historical; current counts must come from a
fresh run. Tests do not authorize new stochastic experiments or physical trials.

Frozen source paths, failed evidence, recovery identities and archives must remain
traceable. Documentation links and the actual GitHub Pages deployment source are
part of the pre-push/release gate. No release or push should proceed while that
gate is unresolved.

Publication validation must also use an isolated snapshot of the exact
committed parent plus only the proposed publication paths. Preserve every
tracked parent file, including retained P1 evidence. Do not overlay a populated
results directory, untracked historical binaries or unrelated working files.
Clear PYTHONPATH and PYTHONHOME, disable user-site imports, and verify that
repository modules resolve inside the snapshot.

Record Python/dependency and relevant C, SPICE, RTL-simulation and synthesis
tool versions. Run the full suite in that isolated environment; classify any
failure before retrying. A documentation-only change does not itself require
historical acquisition, acceptance replay or a separate SPICE continuation run.

## Historical RC engineering evidence

The following sections retain the verified RC sweep reports unchanged. Their
voltages, component values, timings and decoder criteria apply to those specific
historical RC experiments, not to every CPC backend or N0 apparatus.

---

# Verified Decoder-Threshold Sweep

A deterministic decoder-threshold sweep was completed on 5 August 2026
for the behavioral-source RC validation baseline.

The decoder threshold was varied from 0.5 V through 4.5 V in increments
of 0.1 V. All four admitted boundary conditions were simulated at every
threshold value.

The fixed physical parameters were:

- supply voltage: 5.0 V;
- output resistance: 10.0 kOhm; and
- output capacitance: 1.0 uF.

The result was:

| Quantity | Result |
|---|---:|
| Threshold points | 41 |
| Boundary simulations | 164 |
| Passed | 164 |
| Failed | 0 |
| Overall success rate | 100.000000% |
| Fully passing tested interval | 0.5 V to 4.5 V |
| Global minimum signed margin | 0.499950 V |
| Global average signed margin | 2.499975 V |
| Global maximum signed margin | 4.500000 V |

The exact command was:

    python run_threshold_sweep.py

The detailed result file contained 165 rows: one header and 164
boundary-simulation records. The threshold-level summary contained
42 rows: one header and 41 threshold records.

The generated figures are:

- `figures/threshold_success_rate.png`;
- `figures/threshold_margin.png`.

The success-rate figure shows complete decoding agreement throughout the
tested interval. The margin figure shows the expected symmetric reduction
of the minimum decoding margin toward either end of the interval.

This sweep characterizes the decoder operating envelope of the current
behavioral-source RC baseline. It does not establish the corresponding
operating envelope of a future constraint-compiled passive network.

---

# Verified Supply-Voltage Sweep

A deterministic supply-voltage sweep was completed on 5 August 2026
for the behavioral-source RC validation baseline.

The supply voltage was varied from 4.0 V through 5.5 V in increments
of 0.1 V. All four admitted boundary conditions were simulated at
every supply value.

The fixed parameters were:

- decoder threshold: 2.5 V;
- output resistance: 10.0 kOhm; and
- output capacitance: 1.0 uF.

The result was:

| Quantity | Result |
|---|---:|
| Supply-voltage points | 16 |
| Boundary simulations | 64 |
| Passed | 64 |
| Failed | 0 |
| Overall success rate | 100.000000% |
| Fully passing tested interval | 4.0 V to 5.5 V |
| Global minimum signed margin | 1.499960 V |
| Expected-1 output range | 3.999960 V to 5.499945 V |
| Expected-0 output range | 0.000000 V to 0.000000 V |

The exact command was:

    python run_supply_sweep.py

The detailed result file contained 65 rows: one header and 64
boundary-simulation records. The supply-level summary contained
17 rows: one header and 16 supply records.

The generated figures are:

- `figures/supply_success_rate.png`;
- `figures/supply_voltage_response.png`;
- `figures/supply_margin.png`.

The expected-1 output tracked the supply voltage throughout the tested
interval, while the expected-0 output remained at approximately zero.
With the decoder threshold fixed at 2.5 V, the smallest measured signed
margin occurred at the minimum tested supply voltage of 4.0 V.

This sweep characterizes supply-voltage dependence of the current
behavioral-source RC baseline. It does not establish the supply-voltage
envelope of a future constraint-compiled passive network.

---

# Verified Resistance and RC-Timing Sweep

A deterministic resistance sweep was completed on 5 August 2026 for the
behavioral-source RC validation baseline.

The output resistance was varied from 5.0 kOhm through 20.0 kOhm in
increments of 1.0 kOhm. All four admitted boundary conditions were
simulated at every resistance value.

The fixed parameters were:

- supply voltage: 5.0 V;
- decoder threshold: 2.5 V;
- output capacitance: 1.0 uF;
- transient sampling interval: 0.1 ms;
- transient simulation window: 150 ms; and
- settling criterion: final 1% voltage band.

The result was:

| Quantity | Result |
|---|---:|
| Resistance points | 16 |
| Boundary simulations | 64 |
| Passed | 64 |
| Failed | 0 |
| Overall success rate | 100.000000% |
| Measured 10--90% rise-time range | 11.000 ms to 43.900 ms |
| Measured 1% settling-time range | 23.096 ms to 92.196 ms |
| Maximum rise-time relative error | 0.126529% |
| Maximum settling-time relative error | 0.304654% |
| Minimum signed decoding margin | 2.497135 V |

The theoretical first-order RC timing relations used for comparison were:

    t_rise = 2.197224577 R C

and

    t_settle = -ln(0.01) R C.

The exact command was:

    python run_resistance_sweep.py

The detailed result file contained 65 rows: one header and 64
boundary-simulation records. The resistance-level summary contained
17 rows: one header and 16 resistance records.

The generated figures are:

- `figures/resistance_timing.png`;
- `figures/resistance_timing_error.png`;
- `figures/resistance_success_rate.png`.

The measured rise and settling times scale linearly with resistance and
remain in close agreement with first-order RC theory throughout the tested
interval. All expected-high responses settled inside the 150 ms simulation
window.

This sweep validates transient extraction and RC timing analysis for the
current behavioral-source interface. It does not establish timing behavior
for a future constraint-compiled passive carrier network.

---

# Verified Capacitance and RC-Timing Sweep

A deterministic capacitance sweep was completed on 5 August 2026 for
the behavioral-source RC validation baseline.

The output capacitance was varied from 0.25 uF through 2.00 uF in
increments of 0.125 uF. All four admitted boundary conditions were
simulated at every capacitance value.

The fixed parameters were:

- supply voltage: 5.0 V;
- decoder threshold: 2.5 V;
- output resistance: 10.0 kOhm;
- transient sampling interval: 0.1 ms;
- transient simulation window: 120 ms; and
- settling criterion: final 1% voltage band.

The result was:

| Quantity | Result |
|---|---:|
| Capacitance points | 15 |
| Boundary simulations | 60 |
| Passed | 60 |
| Failed | 0 |
| Overall success rate | 100.000000% |
| Measured 10--90% rise-time range | 5.500 ms to 43.900 ms |
| Measured 1% settling-time range | 11.596 ms to 92.196 ms |
| Maximum rise-time relative error | 0.733141% |
| Maximum settling-time relative error | 0.721576% |
| Minimum signed decoding margin | 2.487557 V |

The theoretical first-order RC timing relations used for comparison were:

    t_rise = 2.197224577 R C

and

    t_settle = -ln(0.01) R C.

The exact command was:

    python run_capacitance_sweep.py

The detailed result file contained 61 rows: one header and 60
boundary-simulation records. The capacitance-level summary contained
16 rows: one header and 15 capacitance records.

The generated figures are:

- `figures/capacitance_timing.png`;
- `figures/capacitance_timing_error.png`;
- `figures/capacitance_success_rate.png`.

The measured rise and settling times scale linearly with capacitance and
remain in close agreement with first-order RC theory throughout the tested
interval. All expected-high responses settled inside the 120 ms simulation
window.

This sweep validates transient extraction and RC timing analysis for the
current behavioral-source interface. It does not establish timing behavior
for a future constraint-compiled passive carrier network.

---

# Verified Imposed Temperature-Drift Sweep

A deterministic imposed temperature-drift sweep was completed on
5 August 2026 for the constraint-compiled existential-response circuit
and its RC output interface.

The temperature parameter was varied from -40 degrees C through
125 degrees C in increments of 5 degrees C. All four admitted boundary
conditions were simulated at every temperature point.

Because the present circuit uses ideal SPICE components, temperature
dependence was introduced explicitly through a linear parameter-drift
model rather than through an uncalibrated simulator temperature setting.

The imposed component relations were:

    R(T) = R0 [1 + alpha_R (T - T0)]

and

    C(T) = C0 [1 + alpha_C (T - T0)].

The model parameters were:

- nominal temperature: 25 degrees C;
- nominal resistance: 10.0 kOhm;
- nominal capacitance: 1.0 uF;
- resistor coefficient: +100 ppm per degree C;
- capacitor coefficient: -200 ppm per degree C;
- supply voltage: 5.0 V;
- decoder threshold: 2.5 V;
- transient sampling interval: 0.1 ms;
- transient simulation window: 80 ms; and
- settling criterion: final 1% voltage band.

The verified result was:

| Quantity | Result |
|---|---:|
| Temperature points | 34 |
| Boundary simulations | 136 |
| Passed | 136 |
| Failed | 0 |
| Overall success rate | 100.000000% |
| Effective resistance range | 9.935000 kOhm to 10.100000 kOhm |
| Effective capacitance range | 0.980000 uF to 1.013000 uF |
| Effective RC time-constant range | 9.898000 ms to 10.064155 ms |
| Measured 10--90% rise-time range | 21.700 ms to 22.100 ms |
| Measured 1% settling-time range | 45.596 ms to 46.396 ms |
| Maximum rise-time relative error | 0.233075% |
| Maximum settling-time relative error | 0.232314% |
| Minimum signed decoding margin | 2.498186 V |

The exact command was:

    python run_temperature_sweep.py

The detailed result file contained 137 rows: one header and 136
boundary-simulation records. The temperature-level summary contained
35 rows: one header and 34 temperature records.

The generated figures are:

- `figures/temperature_component_drift.png`;
- `figures/temperature_timing.png`;
- `figures/temperature_margin.png`; and
- `figures/temperature_success_rate.png`.

All admitted boundary conditions decoded correctly over the complete
tested temperature interval. Measured transient timing remained within
approximately 0.24% of first-order RC theory.

This result is a deterministic parameter-sensitivity study under the
declared linear component-drift coefficients. It is not a calibrated
temperature model for a selected resistor, capacitor, semiconductor
process, PCB, or physical carrier substrate.

---

# Scientific Principle

CPC Validation is designed around a simple principle:

A physical implementation is considered correct only if its measured
response reproduces an independently computed mathematical continuation.

This separation between mathematical specification and physical
realization forms the foundation of the validation framework.

