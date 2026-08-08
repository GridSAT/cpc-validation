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

Every generated artifact element SHALL be traceable to either admitted CCIR
data or a globally fixed backend rule.

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

Changing only the independently computed semantic answer SHALL NOT alter the
generated execution artifact.

Changing only the independent validation pipeline SHALL NOT alter the generated
execution artifact.

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

Equivalent CCIR programs SHALL generate reproducible execution artifacts,
subject only to documented canonicalization rules.

Repeated compilation of the same admitted CCIR program SHALL produce
equivalent execution artifacts.

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

Any permitted nondeterminism SHALL be explicitly represented in
`Theta_backend` or backend metadata and SHALL be reproducible from the recorded
artifact information.

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

## 11. Remaining Sections

1. Restricted Interface Principle

2. RC Reference Backend

3. Acceptance Criteria
