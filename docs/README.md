# CPC documentation

[Repository overview](../README.md)

## Architecture and validation

- [Current architecture](architecture.md): CCIR, execution contracts, three general backend families and evidence boundaries.
- [Validation methodology](validation.md): compiler, execution, semantic, qualification and physical-evidence checks; historical RC sweeps.
- [Accepted design RFCs](design/README.md): RFC-0001 through RFC-0010.
- [Compiler](compiler.md), [benchmarks](benchmarks.md) and [benchmark generator](generator.md).
- [Scaling scope](scaling.md) and [roadmap](roadmap.md).

## CPC-Shor and N0

- [Research overview](shor/README.md).
- [Current N0 status](shor/n0-status.md).
- [Native claim boundary](shor/native-boundary.md).

CPC-Shor/N0 is a research/validation line, not a fourth qualified general
backend. Finite software/model results and synthetic N0 rehearsal do not
establish physical N0 validation, native scalable Shor or advantage. Physical
N0 execution and FPGA programming remain unauthorized.

The current bounded release includes P3/P4 software, retained-record replay,
guarded acquisition interfaces, diagnostic/per-trial scoring, classical host
simulation and N0 controller software/RTL. See the Shor overview for exact
exclusions. Publication does not establish stochastic acceptance or authorize
physical execution.

## Historical releases and physical evidence

- [v0.6.0: accepted RFC-0010 software/evidence architecture](releases/v0.6.0.md).
- [v0.5.0: RFC-0009 and P1 physical FPGA baseline](releases/v0.5.0.md).
- [Retained P1 physical evidence](../evidence/p1/physical/README.md).
- [Change history](../CHANGELOG.md).

Release test counts and historical research outcomes retain their original
scope. Current validation counts require a fresh regression run. Research run
directories are not the public documentation entrypoint.
