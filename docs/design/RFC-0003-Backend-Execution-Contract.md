# RFC-0003

# Backend Execution Contract

Status: Draft

Supersedes: —

Depends on: RFC-0001, RFC-0002

---

## 1. Purpose

RFC-0002 establishes the Core Constraint Intermediate Representation (CCIR)
as the canonical backend-independent representation.

RFC-0003 defines the canonical backend execution contract

CCIR → ExecutionArtifact

independently of any concrete execution substrate.

---

## 2. Scope

RFC-0003 specifies

- backend compilation;
- execution artifacts;
- provenance;
- answer independence;
- compiler validation;
- semantic validation; and
- backend independence.

RFC-0003 does not specify

- source languages;
- DIMACS parsing;
- CCIR;
- optimization passes; or
- backend implementations.

---

## 3. Backend Contract

Let `C_X` denote a valid CCIR program representing an admitted constraint
instance `X`.

Every conforming backend SHALL implement a compilation map

<pre>
Compile_backend : CCIR -> ExecutionArtifact
</pre>

The backend contract has exactly one canonical semantic input: `C_X`.

A backend SHALL NOT require source-language objects in addition to CCIR.

In particular, backend compilation SHALL NOT depend on:

- `ParityInstance`;
- `CNFInstance`;
- DIMACS input;
- benchmark JSON; or
- any other source-language representation once CCIR has been constructed.

The result of backend compilation is an execution artifact `A_X`:

<pre>
C_X
 |
 v
Compile_backend
 |
 v
A_X
</pre>

A conforming backend MAY realize `A_X` using any admitted execution mechanism,
including:

- static networks;
- dynamical systems;
- digital logic;
- physical hardware; or
- simulation artifacts.

The backend contract constrains the information boundary and semantic role of
compilation. It does not prescribe the internal realization mechanism of a
backend.

Concrete backend implementations are specializations of the general contract.

For example:

<pre>
Compile_RC : CCIR -> RCArtifact
</pre>

A future backend MAY define another artifact type while preserving the same
canonical CCIR input boundary.

### 3.1 Backend Capability Declaration

Every conforming backend SHALL publish a backend capability declaration.

The capability declaration SHALL identify the admitted CCIR constraint
families, interface features, execution features, and artifact features
implemented by that backend.

A backend SHALL reject any CCIR program requiring unsupported capabilities
before execution-artifact generation begins.

Such rejection SHALL be deterministic and SHALL depend only on the admitted
CCIR program and the declared backend capabilities.

Capability rejection SHALL NOT depend on the independently computed semantic
answer or on any answer-equivalent surrogate.

A backend MAY implement only a subset of the constraint families or execution
features admitted by the current CCIR specification.

A backend capability declaration therefore defines the domain on which

    Compile_backend : CCIR -> ExecutionArtifact

is required to succeed.

CCIR programs outside that declared domain SHALL fail compilation explicitly
and SHALL NOT proceed to artifact generation, execution, or semantic
validation.

Capability declarations allow different conforming backends to support
different admitted CCIR subsets while preserving the same canonical backend
contract.

## 4. Execution Artifact

For an admitted CCIR program `C_X`, backend compilation SHALL produce an
execution artifact

    A_X = (T_X, P_X, I_X, M_X, Pi_X)

with the following required components.

### 4.1 Topology

`T_X` is the complete backend execution topology.

Depending on the backend, topology MAY describe nodes, edges, components,
logic elements, dynamical couplings, state variables, or other structural
execution elements.

### 4.2 Backend Parameters

`P_X` contains the backend-specific parameters required to instantiate the
artifact.

Examples MAY include component values, dynamical coefficients, thresholds,
timing constants, logic configuration, or simulator parameters.

### 4.3 Interface Specification

`I_X` defines the admitted execution interface.

It SHALL identify the boundary or control inputs, prescribed observables,
readout channel, and any information required by the fixed decoder.

### 4.4 Backend Metadata

`M_X` contains metadata required to identify and reproduce the compilation.

Metadata MAY include the backend identifier, compiler version, fixed backend
configuration, serialization version, or calibration identifier.

### 4.5 Provenance

`Pi_X` is a machine-checkable provenance map

    Pi_X : ArtifactElement -> CCIROrigin union BackendRule

`CCIROrigin` SHALL identify machine-resolvable admitted CCIR data sufficient to
recover the structural compiler input responsible for the generated element.

`BackendRule` SHALL identify a machine-resolvable globally fixed backend rule
registered in `Theta_backend`.

When an artifact element is produced by applying a backend rule to admitted
CCIR data, its provenance SHALL permit an auditor to recover both the relevant
CCIR origin and the applied backend rule through the recorded provenance
structure.

A generic or opaque provenance label such as `generated_by_compiler` SHALL NOT
satisfy this requirement.

Every generated artifact element SHALL be traceable to admitted CCIR data, a
globally fixed backend rule, or both as required by the generation step.

No generated artifact element SHALL lack provenance.

Backend-local auxiliary state MAY be introduced when required by the execution
mechanism, but every such element SHALL have provenance under `Pi_X`.

The execution-artifact contract does not require artifacts to be static.
An artifact MAY represent a static network, a dynamical system, a simulator
configuration, programmable logic, physical hardware configuration, or another
backend-defined realization.

## 5. Compiler Dependency Principle

Let `D(C_X)` denote the complete dependency set of backend compilation for an
admitted CCIR program `C_X`.

RFC-0003 requires

    D(C_X) = { C_X, Theta_backend }

where `Theta_backend` denotes the globally fixed rules, constants,
configurations, and calibration data admitted by the backend specification.

A conforming backend SHALL derive every generated artifact solely from:

- the admitted CCIR program `C_X`; and
- `Theta_backend`.

No instance-specific information outside `C_X` SHALL influence compilation.

`Theta_backend` SHALL be fixed independently of the semantic outcome of the
instance being compiled.

Backend rules MAY depend on structural CCIR properties such as:

- constraint family;
- local constraint payload;
- variable incidence;
- constraint arity;
- boundary or interface role; and
- other explicitly admitted structural data represented in CCIR.

Backend rules MAY also depend on globally fixed backend quantities such as:

- component libraries;
- physical constants;
- calibrated device parameters;
- simulator settings;
- serialization rules; and
- backend-wide numerical tolerances.

Such quantities SHALL be selected independently of the semantic answer of any
particular admitted instance.

The compiler dependency principle applies to every stage that contributes to
the final execution artifact, including topology construction, parameter
generation, interface construction, metadata generation, auxiliary-state
construction, and serialization.

Any intermediate compilation stage whose output can influence `A_X` SHALL
itself satisfy the same dependency boundary.

## 6. Answer Independence

Answer independence is a formal compiler dependency condition.

Let

    Eval(X)

denote the independent semantic evaluator for the admitted instance `X`.

RFC-0003 requires

    Eval(X) notin D(C_X)

where `D(C_X)` is the compiler dependency set defined in Section 5.

Accordingly, backend compilation SHALL NOT consume, derive, reconstruct,
query, cache, encode, or otherwise depend upon semantic information that is
equivalent to the expected execution outcome.

This prohibition includes, but is not limited to:

- satisfying assignments;
- completion enumerations;
- completion counts;
- residual satisfiability tables;
- continuation tables;
- expected decoder outputs;
- externally supplied reference answers;
- cached execution results;
- precomputed truth tables; and
- any surrogate carrying equivalent semantic information.

Changing, corrupting, substituting, withholding, or otherwise modifying only
the externally supplied output of the independent reference evaluator SHALL
NOT alter the generated execution artifact.

Changing only the independent validation pipeline SHALL NOT alter the generated
execution artifact.

A conforming validation suite SHOULD include negative-control tests in which
external reference outputs are deliberately altered or withheld while
compilation is repeated from the same `C_X` and `Theta_backend`.

The resulting execution artifacts SHALL remain equivalent under the declared
artifact-equivalence rules.

Answer independence is therefore a property of backend compilation itself and
not merely of the validation procedure.

## 7. Physical Compilation Discipline

The backend compiler SHALL construct execution artifacts exclusively from
admitted CCIR data and globally fixed backend rules.

### 7.1 Constraint-Derived Topology

Every generated node, edge, component, coupling, interface, or execution
element SHALL be derivable from:

- admitted CCIR data;
- admitted interface information; or
- a globally fixed backend rule.

Topology SHALL NOT depend on semantic answers.

### 7.2 Fixed Parameter Rules

Backend parameters SHALL be generated by deterministic compilation rules.

Conceptually,

    theta = g(local CCIR data, Theta_backend)

and SHALL NOT depend upon semantic outcomes.

### 7.3 Deterministic Compilation

Repeated compilation of the same canonical CCIR program under the same
`Theta_backend` SHALL produce equivalent execution artifacts.

RFC-0003 does not require semantically equivalent but structurally distinct
CCIR programs to compile to identical artifacts unless a separate
canonicalization rule explicitly requires that behavior.

Any quantity capable of influencing `A_X` SHALL be fixed before compilation
and SHALL belong to `C_X` or `Theta_backend`.

### 7.4 Canonical Provenance

Every artifact element SHALL remain traceable through the provenance map
defined in Section 4.

Backend-local auxiliary elements SHALL also possess provenance.

The compiler SHALL preserve provenance throughout every compilation stage.

## 8. Compiler Validation

Compiler validation determines whether an execution artifact was generated in
conformance with the backend compilation contract.

Compiler validation is distinct from semantic validation.

Compiler validation SHALL establish that the artifact satisfies the structural
and dependency requirements of Sections 3 through 7 without consulting the
independent semantic evaluator.

### 8.1 Dependency Audit

The validator SHALL verify that backend compilation depends only on:

- the admitted CCIR program `C_X`; and
- the globally fixed backend specification `Theta_backend`.

No semantic oracle or answer-derived dependency MAY participate in compiler
validation or artifact generation.

### 8.2 Provenance Audit

The validator SHALL verify that every generated artifact element has exactly
the provenance required by the execution-artifact contract.

Every artifact element SHALL be traceable through `Pi_X` to either:

- admitted CCIR data; or
- a globally fixed backend rule.

An artifact with missing, unresolved, or inadmissible provenance SHALL fail
compiler validation.

### 8.3 Topology and Parameter Audit

The validator SHALL verify that generated topology and backend parameters can
be reproduced from `C_X` and `Theta_backend` alone.

Topology or parameter values that require semantic answers, satisfying
assignments, completion information, expected outputs, or equivalent semantic
surrogates SHALL cause compiler validation to fail.

### 8.4 Reproducibility Audit

Repeated compilation of the same canonical CCIR input under the same fixed
backend specification SHALL produce equivalent execution artifacts.

Any permitted variability capable of influencing the generated artifact
SHALL be fixed before compilation and represented in `Theta_backend`.

Backend metadata MAY record such variability for audit and reproduction, but
metadata SHALL NOT introduce or authorize a compiler dependency that was not
already contained in `C_X` or `Theta_backend`.

### 8.5 Family-Level Validation

A conforming backend SHALL be validated across an admitted family of instances
using one unchanged compiler and one unchanged backend rule set.

Instance-specific hand tuning outside admitted CCIR data SHALL NOT be used to
obtain successful compilation or execution behavior.

Compiler validation therefore answers:

    Was A_X generated only from permitted compilation inputs?

It does not answer:

    Does A_X produce the correct semantic result?

That question is reserved exclusively for semantic validation.

## 9. Semantic Validation

Semantic validation determines whether an independently executed backend
artifact reproduces the independently defined semantic result of the admitted
instance.

Semantic validation SHALL remain separate from compiler validation.

For an admitted instance `X`, let:

    X -> C_X -> A_X -> Execute -> o_X -> Decode -> d_X

denote the compilation and execution path, where:

- `C_X` is the canonical CCIR program;
- `A_X` is the execution artifact;
- `o_X` is the admitted observable or readout result; and
- `d_X` is the decoded semantic result.

Independently, let:

    X -> Eval -> e_X

denote the reference semantic path.

Semantic correctness requires:

    d_X = e_X

### 9.1 Independent Evaluation

`Eval` SHALL be defined and executed independently of backend compilation.

The output `e_X` SHALL NOT influence:

- CCIR construction;
- backend compilation;
- artifact topology;
- artifact parameters;
- backend metadata;
- backend-local auxiliary state;
- execution preparation;
- prescribed readout; or
- decoder selection.

The independent semantic result MAY be consulted only after the backend
execution path has produced `d_X`.

### 9.2 Post-Execution Comparison

The semantic validator SHALL compare `d_X` with `e_X` only after:

- compilation has completed;
- the execution artifact has been finalized;
- execution has completed;
- the prescribed observable has been read; and
- the fixed decoder has produced `d_X`.

A backend SHALL NOT be recompiled, modified, recalibrated, or otherwise
instance-tuned in response to a semantic-validation mismatch unless the change
is adopted as a new globally fixed backend rule and the affected validation
family is rerun.

### 9.3 Complete Admitted Interface Validation

For instances with multiple admitted boundary or interface conditions,
semantic validation SHALL evaluate every condition required by the declared
validation profile.

The validator SHALL record both the independently computed reference result and
the independently decoded backend result for each admitted condition.

### 9.4 Validation Failure

Semantic validation SHALL fail whenever:

    d_X != e_X

for any condition required by the declared validation profile.

Compiler conformance does not imply semantic correctness.

Semantic correctness does not imply compiler conformance.

A backend is conforming only when both compiler validation and semantic
validation succeed under the applicable RFC-0003 requirements.

## 10. Backend Independence

RFC-0003 permits multiple backend implementations to realize the same admitted
CCIR program using different execution mechanisms.

Let `B_1` and `B_2` be two conforming backends.

For the same admitted CCIR program `C_X`, they MAY produce structurally
different execution artifacts:

    Compile_B1(C_X) = A_X^(1)

    Compile_B2(C_X) = A_X^(2)

Backend independence does not require identical topology, parameters, internal
state, or execution mechanism across backends.

It requires semantic agreement at the admitted decoded interface.

For every admitted instance and interface condition required by the declared
validation profile, conforming backends SHALL satisfy:

    Decode_B1(Execute_B1(A_X^(1))) =
    Decode_B2(Execute_B2(A_X^(2)))

whenever both backends satisfy semantic validation for the same independently
defined semantic result.

Equivalently, if

    Decode_B1(Execute_B1(A_X^(1))) = e_X

and

    Decode_B2(Execute_B2(A_X^(2))) = e_X

then the backend realizations are semantically equivalent with respect to the
admitted interface.

### 10.1 Source-Language Independence

Adding a new source language SHALL NOT require modification of a conforming
backend provided that the new front end lowers the source instance into valid
CCIR admitted by that backend.

A backend SHALL NOT depend on the identity of the source language from which
the CCIR program originated.

### 10.2 Backend Substitutability

Adding or replacing a backend SHALL NOT require modification of admitted
source-language semantics or source-to-CCIR lowering.

Backend-specific realization choices SHALL remain below the CCIR boundary.

### 10.3 Backend-Specific Auxiliary Structure

A backend MAY introduce auxiliary state, topology, parameters, preparation
rules, or execution mechanisms that do not exist in CCIR.

Such backend-specific structure SHALL:

- satisfy the compiler dependency principle;
- satisfy answer independence;
- possess complete provenance;
- remain internal to the backend unless explicitly exposed by the admitted
  interface; and
- preserve semantic correctness at the prescribed decoded interface.

### 10.4 Semantic Equivalence Boundary

Backend equivalence is defined relative to the admitted semantic interface.

RFC-0003 does not require two conforming backends to reproduce identical
internal trajectories, physical states, timing behavior, resource usage, or
artifact structure.

Those quantities MAY differ and SHALL be reported separately when required by
the applicable validation profile.

## 11. Restricted Interface Principle

Semantic correctness SHALL be established exclusively through the admitted
execution interface defined by `I_X`.

The validator SHALL observe only the prescribed readout channel and SHALL apply
only the fixed decoder associated with that interface.

The validation question is therefore:

    Does the prescribed interface decode to the independently defined
    semantic result?

It is not:

    Can the semantic result be reconstructed from arbitrary internal backend
    state?

### 11.1 Admitted Observable

For each execution artifact, `I_X` SHALL identify the observable or finite set
of observables that constitute the admitted semantic readout channel.

The validator SHALL NOT inspect additional internal state for the purpose of
recovering or improving the semantic result.

### 11.2 Fixed Decoder

The decoder SHALL be selected independently of the semantic answer of the
particular instance or interface condition being validated.

A decoder MAY depend on:

- the backend type;
- the admitted interface specification;
- globally fixed calibration data; and
- globally fixed decoding rules.

The decoder SHALL NOT depend on:

- `Eval(X)`;
- satisfying assignments;
- completion information;
- expected outputs; or
- hidden backend state outside the admitted interface.

### 11.3 No Post-Hoc State Search

Validation SHALL NOT search internal trajectories, hidden node values,
auxiliary variables, simulator state, or other non-interface information for
a representation of the semantic answer.

The existence of answer-correlated information somewhere inside the execution
artifact is insufficient to establish semantic correctness.

Only the prescribed decoded interface result `d_X` is admissible for semantic
comparison.

### 11.4 Interface Stability

For one declared backend configuration and validation profile, the admitted
readout interface and decoder SHALL remain unchanged across the admitted
instance family unless the change is adopted as a new globally fixed backend
rule.

Instance-specific interface selection or decoder tuning SHALL NOT be used to
obtain successful semantic validation.

### 11.5 Separation from Diagnostic Observation

A backend MAY expose additional internal observables for engineering,
debugging, physical analysis, or resource measurement.

Such diagnostic observables SHALL be explicitly distinguished from the
semantic interface and SHALL NOT participate in the semantic correctness
decision.

The restricted interface principle therefore preserves a strict separation
between:

- semantic readout;
- internal diagnostics; and
- independent reference evaluation.

## 12. RC Reference Backend

The RC backend is the first reference implementation of the RFC-0003 backend
execution contract.

Its concrete compilation map is

    Compile_RC : CCIR -> RCArtifact

The RC backend SHALL satisfy every normative requirement of Sections 3
through 11.

The RC backend is a reference implementation only. RC-specific topology,
component models, parameter choices, simulation mechanisms, and serialization
formats SHALL NOT become requirements on other conforming backends.

### 12.1 Constraint-Derived RC Topology

The RC compiler SHALL derive generated network topology from:

- admitted CCIR constraints;
- admitted CCIR variable and interface relations; and
- globally fixed RC backend rules.

The RC compiler SHALL NOT generate topology from independently computed
continuation values, satisfying assignments, completion tables, expected
outputs, or equivalent semantic surrogates.

Every generated RC node, connection, source, passive component, auxiliary
element, and interface element SHALL possess provenance under `Pi_X`.

### 12.2 Fixed RC Parameter Rules

RC component parameters SHALL be generated from admitted structural CCIR data
and globally fixed RC backend parameters.

Conceptually,

    theta_e = g(local CCIR data, Theta_RC)

where `Theta_RC` is fixed independently of the semantic answer of the
particular instance.

Instance-specific hand tuning based on reference outcomes SHALL NOT be used.

### 12.3 RC Execution Artifact

An `RCArtifact` SHALL contain, directly or through a deterministic
serialization:

- the generated RC topology;
- component and source parameters;
- boundary and control specification;
- prescribed readout specification;
- backend metadata; and
- complete artifact provenance.

The serialized SPICE or ngspice representation SHALL be reproducible from the
corresponding `RCArtifact`.

### 12.4 RC Execution and Readout

RC execution MAY be performed by ngspice or another explicitly admitted
simulator compatible with the declared RC backend profile.

Semantic validation SHALL use only the prescribed RC interface and fixed
decoder.

Internal node voltages, simulator state, intermediate trajectories, or other
diagnostic information SHALL NOT be used to infer the semantic result unless
they are explicitly part of the admitted readout interface.

### 12.5 Multi-Instance Validation

The RC reference backend SHALL be validated across an admitted family of
constraint instances using:

- one unchanged RC compiler;
- one unchanged `Theta_RC`;
- one unchanged readout rule; and
- one unchanged decoder.

At minimum, the validation family SHALL contain multiple structurally distinct
parity instances.

As CCIR clause execution support is introduced, the same RFC-0003 contract
SHALL apply without changing the source-language or backend dependency
boundaries.

### 12.6 Behavioral Baseline Replacement

The current direct behavioral response realization SHALL be treated as a
validation baseline, not as the final RFC-0003 reference implementation.

RFC-0003 implementation SHALL replace direct answer-conditioned behavioral
response realization with constraint-derived RC topology and fixed compilation
rules satisfying answer independence.

The independent reference evaluator SHALL remain outside the RC compilation
dependency graph and SHALL be used only for post-execution semantic validation.

### 12.7 RC Artifact Audit

The RC validation suite SHALL provide machine-checkable checks establishing
that:

- every generated artifact element has admissible, machine-resolvable
  provenance;
- topology is reproducible from CCIR and `Theta_RC`;
- component parameters are reproducible from CCIR and `Theta_RC`;
- no oracle-derived artifact fields are present;
- altered, substituted, or withheld external reference outputs do not
  influence compilation; and
- the prescribed interface alone determines the decoded semantic result.

## 13. Acceptance Criteria

A backend implementation conforms to RFC-0003 only when all applicable
requirements of this section are satisfied.

### 13.1 Canonical Backend Input

The backend SHALL consume valid CCIR as its canonical semantic input.

The backend SHALL NOT require source-language objects, source files, benchmark
formats, independently computed semantic answers, or other instance-specific
inputs outside the admitted CCIR and globally fixed backend specification.

### 13.2 Complete Execution Artifact

Backend compilation SHALL produce an execution artifact satisfying the
ExecutionArtifact contract of Section 4.

The artifact SHALL contain or deterministically define:

- topology;
- backend parameters;
- interface and readout specification;
- backend metadata; and
- complete provenance.

Every generated artifact element SHALL have admissible provenance.

### 13.3 Compiler Dependency Conformance

The complete backend compilation dependency set SHALL satisfy:

    D(C_X) = { C_X, Theta_backend }

Every stage capable of influencing the final execution artifact SHALL respect
this dependency boundary.

### 13.4 Answer Independence

The independent semantic evaluator and every answer-equivalent surrogate SHALL
remain outside the compilation dependency graph.

Compilation SHALL NOT consume, derive, reconstruct, query, cache, or encode
semantic answer information.

Compiler validation SHALL include machine-checkable tests of this requirement.

### 13.5 Constraint-Derived Compilation

Topology and backend parameters SHALL be generated from admitted CCIR data and
globally fixed backend rules.

One unchanged compiler and one unchanged backend rule set SHALL operate across
the declared validation family.

Instance-specific hand tuning based on semantic outcomes SHALL NOT be used.

### 13.6 Reproducibility

Repeated compilation of the same canonical CCIR input under the same declared
backend specification SHALL produce equivalent execution artifacts.

All permitted variability capable of influencing the artifact SHALL be
represented in `Theta_backend` before compilation.

Artifact metadata MAY record that variability but SHALL NOT serve as an
additional compiler input.

### 13.7 Compiler Validation

Compiler validation SHALL succeed independently of semantic evaluation.

It SHALL verify at minimum:

- compiler dependency conformance;
- provenance completeness;
- topology reproducibility;
- parameter reproducibility;
- absence of answer-derived artifact information; and
- family-level use of unchanged compilation rules.

### 13.8 Semantic Validation

Semantic validation SHALL remain independent of backend compilation.

For every condition required by the declared validation profile, the decoded
backend result `d_X` SHALL equal the independently computed reference result
`e_X`.

A semantic mismatch SHALL cause semantic validation to fail.

### 13.9 Restricted Interface

Semantic correctness SHALL be determined only through the admitted interface
and fixed decoder.

Hidden backend state, diagnostic observables, intermediate trajectories, or
non-interface simulator information SHALL NOT be used to recover or improve
the semantic answer.

### 13.10 Backend Independence

A conforming backend SHALL remain independent of the source language that
produced the admitted CCIR.

Adding a new source language SHALL NOT require backend modification when that
source language lowers to CCIR already admitted by the backend.

Adding or replacing a backend SHALL NOT require modification of source-language
semantics or source-to-CCIR lowering.

### 13.11 RC Reference Backend

The RC reference backend SHALL additionally demonstrate:

- direct CCIR-driven compilation;
- constraint-derived network topology;
- fixed RC parameter-generation rules;
- complete RC artifact provenance;
- answer-independent artifact generation;
- restricted interface readout;
- validation across multiple structurally distinct parity instances; and
- independent post-execution semantic comparison.

The direct behavioral response realization MAY remain as a historical or
comparison baseline, but SHALL NOT constitute the final conforming RFC-0003 RC
reference backend.

### 13.12 Completion of the RFC-0003 Implementation Milestone

The RFC-0003 implementation milestone is complete when:

1. a canonical backend software interface implements
   `Compile_backend : CCIR -> ExecutionArtifact`;

2. the RC reference backend consumes CCIR directly;

3. the RC reference backend no longer relies on direct answer-conditioned
   behavioral response realization;

4. all RC topology and component settings are generated from CCIR and fixed
   backend rules;

5. artifact provenance is machine-checkable;

6. compiler validation and semantic validation are implemented as distinct
   validation paths;

7. answer-independence audits pass across the declared validation family;

8. the prescribed interface and fixed decoder reproduce the independent
   semantic reference results across that family;

9. the existing parity regression suite remains green or is superseded only by
   explicitly documented equivalent validation; and

10. the legacy parity-oriented execution path is retired from the canonical
    backend pipeline.

RFC-0003 completion does not establish polynomial-time solution of SAT,
general physical scalability, hardware feasibility, robustness to arbitrary
noise, or any complexity-theoretic claim not separately demonstrated.

Those questions remain outside the scope of this backend compilation contract.
