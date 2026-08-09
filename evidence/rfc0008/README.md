# RFC-0008 Acceptance Evidence

This directory contains the frozen acceptance evidence for RFC-0008:

- `tri_backend_validation.csv` — per-case RC/Digital/FPGA validation evidence;
- `tri_backend_summary.json` — deterministic aggregate tri-backend summary;
- `fpga.backend-qualification.json` — RFC-0007-compatible qualification
  manifest for the `fpga/1` backend.

These files are copies of generated runtime outputs produced during the
RFC-0008 acceptance run.

Runtime outputs under `results/` remain ignored by Git. Files under this
directory are intentionally tracked as immutable acceptance evidence.

The recorded acceptance run covers:

- 16 benchmarks;
- 64 exhaustive admitted boundary cases;
- RC/Digital/FPGA backend agreement on 64/64 cases;
- independent RC semantic match on 64/64 cases;
- independent Digital semantic match on 64/64 cases;
- independent FPGA semantic match on 64/64 cases; and
- overall PASS on 64/64 cases.

The FPGA qualification evidence records the external execution environment
used by the acceptance run, including the Icarus Verilog execution-engine
version.

This evidence is finite validation evidence for the repository revision,
benchmark corpus, backend implementations, and execution environment actually
exercised. It is not a universal proof for arbitrary programs or execution
environments.
