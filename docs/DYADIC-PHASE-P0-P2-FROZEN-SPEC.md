# CPC Dyadic Phase Order Finding — P0–P2 frozen specification

**Phase A; specification version 1.0; human review required before Phase B.**

This document freezes mathematics, conventions, measurement assumptions and acceptance criteria. It does not assert that every acceptance criterion is already demonstrated. P0 and P1 are derived below. P2 has an explicit ideal monitored-output model; calibrated finite-record inference and its error bound remain unverified. No P3–P7 gate is passed. Changes to a frozen item require explicit reopening; implementation must not alter mathematics to make tests pass.

## A0. Recovery, scope and attribution

The preceding dyadic work left `docs/dyadic-phase-derivation.md`, `src/dyadic_phase_probe.py`, `tests/test_dyadic_phase_probe.py`, a targeted log, and preliminary recovery helpers. The 18 targeted tests passed in 0.33 s with four SciPy deprecation warnings. No dyadic archive, conditioned-record simulator, full dyadic integration validation or decoder had been completed. These files are frozen as supporting prototype evidence; Phase A does not extend them. The full recovery manifest and starting Git state are in `results/shor/dyadic-phase-a/recovery-audit.json`. The user confirmed the first attachment was the complete proposal; the subsequent Phase-A-only request supersedes its implementation scope.

All older CPC-Shor evidence, archives, source and conclusions remain unchanged. The multiplication-tree candidate remains constraint-description-only; its general-tree gate stays closed. No staging, commits, pushes, merges, tags, releases, main modification or hardware/FPGA operation is authorized.

Three layers remain separate:

1. **A — semantics:** arithmetic inputs `(N,a)`, order `r=ord_N(a)`, and standard order-to-factor reduction.
2. **B — ideal measurement:** the exact fixed-multiplier Hamiltonian, probe baths and monitored instrument specified here.
3. **C — physical synthesis:** native realization with polynomial complete resources, unresolved and outside Phase A.

The proposal supplies the Hamiltonian and candidate response formulas. Their verification and the deductions below are mathematical work for this track, not claims of a new quantum algorithm. Unitary eigenvalue measurement is established in [Kitaev, 1995](https://arxiv.org/abs/quant-ph/9511026); single-ancilla iterative phase estimation is established in [Dobšíček et al.](https://arxiv.org/abs/quant-ph/0610214). Absence of an explicit QFT or large phase register is not novelty. [Wiseman](https://arxiv.org/abs/quant-ph/0302080) supplies measurement/trajectory foundations. [Naghiloo et al.](https://arxiv.org/abs/1612.03189) demonstrate phase-sensitive fluorescence monitoring, not modular-multiplier synthesis. No source is used as evidence for Layer C.

## A1. Admitted inputs and total arithmetic (P0)

For the factoring application, N is odd composite and 1<a<N with gcd(a,N)=1. Bounded algebra checks may use primes and even N, explicitly labeled diagnostics. Set n=ceil(log2 N), d=2^n. Let c_j=a^(2^j) mod N, obtained by j modular squarings from a; no order is required.

Define on the full binary register

`U_c |y> = |c*y mod N>` if y<N, and `U_c |y> = |y>` otherwise.

For gcd(c,N)=1 the residue map is bijective with inverse multiplication by c^-1 mod N. Padding is a disjoint identity permutation. Hence U_c is total and unitary. Composition gives U_c U_b=U_(cb mod N), including padding, and adjoints are inverse multipliers. Therefore U_cj=U_a^(2^j) on the entire binary space; all such multipliers and adjoints commute.

Prepare the data once in |1>. Its orbit `{a^k mod N}` contains only residues, so it never reaches padding under these multipliers or the ideal couplings. For proof only, let its length be r and define

`|u_s> = r^(-1/2) sum_(k=0)^(r-1) exp(-2pi i s k/r) |a^k mod N>`, 0<=s<r.

A cyclic index shift gives U_a|u_s>=exp(2pi i s/r)|u_s>, and Fourier orthogonality gives |1>=r^(-1/2)sum_s |u_s>. Thus U_cj|u_s>=exp(2pi i 2^j s/r)|u_s>.

The symbols r,s and eigenvectors are analytical/validation objects only. Compiler, preparation and execution inputs may contain N,a,j (or a bank size), declared rates, truncation/caps, reference configuration, efficiency, time schedule and random seed. They must reject r,p,q,s, expected phases/peaks/denominators, precomputed orders and equivalent advice. No diagnostic eigendecomposition may generate operational records by secretly drawing the correct sector.

## A2. Primary static bank and QND theorem (P0)

Tensor order is probes 0,...,m-1, then data. Each probe basis is `(g,e)` with sigma_minus=|g><e|, sigma_plus=sigma_minus^dag, X=sigma_plus+sigma_minus, Y=[[0,-i],[i,0]]. Set hbar=1. Real g_j>0 and Gamma_j>0 have units inverse time. Any physical drive phase is included in reference calibration, not silently set to zero.

`H_j = g_j (sigma_j^+ tensor U_cj + sigma_j^- tensor U_cj^dag)`;
`J_j = sqrt(Gamma_j) sigma_j^- tensor I`;
`H_QND=sum_j H_j`;
`L(rho)=-i[H_QND,rho]+sum_j D[J_j](rho)`;
`D[J](rho)=J rho J^dag - {J^dag J,rho}/2`.

For j!=k expand the four terms in [H_j,H_k]. In each term probe operators commute because their tensor factors differ; data factors are powers or inverse powers of U_a and commute. Every term is zero. Thus [H_j,H_k]=0. This assumes the exact multipliers on a common data register and distinct probe factors; arbitrary crosstalk, approximation errors or noncommuting controls are not covered. Scalar rate changes do not spoil the algebra, but are not a claim of static hardware synthesis.

Let P_lambda be a full spectral projector of U_a, grouping any degenerate eigenvalue across orbits/padding. Every multiplier is a polynomial in U_a, so `[H_QND,I_probe tensor P_lambda]=[J_j,I_probe tensor P_lambda]=0`. In the adjoint generator, the Hamiltonian term vanishes and each dissipative term is `Q J_j^dag J_j - Q J_j^dag J_j=0`, where Q=I_probe tensor P_lambda. Hence `d Tr(Q rho)/dt=0`. The residue projector is also invariant.

This is conservation of sector population, not preservation of arbitrary coherence between different eigenvalues. Measurement-induced inter-sector dephasing is allowed and expected. It is fundamentally different from the frozen graph-preparation response-class coherence contract. Degenerate vectors within a fixed eigenvalue are not distinguished by the ideal multiplier-dependent apparatus.

## A3. Complete single-sector probe response (P1)

Fix one sector and phi=2pi*2^j*theta modulo2pi. The probe Hamiltonian is

`H_phi = g [[0,exp(-i phi)],[exp(i phi),0]]`, `J=sqrt(Gamma)[[0,1],[0,0]]`.

Write p=rho_ee, q=<sigma_minus>=rho_eg, z=exp(-i phi)q, u=Re z, v=Im z. Direct matrix multiplication gives

`qdot=-(Gamma/2)q - i g exp(i phi)(1-2p)`;
`pdot=-Gamma p-2g v`;
`udot=-(Gamma/2)u`;
`vdot=-(Gamma/2)v-g+2g p`.

Let D=Gamma^2+8g^2 and A=2g Gamma/D. The unique stationary state for this driven, damped two-level sector is

`p_ss=4g^2/D`, `q_ss=-i A exp(i phi)`,
`rho_ss=[[1-p_ss,conj(q_ss)],[q_ss,p_ss]]`.

Its determinant is 16g^4/D^2>0 and its trace is1, so it is positive. Direct substitution and the nonzero decay eigenvalues establish stationarity and uniqueness for the single probe at fixed sector, not for the entire data-plus-probe model.

`<X>_ss=2A sin(phi)`, `<Y>_ss=-2A cos(phi)` under the above Y convention. Photon flux is `Gamma p_ss`, independent of phi.

The exact transient is `u(t)=u(0)e^(-Gamma t/2)` and

`[p(t)-p_ss,v(t)-v_ss]^T = exp(Bt)[p(0)-p_ss,v(0)-v_ss]^T`,
`B=[[-Gamma,-2g],[2g,-Gamma/2]]`.

Eigenvalues are `-3Gamma/4 +/- sqrt(Gamma^2/16-4g^2)`. At g=Gamma/8 use the matrix exponential/Jordan limit, not division by the vanishing square root. Together with -Gamma/2 these specify relaxation. The slowest asymptotic decay exponent is Gamma/2; finite-time norm bounds must retain prefactors and the critical Jordan term. Relaxation is not the time needed to infer a phase at given confidence.

For t=g/Gamma, dipole amplitude A=2t/(1+8t^2), maximized at t=1/sqrt(8) with A=1/(2sqrt(2)). If t remains in a fixed compact interval bounded away from0 and infinity, ideal normalized contrast has a positive lower bound independent of N. This statement assumes rates and reference quality can be maintained; it proves no physical scaling. Signal vanishes as g/Gamma tends to0 or infinity, and identifiability fails when the effective monitored efficiency is0. Gamma=0 is excluded from the stationary dissipative claim.

The phase rotation R_phi=diag(1,exp(i phi)) gives H_phi=R_phi H_0 R_phi^dag and transforms sigma_minus only by a scalar phase. For a ground-prepared probe, number detection and no-click evolution have identical record probabilities for every phi: emission counts, including their temporal correlations, are a phase-blind negative control. A coherently prepared, separately referenced probe could change transient counting information; that is outside this fixed preparation contract.

## A4. Normalized monitored instrument and reference (P2 specification)

The following is an ideal Markov, rotating-frame, vacuum-input output model. Each dissipative output is individually accessible, and detector noise channels are independent conditional on the quantum state. Assume independent baths, no unmodeled dephasing/crosstalk/detuning, known positive rates and a calibrated LO. Failures of these assumptions require an approximate model and explicit error budget.

For homodyne monitoring let `C_j(t)=exp(-i vartheta_j(t)) J_j`, efficiency eta_j in[0,1], and independent innovations satisfying `E[dW_j|past]=0`, `dW_j dW_k=delta_jk dt`. Then

`d rho_c=L(rho_c)dt+sum_j sqrt(eta_j) H[C_j](rho_c)dW_j`,
`H[C](rho)=C rho+rho C^dag-Tr[(C+C^dag)rho]rho`,
`dY_j=sqrt(eta_j)Tr[(C_j+C_j^dag)rho_c]dt+dW_j`.

The variance of dY_j conditional on the past is dt to leading order. With J_j containing sqrt(Gamma_j), its drift is exactly the requested `sqrt(eta_j Gamma_j)<exp(-i vartheta_j)sigma_j^-+exp(i vartheta_j)sigma_j^+>_c`. Do not insert a second sqrt(Gamma_j). Inefficiency changes the monitored innovation, not the unconditional dissipator. Averaging the Ito equation yields GKSL; a GKSL expectation is neither a conditioned state nor an observed current sample.

These conventions agree with fluorescence homodyne normalization after rescaling the measured increment in Naghiloo et al., equations2–3, by sqrt(Gamma); their phase orientation must be translated to the minus sign chosen here. The infinitesimal measurement form is `M_dY=I-iHdt-(1/2)sum J^dag J dt+sum sqrt(eta)C_j dY_j`, with additional unobserved jump terms `(1-eta_j)J_j rho J_j^dag dt`. Gaussian averaging and Ito products recover L to first order. This first-order expression specifies the continuum instrument; it is not a finite-step positivity-preserving numerical integrator.

Freeze time-multiplexed homodyne phases0 and pi/2, with known equal observation windows and no arithmetic switching, as the baseline two-quadrature readout. Each block must either include the probe transient in its likelihood or declare a burn-in/error bound; unconditional stationarity does not make conditioned fluorescence white independent samples. Simultaneous heterodyne is an optional future variant requiring its own split-output normalization and efficiency accounting. A single fixed quadrature has a phase ambiguity and is not sufficient by itself.

For stationary means define `K_j=2sqrt(eta_j Gamma_j)A_j>0`. With ideal reference, `I_0=K_j sin(phi_j)` and `I_pi/2=-K_j cos(phi_j)`. Thus `Z_j=-I_pi/2+i I_0=K_j exp(i phi_j)`. Phase is identifiable from both quadratures modulo2pi. This identifies a response map, not a finite-record accuracy guarantee.

**Explicit reference channel.** Use a probe with U_ref=I and logical phi_ref=0, subject to a characterized drive/LO/detection transfer path. Define the net instrumental phase chi_j so `arg Z_j=phi_j+chi_j`; for a pure LO command offset delta_j, chi_j=-delta_j in these conventions. A matched reference measurement gives `arg Z_ref,j=chi_j`, and corrected phase is `arg(Z_j conj(Z_ref,j))`. For DP-P, use a separate identity-reference channel, or pre/post-trial calibration of the same readout chain with a justified drift bound throughout the trial. A dedicated reference probe is therefore not logically necessary, but an equivalent calibrated reference procedure is. Switching a data-coupled probe to an identity interaction during the trial is a DP-S/calibration variant with explicit switching costs, not the static DP-P baseline. A shared LO alone does not calibrate unknown per-channel transfer phases. The hardware/path equivalence, drift bounds, timestamps, gains, offsets, eta_j, rates and covariance must be recorded. A separate reference may serve several channels only with a verified transfer calibration. Its hardware and measurement time are counted.

If a complex response estimate obeys |Z_hat-Z|<=e<K, a conservative phase error is `arcsin(e/K)`; add the corresponding reference error and bounded unmodeled phase drift, with circular distance and confidence accounting. This deterministic geometric bound does not establish that a finite record achieves e. Gain signs and quadrature orientation must be independently calibrated; conjugation is not harmless.

## A5. Common-sector conditioning and joint inference contract

All powers in one trial share the data initially prepared once in |1>. Every Hamiltonian, jump, monitored linear operator and probe-only reset commutes with the base spectral projectors. The resulting instrument is block diagonal. Its record probability is therefore a mixture over one persistent sector, `P(Y)=sum_s w_s P(Y|theta_s)`; coherences between sectors contribute no term to the trace probability. Here initial orbit weights are1/r only as an analytical explanation; operational execution never receives r or s.

Unconditional sector weights are constant. Conditioned weights are not constant: with `w_s=Tr(Q_s rho_c)`, their stochastic increment is `dw_s=sum_j sqrt(eta_j)(Tr[Q_s(C_j rho_c+rho_c C_j^dag)]-w_s Tr[(C_j+C_j^dag)rho_c])dW_j`. This is Bayesian learning about the unchanged sector, not transitions between sectors. For a definite sector its weight remains1. An unresolved mixture need not collapse completely at the lowest power before higher-power observations are informative.

For a static bank in a definite theta sector, the Hamiltonian and dissipators reduce to independent local probe generators. With product probe preparation, separate outputs and a fixed reference schedule, their record laws factor conditional on theta and calibrated shared parameters; unconditional laws are generally correlated through theta. Adaptive schedules, shared uncertain reference parameters or correlated physical noise must instead use the full conditional joint law. Do not assume unconditional independent per-bit outcomes.

Freeze the future canonical objective as one joint likelihood `L(theta,nu)=P(Y_0,...,Y_(m-1),Y_ref|theta,nu)` with calibration nuisance parameters nu constrained by reference evidence, followed by a declared joint estimator/confidence set for theta. Marginalize or profile nu according to a predeclared rule; do not fit an unconstrained arbitrary offset per dyadic scale, which would make theta unidentifiable. No decoder is implemented or validated in Phase A.

Degeneracy of U_a is grouped at equal base eigenvalue. At power j, distinct base sectors may alias whenever `2^j(theta-theta')` is an integer. Multiple scales and both quadratures may resolve these aliases; this must be handled jointly. Each trial retains the same data; resetting |1> independently for each j destroys the persistent-sector contract. Probe reset alone is a local trace-and-prepare channel and preserves data sector populations, though it may dephase the data.

The ensemble diagnostic is a geometric sum: `r^(-1)sum_s exp(2pi i 2^j s/r)` equals1 if r divides2^j and0 otherwise. For diagnostic r=6 it is0 at every dyadic scale. Independent fresh-data averages therefore cannot stand in for same-sector records. Padding eigenvalue1 and other orbit degeneracies do not alter the |1> orbit result because the initial support and ideal dynamics never enter those spaces.

## A6. Phase accuracy and order-reduction contract — specification only

Use circular phase error initially, then unwrap to an ordinary interval with endpoint handling before applying continued fractions. On the success event require `|theta_hat-s/r|<1/(2N^2)`. Since the reduced fraction s'/q has q<=r<N, this is sufficient for its appearance as a continued-fraction convergent. This is a sufficient accuracy scale, not a guarantee of the measurement apparatus or a claim of minimal resource use.

A conditional scale-count argument is useful without establishing P3: suppose all m wrapped phases, measured in cycles, are each estimated within a common epsilon<1/6. Starting with the finest-scale estimate, recursively select the half-lift closest to the preceding-scale estimate. The correct half is selected because total comparison error is at most3epsilon/2<1/4, less than the midpoint between the two half-lifts. The base error is then at most epsilon/2^(m-1). Thus `2^m>4epsilon N^2` suffices. This is a mathematical consistency witness; the canonical estimator remains joint likelihood or a proved equivalent, not independent per-bit decisions. It does not establish that noisy fluorescence records satisfy the simultaneous error premise.

For example, fixed epsilon=1/8 permits m=2n as a conservative sufficient scale count. `m=2n+lambda` is allowed as extra resolution margin, but lambda does not automatically yield confidence1-2^-lambda. Confidence must come from a finite-record bound: if each required estimate fails with probability at most delta/m, the union bound gives failure at most delta without assuming independence. Calibration and reference errors must also fit that angular budget. No fixed finite record duration, optimal m, or general P3 success guarantee is frozen as proved.

A sample theta=s/r can reduce to s'/q with q=r/gcd(s,r). Zero phase gives denominator1 and may be uninformative; retain its probability and retry cost. Different complete trials may draw different s. Candidate denominator combination (for example LCM) requires a proved success event and independent modular verification. `a^R mod N=1` establishes an exponent multiple of the true order, not minimality. Do not perform exhaustive order search to repair a noisy record. For even verified R, calculate gcd(a^(R/2)-1,N) and gcd(a^(R/2)+1,N), reject trivial outputs and account for retries; successful order information does not guarantee successful factor extraction. P4/P5 and their retry statistics remain unproved here.

## A7. Resource profiles and synthesis boundary

**DP-P, primary:** one n-qubit data register, m probe systems, static simultaneous H_j, individually monitored outputs and explicit reference hardware. No dyadic arithmetic switching/compute-use-uncompute clock is required by this ideal model. LO quadrature modulation and data acquisition remain controls. No multi-probe implementation is authorized in Phase A or the initial Phase-B P0–P2 scope.

**DP-S, secondary:** reuse one or a few probes and retain the same data throughout a trial. Count probe resets, coupling switches, sequencing, repeated calibration, burn-in and accumulated measurement time. This variant cannot redefine the static-bank semantics or silently redraw theta.

For one multiplier, `W_c=|g><g| tensor I+|e><e| tensor U_c` is unitary and `H_c=g W_c(X tensor I)W_c^dag`; therefore `H_c^2=g^2 I` and ||H_c||=g. This is a circuit-mediated reference implementation, not native CPC synthesis. For the ideal bank, simultaneous diagonalization by sectors and independent probe eigenstates gives ||H_QND||=sum_j g_j; jump norm-squares sum to sum_j Gamma_j. Fixing every g_j while increasing m increases the total norm budget. Holding a total budget fixed can change probe contrast and record time.

Each H_j may act on the entire data register plus its probe. Constants c_j have a compact repeated-squaring algorithm, but that neither constructs local interactions nor removes controlled arithmetic/scratch costs. A literal2^j repetition of U_a costs2^j uses. Reversible multiplication by c_j is a different synthesis problem that must be counted. Finite dense/permutation matrices are exponentially large in n and are diagnostics, not efficient physical compilation.

A future ledger must separate: constant generation; multiplier and controlled-arithmetic synthesis; scratch and cleanup; interaction locality; rate/norm budgets; calibration precision/stability; probes and LO/reference; efficiency/bandwidth; mixing/burn-in; correlated record duration; inference time/memory; complete trials; modular verification and factor postprocessing. No polynomial complete physical-resource bound, physical TTS, hardware demonstration or advantage is established.

## A8. RFC-0010 mapping and proposed profile evidence

The accepted RFC remains unchanged. Its section20 permits a declared subset of conformance groups. A monitored QND profile must not impersonate a graph-preparation dark-state profile.

| Requirement | Frozen interpretation and evidence status |
|---|---|
| OS-1 | Ideal hardware stabilization is explicitly0; driven/damped measurement dynamics are the problem generator. No physical protection claim. |
| OS-2 | Canonical full register, residue invariant subspace and base spectral-projector definition. Proof projectors may be diagnostic; no semantic advice enters synthesis. |
| OS-3/OS-4 | Uniform arithmetic inputs only; exact compiled identities and forbidden-advice boundaries required. Finite prototype is evidence, not scalable synthesis. |
| OS-5/OS-6 | No protected violation-removal correction family is claimed. Terminal silence applies to that family under RFC section9; it is not a property of a continuously emitting probe. Mark not claimed with rationale, never passed by substituting a probe stationary state. |
| OS-7/OS-8 | No pure-dark semantic sector or Level-II equality of all fixed states with a graph target is claimed. Only sector-specific probe stationary response is proved. |
| DC-1..DC-3 | No encoded penalty/Lyapunov certificate claimed. |
| DC-4 | Exact single-sector transient exponents and critical case; distinct from phase-record inference time. |
| DC-5 | Ideal sector/residue population invariance; approximate physical leakage unbounded until measured or proved. |
| DC-6 | Separate complete cost ledger; physical fields unknown. |
| RR-1..RR-4 | Reference identity, transfer path, drift/calibration neighborhood and normalized monitored instrument mandatory for phase readout. Ideal specification supplied; physical records absent. |
| RR-5..RR-8 | Fixed estimator, decision/confidence region, robust separation and measurement error bounds required before robust readout claims. Not yet demonstrated. |
| OV-1..OV-4 | Raw admitted measurement records separate from posterior/latent diagnostics and semantic validation; realization labeled abstract/simulated, never physical by a hash or correct answer. |

Proposed **profile-level evidence additions**: instrument/unraveling identity distinct from GKSL identity; probe preparation and within-trial data continuity; output-to-probe mapping; LO schedule and transfer calibration; efficiency/noise covariance; reference record; sampling interval and filtering convention; raw record hash; conditioned-state method/likelihood identity; random seed/solver/discretization checks for simulation; burn-in/record window; stop/retry rules; common-sector/aliasing contract; confidence/error budget and attribution of any oracle-assisted diagnostics. A common GKSL generator can have inequivalent monitored observations, so generator identity alone is insufficient. These are candidates for explicit profile/schema extension, not a new accepted RFC or automatic RFC-0011. Compatibility with existing record types must be reviewed before conformance is claimed.

## A9. Acceptance criteria and present status

**P0 acceptance:** total permutation/padding; dyadic identity; pairwise multiplier and ideal H_j commutators; base-sector and residue invariance, each proved and independently checked on bounded fixtures. Status: algebraic proofs supplied; scratch evidence identifies exact tested cases.

**P1 acceptance:** normalized physical stationary state, phase signs/X/Y, full transient including critical case, phase-blind count control, calibrated two-quadrature identifiability and parameter limits. Status: derived; recovered 18-test prototype provides bounded supporting checks; independent Phase-A scratch checks supplement it without changing the prototype.

**P2 specification acceptance:** fully normalized SME and output law, distinction between state/record/diagnostics, same-sector update, actual reference protocol, finite-model future validation contract and honest open error bounds. Status: ideal measurement mathematics specified. **P2 success gate is not passed** until Phase B demonstrates bounded conditioned-record inference with a predeclared error/confidence criterion, numerical convergence and independent evaluation. A mean-response fit or an oracle-drawn phase cannot satisfy it.

Phase B must state a bounded test grid of single logical phases for reference-only validation, generate records from the full single-probe physical model without r/s advice, document the inference inputs, and independently assess coverage/error and failed/zero-information cases. It must not interpret this finite exercise as dyadic order finding. No two-probe dynamical bank, P3 common-theta decoder, order finder or hardware build is authorized by this specification.

Open items: finite-record confidence with correlated fluorescence and calibration uncertainty; robust estimator/numerical filtering scheme; approximate leakage and noise tolerance; evidence-schema integration; scalability and native synthesis; P3–P7. Primary-bank algebra does not resolve them.

**STOP HERE. HUMAN REVIEW OF P0–P2 FROZEN SPEC REQUIRED. NEXT RUN: PHASE B, GPT-6 ASTRA MEDIUM.**
