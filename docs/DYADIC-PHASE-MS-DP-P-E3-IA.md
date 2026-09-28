# MS-DP-P E3-Ia Interface Integration

**Status:** deterministic integration subgate  
**Execution:** none  
**Stochastic records:** 0  
**P4-v4:** untouched

## Purpose

E3-Ia freezes the software boundary

\[
\{\widehat\phi_j\}_{j=0}^{J}
\longrightarrow
\text{E2 unwrapping}
\longrightarrow
\widehat\theta
\longrightarrow
\text{existing P4 POINT decoder}.
\]

It deliberately does **not** implement the stochastic acquisition adapter.
That is E3-Ib.

This separation is necessary because the historical P4 bounded instrument is
hard-coded to three probes/scales, while MS-DP-P requires up to seven channels
for the frozen N15 fixture. Changing the acquisition layer and the P4 decoder
simultaneously would obscure the source of any failure.

## Operational input boundary

One local evidence row contains only:

- scale;
- local wrapped estimate;
- retained data-register identity;
- trial identity;
- channel identity;
- raw-record hash;
- inference hash;
- profile hash.

The integration API accepts no order, sector, factor, true phase, expected
denominator, expected branch, or expected peak.

Exactly one retained data-register identity is required across all scales.

## P4 boundary

E3-Ia constructs the existing schema

`cpc-shor-p4-phase/1`

with the E2 final phase estimate. The bundle-level `record_sha256`,
`inference_sha256`, and `profile_sha256` are supplied by the future E3-Ib
evidence writer and remain raw/bundle artifact identities; E3-Ia does not fake
them from truth.

The existing byte-identical P4 parser and `decode_point` are then called
directly. E3-Ia does not copy or modify continued-fraction logic.

Frozen P4 source identities:

- `src/dyadic_phase_p4_decode.py`:
  `0a00d976d0db9de95916c17fe6215885fec677a7966dac7fa6b2c01f26669d7d`
- `src/dyadic_phase_p4_types.py`:
  `5880d13a5d6175847fd3c289de7d36446694d2516705825136ce9920202e55a4`

## E3-Ib acquisition decision

The existing P4 `Bank` enforces `scales=(0,1,2)` and constructs an eight-probe-
basis state of dimension \(8d\). It cannot represent the frozen MS-DP-P N15
scale set \(j=0,\ldots,6\).

The frozen P3 mathematics already supplies a second bounded simulation route:
DP-S uses one signal probe plus one reference, resets only the probe, and
retains the complete conditioned data state between scale segments. Under the
declared independent-bath/reference, complete-reset, matched-calibration, and
QND assumptions, P3 established equality in law of the labeled local records
with DP-P.

Therefore the recommended E3-Ib bounded stochastic simulator is DP-S, explicitly
labeled as an equality-in-law simulation/resource variant. DP-P remains the
primary architecture for physical resource claims. No claim that DP-S and DP-P
have equal wall time or hardware cost is permitted.

E3-Ib must validate, before stochastic prerecord:

1. one data preparation only;
2. retained conditioned data state across every scale;
3. complete unobserved probe reset;
4. no data-register reset;
5. independently matched references;
6. unchanged local finite-step instrument;
7. local estimator returns only \(\widehat\phi_j\);
8. E3-Ia receives only those estimates and evidence identities;
9. resource profile counts sequential cumulative time separately;
10. no stochastic scientific records during deterministic validation/profiling.

## Pass meaning

E3-Ia PASS means only that the frozen E2 output is wired correctly into the
unchanged P4 POINT interface with truth-free provenance checks.

It does not establish:

- finite-window acquisition accuracy;
- E3 stochastic acceptance;
- DP-P hardware realization;
- DP-S physical equivalence outside the declared ideal assumptions;
- E1-R robustness;
- native synthesis;
- P4 PASS;
- factoring advantage.
