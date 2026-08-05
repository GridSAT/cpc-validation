# External Parity Benchmark Format

CPC Validation v0.3 introduces an external JSON format for parity-constraint
benchmarks.

The benchmark file describes only:

- the schema version;
- the benchmark name;
- an optional description;
- the boundary variables; and
- the parity constraints.

The benchmark file does not contain:

- continuation values;
- completion counts;
- decoded responses;
- expected SPICE voltages; or
- precomputed truth tables.

This preserves the separation between the admitted instance description and
the independent validation reference.

## Schema version

The current schema version is:

```json
{
  "schema_version": 1
}
```

## Complete example

```json
{
  "schema_version": 1,
  "name": "default-xor",
  "description": "Two parity constraints with boundary variables x0 and x3.",
  "boundary_variables": [0, 3],
  "constraints": [
    {
      "variables": [0, 1, 2],
      "parity": 0
    },
    {
      "variables": [1, 2, 3],
      "parity": 1
    }
  ]
}
```

This represents:

```text
x0 XOR x1 XOR x2 = 0
x1 XOR x2 XOR x3 = 1
```

The boundary variables are `x0` and `x3`. Variables `x1` and `x2` are
therefore internal variables.

## Fields

### `schema_version`

Required integer.

The current loader accepts only schema version `1`.

### `name`

Required nonempty string.

The name identifies the benchmark in output files and validation reports.

### `description`

Optional string.

The description provides human-readable context and does not affect
compilation or validation.

### `boundary_variables`

Required array of distinct nonnegative integer variable indices.

Every listed boundary variable must occur in at least one constraint.

### `constraints`

Required nonempty array of parity-constraint objects.

Each constraint has:

- `variables`: a nonempty array of distinct nonnegative integer indices;
- `parity`: either `0` or `1`.

A constraint is satisfied when the XOR of the listed Boolean variables equals
the declared parity.

## Single-boundary execution

Compile and simulate one admitted boundary condition:

```bash
python run_benchmark.py \
    benchmarks/default_xor.json \
    --boundary 'x0=0,x3=1'
```

The command reports:

- benchmark metadata;
- constraint and variable counts;
- internal-variable count;
- candidate count;
- generated behavioral-source count;
- output voltage;
- decoded value;
- netlist path; and
- ngspice log path.

This command executes one boundary assignment. It does not by itself compare
the decoded result with the independent generic reference evaluator.

## Complete benchmark validation

Validate every admitted boundary assignment:

```bash
python validate_benchmarks.py \
    benchmarks/default_xor.json \
    benchmarks/parity_chain_5.json
```

For each benchmark, the validator:

1. loads and validates the JSON description;
2. enumerates every boundary assignment;
3. independently enumerates all internal completions;
4. computes the continuation value;
5. compiles the parity instance into an ngspice netlist;
6. simulates the generated physical model;
7. applies the fixed decoder;
8. compares the decoded value with the independent reference; and
9. records compilation, simulation, and model-size statistics.

The machine-readable result is written by default to:

```text
results/benchmark_validation.csv
```

## Validation and anti-embedding contract

The generic reference evaluator and the compiler are separate modules:

```text
src/generic_reference.py
src/compiler.py
```

The reference evaluator receives the instance and boundary assignment and
enumerates internal Boolean completions directly.

The compiler receives the same admitted instance and boundary assignment but
does not receive:

- the continuation result;
- the completion count;
- the completion list; or
- any precomputed reference table.

The comparison occurs only after physical-model simulation and decoding.

## Current limitations

The current compiler uses behavioral sources for candidate validity and
existential aggregation.

The external benchmark format and independent validation path are generic for
parity systems, but the current physical realization is still an auditable
behavioral-source research prototype rather than a passive or coherent carrier
network.

Candidate generation is exhaustive in the number of internal variables:

```text
candidate count = 2^(number of internal variables)
```

This v0.3 milestone establishes generic instance description, compilation, and
independent validation. It does not claim scalable physical realization.
