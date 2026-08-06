# CPC Validation Architecture

## Purpose

CPC Validation provides a reproducible reference implementation for the
validation of C-Parity Computing (CPC). Rather than demonstrating only a
numerical result, the repository validates the complete engineering chain
from an independently computed mathematical continuation to the physical
response of a simulated circuit.

The current implementation establishes the first software validation stage.
Future versions will progressively replace abstract behavioral models with
compiled passive networks and ultimately hardware implementations while
preserving the same validation methodology.

---

# Validation Philosophy

Every experiment follows the same sequence.

1. Compute the expected continuation independently.

2. Construct a physical circuit implementing the intended response.

3. Simulate the circuit using ngspice.

4. Decode the resulting physical measurement.

5. Compare the decoded value with the independently computed reference.

Only if both values agree is the validation considered successful.

This separation ensures that the simulator is never validating itself.
The mathematical reference remains independent of the physical realization.

---

# Current Validation Pipeline

Constraint instance

↓

Reference continuation computation

↓

Circuit generation

↓

ngspice transient simulation

↓

Measured output voltage

↓

Threshold decoder

↓

Decoded continuation

↓

Comparison with reference

↓

PASS / FAIL

---

# Reference System

The current benchmark uses two parity constraints

x0 XOR x1 XOR x2 = 0

x1 XOR x2 XOR x3 = 1

Eliminating the internal variables produces the continuation relation

x0 XOR x3 = 1

This relation is computed directly by the reference implementation and is
independent of the circuit simulator.

---

# Physical Model

The first demonstrator intentionally uses a simple behavioral voltage source
combined with an RC network.

This establishes

- deterministic simulation
- reproducible decoding
- automated verification

before introducing physically compiled passive networks.

---

# Separation of Responsibilities

The repository deliberately separates

Reference mathematics

Circuit generation

Physical simulation

Signal decoding

Verification

Each stage can therefore be tested independently.

---

# Why SPICE?

SPICE provides

- reproducible analog simulation
- transient analysis
- component tolerances
- Monte Carlo analysis
- standard circuit descriptions

Using SPICE allows the validation methodology to remain independent of any
particular hardware platform.

---

# Future Architecture

The validation pipeline will evolve through several stages.

Stage 1

Reference continuation
+
Behavioral SPICE model

Stage 2

Compiled passive RC networks

Stage 3

Monte Carlo robustness analysis

Stage 4

Automatically generated networks

Stage 5

PCB demonstrator

Stage 6

Physical measurements

Stage 7

Carrier-based implementations

Throughout all stages the reference continuation remains unchanged.

Only the physical realization evolves.

---

# Design Principle

The mathematical continuation is regarded as the invariant specification.

Every physical implementation must reproduce the same continuation under
measurement.

Consequently the validation framework compares physical responses against
an independently computed mathematical ground truth rather than comparing
one physical implementation against another.

## Intermediate Representation and RC Backend

The v0.4 compiler path is:

```text
ParityInstance
  -> compile_parity_instance_to_ir()
  -> IRProgram
  -> compile_ir_to_rc()
  -> emit_parity_rc_netlist()
  -> RC/ngspice netlist
```

`src/ir_compiler.py` constructs the backend-independent IR.
`src/backends/rc.py` consumes the IR and calls the RC emitter.
`src/rc_emitter.py` generates the netlist text.

The RC backend no longer calls `compile_parity_instance()`.

## Core Constraint Intermediate Representation

RFC-0002 defines CCIR as the canonical representation shared by
front ends, analysis passes, optimization passes, and backends.

The implemented CCIR foundation currently consists of:

- `src/ccir.py`: program, constraint, and typed-payload contracts;
- `src/ccir_parity.py`: Boolean parity constraints; and
- `src/ccir_clause.py`: Boolean clause constraints.

CCIR remains independent of DIMACS, parity JSON, ngspice syntax,
source-language parsing, and independently computed continuation
answers.

The existing parity-oriented IR remains operational during incremental
migration. It will be retired only after both source-model lowerings and
the RC backend migration have passed full regression and SPICE validation.
