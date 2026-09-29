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

# Two-node composition and garbage-coherence derivation

Pre-implementation derivation. This is a bounded two-node study, not a general
tree implementation or a claim of native local physical synthesis. Preserve the
single-node candidates and their distinct contracts.

## Registers, domains, rates, observations

Order registers U,V,W,T,Z; each has n=ceil(log2 N) qubits, d=2^n labels.
The FULL operator domain has Hilbert dimension d^5 and density size d^10.
Define h(u,v)=((u mod N)(v mod N)) mod N and F=h(u,v)(w mod N) mod N.
Total reversible XOR maps are A1: T ^= h(U,V), A2: Z ^= (T mod N)(W mod N) mod N.
They are self-inverse permutations on all binary labels, including labels >=N.
Operators act right to left. V_raw=A2 A1; V_clean=A1 A2 A1.
The preparation domain is original input density on U,V,W with T=Z=0, separately
from the full operator domain. Known-target generator runs use independent plus
states on original leaves. Coherent-reference channels also admit arbitrary
complex input amplitudes alpha_b, including the mandatory two-branch test.

H=0. Every elementary reset is norm sqrt(kappa), kappa>0: q^0=|0><1|,
q^+=|+><-|. A superscript identifies register/bit; identities on other registers
are implicit. All jump lists below are explicit through reversible conjugation.
Baths for different listed jumps are independent. Arithmetic is a costed reversible
component, not a free oracle. No order, factors, peaks or reference answers enter
construction. Fourier processing of the reduced original-input register is an
explicit retained conventional diagnostic, not an order decoder. No sampling or
factor-recovery criterion is used in this bounded study.

## Raw and clean targets; garbage and environment

Raw: sum_b alpha_b |b,h(b),F(b)>.
Clean: sum_b alpha_b |b,0,F(b)>.
Tracing T,Z from raw leaves rho_bc=alpha_b alpha_c* delta_h(b),h(c) delta_F(b),F(c).
Tracing T,Z from clean leaves rho_bc=alpha_b alpha_c* delta_F(b),F(c).
The two states are not interchangeable. Generally a correct branch-preserving
output has a purification |b,F(b),eta_b>, and original-input coherence contains
alpha_b alpha_c* delta_F(b),F(c) <eta_c|eta_b>. eta includes both accessible
work and discarded environmental records. Its phase matters, not just magnitude.

Mandatory UNIT-domain pair N=3: b=(1,1,1), c=(1,2,2), h_b=1,h_c=2,F_b=F_c=1.
Use (|b>+exp(i theta)|c>)/sqrt(2), and retain the complex coherence exp(-i theta)/2.
A coherent raw preparation loses that reduced-input coherence if T is discarded.
Applying A1 coherently BEFORE discarding T restores it. If a syndrome record has
already escaped, A1 cannot erase it. Use theta=pi/3 and pi/2, and a deliberately
wrong phase to detect magnitude-only false positives.

## A: node-wise output-only corrections

L1_i=sqrt(kappa) A1 q^0_(T_i) A1; L2_i=sqrt(kappa) A2 q^0_(Z_i) A2.
Sequential CHANNELS E2 E1 are the infinite-time node channels, not the sum of
node generators. Their explicit reset syndrome isometries are
(b,t,z,0_E1,0_E2) -> (b,h,F, t XOR h, z XOR F).
On blank work the final environment records (h,F), so full graph coherences
survive only if both h and F agree. Coherent cleanup maps accessible T to zero
but leaves that environmental record. It cannot produce the pure clean target.
E1 E2 instead can leave stale downstream outputs: u=v=w=1,N=2,T=Z=0 gives
T=1,Z=0, while the correct final Z is 1.

Simultaneous generator G=G1+G2 is GKSL. It generally differs from sequential
composition; noncommutation alone is not a failure theorem. Here is a falsifiable
full-domain counterexample at N=2, NOT a blank-work preparation:
superpose b=(0,1,0) and c=(0,1,1), both initially T=1,Z=0. E2 E1 keeps final
coherence 1/2, as both correct products are zero and the first syndrome is shared.
For G1+G2, downstream reset can occur only on c before T is repaired. The
surviving coherence is (1/2) integral_0^infinity kappa exp(-3 kappa t/2) dt=1/3.
Test actual sparse evolution against this value. For blank uniform N=2 the
asymptotes may agree; that does not make the full channels identical.

A useful NEW certificate for this SUM does not assume the single-node gap.
Let E1 count wrong bits in T XOR h and E2 count wrong bits in Z XOR (T*W mod N).
Both are diagonal, positive. G1†E1=-kappa E1; G2†E1=0; G2†E2=-kappa E2.
One upstream bit correction can increase E2 by at most n. Hence
G1†E2 <= n*kappa E1. With H_pen=(n+1)E1+E2,
G†H_pen <= -kappa(E1+E2) <= -kappa/(n+1) H_pen, Delta=1.
Verify this matrix inequality in the small full-register case. Its kernel is the
RAW valid graph subspace. Every raw-valid vector is dark, while stationarity of
a density operator forces zero penalty. Thus fixed density operators are exactly
those supported on that subspace; no invalid recurrent density sector survives.
This proves attraction to the valid subspace and fixed-operator degeneracy d^6,
NOT a particular pure preparation. The penalty-rate bound is not a Liouvillian
gap claim; the sum's spectral gap and full-channel mixing bound are not supplied.

## B: naive node-wise input-plus-output preparation

Add A1 q^+_(U_i) A1 and A1 q^+_(V_i) A1 to G1.
Add A2 q^+_(T_i) A2 and A2 q^+_(W_i) A2 to G2.
There are 6n terms. The downstream T input drive acts on computed quantum
information, not a fresh independent input. Exhibit its effect on a correlated
RAW valid state, compute target-stationarity residual and valid-subspace leakage.
The combined family's stationarity/uniqueness/mixing are not inherited from either
isolated node. Finite-time stationary-looking data do not establish uniqueness.
Keep failures as negative controls.

## C: drive original leaves only, then repair the dressing

First remove downstream A2 q^+_T A2 from B. Retain A1-dressed U,V drives,
A2-dressed W drive, and the two output-reset families (5n terms). This avoids
independently resetting computed T, but an upstream drive can still change T
without updating Z. Test the resulting RAW target stationarity and leakage;
do not assume this local modification succeeds.

The justified compatible modification dresses upstream operations through the
remaining computation. Under V_raw=A2 A1, an upstream term becomes
A2 (A1 q A1) A2. It updates downstream data as required. In particular, both
upstream leaf drives AND upstream output corrections need this extra dressing.
The original downstream W and Z terms already have the required form, because
A1 commutes with their bare resets. This leads to the globally conjugated
reference D_raw, not to an unproved node-local implementation. Compute the actual
register support of each resulting matrix to expose the extra dependencies.

## D: explicitly costed global references

Start with product reset generator G0: plus resets on U,V,W and zero resets on
T,Z. D_raw has jumps V_raw q_j V_raw†; D_clean has V_clean q_j V_clean†.
There are 5n terms. Both are unitarily equivalent to independent amplitude
resets (plus-basis on leaves); therefore each has a unique pure target and global
attraction for known-target preparation. Their asymptotic channel sends rho to
Tr(rho)|target><target|. They do NOT preserve arbitrary incoming logical inputs.
The distinct unitary reference CHANNELS V_raw and V_clean DO preserve arbitrary
input amplitudes from blank work and are used for the N=3 phase-pair audit.

For D_raw/D_clean, a separately justified gap is kappa/2 by unitary similarity.
The conjugated excitation penalty decays at kappa, Delta=1; a conservative
trace-norm preparation bound is min(2,20n exp(-kappa*t/2)). These bounds assume
that exact global jumps with the specified rates are available. They say nothing
about the cost of constructing such reservoirs. Raw pure preparation still
fails clean-response readout when discarded T distinguishes equal-F branches.
D_clean and coherent compute/use/uncompute give the desired clean reference,
but are circuit-mediated/global arithmetic constructions, not native locality.

## Separate checks to perform

For each family, compute arithmetic-valid weights, RAW and CLEAN target
stationarity, valid-subspace leakage, silence (only where claimed), and actual
preparation trajectories. Report phase-sensitive off-diagonals, whole-state
fidelity, reduced-input trace distance, Fourier-distribution L1 distance, and
residual-work correlations separately. Numerical stationarity tests should not
be relabelled as uniqueness proofs. B/C gap, uniqueness and mixing remain unknown
unless separately established. Environmental distinguishability is explicit for
sequential channels and the analytic branch test; it is not guessed from a
reduced state for arbitrary simultaneous trajectories.

## Resource and implementation caps, fixed before simulation

N=2 is a full-register toy, not a representative Shor unit-domain instance.
Full-register numerical generator/evolution: ONLY N=2, n=1, dimension 32,
1024 density entries. Sparse 1024x1024 superoperators, capped at 200000 stored
entries; no dense full Liouvillian diagonalization and no full Choi construction.
At most 8 requested times, with kappa*t<=80. Targeted tests and reporting processes
have a 90-second external timeout. Matrix certificates use 32x32 system operators.

N=3 n=2 has dimension 1024 and 1048576 density entries. Do not build its
Liouvillian or full density trajectory here. The mandatory unit pair is treated
by exact sparse two-branch isometries/environment labels plus a 64x64 reduced
input matrix. The arithmetic permutations may be checked in sparse form on all
1024 basis labels. This restriction is explicit, not evidence of scalable
simulation or physical efficiency. No general-tree implementation in this phase.

System size 5n qubits; symbolic jump counts A=2n, B=6n, C=5n, D=5n.
A1 and A2 each act on three n-qubit registers. Global dressing can cross that
boundary. Record actual matrix support, sqrt(kappa) term norms, sum of squared
norms, ancilla costs A_mul(n), gate counts G_mul(n), and depth D_mul(n) as
unimplemented symbolic arithmetic obligations. V_raw uses two modular-XOR calls;
V_clean uses three (including uncompute). A dressed reset implementation can
require forward and inverse arithmetic around a reset step; exact autonomous
reservoir synthesis and physical locality are unknown. Additional scratch must
be cleaned coherently. No circuit depth is equated with relaxation time.

Report classical construction/evolution time and storage separately. Physical
precision, calibration, control/reservoir parallelism, energy, observation time,
TTS and advantage remain unknown. No robust RR, native scalability, physical
execution, order-search decoder, or factor-success claim is made. Retain the
existing parity-only benchmarks contract and all frozen source/checkpoint files.
