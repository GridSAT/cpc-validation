> **Historical prototype reference.**
> The body below preserves the finite prototype checkpoint, including its
> original validation inventory and claim boundaries. The committed
> `run_shor.py` remains a tiny finite demonstration; this document does not
> describe the complete current P3/P4 release or authorize historical
> execution. Historical counts are not current regression counts.
> See [current software scope](shor/README.md) and
> [N0 readiness](shor/n0-status.md).

# CPC-Shor RFC-0010 prototype

This is a simulated, finite-dimensional research prototype for **order finding**,
not a factorization-constraint solver and not a hardware implementation. Its
input is `(N,a,Q)`, with odd `N`, `1<a<N`, `gcd(a,N)=1`, and power-of-two `Q`.
The response is `a**x mod N`; equal responses define the period quotient.
Prime inputs remain legal order-finding instances and need not yield factors.

## Run and validate

From the repository, with the existing virtual environment activated:

```bash
python run_shor.py --N 15 --a 2 --Q 16 --seed 0
python run_shor.py --corpus examples/shor/tiny.json --output results/shor/collective.json
python run_shor.py --corpus examples/shor/tiny.json --mode circuit_clock --output results/shor/circuit.json
python run_shor.py --mode which_x --output results/shor/negative-control.json
python -m pytest tests/test_shor_*.py
python -m pytest
```

The runner never operates hardware. A zero exit status indicates structural and
finite-model conformance, not successful factoring; inspect the independent
`validation` and `decoded.reason` fields. Random sampling records the seed,
attempted shots and failed terminal heralds. Generated reports stay under the
repository's already ignored `results/` directory.
The input corpus lives under `examples/shor/` because the existing `benchmarks/`
discovery contract requires every JSON file there to be a parity benchmark.

## Existing architecture reused

`shor_ccir` introduces a typed `modular_response` payload and canonical CCIR
program. It does not change the semantics of existing Boolean/parity families.
The generator has CCIR constraint provenance and a registered backend rule.
The chain is:

```text
ShorInstance → CCIRProgram → ExecutionArtifact → PreparedExecution
 → density evolution → ObservableExecution → fixed decoder
 → independent semantic validation
```

The existing RFC-0010 `OpenSystemExecutionSpecification`, convergence and
readout records, requirement evidence, and fail-closed validator are reused.
The specification hash is frozen before execution/reference evaluation. The
generator hash binds explicit basis labels, the jump rule, rate and mode.
Preparation binds its initial-state rule, decoder and interface as well.
Hashes identify descriptions; they do not authenticate a physical experiment.

The compiler accepts no order, factors, expected peaks, or arbitrary calibration
advice. JSON input and CCIR metadata reject additional fields. Preparation
recompiles the canonical artifact to detect substituted labels or controls.
The independent reference module is outside the backend import graph and is
called only after observation and decoding. Tests monkeypatch the reference to
fail if called during compilation/execution/decoding. This tests the shipped
implementation's separation, not arbitrary malicious Python code.

## Three executable witnesses and one research description

**Collective graph witness:** explicitly enumerates the response graph for tiny
instances. Its basis has `2Q` vectors, `|clock,x,y_clock(x)>`, with initial blank
work label zero and final work label `a**x mod N`. The jump is
`sqrt(kappa) sum_x |1,x,f(x)><0,x,0|`. It preserves coherence across x.
It is labelled `semantic_reference_only`: enumeration and a collective nonlocal
jump are not a scalable physical compiler.

**Which-x negative control:** splits the collective jump into separate jumps for
each x. The environment learns x, so the terminal state is an incoherent mixture.
Its graph fidelity approaches `1/Q`; the Fourier distribution becomes uniform.
Its dynamics can satisfy terminal-subspace conformance while failing coherent
graph preparation. Therefore conformance is deliberately not a Shor-success
certificate. Chance factor recovery from random bins is not evidence of coherent
execution; inspect the response-class coherence metric and Fourier distribution.

**Dissipative circuit-clock baseline:** uses repeated-squaring constants and one
collective forward jump per controlled-multiplier stage. The work label is the
partial modular product. The clock explicitly retains circuit history; this is
not a native circuit-free result. The logical constant list is short, but the
shipped simulator still enumerates `Q` paths. It is not an efficient simulator or
a demonstrated local physical compilation of the jump operators.

**Native multiplication tree:** describes bit-selected constants, modular-product
constraints and balanced tree layers. Tests evaluate its arithmetic against the
response function. It has **no implemented native dissipator**, no proved mixing
bound and no established coherence-preserving local realization. Its status is
`constraint-description-only`; these unresolved research obligations are not
replaced by the collective witness.

The separate **orbit-spectrum witness O** builds the full permutation
`U|y>=|a*y mod N>` and `H=g(U+U†)` without receiving or computing the order.
It exposes the spectral measure seen from `|1>`. A reference-only diagnostic,
used after validation, reports `4g sin²(pi/r)` and its inverse as a characteristic
resolution time. This exposes the quadratic-in-order precision/time cost; it is
not a measured time-to-solution or an efficiency claim.

## Actual dynamics and certificates

The simulator constructs the sparse GKSL superoperator
`sum_j (J_j* ⊗ J_j - I ⊗ J_j†J_j/2 - (J_j†J_j)^T ⊗ I/2)` and applies
`expm_multiply(t L, vec(rho0))`. Density matrices are actually evolved. Closed-form
decay assumptions are not substituted for simulation. Tests independently compare
small cases with a dense matrix exponential, check trace/positivity/Hermiticity,
and compute small-instance superoperator nullities.

The basis is an isometric restriction to declared reachable states, not a
truncation of an unspecified infinite-dimensional device. Stabilization is zero
on this full admitted finite space; modeled leakage is zero by construction.
Physical leakage, precision and calibration remain unknown.

The terminal sector is the entire final-clock response-graph **subspace**.
It is not just the uniform graph vector. Every density operator supported there,
including coherences, is stationary. The initial uniform x state plus collective
jumps selects the coherent graph trajectory. The certificate checks terminal
silence, the pure-dark space and the fixed-operator space separately: the
superoperator is triangular, every nonterminal diagonal is strictly negative,
and exactly the terminal `Q²` columns vanish.

The penalty has clock weights `H_j=2**(steps-j)-1`. Its smallest positive value
is one and the computed adjoint inequality is `L†H <= -(kappa/2)H`.
Thus the declared rate is `gamma=kappa/2`, **not** a claimed Liouvillian gap.
Numerical certificates use absolute tolerance `1e-9` and are marked `exact=False`.
The report includes the resulting finite-time terminal-support upper bound.

## Observation and decoding

The admitted observation contains only Fourier bins. Measurement projects onto
the final clock, traces out work (retaining x coherences only for equal responses),
then applies the conventional inverse Fourier readout. Nonterminal probability
is counted as failed heralding; it is not silently postselected away.
This intentionally retains Fourier control as permitted by the first native
research boundary. No absolute-energy inference is made.

The fixed decoder forms exact continued-fraction denominators, combines sampled
denominators using LCM, verifies candidates with modular exponentiation and applies
the usual gcd factor extraction. It never reads density matrices or reference
orders. It can return insufficient evidence or a nonminimal order multiple;
independent repeated multiplication checks minimality separately. Candidate
storage is capped at 4096, and this tiny research decoder makes no polynomial
runtime claim. Small Q is pedagogical and need not meet Shor's usual `Q >= N²`
precision condition. No asymptotic success-probability claim follows.

Robust referenced-readout group RR is **not claimed**. Physical calibration,
drift/noise margins and a matched-confidence success theorem are absent. Adding
RR without evidence fails conformance. OS/DC/OV evidence applies only to the
declared finite model and is kept separate from semantic correctness.

## Resources and non-claims

Model dimension is capped at 512 (`2Q` or `(log2(Q)+1)Q`), density storage is
quadratic in dimension, and response/path enumeration is explicit. The orbit
matrix is capped at dimension 512. Fourier simulation is dense. Solver arithmetic
uses complex128; SciPy selects its internal exponential-action tolerance. Seeds,
times, solver identity and numerical certificate tolerances are recorded.

Reports measure compilation, preparation, evolution, readout, decoding and
validation wall times in the simulator. They do not equate wall time or simulated
time with physical runtime. Physical synthesis, control, calibration, energy,
precision, measurement costs, Liouvillian-gap scaling and matched-confidence TTS
remain unknown. The weighted-clock bound itself has initial penalty `2**steps-1`,
which must be included in any use of the bound.

The corpus includes orders 2, 3, 4, 6 and 12, an odd-order case, a minus-one
half-power, and unsuccessful factor extraction. The prototype establishes a
functional simulation/validation architecture. It does **not** establish a
polynomial-resource native CPC-Shor realization, a physical implementation, or
an advantage over gate-based Shor. No new normative RFC is introduced.

## Witness scopes and report compatibility

The mode-specific machine-readable witness scopes are shared by artifact
metadata, execution-specification metadata, evidence details, and the report's
`witness_scope` field:

| Mode | Witness scope |
|---|---|
| `collective` | `semantic_reference_only` |
| `which_x` | `which_x_decoherence_negative_control` |
| `circuit_clock` | `dissipative-circuit-baseline` |

The report field formerly named `native_tree` is now
`multiplication_tree_candidate`, with no legacy alias. Report consumers must use
the new name. Its status remains `constraint-description-only`, its coherence is
`unproved`, and its mixing bound is `unknown`. No scalable native dissipator,
physical realization, matched-confidence advantage, or robust RR claim is
established. Numerical trajectories, measurements, decoding, and pass/fail
criteria are unchanged. Witness-scope metadata changes the which-x specification
hash; evidence identifiers/methods and report metadata also change.

The original 42 test cases retain their bodies and parameterizations across
semantics, open-system, conformance and runner modules. Additional regression
checks lock admitted compiler/execution boundary signatures, reject semantic
advice keywords and variadic argument capture, and check witness/evidence report
identities. Signature checks guard API drift; they do not prove arbitrary payloads
safe and do not replace existing canonical-input or dependency checks.

## Requirement-specific evidence methods

Each evidence identity includes its requirement ID and the descriptive suffix
below. All evidence remains `exact=False` and scoped to `simulated-finite-model`.
Canonical declarations are labelled as such; they are not independent physical
proofs. The numerical certificate methods and their pass/fail tests are unchanged.

| Requirement | Evidence identity suffix | Method |
|---|---|---|
| DC-1 | `semantic-penalty` | `canonical-weighted-clock-penalty-declaration` |
| DC-2 | `positive-penalty-scale` | `numerical-minimum-positive-clock-weight` |
| DC-3 | `penalty-lyapunov` | `numerical-adjoint-penalty-inequality` |
| DC-4 | `convergence-rate` | `declared-kappa-half-rate-backed-by-adjoint-inequality` |
| DC-5 | `leakage-accounting` | `canonical-closed-reachable-basis-leakage-declaration` |
| DC-6 | `resource-accounting` | `canonical-finite-simulator-resource-record` |
| OS-1 | `generator-separation` | `canonical-zero-stabilization-and-problem-generator-declaration` |
| OS-2 | `protected-manifold` | `canonical-reachable-basis-manifold-identity` |
| OS-3 | `uniform-synthesis` | `canonical-instance-and-fixed-rule-recompilation` |
| OS-4 | `answer-independence` | `canonical-admitted-input-artifact-comparison` |
| OS-5 | `correction-family` | `canonical-forward-clock-jump-family-declaration` |
| OS-6 | `terminal-silence` | `numerical-terminal-superoperator-column-check` |
| OS-7 | `dark-vector-sector` | `numerical-jump-loss-kernel-check` |
| OS-8 | `fixed-operator-space` | `numerical-triangular-superoperator-kernel-certificate` |
| OV-1 | `admitted-observations` | `canonical-fourier-bin-interface-declaration` |
| OV-2 | `validation-separation` | `canonical-backend-validation-boundary-declaration` |
| OV-3 | `evidence-binding` | `canonical-preparation-and-specification-hash-binding` |
| OV-4 | `realization-status` | `canonical-simulated-realization-status-check` |
