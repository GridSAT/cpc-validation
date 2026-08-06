# RFC-0001: CPC Architecture

| Field | Value |
|---|---|
| RFC | RFC-0001 |
| Title | CPC Architecture |
| Status | Accepted |
| Version | 1.0 |
| Author | Karim Daghbouche |
| Created | 2026-08-06 |
| Updated | 2026-08-06 |


## Normative Language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**,
**SHALL NOT**, **SHOULD**, **SHOULD NOT**, and **MAY**
are to be interpreted as described in RFC 2119.


## Implementation Status

This RFC defines the target architecture of CPC.

The current `v0.4-dev` implementation conforms through the
canonical `ParityInstance -> IRProgram -> Backend -> Emitter`
compilation pipeline.

Future implementations MAY reorganize internal modules provided
they continue to satisfy this RFC.

## 1. Purpose

Constraint-to-Physical Compilation (CPC) is a layered compilation
framework that transforms declarative constraint systems into physical
realizations through a backend-independent intermediate representation
and interchangeable physical backends.

This RFC defines the architectural contract of CPC. It specifies the
required layers, canonical compilation pipeline, module responsibilities,
public compatibility surface, extension points, and architectural
invariants that future implementations must preserve.

The RFC describes the framework independently of any single physical
backend. The architecture is independent of any particular backend. The RC/ngspice backend is the first reference implementation of this architecture.

## 2. Scope

This RFC governs:

- the layered CPC architecture;
- the canonical logical-to-physical compilation pipeline;
- separation between source constraints, IR, backends, and emitters;
- public compatibility and backend-oriented APIs;
- module-level responsibilities;
- testing of architectural invariants; and
- extension rules for future backends and transformations.

This RFC does not define:

- the complete IR invariant set;
- a concrete backend interface type;
- a backend registry;
- optimization-pass semantics;
- the electrical validity of a particular hardware substrate; or
- performance or complexity guarantees.

Those topics are reserved for later RFCs.

## 3. Architectural Principles

CPC implementations shall preserve the following principles:

1. Every admitted compilation path SHALL traverse the canonical compilation pipeline.
2. Logical compilation is independent of any physical backend.
3. Physical realization begins only after IR construction.
4. Backends consume IR rather than source constraint objects.
5. Emitters generate backend-specific artifacts only.
6. Public compatibility APIs remain stable across internal refactors.
7. Internal modules may evolve without changing public semantics.
8. Compilation is deterministic for identical admitted inputs and settings.
9. Optimization must preserve continuation semantics.
10. Architectural changes require explicit design documentation and
    architectural regression tests.

## 4. Terminology

**Constraint system**

A declarative collection of logical constraints admitted by a CPC front end.

**ParityInstance**

The current source representation for a finite Boolean parity-constraint
system together with its declared boundary variables.

**Boundary assignment**

A complete assignment to the externally supplied boundary variables.

**Internal variable**

A variable not declared as a boundary variable and existentially quantified
by the compiled realization.

**Candidate**

One deterministic assignment to all internal variables represented in the
intermediate or backend-specific program.

**Continuation semantics**

The exact Boolean response indicating whether at least one internal
completion satisfies all admitted constraints for a boundary assignment.

**IRProgram**

The backend-independent intermediate representation produced by logical
compilation and consumed by physical or digital backends.

**Backend**

A component that translates a valid IRProgram into one backend-specific
compiled representation.

**Emitter**

A backend-internal component that serializes or constructs the concrete
artifact required by that backend.

**Physical realization**

A backend-specific artifact whose observable response is intended to
represent the continuation semantics of the source constraint system.

**CompiledParityNetwork**

The stable compatibility result returned by the current public compiler API.

## 5. Layered Architecture

CPC is organized into the following conceptual layers:

```text
Application
      |
      v
Public API
      |
      v
IR compiler
      |
      v
Intermediate representation
      |
      v
Backend
      |
      v
Emitter
      |
      v
Physical realization
```

Each layer has one directional responsibility.

Upper layers may depend on lower-layer contracts. Lower layers shall not
depend on application-level behavior or independently computed continuation
answers.

The current RC/ngspice implementation is one realization of the backend and
emitter layers. It is not part of the definition of the higher layers.

## 6. Module Responsibilities

| Module | Responsibility | Status |
|---|---|---|
| `src/compiler.py` | Public compatibility façade and parity-domain types | Public |
| `src/ir.py` | Backend-independent intermediate representation | Public |
| `src/ir_compiler.py` | Translation from `ParityInstance` to `IRProgram` | Public |
| `src/backends/rc.py` | Translation from `IRProgram` to RC backend result | Internal |
| `src/rc_emitter.py` | RC/ngspice artifact emission | Internal |
| `src/generic_reference.py` | Backend-independent continuation evaluator | Public |
| `src/reference.py` | Legacy fixed-instance semantic reference | Compatibility |
| `src/spice_model.py` | ngspice execution and result extraction | Internal |
| `src/transient_analysis.py` | Transient-response analysis | Internal |

A module shall not assume responsibilities assigned to another layer.
In particular, backends shall not perform source-language compilation,
and emitters shall not determine continuation semantics.

## 7. Canonical Compilation Pipeline

Every CPC compilation path shall traverse the following pipeline:

```text
ParityInstance
      |
      v
compile_parity_instance_to_ir()
      |
      v
IRProgram
      |
      v
Backend
      |
      v
Emitter
      |
      v
Compiled artifact
```

The current public `compile_parity_instance()` function is a compatibility
façade over this pipeline. It is not an alternative implementation path.

No backend may receive an independently computed continuation answer.
No emitter may bypass the admitted IR or source constraints.

## 8. Public API and Compatibility Surface

The stable convenience API is:

```python
compile_parity_instance(...)
```

It returns `CompiledParityNetwork` and preserves the established netlist
and statistics contract.

The backend-oriented API is:

```python
compile_parity_instance_to_ir(...)
compile_ir_to_rc(...)
```

The first function constructs backend-independent IR. The second compiles
that IR through the current RC backend.

Public compatibility types include `ParityConstraint`, `ParityInstance`,
`CompilationStatistics`, `CompiledParityNetwork`, and `IRProgram`.

Internal emitters and backend implementation details may evolve provided
that public semantics and documented compatibility guarantees are preserved.


## 9. Architectural Regression Testing

CPC distinguishes between functional correctness tests, physical
validation tests, and architectural regression tests.

Architectural regression tests verify structural properties of the
implementation rather than numerical results.

Examples include:

- the RC backend MUST NOT invoke the public compiler entry point;
- the public compiler MUST delegate through the canonical IR pipeline.

Architectural changes SHALL introduce corresponding architectural
regression tests.

## 10. Compatibility Policy

The following compatibility surfaces are stable:

- `compile_parity_instance()`;
- `ParityConstraint`;
- `ParityInstance`;
- `CompilationStatistics`;
- `CompiledParityNetwork`; and
- the documented semantics of `IRProgram`.

The following implementation details MAY evolve:

- backend internals;
- emitter internals;
- optimization strategies;
- module-internal helper functions; and
- internal serialization choices.

A change that alters public semantics, the canonical pipeline, IR meaning,
or backend responsibilities SHALL require an RFC, migration notes, and
appropriate architectural regression tests.

## 11. Evolution Strategy

CPC SHALL evolve by extending the canonical architecture rather than by
introducing parallel compilation paths.

Supported extension mechanisms include:

- additional logical front ends;
- IR validation passes;
- semantics-preserving optimization passes;
- additional backends;
- backend-specific emitters;
- physical validation adapters; and
- backend discovery or registration mechanisms.

New front ends SHALL produce valid IR.
New backends SHALL consume valid IR.
New emitters SHALL remain backend-specific.

Extensions MUST NOT bypass the canonical IR pipeline or embed independently
computed continuation answers into compiled artifacts.

## 12. Future RFCs

The following RFCs are anticipated:

- RFC-0002: Backend Interface;
- RFC-0003: IR Invariants;
- RFC-0004: Backend Registry;
- RFC-0005: Testing Strategy; and
- RFC-0006: Optimization Passes.

These RFCs SHALL refine specific extension points without contradicting the
architectural principles and canonical pipeline established here.

## 13. Architecture Compliance

An implementation conforms to RFC-0001 if it satisfies all mandatory
requirements defined in this document.

In particular, a conforming implementation SHALL:

- preserve the canonical compilation pipeline;
- construct backend-independent IR before backend compilation;
- compile all physical realizations from IR;
- preserve the documented public compatibility surface; and
- maintain architectural regression tests protecting these invariants.

Changes that violate these requirements constitute architectural changes
and therefore require an updated or superseding RFC.
