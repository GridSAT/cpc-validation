# Native CPC-Shor claim boundary

## Purpose

This document separates the finite software/model evidence in this repository
from claims that would require a native physical CPC-Shor realization.

## Finite/software layer

The repository contains executable finite models and validation code for selected
Shor components and RFC-0010 open-system concepts.

Within their declared finite domains these implementations can establish facts
about:

- typed modular-response construction;
- exact finite arithmetic maps;
- finite density-matrix evolution;
- selected dissipative witnesses;
- coherence-sensitive negative controls;
- finite Fourier statistics;
- order reconstruction;
- factor validation;
- software-level RFC-0010 mapping;
- synthetic N0 measurement and statistical pipelines.

These are meaningful validation results, but their scope is finite and explicit.

## Native architecture

A native realization requires the relevant computational state and CPC dynamics
to exist physically.

For the current CPC-Shor architecture this includes physical realization of the
required:

1. quantum state;
2. reversible modular dynamics;
3. stabilization/problem dynamics;
4. CPC probe interaction;
5. stochastic physical measurement record;
6. independently auditable acquisition chain.

A numerical simulator does not satisfy those requirements merely because it
implements the same equations.

## Classical control

Classical computation is permitted for control-plane functions such as:

- configuration;
- experiment sequencing;
- timestamping;
- record integrity;
- preregistered calibration;
- acquisition;
- post-acquisition reduction;
- independent validation.

It must not silently replace a required physical quantum/CPC operation.

In particular, semantic answers, expected factors, expected order, hidden
theta_truth, or equivalent answer information must not be supplied to the
physical controller as execution inputs.

## FPGA role

In the N0 apparatus concept, FPGA logic has a deterministic control/acquisition
role. N0 controller RTL, host-side protocol/synthesis software, and simulation
tests are published. This does not establish physical N0 hardware validation
or authorize programming/acquisition.

N0 place-and-route, timing closure, bitstream generation, programming and
physical measurement are not established by that software publication.
Historical P1 physical evidence is a separate, narrower evidence lineage.

The controller is not the quantum state or CPC interaction. Host-native P3/P4
C kernels are classical host simulation, not quantum-native execution.

## Completed classical demonstrator boundary

The [UP5K/Pico three-record milestone](classical-up5k-physical-milestone.md)
establishes bounded classical probability/PRNG transport on physical hardware.
It is separate from both P1 and the N0 controller. Its numerical responses must
not be relabeled as physical Fourier samples, quantum order finding or factors.
The retained software witness's simulated Fourier bins are also not FPGA data.

## N0 versus full Shor

A successful N0 experiment would validate a specific physical CPC measurement
primitive under the preregistered N0 conditions.

It would not alone establish:

- full Shor factorization;
- polynomial-resource native CPC-Shor;
- large-scale fault tolerance;
- general scalable quantum computing;
- computational advantage.

Those require additional architecture, resource, composition, physical, and
scaling evidence.

The published P4 replay, guarded acquisition and calibration-scoring interfaces
are software integrity infrastructure. Their existence is neither stochastic
acceptance nor physical authorization.

## Present repository status

The present repository supports the finite/software side of the boundary and
contains the software/preregistration machinery for N0.

The integrated physical N0 apparatus has not yet been established.

Therefore the current public claim remains:

NATIVE_SCALABLE_SHOR_ESTABLISHED = NO
