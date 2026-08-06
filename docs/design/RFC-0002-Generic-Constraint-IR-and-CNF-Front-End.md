# RFC-0002: Generic Constraint IR and CNF Front End

| Field | Value |
|---|---|
| RFC | RFC-0002 |
| Title | Generic Constraint IR and CNF Front End |
| Status | Draft |
| Version | 0.1 |
| Author | Karim Daghbouche |
| Created | 2026-08-06 |
| Updated | 2026-08-06 |

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
