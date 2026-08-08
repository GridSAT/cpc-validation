# Compiler Scaling Study

## Purpose

The scaling study characterizes the current exhaustive parity-to-ngspice
backend.

It measures how compiler output and ngspice execution change as the number of
variables and internal candidate assignments increase.

The study is implemented in:

```text
run_scaling_study.py
```

## Scope

The current compiler enumerates every assignment to the internal variables.

For `k` internal variables:

```text
candidate count = 2^k
behavioral source count = 2^k + 1
```

The additional behavioral source performs existential aggregation over the
candidate-validity sources.

The scaling study therefore characterizes an explicit exhaustive backend. It
does not claim polynomial scaling, efficient SAT solving, or scalable passive
physical realization.

## Benchmark families

The current study includes:

- chain;
- cycle;
- star; and
- seeded random parity systems.

Each generated benchmark has two boundary variables. All remaining constrained
variables are internal variables.

## Study pipeline

For each family and requested variable count, the scaling runner:

1. generates a deterministic JSON benchmark;
2. loads and validates the benchmark;
3. enumerates every admitted boundary assignment;
4. independently computes the continuation value;
5. compiles the instance into an ngspice netlist;
6. records compilation statistics;
7. executes ngspice;
8. applies the fixed voltage decoder;
9. compares the decoded result with the independent reference; and
10. aggregates one result row per benchmark.

## Recorded metrics

The summary CSV records:

- family;
- benchmark name;
- variable count;
- constraint count;
- boundary-variable count;
- internal-variable count;
- candidate count;
- candidate-source count;
- total behavioral-source count;
- boundary-simulation count;
- passed and failed simulations;
- success rate;
- minimum, mean, and maximum netlist size;
- total, mean, and maximum compilation time;
- total, mean, and maximum ngspice time;
- output-voltage range; and
- internal-completion-count range.

## Smoke study

The current reproducible smoke study uses:

```bash
python run_scaling_study.py \
    --families chain,cycle,star,random \
    --variables 4:8:2 \
    --seed 20260806
```

This produces:

```text
families:              4
variable counts:       4, 6, 8
benchmarks:            12
boundary simulations: 48
passed:                48
failed:                 0
```

## Verified growth

With two boundary variables, the current sizes correspond to:

| Variables | Internal variables | Candidates | Behavioral sources |
|---:|---:|---:|---:|
| 4 | 2 | 4 | 5 |
| 6 | 4 | 16 | 17 |
| 8 | 6 | 64 | 65 |

The measured study confirms that all families preserve exact decoded
continuation values across these sizes.

## Measured smoke-profile results

The current verified measurements were obtained on the development machine
using the command shown above.

| Family | Variables | Constraints | Internal | Candidates | Sources | Mean netlist bytes | Mean compile time | Mean ngspice time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| chain | 4 | 2 | 2 | 4 | 5 | 1,708 | 0.043 ms | 7.77 ms |
| chain | 6 | 4 | 4 | 16 | 17 | 7,781 | 0.133 ms | 34.87 ms |
| chain | 8 | 6 | 6 | 64 | 65 | 39,839 | 0.587 ms | 323.15 ms |
| cycle | 4 | 5 | 2 | 4 | 5 | 3,280 | 0.057 ms | 25.42 ms |
| cycle | 6 | 7 | 4 | 16 | 17 | 13,865 | 0.221 ms | 128.31 ms |
| cycle | 8 | 9 | 6 | 64 | 65 | 63,971 | 0.835 ms | 818.78 ms |
| random | 4 | 4 | 2 | 4 | 5 | 2,862 | 0.055 ms | 17.10 ms |
| random | 6 | 4 | 4 | 16 | 17 | 8,613 | 0.136 ms | 47.03 ms |
| random | 8 | 4 | 6 | 64 | 65 | 31,853 | 0.439 ms | 290.50 ms |
| star | 4 | 3 | 2 | 4 | 5 | 2,094 | 0.045 ms | 10.38 ms |
| star | 6 | 5 | 4 | 16 | 17 | 10,551 | 0.149 ms | 69.05 ms |
| star | 8 | 7 | 6 | 64 | 65 | 55,985 | 0.663 ms | 603.50 ms |

The timing values are implementation and machine dependent. Candidate counts,
source counts, constraint counts, variable counts, and generated logical
structure are deterministic.

## Generated figures

The runner produces:

```text
figures/scaling_candidates.png
figures/scaling_sources.png
figures/scaling_netlist_size.png
figures/scaling_compile_time.png
figures/scaling_simulation_time.png
```

The candidate and behavioral-source figures display the exact exponential
growth defined by the exhaustive backend.

The netlist-size, compilation-time, and simulation-time figures report measured
implementation behavior and may vary across machines.

## Interpretation

The measurements distinguish three effects:

1. **Candidate growth** depends only on the number of internal variables.
2. **Netlist growth** depends on candidate count and constraint-expression
   complexity.
3. **Simulation time** depends on both netlist size and topology-specific
   behavioral-expression complexity.

At eight variables in the current environment:

- cycle has the largest mean netlist size and longest mean ngspice runtime;
- star is the second most expensive topology;
- chain and random are smaller and faster at the same candidate count; and
- compilation time remains much smaller than ngspice execution time.

These observations describe the current backend and benchmark definitions.
They should not be generalized to future physical backends without separate
measurement.

## Reproducibility

The logical benchmark structures are deterministic.

Random benchmarks use an explicit seed. The current reference seed is:

```text
20260806
```

Compilation and simulation timings are machine dependent. Correctness,
candidate counts, source counts, variable counts, constraint counts, and
generated netlist structure are deterministic for fixed inputs.

## Temporary artifacts

Generated benchmark files, netlists, ngspice logs, and CSV outputs under
`results/` are reproducible build artifacts.

The scaling runner removes its temporary working directory unless invoked with:

```bash
--keep-work
```

The scaling figures under `figures/` may be committed when they represent a
documented release or research milestone.

## Consolidated validation profile

The consolidated validator uses a reduced scaling regression:

```text
families:        chain, cycle, star, random
variable counts: 4, 6
seed:            20260806
```

This verifies:

- four topology families;
- candidate growth from 4 to 16;
- complete boundary correctness;
- summary CSV generation;
- scaling-figure generation; and
- temporary-work cleanup.

The larger 4, 6, and 8 smoke profile remains the documented scaling milestone.

## Current limitations

The study currently does not include:

- repeated timing trials;
- warm-up runs;
- confidence intervals;
- memory measurements;
- peak ngspice memory use;
- expression-depth statistics;
- passive-network backends;
- transistor-level backends;
- size-10 measurements across every topology; or
- cross-machine timing comparisons.

These are later characterization tasks rather than correctness requirements for
the current compiler milestone.
