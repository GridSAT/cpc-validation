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

# Scientific Principle

CPC Validation is designed around a simple principle:

A physical implementation is considered correct only if its measured
response reproduces an independently computed mathematical continuation.

This separation between mathematical specification and physical
realization forms the foundation of the validation framework.

