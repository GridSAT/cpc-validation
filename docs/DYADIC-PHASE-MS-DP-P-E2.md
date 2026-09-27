# MS-DP-P E2 Deterministic Multiscale Implementation

**Status:** deterministic implementation candidate  
**Architecture:** MS-DP-P  
**Gate:** E2  
**Stochastic records:** none  
**P4-v4:** not authorized  
**Git:** no commit authorized

## Contract

Operational E2 receives only \(N\), the frozen \(\delta=1/8\), and exactly one
wrapped local phase estimate for each required dyadic scale. It accepts no
order, sector, true phase, factor, expected denominator, expected branch, or
answer table.

The required highest scale is the minimal \(J\) satisfying

\[
2^J>2\delta N^2.
\]

Scale compilation is answer-free:

\[
c_0=a\bmod N,\qquad c_{j+1}=c_j^2\bmod N.
\]

Unwrapping is

\[
\widehat\theta_0=\widehat\phi_0,
\]

\[
k_j=\operatorname{nint}(2^j\widehat\theta_{j-1}-\widehat\phi_j),
\qquad
\widehat\theta_j=(\widehat\phi_j+k_j)/2^j\pmod1.
\]

Nearest-integer selection is exact. An exact half-integer tie fails closed.
The result records exact branch margins as provenance diagnostics; margins are
not truth inputs.

## Complexity

The implementation has no global phase grid. It stores \(J+1=O(\log N)\)
local values and performs \(J\) modular squarings plus \(J\) nearest-integer
operations. It allocates no \(N^2\)-sized inference object.

## Frozen deterministic tests

The E2 validation includes:

- exact all-sector bounded fixtures;
- odd orders;
- power-of-two orders;
- even non-power-of-two orders;
- repeated early dyadic aliases;
- circular-boundary cases;
- exhaustive Cartesian error injection on bounded fixtures;
- adversarial errors approaching \(\pm\delta\);
- fail-closed exact branch ties;
- fail-closed missing/extra channels;
- logarithmic scale counts through 1024-bit synthetic \(N\);
- source-interface audit for absence of truth/order inputs;
- zero global-grid resource accounting.

Truth/order values are used only by tests as independent diagnostics.

## P4 boundary

E2 outputs a phase estimate only. It does not modify the existing P4 strict
POINT radius, reconstruction candidates, LCM aggregation, order verification,
risk accounting, or claim types. A later integration may serialize the E2
estimate into the existing phase-payload contract without changing P4.

## Pass condition

E2 PASS requires:

1. targeted E2 tests PASS;
2. all dyadic/Shor tests PASS;
3. full repository pytest PASS;
4. SPICE 4/4;
5. frozen hashes for all E2 artifacts;
6. zero stochastic records;
7. no P4-v4 execution.

E2 PASS is deterministic mathematical/software evidence only. It does not
establish physical realization, native synthesis, or advantage.

## Next after E2

If E2 passes, E3 is a **design/preregistration phase**, not execution. It must
integrate the E1-A acquisition contract with E2, retain E1-R robustness as an
open obligation, mint a new stochastic identity rather than consume P4-v4,
and freeze thresholds, fixtures, seeds, resource caps, and failure semantics
before any record generation.

Native synthesis of \(H_j\) remains separately open.
