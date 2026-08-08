# RFC-0007: Backend Qualification and Conformance Manifests

**Status:** Draft  
**Category:** CPC Validation Architecture  
**Depends on:** RFC-0001, RFC-0002, RFC-0003, RFC-0004, RFC-0005, RFC-0006

---

# 1. Abstract

RFC-0007 defines a machine-readable qualification layer for CPC execution
backends.

The qualification layer binds backend identity, declared capabilities, fixed
backend rules, execution-profile identifiers, architectural conformance claims,
and finite RFC-0006 corpus evidence into one deterministic manifest.

The manifest does not create conformance by declaration.

Instead, it records claims whose supporting evidence remains external and
executable through the conformance and validation procedures defined by
RFC-0003 through RFC-0006.

A backend is therefore admitted by a common qualification protocol rather than
by substrate type, implementation technology, or organizational provenance.

The same protocol applies to conventional software backends, simulated
physical backends, hardware backends, and future physical execution
technologies.

---

# 2. Motivation

RFC-0003 establishes the backend compilation contract.

RFC-0004 establishes the preparation, execution, observation, and decoding
lifecycle.

RFC-0005 establishes heterogeneous cross-backend validation.

RFC-0006 establishes deterministic corpus validation and reproducible finite
evidence.

A further layer is required to answer a different engineering question:

    What exactly identifies a backend realization as qualified under
    a stated CPC validation baseline?

RFC-0007 answers that question by defining a deterministic qualification
manifest.

The manifest provides a stable boundary between executable evidence and
portable qualification metadata.

---

# 3. Scope

RFC-0007 specifies:

- backend qualification-manifest identity;
- backend and version identity;
- canonical capability declarations;
- fixed backend parameters;
- fixed backend-rule declarations;
- preparation identity;
- execution identity;
- execution-engine identity and version;
- machine-readable architectural conformance claims;
- RFC-0006 corpus-qualification summary;
- deterministic serialization;
- deterministic manifest hashing;
- qualification evidence requirements;
- failure and rejection conditions; and
- substrate-neutral backend admission.

RFC-0007 does not define:

- new CCIR semantics;
- new backend compilation semantics;
- new execution semantics;
- new decoder semantics;
- cryptographic signatures;
- organizational trust;
- hardware attestation;
- remote attestation;
- universal correctness proofs; or
- complexity-theoretic conclusions.

Those concerns remain outside this RFC or may be introduced by future
extensions.

---

# 4. Architectural Position

The qualification architecture is:

    RFC-0003 compiler conformance
                |
                v
    RFC-0004 execution conformance
                |
                v
    RFC-0005 cross-backend eligibility
                |
                v
    RFC-0006 corpus qualification
                |
                v
       Qualification Assembly
                |
                v
    BackendQualificationManifest
                |
                v
       deterministic manifest hash

Qualification assembly occurs outside backend execution.

No qualification-manifest field may alter the result of backend compilation,
preparation, execution, observation, decoding, or reference evaluation.

---

# 5. Evidence and Claim Separation

RFC-0007 distinguishes:

1. executable evidence; and
2. machine-readable qualification claims.

Executable evidence includes, as applicable:

- RFC-0003 compiler and dependency-boundary tests;
- RFC-0004 execution conformance tests;
- RFC-0005 cross-backend conformance tests;
- RFC-0006 corpus-validation records;
- provenance-validation results; and
- Answer Independence tests.

A qualification manifest records claims about that evidence.

The manifest itself is not proof that the claims are true.

Accordingly:

    manifest claim != executable evidence

and:

    manifest existence != backend qualification

Qualification requires both an admissible manifest and the required supporting
evidence.

---

# 6. Schema Identity

The current reference schema is:

    cpc.backend-qualification.v1

Breaking changes to qualification-manifest semantics shall use a new schema
identifier.

The schema identifier shall be included in every serialized manifest.

---

# 7. Backend Identity

Every qualification manifest shall identify:

- backend_id; and
- backend_version.

These values shall equal the corresponding fields of the backend's canonical
BackendSpecification.

Backend identity shall not be inferred from filenames, execution-engine names,
or human-readable descriptions.

---

# 8. Capabilities

The qualification manifest shall expose the backend capabilities admitted by
the canonical BackendSpecification.

The current capability classes are:

- constraint families;
- interface features;
- execution features; and
- artifact features.

Capability serialization shall be deterministic.

Unordered internal collections shall therefore be serialized in canonical
sorted order.

Qualification shall not add capabilities that are absent from the canonical
BackendSpecification.

---

# 9. Fixed Parameters

Fixed backend parameters shall be included in the qualification manifest.

These parameters represent globally fixed backend configuration admitted by the
backend specification.

Qualification assembly shall not silently override fixed parameters.

Environment-dependent execution information shall not be misrepresented as a
fixed backend parameter.

---

# 10. Backend Rules

Every globally fixed backend rule declared by BackendSpecification shall remain
available in the qualification manifest.

Rule identity is represented by the canonical backend rule identifier.

The manifest shall not create backend rules that are absent from the backend
specification.

Backend-rule declarations support auditability of RFC-0003 provenance.

---

# 11. Execution Profile

A qualified backend shall identify the execution realization used by the
qualification claim.

The execution profile contains:

- preparation_id;
- execution_id;
- execution_engine; and
- execution_engine_version.

These values describe the execution realization.

They do not replace BackendSpecification.

Environment-dependent values, including an installed external execution-engine
version, shall be obtained from the actual execution environment where
applicable.

---

# 12. Architectural Conformance Claims

The reference manifest records the following independent claims:

- rfc0003;
- rfc0004;
- rfc0005_eligible;
- rfc0006_qualified;
- answer_independence; and
- provenance_support.

These claims shall remain independent machine-readable fields.

A true value indicates that the backend is being presented as satisfying the
corresponding qualification condition.

It does not eliminate the requirement for supporting executable evidence.

---

# 13. RFC-0003 Qualification

A backend claiming RFC-0003 conformance shall have executable evidence that:

- compilation consumes canonical CCIR;
- backend capabilities are explicit;
- unsupported capabilities are rejected;
- ExecutionArtifact structure is valid;
- provenance is complete;
- backend rules are fixed;
- compiler dependencies satisfy Answer Independence; and
- independent semantic reference data do not enter backend compilation.

---

# 14. RFC-0004 Qualification

A backend claiming RFC-0004 conformance shall have executable evidence for its
preparation, execution, observation, and fixed-decoding lifecycle.

The execution path shall preserve backend identity and provenance.

The execution environment shall expose the identifiers required for
reproduction.

---

# 15. RFC-0005 Eligibility

RFC-0005 eligibility means that a backend can participate in the common
cross-backend validation architecture without violating backend isolation or
reference isolation.

Eligibility does not mean that a particular pair of backends has already been
validated over every possible program.

---

# 16. RFC-0006 Corpus Qualification

Where RFC-0006 qualification is claimed, the manifest may include the admitted
corpus summary:

- report_schema;
- benchmark_count;
- boundary_case_count; and
- overall_pass.

The current reference report schema is:

    cpc.cross-backend-summary.v1

The corpus summary is finite validation evidence.

It shall not be interpreted as a universal backend correctness theorem.

---

# 17. Corpus Evidence Admission

A qualification process shall reject RFC-0006 corpus evidence when:

- the report schema is unsupported;
- the report is malformed;
- overall_pass is false; or
- required qualification fields are absent.

Qualification assembly shall not convert a failed corpus result into a passing
qualification claim.

---

# 18. Deterministic Serialization

Qualification content shall have a deterministic canonical serialization.

For equivalent qualification content:

- object-key ordering shall be canonical;
- capability ordering shall be canonical;
- backend-rule ordering shall follow the canonical backend specification; and
- incidental runtime state shall not affect canonical identity.

Pretty-printed output may differ in whitespace from canonical serialization,
but canonical manifest identity shall not.

---

# 19. Manifest Hash

The reference implementation defines manifest identity as:

    H_M = SHA-256(CanonicalQualificationContent)

and serializes it as:

    sha256:<hex-digest>

The manifest hash covers qualification content prior to insertion of the
manifest_hash field itself.

A change to qualification content shall change the manifest hash except with
negligible cryptographic collision probability.

The hash establishes deterministic content identity.

It does not establish signer identity, organizational authority, or trusted
attestation.

---

# 20. Environment Dependence

Execution-engine versions may depend on the actual execution environment.

For example, the RC reference backend uses ngspice and records the installed
ngspice version.

Such environment-dependent values are part of the qualification realization
and therefore affect manifest identity.

A change in execution environment may legitimately produce a different
qualification manifest hash even when BackendSpecification is unchanged.

---

# 21. Reference Backend Profiles

The current CPC reference implementation provides qualification profiles for:

- the RC Reference Backend; and
- the deterministic Digital Backend.

The profiles share the same qualification protocol.

They do not share execution technology.

The RC profile identifies ngspice execution.

The Digital profile identifies the deterministic Python digital interpreter.

Neither backend receives privileged qualification status because of its
substrate.

---

# 22. Qualification Assembly

Qualification assembly consumes:

- canonical BackendSpecification;
- an admitted execution profile;
- explicit conformance claims; and
- optional admitted RFC-0006 summary evidence.

It produces:

    BackendQualificationManifest

Qualification assembly shall perform no backend semantic evaluation.

It shall not recompute expected benchmark answers.

It shall not enter any backend dependency graph.

---

# 23. Qualification CLI

The reference implementation provides:

    qualify_backends.py

The command consumes an existing RFC-0006 JSON summary and generates
backend-specific qualification manifests.

The qualification CLI shall not rerun the benchmark corpus implicitly.

Corpus execution and qualification assembly are separate operations.

This separation preserves the identity of the evidence used for qualification.

---

# 24. Rejection Semantics

Qualification shall fail rather than silently degrade when required inputs are
invalid.

Examples include:

- unsupported evidence schema;
- failed RFC-0006 corpus evidence;
- empty required execution identifiers;
- malformed backend identity;
- invalid qualification values; or
- incompatible manifest schema.

A failed qualification operation shall not emit a manifest represented as
passing qualification.

---

# 25. Substrate Neutrality

RFC-0007 qualification is substrate-neutral.

A backend may represent:

- conventional software execution;
- deterministic digital hardware;
- FPGA execution;
- analog execution;
- optical execution;
- coherent physical execution;
- C-parity execution;
- other physical substrates; or
- future execution technologies.

Qualification conditions are defined by architectural contracts and evidence,
not by substrate category.

---

# 26. Admission Principle

The normative backend-admission principle is:

    A backend is admitted by satisfying the fixed CPC qualification
    protocol, not by the identity of its substrate or implementer.

A future backend shall therefore enter the framework under the same
qualification conditions used for existing reference backends.

No future backend may weaken existing qualification requirements merely because
its execution technology differs.

---

# 27. Evidence Boundary

A passing qualification manifest supports only the claims represented by its
admitted evidence.

It does not establish:

- universal semantic correctness;
- correctness outside the tested corpus;
- physical realizability beyond the executed realization;
- superior computational complexity;
- general performance superiority;
- hardware authenticity; or
- cryptographic authorship.

Those claims require separate evidence.

---

# 28. Conformance Requirements

An RFC-0007 implementation shall satisfy the following requirements.

## BQ-1 — Schema Identity

Every qualification manifest shall carry an explicit supported schema
identifier.

## BQ-2 — Canonical Backend Identity

Backend identity and version shall originate from BackendSpecification.

## BQ-3 — Capability Fidelity

Serialized capabilities shall equal the canonical backend capabilities and use
deterministic ordering.

## BQ-4 — Fixed-Parameter Fidelity

Qualification shall preserve canonical fixed backend parameters.

## BQ-5 — Backend-Rule Fidelity

Qualification shall preserve canonical backend-rule identifiers.

## BQ-6 — Execution Identity

Preparation, execution, engine, and engine-version identifiers shall be
explicit and non-empty.

## BQ-7 — Claim Separation

Architectural conformance claims shall remain independently machine-readable.

## BQ-8 — Evidence Separation

The manifest shall not be treated as executable conformance evidence.

## BQ-9 — Corpus Evidence Admission

RFC-0006 qualification shall require an admitted passing corpus summary.

## BQ-10 — Deterministic Serialization

Equivalent qualification content shall serialize canonically.

## BQ-11 — Deterministic Manifest Identity

Equivalent qualification content shall produce the same manifest hash.

## BQ-12 — Content Sensitivity

A change in covered qualification content shall change manifest identity.

## BQ-13 — Qualification Isolation

Qualification assembly shall remain outside backend execution and independent
semantic evaluation.

## BQ-14 — Failure Preservation

Failed evidence shall not produce a passing qualification manifest.

## BQ-15 — Substrate Neutrality

The qualification protocol shall not depend on a privileged substrate class.

---

# 29. Security Considerations

The manifest hash provides content identity only.

RFC-0007 does not define digital signatures, certificate authorities,
organizational trust, hardware attestation, secure boot, trusted execution
environments, or remote attestation.

A future RFC may bind qualification manifests to cryptographic signatures or
external trust roots without changing the qualification-content model.

---

# 30. Future Extensions

Potential extensions include:

- detached digital signatures;
- signed validation manifests;
- artifact hashes;
- source revision identifiers;
- reproducible build identifiers;
- hardware device identity;
- FPGA bitstream identity;
- remote execution attestation;
- physical calibration records;
- experimental substrate metadata;
- multi-backend qualification bundles; and
- C-parity backend qualification.

Such extensions shall preserve the distinction between qualification metadata
and supporting evidence.

---

# 31. Acceptance Criteria

RFC-0007 is accepted when the reference implementation demonstrates:

- deterministic qualification-manifest construction;
- canonical backend identity;
- capability fidelity;
- fixed-parameter fidelity;
- backend-rule fidelity;
- explicit execution profiles;
- independent conformance claims;
- admitted RFC-0006 corpus evidence;
- rejection of failed corpus evidence;
- rejection of unsupported evidence schemas;
- deterministic canonical serialization;
- deterministic SHA-256 manifest identity;
- manifest-hash sensitivity to covered content;
- reference qualification profiles for RC and Digital backends;
- qualification CLI generation;
- RFC-0007 conformance tests; and
- complete repository regression without failure.

Acceptance of RFC-0007 establishes a common qualification protocol.

It does not certify unimplemented future backends.

---
