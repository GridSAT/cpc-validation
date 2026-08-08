# RFC-0005

# Cross-Backend Equivalence and Independent Validation

**Status:** Draft

---

# Abstract

RFC-0005 defines the architectural requirements for executing one canonical
Constraint Physical Computing (CPC) program through multiple conforming
execution backends and comparing their decoded results independently of backend
implementation.

The RFC distinguishes two logically separate properties:

1. **backend agreement**, meaning that independently executed backends produce
   the same decoded result; and
2. **semantic correctness**, meaning that a decoded backend result agrees with
   an independent evaluation of the canonical CCIR semantics.

Backend agreement alone is not sufficient to establish correctness. Two
backends may agree while producing the same incorrect result.

RFC-0005 therefore defines a cross-backend validation architecture in which
each backend independently satisfies the RFC-0003 compilation contract and the
RFC-0004 execution lifecycle, after which decoded backend results are compared
with one another and independently with canonical CCIR semantics.

The current reference implementation realizes this architecture using two
structurally distinct execution technologies:

- the RC Reference Backend executed through ngspice; and
- a deterministic digital execution backend implemented as a compiled
  instruction representation interpreted independently of CCIR reference
  evaluation.

The purpose of RFC-0005 is not to prescribe either execution technology.
Rather, it establishes executable evidence that backend interchangeability is
an architectural property of CPC rather than a property of a single reference
implementation.

---

# 1. Scope

RFC-0005 specifies the architecture for cross-backend execution and validation
of canonical CCIR programs.

It defines requirements for:

- execution of one CCIR program through multiple conforming CPC backends;
- independent backend compilation;
- independent backend preparation and execution;
- backend-specific observable interfaces and fixed decoders;
- comparison of decoded backend results;
- independent semantic reference evaluation;
- separation of backend agreement from semantic correctness;
- cross-backend validation records;
- reproducibility of cross-backend runs; and
- backend heterogeneity.

RFC-0005 does not prescribe:

- a particular physical substrate;
- a particular execution mechanism;
- a shared backend topology;
- a shared execution engine;
- shared preparation procedures;
- shared observable quantities;
- shared decoder internals;
- performance equivalence;
- timing equivalence;
- energy equivalence; or
- implementation equivalence.

Two backends may therefore be conforming even when their internal realization,
execution dynamics, and observable interfaces differ completely.

---

# 2. Relationship to Earlier RFCs

RFC-0005 builds upon the architectural contracts established by RFC-0001
through RFC-0004.

## 2.1 RFC-0001

RFC-0001 defines the CPC architecture and establishes the separation between
constraint representation and computational realization.

## 2.2 RFC-0002

RFC-0002 defines the Canonical Constraint Intermediate Representation (CCIR)
as the stable architectural boundary between frontends and execution backends.

All backends participating in an RFC-0005 comparison consume the same canonical
CCIR program.

## 2.3 RFC-0003

RFC-0003 defines the backend compilation contract:

    Compile_backend : CCIR -> ExecutionArtifact

and establishes:

- backend capability declarations;
- deterministic compilation;
- ExecutionArtifact structure;
- machine-checkable provenance;
- Answer Independence;
- restricted interfaces; and
- independent semantic validation.

For an admitted CCIR program `C_X`, RFC-0003 requires the compiler dependency
condition:

    D(C_X) = { C_X, Theta_backend }

where `Theta_backend` is the globally fixed backend specification.

## 2.4 RFC-0004

RFC-0004 defines the execution lifecycle following compilation:

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

RFC-0005 composes multiple independently conforming RFC-0003/RFC-0004 backend
realizations under one external comparison and validation procedure.

---

# 3. Terminology

For the purposes of RFC-0005:

**Canonical program**

An admitted CCIR program supplied identically to every participating backend.

**Backend**

A conforming implementation of the CPC execution-backend contracts.

**Backend realization**

The complete backend-specific path from CCIR compilation through preparation,
execution, observation, and fixed decoding.

**Decoded result**

The semantic output produced by a backend's fixed decoder from its admitted
observable interface.

**Backend agreement**

Equality of decoded results produced by two or more backend realizations for
the same canonical program and admitted interface input.

**Independent reference result**

The result of evaluating canonical CCIR semantics using a procedure outside
all participating backend dependency graphs.

**Semantic match**

Equality between one backend's decoded result and the independent reference
result.

**Cross-backend validation**

The external procedure that records backend agreement and semantic matches
without participating in backend compilation or execution.

---

# 4. Cross-Backend Execution Model

Let `C` be one admitted CCIR program.

Let

    B_1, B_2, ..., B_n

be conforming CPC execution backends.

Each backend independently compiles `C`:

    A_i = Compile_Bi(C)

where `A_i` is the backend-specific ExecutionArtifact.

Each backend then independently performs its RFC-0004 execution lifecycle:

    P_i = Prepare_Bi(A_i, I)

    O_i = Execute_Bi(P_i)

    d_i = Decode_Bi(O_i)

where:

- `I` is the admitted interface input;
- `P_i` is the PreparedExecution;
- `O_i` is the ObservableExecution; and
- `d_i` is the decoded backend result.

The resulting backend paths may therefore be represented as:

                         CCIR C
                           |
              +------------+------------+
              |                         |
              v                         v
          Backend B1                Backend B2
              |                         |
              v                         v
       ExecutionArtifact 1       ExecutionArtifact 2
              |                         |
              v                         v
       PreparedExecution 1       PreparedExecution 2
              |                         |
              v                         v
          Execution 1               Execution 2
              |                         |
              v                         v
      ObservableExecution 1     ObservableExecution 2
              |                         |
              v                         v
        Fixed Decoder 1           Fixed Decoder 2
              |                         |
              v                         v
             d_1                       d_2

No backend is permitted to consume the output of another backend as an input to
compilation, preparation, execution, or decoding.

---

# 5. Canonical Input Identity

Every backend participating in one cross-backend validation run shall operate
on the same canonical CCIR program.

The validator shall not compare executions originating from semantically
similar but structurally different frontend programs and describe them as one
canonical cross-backend run.

The canonical identity condition is therefore:

    C_1 = C_2 = ... = C_n = C

at the architectural backend input boundary.

Frontend syntax is irrelevant after canonical lowering.

For example, if a source problem originated as a parity benchmark, DIMACS
instance, graph formulation, or another admitted frontend representation, the
cross-backend comparison begins only after canonical lowering to CCIR.

---

# 6. Independent Backend Compilation

Each backend shall compile the canonical program independently.

For backend `B_i`:

    A_i = Compile_Bi(C)

shall depend only upon:

    { C, Theta_Bi }

in accordance with RFC-0003.

In particular, compilation of one backend shall not depend upon:

- another backend's ExecutionArtifact;
- another backend's prepared state;
- another backend's observations;
- another backend's decoded result;
- the independent semantic reference result; or
- expected benchmark answers.

Cross-backend comparison therefore occurs strictly downstream of independent
backend execution.

---

# 7. Backend Heterogeneity

Cross-backend validation is intended to compare genuinely distinct execution
realizations.

Participating backends may differ in:

- execution topology;
- artifact structure;
- backend parameters;
- preparation procedure;
- execution engine;
- execution dynamics;
- observable interface;
- decoder specification;
- implementation language;
- simulation technology;
- hardware technology; or
- physical substrate.

RFC-0005 does not require a quantitative measure of backend heterogeneity.

However, implementations claiming heterogeneous cross-backend validation shall
not obtain the second backend result merely by calling or wrapping the first
backend implementation.

Likewise, a backend shall not obtain its decoded result by invoking the
independent semantic reference evaluator.

The current reference pair is intentionally heterogeneous:

**RC Reference Backend**

- electrical RC execution artifact;
- ngspice preparation/execution path;
- voltage observation;
- threshold-based fixed decoder.

**Digital Backend**

- deterministic instruction-derived execution artifact;
- immutable digital prepared program;
- deterministic digital interpreter;
- result-bit observation;
- fixed digital result decoder.

These realizations share canonical semantics but not execution topology or
execution engine.

---

# 8. Backend Agreement

For two backend realizations producing decoded results `d_1` and `d_2`,
backend agreement is defined by:

    d_1 = d_2

For `n` backends, backend agreement requires:

    d_1 = d_2 = ... = d_n

Backend agreement is a consistency condition only.

It shall not be interpreted as proof of semantic correctness.

In particular:

    d_1 = d_2

does not imply:

    d_1 = e

where `e` is the independent semantic reference result.

This distinction is normative.

A cross-backend validator shall expose backend agreement separately from
semantic correctness.

---

# 9. Independent Semantic Reference

Let:

    e = Eval_CCIR(C, I)

denote independent semantic evaluation of the canonical CCIR program under the
admitted interface input `I`.

The independent evaluator shall remain outside every participating backend
dependency graph.

It shall not participate in:

- backend compilation;
- ExecutionArtifact construction;
- backend preparation;
- substrate execution;
- observation generation;
- backend decoding; or
- backend-internal optimization.

Conceptually:

                    Backend paths
                         |
                         v
                 decoded results
                         |
                         |
        ==============================
        backend dependency boundary
        ==============================
                         |
                         v
                  external comparison
                         ^
                         |
               independent e
                         ^
                         |
                 CCIR semantics

The reference evaluator may inspect the canonical CCIR program and the admitted
interface input because those objects define the semantics being independently
checked.

---

# 10. Semantic Match

Backend `B_i` semantically matches the canonical program when:

    d_i = e

For two backends, successful cross-backend semantic validation therefore
requires:

    d_1 = e

and:

    d_2 = e

Backend agreement then follows when the decoded outputs are deterministic.

The stronger relation may be written:

    d_1 = d_2 = e

RFC-0005 nevertheless requires these properties to be recorded separately so
that failure modes remain distinguishable.

---

# 11. Cross-Backend Validation Record

A cross-backend validation record shall expose sufficient information to audit
the comparison.

For a two-backend comparison, the record shall contain at least:

- backend 1 identity;
- backend 1 version;
- backend 1 decoded result;
- backend 2 identity;
- backend 2 version;
- backend 2 decoded result;
- independent reference result;
- backend-agreement status;
- backend 1 semantic-match status;
- backend 2 semantic-match status; and
- overall validation status.

The reference implementation additionally retains each backend's RFC-0004
execution result so that prepared state, observable execution, provenance, and
execution metadata remain available for inspection.

---

# 12. Overall Validation Condition

For two backends, let:

    A = [d_1 = d_2]

    S_1 = [d_1 = e]

    S_2 = [d_2 = e]

The overall cross-backend result is:

    PASS = A AND S_1 AND S_2

Thus:

- backend agreement without semantic matches is FAIL;
- one semantic match and one mismatch is FAIL;
- semantic matches without backend agreement are inconsistent and therefore
  FAIL;
- only complete agreement with the independent semantics is PASS.

This requirement prevents cross-backend consensus from being mistaken for
correctness.

---

# 13. Separation Principle

Cross-backend validation shall remain external to backend implementation.

The architectural structure is:

                         CCIR
                          |
             +------------+------------+
             |                         |
             v                         v
         Backend A                 Backend B
             |                         |
             v                         v
           d_A                       d_B
             |                         |
             +------------+------------+
                          |
                          v
                  backend comparison


                    CCIR semantics
                          |
                          v
              independent reference e
                          |
                          v
                  semantic comparison

No path carrying `e` may enter:

- `Compile_A`;
- `Compile_B`;
- `Prepare_A`;
- `Prepare_B`;
- `Execute_A`;
- `Execute_B`;
- `Decode_A`; or
- `Decode_B`.

---

# 14. Provenance Preservation

RFC-0005 does not replace the provenance requirements of RFC-0003 and
RFC-0004.

Each backend shall retain its own machine-checkable provenance independently.

Cross-backend validation does not require artifacts from different backends to
have identical provenance structures.

Instead, each backend's artifact elements shall remain traceable to:

- admitted CCIR origins; or
- globally fixed backend rules.

The fact that two backends implement the same CCIR program does not imply that
their artifact elements correspond one-to-one.

For example, an RC candidate source and a digital parity instruction may have
different backend-rule origins while ultimately tracing to the same canonical
constraint.

---

# 15. Interface Independence

Participating backends are not required to expose identical physical or
implementation-level observables.

One backend may expose:

- voltages;
- currents;
- timing events; or
- other physical quantities.

Another may expose:

- digital registers;
- logical values;
- symbolic states; or
- hardware interface signals.

Cross-backend comparison occurs only after each backend's fixed decoder has
mapped admitted observations into the common semantic result domain.

Therefore:

    ObservableExecution_A != ObservableExecution_B

is permitted even when:

    Decode_A(O_A) = Decode_B(O_B)

This distinction is central to substrate independence.

---

# 16. Reproducibility

A cross-backend validation run shall make available sufficient information for
independent reproduction.

At minimum this includes:

- identity of the canonical CCIR program;
- admitted boundary/interface input;
- participating backend identities;
- participating backend versions;
- preparation identifiers where applicable;
- execution-engine identifiers;
- execution-engine versions where available;
- decoded backend outputs;
- independent semantic reference result; and
- comparison outcome.

Run-specific information that does not affect reproducibility need not be part
of the canonical validation record.

---

# 17. Reference Implementation

The CPC Reference Validation Framework currently implements RFC-0005 using two
execution backends.

## 17.1 RC Reference Backend

The RC Reference Backend compiles CCIR into an electrical ExecutionArtifact.

Its RFC-0004 lifecycle is:

    CCIR
      |
      v
    RC ExecutionArtifact
      |
      v
    RC netlist preparation
      |
      v
    PreparedExecution
      |
      v
    ngspice execution
      |
      v
    ObservableExecution
      |
      v
    voltage threshold decoder
      |
      v
    decoded result

## 17.2 Digital Backend

The deterministic digital backend compiles CCIR into an instruction-derived
ExecutionArtifact.

Its lifecycle is:

    CCIR
      |
      v
    Digital ExecutionArtifact
      |
      v
    digital program preparation
      |
      v
    PreparedExecution
      |
      v
    deterministic digital execution
      |
      v
    ObservableExecution
      |
      v
    result-bit decoder
      |
      v
    decoded result

The digital execution stage consumes only its PreparedExecution representation
and does not import the CCIR reference evaluator.

## 17.3 Independent Comparison

After both backend executions complete, the reference implementation evaluates
canonical continuation semantics independently and constructs a
CrossBackendValidationResult.

Backend agreement and semantic correctness remain separate fields.

---

# 18. Reference Demonstration

The reference implementation provides the command:

    python validate_cross_backend.py \
        benchmarks/default_xor.json \
        --boundary 0=0 \
        --boundary 3=1

A successful run reports the participating execution technologies and the
independent comparison result.

The essential output is:

    RC Reference Backend
      decoded result:     1

    Digital Backend
      decoded result:     1

    Independent Reference
      semantic result:    1

    Backend agreement:    PASS
    RC semantic match:    PASS
    Digital semantic:     PASS

    OVERALL:              PASS

This command is an executable demonstration of canonical backend
interchangeability.

---

# 19. Conformance Requirements

A cross-backend validation implementation conforms to RFC-0005 only if all of
the following requirements are satisfied.

## CB-1 — Canonical Input Identity

All participating backends shall consume the same admitted CCIR program.

## CB-2 — Independent Compilation

Each backend shall independently satisfy:

    Compile_backend : CCIR -> ExecutionArtifact

without consuming another backend's result.

## CB-3 — Independent Execution Lifecycle

Each backend shall independently traverse the RFC-0004 preparation, execution,
observation, and fixed-decoding lifecycle.

## CB-4 — Backend Heterogeneity

Backends presented as heterogeneous realizations shall not obtain one another's
results through delegation or wrapping.

## CB-5 — Reference Isolation

No participating backend shall consume the independent semantic reference
result or reference evaluator.

## CB-6 — Post-Execution Comparison

Backend comparison shall occur only after participating backend executions and
decoding have completed.

## CB-7 — Agreement Separation

Backend agreement shall be recorded separately from semantic correctness.

## CB-8 — Independent Semantic Match

Each backend's decoded result shall be compared independently with canonical
reference semantics.

## CB-9 — Overall Validation

Overall PASS shall require every mandatory backend-agreement and semantic-match
condition.

## CB-10 — Reproducibility

The validation record shall expose sufficient backend, input, execution, and
comparison information for independent reproduction.

---

# 20. Negative Controls

Conformance testing should include negative controls capable of detecting
architectural violations.

Examples include:

- a backend importing the independent reference evaluator;
- a backend receiving expected answers during compilation;
- one backend delegating execution to another;
- comparison occurring before decoding;
- backend agreement being treated as sufficient correctness;
- mismatched canonical input programs;
- unsupported backend capabilities being silently ignored;
- provenance disappearing during execution; and
- a validator reporting PASS when one backend disagrees with the reference.

Negative controls are necessary because successful output agreement alone does
not establish architectural separation.

---

# 21. Backend Interchangeability

RFC-0005 provides an executable interpretation of backend interchangeability.

A frontend application supplies one canonical CCIR program.

A conforming backend may be substituted without requiring modification of:

- the frontend source representation;
- canonical lowering;
- CCIR semantics; or
- independent validation semantics.

Backend-specific compilation, preparation, execution, observation, and
decoding remain encapsulated below the backend boundary.

Accordingly, backend interchangeability means interchangeability at the CPC
architectural interface, not identity of internal computation.

---

# 22. Architectural Significance

RFC-0003 establishes backend independence as a compilation contract.

RFC-0004 establishes a backend-independent execution lifecycle.

RFC-0005 adds executable evidence that these abstractions can support
structurally different computational realizations of one canonical constraint
program.

The significance of cross-backend validation is therefore not that two
implementations happen to return the same answer.

The stronger architectural statement is:

1. one canonical CCIR program is supplied;
2. each backend compiles it independently;
3. each backend produces a different backend-specific ExecutionArtifact;
4. each backend follows its own preparation and execution procedure;
5. each backend exposes only its admitted interface;
6. each fixed decoder produces a semantic result;
7. backend results are compared only afterwards; and
8. independent canonical semantics judge each backend separately.

This architecture permits future execution technologies to be introduced
without granting them privileged semantic status.

A future physical backend therefore enters CPC as a candidate realization that
must satisfy the same contracts and validation procedures as conventional
backends.

---

# 23. Relationship to Future Physical Backends

RFC-0005 is intentionally substrate-neutral.

Future backend families may include:

- FPGA implementations;
- digital hardware;
- optical systems;
- analog systems;
- coherent physical substrates;
- C-parity execution backends;
- quantum-inspired systems; and
- other computational substrates.

A new backend does not alter canonical CCIR semantics.

Instead, it is evaluated according to the same architecture:

    CCIR
      |
      v
    Compile_new_backend
      |
      v
    ExecutionArtifact
      |
      v
    PreparedExecution
      |
      v
    execution
      |
      v
    ObservableExecution
      |
      v
    fixed decoder
      |
      v
    decoded result
      |
      v
    independent cross-backend validation

Consequently, failure of one candidate backend does not invalidate the CPC
architecture or other conforming backends.

---

# 24. Security Considerations

RFC-0005 defines architectural validation requirements rather than operational
security policy.

It does not prescribe:

- process isolation;
- hardware isolation;
- sandboxing;
- trusted execution environments;
- cryptographic attestation; or
- adversarial execution protection.

However, implementations claiming independent backend validation should avoid
shared hidden state that would undermine the claimed independence of execution
paths.

Security and adversarial certification may be defined by future profiles.

---

# 25. Future Extensions

Potential extensions include:

- validation across more than two simultaneous backends;
- heterogeneous hardware execution;
- cross-backend benchmark suites;
- canonical machine-readable validation reports;
- execution-artifact structural comparison;
- backend certification profiles;
- reproducibility manifests;
- performance-independent semantic equivalence testing;
- fault-injection studies;
- differential backend testing;
- hardware/software co-validation;
- experimental physical backend certification; and
- automated backend qualification against CPC conformance suites.

---

# 26. Acceptance Criteria

RFC-0005 may be considered implemented by the CPC Reference Validation
Framework when:

- at least two structurally distinct backends consume identical CCIR programs;
- both backends independently satisfy RFC-0003 compilation;
- both backends independently satisfy the RFC-0004 execution lifecycle;
- backend-specific artifacts remain distinct;
- backend-specific execution engines remain distinct;
- backend decoded outputs are compared after execution;
- independent semantic evaluation remains outside backend dependencies;
- backend agreement is distinguished from semantic correctness;
- each backend is independently compared against CCIR semantics;
- negative controls enforce reference isolation;
- a reproducible cross-backend command is provided; and
- the complete repository regression suite passes.

---

# References

RFC-0001 — CPC Architecture

RFC-0002 — Generic Constraint IR and CNF Front End

RFC-0003 — Backend Execution Contract

RFC-0004 — Physical Execution Backend Engineering and Conformance
