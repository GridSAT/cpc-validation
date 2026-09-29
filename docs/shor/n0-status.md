# N0 validation status

## Scope

N0 is a physical CPC measurement validation milestone for a known/prepared
physical eigenphase.

It does not by itself establish:

- full Shor execution;
- native scalable quantum computing;
- scalable CPC-Shor;
- computational advantage;
- a complete semantic L_prob realization.

## Effective model

The finite N0 model uses the stabilized bosonic dynamics

L_stab =
    kappa_2 D[a^2 - alpha^2]
  + kappa_1 D[a]
  + kappa_phi D[a^\dagger a].

The logical preparation is

(|0_L> + exp(i theta)|1_L>)/sqrt(2),

and the logical probe is

O_beta = X_L cos(beta) + Y_L sin(beta).

The effective measurement record is represented as

dY =
    2 sqrt(eta Gamma_m) Tr[O_beta rho] dt
  + dW.

These equations define the finite/effective validation model. They are not a
claim that a specific integrated physical apparatus has already realized every
term exactly.

## Frozen logical basis and measurement route

The current logical basis is the even/odd parity-cat basis,

|0_L> = |C_+>,
|1_L> = |C_->,

with parity representing logical Z_L.

A bare arbitrary-quadrature implementation was investigated and rejected as the
primary route because the logical Y contribution suffers an unfavorable
amplitude penalty and bare ladder operators introduce leakage outside the
logical subspace.

The retained route is:

1. parity-phase rotation,
2. fixed-axis logical measurement.

With

U_beta = exp(+i beta Pi / 2),

the finite logical model gives

U_beta^\dagger X_L U_beta = O_beta.

The two-photon stabilization term and number-dephasing term have the required
covariance in this model. Single-photon loss breaks the exact covariance; the
resulting mismatch was found to scale with kappa_1 in the finite numerical
study.

This validates the finite-model reduction. It does not establish a complete
microscopic physical synthesis.

## Apparatus concept

Primary carrier profile:

- stabilized superconducting bosonic/cat oscillator.

Fallback research profiles:

- GKP bosonic encoding;
- multimode bosonic implementations.

The present apparatus classification is:

APPARATUS_STATUS = D

meaning that an apparatus concept has been defined, but the required CPC
interaction has not yet been established on a specific integrated physical
platform with the required independently auditable acquisition access.

## Historical external-platform assessment

This records the earlier apparatus-screening study. It is not a current
vendor-capability certification or evidence that an integrated N0 apparatus
has been established.

Alice & Bob Helium/Boson-class hardware is a capability target considered during
the apparatus study.

Publicly available information was sufficient to motivate that target, but not
to establish all N0 requirements on one integrated device, in particular the
complete required logical rotation/control and independently auditable raw
measurement/timebase interface.

Accordingly:

EXISTING_INTEGRATED_N0_CAPABILITY_PROVEN = NO

NEW_DEVICE_OR_FABRICATION_REQUIRED_PROVEN = NO

PUBLIC_EVIDENCE_INSUFFICIENT_FOR_B_OR_C = YES

This assessment is a capability-screening result, not a statement that the
platform is unsuitable.

## N0 software stack

The published pre-physical software stack includes:

- physical-profile schema;
- raw-record schema;
- calibration/device adapter;
- claim firewall;
- finite bosonic model;
- effective measurement model;
- stochastic synthetic device;
- statistical primitives;
- record and model fault injection;
- end-to-end synthetic rehearsal;
- RFC-0010 mapping;
- controller protocol and synthesis checks;
- physical-adapter boundary checks;
- statistical decision logic;
- repeated held-out synthetic statistical rehearsal;
- physical-preregistration freeze framework;
- readiness gates.

This software layer remains a freeze candidate and is not equivalent to physical validation.

## Controller / FPGA boundary

N0 controller RTL, host-side protocol/synthesis software, and simulation tests
are published. This does not establish physical N0 hardware validation or
authorize programming/acquisition.

The controller's intended apparatus role is deterministic sequencing, timing,
instrument control and transfer of integrity-preserving raw records.
Physical acquisition interfaces and the integrated apparatus must be
implemented and qualified separately. Published simulation/synthesis checks
do not establish place-and-route, timing closure, an N0 bitstream, programming
or physical measurement.

It is not:

- the CPC dynamics;
- the bosonic quantum state;
- the required physical probe interaction;
- waveform synthesis unless separately implemented and validated;
- semantic inference;
- a truth or factor oracle.

The FPGA/controller must not receive theta_truth or an equivalent semantic
answer.

## Current readiness gate

The current readiness state is:

SOFTWARE_FREEZE_CANDIDATE = YES

PHYSICAL_N0_VALIDATED = NO

PHYSICAL_EXECUTION_AUTHORIZED = NO

FPGA_PROGRAMMING_AUTHORIZED = NO

PHYSICAL_ACQUISITION_PERFORMED = NO

NEXT = DEFINE_PHYSICAL_N0_APPARATUS_AND_PROFILE

DO_NOT_PROGRAM_FPGA = YES

DO_NOT_ACQUIRE_PHYSICAL_N0 = YES

No positive physical N0 authorization is created by this documentation.
