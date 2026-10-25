# Bounded UP5K/Pico classical physical milestone

Status: **completed and frozen within the three-record scope** (2026-10-25).

The documentation classification is
`UP5K_PICO_BOUNDED_CLASSICAL_HARDWARE_DEMONSTRATOR_PASS_3_ORACLE_RECORDS`.
This label is not an observed on-device identifier or a new evidence schema.

## What was physically demonstrated

The iCE40UP5K/Pico Area-v3 implementation executed a deterministic classical
probability/PRNG service over the 22-bit half-duplex interface (16 DATA bits).
Three distinct seeded SEED → PROB pairs matched the immutable authoritative-v2
wire oracle, including both take outcomes and nonzero numerical/PRNG outputs.

| PROB oracle record | SEED oracle record | SEED / PROB sequence | PROB status / outcome | rsp_cycles | SEED response CRC16 | PROB response CRC16 |
|---:|---:|---|---|---:|---|---|
| 2 | 1 | 1 / 2 | 0001 / take=1 | 13537 (34E1) | C658 | 80B4 |
| 68 | 67 | 3 / 4 | 0000 / take=0, no semantic error | 13537 (34E1) | A838 | DBD0 |
| 194 | 193 | 5 / 6 | 0001 / take=1, nonzero numeric outputs | 13562 (34FA) | 1A98 | C65E |

Each pair comprises a 10-word SEED request and 6-word response, followed by a
28-word PROB request and 38-word response. The sealed independent audit verified
six exact response frames (132 words), six request CRCs, six response CRCs,
18 FIFO snapshot hashes and final software-reported state. These are three
retained sessions, not a statistical reliability or complete-corpus sample.
Their single-use identities remain consumed; publication requires no new run.

Direct Area-v3 RTL differential and compiled Pico-C/assembled-v6-PIO/Area-v3
joint simulation are companion evidence. They remain simulation evidence and
are distinct from the physical frames and from actual ARM instruction execution.

## Frozen identities and independent verification

| Artifact | SHA-256 |
|---|---|
| Authoritative-v2 oracle expected.txt | e501eb80a0e2b13fdd59da9bfe8c3db5fcfbf225aa20776ba25a66e5c68eb889 |
| Frozen 14-transaction Phase-E matrix | 619cf5f93dc939452266198a7519fb2b1b9eecd246ed070d33979eaa728f779c |
| Qualified v6 Pico UF2 file | edb273e1b85b27ee2a51a911fc618052e39007e716b2a4d5b0faf79a62a6ba45 |
| Qualified Area-v3 FPGA BIN file | a9b5b1208915082cfe499b5f45ed570a6e2c886053d6f7bdfeb2e63774c04ab0 |
| Sealed three-record closure ZIP | 5d4336e9fd4798ca39c66849f083c50cd80457bec96fe22e413daebf1bd68e5a |
| Sealed end-to-end architecture-gate ZIP | 784e8fad191d644371f3370b51c096b1cf84316ed639fa2975b11edd4bbba71f |

The two original sealed packages passed their manifests and packaged independent
verifiers. The closure negative tests also passed. Original archives, failures,
oracle bytes and source identities are preserved outside the public subset.

The public [evidence subset](../../evidence/shor/up5k-physical-v6/README.md)
contains unchanged oracle fixtures/source pins and exact selected numerical
transcript lines. Its manifest, original-report hashes, raw-capture hashes and
selection policy are included. Host/operator metadata and USB identifiers are
withheld after privacy review; sealed originals were not redacted or replaced.

From the repository root, Python 3 standard library only:

~~~bash
python3 -B verify_up5k_physical_evidence.py
~~~

The [read-only verifier](../../verify_up5k_physical_evidence.py) checks manifest
integrity, fixture pins, exact frames, CRC16, sequence, reported READY/turnaround,
FIFO/shadow words, snapshot/postprint hashes, protocol results and final
software status. [Tampering tests](../../tests/test_up5k_physical_evidence.py)
reject changed CRCs, FIFO/shadow words, snapshots, protocol errors, unsafe
reported state and missing/duplicate/unexpected records. Run them as part of
the complete repository suite; a targeted pass does not authorize a commit.

## Trust boundary and retained failures

The host-recorded physical provenance was independently audited from retained
logs. Public excerpt consistency is reproducible; it is not independent sensor
attestation of the physical event. FIFO, READY, output-enable and final STATUS
fields are firmware telemetry. They do not independently measure electrical
noncontention, emergency intervention latency or installed binary identity.
The FPGA BIN **file** is hash-bound and was physically executed; the complete
installed fabric configuration was not independently cryptographically read back.

Unseeded oracle record **217** remains a known divergence: physical Area-v3
status **0022**, immutable oracle **0002**. The PRNG unseeded-stream error-path
mechanism was identified, but full error-path oracle equivalence was not
established. Records **217, 200, 206, 215 and 219** remain without demonstrated
physical matches. Neither those failures nor earlier consumed transport-failure
records are erased or promoted by this later three-record milestone.

This does not resolve or conflate every earlier Phase-E physical discrepancy.
Additional error-path or diagnostic experiments would be separately authorized
extensions, not prerequisites for freezing this completed bounded milestone.

## Classical, simulated and quantum claims

The service is classical probability/PRNG transport. It is not physical N0
measurement, coherent modular order finding, quantum Fourier readout or Shor
factorization. A separate retained witness recovered N=15, a=2, Q=16, r=4 and
factors 3 and 5 with 256 simulated shots using cpc.shor.density / circuit_clock.
Its realization is explicitly **simulated** and uses no FPGA.

The [N0 status](n0-status.md) remains apparatus Status D with physical validation
and acquisition unestablished and unauthorized. [Native scalable Shor](native-boundary.md),
scalable quantum computation and quantum advantage remain unproven.
Older [P1 physical evidence](../../evidence/p1/physical/README.md) is a separate
lineage and is retained unchanged. No publication here authorizes hardware work.
