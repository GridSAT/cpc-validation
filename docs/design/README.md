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
- RFC-0002 — Generic Constraint IR and CNF Front End — Accepted

- RFC-0003 — Backend Execution Contract — Accepted
