# Validation Methodology

## Purpose

The objective of CPC Validation is not to demonstrate that a circuit
produces a desired output. Rather, the objective is to verify that a
physical implementation reproduces an independently computed mathematical
continuation.

Every validation therefore compares two completely independent objects:

1. A mathematical reference continuation.
2. A physical measurement obtained from circuit simulation or hardware.

Agreement between these two objects constitutes a successful validation.

---

# Validation Pipeline

Every experiment follows the same sequence.

Constraint instance

↓

Reference continuation computation

↓

Circuit generation

↓

Physical simulation (ngspice)

↓

Measured voltage

↓

Threshold decoding

↓

Decoded continuation

↓

Reference comparison

↓

PASS / FAIL

The mathematical reference never depends on the simulator.

---

# Independent Reference

For the current benchmark

x0 XOR x1 XOR x2 = 0

x1 XOR x2 XOR x3 = 1

elimination of the internal variables yields

x0 XOR x3 = 1

The reference implementation computes this continuation directly.

The circuit simulator has no knowledge of this computation.

---

# Validation Criterion

For every boundary assignment

(x0,x3)

the decoded physical response must equal the independently computed
reference continuation.

Formally,

decoded_response = reference_continuation

for every tested assignment.

Only then is the experiment considered successful.

---

# Current Benchmark

Boundary assignments

x0=0  x3=0

x0=0  x3=1

x0=1  x3=0

x0=1  x3=1

Expected continuation

0

1

1

0

The present repository verifies all four cases automatically.

---

# Physical Simulation

Current simulations use

- ngspice
- transient analysis
- RC output stage
- deterministic threshold decoder

The physical model intentionally remains simple.

Its purpose is validation of the engineering pipeline rather than
optimization of hardware.

---

# Decoder

The physical simulator produces an analog voltage.

A threshold decoder converts this voltage into a binary continuation.

Current threshold

2.5 V

Voltages above the threshold decode to

1

Voltages below the threshold decode to

0

Future versions may implement more sophisticated decoding methods.

---

# Regression Testing

Every repository revision should satisfy

- unit tests
- continuation verification
- SPICE simulation
- decoder verification

No code change should alter previously validated continuation results
unless the benchmark itself changes.

---

# Reproducibility

A validation result should be reproducible from

git clone

↓

dependency installation

↓

python run_spice.py

↓

identical continuation table

Independent researchers should obtain the same validation results without
modifying the repository.

---

# Future Validation Stages

The same methodology will be applied to progressively more realistic
implementations.

Stage 1

Behavioral SPICE

Stage 2

Passive RC compilation

Stage 3

Monte Carlo component variation

Stage 4

Automatic network synthesis

Stage 5

PCB demonstrator

Stage 6

Laboratory measurements

Stage 7

Carrier-based implementations

At every stage the mathematical reference remains unchanged.

Only the physical realization evolves.

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

