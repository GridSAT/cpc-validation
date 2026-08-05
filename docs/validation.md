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

# Scientific Principle

CPC Validation is designed around a simple principle:

A physical implementation is considered correct only if its measured
response reproduces an independently computed mathematical continuation.

This separation between mathematical specification and physical
realization forms the foundation of the validation framework.

