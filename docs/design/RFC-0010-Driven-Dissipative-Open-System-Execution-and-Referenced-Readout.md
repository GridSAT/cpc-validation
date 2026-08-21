# RFC-0010: Driven-Dissipative Open-System Execution and Referenced Readout

**Status:** Review  
**Category:** CPC Execution and Validation Architecture  
**Depends on:** RFC-0001, RFC-0002, RFC-0003, RFC-0004, RFC-0005, RFC-0006, RFC-0007, RFC-0008, RFC-0009

---

# 1. Abstract

RFC-0010 specifies an execution and evidence contract for CPC backends whose
physical dynamics are modeled as driven-dissipative open quantum systems.

The central architectural separation is

\[
\boxed{
\mathcal L_{X,\beta}
=
\mathcal L_{\mathrm{stab}}
+
\mathcal L^{\mathrm{prob}}_{X,\beta}
}
\]

where

- \(\mathcal L_{\mathrm{stab}}\) protects a declared physical representation
  manifold; and
- \(\mathcal L^{\mathrm{prob}}_{X,\beta}\) implements instance-dependent
  semantic problem dynamics.

RFC-0010 extends the physical-execution evidence architecture of RFC-0009
with contracts for:

1. protected-manifold identity;
2. stabilization/problem-generator separation;
3. answer-independent problem-generator synthesis;
4. protected correction channels;
5. semantic terminal sectors;
6. dark-vector and stationary-state evidence;
7. penalty-Lyapunov convergence evidence;
8. resource-bounded convergence claims;
9. external operational references;
10. referenced measurement models;
11. fixed semantic decoders;
12. calibration and error margins; and
13. exact versus approximate realization status.

The RFC does not identify any particular hardware substrate with the CPC
semantic carrier. Superconducting bosonic systems, other open quantum
systems, and future substrates MAY implement this contract if they satisfy
its conformance requirements.

The architectural distinction is

\[
\boxed{
\text{semantic representation}
\neq
\text{hardware stabilization}
\neq
\text{problem dynamics}
\neq
\text{physical readout}
}
\]

and implementations MUST preserve it.

---

# 2. Scope

RFC-0010 governs CPC execution backends that make claims involving
open-system dynamics, dissipative stabilization, convergence to a semantic
terminal sector, or referenced physical readout.

It extends, rather than replaces, the existing CPC execution chain

\[
\mathrm{CCIR}
\rightarrow
A_X
\rightarrow
P_X
\rightarrow
E_X
\rightarrow
O_X
\rightarrow
\mathrm{Decode}_X(O_X)
\]

with open-system realization data.

A conforming RFC-0010 execution MAY refine the physical-execution portion as

\[
\mathrm{CCIR}
\rightarrow
A_X
\rightarrow
P_X
\rightarrow
\mathfrak L_{X,\beta}
\rightarrow
\rho_t
\rightarrow
M^{R}_{X,\beta}
\rightarrow
O_X
\rightarrow
D^{R}_{X,\beta}(O_X),
\]

where

- \(A_X\) is an RFC-0003 `ExecutionArtifact`;
- \(P_X\) is an RFC-0004 `PreparedExecution`;
- \(\mathfrak L_{X,\beta}\) is the declared open-system execution
  specification;
- \(\rho_t\) is the realized physical state trajectory or its admitted
  evidence representation;
- \(R\) is an external operational reference when required;
- \(M^{R}_{X,\beta}\) is the admitted referenced measurement;
- \(O_X\) is an RFC-0004 `ObservableExecution`; and
- \(D^{R}_{X,\beta}\) is the fixed backend decoder.

RFC-0010 does not redefine CCIR, semantic response, continuation semantics,
backend compilation, `ExecutionArtifact`, `PreparedExecution`,
`ObservableExecution`, physical-evidence identity, or independent semantic
validation.

Those remain governed by RFC-0001 through RFC-0009.

---

# 3. Motivation

A static physical representation is not yet a physical computation.

A Hamiltonian, circuit, state encoding, or protected manifold can represent
the semantic structure of a problem without establishing:

- how an admitted physical state is prepared;
- how the instance-dependent dynamics are synthesized;
- whether the protected representation is preserved;
- whether nonsemantic dark states exist;
- whether the physical evolution converges;
- how quickly convergence occurs;
- whether the convergence claim is resource bounded;
- which observable is admitted;
- whether the observable requires an external reference;
- how calibration uncertainty is represented;
- how the physical outcome is decoded; or
- whether the decoded result agrees with the independent semantic reference.

Open-system computation therefore requires a typed separation between
representation, dynamics, observation, and semantic validation.

RFC-0010 makes that separation machine-inspectable.

---

# 4. Normative terminology

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this
document are to be interpreted as normative requirements.

RFC-0010 distinguishes four realization levels.

## 4.1 Level I: static semantic representation

A Level-I claim asserts that a static physical or mathematical object
represents the required semantic response.

For a penalty Hamiltonian, a typical claim is

\[
E_0(X,\beta)=0
\quad\Longleftrightarrow\quad
\mathfrak R(X,\beta)=1.
\]

A Level-I claim MUST NOT by itself be reported as evidence of physical
convergence or efficient physical computation.

## 4.2 Level II: exact dissipative compatibility

A Level-II claim asserts that the admitted stationary physical states coincide
with the declared semantic terminal sector.

A typical exact condition is

\[
\operatorname{Fix}_{\mathrm{adm}}
\left(
\mathcal L_{X,\beta}
\right)
=
\mathfrak S
\left(
\mathcal G^{\mathrm{sem}}_{X,\beta}
\right).
\]

A Level-II claim MUST identify the admitted state space, the fixed-point
notion used, and the semantic terminal sector.

## 4.3 Level III: efficient physical convergence

A Level-III claim additionally asserts resource-bounded compilation,
preparation, control, convergence, and precision.

A polynomial-time claim MUST explicitly account for every resource on which
its convergence bound depends.

## 4.4 Level IV: robust referenced readout

A Level-IV claim additionally specifies an admitted physical measurement,
external reference where required, fixed decoder, calibration model, and
error bound sufficient to recover the semantic response.

The four levels MUST remain distinct.

Level I does not establish Level II.

Level II does not establish Level III.

Level III does not establish Level IV.

---

# 5. Open-system execution specification

An RFC-0010 backend SHALL define a canonical open-system execution
specification.

At minimum it MUST identify:

- the instance identity \(X\);
- the admitted boundary/control value \(\beta\);
- the prepared-execution identity;
- the physical Hilbert or state space used by the model;
- the protected representation manifold;
- the stabilization generator;
- the instance-dependent problem generator;
- the semantic terminal sector;
- the measurement interface;
- the decoder identity;
- the external operational reference, when required;
- the resource-accounting record; and
- the realization status.

The realization status MUST distinguish at least:

- `abstract`;
- `simulated`;
- `physical_approximate`; and
- `physical_exact`.

An implementation MUST NOT silently upgrade one status to another.

---

# 6. Stabilization and problem dynamics

The combined generator is

\[
\mathcal L_{X,\beta}
=
\mathcal L_{\mathrm{stab}}
+
\mathcal L^{\mathrm{prob}}_{X,\beta}.
\]

The two terms have distinct roles.

## 6.1 Stabilization generator

\(\mathcal L_{\mathrm{stab}}\) specifies hardware-native protection of the
declared physical representation manifold.

Its evidence MAY include:

- dissipative stabilization;
- passive protection;
- active error correction;
- reservoir engineering;
- feedback stabilization; or
- another explicitly declared mechanism.

The stabilization mechanism MUST NOT be identified with CPC semantic
quotienting merely because it protects encoded information.

## 6.2 Problem generator

\(\mathcal L^{\mathrm{prob}}_{X,\beta}\) specifies the instance-dependent
semantic dynamics.

The problem generator MUST be constructed from admitted instance data and
declared backend parameters.

It MUST NOT receive:

- independently computed continuation values;
- satisfying assignments;
- completion tables;
- expected decoded outputs;
- semantic oracle responses; or
- equivalent solution-dependent advice.

This is the RFC-0010 specialization of the Answer Independence Principle.

## 6.3 Generator identity

The execution record MUST cryptographically identify the exact generator
description or the exact canonical artifact from which the generator was
constructed.

For a physical execution, RFC-0009 physical-evidence requirements continue to
apply.

---

# 7. Protected manifold

Let

\[
V:
\mathcal H_{\mathrm{log}}
\rightarrow
\mathcal H_{\mathrm{phys}}
\]

be the declared encoding isometry when such an isometric description is used,
and define

\[
\Pi_{\mathrm{stab}}
=
VV^\dagger.
\]

A backend MAY use another mathematically equivalent protected-manifold
description, but it MUST expose a canonical protected-manifold identity.

The problem dynamics SHOULD preserve the protected manifold.

For an exact realization, a sufficient condition is

\[
\rho
=
\Pi_{\mathrm{stab}}
\rho
\Pi_{\mathrm{stab}}
\quad\Longrightarrow\quad
\mathcal L^{\mathrm{prob}}_{X,\beta}(\rho)
=
\Pi_{\mathrm{stab}}
\mathcal L^{\mathrm{prob}}_{X,\beta}(\rho)
\Pi_{\mathrm{stab}}.
\]

An approximate realization MUST instead declare a quantitative leakage bound.

Missing leakage information MUST NOT be interpreted as zero leakage.

---

# 8. Encoded semantic penalty

When a backend uses a penalty representation together with an
isometric encoding
\(V:\mathcal H_{\mathrm{log}}\rightarrow\mathcal H_{\mathrm{phys}}\),
let

\[
H_{X,\beta}
=
\sum_\alpha
\lambda_{X,\alpha}
P_{X,\alpha}^{(\beta)},
\qquad
\lambda_{X,\alpha}>0,
\]

be the logical penalty Hamiltonian.

Its encoded representative is

\[
H^{\mathrm{enc}}_{X,\beta}
=
V H_{X,\beta} V^\dagger.
\]

A backend using a non-isometric but mathematically equivalent protected-manifold
description MUST provide the corresponding encoded penalty and semantic-target
construction explicitly rather than implicitly reusing the isometric formulas.

Because the encoded operator may vanish outside the protected manifold, the
semantic target MUST be defined inside the protected representation rather
than as the unrestricted kernel of the encoded operator.

Define

\[
\mathcal G^{\mathrm{sem}}_{X,\beta}
=
V
\left(
\ker H_{X,\beta}
\right).
\]

This is the semantic target sector for the encoded penalty construction.

---

# 9. Protected correction family

A problem generator MAY be constructed from protected violation-removal
channels.

For violation projector
\(P_{X,\alpha}^{\mathrm{enc},(\beta)}\)
and partial correction
\(R_{X,\beta,\alpha,r}\),
a jump operator MAY take the form

\[
L_{X,\beta,\alpha,r}
=
\sqrt{
\kappa_{X,\beta,\alpha,r}
}
R_{X,\beta,\alpha,r}
P_{X,\alpha}^{\mathrm{enc},(\beta)}.
\]

A correction family claiming RFC-0010 conformance MUST declare evidence for
the applicable conditions below.

## 9.1 Uniform synthesis

Each correction MUST be generated uniformly from admitted instance and
backend data without solution-dependent advice.

## 9.2 Protected-manifold compatibility

For an exact protected realization,

\[
\left(
I-\Pi_{\mathrm{stab}}
\right)
R_{X,\beta,\alpha,r}
\Pi_{\mathrm{stab}}
=
0.
\]

For an approximate realization, the backend MUST expose an explicit leakage
bound.

## 9.3 Logical intertwining

When a logical correction model is claimed, there MUST exist a declared
logical operator
\(\widetilde R_{X,\beta,\alpha,r}\)
such that

\[
\Pi_{\mathrm{stab}}
R_{X,\beta,\alpha,r}
\Pi_{\mathrm{stab}}
=
V
\widetilde R_{X,\beta,\alpha,r}
V^\dagger.
\]

## 9.4 Terminal silence

The correction channel MUST become silent on the semantic terminal sector:

\[
R_{X,\beta,\alpha,r}
P_{X,\alpha}^{\mathrm{enc},(\beta)}
\Pi^{\mathrm{sem}}_{X,\beta}
=
0.
\]

Operationally, this ensures that local semantic correction channels cease to
act once the system enters the declared target sector.

## 9.5 Dark-vector completeness

If a backend claims that its common pure dark-vector sector equals the
semantic target, it MUST provide evidence for a condition of the form

\[
\left(
\bigcap_{\alpha,r}
\ker
L_{X,\beta,\alpha,r}
\right)
\cap
\mathcal C_{\mathrm{stab}}
=
\mathcal G^{\mathrm{sem}}_{X,\beta}.
\]

A dark-vector statement MUST NOT be reported as a complete fixed-density-state
statement unless the latter has been established separately.

---

# 10. Fixed-point evidence

RFC-0010 distinguishes dark-vector evidence from stationary-state evidence.

Hamiltonian evolution, stationary coherences, decoherence-free subsystems, or
other invariant operator structures may enlarge the set of stationary density
operators beyond the common pure dark-vector sector.

A Level-II exact compatibility claim therefore MUST establish

\[
\operatorname{Fix}_{\mathrm{stab}}
\left(
\mathcal L_{X,\beta}
\right)
=
\mathfrak S
\left(
\mathcal G^{\mathrm{sem}}_{X,\beta}
\right),
\]

or provide a mathematically equivalent statement.

The execution evidence MUST identify:

- the fixed-point definition;
- the admitted state space;
- the semantic target;
- the proof, certificate, computation, or external evidence supporting the
  equality; and
- whether the claim is exact or approximate.

Absence of spurious pure dark vectors alone is insufficient evidence for this
claim.

---

# 11. Penalty-Lyapunov convergence evidence

A backend MAY support a convergence claim by exposing a penalty-Lyapunov
certificate.

For rate
\(\gamma_{X,\beta}>0\),
the certificate asserts

\[
\operatorname{Tr}
\left[
H^{\mathrm{enc}}_{X,\beta}
\mathcal L_{X,\beta}(\rho)
\right]
\le
-
\gamma_{X,\beta}
\operatorname{Tr}
\left[
H^{\mathrm{enc}}_{X,\beta}
\rho
\right]
\]

over the declared admitted state domain.

Under the stated assumptions this yields

\[
E(t)
\le
E(0)
e^{-\gamma_{X,\beta}t}.
\]

The certificate MUST identify:

- the encoded penalty;
- the admitted state domain;
- \(\gamma_{X,\beta}\);
- the method used to establish the inequality;
- numerical or symbolic tolerances, if applicable; and
- the realization status.

A reported \(\gamma_{X,\beta}\) MUST NOT be called a Liouvillian spectral gap
unless the backend separately establishes that identification.

---

# 12. Positive penalty scale and terminal-support bound

When the positive encoded spectrum is discrete and nonempty, define

\[
\Delta_{X,\beta}
=
\min
\left(
\operatorname{spec}
\left(
H^{\mathrm{enc}}_{X,\beta}
\big|_{\mathcal C_{\mathrm{stab}}}
\right)
\setminus
\{0\}
\right).
\]

If

\[
H^{\mathrm{enc}}_{X,\beta}
\succeq
\Delta_{X,\beta}
\left(
\Pi_{\mathrm{stab}}
-
\Pi^{\mathrm{sem}}_{X,\beta}
\right),
\]

then the backend MAY derive a target-sector support bound of the form

\[
\operatorname{Tr}
\left[
\left(
\Pi_{\mathrm{stab}}
-
\Pi^{\mathrm{sem}}_{X,\beta}
\right)
\rho_t
\right]
\le
\frac{
E(0)e^{-\gamma_{X,\beta}t}
}{
\Delta_{X,\beta}
}.
\]

A backend using this bound MUST expose both
\(\gamma_{X,\beta}\)
and
\(\Delta_{X,\beta}\).

A convergence-time claim MUST include every additional factor required to turn
this inequality into the claimed terminal error.

---

# 13. Resource accounting

A Level-III efficiency claim MUST account for the resources required by:

1. instance compilation;
2. preparation;
3. stabilization synthesis;
4. problem-generator synthesis;
5. interaction locality or nonlocal-interaction synthesis;
6. coefficient precision;
7. external control precision;
8. convergence time;
9. leakage suppression;
10. measurement;
11. calibration;
12. repeated sampling;
13. decoding; and
14. any classical preprocessing or postprocessing.

A polynomial convergence claim MUST expose a fixed polynomial bound in the
declared logical input-size measure.

The existence of an exact static representation MUST NOT be used as evidence
of efficient physical synthesis.

The existence of an exact dissipative fixed-point relation MUST NOT be used as
evidence of polynomial convergence.

---

# 14. Global-energy-shift obstruction

Consider Hamiltonians related by

\[
H_1
=
H_0
+
\Delta I.
\]

For normalized closed-system density-operator evolution,

\[
e^{-itH_1}
\rho
e^{itH_1}
=
e^{-itH_0}
\rho
e^{itH_0}.
\]

Whenever the normalized Gibbs state is well defined, it is likewise
invariant under the same scalar shift.

Therefore, if a semantic distinction is encoded solely as an absolute scalar
Hamiltonian shift, an observation model whose admitted normalized state data
are invariant under

\[
H
\mapsto
H+\Delta I
\]

cannot recover that distinction without additional operational structure.

An RFC-0010 backend claiming absolute-energy discrimination MUST therefore
declare either:

- an external operational reference;
- a shift-sensitive observable; or
- another explicitly justified mechanism that breaks the invariance.

A backend MUST NOT certify absolute-energy decoding from invariant normalized
state data alone.

---

# 15. External operational reference

When an external reference is required, the execution specification MUST
identify it explicitly.

A reference record SHOULD include:

- reference type;
- stable identity;
- nominal value or parameter set;
- calibration procedure;
- calibration timestamp;
- calibration uncertainty;
- admitted drift or perturbation region;
- instrumentation identity;
- provenance; and
- evidence digest where applicable.

Reference calibration MUST be independent of the independently computed
semantic answer for the execution being validated. Calibration data MUST NOT
contain expected continuation values, expected decoded outputs, satisfying
assignments, completion tables, or equivalent answer-dependent tuning
information.

For microwave-referenced execution, a reference MAY include

\[
R
=
\left(
\omega_{\mathrm{LO}},
\phi_{\mathrm{LO}},
A_{\mathrm{LO}}
\right),
\]

or an equivalent experimentally meaningful parameterization.

RFC-0009 evidence-integrity requirements continue to apply to recorded
reference and calibration artifacts.

---

# 16. Referenced measurement model

An RFC-0010 backend MUST distinguish:

- physical state;
- admitted measurement;
- recorded observation;
- decoder; and
- independent semantic comparison.

For semantic class \(c\), let

\[
P^{R'}_{X,c}
\]

denote the admitted physical outcome distribution when the realized reference
is \(R'\).

The backend MUST identify the measurement model from which this distribution
is defined or estimated.

Internal backend state not admitted by the declared observable interface MUST
NOT be used by the semantic decoder.

This is the RFC-0010 specialization of the Restricted Interface Principle.

---

# 17. Fixed decoder and robust decision regions

A referenced decoder MAY use pairwise disjoint decision regions

\[
\{\Omega_c\}_{c\in\mathcal C_X}.
\]

For nominal reference \(R\) and admitted perturbation neighborhood
\(B_\delta(R)\), a robust decoding claim MAY use the condition

\[
\inf_{R'\in B_\delta(R)}
P^{R'}_{X,c}
\left(
\Omega_c
\right)
\ge
1-\epsilon
\]

for every semantic class \(c\).

The decoder and its decision regions MUST be fixed from admitted
backend, reference, and calibration data before independent semantic
comparison. They MUST NOT be selected, tuned, or altered using the expected
semantic answer for the execution being validated.

The backend MUST expose:

- the decision regions;
- decoder identity;
- calibration neighborhood;
- declared error bound;
- evidence supporting the separation claim; and
- realization status.

If a scalar decision margin \(\Gamma\) and total implementation uncertainty
\(\eta\) are used, the backend MUST state the inequality required for
correctness, for example

\[
\eta
<
\Gamma.
\]

A backend MUST NOT report robustness when the declared error budget saturates
or exceeds the required decision margin.

---

# 18. Exact and approximate realization

Physical open-system realizations will often be approximate.

RFC-0010 therefore requires explicit classification.

An exact claim MUST establish the exact condition it names.

An approximate claim MUST expose a quantitative error or leakage parameter.

Relevant quantities MAY include:

- protected-manifold leakage;
- generator approximation error;
- calibration uncertainty;
- finite-time convergence error;
- readout noise;
- state-preparation error;
- detector error; and
- decoder error.

The total semantic-success statement MUST identify how these errors compose.

The value `unknown` MUST be preferred over an unsupported zero-error claim.

---

# 19. Relationship to RFC-0009 physical evidence

RFC-0009 remains authoritative for physical execution evidence and substrate
conformance.

RFC-0010 adds open-system-specific evidence categories.

An RFC-0010 physical execution MAY bind, through RFC-0009 evidence records:

- prepared-execution identity;
- physical-device identity;
- generator-control artifact identity;
- programming or calibration records;
- stabilization configuration;
- problem-generator configuration;
- execution-event records;
- reference identity;
- calibration records;
- measurement records;
- admitted observations; and
- decoder identity.

Physical-evidence completeness MUST remain distinct from semantic correctness.

A complete physical record MAY show that a declared open-system experiment
occurred while the decoded result is semantically incorrect.

A semantically correct decoded result MUST NOT be used by itself as evidence
that the declared physical experiment occurred.

---

# 20. Conformance groups

RFC-0010 defines four conformance groups.

## 20.1 OS: open-system architecture

- **OS-1** Stabilization/problem-generator separation.
- **OS-2** Protected-manifold identity.
- **OS-3** Uniform instance-dependent generator synthesis.
- **OS-4** Answer-independent generator construction.
- **OS-5** Protected correction-family declaration.
- **OS-6** Terminal-silence evidence.
- **OS-7** Dark-vector-sector evidence when claimed.
- **OS-8** Fixed-point-set evidence for Level-II claims.

## 20.2 DC: dissipative convergence

- **DC-1** Declared semantic penalty observable.
- **DC-2** Positive penalty-scale evidence when used.
- **DC-3** Penalty-Lyapunov evidence when claimed.
- **DC-4** Convergence-rate evidence.
- **DC-5** Leakage accounting.
- **DC-6** Runtime and resource accounting.

## 20.3 RR: referenced readout

- **RR-1** External-reference identity when required.
- **RR-2** Reference calibration record.
- **RR-3** Calibration-neighborhood specification.
- **RR-4** Referenced measurement model.
- **RR-5** Decision-region specification.
- **RR-6** Fixed decoder.
- **RR-7** Robust separation evidence.
- **RR-8** Declared measurement-error bound.

## 20.4 OV: observation and validation

- **OV-1** `ObservableExecution` contains only admitted observations.
- **OV-2** Semantic validation remains outside the backend dependency graph.
- **OV-3** Physical evidence remains distinct from semantic correctness.
- **OV-4** Exact versus approximate realization status is explicit.

A backend profile MAY require only a declared subset of these groups, but it
MUST NOT claim a higher realization level without satisfying all conformance
requirements relevant to that level.

---

# 21. Failure semantics

RFC-0010 validation MUST fail closed.

Missing evidence MUST NOT be interpreted as successful conformance.

At minimum, validation MUST reject or report nonconformance for:

- missing protected-manifold identity when one is claimed;
- missing stabilization/problem-generator separation;
- solution-dependent problem-generator input;
- undeclared semantic target;
- unsupported exact fixed-point claims;
- nonpositive declared convergence rates;
- missing convergence evidence for Level-III claims;
- missing required external reference;
- missing calibration information;
- decoder dependence on undeclared internal backend state;
- missing error-budget information for robustness claims; and
- total declared uncertainty incompatible with the declared decision margin.

A validator SHOULD distinguish malformed evidence from valid evidence that
fails a physical or semantic requirement.

---

# 22. Security and integrity considerations

RFC-0010 introduces additional control and calibration artifacts that may
affect semantic interpretation.

Implementations SHOULD bind these artifacts through RFC-0009 provenance and
digest mechanisms.

In particular, a conforming evidence package SHOULD make substitution of any
of the following independently detectable:

- stabilization configuration;
- problem-generator configuration;
- external reference;
- calibration record;
- measurement model;
- decoder; or
- semantic-target declaration.

The semantic reference computation MUST remain independently derived from the
original admitted instance.

---

# 23. Reproducibility requirements

A reproducible RFC-0010 backend SHOULD provide enough information to recreate,
within its declared realization class:

- the open-system execution specification;
- the protected-manifold model;
- stabilization controls;
- problem-generator controls;
- convergence certificate or measurement;
- external reference;
- calibration procedure;
- readout protocol;
- decoder; and
- resource report.

Simulation-specific random seeds, solver tolerances, truncation dimensions,
and integration tolerances MUST be recorded when they can affect the admitted
result.

For an infinite-dimensional physical model represented by finite truncation,
the truncation procedure and admitted truncation error MUST be explicit.

---

# 24. Substrate neutrality

RFC-0010 is substrate neutral.

A backend MAY target:

- superconducting bosonic systems;
- other engineered open quantum systems;
- optical dissipative systems;
- trapped-ion or atomic open-system platforms;
- hybrid systems;
- numerical Lindbladian simulators; or
- another substrate satisfying the same execution and evidence contract.

The use of superconducting bosonic hardware as a motivating implementation
does not make bosonic protection part of CPC semantic quotienting.

Likewise, RFC-0010 does not require the physical substrate to reproduce the
ontology of any representation-theoretic construction that motivated CPC.

Conformance is determined by the declared semantic, dynamical, evidence, and
readout contracts.

---

# 25. Non-claims

RFC-0010 does not establish:

- a general efficient physical solver for CPC instances;
- a polynomial convergence bound for an arbitrary open-system generator;
- a local physical synthesis of every extensional penalty Hamiltonian;
- a superconducting implementation of arbitrary CPC semantic dynamics;
- equivalence between physical error correction and semantic quotienting;
- equality between a penalty-Lyapunov rate and a Liouvillian spectral gap;
- absolute-energy observability without an appropriate reference or
  shift-sensitive observable;
- physical authenticity from cryptographic identity alone; or
- semantic correctness from physical-evidence completeness alone.

These questions require separate mathematical, physical, or experimental
evidence.

---

# 26. Implementation plan

RFC-0010 is a Draft architectural specification.

Implementation MUST NOT be treated as authorizing acceptance of the RFC.

The intended implementation sequence after architectural review is:

1. canonical RFC-0010 conformance data models;
2. validators for OS, DC, RR, and OV evidence;
3. positive and negative regression tests;
4. documentation of open-system backend qualification;
5. backend-specific profiles; and
6. release qualification under the existing CPC validation architecture.

Implementation commits SHOULD reference RFC-0010.

---

# 27. Acceptance criteria

RFC-0010 MAY advance from Draft to Review when:

1. the distinction between stabilization and semantic dynamics is agreed;
2. the four-level realization hierarchy is agreed;
3. the fixed-point and dark-vector requirements are mathematically
   unambiguous;
4. the convergence-evidence requirements are considered implementable;
5. the global-energy-shift obstruction and external-reference requirements
   are correctly scoped;
6. RFC-0009 integration is coherent; and
7. no requirement permits answer information to enter through compilation,
   preparation, calibration, measurement, decision-region selection, or
   decoding.

RFC-0010 MAY advance to Accepted only after review of the normative text and
the repository governance process required for accepted RFCs.

---

# 28. Summary

RFC-0010 extends CPC validation from generic physical-execution evidence to a
typed open-system realization contract.

The architecture is

\[
\boxed{
\text{semantic target}
\rightarrow
\text{protected representation}
\rightarrow
\text{instance-dependent dynamics}
\rightarrow
\text{convergence evidence}
\rightarrow
\text{referenced observation}
\rightarrow
\text{fixed decoding}
\rightarrow
\text{independent semantic validation}
}
\]

with

\[
\boxed{
\mathcal L_{X,\beta}
=
\mathcal L_{\mathrm{stab}}
+
\mathcal L^{\mathrm{prob}}_{X,\beta}.
}
\]

The RFC makes exact representation, dissipative compatibility, efficient
convergence, and robust readout separately testable claims.

That separation is the basis for extending CPC validation to
driven-dissipative physical computation without conflating semantic
representation with physical stabilization or scalable hardware synthesis.
