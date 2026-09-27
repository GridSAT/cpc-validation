# CPC-Shor P3: same-eigenphase dyadic composition — specification v1.0

Phase C: mathematics and bounded deterministic checks only. This document
becomes normative **only when named by the FINAL verified Phase-C manifest**.
Rolling recovery snapshots do not freeze it. Human review is required before
implementation. No stochastic P3 experiment or P4 is authorized by this file.

## 0. Baseline, scope and conventions

P2 PASSED only for the bounded finite model, under V2 acceptance SHA256
`2067dccf3b7709096bfd091ef70e26a72ef13d0657db5650eb7823bda4ed87f5`.
Attempt1 remains permanently FAILED. V2 completed25 batches once, passed153
criteria and independent recomputation, with15/255/1265 software tests and
SPICE4/4. Its primary hash is
`fa0f18ddd3ad621dcad3b5c7382e6f6e8575de017d5ba8e471d1de9cd80cb3ed`.
The P0–P2 specification, instrument, estimator, records, failed experiment,
failure analysis and all earlier evidence remain immutable. V2 records are
single-probe P2 evidence and MUST NOT be reused as multi-scale P3 trials.

The approved P0–P2 mathematics and conventions are inherited: hbar=1,
probe order (g,e), sigma_minus=|g><e|, real positive g_j,Gamma_j, total binary
multiplier U_c with identity padding, and LO_actual=LO_command−chi.
The present contract extends the same-data mathematical architecture, not its
native synthesis. Input arithmetic is N,a with coprime a; c_0=a and
c_(j+1)=c_j² mod N. Compilation/execution use these constants, never an order,
sector label, expected phase/denominator/peak, factors or spectral oracle.

## 1. Common-sector theorem (requirements2–4)

Let U=U_a on d=2^ceil(log2 N) dimensions. Composition including padding proves
U_cj=U^(2^j). Let P_lambda be the **full** spectral projectors of U, grouped
by equal eigenvalue across orbits and padding. On the |1> orbit, proof-only
vectors u_s obey U u_s=exp(2pi i s/r)u_s, theta_s=s/r. Rank-one orbit projectors
are useful independent diagnostics; the general theorem uses P_lambda.

For distinct probes j,k, every term of [H_j,H_k] is a product of commuting
probe operators and commuting powers/adjoints of U. Therefore

    H_j=g_j(sigma_j^+ U^(2^j)+sigma_j^- U^(-2^j)),
    [H_j,H_k]=0,
    [H_j,I_probes tensor P_lambda]=0.

The sum H_total has the same commutator property. Local probe fluorescence
J_j=sqrt(Gamma_j)sigma_j^- tensor I_D, monitored C_j=e^(-i vartheta_j)J_j,
inefficient unobserved channels, independent identity-reference operators and
ideal probe-only controls all commute with the data projectors. Time-ordered
products, finite collision Kraus maps and unobserved Kraus sums inherit this
block structure. Thus a definite sector never transitions. For every complete
instrument outcome y, write M_y for its CP map. With Q_s=I_probes tensor P_s,

    p(y)=Tr M_y(rho),
    w_s(y)=Tr[Q_s M_y(rho)]/p(y),
    integral p(y)w_s(y)dy=w_s(before).

The final equality follows from completeness and QND conservation, not from
equating conditioned and unconditioned states. Therefore w_s is a martingale;
its unconditional mean is conserved, while conditioned weights learn.
The |1> preparation gives proof-only initial weights1/r. One conserved latent
s reproduces **record probabilities**; operational generation must still
evolve the full arithmetic register, not secretly draw s from that mixture.

Sector conservation is not identification. Nor does it preserve off-diagonal
coherence between different base eigenvalues. Output baths may learn those
eigenvalues and dephase them, whether monitored or discarded. That is allowed
here. Equal-base-eigenvalue degeneracies are not distinguished by the ideal
apparatus. This is not the older graph-response coherence contract.

## 2. DP-P: primary parallel static bank (requirements3,5,8)

Prepare one data register in |1> ONCE and m signal probes in a product of
ground states. All m arithmetic couplings act on that same retained register.
Use independent vacuum Markov baths, separately labeled signal outputs and,
in the canonical profile, m separately prepared identity-reference probes.
References have no data coupling. Their calibrated transfer paths must match
the corresponding signal paths; a common LO alone does not establish this.

    L rho = -i[sum_j H_j + H_ref,rho]
            +sum_j D[J_j]rho +sum_j D[J_ref,j]rho.

The Hamiltonians are static during each trial. Each output uses the inherited
two homodyne commands0 and pi/2 with predeclared windows/transient treatment.
The two quadratures of one output are time-multiplexed, not two simultaneous
full-efficiency measurements. LO changes are controls even in this static
arithmetic profile. Optional heterodyne would split the output and needs a
separately reviewed efficiency/noise model; it is not silently substituted.

For a fixed theta and fixed calibration parameters, H_j reduces to the P2
two-level H_(2pi*2^j*theta). The sector-restricted generator is a sum of local
probe generators, with product initial probes and independent baths. Their
unnormalized instruments tensor-factor across j. This proves factorization
of the **entire local time-series laws**, not independence of samples within a
fluorescence record. It also proves that simultaneous backaction does not
cause sector transitions. The unresolved mixture couples all channel laws.

## 3. DP-S: resource variant with retained data (requirements3,8)

The canonical variant uses one signal probe and one independent identity
reference, each ground-prepared for every dyadic segment. The data is prepared
once. Segment j couples via c_j; within the segment both homodyne quadratures
and probe memory are treated exactly as in DP-P. At the segment boundary:

1. Stop observations according to the declared schedule and disconnect the
   signal–data Hamiltonian. Record the switching event and retained data ID.
2. Apply an **unobserved, complete** local probe reset
   R(rho_PD)=|g><g| tensor Tr_P rho_PD; likewise reset the reference probe.
3. Retain the full reduced conditioned data state. During dead time the
   ideal baseline data map is identity (a stated extension may use a
   sector-preserving channel, with its effect explicitly included).
4. Change c_j by the prescribed arithmetic schedule; calibrate the next
   reference transfer; reconnect, include burn/transient, and collect the
   next records without preparing a new data |1>.

For arbitrary entangled rho_PD,
Tr_P R(rho_PD)=Tr_P rho_PD exactly. In particular every retained sector weight
is unchanged by this ideal reset. This is stronger and more precise than
assuming a reset redraws a sector. Reset destroys probe–data correlations;
it does NOT erase information already in an environment. The reduced data
immediately before and after this ideal channel is identical, including its
existing coherences; it does not restore coherence previously lost.

Reset with the interaction still active is not automatically this map.
Postselecting a reset outcome can update sector weights even if every Kraus
operator commutes with P_s. Neither is admitted as the canonical reset.
For an unobserved dead-time QND channel E, E†(P_s)=P_s is required; it may
dephase inter-sector coherences. A monitored dead time adds records and a
likelihood factor. Missing outcomes are marginalized, never invented.

Sequential conditional data after segment j is the normalized partial trace
of its full instrument acting on the previous conditioned data, not a fresh
uniform sector mixture. DP-S must carry this state across resets. Full
probability bookkeeping includes reset baths and unobserved intervals.

## 4. Multi-channel monitored law and reference (requirement5)

Let alpha label every active signal or reference output. Set
C_alpha(t)=exp[-i(command_alpha(t)−chi_alpha(t))]J_alpha. For independent vacuum
baths and detectors in the frozen ideal profile,

    d rho_c=L rho_c dt +sum_alpha sqrt(eta_alpha) H[C_alpha](rho_c)dW_alpha,
    dY_alpha=sqrt(eta_alpha)Tr[(C_alpha+C_alpha†)rho_c]dt+dW_alpha,
    dW_alpha dW_beta=delta_alpha,beta dt,
    H[C]rho=C rho+rho C†−Tr[(C+C†)rho]rho.

Gamma already occurs in J=sqrt(Gamma)sigma_minus. Inefficiency splits observed
and unobserved output without removing the unconditional dissipator. The
innovations have independent infinitesimal vacuum noise; the finite records
are generally **unconditionally dependent** through the common sector and
possibly shared calibration parameters. No iid-in-time approximation is
implied. Probe fluorescence correlation time and transient costs remain.

Canonical calibration: per-path constant chi_j within a trial, known positive
gain and known offset after independently declared calibration, matched
identity-reference transfer, no unmodeled drift, and separately declared eta,
g,Gamma. chi_j is not supplied as a hidden truth to the estimator. References
must identify it from their records. An external calibration prior is fixed
before signal data; the canonical uninformative phase prior is uniform on
[−pi,pi). Signal/reference noises are independent conditional on theta and
these parameters. Any shared nuisance is integrated **once jointly**, not once
per signal. Reusing a noisy reference does not create independent calibration
estimates. Bounds on drift/gain/offset uncertainty must enter the future
preregistration; ideal zero drift does not establish physical robustness.

Correlated detector noise, cross-bath mixing, entangled probes, unmodeled
shared drift and adaptive scheduling fall outside the canonical factorized
profile. A covariance matrix alone does not specify a quantum instrument.
A future correlated profile must declare physical output mixing/unraveling,
covariance and whitening/inference together; replacing delta_alpha,beta by a
matrix in the innovation equation without revising the measurement map is
not an authorized shortcut.

## 5. Joint likelihood and answer-free operational inference (requirement6)

Under an ostensible product Wiener measure, the unnormalized filter is

    d rho_tilde=L rho_tilde dt
      +sum_alpha sqrt(eta_alpha)(C_alpha rho_tilde+rho_tilde C_alpha†)dY_alpha.

Its trace is the record likelihood ratio with respect to that measure.
For finite collision steps, use the exact positive P2 instrument and multiply
the trace normalizations; do not use an unnormalized Euler approximation as
the production finite-step law. Unrecorded intervals propagate the averaged
channel. Stored generator-conditioned states from discarded burn records
MUST NOT be supplied to an operational likelihood filter.

In a fixed sector the likelihood is L_s=P(all retained records|theta_s,nu).
With product probe preparations, fixed schedules, independent baths and
independent matched references, conditional on fixed nu:

    L(theta,nu)=product_j ell_signal,j(Y_j|2^j theta,nu_j)
                          ell_ref,j(R_j|0,nu_j).

Each ell is a full temporal instrument likelihood, including unobserved gaps.
For arbitrary uncertain shared nu the canonical marginalized likelihood is

    Lbar(theta)=integral L(theta,nu) p_cal(nu) dnu.

When both prior and conditional local laws factor, the separate nuisance
integrals factor too. Otherwise they do not. An equivalent conditional-on-
reference expression uses p(nu|R) and signal likelihoods; the same reference
must not be counted again. No free per-scale phase offset is fitted without
reference constraints: phi_j+chi_j alone is unidentifiable.

For diagnostic known sectors, pi_s(Y)=w_s(0)Lbar(theta_s)/sum_t w_t(0)Lbar(theta_t).
With known calibration this matches projectors applied to the full quantum
filter; with calibration uncertainty it matches the corresponding hybrid
quantum/classical mixture, not a filter given true hidden calibration.
This equation explains the physical prior; it does not authorize giving r,
s, spectral grids or oracle order tables to operational inference.

**Canonical operational output:** one record-only likelihood over the entire
circle theta in[0,1), its predeclared maximizer (ties: smallest coordinate),
and a jointly calibrated confidence set. Its input includes records, j values,
declared instrument/schedules and reference model, but not r, an N-derived
oracle spectral grid, expected rational values, or final conditioned states.
A uniform phase-grid numerical quadrature is allowed only if declared without
the answer, with discretization/error control; it is not an assertion that
the physical |1> spectral prior is Haar-uniform. A Haar-normalized likelihood
may be reported as a **working-prior** posterior, explicitly distinguished
from the physical discrete pi_s. Diagnostic projectors/known orders remain
outside the operational estimator. This resolves the prior/advice boundary
without reconstructing the order inside inference.

## 6. DP-P/DP-S equivalence: precise scope (requirement8)

For fixed theta, each DP-S segment begins with the same product ground probe
and independent bath/reference state as the corresponding DP-P channel.
Its local controls, rates, relative-time observation schedule and calibration
law are identical. Probe-only reset and unobserved sector-preserving dead time
leave sector weights unchanged. Hence its joint record probability is the
same product of ell_j. Multiplication of likelihood factors commutes, so both
profiles give the same diagnostic posterior for the same labeled local
records and same prior. This is **equality in law under a time relabeling**,
not equality of records generated with arbitrary RNG calls, intermediate
states, wall time, or physical resource cost.

It fails without these assumptions. Commuting Hamiltonians alone do not
guarantee product probe inputs, independent output maps, matched calibration,
or equivalent record laws. Incomplete reset retains sector-dependent probe
memory; reinitializing data replaces a common-sector mixture of products by
a product of mixtures; shared drift marginalized separately gives a wrong
likelihood; monitored resets/dead time add evidence; time-dependent hardware
drift changes the calibration law between simultaneous and sequential runs.
These are separate profiles requiring explicit rederivation, not silently
equivalent implementations. DP-P remains primary; DP-S is a resource variant.

## 7. Aliasing and resolution (requirement7)

For a nonempty dyadic index set J, exact complex phases alias iff
2^j(theta−theta') is an integer for every j. Since every2^j is divisible by
2^min(J) and that smallest power is included, the kernel is
theta−theta'=k/2^min(J) modulo1. In particular J={0,...,m−1} is already
injective for m>=1: **j0 alone removes exact complex-phase aliases**. Higher
scales improve potential precision, not injectivity of an already exact j0.
A single homodyne quadrature still has reflection ambiguity; both quadratures
or the justified complete temporal likelihood are required.

On a diagnostic order-r grid, an alias class at minimum index q has size
gcd(r,2^q)=2^min(v2(r),q). If r is odd, each dyadic map permutes its distinct
phases. If r=2^v r_odd, high scales erase the two-primary distinctions but
retain r_odd classes. When r is a power of two, scales j>=v are all phase0.

Mandatory tables (s listed only for independent validation):

| r | j0 numerators mod r | j1 | j2 | Consequence |
|---|---|---|---|---|
| 3 | 0,1,2 | 0,2,1 | 0,1,2 | odd order; each scale injective on this grid |
| 4 | 0,1,2,3 | 0,2,0,2 | 0,0,0,0 | two aliases at j1; complete loss at j2 |
| 6 | 0,1,2,3,4,5 | 0,2,4,0,2,4 | 0,4,2,0,4,2 | s and s+3 alias at every j>=1 |

For r6, j1 and j2 do not resolve their mutual twofold alias; j0 is essential.
Thus “early aliases” mean an early available subset such as {1} or {1,2},
not nonexistent exact aliases of the complete j0 complex phase.
With finite noise, even injective maps can have broad/multimodal likelihoods.
The posterior must retain all surviving modes; a narrow local peak is not
a global confidence set. Averaging branch-lifted phases chosen using truth
is prohibited.

Conditional error witness: if every scale observation in cycles is within
epsilon<1/6 of its true wrapped phase, a finest-to-coarsest half-lift rule
using only the observed phases selects the correct lift. At a step the
correct lift differs from the coarser observation by at most3epsilon/2<1/4,
while the alternative is1/2 away. Induction gives base error at most
epsilon/2^(m−1). This is a proof of a sufficient simultaneous-error event,
not the canonical estimator and not a measured success claim. Union-bound
per-scale/reference failure budgets suffice without unconditional independence.
For any requested resolution delta, choose m with epsilon/2^(m−1)<delta.
The inherited sufficient cell scale1/(2N²) therefore has a finite conditional
scale requirement; no rational reconstruction is performed. For illustration,
epsilon=1/8, N7 requires m>=5 by this witness. The smallest m<=3 mechanism
fixtures below do not establish that rational-resolution target, and arbitrarily
longer j0 records could in principle improve resolution without more scales.
Finite m alone never guarantees confidence or information at eta0.

## 8. Information criterion and proposed P3 gates (requirements9–10)

The most direct operational criterion is **calibrated global circular error
and a confidence-set width for one common theta**, with a model-consistency
test of the full multi-channel likelihood. In known-sector diagnostics,
evaluate coverage and concentration against labels only AFTER inference.
On physical operational runs report model-based sector posterior diagnostics
separately. Entropy, max pi_s, sum pi_s² and top-two log odds are useful but
do not independently certify a correct likelihood or accuracy. Expected
posterior entropy decreases under additional correctly modeled records;
individual trajectories need not do so monotonically.

| Gate | Mathematical rationale and future measured quantity |
|---|---|
| P3-A | Common-sector/QND: analytic commutators; finite-step no-transfer for each diagnostic sector; posterior martingale and residue leakage; prove one data-preparation event per trial. No ensemble-growth requirement. |
| P3-B | Joint-likelihood consistency: full-register instrument likelihood agrees with the independently derived sector mixture for fixed synthetic increments; operational likelihood uses all retained channels and no oracle. Separate nuisance integration validated. |
| P3-C | Joint confidence and concentration: circular error/coverage and total confidence-set diameter/arc length, including all modes; diagnostic pi_s/entropy as supporting evidence, not acceptance substitutes. Abstention and nonidentifiability retained. |
| P3-D | Alias resolution: verify r3/r4/r6 tables, unresolved subset modes and resolution when j0 is added; noisy performance measured at preregistered resolution, never by truth-selected lifts. |
| P3-E | Fresh-data negative control: independently reinitialize data between scales and compare the correct product-of-mixtures law against common-sector mixture-of-products; use a joint likelihood/record-correlation statistic with precomputed effect/power. Never assume every fresh trial is inconsistent. |
| P3-F | eta0 and number-detection controls: no theta information in observed vacuum homodyne at eta0; number records phase-blind for the ground-prepared, correctly reset profile. Detector random phases are not successful inference. |
| P3-G | Reference control: matched identity references, transfer phase signs and shared-nuisance accounting; predeclared wrong-sign/mismatched-reference tests and drift/efficiency sensitivity. Removing phase anchoring may make theta unidentifiable. |

No stochastic threshold is frozen here without power/error analysis. The future
acceptance identity must specify theta grid, diagnostic vs operational roles,
all parameters and nuisance priors, dt/convergence, retained/burn windows,
trials/seeds, caps, estimator grids/tie rules/integration tolerances, circular
resolution, global confidence construction, familywise error allocation and
each gate's numeric threshold. Discretization/nuisance quadrature errors must
be budgeted, not hidden by a fine-looking plotted peak. For Bernoulli diagnostic
success, exact binomial/Clopper–Pearson power at a declared alternative can
size trials; for likelihood ratios use a justified finite-model calibration
or rigorous bound, not an unproved chi-square asymptotic. Neither V2 counts
nor V2 thresholds transfer automatically. Freeze all choices before P3 records.

An exact distinguishability witness for P3-E uses j0 and j1 on r6. In an
ideal phase-resolving limit define A=exp(−4pi i theta_0), B=exp(2pi i theta_1).
For retained data theta_1=2theta_0 mod1, so E[AB]=1. For independent fresh
sectors both separate means vanish, so E[AB]=0. No truth label enters this
statistic. Finite fluorescence/reference records require a specified noisy
version and power analysis; the ideal witness is not itself a noisy threshold.
Some configurations (e.g. a constant j1 phase on r2) cannot distinguish these
models and are unsuitable as the sole negative-control fixture.

## 9. Bounded fixtures and resource contract (requirements11,13)

Use N7,a3 as mandatory operational input; r6 is independent-validation fact
only. Add N7,a2 (odd order3) and N5,a2 (power-of-two order4) only to test the
distinct structures above. Diagnostic c sequences are (3,2,4), (2,4,2),
(2,4,1) respectively for j0,1,2. Compilation computes c by squaring,
without validating order. No coprimality/order/factor result is inferred
from measurement here. Controlled small tests can include subsets {1},{1,2}
and the complete {0,1,2}; the first bounded implementation should use at most
three signal probes until separately reviewed. This cap is a resource choice,
not an assertion of rational-resolution accuracy.

DP-P: n data qubits, m signal probes, m dedicated reference probes in the
canonical profile; m simultaneous arithmetic couplings; 2m separately labeled
monitored outputs, each quadrature-switched in time. ||H_signal||=sum_j g_j:
in a sector the independent probe Hamiltonians have eigenvalues±g_j, whose
maximum sum is attained. References add sum_j g_ref,j to total norm;
sum Gamma_j plus reference rates counts dissipative strength. Fixed individual
g as m grows increases the total budget. Wall observation time is the maximum
channel schedule when simultaneous; calibration/burn/correlation time still
count. Full signal state dimension d2^m is64 for N7,m3; references may be
simulated separately only because their quantum instruments factor as stated.
Literal dense representations scale exponentially; no physical efficiency claim.

DP-S: one signal plus one reference probe, signal state dimension2d; m−1
coupling retunes, m ground preparations including m−1 resets, explicit reset
duration/error and switching/dead-time costs. Cumulative signal time is the
sum of segment burns/windows plus resets/switches/calibration. Retained data
must remain QND throughout; no hidden reprepare. Inference with M theta points,
K local nuisance points and T total record steps costs at least the declared
filter work (factorized two-level likelihood roughly O(MKT)); shared nuisance
dimension can make quadrature exponential. Report memory, global grid
resolution, refinement and convergence, not just an arithmetic operation count.

Native H_j synthesis stays unresolved P6. No locality, polynomial complete
resource bound, physical calibration stability or hardware feasibility follows
from commuting dense/permutation Hamiltonians.

## 10. RFC-0010/profile mapping (requirement14)

Compilation: arithmetic constants and generator/channel identities only.
Preparation: one retained-data ID and |1> preparation event, probe/reference
preparations and reset map. Open-system execution: profile DP-P or DP-S,
instrument/unraveling, schedules and all baths. Referenced observation: raw
channel records with timestamps/window masks and calibration provenance.
Fixed inference: joint likelihood/estimator identity, prior/nuisance policy and
error control. Independent validation: separate known-order/projector fixtures,
truth labels, alias tables and requirement-specific methods/identities.

Repository review: `OpenSystemExecutionSpecification` and external-reference
declarations provide execution/reference identities and metadata; `ObservableExecution`
permits named observations and metadata; `RequirementEvidence` supplies an
evidence_id, method and sorted details per requirement. These can **carry**
channel maps and hashed sidecars but do not themselves enforce common-trial
data continuity, joint likelihood semantics or multi-channel record alignment.
The current specification has a singular optional `external_reference` field;
a bank-wide reference bundle needs an explicit profile convention/sidecar,
not an assumption that a typed per-channel reference list already exists.
Existing Shor graph certificates must not be reused as monitored-QND evidence.

Propose a versioned profile sidecar (not an implemented schema or new RFC):
profile_id, trial_id, data_register_id, exactly-one preparation_event_id,
ordered reset/switch/dead-time events, channel_id→probe/reference mapping,
record and retained-window hashes, instrument_id distinct from GKSL_id,
schedule/timebase, noise-independence assumptions, calibration/nuisance identity,
likelihood/estimator/confidence identities, source/seeds for simulation,
oracle-diagnostic provenance, and requirement-specific same-sector evidence.
Validate references and chronology rather than trusting arbitrary strings.

OS-1..4: preserve generator decomposition, admitted arithmetic and answer
independence; OS-2 also binds the base-sector/residue definition. OS-5..8:
no violation-removal dark-state or unique semantic fixed-space claim.
DC-4: probe relaxation is separate from inference time; DC-5: sector/residue
leakage; DC-6: complete profile cost ledger. RR-1..4: channel/reference/drift
identities; RR-5..8: fixed joint confidence/robustness evidence remains future
and cannot be passed by this derivation. OV-1..4: raw observation vs inference
vs validation separation, same-trial provenance and abstract/simulated status.
No RFC-0011 or normative RFC modification is proposed by this phase.

## 11. Verification, unresolved work and stop boundary

The companion deterministic checker tests bounded commutators, projector
invariance, local reset on entangled states, exact finite-outcome instrument
factorization/full-mixture likelihood, posterior normalization/martingale,
alias tables and fresh-data/control witnesses. Chosen increments and Gaussian
quadrature nodes are deterministic mathematical test inputs, not P3 records.
No stochastic runner, operational P3 decoder or P4 algorithm is implemented.
The Phase-C check file reports **18 passed in0.16 seconds, no warnings**.
Its synthetic finite-outcome collision steps are algebraic test inputs, not
an experimental timestep selection or a generated measurement population.

Mathematical feasibility is established under the stated ideal assumptions;
finite-record P3 success is not. Open: preregistered power/error budgets,
global likelihood confidence calibration with nuisance integration, finite
step/grid convergence, reset imperfections/dead-time models, correlated baths,
physical transfer stability, schema enforcement, and all synthesis/scaling.
No continued fractions, rational/order reconstruction or verification,
LCM/GCD combination, factoring or P4 result is part of the deliverable.
No robust order recovery, native/scalable/physical realization, physical TTS,
robust RR or matched-confidence advantage is established. The earlier
multiplication-tree candidate remains constraint-description-only.

P2 PASSED only for the bounded finite model. Human review of this FINAL-frozen
specification and a new separately hashed preregistration are required before
P3 stochastic implementation/execution. STOP after Phase C.
