# Reproducible Parity Benchmark Generator

## Purpose

The benchmark generator creates schema-compatible parity benchmark files for
compiler regression and scaling studies.

The generator is:

```text
generate_parity_benchmarks.py
```

Generated benchmark corpora are reproducible build artifacts and are excluded
from Git.

## Supported families

### Chain

Overlapping three-variable parity constraints:

```text
x0 XOR x1 XOR x2 = p0
x1 XOR x2 XOR x3 = p1
...
```

The first and last variables are boundaries.

### Cycle

A closed sequence of overlapping parity constraints with wraparound and a
boundary-closing relation.

### Star

A family centered on one internal variable and connected to multiple leaves.

### Random

A deterministic pseudorandom parity system controlled by:

- variable count;
- constraint count;
- arity; and
- random seed.

The random generator guarantees that every declared variable occurs in at
least one constraint.

## Size syntax

One benchmark size:

```text
8
```

An inclusive size sequence:

```text
4:10:2
```

which generates:

```text
4, 6, 8, 10
```

When the stop value is not reached exactly, it is appended.

## Examples

Generate chains:

```bash
python generate_parity_benchmarks.py \
    --family chain \
    --variables 4:10:2 \
    --output-directory benchmarks/generated/chain
```

Generate cycles:

```bash
python generate_parity_benchmarks.py \
    --family cycle \
    --variables 4:8:2 \
    --output-directory benchmarks/generated/cycle
```

Generate stars:

```bash
python generate_parity_benchmarks.py \
    --family star \
    --variables 4:8:2 \
    --output-directory benchmarks/generated/star
```

Generate deterministic random systems:

```bash
python generate_parity_benchmarks.py \
    --family random \
    --variables 4:8:2 \
    --constraints 4 \
    --arity 3 \
    --seed 20260806 \
    --output-directory benchmarks/generated/random
```

## Current verified corpus

The current development corpus contains:

- four chain benchmarks;
- three cycle benchmarks;
- three star benchmarks; and
- three random benchmarks.

Totals:

```text
benchmarks:            13
boundary simulations:  52
passed:                52
failed:                 0
```

The largest current instance has:

```text
variables:             10
internal variables:     8
candidate assignments: 256
```

## Validation

Validate the generated corpus:

```bash
python validate_benchmarks.py \
    benchmarks/generated \
    --output results/generated_benchmark_validation.csv
```

The generated result CSV records one row per boundary assignment.

## Reproducibility

Random benchmark generation is deterministic for a fixed:

- variable count;
- constraint count;
- arity; and
- seed.

The generator tests verify:

- family structure;
- size parsing;
- JSON round trips;
- random reproducibility;
- random-seed differentiation;
- boundary participation;
- full variable coverage; and
- rejection of underspecified random systems.

## Scope

The generator creates logical benchmark descriptions.

It does not:

- compute expected continuation tables;
- insert expected answers;
- generate cached completion data;
- determine expected output voltages; or
- bypass independent validation.

Reference values are computed only by the separate generic evaluator.
