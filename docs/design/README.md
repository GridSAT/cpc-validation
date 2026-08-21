# CPC Design RFCs

This directory contains normative and proposed architecture documents for
the CPC Validation project.

## Purpose

RFCs record architectural intent separately from implementation details.
Accepted RFCs define the design constraints that future code and tests
must preserve.

## Status values

- Draft
- Review
- Accepted
- Superseded
- Withdrawn

## Lifecycle

1. A nontrivial architectural change begins as a Draft RFC.
2. The RFC is reviewed before implementation.
3. Accepted RFCs become normative.
4. Implementation commits should reference the authorizing RFC.
5. Superseded RFCs remain in the repository for historical context.

## Scope

RFCs are required for changes to:

- the canonical compilation pipeline;
- public APIs;
- IR semantics or invariants;
- backend contracts;
- module responsibilities;
- compatibility guarantees; or
- architectural testing requirements.

Routine bug fixes, documentation corrections, and implementation-preserving
refactors do not require a new RFC.
## RFC Index

- RFC-0001 — CPC Architecture — Accepted
- RFC-0002 — Generic Constraint IR and CNF Front End — Accepted
- RFC-0003 — Backend Execution Contract — Accepted
- RFC-0004 — Physical Execution Backend Engineering and Conformance — Accepted
- RFC-0005 — Cross-Backend Equivalence and Validation — Accepted
- RFC-0006 — Cross-Backend Benchmark Validation and Reproducibility — Accepted
- RFC-0007 — Backend Qualification and Conformance Manifests — Accepted
- RFC-0008 — FPGA Execution Backend and Tri-Backend Validation — Accepted
- RFC-0009 — Physical Execution Evidence and Substrate Conformance — Accepted
- RFC-0010 — Driven-Dissipative Open-System Execution and Referenced Readout — Accepted
