# P4 Phase D.1 — bounded-error order-recovery supplement v1.0

Status: frozen proposed normative supplement for HUMAN REVIEW; implementation is not authorized. The user has approved the amendment's scope, not a completed mathematical review of this artifact. Record review approval separately; do not manufacture it. No P4 PASS, stochastic records or P5.

Parent: Phase-D checkpoint SHA256 5875d441add29e222cf33a3fa782deefc3ff2bab4cde8b0ea1bcd6a2f4d1d137; unchanged original specification SHA256 0d09aee9c07a27eacef0190de904e3726783116891aa055e0df9024543c47cca. The original specification is the **P4-EXACT reference contract**. This additive supplement changes no original bytes or prior result. After human review, the pair (parent specification, supplement) governs the two explicitly named profiles. Wherever the parent requires deterministic minimality for every accepted output, that requirement continues to apply to P4-EXACT; P4-BE instead uses the distinct contract below. No silent guarantee substitution is permitted.

## 1. Common operational boundary

Retain N>=2, 1<=a<N, gcd(a,N)=1, B=N-1, answer-independent bounds, sanitized P3 inputs, the strict circular POINT radius rho_N=1/(2N^2), complete SET enumeration, exact arithmetic, fresh-preparation provenance, complete aggregation and fail-closed caps. The decoder receives neither true r/s nor factors/order tables/expected peaks. Diagnostic truth is used only after outputs are fixed. Error budgets and their justification must be registered before any experiment; a Boolean runtime claim that a budget is 'satisfied' is not itself evidence.

POINT returns at most one rational per admitted trial. No output, incomplete work or invalid provenance does not become a guessed denominator. For the primary fixed-k route, account for every predeclared trial; do not retain only favorably reconstructed or coprime sectors. Keep same-sector readout, dyadic channels and time windows distinct from independent fresh |1> preparations.

## 2. Two acceptance profiles

**P4-EXACT:** retain complete factorization of R; independent prime/product checks; a^R=1 mod N; and a^(R/p)!=1 mod N for each distinct prime p|R. Output **CERTIFIED_EXACT_ORDER**. This explicitly names the parent's CERTIFIED_ORDER status without modifying the archived contract. The exact soundness claim is conditional on correct integer arithmetic, certificate verifier and provenance implementation. Factor generation remains without a demonstrated general polynomial bound.

**P4-BE:** output **CERTIFIED_BOUNDED_ERROR_ORDER**, carrying the declared error contract, risk type, population, confidence allocation and all parent identities. Accept only when:

1. All required trial outputs and preparation records are admitted by the frozen profile rules.
2. Candidate enumeration/aggregation is complete, and the candidate state is unambiguous. POINT has one denominator per trial; SET retains the parent's complete-singleton aggregate rule.
3. 1<=R<=B and exact modular exponentiation verifies a^R mod N=1.
4. The predeclared, rigorously justified semantic-error budget is within the accepted limit; enclosure, provenance and implementation assumptions match that justification.

P4-BE does not factor R or test minimality with its prime factors. It makes a bounded-error semantic statement, not an unconditional deterministic certificate. Missing/unjustified error budgets produce UNVERIFIED_CANDIDATE/ABSTAIN even if a^R=1. It is never relabeled P4-EXACT. No P5 consumer may silently treat BE output as EXACT: the parent's exact-only P5 interface remains unchanged; any future P5 bounded-error composition needs separate authorization and risk propagation.

## 3. Divisibility theorem

Let r=ord_N(a). For trial i define G_i to mean that the operational denominator exists and equals r/gcd(s_i,r); an abstention may be counted as G_i failure under this convention. On G=intersection_i G_i, every q_i divides r. Prime valuations or the universal property of LCM then imply R=lcm(q_1,...,q_k) divides r.

For any positive integer R, divide R=ur+t with 0<=t<r. If a^R=1, then a^t=1, so order minimality forces t=0. Thus modular acceptance implies r divides R. On G both divisibilities hold and **R=r**. No factorization of R is used anywhere in this proof or its modular test.

Consequently an accepted wrong order is impossible on G for a correctly implemented POINT protocol, irrespective of whether the numerators are uniform, independent, or informative. Those assumptions are needed for success probabilities, not for this soundness implication.

SET extension: let E_i denote inclusion of the true reduced rational in the complete candidate set Q_i. On all E_i, the branch selecting each true rational survives aggregation: its LCM R_true divides r and is <=B. If the complete aggregate is the singleton {R}, then R=R_true. Modular acceptance again implies R=r. Thus SET can use true-fraction inclusion error bounds, without falsely asserting that every alternative denominator is correct. Its ambiguity and enumeration costs remain separate.

## 4. Wrong-accepted-order probability and risk semantics

Under correct arithmetic/protocol execution, wrong acceptance is a subset of union_i G_i^c. Therefore, if unconditional P(G_i^c)<=beta_i,

P(accept AND R!=r) <= min(1, sum_i beta_i).

No independence is needed. If G_i genuinely are mutually independent under the full model, a separately justified stronger bound is 1-product_i(1-beta_i). Fresh sectors alone do not establish this if reconstruction shares random calibration/nuisance or adaptive selection. Do not assume independence just to tighten the budget.

For SET replace beta_i by bounds on E_i^c, including the confidence-enclosure contract. A calibrated confidence set can justify inclusion probability; it does not automatically give POINT denominator correctness or uniqueness. The POINT sufficient event d_c(theta_hat_i,s_i/r)<rho_N implies G_i, but its probability must be proved/bounded for the actual acquisition and numerical model. P3-v1 PASS does not establish that general bound.

If unaccounted exceptional events H_num, H_enc, H_prov, H_impl have rigorously justified probabilities bounded by epsilon_num, epsilon_enc, epsilon_prov, epsilon_impl, add their sum once. If already included in beta_i, do not add them again. Deterministic exact integer arithmetic contributes no roundoff event in the mathematical model. Software tests alone do not justify an arbitrary numerical probability of implementation failure. Unbounded provenance/implementation risk must be stated as a validity assumption or cause rejection, not assigned an invented epsilon. Integrity failures observed at runtime fail closed.

These are **unconditional joint-event bounds per declared run**, not a posterior probability for a particular reported integer. In particular P(R!=r | accept) need not be <=sum beta_i. If P(accept)>=L>0 is separately established, the conditional risk is at most min(1, epsilon_total/L); otherwise report that conditional accepted-output risk is not bounded by the joint-risk number. Record this risk-type distinction in every BE output.

## 5. Ideal LCM and operational success

Define q_i^*=r/gcd(s_i,r) for all predeclared latent samples, whether or not their estimates succeed. For independent uniform fresh s_i, the preserved Phase-D theorem gives

P(lcm(q_1^*,...,q_k^*)=r)=P_ideal=product_{p|r}(1-p^(-k)).

Failure is <=sum_{p|r}p^(-k)<=3*2^(-k) for k>=2. This is an ideal sampling bound; it does not include measurement failure.

Important conditioning distinction: the product is the unconditional ideal-denominator law. It is also the law of an ideal experiment whose decoder is always exact. It is **not generally** P(LCM=r | all G_i), because estimation success can depend on sector. Counterexample: r=2,k=1 and an estimator succeeds only at s=0; conditioning on G selects the uninformative denominator 1 and gives success probability zero, although P_ideal=1/2. No change to the user's intended union-bound conclusion is necessary.

Let gamma bound remaining ambiguity/resource/noncompletion events that can prevent acceptance on ideal success and correct reconstruction. Keep gamma disjoint in bookkeeping from failures already charged to beta_i; mathematical independence is not required. Then

P(correct accepted order) >= max(0, P_ideal - sum_i beta_i - gamma - epsilon_extra).

Here epsilon_extra includes separately justified exceptional failure terms not counted above. For SET use inclusion failures and include unresolved singleton ambiguity in gamma. For POINT abstention is already G_i^c under the convention in section 3, so do not also charge the same abstention to gamma. When resource completion is deterministic within a proved bound, its gamma contribution is zero on the declared domain. If no bound on gamma is available, do not invent a positive success guarantee.

An answer-independent sufficient allocation for a desired total failure delta is to choose fixed k>=2 with 3*2^(-k)<=delta_LCM, and separately prove sum beta_i+gamma+epsilon_extra<=delta-delta_LCM. This is a symbolic design rule, not a frozen stochastic numerical threshold. Future power/error analysis must justify every numerical allocation before records.

Same-sector copies leave the denominator unchanged; they do not inherit the k-sample product. The fixed-k protocol is the primary BE route. Any bounded sequential extension must use a predeclared k_max and simultaneous/per-look error allocation. Wrong acceptance by any look is bounded by the union of reconstruction/error events used through k_max, not by reusing a fixed-time beta at each adaptive stop. No truth-based stopping or trial deletion is permitted.

## 6. Corrupted-denominator controls

Corrupted denominators can pass the modular check with a wrong multiple, which is exactly why BE is a risk contract:

- N=7,a=2 has diagnostic r=3. A corrupted POINT result 1/6 yields R=6<=B and 2^6 mod 7=1. BE's modular subtest passes, while R is wrong and G is false; EXACT rejects minimality.
- N=15,a=2 has r=4. A corrupted 1/8 result gives R=8<=14 and 2^8 mod 15=1; again a wrong accepted multiple is possible only outside the reconstruction-correct event under the stated protocol.

These examples do not license accepting an arbitrary denominator without a valid preregistered budget. They are adversarial mathematical controls, not stochastic error-rate estimates. No P5 factor extraction is performed.

## 7. Separated resource analysis

For P4-BE-POINT, let L bound encoded phase precision, n=ceil(log2 N), k the fixed fresh-trial count, and H total admitted metadata/provenance input length. Three exact CF expansions per sample use O(L) Euclidean steps on polynomial-size integers. Canonicalization/filtering retains at most one denominator <=B. Incremental LCM uses k gcd operations; before rejecting an LCM above B, the product of two admitted values is at most B^2 and has O(n) bits. Modular verification uses O(n) modular multiplications with O(n)-bit residues. Candidate R is not factored.

Thus the **classical P4-BE-POINT reconstruction and modular-verification route is polynomial in k, L, n and H**, conditional on supplied sufficiently accurate, authenticated P3 phase objects, a valid predeclared error contract, and the specified finite exact arithmetic. If L and H per trial and k are polynomial in n and the requested security/accuracy parameters, this postprocessing is polynomial in those parameters. k=O(log(1/delta_LCM)) controls ideal denominator diversity, not noisy reconstruction. Cost of validating a fixed registered error-contract identity is counted in H; deriving an arbitrary new error theorem is not assumed algorithmically free.

This does not hide P3 record processing: if P4 must itself read/hash B_raw bytes of retained evidence, add Omega(B_raw) work. P3 likelihood fitting, acquisition duration, preparation/measurement cost, numerical precision needed to deliver the objects, and error-analysis construction are separately accounted upstream. No polynomial physical CPC resource conclusion follows from the conditional classical result.

P4-BE-SET still has Theta(N^2) worst-case explicit rational output for broad sets, and the complete LCM-state work of the parent. Removing candidate factorization does not remove that output-size obstruction. Compact set representations require separately proved complete algorithms. Ambiguity, inclusion enclosure and noisy trial counts remain open. P4-EXACT retains its candidate-factorization/certificate-generation bottleneck; it is not evidence that BE-POINT is non-polynomial.

The full vector (T,S,P,E,C,M,V) remains mandatory: count classical/bit/provenance costs, storage, O(N^-2) sufficient phase accuracy, inherited physical energy/acquisition, fixed/adaptive control, genuinely fresh trials, and independent validation. No exact factorization term belongs in BE's required V; modular verification and error-contract validation do.

## 8. Gate and evidence amendment

Preserve P4-A–F and P4-I–K. Split G into **P4-G-EXACT** (complete deterministic minimality certificate) and **P4-G-BE** (denominator-divisibility implication plus modular check and rigorously registered risk contract). Add **P4-L — claim-type separation**: schema/status/risk/certificate fields must distinguish the profiles; no BE output can satisfy an EXACT-only consumer.

P4-H remains strongest for EXACT: wrong divisors/multiples must never be deterministically certified. For BE, explicitly test wrong divisors rejected by modular verification and corrupted proper multiples that can pass it; they must never be labeled EXACT and must be accounted by the reconstruction-error bound. It would be mathematically false to demand deterministic rejection of every wrong multiple from BE's modular subtest. P4-K reports conditional BE-POINT polynomial postprocessing separately from EXACT certificate generation and explicit SET costs.

A BE sidecar must bind claim_type, status, parent/amendment/decoder identities, fresh-preparation ledger, candidate and modular-residue evidence, risk_type='unconditional_wrong_acceptance_per_run', bound and its population/assumptions, beta/gamma/exceptional-event bookkeeping, numeric enclosure and completeness, and independent validation. EXACT additionally binds prime/product/minimality evidence. Hashes alone do not prove risk or correctness. Neither sidecar upgrades RFC-0010 realization, readout or RR evidence; no RFC-0011 is introduced.

## 9. Deterministic verification

The bounded check script passed 52,836 assertions over all units 2<=N<=25 with two exact-sector samples, the four mandatory fixtures, corrupted proper multiples, exact finite-population error/success bounds, fresh-sector probabilities, same-sector copies, and the SET true-path extension. No stochastic records or production P4 decoder were created. The unchanged Phase-D checks were not rerun.

## 10. Freeze, implementation boundary and nonclaims

The revised implementation prompt must retain both authoritative policies verbatim, require both distinct profiles, and prohibit mathematical changes to make tests pass. New stochastic acceptance, power/error analysis, source/dependency seals, human execution GO and autonomous terminal reporting remain mandatory. No implementation or stochastic record is produced by this amendment.

The original Phase-D specification and checkpoint remain immutable. The old implementation prompt is preserved byte-for-byte; its revised working version is the sole authorized revision to an existing document. The amendment's reviewed normative status requires subsequent human review. Current checkpoint status is **PHASE D.1 FROZEN FOR HUMAN REVIEW**, not an assertion that review occurred.

Retain **P3 PASS — bounded finite model only**. No P4 PASS, general scalable order finding, factoring, scalable/native physical realization, physical TTS, robust RR or matched-confidence advantage. Multiplication-tree remains constraint-description-only; P2 bounded-only; Attempt 1 permanently FAILED. STOP for human review before implementation.
