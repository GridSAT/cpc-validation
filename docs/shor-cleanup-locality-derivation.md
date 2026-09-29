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

# Cleanup-aware two-node locality: derivation before implementation

This phase preserves all previous evidence. It asks whether local correction can both prepare a clean response and avoid recording the intermediate product. A restricted local repair architecture is obstructed below. A second construction passes the coherence test, but explicitly executes a clocked reversible circuit; it is a control, not a native solution. No general tree is authorized by either result.

## Registers, domain and target

Data registers are U,V,W,T,Z with d=2^n, n=ceil(log2 N), exactly as in the frozen two-node model. Arithmetic uses the full binary extension m(a,b)=((a mod N)(b mod N)) mod N. Let h=m(U,V), F=m(h,W). A1 flips T by XOR h and A2 flips Z by XOR m(T,W). Both are total involutions. The clean target for arbitrary amplitudes is sum_b alpha_b |b,0,F(b)>; the raw target retains T=h(b). Numerical preparation is uniform full-binary leaves with blank T,Z. N=2 is a toy mechanism case; N=3 unit-pair evidence is separate.

## Attempt L: autonomous dark local repair (obstructed)

Attempted operators have H=0 and independent jumps supported on UVT and TWZ, respectively. Each preserves the leaf labels. Optional ancillas may be included in each neighborhood, including a common shared ancilla, but the clean code has a fixed branch-independent ancilla state a0 and the prescribed blank preparation uses that same state. Every jump annihilates every clean arithmetic basis state. This silence requirement is an explicit architectural assumption, stronger than stationarity of one prescribed pure state.

For upstream jumps J_L, silence forces J_L|u,v,T=0,a0>=0 for all allowed u,v. For downstream J_R, it forces J_R|w,T=0,z,a0>=0 for every z that occurs as a valid final response at that w. In the full input domain h=0 is available; hence z=0 occurs at every w. Every |u,v,w,0,0,a0> is therefore killed by every jump. Its density and all coherences between such vectors are stationary. Blank preparation is trapped even on inputs with nonzero F. This is a local indistinguishability obstruction, not a numerical small-residual inference.

On the N=3 unit-only domain, outputs span {1,2} at each unit w. Thus all clean-T states with either unit output are dark, including incorrect outputs. This proves wrong-output traps, but does NOT prove blank Z=0 is dark in the unit-only domain. A fixed common ancilla does not remove either local indistinguishability argument.

This theorem does not cover non-dark stationary jumps, interacting Hamiltonians with cancellation, coherently shared baths, evolving computational ancillas/clocks, or other neighborhoods. A single J_L+J_R must be counted with union support and cross terms; it is not two independent baths. No universal local-construction impossibility is claimed.

## The environment obstruction and the mandatory gate

For b=(1,1,1), c=(1,2,2) at N=3, h_b=1,h_c=2 and F_b=F_c=1. Starting with (|b>+exp(i theta)|c>)/sqrt(2), the required off-diagonal is exp(-i theta)/2. A branch-preserving dilation with final output F has reduced off-diagonal alpha_b alpha_c* delta(F_b,F_c)<eta_c|eta_b>, where eta contains every discarded work/control/bath degree of freedom. Complex overlap must be 1, not merely have magnitude 1.

The already established node-reset syndrome records (h,F) are orthogonal for this pair: overlap 0, reduced coherence 0 even after accessible T cleanup. No new failed-reset generator is implemented or simulated here. The required values at theta=pi/3,+pi/2,-pi/2 are 1/4-i sqrt(3)/4, -i/2,+i/2. Conjugating the coherence gives a wrong-phase control of equal magnitude and different Fourier statistics. Re-preparing one known phase is not recovery of arbitrary input phase.

## Attempt C: collective clock transitions (passes, explicitly circuit-mediated)

Add one four-level clock C=0,1,2,3, encoded by two qubits. Order is C,U,V,W,T,Z. No other modeled ancilla is added. Initially C=0 and T=Z=0. The clock ends at 3; it must not be silently treated as reset. H=0 and the three independent bath couplings are

J_j=sqrt(kappa)|j+1><j|_C tensor B_j, j=0,1,2,
B_0=A1, B_1=A2, B_2=A1.

Each B_j is the whole coherent unitary arithmetic permutation, not separate jumps per data branch. Supports are (C,U,V,T), (C,T,W,Z), (C,U,V,T): 3n+2 qubits in the binary-clock implementation, five qubits per jump at N=2. The two-node interaction neighborhoods are bounded, but qubit support grows with n and arithmetic synthesis is not supplied. This is an explicitly programmed three-transition compute/use/uncompute circuit; bounded neighborhoods do not change its classification.

J_j^dag J_j=kappa |j><j| tensor I, so jump intensities and no-jump survival probabilities contain no data labels. The bath for transition j records j and the emission time. It learns progress, not h, F, any leaf, or a branch-dependent phase under the exact assumed coherent coupling. This collectivity is a reservoir/control requirement, not a demonstrated hardware capability. Splitting J_j into branch- or product-resolved jumps changes the dissipator and can export which-branch information. In particular resolving h in the first bath gives overlap 0 for the mandatory pair. Equal diagonal transition probabilities do not justify such a split.

Let V0=I, V1=A1, V2=A2 A1, V3=A1 A2 A1. For x=kappa*t the solution from clock0 is
rho(t)=sum_{j=0}^3 p_j(x)|j><j| tensor V_j rho0 V_j^dag,
p0=exp(-x), p1=x exp(-x), p2=x^2 exp(-x)/2,
p3=1-exp(-x)(1+x+x^2/2).

A joint trajectory dilation has branch-independent normalized bath vectors E_j(t) in orthogonal emission-count sectors. For each j, the conditional bath overlap is exactly 1 for all b,c. Bath reduced states for basis branches are identical; at finite time accessible work still differs. At absorption the environment factors from the data, eta_b=|C=3,T=0,E_3> for every branch, and overlap is exactly 1. Integrating over jump times cannot leak branch identity because the waiting-time amplitudes are branch independent. This explicitly distinguishes accessible intermediate records from irreversible bath records.

For the mandatory pair the work labels by stage are (T,Z)=(0,0),(h,0),(h,1),(0,1). Thus reduced coherence at finite time is exp(-i theta)(p0+p3)/2; the missing p1+p2 coherence is correlated with accessible T. At completion it is exp(-i theta)/2. At t=0, matching readout coherence does not imply arithmetic correctness: Z is still blank. At all stages full corresponding branch coherence is preserved within the stage. These formulas hold for theta=pi/3 and signed pi/2; deliberately conjugating the desired phase fails a Fourier-distribution comparison despite equal magnitudes.

Analytical gate: C passes the required N=3 overlap/phase test for the stated exact coupling and preparation. L and the product-resolved bath control do not pass as a native clean preparation. Only C proceeds to full numerical implementation.

## Stationarity, attraction, costs and limits

Define Wclock=sum_j |j><j| tensor V_j. Conjugating J_j by Wclock gives sqrt(kappa)|j+1><j| tensor I. This is a clock-chain similarity, not the frozen global product-reset generator. It exposes the circuit equivalence. The sink contains every data operator: stationary dimension D^2 (1024 for D=32). For off-diagonal clock blocks the rates are -kappa when both clocks are transient and -kappa/2 with one sink. Diagonal transient blocks form a triangular chain with eigenvalue -kappa, sink zero. Thus the positive real-part gap is kappa/2, proved separately; transient Jordan blocks produce polynomial factors. There is no unique logical target and no mixing-to-one-state claim.

For clock0 and any normalized rho0, the full-state trace distance to |3><3| tensor V3 rho0 V3^dag is exactly q=1-p3. The data trace distance is at most q and Fourier L1 at most 2q by contraction. This proves attraction from the specified blank preparation to its clean output. Expected absorption time is 3/kappa in this ideal model. It is not physical TTS. Exact finite-time terminal conditioning gives the output with probability p3, but the main diagnostics are unconditional and no discarded heralds are hidden.

Terminal clean-subspace leakage and target residual vanish because every sink state is dark, including wrong outputs. This is not a repair property. Arbitrary initial T=t,Z=z instead ends with T=t, Z=z XOR m(t XOR h,w), so nonblank preparation generally fails. Reusing C=3 without reset does nothing; adding C3->C0 reset with active gates repeats V3, an involution, and toggles an ideal clean output back to blank. External reinitialization/control for a new blank run is an additional cost. No self-correcting repeated-operation or tree composition claim follows.

Resource ledger: three bath channels, each norm sqrt(kappa), sum norm-squares 3kappa; two clock qubits plus 5n data qubits; three coherent multiplication calls (two A1, one A2). Arithmetic gate count/depth and scratch A_mul(n), bath spectral matching, calibration, collective transition engineering, control locality, reset energy and observation are unresolved. The dense arithmetic-permutation description is a finite reference, not gate synthesis.

Full numerical cap: N=2 only, Hilbert dimension128, density entries16384, sparse Liouvillian dimension16384 with at most200000 nonzeros, at most8 times with 0<=kappa*t<=80. No dense Liouvillian or Choi matrix. Use complex128 sparse exponential action, external 120-second runtime cap, and 1-GiB process address-space cap with single-threaded BLAS. N=3 uses two branches and 64x64 reduced-input diagnostics only. No full N=3 clock Liouvillian. All old controls are compared using their frozen source-bound report; required repository validation may rerun tests without overwriting old logs.

## Decision gate and exact next step

C can establish arithmetic, response-class phase, branch-blind discarded baths and one-run work cleanup under its preparation contract. It fails the native-locality gate because it explicitly schedules the known circuit, and autonomous reset/reuse is not established. L fails under its stated dark-local assumptions. The general-tree decision gate therefore remains closed. A future native candidate must change an explicit assumption (for example genuinely local Hamiltonian interference with a common clean ancillary state) and derive bath overlap and stationarity before simulation; the present theorem does not adjudicate such architectures.

No RFC-0010 native realization, physical realization, robust RR, physical TTS, matched-confidence advantage or scalable CPC-Shor dissipator is established. The frozen multiplication-tree candidate remains constraint-description-only.
