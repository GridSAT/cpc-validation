# Alice & Bob technical collaboration brief — draft

**DRAFT FOR REVIEW; NOT SENT.** No access request, vendor commitment or physical
execution authorization is implied. Prepared 2026-10-25.

## Proposed initial scope

Explore a jointly scoped WP-B2/WP-B3 physical CPC-compatibility study and an
N0 **known/prepared eigenphase** measurement experiment. The immediate objective
is to establish a device-to-model and raw-data contract, not scalable Shor,
quantum advantage or evidence of a completed integrated cat-qubit apparatus.

GridSAT can contribute the canonical execution/provenance framework, independent
validation, finite bosonic/effective N0 models and preregistration machinery.
The [UP5K/Pico demonstrator](classical-up5k-physical-milestone.md) has physically
validated three bounded classical SEED/PROB oracle pairs. It is a classical
component/reference, not plug-and-play microwave control hardware and not a
quantum measurement result. [WP-B1 software conformance](wp-b1-conformance-checklist.md)
remains open and can progress independently in parallel.

## Questions requiring Alice & Bob confirmation

1. **Access and control surface.** Is a Helium co-design engagement appropriate,
   and what experiment access is available? Which raw AWG/microwave controls or
   programmable pulse primitives can a collaborator specify, inspect and archive?
   Do not assume a Felis interface offers arbitrary pulse-level access.
2. **Physical model mapping.** Which two-photon stabilization parameters,
   Hamiltonian terms, dissipators, drive phases and logical operations are
   controllable? What ranges, units, drift, calibration and restrictions apply?
   Can the retained parity-phase rotation plus fixed-axis logical measurement
   route be implemented and independently characterized?
3. **Raw acquisition.** Can time-resolved heterodyne/homodyne and reference
   records be retained with calibration identities, demodulation/filter settings,
   acquisition timebase, timestamp uncertainty and missing/saturated-sample flags?
   Which preprocessing is unavoidable and auditable?
4. **Feedback and interconnect.** What latency, jitter, bandwidth and transport
   limits apply to feedback? Which external-controller interconnects are permitted?
   Any FPGA/AWG link would need a new electrical, timing and safety contract;
   the existing Pico/UP5K interface provides no demonstrated direct compatibility.
5. **Error and model risk.** How should leakage, single-photon loss, logical
   errors, Liouvillian mixing and reference-readout uncertainty be measured?
   Can independent held-out measurements and negative controls distinguish
   calibration fit from operational inference?
6. **Scientific evidence and rights.** What de-identification, raw-data,
   calibration-metadata, reproducibility and publication permissions are possible?
   Agree ownership, embargoes and vendor review before acquisition or release.

The finite N0 model uses kappa_2 D[a²−alpha²], kappa_1 D[a] and number dephasing;
its covariance reduction has explicit single-photon-loss limitations.
These are model requirements to discuss, not assertions about vendor hardware.
Neither erasure-event thresholding alone nor natural cavity relaxation is
assumed to supply CPC semantic decoding or an instance's ground state.

## Proposed joint acceptance deliverable

First produce a written capability/gap matrix mapping the required controls,
measurement and timebase to actual device operations. Retain unsupported/HOLD
items. Then jointly freeze one known-phase N0 experiment: logical preparation,
probe/rotation, stabilization, raw/reference channels, calibration uncertainty,
held-out phases, sample sizes, fixed estimator and abstention rules, numerical
error/power/resource criteria, safety/abort conditions and publication scope.

Only after the apparatus/profile and those gates are accepted should a separately
authorized physical study be proposed. Preserve raw observations and negative
controls; keep truth labels outside operational decoding and controller inputs.
Independent reduction must use the preregistered records and report failures.

## Claim boundary

[N0 apparatus status](n0-status.md) remains D. Physical N0 validation,
acquisition and native Shor order finding remain unestablished. A successful
known-phase N0 primitive would still require separate composition, resource
scaling, order-finding and factor-validation evidence before any Shor or
quantum-advantage claim. This brief makes no claim of vendor endorsement.
