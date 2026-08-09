# RFC-0009: Physical Execution Evidence and Substrate Conformance

**Status:** Draft  
**Category:** CPC Execution and Validation Architecture  
**Depends on:** RFC-0001, RFC-0002, RFC-0003, RFC-0004, RFC-0005, RFC-0006, RFC-0007, RFC-0008

---

# 1. Abstract

RFC-0009 specifies the evidence architecture required to connect a CPC
prepared execution to an independently inspectable claim of execution on a
physical substrate.

Earlier CPC RFCs define canonical constraint representation, backend
compilation, execution artifacts, preparation, substrate execution,
restricted observation, semantic decoding, cross-backend validation,
benchmark validation, backend qualification, and the FPGA execution backend.

Those contracts establish what a CPC backend must compile, expose, execute,
and validate. They do not by themselves establish that a particular
prepared computation was physically realized on a particular physical
device, that a particular build artifact was programmed into that device,
or that an admitted physical observation originated from that execution.

RFC-0009 introduces a separate physical-evidence layer for those claims.

The central distinction is

\[
\boxed{
\text{content identity}
\neq
\text{physical authenticity}
\neq
\text{semantic correctness}
}
\]

A cryptographic digest can establish the identity of recorded content.
A complete evidence chain can bind recorded content to a declared physical
execution lifecycle. Semantic validation can determine whether admitted
observable output agrees with the semantics of the original constraint
instance.

These are different claims and MUST remain architecturally distinct.

RFC-0009 defines:

1. canonical physical execution evidence;
2. external evidence-record integrity verification;
3. substrate evidence profiles and conformance evaluation;
4. a physical FPGA realization profile;
5. physical build provenance;
6. device-programming evidence;
7. physical execution-event binding; and
8. the boundary between physical evidence and semantic validation.

RFC-0009 does not assert that any physical FPGA execution has occurred merely
because these contracts exist. Physical execution is established only by an
actual evidence instance satisfying the applicable evidence and conformance
requirements.

---

# 2. Scope

RFC-0009 concerns evidence for physical execution.

It specifies how CPC may represent and verify the chain

\[
\mathrm{CCIR}
\rightarrow
A_X
\rightarrow
P_X
\rightarrow
M_{\mathrm{build}}
\rightarrow
B_X
\rightarrow
R_{\mathrm{program}}
\rightarrow
E_{\mathrm{run}}
\rightarrow
O_X
\rightarrow
\mathrm{Decode}_X(O_X),
\]

where:

- \(A_X\) is an RFC-0003 `ExecutionArtifact`;
- \(P_X\) is an RFC-0004 `PreparedExecution`;
- \(M_{\mathrm{build}}\) is a physical build manifest;
- \(B_X\) is a substrate configuration artifact such as an FPGA bitstream;
- \(R_{\mathrm{program}}\) is a device-programming record;
- \(E_{\mathrm{run}}\) is a physical execution-event record;
- \(O_X\) is an RFC-0004 `ObservableExecution`; and
- \(\mathrm{Decode}_X\) is the backend decoder.

RFC-0009 does not redefine CCIR, backend compilation, `ExecutionArtifact`,
`PreparedExecution`, `ObservableExecution`, semantic decoding, or
cross-backend semantic validation.

Those remain governed by the earlier RFCs.

---

# 3. Motivation

A software or simulator execution can often be reproduced from source code,
tool identity, and deterministic execution inputs.

A physical execution introduces additional questions.

For example:

- Which exact prepared representation was used?
- Which synthesis and implementation inputs were used?
- Which physical target was selected?
- Which configuration artifact resulted?
- Which exact configuration artifact was programmed?
- Which device was programmed?
- Through which interface was it programmed?
- What stimulus was physically applied?
- What physical observation was recorded?
- Which files constitute the evidence?
- Do the recorded files still match their declared digests?
- Does the evidence satisfy the requirements of the substrate profile?

Without explicit answers to these questions, the statement

> this result came from the physical substrate

is not a machine-checkable CPC claim.

RFC-0009 therefore treats physical execution provenance as a first-class
architectural object.

---

# 4. Normative terminology

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this
document are to be interpreted as normative requirements.

RFC-0009 distinguishes four kinds of statements.

## 4.1 Identity statement

An identity statement asserts that recorded bytes have a particular
cryptographic digest.

For content \(C\),

\[
I(C)=H(C).
\]

This establishes content identity under the selected digest function.

It does not establish the truth of statements contained in \(C\).

## 4.2 Provenance statement

A provenance statement binds one recorded object to another through a
canonical record.

For example,

\[
H(P_X)
\longrightarrow
M_{\mathrm{build}}
\longrightarrow
H(B_X).
\]

This establishes a declared provenance relation.

The digest alone does not prove that the declared physical event occurred.

## 4.3 Physical-evidence statement

A physical-evidence statement asserts that a collection of externally
inspectable records represents a declared physical execution lifecycle and
satisfies a specified evidence profile.

Its strength depends on the evidence records, their integrity, and the
external trust model under which they were acquired.

## 4.4 Semantic statement

A semantic statement asserts something about the logical meaning of an
admitted observation.

For example,

\[
\mathrm{Decode}_X(O_X)
=
\mathfrak R(C_X).
\]

Semantic statements belong to CPC semantic validation.

They MUST NOT be inferred merely from physical evidence completeness.

---

# 5. Three independent claim dimensions

RFC-0009 requires implementations and documentation to preserve the
following distinction:

\[
\boxed{
\text{identity}
\neq
\text{authenticity}
\neq
\text{correctness}
}
\]

## 5.1 Content identity

Content identity answers:

> Are these the same recorded bytes?

Cryptographic hashing is sufficient for the RFC-0009 content-identity
mechanism.

## 5.2 Physical authenticity

Physical authenticity answers:

> Does this evidence support the claim that the recorded event occurred on
> the declared physical substrate?

RFC-0009 provides the data structures and integrity relations required to
make such a claim inspectable.

Cryptographic hashes alone are not sufficient to establish physical
authenticity.

Authentication, trusted acquisition, signed records, controlled laboratory
procedures, independent witnessing, attestation hardware, or other
mechanisms MAY strengthen physical authenticity, but are outside the
mandatory core of RFC-0009.

## 5.3 Semantic correctness

Semantic correctness answers:

> Does the admitted observation have the correct meaning with respect to the
> original CPC constraint instance?

That question is answered by the existing CPC decoding and semantic
validation architecture.

Physical evidence MUST NOT replace semantic validation.

Semantic validation MUST NOT be used as evidence that a physical execution
occurred.

---

# 6. Canonical physical execution evidence

RFC-0009 defines a canonical physical evidence object represented by
`PhysicalExecutionEvidence`.

Its schema identity is

```text
cpc.physical-execution-evidence.v1
```

A physical execution evidence object binds the relevant execution identities
to substrate, instrumentation, calibration, evidence-record, provenance, and
metadata fields.

Conceptually,

\[
\mathcal E_X
=
(
H(P_X),
H(O_X),
S_X,
I_X,
K_X,
R_X,
\Pi_X,
M_X
),
\]

where:

- \(H(P_X)\) identifies the prepared execution;
- \(H(O_X)\) identifies the observable execution;
- \(S_X\) contains substrate identity;
- \(I_X\) contains instrumentation identity;
- \(K_X\) contains calibration identity;
- \(R_X\) contains external evidence records;
- \(\Pi_X\) contains evidence provenance; and
- \(M_X\) contains additional evidence metadata.

The evidence object MUST NOT contain an independently computed semantic
reference result.

---

# 7. Canonical hashing of execution objects

RFC-0009 defines deterministic content identities for
`PreparedExecution` and `ObservableExecution`.

Let

\[
\operatorname{Canon}(Y)
\]

denote the canonical serialization admitted by the RFC-0009 implementation.

Then

\[
H_P
=
\operatorname{SHA256}
(
\operatorname{Canon}(P_X)
)
\]

and

\[
H_O
=
\operatorname{SHA256}
(
\operatorname{Canon}(O_X)
).
\]

These identities are used to bind evidence to the exact CPC execution
objects to which it refers.

Canonicalization MUST be deterministic.

Equivalent object content MUST produce identical canonical content identity.

Changes to admitted content MUST change the resulting digest except with the
ordinary cryptographic collision limitations of SHA-256.

---

# 8. Evidence records

An external physical artifact is represented by an `EvidenceRecord`.

Examples include:

- build reports;
- timing reports;
- bitstreams;
- programming logs;
- stimulus logs;
- measurement logs;
- instrument exports;
- calibration records; and
- other substrate-specific evidence.

An evidence record identifies at minimum the declared evidence type and the
cryptographic identity of its content.

For evidence bytes \(D_i\),

\[
R_i
=
(
t_i,
H(D_i),
\ldots
).
\]

An `EvidenceRecord` MAY be constructed directly from bytes.

The digest records content identity only.

It does not certify the truth, origin, or physical authenticity of the
content.

---

# 9. External evidence verification

RFC-0009 requires evidence content to be independently verifiable against
its declared digest.

Given evidence record \(R_i\) and supplied bytes \(D_i\), verification checks

\[
H(D_i)
\stackrel{?}{=}
H_i.
\]

The reference implementation provides verification for:

- evidence bytes;
- evidence files;
- evidence sets represented as bytes; and
- evidence sets represented as files.

Verification results are distinct from physical execution conformance.

A successful digest verification means:

> the supplied bytes match the content identity declared by the evidence
> record.

It does not mean:

> the statements in the supplied bytes are true.

It also does not mean:

> the declared physical event occurred.

---

# 10. Physical evidence profiles

Different physical substrates require different evidence.

RFC-0009 therefore defines `PhysicalEvidenceProfile`.

A physical evidence profile declares required:

- substrate fields;
- instrumentation fields;
- calibration fields; and
- evidence types.

Let a profile be

\[
\mathcal P
=
(
F_S,
F_I,
F_K,
T_E
),
\]

where:

- \(F_S\) is the set of required substrate fields;
- \(F_I\) is the set of required instrumentation fields;
- \(F_K\) is the set of required calibration fields; and
- \(T_E\) is the set of required evidence-record types.

Profiles define evidentiary completeness requirements.

They MUST NOT define semantic answers.

They MUST NOT contain independently computed reference results.

---

# 11. Physical execution conformance

RFC-0009 defines physical execution conformance as evaluation of a physical
evidence object against a physical evidence profile.

Conceptually,

\[
\operatorname{Conform}
(
\mathcal E_X,
\mathcal P
)
\rightarrow
Q_X,
\]

where \(Q_X\) is a `PhysicalExecutionConformanceResult`.

Conformance evaluates evidentiary properties such as:

1. required substrate fields are present;
2. required instrumentation fields are present;
3. required calibration fields are present;
4. required evidence types are present; and
5. admitted evidence records are internally integrity-valid.

The aggregate conformance result is derived from these component checks.

Physical execution conformance MUST NOT call a semantic reference evaluator.

Physical execution conformance MUST NOT decode the CPC answer in order to
determine whether evidence is complete.

Physical execution conformance therefore answers:

> Is the declared physical evidence structurally complete and internally
> consistent under this profile?

It does not answer:

> Is the decoded computation result correct?

---

# 12. Evidence integrity versus evidence completeness

RFC-0009 distinguishes integrity from completeness.

## 12.1 Integrity

Integrity asks whether a supplied evidence artifact matches its committed
identity.

For each record,

\[
H(D_i)=H_i.
\]

## 12.2 Completeness

Completeness asks whether all evidence required by the applicable physical
profile is present.

Thus an evidence set can be:

- integrity-valid but incomplete;
- complete in declared fields but integrity-invalid;
- both valid and complete; or
- neither valid nor complete.

Implementations MUST NOT collapse these conditions into a single
unqualified statement.

---

# 13. Physical FPGA realization profile

RFC-0009 defines the first CPC physical realization profile for the RFC-0008
FPGA backend.

Its profile identity is

```text
fpga.physical-device.v1
```

The profile applies to:

```text
backend_id      = fpga
backend_version = 1
hdl_target      = verilog-2001
```

The profile is intentionally vendor-neutral.

It does not prescribe a particular FPGA vendor, board, synthesis system,
place-and-route implementation, programmer, or laboratory instrument.

---

# 14. FPGA physical realization lifecycle

The physical FPGA profile identifies the following realization stages:

1. synthesis;
2. technology mapping;
3. placement;
4. routing;
5. bitstream generation;
6. device programming;
7. physical stimulus;
8. physical observation; and
9. timing validation.

These stages describe the physical realization lifecycle.

They are distinct from the RFC-0008 reference simulation path.

RFC-0008 may execute the prepared Verilog representation through an HDL
simulation engine.

RFC-0009 defines how a physical realization of the same backend
representation can be evidenced.

Simulation and physical realization therefore remain different execution
realizations of the FPGA backend representation.

---

# 15. FPGA evidence requirements

The reference physical FPGA profile requires substrate identity sufficient to
identify:

- board;
- device family;
- device;
- device part.

It requires instrumentation identity sufficient to identify:

- observation interface;
- programming interface;
- stimulus interface.

It requires a timing-validation calibration identity.

The reference profile requires evidence types covering:

- bitstream;
- build report;
- measurement log;
- programming log; and
- timing report.

These requirements establish evidentiary completeness.

They do not themselves establish semantic correctness.

---

# 16. Physical build provenance

RFC-0009 defines `PhysicalBuildManifest`.

Its schema identity is

```text
cpc.physical-build-manifest.v1
```

A physical build manifest binds:

1. CPC backend identity;
2. physical profile identity;
3. prepared-execution identity;
4. target device family;
5. target device part;
6. build-tool identities;
7. build-input identities;
8. bitstream format;
9. bitstream identity; and
10. optional deterministic metadata.

Conceptually,

\[
M_{\mathrm{build}}
=
(
X,
\mathcal P,
H(P_X),
D,
T,
I,
F_B,
H(B_X),
M
).
\]

The manifest establishes a deterministic provenance commitment from the
prepared representation to the declared physical configuration artifact:

\[
H(P_X)
\rightarrow
M_{\mathrm{build}}
\rightarrow
H(B_X).
\]

---

# 17. Build-tool identity

A build tool is represented by `BuildToolIdentity`.

It records:

- build stage;
- tool identity; and
- tool version.

Tool identities MUST be explicit.

A physical build manifest MUST NOT silently depend on an undeclared build
tool whose output contributes to the committed configuration artifact.

The manifest records tool identity for reproducibility and auditability.

It does not imply that a particular tool is trusted.

---

# 18. Build-input identity

A build input is represented by `BuildInputRecord`.

Each input records:

- input identity;
- media type; and
- SHA-256 digest.

The physical build manifest therefore commits not merely to the resulting
bitstream but also to the declared inputs from which that bitstream was
produced.

This permits an auditor to distinguish:

\[
B_X = F(P_X,I_1,\ldots,I_n,T)
\]

from another build that happens to target the same device but uses different
inputs or tools.

---

# 19. Build manifest identity

`PhysicalBuildManifest` has a deterministic canonical serialization.

Its manifest identity is

\[
H_M
=
H(
\operatorname{Canon}
(
M_{\mathrm{build}}
)
).
\]

The manifest hash commits to the manifest content.

Changing a committed build input, tool identity, target identity, prepared
execution identity, bitstream identity, or other canonical manifest field
changes the manifest identity except with the ordinary collision limitations
of SHA-256.

A build manifest MUST NOT assert that the resulting bitstream was programmed
onto a physical device.

That is a separate lifecycle event.

---

# 20. Device-programming record

RFC-0009 defines `DeviceProgrammingRecord`.

Its schema identity is

```text
cpc.device-programming-record.v1
```

A device-programming record binds a physical build to a declared
device-programming event.

It records:

- backend identity;
- physical profile identity;
- physical build-manifest identity;
- bitstream identity;
- board identity;
- device family;
- device part;
- device identity;
- programming interface;
- programmer identity;
- programmer version;
- programming-log identity; and
- optional metadata.

Conceptually,

\[
R_{\mathrm{program}}
=
(
H(M_{\mathrm{build}}),
H(B_X),
D_X,
J_X,
H(L_{\mathrm{program}}),
M
).
\]

---

# 21. Programming binding invariant

A device-programming record derived from a physical build MUST preserve the
build's:

- backend identity;
- backend version;
- physical profile identity;
- device family;
- device part; and
- bitstream digest.

Therefore the programming record establishes the declared binding

\[
H(M_{\mathrm{build}})
\longrightarrow
H(B_X)
\longrightarrow
D_X.
\]

The programming record does not by itself establish that the device
subsequently executed the computation.

Programming and execution are separate events.

---

# 22. Programming-record identity

`DeviceProgrammingRecord` has deterministic canonical serialization.

Its record identity is

\[
H_R
=
H(
\operatorname{Canon}
(
R_{\mathrm{program}}
)
).
\]

Changing the declared device, bitstream, build manifest, programmer,
programming interface, programming log, or other canonical record content
changes the record identity except with the ordinary collision limitations
of SHA-256.

---

# 23. Physical execution event

RFC-0009 defines `PhysicalExecutionEvent`.

Its schema identity is

```text
cpc.physical-execution-event.v1
```

A physical execution event binds:

- the programming-record identity;
- the prepared-execution identity;
- the observable-execution identity;
- board identity;
- device identity;
- stimulus interface;
- observation interface;
- stimulus-record identity;
- measurement-record identity; and
- optional metadata.

Conceptually,

\[
E_{\mathrm{run}}
=
(
H(R_{\mathrm{program}}),
H(P_X),
H(O_X),
D_X,
H(S_X),
H(M_X),
I_S,
I_O,
M
).
\]

---

# 24. Execution binding invariant

Construction of a physical execution event MUST reject incompatible backend
identities.

The programming record, prepared execution, and observable execution MUST
refer to the same backend identity and backend version.

The event then establishes the recorded chain

\[
H(R_{\mathrm{program}})
\rightarrow
E_{\mathrm{run}}
\leftarrow
H(P_X)
\]

and

\[
E_{\mathrm{run}}
\rightarrow
H(O_X).
\]

It additionally commits to the stimulus and measurement records associated
with that run.

This prevents an evidence chain from silently substituting an observable
execution belonging to another backend.

---

# 25. Execution-event identity

`PhysicalExecutionEvent` has deterministic canonical serialization.

Its event identity is

\[
H_E
=
H(
\operatorname{Canon}
(
E_{\mathrm{run}}
)
).
\]

Changing the programming record, prepared execution, observable execution,
device identity, stimulus record, measurement record, or other canonical
event content changes the event identity except with the ordinary collision
limitations of SHA-256.

---

# 26. Complete physical evidence chain

For a physical FPGA execution, RFC-0009 permits the following complete
recorded chain:

```text
CCIR
 |
 v
ExecutionArtifact
 |
 v
PreparedExecution
 |
 | H(P)
 v
PhysicalBuildManifest
 |
 | H(bitstream)
 v
Bitstream
 |
 v
DeviceProgrammingRecord
 |
 | H(programming record)
 v
PhysicalExecutionEvent
 |
 | H(observable execution)
 v
ObservableExecution
 |
 v
Backend Decoder
 |
 v
Decoded Semantic Result
```

In symbolic form,

\[
C_X
\rightarrow
A_X
\rightarrow
P_X
\rightarrow
M_{\mathrm{build}}
\rightarrow
B_X
\rightarrow
R_{\mathrm{program}}
\rightarrow
E_{\mathrm{run}}
\rightarrow
O_X
\rightarrow
\mathrm{Decode}_X(O_X).
\]

RFC-0009 governs the evidence-bearing middle of this chain.

Earlier RFCs govern compilation, execution interfaces, decoding, and semantic
validation.

---

# 27. No hidden semantic channel

RFC-0009 physical evidence MUST remain semantically non-authoritative.

Evidence metadata, build logs, programming logs, timing reports, instrument
records, diagnostic channels, and substrate metadata MUST NOT become
undeclared semantic readout channels.

The semantic result MUST continue to be obtained through the backend's
declared observable interface and decoder.

Thus an implementation MUST NOT determine semantic success by inspecting,
for example:

- a simulator-only reference value;
- a build-system annotation containing the expected answer;
- a diagnostic log populated from a semantic oracle;
- an undeclared FPGA signal;
- a test harness field containing the expected result; or
- an external reference evaluator embedded into physical conformance.

This preserves the RFC-0003 Answer Independence boundary.

---

# 28. Relationship to Answer Independence

RFC-0003 constrains backend compilation dependencies.

RFC-0009 extends the same architectural discipline into physical evidence.

Physical evidence may depend on:

- admitted prepared execution content;
- declared build inputs;
- declared build tools;
- substrate identity;
- programming activity;
- physical stimulus;
- physical observation;
- instrumentation;
- calibration; and
- evidence acquisition.

It MUST NOT depend on an independently computed semantic answer for the
purpose of constructing evidence that purports to establish execution.

Formally, if \(\mathcal G_X\) denotes physical evidence generation, then the
evidence dependency boundary excludes a semantic oracle:

\[
\mathfrak R(C_X)
\notin
D(\mathcal G_X)
\]

unless that value is itself explicitly declared as diagnostic material and
excluded from semantic readout and conformance decisions.

The preferred architecture is to omit such reference information entirely
from the physical evidence path.

---

# 29. Diagnostics and semantic readout

Physical experiments commonly require diagnostics.

RFC-0009 does not prohibit diagnostic data.

It requires diagnostics to remain architecturally distinct from semantic
readout.

A diagnostic channel MAY report:

- supply voltage;
- clock frequency;
- temperature;
- timing margins;
- programming status;
- instrument state;
- signal-integrity information; or
- other physical operating conditions.

A diagnostic channel MUST NOT silently determine the CPC semantic result.

If a field participates in semantic decoding, it belongs to the declared
observable interface.

---

# 30. Evidence trust boundary

RFC-0009's core integrity mechanism is cryptographic content identity.

This creates a clear trust boundary.

RFC-0009 can establish mechanically that:

- canonical records have deterministic identities;
- supplied evidence bytes match committed digests;
- required evidence fields are present;
- required evidence types are present;
- records bind to declared upstream identities; and
- incompatible backend identities are rejected.

RFC-0009 cannot establish from hashes alone that:

- a camera image depicts the claimed device;
- a measurement instrument was correctly connected;
- a log was generated by the claimed instrument;
- a human did not fabricate a record before hashing it;
- a board serial number corresponds to the physical board shown;
- a programmer actually transferred the committed bitstream; or
- a physical event occurred merely because a syntactically valid record says
  that it occurred.

Those are authenticity questions.

RFC-0009 makes such questions explicit rather than conflating them with
content integrity.

---

# 31. Strengthening authenticity

Implementations MAY strengthen physical authenticity through mechanisms such
as:

- signed evidence records;
- hardware attestation;
- trusted timestamps;
- instrument signatures;
- device certificates;
- independently witnessed measurements;
- reproducible laboratory procedures;
- immutable evidence publication;
- video or photographic acquisition records;
- independently replicated experiments; or
- controlled chain-of-custody procedures.

Such mechanisms are compatible with RFC-0009.

They are not required by the version-1 generic evidence contract.

A future RFC MAY define stronger authenticated physical-evidence profiles.

---

# 32. Relationship to RFC-0007 qualification

RFC-0007 defines backend qualification and conformance manifests.

Backend qualification answers whether a backend implementation satisfies the
declared CPC architectural and validation requirements.

RFC-0009 answers a different question:

> What evidence supports the claim that a particular prepared computation was
> realized through a particular physical execution lifecycle?

A backend can therefore be RFC-0007-qualified without any RFC-0009 physical
execution evidence.

Likewise, the existence of RFC-0009 physical evidence does not automatically
qualify a backend under RFC-0007.

The two layers are complementary.

---

# 33. Relationship to RFC-0008

RFC-0008 introduces the CPC FPGA execution backend and tri-backend semantic
validation.

Its current executable realization can prepare Verilog and execute that
representation through an HDL execution engine.

RFC-0009 does not replace that path.

Instead it defines the evidence architecture required for an additional
physical realization path:

```text
                       FPGA ExecutionArtifact
                                |
                                v
                         Prepared Verilog
                         /             \
                        /               \
                       v                 v
              HDL execution       Physical build
                       |                 |
                       v                 v
             ObservableExecution     Bitstream
                                         |
                                         v
                                  Device programming
                                         |
                                         v
                                  Physical execution
                                         |
                                         v
                                  ObservableExecution
```

Both paths ultimately produce observations admitted by the backend
interface.

Semantic comparison remains downstream of those observations.

---

# 34. Substrate neutrality

Although RFC-0009 defines an FPGA reference profile, the generic physical
evidence architecture is substrate-neutral.

A future physical backend may define another `PhysicalEvidenceProfile` for,
for example:

- analog electrical hardware;
- optical systems;
- mechanical systems;
- spin or magnetic substrates;
- quantum devices;
- biochemical systems;
- biological substrates; or
- other physical constraint realizations.

Such a profile may require entirely different substrate, instrumentation,
calibration, and evidence fields.

The generic RFC-0009 distinction between identity, authenticity, evidence
conformance, and semantic correctness remains unchanged.

---

# 35. Biological and other non-electronic substrates

RFC-0009 does not assume that physical execution means digital electronic
hardware.

For a biological substrate, for example, an evidence profile might require
records describing:

- sample identity;
- preparation protocol;
- reagent or sequence identity;
- environmental conditions;
- stimulus protocol;
- acquisition instrumentation;
- calibration;
- raw measurement output; and
- chain of custody.

Those fields are substrate-specific.

The generic architecture remains

\[
P_X
\rightarrow
\text{physical realization}
\rightarrow
O_X
\rightarrow
\mathrm{Decode}_X(O_X).
\]

RFC-0009 therefore provides an evidentiary interface through which future CPC
substrates can be introduced without redefining the canonical CPC compiler
architecture.

---

# 36. Reproducibility

RFC-0009 distinguishes reproducibility of records from reproducibility of
physical outcomes.

Deterministic serialization and content hashing permit reproducibility of
record identity.

Build provenance permits an auditor to identify the declared toolchain,
inputs, target, and bitstream.

Physical reproducibility additionally depends on the substrate and
experimental conditions.

RFC-0009 therefore does not define

\[
\text{same evidence manifest}
\Rightarrow
\text{same physical outcome}
\]

as a general law.

A substrate-specific profile or later RFC MAY impose stronger reproducibility
requirements.

---

# 37. Timing evidence

The physical FPGA profile requires timing-validation evidence.

Timing evidence concerns whether the declared physical realization operated
within its admitted timing conditions.

Timing conformance MUST remain distinct from algorithmic or computational
complexity claims.

A timing report can establish properties of a particular implementation and
execution environment.

It does not establish asymptotic complexity.

---

# 38. Performance non-claims

RFC-0009 does not establish:

- polynomial-time execution;
- constant-time execution;
- asymptotic speedup;
- energy advantage;
- scaling advantage;
- complexity-class collapse;
- efficient physical relaxation;
- optimality of a substrate;
- robustness under arbitrary noise;
- fault tolerance; or
- superiority to conventional computation.

Any such claim requires separate evidence and analysis.

RFC-0009 establishes an evidence architecture, not a computational complexity
theorem.

---

# 39. Physical-execution non-claim

The existence of:

- `PhysicalExecutionEvidence`;
- `PhysicalEvidenceProfile`;
- `PhysicalBuildManifest`;
- `DeviceProgrammingRecord`;
- `PhysicalExecutionEvent`; or
- their corresponding tests

does not establish that a physical CPC execution has occurred.

These objects define the contract under which such an execution can be
recorded and audited.

A physical execution claim requires actual physical evidence acquired from an
actual substrate execution.

This distinction is normative.

---

# 40. Failure semantics

Physical evidence evaluation MUST fail closed with respect to missing required
evidence.

A profile requiring evidence type \(t\) MUST NOT pass a record set in which
\(t\) is absent.

A digest mismatch MUST NOT be treated as a successful integrity check.

An incompatible backend identity MUST NOT be silently coerced into a physical
execution event.

An empty evidence requirement set MUST NOT be interpreted as evidence of
semantic correctness.

Failures in physical evidence conformance MUST remain distinct from semantic
validation failures.

---

# 41. Determinism requirements

Canonical RFC-0009 records MUST serialize deterministically.

Where a collection is semantically unordered, the representation MUST impose
a deterministic canonical ordering.

Where ordering represents lifecycle semantics, that ordering MUST be
preserved explicitly rather than replaced by arbitrary canonical sorting.

This distinction is important.

For example:

- metadata key collections may be canonically sorted;
- build-input identities may be canonically ordered;
- tool identity records may use deterministic ordering; while
- the physical FPGA realization-stage sequence represents an ordered
  lifecycle.

Deterministic serialization is required so that record identities are stable
and reproducible.

---

# 42. Versioning

The initial RFC-0009 serialized schemas are:

```text
cpc.physical-execution-evidence.v1
cpc.physical-build-manifest.v1
cpc.device-programming-record.v1
cpc.physical-execution-event.v1
```

The initial physical FPGA profile identity is:

```text
fpga.physical-device.v1
```

Schema changes that alter canonical interpretation or hashing behavior MUST
use a new schema version.

Physical profile changes that alter required evidence semantics SHOULD use a
new profile identity.

---

# 43. Security considerations

RFC-0009 uses SHA-256 as a content-identity mechanism.

Implementations MUST understand the limits of this mechanism.

Hashing protects against unnoticed content substitution after an identity has
been committed, assuming the cryptographic properties of SHA-256.

Hashing does not authenticate the origin of content.

An attacker capable of fabricating an evidence artifact before its digest is
committed can produce a self-consistent but false evidence record.

Accordingly:

\[
\text{digest validity}
\not\Rightarrow
\text{physical truth}.
\]

Higher-assurance deployments SHOULD combine RFC-0009 content integrity with
appropriate authentication, attestation, acquisition, and custody mechanisms.

---

# 44. Privacy considerations

Physical evidence may contain:

- device serial numbers;
- laboratory identifiers;
- timestamps;
- operator information;
- photographs;
- instrument logs;
- network identifiers; or
- other operational metadata.

Evidence publishers SHOULD disclose only information required for the desired
verification level.

A substrate profile SHOULD avoid requiring personally identifying information
unless it is necessary for the intended assurance model.

---

# 45. Reference implementation

The RFC-0009 reference implementation is divided into the following modules:

```text
src/physical_execution_evidence.py
src/physical_execution_conformance.py
src/physical_evidence_verification.py
src/physical_fpga_profile.py
src/physical_build_provenance.py
src/physical_device_programming.py
src/physical_execution_event.py
```

The implementation intentionally separates:

```text
evidence representation
        |
        v
external integrity verification
        |
        v
profile conformance
        |
        v
substrate-specific realization profile
        |
        v
build provenance
        |
        v
device-programming binding
        |
        v
physical execution-event binding
```

Semantic validation remains outside this stack.

---

# 46. Reference conformance suites

The RFC-0009 reference implementation provides dedicated tests covering:

```text
tests/test_physical_execution_evidence.py
tests/test_physical_execution_evidence_real_backends.py
tests/test_physical_execution_conformance.py
tests/test_physical_evidence_verification.py
tests/test_physical_fpga_profile.py
tests/test_physical_build_provenance.py
tests/test_physical_device_programming.py
tests/test_physical_execution_event.py
```

The suites collectively exercise:

- canonical evidence identity;
- real CPC execution-object binding;
- evidence-profile validation;
- evidence completeness;
- external digest verification;
- FPGA physical-profile requirements;
- deterministic build provenance;
- bitstream binding;
- device-programming binding;
- programming-log identity;
- physical execution-event binding;
- stimulus identity;
- measurement identity;
- backend identity consistency; and
- exclusion of semantic success claims from the physical evidence layer.

---

# 47. RFC-0009 conformance requirements

An implementation claiming RFC-0009 generic conformance MUST satisfy the
following requirements.

## PE-1 — Canonical prepared-execution identity

The implementation MUST provide deterministic identity for admitted
`PreparedExecution` content.

## PE-2 — Canonical observable-execution identity

The implementation MUST provide deterministic identity for admitted
`ObservableExecution` content.

## PE-3 — External evidence identity

External evidence records MUST commit to their content by cryptographic
digest.

## PE-4 — Independent evidence verification

The implementation MUST permit supplied evidence bytes to be checked against
their committed identities.

## PE-5 — Profile-defined completeness

Physical evidence completeness MUST be evaluated against explicit
substrate-profile requirements.

## PE-6 — Integrity/completeness separation

Evidence integrity and evidence completeness MUST remain distinguishable.

## PE-7 — Build provenance

A physical build record MUST bind the prepared execution, declared build
inputs, tool identities, physical target, and resulting configuration-artifact
identity.

## PE-8 — Programming binding

A device-programming record MUST bind the physical build and configuration
artifact to a declared device and programming record.

## PE-9 — Execution-event binding

A physical execution event MUST bind the programming record, prepared
execution, observable execution, stimulus record, and measurement record.

## PE-10 — Backend identity consistency

Construction of a physical execution event MUST reject inconsistent backend
identities or versions.

## PE-11 — Semantic separation

Physical evidence conformance MUST NOT require an independently computed
semantic reference answer.

## PE-12 — Restricted semantic readout

Physical evidence and diagnostic fields MUST NOT silently become undeclared
semantic output channels.

## PE-13 — Deterministic record identity

Canonical physical evidence records MUST have deterministic identities.

## PE-14 — Explicit physical profile

A claim of physical evidence completeness MUST identify the physical evidence
profile under which completeness was evaluated.

## PE-15 — No implicit physical-execution claim

The presence of RFC-0009 data structures or passing software tests MUST NOT
be represented as evidence that a physical substrate execution occurred.

---

# 48. FPGA profile conformance requirements

A physical FPGA realization claiming conformance with
`fpga.physical-device.v1` MUST additionally satisfy the following.

## PF-1 — RFC-0008 backend binding

The realization MUST bind to backend:

```text
fpga/1
```

## PF-2 — Prepared HDL binding

The physical build MUST bind to the exact admitted RFC-0008 prepared
execution.

## PF-3 — Device target identity

The evidence MUST identify board, device family, device part, and device.

## PF-4 — Build identity

The evidence MUST identify the build inputs, build tools, and resulting
bitstream.

## PF-5 — Programming identity

The evidence MUST identify the programming interface, programmer, programmer
version, and programming log.

## PF-6 — Stimulus identity

The physical execution event MUST commit to the physical stimulus record.

## PF-7 — Observation identity

The physical execution event MUST commit to the physical measurement record
and admitted `ObservableExecution`.

## PF-8 — Timing evidence

The evidence set MUST contain the timing-validation evidence required by the
profile.

## PF-9 — Required evidence types

The evidence set MUST satisfy the evidence-type requirements of
`fpga.physical-device.v1`.

## PF-10 — Semantic independence

No FPGA build, programming, execution, diagnostic, or evidence field may be
used as an undeclared semantic oracle.

---

# 49. Acceptance criteria

RFC-0009 may advance from Draft to Accepted when all of the following hold:

1. the generic physical execution evidence model is implemented;
2. deterministic prepared and observable execution identities are tested;
3. external evidence integrity verification is implemented and tested;
4. substrate evidence profiles and conformance evaluation are implemented and
   tested;
5. the physical FPGA profile is implemented and tested;
6. physical build provenance is implemented and tested;
7. device-programming binding is implemented and tested;
8. physical execution-event binding is implemented and tested;
9. the RFC-0008 regression suite remains passing;
10. the complete repository regression suite remains passing;
11. RFC-0009 conformance tests explicitly cover PE-1 through PE-15;
12. FPGA profile conformance tests explicitly cover PF-1 through PF-10; and
13. the accepted RFC text and implementation are synchronized.

Physical hardware evidence is not required to accept the generic RFC-0009
architecture.

A claim that a particular physical FPGA execution has occurred does require
such evidence.

---

# 50. Future work

RFC-0009 intentionally leaves several stronger assurance mechanisms to future
work.

Possible extensions include:

- authenticated evidence records;
- signed manifests;
- trusted timestamps;
- hardware-rooted attestation;
- device certificates;
- instrument attestation;
- laboratory chain-of-custody records;
- reproducible physical-experiment bundles;
- physical evidence publication formats;
- independent replication manifests;
- analog physical profiles;
- optical physical profiles;
- quantum physical profiles;
- biochemical physical profiles; and
- biological physical profiles.

These extensions SHOULD build on the RFC-0009 identity/authenticity/correctness
separation rather than collapsing those concepts.

---

# 51. Architectural result

RFC-0009 extends CPC from executable backend validation to an explicit
physical-evidence architecture.

Before RFC-0009, CPC can establish:

\[
C_X
\rightarrow
A_X
\rightarrow
P_X
\rightarrow
O_X
\rightarrow
\mathrm{Decode}_X(O_X)
\]

under the applicable backend execution contract.

RFC-0009 adds independently inspectable physical provenance:

\[
P_X
\rightarrow
M_{\mathrm{build}}
\rightarrow
B_X
\rightarrow
R_{\mathrm{program}}
\rightarrow
E_{\mathrm{run}}
\rightarrow
O_X.
\]

The combined architecture is therefore

\[
\boxed{
C_X
\rightarrow
A_X
\rightarrow
P_X
\rightarrow
M_{\mathrm{build}}
\rightarrow
B_X
\rightarrow
R_{\mathrm{program}}
\rightarrow
E_{\mathrm{run}}
\rightarrow
O_X
\rightarrow
\mathrm{Decode}_X(O_X)
}
\]

while preserving the fundamental separation

\[
\boxed{
\text{representation}
\neq
\text{physical realization}
\neq
\text{evidence}
\neq
\text{semantic validation}.
}
\]

This permits CPC to make future physical-execution claims in a form that is
explicit, inspectable, reproducible at the record level, and compatible with
the Answer Independence requirements of the existing CPC architecture.

---

# 52. Status

RFC-0009 is initially introduced as **Draft**.

Its implementation contracts exist in the reference framework, but acceptance
requires explicit RFC-0009 conformance coverage and synchronization of the
normative document with the executable implementation.

No physical FPGA execution is claimed by the Draft RFC itself.
