# MS-DP-P E3-Ib — Deterministic DP-S Acquisition Adapter

**Status:** deterministic acquisition-integration gate  
**Scientific stochastic execution:** not authorized  
**Run identity:** unassigned  
**P4-v4:** untouched  
**DP-P:** remains the primary physical architecture

## 1. Native-kernel audit result

The frozen P3 native generator already implements the required DP-S semantics:

- profile 1 uses state dimension \(2d\);
- one data preparation is counted;
- each later scale performs an unobserved probe-reset environment branch;
- the selected probe branch is moved into the ground-probe block;
- the data register is re-prepared only for profile 2, the explicit
  fresh-data negative control;
- the signal and reference records are indexed by scale.

The obstacle is purely a bounded implementation cap: the frozen P3 kernel
rejects \(m>3\) and declares `refs[3][2]`.

For E3-Ib, the kernel is copied to a new source identity and changed in exactly
two places:

1. `m>3` becomes `m>7`;
2. `refs[3][2]` becomes `refs[7][2]`.

No historical P3/P4 source or binary is modified.

Seven scales are sufficient for the frozen \(N=15\) fixture.

## 2. Arbitrary-scale DP-S compiler

The historical Python `Bank` also restricts scales to 0,1,2. E3-Ib therefore
uses a new `SequentialBank` whose scale set is not caller-selected:

\[
(0,1,\ldots,J),\qquad
2^J>2\delta N^2,\quad \delta=1/8.
\]

Each scale compiles the single-probe permutation directly from

\[
c_j=a^{2^j}\bmod N
\]

and its modular inverse. For \(j=0,1,2\), deterministic tests require exact
equality with the frozen P3 single-probe compiler.

The DP-S native state dimension is always \(2d\), independent of scale count.

## 3. Local record-only estimator

For each scale and each retained two-quadrature record,

\[
Z_s=-\bar I^{(s)}_{\pi/2}+i\bar I^{(s)}_0,
\qquad
Z_r=-\bar I^{(r)}_{\pi/2}+i\bar I^{(r)}_0.
\]

The local estimator is

\[
\widehat\phi_j=
\frac{1}{2\pi}\arg(Z_s Z_r^*)\pmod 1.
\]

This is the same matched-reference vector estimator used in E1-A. It receives
records only. Transfer phase is removed by the independently generated
reference record; no true transfer value is passed to the estimator.

If the corrected complex vector is exactly zero, inference fails closed.

The \(J+1\) local estimates are then passed to the already frozen E3-Ia/E2
interface.

## 4. DP-S interpretation

The DP-S simulator is admitted only as the already-derived equality-in-law
resource variant. It is not substituted for DP-P in physical-resource claims.

The native generator samples the unobserved reset-environment branch internally.
That hidden branch is not an inference input. Averaging over the hidden
environment implements the complete probe reset while retaining the data state
law.

Identity dead time, retune time, and reset duration are counted in the resource
profile; the frozen ideal model applies no data evolution during those
intervals.

## 5. Deterministic profiling

Before any prerecord, E3-Ib profiles all four fixtures with a fixed callback
value 0.125:

- no PRNG is instantiated;
- generated arrays are discarded;
- no output record is retained;
- the profile is not scientific evidence.

The practical candidate schedule remains

\[
\Gamma=1,\quad g=1/\sqrt8,\quad\eta=0.8,
\]

\[
B=16,\quad \Delta t=0.04,\quad T=81.92,
\]

or 2048 retained steps per quadrature window.

Gap accounting uses the historical bounded values

\[
t_{\rm reset}=0.25,\qquad
t_{\rm retune}=0.1,\qquad
t_{\rm dead}=0.5.
\]

## 6. Resource-cap rule

The E3-Ib freeze derives numeric final-prerecord caps from:

1. exact structural array sizes;
2. measured fixed-callback runtime/RSS on \(J=3,4,6\);
3. conservative floors inherited from the successfully exercised P4
   supervisor caps.

The caps are execution ceilings, not performance claims. They may not be
changed after the final E3 prerecord is frozen.

## 7. Nonclaims

E3-Ib PASS does not establish:

- E3 stochastic acceptance;
- finite-window local error \(<1/140\);
- E1-R robustness;
- physical DP-P realization;
- equal DP-P/DP-S hardware cost or wall time;
- native polynomial synthesis of \(H_j\);
- scalable hardware factoring;
- a quantum advantage.

## 8. Next gate

If E3-Ib passes, build **E3-P**, the final prerecord:

- freeze the new kernel/library hashes;
- freeze source and dependency seals;
- freeze the \(n_{\rm cal}=1024,\ X_{\rm cal}\le1\) calibration gate;
- freeze 128 bundles per fixture and \(k=4\);
- freeze the numeric resource caps from E3-Ib;
- mint a fresh stochastic run identity and seed ledger;
- freeze an unused output namespace;
- STOP for separate explicit human GO.

No stochastic execution occurs during E3-Ib.
