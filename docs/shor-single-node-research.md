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

# Single-node modular-multiplication reset research

Status: mathematical/simulation research checkpoint; no tree composition yet.
The finite Shor prototype and its witness scopes are unchanged. This document is
written before implementing the following new experiments.

## Model and admitted data

Let n=ceil(log2 N), d=2^n, N>=2. Registers U,V,Z each comprise n qubits,
H=(C^d)_U tensor (C^d)_V tensor (C^d)_Z. For all binary input labels define
f(u,v)=((u mod N)(v mod N)) mod N. Extending the function to every binary label
makes the unitary total; it does not silently discard labels >=N. Uniform-input
experiments use all d^2 branches, not uniform residues modulo N. These are node
tests, not order-finding or general-Q Shor executions.

The reversible arithmetic map is
A|u,v,z> = |u,v,z XOR f(u,v)>; A=A† and A²=I.
This is reversible even though multiplication is not invertible: inputs are kept.
Admitted compiler data are N, reset rate kappa>0 and the explicitly named candidate.
No order, factors, expected peaks or semantic reference are compiler inputs.

Initial preparation is |+_d>_U |+_d>_V |0>_Z unless a test explicitly supplies
another density operator. The pure target is
|G_f> = d^-1 sum_(u,v) |u,v,f(u,v)>.
The relation-valid subspace G is the span of all those basis states, not just
|G_f>. Its projector is P=A(I_UV tensor |0><0|_Z)A†.
H=0 for every generator below. Every jump has operator norm sqrt(kappa).

## Candidate A: coherent syndrome extraction, correction, and reset

Using a clean n-qubit syndrome S, the reversible computation on S=0 is
|b,z,0> -> |b,z,z XOR f(b)> -> |b,f(b),z XOR f(b)> (b=(u,v)).
The second operation XORs S into Z. The resulting isometry is unitary on the
larger space; discarding/resetting S yields Kraus operators
K_s = sum_b |b,f(b)><b,s XOR f(b)|, s=0,...,d-1.
Sum_s K_s†K_s=I, hence the channel is CPTP. These expressions specify the full
channel, not merely its classical truth table.

For a blank output, each matrix unit transforms as
|b,0><c,0| -> delta_(f(b),f(c)) |b,f(b)><c,f(c)|.
The discarded syndrome distinguishes different responses. Equal-response branch
coherences survive. With uniform input, target fidelity is sum_y p_y², where p_y
is the fraction of branches with response y. It is below one for nonconstant f.
The relation is satisfied, but pure graph preparation fails. Preserve this result.

Separately, tracing out Z gives the same reduced UV state as the ideal graph for
this initial state: both multiply each input matrix element by delta_(f(b),f(c)).
Any Fourier measurement on UV alone therefore agrees. This is a proved
alternative-output property of this single node, NOT a replacement for the pure
target or a claim about composed multiplication trees. Intermediate syndrome
records can distinguish branches that later share a final product.

## Candidate B: output-only conjugated GKSL reset

For output bit i let a_i=|0><1|_i and define
L_i=sqrt(kappa) A(I_UV tensor a_i)A†, i=1,...,n.
The generator is sum_i D[L_i], where `D[L](rho)=L rho L†-{L†L,rho}/2`.
It is a finite GKSL generator and unitarily equivalent to n independent amplitude
resets with a UV spectator. The asymptotic channel for arbitrary rho is exactly
Phi_inf(rho)=A(Tr_Z[A†rho A] tensor |0><0|_Z)A†.
It equals the syndrome channel in Candidate A, including its coherence loss.

Its fixed-operator space has dimension d^4 and consists precisely of operators
supported on G. All relation-valid states are silent. No invalid stationary
state or other recurrent sector survives; the tensor-reset spectrum has strictly
negative real parts outside that fixed space. Dark-vector completeness and fixed
operator completeness are distinct consequences, not inferred from one another.
The specified blank preparation nonetheless fails the pure target as shown above.

Let W_Z count output excitations in the decoded frame; H_pen=A W_Z A†.
L†(H_pen)=-kappa H_pen, Delta=1. Invalid-sector probability is bounded by
n exp(-kappa t). Separately, the nonzero spectral real-part gap is kappa/2 by
unitary similarity to the tensor-reset generator. This separate spectral argument
must not be confused with the penalty-Lyapunov rate kappa.
A conservative full-channel trace-norm convergence bound to Phi_inf is
min(2,4n exp(-kappa t/2)), obtained by telescoping single-qubit reset channels;
it concerns the actual asymptotic channel, not the desired pure graph.

## Candidate B+: input preparation as well as output reset

Do not stop at the failed blank-preparation ansatz. Add, for each U/V bit j,
M_j=sqrt(kappa) A(|+><-|_j tensor I_rest)A† to Candidate B.
There are 3n jumps total: 2n input-preparation terms plus n output corrections.
The decoded generator independently resets U/V to plus and Z to zero. Therefore
its unique stationary density operator is |G_f><G_f| and it attracts every initial
density matrix on the declared finite space, including the required blank input.
Its full asymptotic channel is rho -> Tr(rho)|G_f><G_f|. In particular this is
state preparation, NOT coherent processing of an arbitrary unknown UV input.

The graph subspace G is invariant. Output correction terms are silent throughout
G; input-preparation terms are silent only on the intended pure target, not on
every relation-valid state. Thus B+ does not satisfy an interchangeable module
contract that requires ALL valid states to remain unchanged. This limitation is
an explicit test, not a hidden weakening of Candidate B's contract.
It restores required off-diagonals for the known uniform target by driving inputs;
it does not preserve arbitrary incoming logical information. The discarded baths
can contain that initial information. This prevents inferring tree composability.

Use the sum of input minus-projectors and output one-projectors, conjugated by A,
as H_pen. Then L†H_pen=-kappa H_pen, Delta=1, unique dark vector |G_f>, unique
stationary state as above, and conservative trace-norm error <=
min(2,12n exp(-kappa t/2)); target-infidelity bound <=3n exp(-kappa t).
These are abstract fixed-rate generator bounds, not physical synthesis bounds.

## Resource obligations and classification

Input size is n bits, not the numerical modulus alone. The state uses 3n qubits.
Candidate A additionally uses n syndrome qubits and their reset; an actual
reversible arithmetic implementation may need A_mul(n) scratch qubits which must
be cleanly uncomputed. Candidates B/B+ have n/3n symbolic terms respectively,
with support potentially ALL 3n node qubits after arithmetic conjugation. They
are not bounded-weight/geometrically local just because each decoded reset is.
Each term has norm sqrt(kappa); their total squared-norm budgets are n*kappa or
3n*kappa. Parallel reservoir/control requirements must scale with the term count.

A's evaluation schedule, reversible gate count G_mul(n), depth D_mul(n), ancilla
count A_mul(n), and physical reservoir synthesis are not implemented here and
must not be set to zero. An implementation using A†, reset, then A explicitly
uses reversible arithmetic circuits; it is a costed circuit-mediated reset channel,
not evidence of an autonomous native local multiplication constraint. A compact
symbolic conjugation specifies a family but does not provide local synthesis.
There is no clock in these equations; no identification of circuit depth with
relaxation time is made. General tree construction/locality remains unresolved.

The tiny simulator enumerates the FULL tensor-product space, dimension d^3, with
density storage d^6 and a sparse superoperator acting on d^6 entries. It must
reject dimensions above its declared small bound. Classical construction/evolution
costs are measured separately from any physical cost. Precision, calibration,
physical preparation/control/reset/energy, observation duration and physical TTS
remain unknown. Deterministic density diagnostics use no shots; Fourier processing
is retained only as a numerical reduced-state diagnostic. There is no operational
order decoder, order search, factor extraction or advantage estimate in this node
experiment. Existing order validators/decoders remain outside its dependency graph.

## Tests and evidence to execute next

1. Check arithmetic permutation unitarity and GKSL trace/Hermiticity/positivity.
2. Compare syndrome Kraus and conjugated-reset limits on ALL matrix units at N=2;
   check Kraus completeness and both the equal/different-response superpositions.
3. Evolve actual density matrices under the sparse generator (no assumed decay).
   Compare B's asymptote, B+'s pure target, and penalty bounds at N=2 and N=3.
4. Check terminal subspace invariance separately from correction silence. Exhibit
   a valid basis state changed by B+ input preparation. Test unwanted fixed sectors
   by small full-superoperator nullities and analytic tensor-reset similarity.
5. Audit reduced input state/Fourier statistics for Candidate B separately from
   graph fidelity, and explicitly record that these do not prove tree composition.
6. Bind model, initial state, generator matrices, times, solver, implementation and
   derivation hashes to computed residuals. No hard-coded conformance boolean.
7. Run all Shor tests, full pytest and final SPICE gate, then save a new checkpoint.

Next research after this bounded checkpoint: two-node shared-register composition.
Test stale downstream products, noncommutators and environment distinguishability;
B+ input-driving terms are not assumed to be interchangeable local corrections.
Compare a global conjugation of the whole reversible computation with a sum of
node-wise dressed terms and cost the differences. Do not start tree simulations
until the single-node tests and notes are saved.

## Relation to prior work

Dissipative computation/state engineering is established research, not a novelty
claim here: [Verstraete, Wolf and Cirac](https://arxiv.org/abs/0803.1447).
Locality-constrained stabilization requires a separate analysis:
[Ticozzi and Viola](https://arxiv.org/abs/1112.4860).
The equations and candidate-specific conclusions above are the present derivation;
these papers are context, not evidence that this arithmetic node has a scalable
local implementation. No robust RR or physical claim is made.
