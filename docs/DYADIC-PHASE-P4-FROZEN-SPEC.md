# CPC-Shor Phase D: P4 order-reconstruction specification v1.0

Status: derivation-only specification, normative only when included in the verified FINAL Phase-D checkpoint. This is NOT P4 PASS, a stochastic acceptance plan, implementation authorization, or P5 authorization. Scope: bounded exact reference design with explicitly OPEN scalability and measurement-resolution gates. Human review is required before implementation.

The immutable baseline is **P3 PASS — bounded finite model only**. All P0–P3 source, records, results, thresholds and checkpoints remain unchanged. BASELINE.json binds the six supplied P3 identities, HEAD/main b9f8820cef9d7ca3d77c7e68199ec869720cb8b9, branch shor-rfc0010-prototype and unchanged index. No Git mutations or FPGA operations are allowed.

## 1. Operational contract and advice boundary

Admissible input: integers N>=2, 1<=a<N, gcd(a,N)=1; a declared P3 phase object; fixed decoder profile and resource policy; and provenance establishing which records belong to distinct fresh preparations. Set B=N-1 and n=ceil(log2 N). Since ord_N(a) divides the finite unit-group cardinality, 1<=r<=phi(N)<=B. The decoder does not compute phi(N) or r to choose its bounds.

The phase object is a sanitized, versioned object containing only: exact maximum-likelihood grid index/grid size (or exact rational encoding of the declared stored estimate); a finite union of global confidence arcs; their numerical enclosure contract; confidence level/method identity; raw-record, P3 inference, source and profile hashes; and preparation identity. Likelihood arrays may be retained for audit, but the profiles below do not use truth or perform a new likelihood fit. P3 ties retain the frozen smallest-index rule. No new spectral grid is fitted to the order.

Forbidden operational inputs: true r or s; factors of N; expected denominators/convergents/peaks; diagnostic final ket or diagnostic sector; order tables; truth-selected lifts; and retry choices based on truth. Reject unknown semantic fields at the adapter. Do not pass entire P3 summary JSON, since it contains diagnostic truth. Preparation IDs and opaque hashes cannot serve as lookup keys into order tables. Inputs, source and outputs must be frozen before independent diagnostic truth is compared.

Proposed signatures (normative interfaces, not production implementation):

- `decode_point(N, a, phase_view, policy)`
- `decode_set(N, a, phase_view, policy)`
- `aggregate(N, a, candidate_views, preparation_views, policy)`
- `certify_order(N, a, candidate_R, policy)`
- `verify_order_certificate(N, a, candidate_R, certificate)`

Certificates may contain internally obtained factors of **candidate R**, with independently checked primality/product witnesses; these are not factors of N supplied as advice. No external factorization oracle is silently admitted. Freeze policy before diagnostic comparison. Signature deny-lists alone are insufficient: schema allow-lists, dependency/import checks and adversarial diagnostic-label replacement are also mandatory.

## 2. Rational reconstruction theorems

Write d=gcd(s,r), p=s/d, q=r/d; for s=0 use p/q=0/1, including r=1. A phase determines the reduced fraction p/q, not generally r.

**Legendre criterion.** If gcd(p,q)=1, q>=1 and |x-p/q|<1/(2q^2), then p/q is a regular continued-fraction convergent of x. Finite rational inputs use exact Euclidean arithmetic and the canonical finite expansion (last term >=2, except integers); endpoint equality is not covered by the strict theorem.

Proof route: a reduced noninteger p/q has the two finite continued-fraction expansions. Their predecessor denominators v and q-v lie strictly between 0 and q. The two cylinders where p/q is a convergent extend from p/q on its two sides to the mediants with those predecessors. Their distances from p/q are 1/[q(q+v)] and 1/[q(2q-v)], both greater than 1/(2q^2), using determinant magnitude one for adjacent convergents. Thus the stated open neighborhood lies inside their union. Rational endpoints within that open neighborhood are covered by the finite Euclidean expansions too. For q=1, an integer within distance <1/2 is either the integer-part convergent or the following denominator-one convergent. This also handles negative real lifts.

Consequently |x-s/r|<1/(2r^2) implies the criterion for reduced p/q, since q<=r. The stronger **answer-independent** radius rho_N=1/(2N^2) suffices for all admissible orders. This is a sufficient condition, not a measured accuracy guarantee inherited from P3.

**Separation and neighborhood uniqueness.** Distinct reduced rationals with denominators <=B have circular separation at least 1/B^2: the difference after any integer lift has nonzero integer numerator over qq'. Therefore an arc of diameter <1/B^2 contains at most one such rational. In particular the open circular rho_N-ball has at most one, since 2rho_N=1/N^2<1/B^2. A narrow component in a multimodal union does not establish uniqueness of the whole union.

For a closed declared confidence set C, completeness means containing every reduced p/q in C, not selecting a nearby mode. True-fraction inclusion follows only on the event theta in C. Coverage alone does not establish precision or uniqueness.

Odd/even r changes neither theorem. Repeated reduced denominators add no new prime powers. For r=6, s=0,1,2,3,4,5 give q=1,6,3,2,3,6. One denominator 2 or 3 is not order 6. Zero phase is uninformative about the missing cofactor except when separate arithmetic certifies order 1.

## 3. Circular and numerical conventions

Use the fixed cut at 0, with phases in [0,1); d_c(x,y)=min_{h in Z}|x-y-h|. Never rotate the cut using truth. Split wrap-around arcs at 0/1; closed endpoint 1 is also 0. Canonical rationals satisfy 0<=p<q, q>=1, gcd(p,q)=1. Canonicalize 1/1 to 0/1 and deduplicate exactly. A full circle and an empty set have different explicit encodings.

Stored floating endpoints are converted to exact binary rationals without decimal rounding. The adapter may instead receive outward certified rational endpoint intervals. A fixed nonnegative rational numerical enlargement epsilon is part of the policy; epsilon=0 is the deterministic reference default for the **declared stored set**, not a proof about an ideal real-arithmetic set. C_plus is the closed circular epsilon-neighborhood of that declared set. Reject NaN, infinity, malformed or unbounded endpoint encodings. Merge overlapping/touching arcs; retain isolated points. Any relation to an underlying ideal P3 confidence set needs a separately justified outward error budget. Numerical enlargement cannot be tuned after seeing truth.

## 4. Canonical decoder profiles

### P4-CF-POINT

Let x be the frozen P3 ML estimate reduced modulo 1. Compute all convergents of x+h for h=-1,0,1, canonicalize them modulo 1, retain q<=B and d_c(x,p/q)<rho_N, and deduplicate. All three lifts are processed, not selected by truth. Return the entire retained set, of size at most one by separation. If empty, return INSUFFICIENT_PHASE_RESOLUTION; an empty list does not imply absence of an order. No nearest-denominator fallback is allowed.

Legendre and the lift convention imply inclusion of the true reduced rational when d_c(x,s/r)<rho_N. This event has no automatic probability bound from P3-v1 PASS. A 512-point ML grid stays exactly that grid; it is not silently refined. For nearest-grid rounding alone, 1/(2G)<rho_N requires G>N^2 as a sufficient uniform condition. Noise/model error consumes additional budget. Exact alignment can succeed at smaller G, but is not a uniform guarantee. Representation precision needs about 2 log2 N bits; the physical/simulated cost of attaining such accuracy remains open.

### P4-CF-SET

Return exactly Q(C_plus,B)={p/q:0<=p<q<=B, gcd(p,q)=1, p/q in C_plus}. A bounded reference enumeration loops q=1..B and p=0..q-1 with exact gcd/membership checks; it returns every candidate, including 0/1 when appropriate. An optimized Farey/Stern–Brocot or interval-CF traversal may replace this only after equivalence and completeness proofs. Point convergents alone are not a complete set enumerator.

Sort output by rational value, then denominator/numerator for deterministic serialization. If the enumeration resource cap is reached, return ENUMERATION_INCOMPLETE with the partial set explicitly marked incomplete, never a falsely complete singleton. The reference is exact and finite but worst-case exponential in n. The full circle contains 1+sum_{q=2}^B phi(q)=Theta(B^2) rationals; explicit output itself prevents a general polynomial-in-n implementation. A compressed representation would be a new design requiring separately proved downstream algorithms, not a silent replacement of this explicit-output contract.

## 5. Aggregation, ambiguity and conservative acceptance

Each admitted trial supplies the **complete** candidate set Q_i, or an explicit incomplete/failure status. Candidate numerator choices remain in evidence; aggregate by their denominator sets D_i. For k trials set S_0={1} and

S_i={lcm(R,q):R in S_{i-1}, q in D_i, lcm(R,q)<=B}.

Deduplicate and sort ascending; preserve a canonical predecessor witness and hash the full stage sets. Pruning >B is sound because subsequent LCMs never decrease. This is union over all compatible choices, **not** the LCM of every alternative within one trial. Empty D_i makes the batch unsuccessful; it is not silently discarded. Incomplete enumeration/aggregation cannot support an exact-order acceptance.

Conservative primary rule: only if the complete final S_k is a singleton {R} may the decoder attempt exact certification of R. |S_k|>1 returns AMBIGUOUS_CANDIDATES. The protocol does not search every alternative arithmetically until it finds r. This avoids disguising a broad/full-circle input as successful phase-information recovery via exhaustive classical order search. Even if one ambiguous branch is certifiable, this primary profile abstains. An arithmetic-dominated baseline would require a separately named profile and cannot count as primary phase-information success.

A singleton without a certificate is CANDIDATE_ORDER, not an accepted exact order. Distinguish EMPTY_PHASE_CANDIDATES, INSUFFICIENT_PHASE_RESOLUTION, ENUMERATION_INCOMPLETE, AGGREGATION_INCOMPLETE, AMBIGUOUS_CANDIDATES, VERIFICATION_FAILURE, CERTIFICATION_INCOMPLETE, and CERTIFIED_ORDER. Detail reasons include nonmultiple, nonminimal multiple, or malformed certificate. Diagnosis of actual denominator-divisor loss uses truth only after inference; operationally a failed singleton modular test may have several causes.

## 6. Single-sample limitations and certification

Searching q,2q,...,floor(B/q)q is answer-independent but costs Theta(N/q) modular tests in the worst case, exponential in n when q is small, especially q=1. Modular exponentiation is efficient per test; it does not supply the unknown cofactor in polynomial time. A fixed poly(n) multiple cap is a bounded heuristic with unproved general completeness, not a cure. If q truly divides r, the first successful multiple in exhaustive increasing order equals r; without that unverified premise it is lcm(q,r), potentially larger than r. This search is analyzed, **not adopted** by the primary profiles.

For a candidate R, a^R mod N=1 iff r divides R. This is an order-multiple witness, not exact-order certification. A complete prime factorization R=product ell^e gives the exact certificate:

1. Validate 1<=R<=B, positive exponents, distinct prime ell, and exact product R.
2. Independently verify primality, not merely probable-prime labels.
3. Verify a^R mod N=1.
4. For every distinct ell|R verify a^(R/ell) mod N !=1.

Proof: if r|R but r<R, choose a prime ell dividing R/r; then r|R/ell, contradicting step 4. Conversely if R=r each proper divisor R/ell fails. For R=1 the factor list is empty and a mod N=1 suffices.

The bounded reference obtains factors of R internally by complete trial division, including the final residual, and uses exact deterministic primality checks. At most O(sqrt(R)) trial divisions are required; this is exponential in n, even though R<N. Budget exhaustion returns CERTIFICATION_INCOMPLETE. A polynomial-time primality verifier exists, but does not factor R or generate the certificate. Factoring rational denominators is not free because their integer values are explicitly known; storing factorizations only helps after obtaining them. LCM factor maps are cheap once those factorizations exist.

Gcds between candidate integers reveal some common factors, not necessarily a complete prime factorization; one candidate alone exposes the unresolved case. Given a multiple and its complete factors, repeated modular tests can reduce it to r; a partial factor list cannot certify minimality. An alternative exhaustive check a^t!=1 for all 1<=t<R avoids factoring but costs O(R) group operations and has an exponentially long certificate/transcript. Neither route supplies a general polynomial complete-resource bound here.

If exact recovered denominators are externally **proved** to divide r, their LCM divides r, and a^R=1 proves equality without factoring. No noisy operational confidence object supplies that exact divisibility premise. Treating it as true would turn a probabilistic phase inference into an unsound unconditional certificate. The primary acceptance rule therefore keeps independent minimality certification.

Conclusion: bounded single-sample exact recovery is possible when the retained candidate actually equals r and certification completes. General polynomial-time one-sample exact recovery is **not established by this design**. This is not an impossibility theorem about all algorithms.

## 7. Fresh-sector LCM theorem and probability

For ideal fresh independent |1> preparations, the orbit basis gives |1>=r^(-1/2)sum_s |u_s> up to phase convention. Sector-preserving measurement effects make the record law a classical mixture with uniform latent s; full collapse is unnecessary for this statement. Independent preparation/noise/reference draws give independent latent s_i. P3's finite fixture validation does not prove arbitrary-N preparation, independence or precision.

Let q_i=r/gcd(s_i,r) be **correctly reconstructed** denominators. For r=product_{p|r}p^{e_p},

v_p(q_i)=e_p-min(v_p(s_i),e_p), with v_p(0)=infinity.

Thus q_i retains the full p^{e_p} exactly when p does not divide s_i. Therefore R_k=lcm(q_1,...,q_k)=r iff every prime p|r fails to divide at least one s_i; equivalently gcd(s_1,...,s_k,r)=1. Missing primes may be supplied by different samples; no individual numerator need be coprime to r. Example r=6, s_1=2,s_2=3 yields q_1=3,q_2=2 and LCM 6.

For uniform independent numerators, failure event A_p means all k are divisible by p, with probability p^(-k). For any prime subset J, CRT gives P(intersection_{p in J} A_p)=(product_{p in J}p)^(-k). Inclusion–exclusion hence yields the exact formula

P(R_k=r)=product_{p|r}(1-p^(-k))
 =sum_{d|rad(r)} mu(d)/d^k.

This is not [phi(r)/r]^k or the probability that any one numerator is coprime. The union bound is P(failure)<=sum_{p|r}p^(-k)<=omega(r)2^(-k)<=n2^(-k). For k>=2 it is also <=sum_{m=2}^infinity m^(-k)<=2^(-k)+2^(1-k)/(k-1)<=3*2^(-k). Operational choice k=max(2,ceil(log2(3/delta))) suffices for ideal denominator recovery with failure <=delta, independent of the unknown r. Empty products give success 1 for r=1.

Define ideal T=min{k>=1:R_k=r}. For r>1, E[T]=1+sum_{k>=1}[1-product_{p|r}(1-p^(-k))]. The k=1 term is <=1; summing the k>=2 union bound over all integers m>=2 gives sum_m 1/[m(m-1)]=1, so E[T]<=3 (strictly <3 for finite r>1). This ideal sample count excludes phase-resolution failures, decoder ambiguity, certification cost and physical duration. It is not an operational P4 performance claim.

If G_i denotes correct singleton reconstruction, P(any G_i fails)<=sum beta_i implies P(certified success)>=product(1-p^(-k))-sum beta_i, **only if resource completion and certification are guaranteed**. No independence between G_i and s_i is assumed; use an unconditional union bound, not a false uniformity claim conditioned on successful estimation. With extra resource-failure probability gamma subtract gamma. Set coverage with failure alpha_i guarantees true rational inclusion with union failure <=sum alpha_i, but does not guarantee singleton sets or singleton aggregate. An additional ambiguity/noncompletion term is necessary. P3 PASS alone supplies none of these P4 beta/ambiguity guarantees.

Repeated measurements/windows of one retained sector refine one s/r; they do not change gcd(s,r) or supply new numerators. Dyadic j=0,1,2 channels in one P3 trial share the same s. Repeated copies of one denominator have LCM q forever. Fixed-sector diagnostics and P3 fresh-data negative controls are not eligible common-theta operational order trials. Freshness must be established by preparation evidence, not merely different filenames.

## 8. Retry and confidence bookkeeping

Primary reference policy is fixed-k: preregister k and execute exactly k genuinely independent fresh-sector trials, including unsuccessful/ambiguous ones in accounting. Do not sample until diagnostic truth agrees. No new records are authorized in Phase D.

A future bounded sequential variant may stop at the first independently CERTIFIED_ORDER, or at k_max/resource failure, with deterministic tie/order rules. It must retain all consumed evidence. Wrong-order probability is zero under exact certificate arithmetic, independent of optional stopping. This does not make phase confidence intervals anytime-valid. Preallocate per-look error alpha_i with sum<=alpha (for example alpha/[i(i+1)]), or prove a confidence-sequence guarantee before making sequential confidence claims. Repeated looks at a single record require their own simultaneous coverage justification.

Under ideal exact-denominator inputs, certification completion and the singleton rule, the event of success by k_max has the same LCM formula as fixed k_max: couple to the unused fresh trials of a predeclared ledger, with early certified success latched. Under noisy or ambiguous inputs, subtract the reconstruction/ambiguity/resource terms justified for the actual rule. An empty candidate-set batch may terminate as failure; silently replacing its trial is forbidden. Any additional batch/retry policy requires its own preregistration, caps, confidence allocation and complete cost accounting.

## 9. Proposed gates, not stochastic acceptance thresholds

| Gate | Deterministic requirement / later empirical obligation |
|---|---|
| P4-A | Sanitized operational schemas and signatures reject semantic advice; no truth imports or fixture/order lookup. |
| P4-B | Exact rational neighborhoods strictly within rho_N include the correct reduced rational via CF, including circular and zero cases. |
| P4-C | SET equals exact bounded rational enumeration; wrap, endpoints, disjoint modes and incomplete outputs handled without false completeness. |
| P4-D | Every diagnostic gcd case records q=r/gcd(s,r); q is never automatically certified as r. |
| P4-E | Fresh-trial denominator alternatives aggregate by the stated LCM set recurrence, with witnesses and complete status. |
| P4-F | Exact enumeration agrees with product and inclusion–exclusion probabilities; general theorem remains conditional on uniform fresh sectors and correct denominators. |
| P4-G | Independently checked minimality certificate required for accepted exact order; incomplete factoring abstains. |
| P4-H | Wrong divisors and nonminimal multiples, malformed factor maps and pseudoprime labels cannot be accepted. |
| P4-I | Broad/multimodal inputs preserve ambiguity; no arithmetic search across alternatives masquerades as phase information. |
| P4-J | Same-sector repetitions, dyadic channels and duplicate preparation identities do not count as new numerator draws. |
| P4-K | Report all candidate counts, bit lengths, arithmetic calls, factor work, memory and caps. Bounded reference is defined; general polynomial complete-resource scalability remains OPEN. |

Later numerical acceptance thresholds, trial counts, sampling/error models and power analyses must be separately preregistered, hashed, reviewed and sealed before stochastic evaluation. No P4-ACCEPTANCE.json or P4 PASS is created here. Failure and abstention rates must be distinct from wrong certified orders, and arithmetic-dominated baselines distinct from successful phase-information recovery.

## 10. Mandatory bounded fixtures and deterministic scope

- N=7,a=3, diagnostic r=6: all s, q in {1,2,3,6}, complementary 2/3 denominator samples, duplicates and zero.
- N=7,a=2, diagnostic r=3: odd order, zero and nonzero sectors.
- N=5,a=2, diagnostic r=4: powers of two and denominator loss.
- N=15,a=2, diagnostic r=4: composite N and gcd(a,N)=1. **No P5 gcd extraction is executed.**

Truth is computed by an independent diagnostic enumerator after operational functions are defined, and used only to construct/check synthetic mathematical fixtures. Synthetic neighborhoods are not stochastic P3 records or evidence of P3 precision. Deterministic probes are research scripts outside frozen P0–P3 production sources, not the final P4 implementation. Counts and exact ranges are recorded in DETERMINISTIC-CHECKS.json: 12 methods and 22,802 exact predicate/rejection assertions passed, including 7,025 strict CF neighborhoods, 184 SET/Farey comparisons, 12,621 certificate-vs-order comparisons and 48 exhaustive product/inclusion–exclusion cases. These are bounded deterministic checks, not stochastic P4 acceptance.

## 11. Complete resource vector C(R)=(T,S,P,E,C,M,V)

Use L for phase-endpoint bit length, b for interval count, m_i for rational candidate count, c_i=|S_i|<=B, k for fresh trials and D for a fixed elementary-operation budget.

T: Euclidean CF and gcd take polynomial time in input bit length; O(L) CF steps with polynomial-size integers is a safe bound. Point profile is polynomial in L+n. LCM of k single integers has bit length <=kn without pruning and <=n in the bounded state sets; Euclidean arithmetic and modular exponentiation (O(n) modular multiplications for exponent <=B) are polynomial per operation. The straightforward set enumerator uses O(B^2) gcd/membership work, times polynomial endpoint cost and b; output-sensitive Farey methods do not remove the Omega(B^2) full-circle output lower bound. Aggregation uses O(sum c_{i-1}|D_i|) LCM computations (<=O(kB^2) after denominator deduplication), exponential in n despite avoiding a naive Cartesian-product representation. Trial division costs O(sqrt(B)) divisions per candidate, not polynomial in n. Certificate verification with proven primes can be polynomial given the certificate, but production is not shown polynomial here.

S: point CF can use polynomial workspace; explicit set storage is O(m_i(n+L)) bits, aggregated states/witnesses O(kB(n+L)) conservatively. Streaming enumeration reduces transient memory, not total work/output. Preserve and charge raw P3 storage separately.

P: sufficient point accuracy O(N^-2), approximately 2n bits plus error margin; interval endpoint exactness/enclosure and all multiprecision integer costs must be counted. Bit precision is not a bound on measurement time needed to achieve it.

E: no new physical-energy estimate. Inherit P3 measurement/preparation cost as a separate, unproved-scaling component.

C: fixed-k or explicitly bounded sequential classical control; charge serialization, hashing and confidence allocation; no truth-based stopping.

M: exactly the number of independent fresh |1> preparations. Channels, windows and same-sector refinements do not inflate it. Ideal k=O(log(1/delta)) does not account for noisy resolution/ambiguity failures.

V: independently check all modular residues, factor/product/primality evidence, inclusion completeness and provenance. Include any reference order enumeration separately as validation-only cost, never hide it inside the operational routine.

Resource policy fields (bit length, q-visits/candidate count, LCM calls, trial divisions, memory, deadline, k/k_max) must be fixed before execution; zero/finite caps fail closed. A cap never authorizes truncating alternatives and calling the output complete. Future stochastic acceptance chooses numerical caps after a power/error and resource analysis, not in this derivation.

**Open gates:** general P3 precision/preparation/independence scaling; explicit rational-set output explosion; candidate/certification work; ideal-to-noisy success transfer. Not every essential P4 step has a polynomial complete-resource implementation in log N. No mathematical impossibility of all alternative designs is asserted. The frozen contract supports a bounded implementation only after human review; it does not resolve the scalable research question.

## 12. RFC-0010 sidecar mapping

Use proposed `cpc-shor-p4-profile/1` as a classical semantic reconstruction sidecar alongside the existing `cpc-shor-p3-profile/1`; no RFC-0011 or modification to RFC-0010 is justified here. Preserve representation != realization != readout != semantic correctness.

Bind separate content identities for: P3 raw record and channel/preparation profile; P3 likelihood/confidence and its enclosure contract; P4 spec/decoder source/policy; each exact rational candidate set with complete flag; fresh-preparation ledger; each aggregation stage and witness; arithmetic/minimality certificate; and independent validation. Domain-separate schema/kind tags and hash canonical, sorted serialization with explicit rational numerator/denominator integers, no NaNs. Reject missing parents and conflicting identities. Hashes establish provenance, not truth.

OS/DC claims remain the unchanged P3 evidence. P4 does not manufacture a new dissipator, external reference, native realization or RR result. Sidecar readout lineage supports OV-1 provenance; answer separation and independent semantic validation support an OV-4-associated evidence link; classical resource counts are separately identified alongside DC-6 accounting. These associations are evidence links, not automatic satisfaction of any RFC requirement. Each method/evidence identity is requirement-specific; do not reuse a generic 'validated' flag. An accepted semantic certificate is a distinct classical claim, not physical conformance.

## 13. P5 interface, definitions only

Only CERTIFIED_ORDER may be passed to a future P5 consumer, with N,a,r, certificate and provenance. The future consumer checks even r and x=a^(r/2) mod N. Odd r gives ODD_ORDER/RETRY; x=-1 gives TRIVIAL_MINUS_ONE/RETRY. An exact even order excludes x=1. Otherwise candidate factors gcd(x-1,N), gcd(x+1,N) must be checked as nontrivial divisors; for general composite N do not promise that they are distinct primes or form an exact complementary pair without checking. Define USABLE_ORDER, NONTRIVIAL_DIVISORS, VERIFIED_FACTOR_PAIR, and RETRY distinctly. No factoring success counts toward P4; no such P5 computation is executed here.

## 14. References and frozen boundary

Legendre's convergent criterion is standard; the self-contained proof above fixes the strict/circular conventions used here. Primary mathematical reference: Dominique Barbolosi and Hendrik Jager, “On a theorem of Legendre in the theory of continued fractions,” https://jtnb.centre-mersenne.org/item/10.5802/jtnb.106.pdf. Shor's order-finding discussion separates reduced denominators and repeated samples: https://arxiv.org/abs/quant-ph/9508027. Polynomial primality testing does not solve integer factorization: Agrawal–Kayal–Saxena, https://annals.math.princeton.edu/2004/160-2/p12. The product probability, confidence-transfer qualifications and bounded-profile rules here are explicitly derived above; these sources are context, not claims that this CPC model inherits Shor's complete complexity bound.

No P4 PASS, general order recovery, rational reconstruction performance guarantee, factoring, native synthesis, scalable CPC-Shor, physical realization/TTS, robust RR or matched-confidence advantage is established. Multiplication-tree remains constraint-description-only; P2 is bounded-model-only; Attempt 1 remains permanently FAILED. Human review must resolve the bounded implementation scope and acknowledge the open scalability gates. STOP before implementation or P5.
