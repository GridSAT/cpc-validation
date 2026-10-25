# WP-B1 bosonic software conformance: outstanding gates

Status: **open workstream; full WP-B1 conformance not established** (2026-10-25).
This checklist is a plan and source inventory, not an implementation or device
qualification. It progresses in parallel with physical-device collaboration.

WP-B1 requires the complete chain:

canonical CCIR → bosonic/vendor-facing execution artifact → complete provenance
→ simulated/vendor abstraction execution → admitted observations → fixed decoding
→ independent canonical semantic validation.

The [bounded UP5K/Pico milestone](classical-up5k-physical-milestone.md) supplies
classical transport/PRNG engineering evidence. It does not implement this whole
bosonic chain or establish a cat-qubit substrate.

## Present building blocks and missing integration

| Gate | Present source/evidence | WP-B1 status and required acceptance |
|---|---|---|
| Canonical input/admission | [CCIR](../../src/ccir.py), [backend contract](../../src/backend.py), [generic reference](../../src/generic_reference.py) | General infrastructure present. Bosonic supported-domain declaration and frozen case inventory missing. Reject unsupported inputs explicitly. |
| Vendor-facing compilation | [Compilation dispatch](../../src/compile_backend.py), [RFC-0010 execution specification](../../src/open_system_execution.py) | Partial reusable infrastructure; no qualified integrated vendor/bosonic CCIR compiler established. Define artifact schema and deterministic compiler first. |
| Preparation/provenance | [PreparedExecution](../../src/prepared_execution.py), [N0 physical profile](../../src/n0_physical_profile.py), [adapter](../../src/n0_device_adapter.py) | Contracts and N0 boundaries present. Full case-to-vendor-artifact provenance and capability admission missing. |
| Execution adapter | [Finite bosonic model](../../src/n0_bosonic_model.py), [synthetic device](../../src/n0_synthetic_device.py) | Finite/synthetic execution present, explicitly labeled. End-to-end WP-B1 vendor abstraction integration unqualified. |
| Restricted observations | [ObservableExecution](../../src/observable_execution.py), [N0 raw records](../../src/n0_raw_record.py) | Software contracts present. Bosonic backend-to-canonical admitted observation mapping missing. |
| Fixed decoding | [N0 reducer](../../src/n0_reducer.py), [Shor decoder](../../src/shor_decoder.py) | Domain-specific building blocks, not a general bosonic semantic decoder. Freeze decoder inputs, algorithm and costs for the declared domain. |
| Independent semantics | [CCIR reference](../../src/ccir_reference.py), [open-system reference](../../src/open_system_reference.py) | References present for their domains. Complete WP-B1 case-level decoded-output comparison not established. |
| Complete gate evidence | Existing general/N0 software tests and [validation methodology](../validation.md) | Partial evidence only. No single full WP-B1 conformance report, preregistered corpus, resource ledger and negative matrix yet. |

Existing tests passing at a documentation commit boundary validate the current
repository. They do not turn the missing WP-B1 integration into PASS.

## Proposed interface and evidence contract

Before implementation, freeze a supported CCIR subset and versioned capability
profile. Each case must bind canonical input bytes/hash, boundary assignment,
compiler/profile versions, source revision, artifact hash and a machine-resolvable
mapping from every generated parameter to CCIR data or a globally fixed rule.

The execution artifact must declare the Hamiltonian/dissipator or vendor
primitive mapping, model truncation, units, timing, stabilization assumptions,
resources, admitted ports, preparation and decoder specification. A vendor
capability not available or not mapped is an explicit unsupported/HOLD outcome.

Preparation binds that artifact to the adapter, simulator or vendor abstraction,
calibration/profile identities, seed policy, versions and resource limits.
Execution returns immutable admitted observations plus timestamps, provenance,
failure/abstention and realization_status. Simulated records remain simulated;
a vendor abstraction is not physical acquisition.

Decoding consumes only admitted observations and frozen calibration/reference
inputs. The independently implemented canonical reference runs outside
compilation, preparation and execution. Expected answers, truth phases, orders
and factors must never enter an execution artifact or controller.

## Preregistered conformance and negative matrix

All gates below are **outstanding for the integrated WP-B1 candidate**:

- [ ] Freeze cases, full boundary assignments, supported/unsupported families,
  decoder thresholds, tolerances, uncertainty and resource ceilings before scoring.
- [ ] Compile the same canonical input reproducibly; resolve every generated
  parameter and provenance edge. Reject missing, changed or foreign bindings.
- [ ] Demonstrate answer independence: alter/withhold external reference answers
  without altering compiled artifacts or execution; reject hidden truth inputs.
- [ ] Execute all admitted cases through the actual abstraction adapter and
  capture raw allowed observations. Reject fabricated, stale, reordered,
  truncated, out-of-profile and wrong-calibration records.
- [ ] Freeze decoder behavior and prove stability under the preregistered
  observation/calibration perturbations; report abstentions and failures.
  Measure decoding cost and full compilation/execution costs against fixed caps.
- [ ] Independently validate decoded canonical semantics for every preregistered
  case and boundary assignment. Backend agreement alone is insufficient.
- [ ] Inject provenance corruption, unsupported dynamics, leakage/invalid
  observations, timeout and resource exhaustion; verify fail-closed behavior.
- [ ] Run the complete suite on every atomic commit and publish a reproducible,
  source-pinned conformance manifest with all cases, costs and failed gates.

Completion requires every admitted preregistered case and negative gate to pass
without postselection, answer leakage, decoder retuning or relaxed limits.
Define the exact new tests and output schema in the implementation proposal;
this document deliberately does not invent missing execution results.

## Parallel handoff

WP-B1 may proceed using an explicitly simulated abstraction while
Alice & Bob co-design preparation clarifies
possible WP-B2/WP-B3 device compatibility and N0 interfaces. Vendor confirmation
and a separately scoped physical contract are prerequisites to physical claims,
not prerequisites to honest software progress.
