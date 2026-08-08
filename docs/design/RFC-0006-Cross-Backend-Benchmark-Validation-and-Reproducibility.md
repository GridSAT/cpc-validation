# RFC-0006: Cross-Backend Benchmark Validation and Reproducibility

**Status:** Draft  
**Category:** CPC Validation Architecture  
**Depends on:** RFC-0001, RFC-0002, RFC-0003, RFC-0004, RFC-0005

---

# 1. Abstract

This RFC defines the CPC architecture for systematic cross-backend validation
over benchmark corpora.

RFC-0005 establishes comparison of heterogeneous execution backends for one
canonical CCIR program and one admitted boundary assignment. RFC-0006 lifts
that validation procedure to finite benchmark corpora and finite sets of
admitted boundary assignments.

For every benchmark case, the same canonical CCIR program is compiled,
prepared, executed, observed, and decoded independently by each participating
backend. Backend agreement is evaluated only after execution. Each decoded
result is additionally compared against an independent canonical semantic
reference.

RFC-0006 further defines deterministic benchmark discovery, exhaustive
boundary enumeration where applicable, machine-readable validation records,
aggregate summaries, reproducibility requirements, and corpus-level acceptance
criteria.

Finite benchmark success is evidence of implementation conformance over the
tested corpus. It is not a proof of universal semantic correctness, backend
equivalence, computational complexity, or physical realizability beyond the
executed cases.

---

# 2. Motivation

A single cross-backend execution demonstrates that heterogeneous backend
realizations can be compared under the CPC architecture.

A validation framework intended to support backend engineering requires more.

It must be possible to execute a permanent or generated benchmark corpus,
enumerate admitted boundary conditions deterministically, preserve the identity
of every tested case, compare heterogeneous backend results, compare each
backend independently against canonical semantics, and emit reproducible
machine-readable evidence.

RFC-0006 standardizes that layer.

---

# 3. Scope

RFC-0006 specifies:

- benchmark-corpus discovery;
- deterministic benchmark ordering;
- canonical lowering of each benchmark;
- finite boundary-case enumeration;
- reuse of the RFC-0005 cross-backend validation procedure;
- backend-agreement recording;
- independent semantic-match recording;
- per-case validation records;
- aggregate corpus summaries;
- deterministic report schemas;
- failure propagation;
- reproducibility requirements; and
- corpus-level acceptance criteria.

RFC-0006 does not define:

- new CCIR semantics;
- new backend compilation rules;
- backend preparation semantics;
- backend execution semantics;
- decoder semantics;
- probabilistic statistical certification;
- universal program equivalence;
- universal backend correctness;
- complexity-theoretic conclusions; or
- physical claims beyond the executed backend realization.

Those responsibilities remain with the appropriate preceding RFCs or future
extensions.

---

# 4. Architectural Position

The RFC-0006 validation architecture is:

    Benchmark Corpus
          |
          v
    Deterministic Discovery
          |
          v
    Benchmark
          |
          v
    Canonical Lowering
          |
          v
    CCIR Program
          |
          v
    Boundary Enumeration
          |
          v
    (program, boundary assignment)
          |
          v
    RFC-0005 Cross-Backend Validation
          |
          +---------------+
          v               v
    Backend Agreement   Independent Semantic Matches
          |               |
          +-------+-------+
                  v
           Per-Case Record
                  |
                  v
           Corpus Aggregation
                  |
                  v
         Machine-Readable Reports

RFC-0006 does not enter any backend dependency graph.

---

# 5. Terminology

## 5.1 Benchmark

A benchmark is an admitted source representation that can be canonically
lowered to CCIR.

## 5.2 Benchmark Corpus

A benchmark corpus is a finite ordered collection of benchmark inputs selected
for validation.

## 5.3 Boundary Assignment

A boundary assignment is an admitted assignment to the boundary variables of a
canonical CCIR program.

## 5.4 Benchmark Case

A benchmark case is the pair

    K = (C_X, b)

where `C_X` is a canonical CCIR program and `b` is one admitted boundary
assignment.

## 5.5 Cross-Backend Case Result

A cross-backend case result is the RFC-0005 validation result associated with
one benchmark case.

## 5.6 Corpus Validation Result

A corpus validation result is the ordered collection of all cross-backend case
results together with aggregate validation counts.

---

# 6. Deterministic Benchmark Discovery

Benchmark discovery shall be deterministic.

Given the same input files and directories, the validator shall discover the
same benchmark set in the same order.

Directory traversal shall not depend on filesystem enumeration order.

Only admitted benchmark files shall enter the corpus.

Duplicate benchmark paths shall not create duplicate validation cases.

Discovery itself shall perform no semantic evaluation.

---

# 7. Canonical Lowering

Each discovered benchmark shall be lowered through the canonical frontend
defined by RFC-0001 and RFC-0002.

Backend-specific code shall not participate in canonical lowering.

Semantically irrelevant source ordering that is not admitted by canonical CCIR
shall be normalized during lowering.

For parity-family constraints, variable identifiers within a constraint are
represented in canonical sorted order.

This normalization is structural. It does not evaluate the constraint or
derive its response.

---

# 8. Boundary Enumeration

For a benchmark with finite Boolean boundary variables

    B = (b_0, ..., b_{k-1}),

exhaustive validation enumerates all assignments in

    {0,1}^k.

The enumeration order shall be deterministic.

Each assignment shall be represented canonically so that the same benchmark
case has the same machine-readable identity across repeated runs.

Future RFCs may define sampled or non-Boolean boundary domains. Such procedures
shall be distinguished explicitly from exhaustive Boolean enumeration.

---

# 9. Cross-Backend Execution

Each benchmark case shall be validated through the RFC-0005 cross-backend
validation procedure.

For every participating backend:

    CCIR
      |
      v
    Compile_backend
      |
      v
    ExecutionArtifact
      |
      v
    Preparation
      |
      v
    PreparedExecution
      |
      v
    Execution
      |
      v
    ObservableExecution
      |
      v
    Fixed Decoder
      |
      v
    Decoded Result

No backend may consume another backend's artifact, prepared state, observation,
decoded result, or semantic reference result.

---

# 10. Independent Semantic Reference

Canonical semantic evaluation shall remain outside all backend dependency
graphs.

For each benchmark case, the independent reference result shall be computed
from admitted canonical semantics and the admitted boundary assignment.

The reference result shall not enter:

- backend compilation;
- backend preparation;
- backend execution;
- observation;
- decoding; or
- backend-to-backend comparison.

---

# 11. Backend Agreement

For two backends with decoded results `d_1` and `d_2`:

    backend_agreement := (d_1 = d_2)

For more than two backends, agreement requires equality of all decoded results.

Backend agreement is a cross-implementation consistency condition.

It is not sufficient evidence of semantic correctness.

---

# 12. Semantic Match

For backend `i` with decoded result `d_i` and independent reference result `e`:

    semantic_match_i := (d_i = e)

Semantic match is recorded independently for every backend.

A backend may agree with another backend while both fail semantic validation.

Therefore backend agreement and semantic correctness shall remain separate
fields.

---

# 13. Per-Case Overall Result

For a benchmark case with participating backends `1 ... n`:

    overall_case_pass :=
        backend_agreement
        AND semantic_match_1
        AND ...
        AND semantic_match_n

Failure of any required condition causes the benchmark case to fail.

---

# 14. Validation Record

Every benchmark case shall produce a machine-readable validation record.

The record shall identify at minimum:

- benchmark identity;
- benchmark path or equivalent corpus identity;
- canonical boundary assignment;
- participating backend identities and versions;
- execution-engine identities where available;
- decoded backend results;
- independent reference result;
- backend-agreement result;
- per-backend semantic-match results; and
- overall case result.

The current reference CSV representation is:

    benchmark
    benchmark_path
    boundary
    rc_backend
    rc_execution_engine
    rc_decoded
    digital_backend
    digital_execution_engine
    digital_decoded
    reference_result
    backend_agreement
    rc_semantic_match
    digital_semantic_match
    overall_pass

Backend-specific column names are a reference implementation schema, not a
restriction that RFC-0006 supports only two backend families.

---

# 15. Corpus Aggregation

For a finite corpus producing case results

    R = (R_1, ..., R_m),

the validator shall compute aggregate counts including:

- benchmark count;
- boundary-case count;
- backend-agreement passes and failures;
- semantic-match passes and failures for every backend;
- overall passes and failures; and
- corpus-level overall result.

The corpus passes only if every required benchmark case passes.

---

# 16. Machine-Readable Summary

The reference implementation emits a JSON summary.

The current schema identifier is:

    cpc.cross-backend-summary.v1

The summary records aggregate corpus information and shall be deterministic for
the same admitted corpus, backend implementations, execution environment, and
validation configuration, subject to explicitly recorded environment-dependent
metadata.

Schema evolution shall use a new schema identifier when compatibility would
otherwise be broken.

---

# 17. Report Determinism

Report ordering shall be deterministic.

Given equivalent admitted inputs and equivalent execution results:

- benchmark ordering shall be stable;
- boundary ordering shall be stable;
- validation-record ordering shall be stable;
- field names shall be stable within one schema version; and
- aggregate counts shall be reproducible.

Timestamps, temporary paths, process identifiers, or other incidental runtime
state shall not be required components of canonical validation identity.

---

# 18. Reproducibility

A corpus validation claim shall identify enough information to reconstruct the
validation context.

At minimum this includes:

- corpus identity;
- benchmark inputs;
- backend identities and versions;
- report schema version; and
- execution-environment metadata required by the participating backends under
  RFC-0004.

A stored validation report is evidence for the execution that produced it.

It does not replace the executable benchmark corpus or validation procedure.

---

# 19. Generated Benchmarks

Generated benchmarks may participate in an RFC-0006 corpus.

A generated benchmark shall have reproducible construction parameters.

Where pseudorandom generation is used, the seed shall be explicit.

Generated benchmark identity should encode or otherwise preserve sufficient
generation information to reproduce the benchmark.

Generated benchmarks are subject to the same canonical lowering and validation
rules as permanent hand-authored benchmarks.

---

# 20. Permanent Benchmarks

A repository may designate selected benchmarks as permanent regression cases.

Permanent benchmarks should remain stable once published unless a defect in the
benchmark itself is identified.

Changes to permanent benchmark semantics shall be treated as validation-corpus
changes rather than ordinary implementation refactoring.

---

# 21. Failure Semantics

The validator shall not conceal partial failure.

The following conditions cause failure of the affected benchmark case:

- backend disagreement;
- failure of any required backend semantic match;
- backend compilation failure;
- preparation failure;
- execution failure;
- observation failure;
- decoding failure;
- reference-evaluation failure; or
- malformed admitted validation input.

Corpus-level success requires success of every required case.

---

# 22. Empty Corpus

An empty discovered corpus shall not be reported as successful validation.

A validation invocation that discovers no admitted benchmarks shall fail or
produce an explicitly non-passing result.

This prevents vacuous corpus-level success.

---

# 23. Evidence Boundary

RFC-0006 validation establishes finite empirical evidence.

If all cases in corpus `K` pass, the supported statement is:

    All executed RFC-0006 validation cases in K passed.

The result does not establish:

    all possible programs pass

or

    all possible boundary assignments for programs outside K pass

or

    all conforming backends are semantically equivalent

or

    the backend architecture proves a complexity-theoretic claim.

Corpus validation shall not be presented as universal proof.

---

# 24. Reference Implementation

The current reference implementation provides:

    src/cross_backend_benchmarks.py
    validate_cross_backend_benchmarks.py

The implementation supports deterministic discovery of parity benchmarks,
exhaustive Boolean boundary enumeration, RFC-0005 RC/digital cross-backend
validation, CSV case reports, and JSON aggregate summaries.

The currently implemented heterogeneous execution paths are:

    RC backend
        ngspice execution

    Digital backend
        deterministic Python digital interpreter

Both remain independently validated against canonical CCIR semantics.

---

# 25. Conformance Requirements

An RFC-0006 implementation shall satisfy the following requirements.

## BV-1 — Deterministic Discovery

Benchmark discovery shall be deterministic.

## BV-2 — Canonical Input

Every benchmark shall be lowered through canonical CCIR before backend
execution.

## BV-3 — Deterministic Boundary Enumeration

Finite exhaustive boundary enumeration shall have deterministic ordering.

## BV-4 — RFC-0005 Reuse

Every benchmark case shall use the RFC-0005 cross-backend validation
architecture.

## BV-5 — Backend Isolation

Participating backends shall execute independently.

## BV-6 — Reference Isolation

Independent semantic evaluation shall remain outside backend dependency graphs.

## BV-7 — Agreement Separation

Backend agreement shall be recorded separately from semantic correctness.

## BV-8 — Per-Backend Semantic Validation

Every required backend shall be compared independently with canonical
semantics.

## BV-9 — Machine-Readable Evidence

Every executed case shall be representable in a machine-readable validation
record.

## BV-10 — Deterministic Aggregation

Corpus summaries and record ordering shall be deterministic.

## BV-11 — Failure Propagation

Any required case failure shall cause corpus-level validation failure.

## BV-12 — Non-Vacuity

An empty corpus shall not produce a successful validation result.

## BV-13 — Reproducibility Metadata

The validation context shall preserve sufficient backend and environment
identity for reproduction.

## BV-14 — Evidence-Boundary Discipline

Finite corpus success shall not be represented as universal correctness proof.

---

# 26. Security Considerations

RFC-0006 specifies validation architecture rather than operational security.

Benchmark files remain untrusted external inputs and should be parsed under the
input-validation requirements of the relevant frontend.

Backend execution may invoke external execution engines. Operational isolation,
resource limits, sandboxing, and deployment security remain implementation
concerns.

---

# 27. Future Extensions

Future RFC-0006-compatible extensions may include:

- additional backend families;
- larger permanent corpora;
- reproducible benchmark generators;
- sampled validation for large boundary spaces;
- randomized differential testing;
- property-based benchmark generation;
- execution-time and resource metadata;
- artifact hashes;
- signed validation manifests;
- continuous-integration validation snapshots;
- FPGA backends;
- optical backends;
- coherent physical substrates;
- C-parity execution backends; and
- remote heterogeneous execution environments.

Such extensions shall preserve backend isolation, independent semantic
validation, reproducible case identity, and the distinction between finite
validation evidence and universal proof.

---

# 28. Acceptance Criteria

RFC-0006 is accepted when the reference implementation demonstrates:

- deterministic benchmark discovery;
- canonical lowering for the complete admitted corpus;
- exhaustive deterministic Boolean boundary enumeration;
- heterogeneous RC and digital backend execution;
- independent semantic validation for every executed case;
- separate backend-agreement and semantic-match fields;
- deterministic CSV case reporting;
- deterministic JSON aggregate reporting;
- explicit report-schema identity;
- failure propagation;
- non-vacuous corpus validation;
- regression tests for the corpus-validation API;
- regression tests for the corpus-validation CLI; and
- complete repository regression without failure.

Acceptance applies only to the finite benchmark corpus actually executed.

---
