> **Historical research checkpoint.**
> The body below preserves an earlier derivation or reported result. Its
> commands, test counts, HEAD references, execution instructions and next
> actions belong to that checkpoint; they are not current authorization or
> a claim that its complete executable workflow is published here.
> References to results/checkpoints are archival workspace references, not
> clean-clone dependencies supplied by this documentation release. No
> historical execution, evidence replacement or tolerance change is authorized.
> See [current software scope](shor/README.md) and
> [N0 readiness](shor/n0-status.md).

# Single-node checkpoint results

This bounded checkpoint completes the reset-based modular-node derivation and
full-channel experiment. No two-node or tree simulation has been attempted.
The mathematical setup is in [the derivation](shor-single-node-research.md).

## Reproduce

From the approved repository, with the existing environment:

```bash
. .venv/bin/activate
python -m pytest tests/test_shor_modular_node.py -q
python run_shor_node.py --output results/shor/native-research/node-report.json
```

The report binds actual jump matrices, the exact model, initial state, solver,
versions, source, derivation, times and state hashes. It contains numerical
residuals and independently computed small-matrix nullities/gaps; it is not an
RFC-0010 conformance claim. Model dimension is the full binary tensor space,
not a response-graph compression. N=3 includes binary input value 3 via the
explicit modular extension. These are node tests, not general-Q Shor runs.

## Candidate results

| Candidate | N | Hilbert dimension | Asymptotic graph fidelity | Final error to actual asymptote, trace norm (t=40) | Fixed-operator dimension |
|---|---:|---:|---:|---:|---|
| Output-only reset | 2 | 8 | 0.625 | 1.79e-9 | 16, numerically checked |
| Input + output reset | 2 | 8 | 1 | 1.15e-15 | 1, numerically checked |
| Output-only reset | 3 | 64 | 0.59375 | 1.79e-9 | 256, derived by tensor-reset similarity |
| Input + output reset | 3 | 64 | 1 | 6.14e-15 | 1, derived by tensor-reset similarity |

All rates are kappa=1; small floating-point fidelity values slightly above one
are reported without treating them as physical probabilities above one.
Numerical residual tolerance is 1e-9. No shot sampling or postselection is used.

**A: syndrome extraction/correction/reset.** The environment retains
z XOR f(u,v). Its full Kraus channel equals the output-reset asymptotic channel,
verified on all matrix units for N=2. Same-product coherences survive;
different-product coherences from blank work vanish. Pure graph preparation
fails. The reduced input state and its Fourier probabilities equal those of the
ideal graph for the specified initial preparation, but this is explicitly a
separate alternative-output result. It does not establish the requested pure
state or the correctness of a composed tree.

**B: output-only conjugated resets.** The entire graph subspace is silent, and
invalid sectors decay. That compatibility does not imply preparation from blank
work. The fidelity ceilings above are derived and observed, not test failures
hidden by a relaxed threshold. Next modification: drive the known input state
as well, which leads to B+.

**B+: input preparation plus output reset.** The desired pure uniform graph is
the unique attractive state on the declared full single-node domain. Actual
GKSL evolution reaches that target. This is a positive mathematical/finite-model
state-preparation result, not a scalable native-node result: input-driving terms
change other valid graph states and erase arbitrary incoming logical information.
Tests deliberately exhibit this disturbance. Consequently B+ cannot simply be
inserted as a nondisturbing correction on shared tree registers.

## Resource and claim audit

There are 3n system qubits and n/3n symbolic jumps for B/B+ respectively. Each jump
has norm sqrt(kappa) and may act on all 3n qubits. Independent reset spectra give
a separately justified gap kappa/2; the penalty decays at rate kappa. These bounds
are for the specified abstract generator at fixed rates, not for its physical
implementation. A reversible arithmetic map is not free: gate/depth/ancilla and
reservoir realization costs remain unimplemented and explicitly unknown. The
simulator enumerates dimension d^3 and stores d^6 density entries.

No scalable local synthesis, physical realization, matched-confidence advantage,
robust RR result or tree-composition theorem follows. The original collective,
which_x and circuit_clock scopes are unchanged. The existing multiplication tree
remains constraint-description-only. The orbit-spectrum resource diagnostic is
not used as a universal impossibility argument.

## Next executable research step

After reviewing this checkpoint, introduce exactly TWO linked modular nodes with
a shared intermediate register. Before coding, specify both local and globally
conjugated jump families and their preparation domains. Test whether node-wise
input-driving destroys the upstream correlation, whether upstream output changes
create stale downstream products, and whether environmental records distinguish
branches with the same final product. Compute noncommutators and fixed sectors at
the smallest admissible dimensions. Do not infer closure under composition from
single-node uniqueness. Investigate the next justified correction if it fails;
do not rename global arithmetic conjugation as native local synthesis.

The persistent resume and complete manifests are under
`results/shor/native-research/RESUME.md` and the checkpoint named in `LATEST.txt`.
Final integration logs and exact test counts accompany that resume note.

## Final integration gate

- Single-node tests: 38 passed in 0.97s.
- All Shor tests: 106 passed in 1.86s.
- Full suite: 1116 passed in 93.12s.
- SPICE: all 4 boundary cases and complete continuation table passed.
- All 281 original prototype working-source files remain byte-identical.
- Original finite-prototype archive SHA256 remains unchanged.
- HEAD/main remain at b9f8820cef9d7ca3d77c7e68199ec869720cb8b9; nothing staged,
  committed or pushed. No FPGA operations.
