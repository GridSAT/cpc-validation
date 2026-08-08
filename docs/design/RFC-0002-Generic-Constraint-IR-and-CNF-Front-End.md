# RFC-0002: Generic Constraint IR and CNF Front End

| Field | Value |
|---|---|
| RFC | RFC-0002 |
| Title | Generic Constraint IR and CNF Front End |
| Status | Accepted |
| Version | 1.0 |
| Author | Karim Daghbouche |
| Created | 2026-08-06 |
| Updated | 2026-08-06 |

## Normative Language

The key words **MUST**, **MUST NOT**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, and **MAY** are normative requirements.

## Implementation Status

This RFC specifies the accepted target architecture.

The CNF source model, DIMACS parser, and independent CNF reference
semantics are implemented. CCIR, source-model lowering, and CCIR backend
migration remain to be implemented through separate atomic commits.

Acceptance of this RFC approves the design; it does not assert that every
acceptance criterion in Section 12 has already been implemented.

## 1. Purpose

This RFC extends the CPC architecture from a parity-specific front end to
multiple source languages while preserving the canonical architecture
defined by RFC-0001.

The first additional source language is DIMACS CNF.

DIMACS is an external interchange format.
CNF is a source model.
Neither defines the backend architecture.

## 2. Architectural Goal

The CPC architecture shall become:

    Source Model
         │
         ▼
     Front End
         │
         ▼
Generic Constraint IR
         │
         ▼
      Backend
         │
         ▼
      Emitter

Parity and CNF become independent front ends targeting the same IR.

## 3. Scope

This RFC defines:

- the generic constraint IR;
- the CNF source model;
- the DIMACS front end;
- preservation of the parity front end; and
- lowering into the generic constraint IR.

Implementation details are intentionally left to later commits.

## 4. Terminology

**Core Constraint Intermediate Representation (CCIR)**

The canonical backend-independent representation shared by CPC front ends,
analysis passes, optimization passes, and backends.

**Source model**

A typed representation of one admitted source language before lowering.
`ParityInstance` and `CNFInstance` are source models.

**Front end**

A component that translates one source model into CCIR.

**Constraint family**

A typed semantic relation represented in CCIR. The initial families are
parity constraints and clauses.

**Lowering**

A semantics-preserving translation from a source model into CCIR.

## 5. CCIR Responsibilities

CCIR SHALL preserve the semantic content required to evaluate every admitted
constraint under a complete Boolean assignment.

CCIR SHALL represent:

- declared variables;
- variable roles, where applicable;
- typed constraints; and
- backend-independent semantic metadata required to preserve the meaning of
  the source model.

CCIR describes the logical constraint system. It does not prescribe a
particular execution strategy, search procedure, optimization, or physical
realization.

CCIR SHALL NOT encode:

- DIMACS line numbers, comments, whitespace, or token layout;
- parity-benchmark JSON formatting;
- independently computed continuation answers;
- ngspice syntax; or
- backend-specific artifact text.

## 6. Typed Constraint Families

CCIR SHALL represent constraints as typed semantic relations rather than as
an unrestricted Boolean-expression syntax tree.

The initial constraint families are:

### 6.1 Parity

A parity constraint requires the XOR of its declared variables to equal one
Boolean parity value.

### 6.2 Clause

A clause constraint requires at least one of its signed literals to evaluate
to true. An empty clause evaluates to false.

Constraint-family payloads SHALL be immutable and validated independently.
A backend MAY support one or more admitted families, but it SHALL reject
unsupported families explicitly.

Additional constraint families MAY be standardized by later RFCs without
changing the semantics of existing families.

## 7. Front-End Lowering Rules

Each front end SHALL accept exactly one source model and produce CCIR.

The parity front end SHALL lower `ParityInstance` objects into parity-family
CCIR constraints.

The CNF front end SHALL lower `CNFInstance` objects into clause-family CCIR
constraints.

Lowering SHALL be semantics-preserving.

In particular, lowering SHALL preserve:

- declared variables;
- boundary and internal-variable roles;
- constraint semantics;
- deterministic ordering; and
- admitted interface information.

Lowering SHALL NOT compute or embed a continuation answer.

## 8. Analysis and Optimization Boundaries

CCIR MAY be consumed by analysis and optimization passes before backend
compilation.

Analysis passes MAY validate invariants, compute statistics, or report
structural properties.

Analysis passes SHALL NOT modify CCIR.

Optimization passes MAY transform CCIR only when continuation semantics are
preserved exactly.

Front ends SHALL NOT perform backend-specific optimization.
Backends SHALL NOT perform source-language parsing or lowering.

The concrete pass interface is outside the scope of this RFC.

## 9. Migration from the Existing IR

The current intermediate representation is parity-oriented and will be superseded incrementally by CCIR.
Migration to CCIR SHALL occur incrementally.

The migration sequence is:

1. introduce CCIR types without changing existing compilation behavior;
2. lower parity source models into CCIR;
3. lower CNF source models into CCIR;
4. update the RC backend to consume CCIR;
5. preserve public compatibility wrappers during migration; and
6. retire the legacy parity-specific IR only after complete regression and
   physical validation.

At no point SHALL two independent canonical compilation pipelines be
maintained as permanent architecture.

## 10. Architectural Invariants

A conforming implementation SHALL preserve all of the following invariants:

1. Every admitted source model is lowered into CCIR before backend compilation.
2. CCIR remains independent of DIMACS, JSON, ngspice, and other concrete formats.
3. Constraint families are represented by typed semantic payloads.
4. Front ends do not perform backend-specific work.
5. Backends do not parse or interpret source-language syntax.
6. Emitters do not determine logical semantics.
7. No compiled artifact contains an independently computed continuation answer.
8. Parity and CNF lowerings preserve exact continuation semantics.
9. Every architectural layer has one well-defined input representation and
   one well-defined output representation.

## 11. Implementation Sequence

Implementation SHALL proceed in independently reviewable commits.

The intended sequence is:

1. introduce CCIR program and constraint types;
2. introduce parity-family CCIR payloads;
3. introduce clause-family CCIR payloads;
4. lower `ParityInstance` into CCIR;
5. lower `CNFInstance` into CCIR;
6. validate semantic equivalence against independent reference semantics;
7. update the RC backend to consume CCIR;
8. preserve compatibility wrappers and byte-compatible parity output;
9. run complete Python and physical regressions; and
10. retire the legacy parity-specific IR after migration is complete.

Each commit SHALL implement no more than one architectural idea.

## 12. Compatibility and Acceptance Criteria

RFC-0002 is implemented only when all of the following are true:

- the existing parity public API remains operational;
- parity compilation traverses CCIR;
- CNF source models lower into CCIR;
- the RC backend consumes CCIR;
- parity netlist output remains byte-compatible unless separately documented;
- CNF semantics agree with the independent reference semantics;
- architectural regression tests protect the CCIR pipeline;
- all existing regression tests continue to pass throughout migration;
- the complete Python regression passes; and
- the established SPICE validation remains successful.

Acceptance of this RFC does not itself claim efficient SAT compilation,
polynomial scaling, or a passive hardware implementation.
