# P1 physical FPGA evidence

This directory freezes the evidence for the 2026-08-15 CPC P1 execution on the Lattice iCE40 UltraPlus Breakout Board. The RFC-0009 `fpga.physical-device.v1` evidence-profile evaluation passes, and the separately decoded result `1` matches the CCIR reference result `1` for `x0=0, x3=1`.

These remain distinct claims: digests establish byte identity; the evidence envelope establishes declared lifecycle conformance; the photograph supports physical observation within its stated trust boundary; and the execution report establishes semantic agreement.

## Artifact index

| Artifact | SHA-256 | Role | Claim dimension |
|---|---|---|---|
| `p1-device-programming-record.json` | `sha256:f7dbb2746357ba83cdaf93a43eac8f03009da45a51950bb121051f635fd468fe` | programming binding | provenance |
| `p1-icebreaker.bin` | `sha256:7d69fad66e08b4528c58c710ddaeb945b7aea822add761a251c85ec8ee1968c5` | programmed bitstream | identity |
| `p1-measurement-record.json` | `sha256:bfafbad305603fbdd2c8d11cfcae541923852ebce490ad1c2ef12d6b5a7684c0` | LED measurement | observation |
| `p1-observable-execution.json` | `sha256:c6d7745819a1c79c6bb933468054e6090cd5c1cff80b27afc5fb593f93e22da7` | admitted observable | observation |
| `p1-physical-build-manifest.json` | `sha256:138fa129a606f565e025544f9ca8d99aa4816f5105f79548fc5f0610a9f8dead` | build manifest | provenance |
| `p1-physical-build-report.json` | `sha256:2c3d7496acf7618a08b1007b241f63ac16aaf718140a951e8419dd3243791509` | build report | provenance |
| `p1-physical-evidence-conformance-report.json` | `sha256:5db821e2127171708cf3234e9d2783da313ba118e72b955f74f967666f840096` | RFC-0009 profile result | conformance |
| `p1-physical-execution-evidence.json` | `sha256:3f1ed5bae653959e6d54b3b607553459f9d24778f82680e9d0a8488630a43a1b` | RFC-0009 evidence envelope | conformance |
| `p1-physical-execution-event.json` | `sha256:d21b668e1a9d585e15547b71921b41d378aeb0ec80e8a7aa2a7fcf6d8536a829` | execution event | provenance |
| `p1-physical-execution-report.json` | `sha256:2420756e268f8dca97541010fe5a1da434a776fd10ffa85fdc0a47b877819f88` | independent CCIR result | semantic validation |
| `p1-physical-observation.heic` | `sha256:6438d0956063a7a3318eab66a0d238fe8d4b0be6583e56c4a409848dabde09ed` | original photograph | observation |
| `p1-physical-top.v` | `sha256:2e0eb4039dafe4d3539e3e1c22695d44899f47535a4a8d1f0aed6f61a4c572eb` | physical Verilog | build input |
| `p1-programming-log.json` | `sha256:786468e77f513e48fd45f92a8dffa5ab883a5907fd35a796cb144dd602e09517` | guarded action log | programming |
| `p1-programming-report.json` | `sha256:eb4bd6e7571ed5c8a77d7cca11c5d7a5c3e06d44675e5afe8ef7de121d0ead35` | programming status | programming |
| `p1-stimulus-record.json` | `sha256:ad073a9c043e1adac44bb380e0c1e8bc3c99291a1b1838730c7e0e9812b14994` | fixed boundary stimulus | stimulus |
| `p1-timing-report.json` | `sha256:dd140878dadd84b2562f178104805a1806647c18949fecc0017a13f1c6a12aba` | static timing report | timing |

## Timing scope

P1 is a static combinational output with synthesis-bound constants, no clock domain, and no interior timing path. The retained nextpnr report records successful routing under the admitted single-shot static observation conditions. It makes no Fmax, latency, scaling, or computational-complexity claim.

## Reproduction order

The derived records are reproduced without reprogramming the board:

```text
python3 build_p1_physical_artifacts.py
python3 record_p1_physical_programming.py
python3 record_p1_physical_execution.py
python3 validate_p1_physical_evidence.py
python3 validate_p1_physical_execution.py
python3 freeze_p1_physical_evidence.py
```

The guarded programming action is intentionally absent from this sequence. Reprogramming is a separate consequential operation that requires explicit approval.

## Trust boundary

The record binds the supplied photograph and its visible state; it does not independently authenticate the photographer or capture environment.
