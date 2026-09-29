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

# Two-node composition and garbage-coherence audit

The bounded audit is complete. Node-wise reset does not yet provide a composable pure clean-response preparation. A globally dressed compute/use/uncompute reference succeeds in this finite model, with explicitly enlarged operator support; it is not a native local synthesis result.

## Domains and evidence

The full five-register numerical model uses N=2, Hilbert dimension 32 and 1024 density entries. This is a toy mechanism test, not a representative Shor unit-domain instance. The N=3 unit-input pair (1,1,1)/(1,2,2) is checked analytically and with sparse arithmetic, retaining complex phase. No full N=3 Liouvillian or general tree is constructed. Derivations and caps are in shor-two-node-derivation.md; source-bound evidence is in results/shor/native-research/two-node/report.json.

## Candidate outcomes

The following are rounded N=2 results at kappa*t=80 from uniform leaves and blank work. Arithmetic validity means final Z correctness only; it does not imply correct T, pure preparation, or readout.

| Candidate | Final arithmetic validity | Raw fidelity | Clean fidelity | Reduced-input trace distance to clean reference | Fourier L1 distance |
|---|---:|---:|---:|---:|---:|
| Output-only sum | 1 | 0.593750 | 0.562500 | 0.306186 | 0.375000 |
| Naive input/output reset | 0.823260 | 0.513656 | 0.412650 | 0.322749 | 0.447647 |
| Leaf-only drive | 0.921694 | 0.729781 | 0.495019 | 0.342803 | 0.460341 |
| Global raw reference | 1 | 1 | 0.562500 | 0.306186 | 0.375000 |
| Global clean reference | 1 | 0.562500 | 1 | <1e-14 | <1e-14 |

Output-only corrections preserve the raw valid sector. The new weighted-syndrome inequality gives attraction with penalty rate kappa/(n+1) and stationary operator dimension d^6; it does not establish an inherited kappa/2 spectral gap or pure-state preparation. Sequential channels and simultaneous generators differ on a nonblank full-domain probe: the phase-sensitive surviving coherence is exp(-i theta)/2 versus exp(-i theta)/3. Their blank uniform N=2 asymptotes agree. Reversing channel order can leave stale downstream outputs.

Naive downstream plus-driving of T damages upstream correlations. Removing that drive is insufficient: upstream updates still leave stale Z. Raw-target stationarity residuals are approximately 1.07165 and 0.50775, respectively. Small late-time residuals do not prove uniqueness; their gaps and mixing bounds remain unknown. Both failed candidates remain executable negative controls.

Dressing upstream terms through downstream arithmetic repairs raw preparation but expands some jumps to all five registers. Globally conjugated product reset has a separately justified unique target and kappa/2 gap by unitary similarity. Clean compute/use/uncompute additionally removes accessible intermediate garbage. These are global/circuit-mediated references, with arithmetic calls and actual support accounted separately from symbolic jump counts. Physical synthesis, reservoirs and controls remain unspecified. Known-target reset preparation does not preserve arbitrary unknown incoming states; the coherent unitary reference does.

## Garbage and environment

For the N=3 unit pair, intermediate products are 1 and 2 while final products are both 1. Tracing raw T removes their reduced-input coherence despite equal final response. Coherent cleanup before discard restores exp(-i theta)/2. Sequential reset instead exports distinguishable (h,F) syndrome records: later cleanup of accessible T cannot restore that coherence. Tests include theta=pi/3 and signed pi/2 and a wrong-phase control, not magnitude-only comparisons. Environment records are explicit for the branch/reset audit; arbitrary simultaneous-generator environment states are not reconstructed.

## Validation and preserved state

- New targeted tests: 40 passed in 1.42s.
- All Shor tests: 146 passed in 3.05s.
- Complete python -m pytest: 1156 passed in 93.42s.
- python run_spice.py: 4/4 passed; complete continuation table PASS.

Commands, logs and report are under results/shor/native-research/two-node/. Existing prototype and single-node source behavior is unchanged: all 286 prior source files match their checkpoint. New research files add bounded models, diagnostics, tests and a runner. HEAD and main remain b9f8820cef9d7ca3d77c7e68199ec869720cb8b9 on shor-rfc0010-prototype, with no staging, commits, pushes or FPGA actions.

The multiplication-tree candidate remains constraint-description-only. No scalable native dissipator, physical realization, matched-confidence advantage or robust RR claim is established.

## Exact next action after review

Before any general-tree implementation, derive a bounded-support, cleanup-aware two-node correction with explicit ancilla/control and environment records, or retain an explicitly clock/circuit-mediated classification. First test the same N=3 unit pair for equal-final-response environment overlap and complex phase preservation, then test target stationarity and attraction in the capped N=2 model. Compare to the existing global-clean positive control and preserved local negative controls. Do not repeat the completed single-node or two-node audit to recover context; use the immutable archive and resume note. Git reconstruction remains deferred pending explicit authorization.
