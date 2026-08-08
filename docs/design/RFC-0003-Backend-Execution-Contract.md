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

## 4. Remaining Sections

1. Execution Artifact

2. Compiler Dependency Principle

3. Answer Independence

4. Physical Compilation Discipline

5. Compiler Validation

6. Semantic Validation

7. Backend Independence

8. Restricted Interface Principle

9. RC Reference Backend

10. Acceptance Criteria
