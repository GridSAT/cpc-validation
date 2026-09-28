# MS-DP-P E3 Calibration Amendment v2

**Status:** deterministic prerecord amendment  
**Applies to:** E3-P final stochastic prerecord only  
**Execution authorization:** none  
**Run identity:** unassigned  
**Stochastic records generated:** 0  
**P4-v4:** untouched

## 1. Reason for amendment

E3-D v1 proposed one pooled finite-model calibration population with

\[
n_{\rm cal}=1024,\qquad X_{\rm cal}\le 1,
\]

conditional on a deterministic proof that every admitted local phase and
dyadic scale has the same finite-window error law.

E3-Ib established the multiscale DP-S acquisition adapter and the local
matched-reference estimator, but did **not** establish phase-independence of
the complete finite-window, time-multiplexed two-quadrature error law.

Therefore the single pooled calibration population is not admitted for E3-P.

This amendment does not weaken any scientific threshold. It increases
calibration coverage and tightens the per-cell acceptance count.

## 2. Exact local phase classes in the frozen fixture family

For a diagnostic order \(r\), sector \(s\), and dyadic scale \(j\),

\[
\phi_{r,s,j}=2^j s/r \pmod 1.
\]

The frozen fixtures are:

- \(N=5,a=2,r=4,J=3\);
- \(N=7,a=2,r=3,J=4\);
- \(N=7,a=3,r=6,J=4\);
- \(N=15,a=2,r=4,J=6\).

Across all sectors and all admitted scales, the exact union is

\[
\Phi_{\rm cal}
=
\left\{
0,\frac16,\frac14,\frac13,\frac12,\frac23,\frac34,\frac56
\right\}.
\]

There are exactly eight calibration phase classes.

## 3. What may still be pooled

For a fixed local phase \(\phi\), the sector-restricted signal Hamiltonian is

\[
H(\phi)
=
g
\begin{pmatrix}
0 & e^{-2\pi i\phi}\\
e^{2\pi i\phi} & 0
\end{pmatrix}.
\]

The dissipator, efficiency, timestep, burn, retained window, LO schedule, and
matched-reference law are otherwise independent of \(N\), \(r\), \(s\), and
\(j\).

Hence occurrences with the **same exact \(\phi\)** reduce to the same local
finite instrument. Pooling across \(N,j,s\) is admitted only within one exact
phase class.

No pooling is made across distinct values of \(\phi\).

## 4. Local error boundary

Retain the frozen local-channel target

\[
p_\star=\frac1{140},
\qquad
\delta=\frac18.
\]

A calibration error is

\[
d_{\mathbb T}(\widehat\phi,\phi)>\frac18.
\]

## 5. Per-phase calibration gate

For each of the eight exact phase classes, freeze

\[
n_{\rm cell}=1024,
\qquad
X_{\rm cell}=0.
\]

Thus E3 calibration passes only if **all 8192 diagnostic local acquisitions**
contain zero local errors.

At the boundary \(p_\star=1/140\),

\[
\Pr[X_{\rm cell}=0]
=
\left(\frac{139}{140}\right)^{1024}
\approx 6.487045225\times10^{-4}.
\]

Using a conservative union bound over eight separately admitted phase classes,

\[
\Pr(\text{any bad phase class falsely admitted})
\le
8\left(\frac{139}{140}\right)^{1024}
\approx 0.00518963618
<
0.01.
\]

The global event that all eight cells pass while at least one cell has
\(p>1/140\) has an even smaller worst-case bound, but E3-P freezes the
conservative union bound above.

## 6. Operational risk bound unchanged

Once every admitted local phase class satisfies the calibration contract,

\[
\Pr[
d_{\mathbb T}(\widehat\theta,\theta)>1/(2N^2)
]
\le
7\left(\frac1{140}\right)
=
\frac1{20}.
\]

For \(k=4\) fresh phase trials,

\[
\Pr(\text{at least one bad final phase})
\le
4\left(\frac1{20}\right)
=
\frac15.
\]

Adding the conservative calibration false-admission exception gives

\[
\Pr(\text{BE accept wrong})
\le
\frac15+\frac1{100}
=
\frac{21}{100}.
\]

Thus the frozen E3 BE risk budget is unchanged.

## 7. Trial-count amendment

Operational evaluation remains:

\[
4\ {\rm fixtures}
\times128\ {\rm bundles}
\times4\ {\rm fresh\ phase\ trials}
=
2048
\]

operational phase trials.

Calibration is now

\[
8\times1024=8192
\]

local diagnostic trials.

Therefore the final stochastic acquisition count is

\[
\boxed{10240}.
\]

This replaces the E3-D v1 top-level count 3072.

The E3-Ib `maximum_trials=4096` candidate cap is consequently superseded
**before prerecord** by

\[
\boxed{\texttt{maximum\_trials}=12288}.
\]

No other frozen E3-Ib resource cap is changed by this amendment.

This is a capacity correction caused by the stricter calibration design, not
a scientific-threshold relaxation.

## 8. Diagnostic implementation boundary

Calibration records are diagnostic only.

Each phase class may be instantiated by any frozen fixture/sector pair having
that exact \(j=0\) eigenphase:

- sixths from the order-6 fixture \(N7-a3\);
- quarters from an order-4 fixture;
- thirds from the order-3 fixture;
- phase zero from any admitted fixture.

The diagnostic generator receives the chosen sector only in the explicitly
labeled fixed-sector calibration role.

Operational \(|1\rangle\) trials continue to receive no sector/order truth.

## 9. Relationship to previous freezes

Preserve E3-D v1, E3-Ia, and E3-Ib unchanged as historical frozen artifacts.

For E3-P:

- the E3-D v1 pooled-calibration clause is superseded by this amendment;
- all other E3-D thresholds remain in force;
- E3-Ia remains unchanged;
- E3-Ib remains unchanged;
- P4 POINT/EXACT/BE semantics remain unchanged.

## 10. Gate state

After deterministic validation and freeze of this amendment:

- E3-D v1: preserved;
- E3 calibration v2: authoritative for E3-P;
- E3-Ia: PASS;
- E3-Ib: PASS;
- E3-P: OPEN NEXT;
- stochastic execution: NOT AUTHORIZED;
- run identity: UNASSIGNED;
- P4-v4: untouched.

The next step is to build the final E3-P prerecord and only then mint a fresh
stochastic identity and ledger.
