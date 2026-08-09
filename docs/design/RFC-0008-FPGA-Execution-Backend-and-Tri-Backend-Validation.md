# RFC-0008: FPGA Execution Backend and Tri-Backend Validation

**Status:** Accepted  
**Category:** CPC Execution and Validation Architecture  
**Depends on:** RFC-0001, RFC-0002, RFC-0003, RFC-0004, RFC-0005, RFC-0006, RFC-0007

---

# 1. Abstract

RFC-0008 specifies the first hardware-oriented digital logic execution backend
for the CPC architecture.

The backend compiles canonical CCIR programs into a backend-specific
ExecutionArtifact representing a synthesizable logic-network realization,
prepares that artifact as deterministic Verilog, executes the prepared
representation through an external HDL execution engine, admits only the
declared result observation, and decodes that observation through a fixed
backend decoder.

The reference implementation uses Icarus Verilog for external HDL execution.

RFC-0008 also extends executable backend validation from the two-backend
RC/digital architecture of RFC-0005 and RFC-0006 to a three-backend validation
architecture consisting of:

- the RC Reference Backend;
- the deterministic Digital Backend; and
- the FPGA Backend.

All three backends consume the same canonical CCIR program but compile,
prepare, execute, observe, and decode through distinct backend-specific
realizations.

Backend agreement is evaluated only after all three executions complete.

Independent canonical CCIR continuation semantics are then evaluated outside
all backend dependency graphs.

Agreement among the three backends is not treated as sufficient evidence of
correctness. Each decoded backend result must also agree independently with
canonical CCIR semantics.

RFC-0008 further defines corpus-scale tri-backend validation and qualification
of the FPGA backend through the existing RFC-0007 backend qualification
manifest architecture.

---

# 2. Motivation

RFC-0003 introduced backend independence through the general compilation
contract

    Compile_backend : CCIR -> ExecutionArtifact

and required machine-checkable provenance for every generated artifact
element.

RFC-0004 specified the backend execution lifecycle

    ExecutionArtifact
        -> PreparedExecution
        -> ObservableExecution
        -> DecodedResult

and separated compilation, preparation, execution, observation, and decoding.

RFC-0005 demonstrated heterogeneous execution by realizing one canonical CCIR
program through two distinct backends:

- an RC/ngspice execution path; and
- a deterministic digital/Python execution path.

RFC-0006 extended this comparison from individual cases to reproducible
benchmark-corpus validation.

RFC-0007 introduced backend qualification manifests.

Those RFCs establish backend independence architecturally and operationally,
but the two current reference backends remain either analog-simulation based
or software-interpreter based.

RFC-0008 adds a third realization whose prepared representation is a hardware
description suitable for logic synthesis and whose reference execution path is
an independent HDL simulator.

This creates three materially distinct execution technologies behind one
canonical representation:

    CCIR
      |
      +--> RC topology      -> ngspice
      |
      +--> digital program  -> Python interpreter
      |
      +--> logic network    -> Verilog -> Icarus Verilog

The objective is not to claim physical FPGA deployment from HDL simulation
alone.

The objective is to establish a conforming hardware-oriented backend whose
artifact, preparation, execution, observation, decoding, validation, and
qualification paths satisfy the existing CPC backend contracts.

---

# 3. Scope

RFC-0008 specifies:

- the `fpga/1` backend identity;
- FPGA backend capabilities;
- FPGA ExecutionArtifact structure;
- canonical FPGA compilation from parity CCIR;
- provenance requirements;
- deterministic Verilog preparation;
- structural existential-completion realization;
- admitted boundary values;
- external HDL execution;
- admitted FPGA observations;
- fixed FPGA decoding;
- the FPGA execution-result wrapper;
- tri-backend semantic validation;
- tri-backend benchmark-corpus validation;
- tri-backend machine-readable reports;
- FPGA backend qualification;
- execution-engine identity and version recording;
- failure semantics;
- reproducibility requirements; and
- acceptance criteria.

RFC-0008 does not specify:

- placement or routing for a physical FPGA device;
- synthesis-tool optimization;
- timing closure;
- LUT or routing utilization guarantees;
- hardware resource bounds;
- FPGA-board I/O protocols;
- clock-domain architecture;
- asynchronous physical realization;
- high-performance FPGA implementation;
- polynomial resource bounds;
- superiority over conventional SAT solvers;
- general computational-complexity claims; or
- physical C-parity hardware realization.

Those are future backend-engineering questions.

---

# 4. Architectural Position

RFC-0008 extends, but does not replace, the earlier CPC RFCs.

The architecture is:

    Source Representation
            |
            v
          CCIR
            |
            +---------------------------------------------+
            |                     |                       |
            v                     v                       v
       Compile_RC           Compile_Digital          Compile_FPGA
            |                     |                       |
            v                     v                       v
       RC Artifact          Digital Artifact          FPGA Artifact
            |                     |                       |
            v                     v                       v
      Prepare_RC           Prepare_Digital          Prepare_FPGA
            |                     |                       |
            v                     v                       v
    PreparedExecution    PreparedExecution        PreparedExecution
            |                     |                       |
            v                     v                       v
        ngspice          Python interpreter      iverilog / vvp
            |                     |                       |
            v                     v                       v
   ObservableExecution   ObservableExecution     ObservableExecution
            |                     |                       |
            v                     v                       v
       Decode_RC          Decode_Digital           Decode_FPGA
            |                     |                       |
            +---------------------+-----------------------+
                                  |
                                  v
                         Backend Comparison
                                  |
                                  v
                      Independent CCIR Semantics

The independent semantic reference is not an execution backend.

It is excluded from the compilation, preparation, execution, observation, and
decoding dependency graphs of all three backends.

---

# 5. Backend Identity

The reference FPGA backend identity is:

    backend_id      = "fpga"
    backend_version = "1"

The canonical shorthand is:

    fpga/1

The backend shall declare the parity constraint family.

The current reference backend declares:

    constraint_families:
        parity

    interface_features:
        boundary-control
        restricted-readout

    execution_features:
        synthesizable-logic

    artifact_features:
        provenance
        logic-network-topology
        hdl-preparable

The current fixed parameters are:

    logic_domain   = bit
    representation = synthesizable-logic-network-v1
    hdl_target     = verilog-2001

---

# 6. FPGA Compilation Contract

The FPGA backend conforms to the RFC-0003 contract

    Compile_fpga : CCIR -> ExecutionArtifact

Compilation shall depend only on:

    D(Compile_fpga) = { CCIR, Theta_fpga }

where `Theta_fpga` denotes globally fixed FPGA backend rules and parameters.

Compilation shall not consume:

- boundary assignments;
- expected decoded results;
- independent semantic-reference results;
- benchmark labels encoding expected answers;
- execution-engine output;
- validation records; or
- qualification results.

The FPGA compiler therefore constructs a reusable artifact before any
particular boundary execution is selected.

---

# 7. FPGA ExecutionArtifact

The FPGA ExecutionArtifact is represented through the common RFC-0003
ExecutionArtifact structure

    A_fpga = (T_fpga, P_fpga, I_fpga, M_fpga, Pi_fpga)

where:

- `T_fpga` is the hardware-oriented topology;
- `P_fpga` contains fixed backend parameters;
- `I_fpga` defines the admitted boundary and readout interface;
- `M_fpga` contains backend metadata; and
- `Pi_fpga` records provenance.

The reference topology contains elements corresponding to:

- variable signals;
- boundary ports;
- parity networks;
- constraint-match logic;
- existential reduction;
- the result signal; and
- the admitted readout.

The FPGA artifact is intentionally distinct from the Digital Backend artifact.

The FPGA backend shall not represent its compiled constraints as digital
interpreter instructions.

---

# 8. FPGA Backend Rules

The reference `fpga/1` backend defines the following fixed backend rules:

    fpga.variable-signal
    fpga.boundary-port
    fpga.parity-network
    fpga.constraint-match
    fpga.existential-reduction
    fpga.result-signal
    fpga.readout

Every generated topology element shall be traceable to:

- one or more admitted CCIR origins;
- one or more fixed FPGA backend rules; or
- both.

No topology element may exist without admitted provenance.

---

# 9. Canonical Variable Representation

Each admitted CCIR variable participating in a parity constraint is represented
by a hardware-oriented variable signal.

Boundary variables additionally receive declared boundary-port elements.

Variable-signal identity is deterministic.

Constraint-variable ordering shall already be canonical at the CCIR boundary
as required by RFC-0002.

The FPGA backend shall not derive topology identity from arbitrary source-order
variation.

---

# 10. Parity-Network Realization

For every parity constraint

    x_i1 XOR x_i2 XOR ... XOR x_ik = p

the FPGA artifact contains a parity-network element associated with the
corresponding CCIR constraint.

A corresponding constraint-match element represents equality between the
computed parity value and the admitted parity bit.

The reference implementation emits these structures as combinational XOR and
comparison logic during Verilog preparation.

---

# 11. Existential Continuation Semantics

CPC continuation semantics ask whether a supplied boundary assignment admits at
least one assignment of the remaining internal variables satisfying all
constraints.

Let:

- `B` denote the boundary variables;
- `I` denote the internal variables;
- `b` denote one supplied boundary assignment; and
- `C(b,i)` denote satisfaction of all constraints under complete assignment
  `(b,i)`.

The continuation response is

    R(b) = OR_{i in {0,1}^{|I|}} C(b,i)

The reference FPGA backend realizes this existential operation structurally.

For each internal assignment, the prepared hardware representation contains a
parallel completion branch.

Each branch computes all parity constraints under:

- the admitted boundary inputs; and
- one fixed internal completion.

The branch result is the conjunction of all constraint-match signals.

The final result is the disjunction of all completion-branch results.

---

# 12. Structural Expansion Boundary

The reference FPGA backend uses explicit structural expansion rather than
performing semantic elimination during preparation.

For `k` internal Boolean variables, preparation emits up to

    2^k

parallel completion branches.

This is a reference-realization choice.

RFC-0008 does not claim that this representation is asymptotically efficient.

It is selected because the dependency boundary is transparent:

- preparation instantiates the finite hardware structure;
- execution evaluates the structure;
- no independent semantic evaluator participates in preparation or execution.

Future optimized FPGA backends may replace explicit completion expansion with
semantics-preserving logic minimization, Gaussian elimination, synthesis
optimization, or other fixed backend transformations.

Such optimizations must preserve RFC-0003 dependency and provenance
requirements.

---

# 13. FPGA Preparation

FPGA preparation has the form

    Prepare_fpga(
        CCIR,
        ExecutionArtifact,
        BoundaryValues
    )
        -> PreparedExecution

Boundary values are admitted execution inputs.

They are not expected answers.

The prepared representation shall be deterministic for fixed:

- CCIR;
- FPGA artifact;
- boundary assignment; and
- fixed backend preparation rules.

The reference prepared payload is Verilog source.

---

# 14. PreparedExecution Contract

FPGA preparation returns the common RFC-0004 `PreparedExecution` type.

It shall not introduce a backend-specific parallel lifecycle type.

The prepared execution records:

- backend identity;
- backend version;
- the Verilog payload;
- the admitted readout interface;
- the fixed decoder specification;
- artifact provenance; and
- preparation metadata.

The reference preparation identifier is:

    fpga.verilog.v1

---

# 15. Verilog Representation

The reference FPGA prepared representation targets:

    Verilog-2001

The prepared module is deterministic.

The current module identity is:

    cpc_fpga_execution

The module exposes the admitted result signal:

    result

Boundary values are materialized as fixed execution inputs for one prepared
execution.

Internal assignments are materialized as structural constants inside the
parallel completion branches.

---

# 16. Observation Harness

A prepared FPGA execution must provide an admitted execution observation.

The reference prepared module emits exactly one record of the form

    CPC_RESULT=0

or

    CPC_RESULT=1

after combinational stabilization.

The observation harness exposes the already-computed `result` signal.

It shall not:

- compute continuation semantics independently;
- access expected answers;
- invoke the CCIR semantic reference;
- modify the result signal; or
- perform decoding.

The observation harness is part of preparation for the external execution
engine.

---

# 17. FPGA Execution

FPGA execution has the form

    Execute_fpga(
        PreparedExecution
    )
        -> ObservableExecution

Execution consumes only `PreparedExecution`.

It shall not receive:

- CCIR;
- ExecutionArtifact;
- source benchmark representation;
- boundary assignments separately from the prepared representation;
- expected results;
- semantic-reference results; or
- qualification records.

This preserves the RFC-0004 execution boundary.

---

# 18. External HDL Engine

The current reference execution engine uses:

    iverilog
    vvp

The canonical execution-engine identity is:

    iverilog/vvp

The current execution identifier is:

    fpga.icarus-verilog.v1

The installed Icarus Verilog version is discovered from the actual execution
environment.

It is not fixed by the FPGA backend specification.

---

# 19. HDL Compilation

The execution stage writes the prepared Verilog payload into an isolated
temporary execution directory.

It invokes the external HDL compiler to produce the executable simulation
representation.

Compilation failure is a backend execution failure.

Compiler stdout or stderr shall not be interpreted as a semantic result.

---

# 20. HDL Simulation

After successful HDL compilation, the reference backend invokes `vvp`.

The simulator output is treated as substrate observation data.

The execution stage shall not derive a semantic result by directly examining
CCIR or by running the independent semantic evaluator.

Only the admitted observation record may enter the FPGA decoder.

---

# 21. ObservableExecution

The FPGA execution stage returns the common `ObservableExecution` type.

The admitted observation is:

    result_bit in {0,1}

The observable metadata records at least:

    execution_engine
    execution_engine_version
    execution_id

For the current reference realization:

    execution_engine = iverilog/vvp
    execution_id     = fpga.icarus-verilog.v1

The execution-engine version is environment-derived.

---

# 22. Observation Failure Semantics

The reference execution stage requires exactly one valid observation.

The following are failures:

- no `CPC_RESULT` observation;
- more than one `CPC_RESULT` observation;
- `CPC_RESULT=x`;
- `CPC_RESULT=z`;
- any non-Boolean result value;
- malformed result syntax;
- HDL compilation failure;
- HDL execution failure; or
- inability to determine the execution-engine version.

These conditions shall not be silently coerced into Boolean results.

---

# 23. FPGA Decoder

The FPGA decoder has the form

    Decode_fpga(
        ObservableExecution,
        DecoderSpecification
    )
        -> {0,1}

The current fixed decoder admits only the declared result signal.

The decoder requires:

    result_bit in {0,1}

Decoding performs no execution and no independent semantic evaluation.

---

# 24. FPGA Execution Result

RFC-0008 defines a composed FPGA execution result analogous to the existing RC
and Digital execution-result wrappers.

The result retains:

    PreparedExecution
    ObservableExecution
    DecodedResult

The current wrapper is conceptually:

    FPGAExecutionResult = (
        prepared,
        observable,
        decoded
    )

The wrapper performs no semantic-reference evaluation.

Its purpose is to preserve the complete execution record for downstream
validation and reporting.

---

# 25. Tri-Backend Validation

RFC-0008 defines tri-backend validation over:

- RC;
- Digital; and
- FPGA.

For canonical CCIR program `C` and boundary assignment `b`, each backend is
compiled and executed independently:

    r_RC      = Run_RC(C, b)
    r_Digital = Run_Digital(C, b)
    r_FPGA    = Run_FPGA(C, b)

Only after all three decoded results exist is independent canonical semantics
evaluated:

    r_ref = Reference(C, b)

The reference evaluator is not a backend.

---

# 26. Tri-Backend Agreement

Tri-backend agreement is:

    r_RC = r_Digital = r_FPGA

For one validation case:

    backend_agreement =
        (r_RC == r_Digital == r_FPGA)

Backend agreement is a cross-implementation consistency condition.

It shall not be interpreted as proof of semantic correctness.

Three implementations can in principle agree on the same incorrect result.

---

# 27. Independent Semantic Match

Each backend therefore receives its own semantic-match condition:

    rc_semantic_match =
        (r_RC == r_ref)

    digital_semantic_match =
        (r_Digital == r_ref)

    fpga_semantic_match =
        (r_FPGA == r_ref)

Overall validation passes only if:

    backend_agreement
    AND rc_semantic_match
    AND digital_semantic_match
    AND fpga_semantic_match

Agreement and correctness remain separate evidence fields.

---

# 28. Reference Isolation

The independent semantic evaluator shall execute only after all three backend
executions and decodings have completed.

The evaluator shall not participate in:

- RC compilation;
- Digital compilation;
- FPGA compilation;
- RC preparation;
- Digital preparation;
- FPGA preparation;
- RC execution;
- Digital execution;
- FPGA execution;
- RC observation;
- Digital observation;
- FPGA observation; or
- any backend decoder.

This requirement preserves answer independence.

---

# 29. Execution-Record Retention

The tri-backend validation result shall retain the composed execution result of
each backend.

Downstream consumers must be able to inspect:

- prepared backend identity;
- prepared backend version;
- admitted observations;
- execution metadata;
- provenance;
- decoded result.

The reporting layer shall derive backend and execution-engine identity from
these execution records.

It shall not hard-code the identities of the backends being reported.

---

# 30. Tri-Backend Benchmark Validation

RFC-0008 extends corpus-scale validation to all three current reference
backends.

For every admitted benchmark:

1. load the benchmark;
2. lower it canonically to CCIR;
3. enumerate all Boolean boundary assignments deterministically;
4. execute tri-backend validation for every boundary case;
5. retain separate backend-agreement and semantic-match conditions; and
6. aggregate the resulting evidence.

The accepted RFC-0006 two-backend report remains unchanged.

RFC-0008 produces separate tri-backend evidence.

---

# 31. Benchmark Discovery

RFC-0008 reuses RFC-0006 deterministic benchmark discovery.

Benchmark files are discovered from explicit JSON paths or recursively searched
directories.

Duplicate paths are removed.

The final path sequence is deterministic and lexicographically ordered by
normalized path representation.

An empty discovered corpus is an error.

---

# 32. Boundary Enumeration

Boundary assignments are enumerated through the canonical RFC-0006 boundary
enumeration procedure.

For `n` boundary variables, all

    2^n

Boolean assignments are executed.

Enumeration order shall be deterministic.

No random sampling substitutes for exhaustive admitted boundary enumeration in
the reference RFC-0008 corpus validator.

---

# 33. Tri-Backend Case Record

For each benchmark-boundary pair, the reference machine-readable record
contains at least:

    benchmark
    benchmark_path
    boundary

    rc_backend
    rc_execution_engine
    rc_decoded

    digital_backend
    digital_execution_engine
    digital_decoded

    fpga_backend
    fpga_execution_engine
    fpga_decoded

    reference_result

    backend_agreement
    rc_semantic_match
    digital_semantic_match
    fpga_semantic_match
    overall_pass

Backend identities and execution engines shall be derived from the retained
execution records.

---

# 34. CSV Report

The tri-backend corpus validator produces deterministic CSV case evidence.

Boolean validation fields are encoded machine-readably.

The reference report path is:

    results/tri_backend_validation.csv

The CSV report is distinct from the RFC-0006 report:

    results/cross_backend_validation.csv

No RFC-0006 evidence file is overwritten.

---

# 35. JSON Summary

The tri-backend aggregate report uses schema:

    cpc.tri-backend-summary.v1

The reference summary path is:

    results/tri_backend_summary.json

The summary contains at least:

    schema
    benchmark_count
    benchmarks
    boundary_case_count

    backend_agreement_passed
    backend_agreement_failed

    rc_semantic_passed
    rc_semantic_failed

    digital_semantic_passed
    digital_semantic_failed

    fpga_semantic_passed
    fpga_semantic_failed

    overall_passed
    overall_failed
    overall_pass

The JSON representation shall be deterministic.

---

# 36. Non-Vacuous Validation

An empty result set shall not produce a passing aggregate report.

The aggregate condition is:

    overall_pass =
        boundary_case_count > 0
        AND overall_passed == boundary_case_count

This prevents vacuous qualification from empty evidence.

---

# 37. Tri-Backend CLI

The reference CLI is:

    validate_tri_backend_benchmarks.py

It accepts benchmark JSON files or benchmark directories.

It shall support explicit output paths for:

- CSV case evidence; and
- JSON aggregate evidence.

The CLI shall return success only when every executed case satisfies the
overall tri-backend validation condition.

---

# 38. FPGA Qualification

RFC-0008 qualifies the FPGA backend using the existing RFC-0007 qualification
manifest schema:

    cpc.backend-qualification.v1

A new manifest schema is not required.

The FPGA manifest identifies:

    backend = fpga/1

and records:

- FPGA backend capabilities;
- fixed FPGA backend parameters;
- backend rules;
- preparation identity;
- execution identity;
- execution engine;
- actual execution-engine version;
- conformance claims;
- corpus evidence;
- deterministic manifest hash.

---

# 39. FPGA Qualification Evidence

The FPGA qualification corpus shall use:

    cpc.tri-backend-summary.v1

The reference qualification procedure requires:

    benchmark_count > 0

    boundary_case_count > 0

    fpga_semantic_passed
        == boundary_case_count

    fpga_semantic_failed
        == 0

    overall_passed
        == boundary_case_count

    overall_failed
        == 0

    overall_pass
        == true

This ensures the FPGA backend itself matched independent semantics on every
admitted case.

---

# 40. FPGA Qualification Profile

The reference FPGA qualification execution profile records:

    preparation_id =
        fpga.verilog.v1

    execution_id =
        fpga.icarus-verilog.v1

    execution_engine =
        iverilog/vvp

    execution_engine_version =
        value observed from the actual execution environment

The engine version is not fixed by the backend specification.

---

# 41. FPGA Qualification Manifest

The reference persistent manifest path is:

    results/qualification/fpga.backend-qualification.json

It shall use:

    schema =
        cpc.backend-qualification.v1

The manifest hash shall be derived deterministically from canonical
qualification content according to RFC-0007.

The FPGA manifest shall be distinct from the RC and Digital manifests.

---

# 42. Relationship to RFC-0007

RFC-0008 does not change the RFC-0007 qualification-manifest model.

The existing RC and Digital qualification workflow remains valid.

RFC-0008 demonstrates that the RFC-0007 architecture admits a new backend with:

- a different compiled artifact;
- a different prepared representation;
- a different execution engine;
- a different execution identifier; and
- a different corpus evidence schema.

This is an executable demonstration that backend qualification is itself
backend-neutral.

---

# 43. Reproducibility

For fixed:

- repository revision;
- benchmark corpus;
- CCIR lowering rules;
- FPGA backend specification;
- boundary enumeration;
- FPGA preparation rules;
- external HDL engine version; and
- report schema,

the reference workflow shall produce deterministic:

- FPGA artifacts;
- prepared Verilog;
- decoded results;
- per-case validation records;
- aggregate validation summaries; and
- qualification manifests.

Environment-derived execution-engine version identity is intentionally part of
the qualification evidence.

---

# 44. Failure Semantics

A tri-backend validation case fails if any of the following occurs:

- backend compilation failure;
- preparation failure;
- execution failure;
- observation failure;
- decoding failure;
- disagreement among decoded backend results;
- RC semantic mismatch;
- Digital semantic mismatch;
- FPGA semantic mismatch; or
- independent semantic-reference failure.

Corpus validation fails if any admitted case fails.

FPGA qualification fails if:

- the tri-backend report schema is wrong;
- the corpus is empty;
- any FPGA semantic case fails;
- any aggregate tri-backend case fails; or
- the overall tri-backend result is not PASS.

---

# 45. Evidence Boundary

Passing RFC-0008 validation establishes finite executable evidence for the
specific:

- repository revision;
- benchmark corpus;
- boundary assignments;
- backend implementations;
- execution engines; and
- execution-engine versions actually exercised.

It does not prove:

- universal semantic equivalence for all possible CCIR programs;
- correctness of every future FPGA compiler;
- correctness of every HDL simulator;
- equivalence of all FPGA devices;
- physical FPGA timing correctness;
- resource efficiency;
- asymptotic efficiency; or
- any complexity-class separation.

This distinction is mandatory.

---

# 46. Hardware Interpretation

The `fpga/1` backend is hardware-oriented because its prepared representation
is an HDL realization of a combinational logic network.

The reference execution engine is an HDL simulator.

Therefore RFC-0008 establishes executable HDL-backend realization, not
deployment onto a physical FPGA device.

Physical-device realization would additionally require, among other things:

- synthesis;
- technology mapping;
- placement;
- routing;
- bitstream generation;
- device programming;
- physical I/O;
- timing validation; and
- device-level observation.

Those steps may be standardized by future RFCs.

---

# 47. Security and Trust Considerations

The external HDL toolchain is part of the execution environment.

A compromised or incorrect HDL compiler or simulator could produce incorrect
observations.

RFC-0008 does not treat tool identity alone as proof of tool correctness.

Cross-backend agreement and independent semantic matching reduce the risk of
undetected backend-specific implementation errors but do not eliminate common
mode failures.

Generated HDL shall be treated as execution input to an external toolchain.

Implementations should isolate temporary execution files and avoid executing
untrusted shell fragments derived from benchmark content.

---

# 48. Future Extensions

Future RFCs may define:

- Yosys synthesis;
- physical FPGA-board execution;
- vendor FPGA toolchains;
- bitstream provenance;
- FPGA timing reports;
- resource-utilization evidence;
- optimized GF(2) logic synthesis;
- hardware parallelization policies;
- alternative HDLs;
- formal HDL equivalence checking;
- gate-level simulation;
- ASIC backends;
- graph-processing backends;
- C-parity hardware backends; and
- more general n-backend validation.

Such extensions must preserve:

- canonical CCIR input;
- answer-independent compilation;
- complete provenance;
- separation of preparation, execution, observation, and decoding;
- independent semantic validation; and
- explicit evidence boundaries.

---

# 49. Normative Conformance Requirements

A conforming RFC-0008 implementation shall satisfy the following requirements.

## FPGA-1 — Distinct Backend Identity

The hardware-oriented backend shall use a distinct backend identity and shall
not masquerade as the deterministic Digital Backend.

## FPGA-2 — Canonical CCIR Input

FPGA compilation shall consume canonical CCIR.

## FPGA-3 — Answer-Independent Compilation

FPGA compilation shall not consume boundary assignments, expected answers, or
semantic-reference results.

## FPGA-4 — Provenance

Every required FPGA artifact element shall have admitted provenance according
to RFC-0003.

## FPGA-5 — Hardware-Oriented Artifact

The FPGA ExecutionArtifact shall represent a logic-network realization rather
than a Digital Backend instruction program.

## FPGA-6 — Common PreparedExecution Contract

FPGA preparation shall return the common `PreparedExecution` lifecycle type.

## FPGA-7 — Structural Existential Realization

The reference FPGA v1 implementation shall represent existential continuation
through structural completion branches and final OR reduction.

## FPGA-8 — External HDL Execution

The reference FPGA execution path shall execute prepared HDL through an
external HDL execution engine.

## FPGA-9 — Execution Isolation

FPGA execution shall consume only `PreparedExecution`.

## FPGA-10 — Restricted Observation

Only the admitted result observation shall enter the FPGA decoder.

## FPGA-11 — Fixed Decoder

The FPGA decoder shall convert only admitted Boolean result observations into
decoded results.

## FPGA-12 — Execution Record

The composed FPGA lifecycle shall retain prepared, observable, and decoded
execution state.

## TB-1 — Three Independent Backends

Tri-backend validation shall execute RC, Digital, and FPGA backend lifecycles.

## TB-2 — Post-Execution Reference

Independent semantic evaluation shall occur only after all three backend
executions complete.

## TB-3 — Agreement Separation

Backend agreement shall remain separate from semantic correctness.

## TB-4 — Independent Semantic Match

RC, Digital, and FPGA results shall each be compared separately against
canonical CCIR semantics.

## TB-5 — Overall Validation

Overall success shall require backend agreement and all three independent
semantic matches.

## TB-6 — Execution-Derived Reporting Identity

Backend and execution-engine identities in validation evidence shall be derived
from execution records rather than hard-coded by the reporting layer.

## TB-7 — Deterministic Corpus Validation

Benchmark discovery, boundary enumeration, case execution, and reporting shall
be deterministic.

## TB-8 — Non-Vacuous Aggregate Success

An empty validation corpus shall not pass.

## TB-9 — Separate RFC-0008 Evidence

Tri-backend evidence shall not overwrite or reinterpret accepted RFC-0006
two-backend evidence.

## QF-1 — Existing Qualification Schema

FPGA qualification shall use `cpc.backend-qualification.v1`.

## QF-2 — Actual Engine Identity

FPGA qualification shall record the actual external execution-engine version.

## QF-3 — FPGA-Specific Semantic Gate

FPGA qualification shall require every admitted FPGA semantic case to pass.

## QF-4 — Aggregate Validation Gate

FPGA qualification shall require the complete tri-backend corpus to pass.

## QF-5 — Deterministic Manifest

The FPGA qualification manifest shall have deterministic canonical content and
manifest hash.

---

# 50. Reference Implementation

The current reference implementation consists of:

    src/backends/fpga_ccir.py
    src/backends/fpga_prepare.py
    src/backends/fpga_execute.py
    src/backends/fpga_decode.py
    src/backends/fpga_run.py

    src/tri_backend_validation.py
    src/tri_backend_benchmarks.py

    validate_tri_backend_benchmarks.py

    src/backend_qualification_profiles.py
    qualify_fpga_backend.py

The relevant tests include:

    tests/test_fpga_ccir.py
    tests/test_fpga_prepare.py
    tests/test_fpga_execute.py
    tests/test_fpga_decode.py
    tests/test_tri_backend_validation.py
    tests/test_tri_backend_benchmarks.py
    tests/test_tri_backend_benchmarks_cli.py
    tests/test_backend_qualification_profiles.py
    tests/test_qualify_fpga_backend_cli.py

The generic RFC-0003, RFC-0004, RFC-0005, RFC-0006, and RFC-0007 regression
suites remain applicable.

---

# 51. Current Reference Evidence

At the time RFC-0008 entered acceptance review, the permanent tri-backend
corpus contained:

    16 benchmarks
    64 boundary cases

The reference execution produced:

    Backend agreement:       64/64 PASS
    RC semantic match:       64/64 PASS
    Digital semantic match:  64/64 PASS
    FPGA semantic match:     64/64 PASS
    Overall:                 PASS

The FPGA execution environment reported:

    backend:                 fpga/1
    execution engine:        iverilog/vvp
    execution-engine version:
        12.0 (stable) ()

The generated FPGA qualification manifest reported:

    qualification: PASS

and used:

    schema:
        cpc.backend-qualification.v1

    corpus report schema:
        cpc.tri-backend-summary.v1

These values are finite reference evidence, not universal claims.

---

# 52. Acceptance Criteria

RFC-0008 is accepted when the reference implementation demonstrates:

- a distinct `fpga/1` backend;
- canonical CCIR-to-FPGA compilation;
- complete FPGA artifact provenance;
- deterministic hardware-oriented FPGA topology;
- deterministic Verilog preparation;
- common `PreparedExecution` lifecycle integration;
- external Icarus HDL execution;
- admitted result observation;
- fixed FPGA decoding;
- retained FPGA execution records;
- tri-backend RC/Digital/FPGA validation;
- post-execution independent semantic evaluation;
- separate backend-agreement and semantic-match conditions;
- exhaustive deterministic corpus validation;
- deterministic CSV tri-backend evidence;
- deterministic JSON tri-backend summary;
- execution-derived report identities;
- non-vacuous corpus success;
- FPGA qualification using the RFC-0007 manifest schema;
- actual execution-engine version recording;
- FPGA-specific semantic qualification gating;
- deterministic FPGA qualification manifest hashing;
- RFC-0008 conformance tests;
- complete repository regression without failure; and
- persistent acceptance evidence for the admitted benchmark corpus.

Acceptance applies only to the finite implementations, benchmark corpus,
execution environment, and evidence actually exercised.

---
