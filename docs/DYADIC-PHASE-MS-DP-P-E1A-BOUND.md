# MS-DP-P E1-A: Uniform Finite-Time Bound for the Canonical Referenced Channel

**Status:** FROZEN DERIVATION CANDIDATE  
**Architecture:** MS-DP-P  
**Gate:** E1-A — canonical ideal matched-reference profile  
**Scope:** deterministic mathematical bound only  
**Stochastic records:** none  
**P4-v4:** not authorized

## 1. Purpose

The MS-DP-P architecture requires each dyadic channel to estimate only its
wrapped local phase

\[
\phi_j=2^j\theta\pmod1
\]

to a fixed constant precision

\[
0<\delta<\frac16.
\]

The outstanding E1 question is whether one canonical referenced channel can
achieve such constant precision in observation time polynomial in the input
length.

This document proves a conservative \(O(1/T)\) mean-square bound for the
canonical ideal matched-reference profile. The constants are deliberately
loose; the result is a scaling theorem, not a practical time-to-solution
estimate.

The proof does not use any stochastic records or any observed P4 outcome.

## 2. Frozen canonical local profile

For a fixed conserved data-register sector, write the physical phase angle as

\[
\alpha=2\pi\phi.
\]

The probe Hamiltonian and decay operator are

\[
H_\alpha
=
g\left(e^{i\alpha}\sigma_+
       +e^{-i\alpha}\sigma_-\right),
\qquad
L=\sqrt{\Gamma}\,\sigma_-.
\]

Freeze

\[
g=\frac{\Gamma}{\sqrt8},
\qquad
0<\eta\leq1.
\]

For a homodyne local-oscillator angle \(\vartheta\),

\[
C_\vartheta=e^{-i\vartheta}L,
\]

and the monitored law is

\[
d\rho_c
=
\mathcal L_\alpha(\rho_c)\,dt
+
\sqrt{\eta}\,
\mathcal H[C_\vartheta](\rho_c)\,dW,
\]

\[
dY_\vartheta
=
\sqrt{\eta}\,
\operatorname{Tr}\!\left[
(C_\vartheta+C_\vartheta^\dagger)\rho_c
\right]dt+dW,
\qquad
(dW)^2=dt.
\]

Two orthogonal LO phases are used for each complex phase estimate.

The referenced profile contains:

- one signal complex phase with unknown wrapped phase \(\phi+\chi\);
- one matched reference complex phase with wrapped phase \(\chi\);
- the same fixed transfer phase \(\chi\) over the paired signal/reference
  acquisition;
- calibrated unit gain;
- the same declared \(g,\Gamma,\eta\);
- independent baths conditional on the fixed nuisance \(\chi\).

The proof below does not require signal/reference statistical independence for
the final mean-square inequality; matched-reference independence remains the
canonical profile assumption.

Drift of \(\chi\), gain mismatch, detector crosstalk and correlated bath noise
are outside this E1-A profile and remain robustness obligations.

## 3. Phase covariance

Let

\[
R_\alpha=e^{i\alpha\sigma_z/2}.
\]

Then

\[
H_\alpha=R_\alpha H_0R_\alpha^\dagger,
\]

and the amplitude-damping dissipator is covariant under the same rotation.
Consequently every local phase has the same Liouvillian spectrum and the same
concentration constants after rotating the homodyne axes.

It is therefore enough to derive the bound at \(\alpha=0\).

## 4. Bloch contraction at the canonical coupling

At \(\alpha=0\), write a density matrix as

\[
\rho=\frac12(I+x\sigma_x+y\sigma_y+z\sigma_z).
\]

The deviation from stationarity obeys

\[
\frac{d}{dt}
\begin{pmatrix}
\delta x\\
\delta y\\
\delta z
\end{pmatrix}
=
A
\begin{pmatrix}
\delta x\\
\delta y\\
\delta z
\end{pmatrix},
\]

where, at \(g=\Gamma/\sqrt8\),

\[
A
=
\Gamma
\begin{pmatrix}
-\frac12 & 0 & 0\\
0&-\frac12&-\frac1{\sqrt2}\\
0&\frac1{\sqrt2}&-1
\end{pmatrix}.
\]

Its symmetric part is

\[
\frac{A+A^\mathsf T}{2}
=
\Gamma\,
\operatorname{diag}
\left(-\frac12,-\frac12,-1\right).
\]

Hence

\[
\frac{d}{dt}\|\delta r_t\|_2^2
\leq
-\Gamma\|\delta r_t\|_2^2,
\]

and therefore

\[
\boxed{
\|\delta r_t\|_2
\leq
e^{-\Gamma t/2}\|\delta r_0\|_2.
}
\]

For a traceless Hermitian qubit operator
\(X=(x\cdot\sigma)/2\),

\[
\|X\|_1=\|x\|_2.
\]

Thus the unconditional semigroup contracts every traceless Hermitian
deviation in trace norm as

\[
\boxed{
\|e^{t\mathcal L}(X)\|_1
\leq
e^{-\Gamma t/2}\|X\|_1.
}
\]

This proves the required contraction directly; no inference is made merely
from the location of Liouvillian eigenvalues.

## 5. Stationary phase contrast

The stationary coherence is

\[
q_{\rm ss}
=
\langle\sigma_-\rangle_{\rm ss}
=
-\frac{2ig\Gamma}{\Gamma^2+8g^2}e^{i\alpha}.
\]

At \(g=\Gamma/\sqrt8\),

\[
|q_{\rm ss}|=\frac1{\sqrt8}.
\]

Two orthogonal stationary homodyne means form a planar vector of radius

\[
R
=
2\sqrt{\eta\Gamma}\,|q_{\rm ss}|
=
\boxed{\sqrt{\frac{\eta\Gamma}{2}}}.
\]

The radius is independent of \(N,j,r,s,\alpha\).

## 6. Uniform output-covariance bound

For one fixed homodyne window define

\[
B_\vartheta=C_\vartheta+C_\vartheta^\dagger.
\]

Because

\[
\|C_\vartheta\|_\infty=\sqrt{\Gamma},
\qquad
\|B_\vartheta\|_\infty=\sqrt{\Gamma},
\]

and for any density matrix \(\rho\)

\[
D_\vartheta(\rho)
=
C_\vartheta\rho+\rho C_\vartheta^\dagger
-\operatorname{Tr}(B_\vartheta\rho)\rho
\]

is Hermitian and traceless,

\[
\|D_\vartheta(\rho)\|_1
\leq
3\sqrt{\Gamma}.
\]

For \(t>s\), the regular part of the homodyne-output covariance is given by
the quantum regression/innovations identity

\[
K_\vartheta(t,s)
=
\eta\,
\operatorname{Tr}
\left[
B_\vartheta
e^{(t-s)\mathcal L}
D_\vartheta(\rho_s)
\right].
\]

Using the trace-norm contraction,

\[
\boxed{
|K_\vartheta(t,s)|
\leq
3\eta\Gamma e^{-\Gamma(t-s)/2}.
}
\]

The white innovations term contributes the usual delta-function shot noise.

For a retained window of duration \(T\), define

\[
\overline I_\vartheta
=
\frac{Y_\vartheta(T)-Y_\vartheta(0)}{T}.
\]

Then, uniformly over phase and initial probe state,

\[
\operatorname{Var}(\overline I_\vartheta)
\leq
\frac1T
+
\frac{2}{T}
\int_0^\infty
3\eta\Gamma e^{-\Gamma\tau/2}\,d\tau,
\]

so

\[
\boxed{
\operatorname{Var}(\overline I_\vartheta)
\leq
\frac{1+12\eta}{T}.
}
\]

No stationarity assumption is required for this variance bound.

## 7. Burn-in bias

Let \(B\geq0\) denote a burn duration before the retained window.

For any initial probe state,

\[
\|\rho_t-\rho_{\rm ss}\|_1
\leq
2e^{-\Gamma t/2}.
\]

Therefore the retained-window mean differs from its stationary value by at
most

\[
\left|
\mathbb E\overline I_\vartheta-\mu_{\vartheta,\rm ss}
\right|
\leq
\frac{4\sqrt{\eta}}
{\sqrt{\Gamma}\,T}
e^{-\Gamma B/2}.
\]

For the two-quadrature vector \(\widehat m\),

\[
\boxed{
\mathbb E\|\widehat m-m\|_2^2
\leq
\frac{2(1+12\eta)}{T}
+
\frac{32\eta}{\Gamma T^2}e^{-\Gamma B}.
}
\]

## 8. Vector-to-phase lemma

Let \(m\in\mathbb R^2\) satisfy \(\|m\|=R>0\), and let
\(\widehat m=m+e\). Define the phase of the zero vector arbitrarily.

Let \(d_{\mathbb T}\) denote circular phase error in cycles. On
\(\|e\|\leq R/2\),

\[
d_{\mathbb T}(\arg\widehat m,\arg m)
\leq
\frac{\|e\|}{\pi R}.
\]

On the complement,

\[
d_{\mathbb T}^2\leq\frac14.
\]

Markov's inequality for \(\|e\|^2\) therefore gives

\[
\boxed{
\mathbb E d_{\mathbb T}^2
\leq
\left(1+\frac1{\pi^2}\right)
\frac{\mathbb E\|e\|^2}{R^2}.
}
\]

Define

\[
A_\pi:=1+\pi^{-2}.
\]

## 9. Matched-reference phase theorem

Let \(\widehat\psi_s\) and \(\widehat\psi_r\) be the signal and matched-reference
phase estimates obtained from their two-quadrature vectors.

The corrected phase estimate is

\[
\widehat\phi
=
\widehat\psi_s-\widehat\psi_r
\pmod1.
\]

The true phases are respectively \(\phi+\chi\) and \(\chi\), so the fixed
transfer phase cancels.

By circular triangle inequality,

\[
d_{\mathbb T}(\widehat\phi,\phi)
\leq
d_{\mathbb T}(\widehat\psi_s,\phi+\chi)
+
d_{\mathbb T}(\widehat\psi_r,\chi).
\]

Using \((a+b)^2\leq2(a^2+b^2)\), the preceding vector bound and

\[
R^2=\frac{\eta\Gamma}{2},
\]

one obtains

\[
\boxed{
\mathbb E
d_{\mathbb T}(\widehat\phi,\phi)^2
\leq
\frac{C_A(\eta)}{\Gamma T}
+
\frac{D_A}{(\Gamma T)^2}e^{-\Gamma B},
}
\]

where

\[
\boxed{
C_A(\eta)
=
16\left(1+\frac1{\pi^2}\right)
\frac{1+12\eta}{\eta},
}
\]

and

\[
\boxed{
D_A
=
256\left(1+\frac1{\pi^2}\right).
}
\]

The bound is uniform in

\[
N,\ j,\ r,\ s,\ \phi,\ \chi.
\]

For \(\Gamma T\geq1\),

\[
\boxed{
\mathbb E
d_{\mathbb T}(\widehat\phi,\phi)^2
\leq
\frac{C_{\rm loc}(\eta,B)}{\Gamma T},
}
\]

with

\[
C_{\rm loc}(\eta,B)
=
C_A(\eta)+D_Ae^{-\Gamma B}.
\]

This is the E1-A form required by the MS-DP-P frozen architecture.

## 10. Canonical numerical constant

For the already used canonical efficiency

\[
\eta=0.8
\]

and burn

\[
B=\frac{16}{\Gamma},
\]

the conservative analytic constants are

\[
C_A(0.8)
=
233.4800909321756,
\]

\[
D_A
=
281.9382230124385,
\]

and

\[
\boxed{
C_{\rm loc}
=
233.4801226601428.
}
\]

These constants are intentionally conservative. They are not fitted to P3/P4
records.

## 11. Finite-time local failure bound

For any fixed local target

\[
0<\delta<\frac16,
\]

Markov gives

\[
\Pr\left[
d_{\mathbb T}(\widehat\phi,\phi)>\delta
\right]
\leq
\frac{C_{\rm loc}}
{\Gamma T\delta^2},
\qquad
\Gamma T\geq1.
\]

If MS-DP-P uses \(J+1\) scales and allocates

\[
\beta_j=\frac{\beta}{J+1},
\]

then it suffices to choose

\[
\boxed{
\Gamma T
\geq
\frac{C_{\rm loc}(J+1)}
{\beta\delta^2}.
}
\]

For fixed bounded-error target \(\beta\), fixed \(\delta\), and
\(J=O(\log N)\),

\[
\boxed{
T=O(\log N)/\Gamma.
}
\]

Thus the canonical ideal local measurement cost is polynomial in the input
length \(n=\lceil\log_2N\rceil\).

This E1-A route gives \(1/\beta\) rather than logarithmic confidence scaling.
It establishes bounded-error polynomiality. It does not by itself establish
efficient arbitrarily small \(\beta\) when \(\beta\) is specified in binary.
The stronger E1-B exponential-concentration route remains useful for that
purpose.

## 12. Physical-time accounting

One corrected local phase estimate uses four retained windows:

1. signal quadrature 0;
2. signal quadrature \(\pi/2\);
3. reference quadrature 0;
4. reference quadrature \(\pi/2\).

Each window has burn \(B\) and retained duration \(T\), unless a future
validated implementation safely shares burn/transient handling.

Therefore the conservative per-scale channel-time is

\[
4(B+T).
\]

In ideal DP-P, corresponding windows for all \(J+1\) scales may be operated
simultaneously under the commuting-bank model. Hence:

- elapsed local-measurement time: \(O(B+T)=O(\log N)\) for fixed \(\beta\);
- aggregate channel-time:
  \(O((J+1)(B+T))=O((\log N)^2)\).

This accounting excludes native-Hamiltonian synthesis cost.

## 13. Gate decision

### E1-A canonical ideal matched-reference profile

\[
\boxed{\text{PASS as a deterministic finite-time scaling theorem.}}
\]

The pass means only:

- the canonical local phase problem has a uniform explicit
  \(C_{\rm loc}/(\Gamma T)\) mean-square bound;
- the constant is independent of \(N,j,r,s,\phi,\chi\);
- fixed-precision bounded-error local acquisition therefore has polynomial
  observation-time scaling when \(J=O(\log N)\).

### E1-R robustness

**OPEN.**

The theorem does not cover:

- time-dependent transfer-phase drift;
- unequal signal/reference gains;
- uncertain or varying \(\eta\);
- detector bandwidth/filter distortion;
- correlated signal/reference noise;
- inter-scale crosstalk;
- hardware non-Markovianity.

### E1-B exponential concentration

**OPEN / OPTIONAL FOR CURRENT BOUNDED-ERROR POLYNOMIALITY.**

A tilted-generator or other rigorous exponential bound may substantially
improve constants and confidence scaling.

## 14. Consequence for the research path

The fixed-\(j=(0,1,2)\) candidate remains closed.

The mathematical chain now is:

\[
\text{constant local contrast}
\rightarrow
\text{uniform qubit contraction}
\rightarrow
\text{uniform }O(1/T)\text{ referenced phase MSE}
\rightarrow
J=O(\log N)
\rightarrow
\text{POINT precision without an }O(N^2)\text{ global grid}.
\]

This is enough to open **E2 deterministic multiscale implementation**.

E2 must still be truth-free and must test:

- circular-boundary cases;
- odd orders;
- even non-power-of-two orders;
- repeated early dyadic aliases;
- exact branch-margin behavior;
- local-estimate error injection up to the frozen \(\delta\);
- \(O(\log N)\) scale count;
- absence of any \(N^2\)-sized inference object.

No new stochastic P4 identity is authorized by this result.

## 15. Non-claims

This theorem does not establish:

- P4 PASS;
- physical detector robustness;
- native synthesis of \(H_j\);
- scalable hardware realization;
- physical time-to-solution advantage;
- matched-confidence advantage over circuit Shor;
- factoring performance on hardware;
- any system-level AI-control claim.
