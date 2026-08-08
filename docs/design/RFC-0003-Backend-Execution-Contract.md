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

## 6. Remaining Sections

1. Answer Independence

2. Physical Compilation Discipline

3. Compiler Validation

4. Semantic Validation

5. Backend Independence

6. Restricted Interface Principle

7. RC Reference Backend

8. Acceptance Criteria
