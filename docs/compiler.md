# Generic Parity Compiler

## Purpose

The generic parity compiler converts a declarative Boolean parity system into
an ngspice netlist with a restricted RC output interface.

The compiler is implemented in:

```text
src/compiler.py
```

It is independent of:

- the generic reference evaluator;
- ngspice execution;
- voltage measurement;
- semantic decoding; and
- validation comparison.

This separation preserves the CPC validation architecture.

## Constraint representation

A parity constraint has the form:

```text
x_i1 XOR x_i2 XOR ... XOR x_ik = p
```

where `p` is either `0` or `1`.

In Python:

```python
ParityConstraint(
    variables=(0, 1, 2),
    parity=0,
)
```

A parity instance contains:

```python
ParityInstance(
    constraints=(...),
    boundary_variables=(0, 3),
)
```

Every constrained variable that is not declared as a boundary variable is an
internal variable.

## Compilation contract

The compiler receives:

- the parity instance;
- one admitted boundary assignment;
- the supply voltage;
- the RC-interface values; and
- the transient duration.

The compiler does not receive:

- the independently computed continuation value;
- the internal-completion count;
- the list of satisfying completions;
- a precomputed truth table; or
- an expected output voltage.

## Candidate generation

For `k` internal variables, the current compiler enumerates:

```text
2^k
```

candidate assignments.

Each candidate source is high exactly when that internal assignment satisfies
all constraints under the admitted boundary condition.

## XOR expressions

For normalized Boolean values `a` and `b`, the backend uses:

```text
XOR(a,b) = a + b - 2ab
```

Longer XOR expressions are compiled by repeated composition.

The expression generator is validated against complete Boolean truth tables.

## Existential aggregation

Candidate responses are combined using normalized Boolean OR:

```text
OR(c1,...,cn) = 1 - product_i(1-ci)
```

The aggregate source is high exactly when at least one internal completion
exists.

## Restricted interface

The logical aggregate drives:

```text
Rout -> vout
          |
         Cout
          |
        ground
```

The semantic decoder reads only the designated output voltage.

It does not reconstruct the internal candidate state.

## Compilation statistics

The compiler reports:

- constraint count;
- variable count;
- boundary-variable count;
- internal-variable count;
- candidate count;
- candidate-source count; and
- total behavioral-source count.

The benchmark validator additionally records:

- generated netlist bytes;
- compilation time; and
- ngspice simulation time.

## Current complexity

The present backend is exhaustive in the number of internal variables:

```text
candidate count = 2^(internal-variable count)
```

The generated netlist therefore grows exponentially in this parameter.

The current compiler is intended to establish:

- a generic compilation API;
- answer-independent netlist generation;
- reproducible backend behavior;
- complete validation;
- resource accounting; and
- an auditable baseline for later physical backends.

It does not establish an efficient general-purpose solver.

## Inspection

Generate netlists for the built-in reference instance:

```bash
python run_compiler.py
```

Compile an external benchmark:

```bash
python run_benchmark.py \
    benchmarks/default_xor.json \
    --boundary 'x0=0,x3=1'
```

Validate the complete benchmark suite:

```bash
python validate_benchmarks.py benchmarks/
```
