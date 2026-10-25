# CPC-Shor research and N0 validation

[Documentation index](../README.md) · [Architecture](../architecture.md) · [Validation](../validation.md)

CPC-SHOR is a **core CPC research and validation program** associated with
RFC-0010. This section is its public entrypoint for qualified software, the
bounded classical hardware milestone and the outstanding quantum research gates.

The repository now contains several distinct layers of evidence. They must not be
collapsed into a single claim.

## Current status

| Layer | Status |
|---|---|
| Finite Shor software/model validation | Established for the tested finite scope |
| RFC-0010 mapping | Implemented and tested in the software/model scope |
| N0 software stack | Pre-physical software-freeze candidate |
| P3/P4 libraries | Published bounded software/model capabilities |
| Retained-record replay and per-trial scoring | Implemented software; not aggregate scientific acceptance |
| Host-native C kernels | Classical host simulation |
| N0 RTL/protocol/synthesis | Published software and simulation infrastructure |
| Physical N0 validation | No |
| N0 FPGA programming authorization | No |
| Synthetic device/statistical rehearsal | Completed for the defined synthetic scope |
| Physical preregistration framework | Implemented; physical numerical parameters remain unresolved |
| Cat/bosonic N0 apparatus concept | Defined |
| Logical O_beta measurement route | Validated in the finite model |
| Parity-phase plus fixed-axis route | Retained as the primary finite-model route |
| Integrated physical N0 apparatus | Not established |
| Apparatus status | D |
| Physical N0 execution authorization | No |
| Physical N0 acquisition | Not performed |
| Native scalable CPC-Shor | Not established |

## Parallel classical hardware milestone

The [UP5K/Pico Area-v3 milestone](classical-up5k-physical-milestone.md) is complete
within a bounded **classical probability/PRNG** scope: seeded physical oracle
records 2, 68 and 194, independently audited exact response frames.
It is distinct from the finite Shor simulator and from N0 quantum measurement.
It does not change the N0-specific authorization flags below.

Known unseeded record 217 (0022 versus oracle 0002) and five unmatched physical
error-path records remain open. Full-corpus physical conformance, physical N0,
native quantum order finding and advantage are not established.
The linked milestone records provenance, limitations and read-only verification.

## What the finite Shor work establishes

The finite software/model line includes typed modular-response representations,
finite open-system witnesses, coherence negative controls, Fourier readout, and
independent order/factor validation for the tested finite instances.

These results are evidence about the implemented finite models. They are not
evidence of a native scalable physical Shor implementation.

The original prototype description is retained at
[../shor-rfc0010-prototype.md](../shor-rfc0010-prototype.md).

## Published P3/P4 software

The release includes bounded P3 models/compiler, inference/analysis, host
filtering and execution/provenance support. P4 includes deterministic
arithmetic/reconstruction, distinct EXACT and bounded-error certification,
risk contracts, retained-record replay, guarded acquisition adapters,
diagnostic-state construction, per-trial retained-artifact calibration scoring
and a classical host C simulation kernel.

BE certification does not require factorization of the candidate order.
Its wrong-acceptance risk is a joint-event bound under the stated assumptions,
not automatically a conditional error bound given acceptance. Exact and
bounded-error guarantees must not be conflated.

The release excludes the complete historical autonomous P4 workflow,
calibrated-population registry, evidence/reducer/supervisor modules and
historical launchers. Per-trial scoring is not a calibration PASS. Zero local
errors per phase class is an acceptance criterion, not an observed result.

E5-v1 remains consumed, non-retryable and INCOMPLETE_OR_INVALID_GRID. E5-R1 is
post hoc recovery only; it does not establish a retrospective E5 grid PASS.
No software interface or document grants new execution authorization.

## N0

N0 is the next physical-validation layer. Its purpose is narrower than full Shor:
it asks whether a prepared physical bosonic logical state can exhibit the specified
CPC measurement behavior under a preregistered physical profile and independently
auditable acquisition chain.

N0 is not:

- a full Shor execution;
- a scalability demonstration;
- a quantum-advantage claim;
- proof of native polynomial-resource CPC-Shor;
- proof that a presently identified commercial platform implements the required
  integrated apparatus.

See [n0-status.md](n0-status.md).

## Native claim boundary

The native CPC-Shor architecture requires physical realization of the quantum
state, reversible modular dynamics, CPC probe interaction, and stochastic
measurement record.

Classical software and FPGA logic may orchestrate, timestamp, acquire, validate,
and reduce records. They do not substitute for the required physical quantum/CPC
dynamics.

See [native-boundary.md](native-boundary.md).

Current N0 authorization and evidence flags are:

- PHYSICAL_N0_VALIDATED = NO
- PHYSICAL_EXECUTION_AUTHORIZED = NO
- FPGA_PROGRAMMING_AUTHORIZED = NO
- PHYSICAL_ACQUISITION_PERFORMED = NO

Host-native means classical host simulation. Software and RTL publication do
not establish native quantum synthesis, physical TTS, scalable QC or
computational advantage.

## Historical research checkpoints

These documents preserve earlier reasoning and reported results. Their
historical commands, test counts, paths and next actions are not a current
clean-clone reproduction promise or execution authorization. The uncommitted
single-node runners and two-node/cleanup executable workflows are not
published by this documentation unit.

The following documents are retained as intermediate scientific checkpoints:

- [Single-node derivation](../shor-single-node-research.md)
- [Single-node results](../shor-single-node-results.md)
- [Two-node derivation](../shor-two-node-derivation.md)
- [Two-node results](../shor-two-node-results.md)
- [Cleanup/locality derivation](../shor-cleanup-locality-derivation.md)
- [Cleanup/locality results](../shor-cleanup-locality-results.md)
- [RFC-0010 finite Shor prototype](../shor-rfc0010-prototype.md)

They remain useful provenance, but they are not the current N0 readiness statement.
