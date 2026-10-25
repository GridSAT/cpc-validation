# Bounded UP5K/Pico evidence publication note

**Release collateral only — no version tag or GitHub release created.**
Prepared 2026-10-25 for review against the research branch.

The completed [Area-v3/Pico milestone](../shor/classical-up5k-physical-milestone.md)
is frozen within three seeded classical oracle records: 2, 68 and 194.
Six physical SEED/PROB response frames (132 words) match immutable fixtures,
including CRCs, sequences and reported FIFO/shadow audit hashes.
The [public subset](../../evidence/shor/up5k-physical-v6/README.md) supplies
privacy-reviewed numerical excerpts, original identity pins and a read-only
standard-library verifier:

    python3 -B verify_up5k_physical_evidence.py

Original sealed reports remain unchanged and private. Hashes bind artifact
files; firmware telemetry is not independent electrical measurement or
cryptographic readback of the installed FPGA fabric.

Known unseeded record 217 (physical 0022 versus oracle 0002) and five unmatched
physical error-path cases remain open. This note does not erase historical
failed runs or claim complete physical oracle conformance.

[WP-B1 software conformance](../shor/wp-b1-conformance-checklist.md) is outstanding.
The [Alice & Bob brief](../shor/alice-bob-collaboration-brief.md) is an unsent
technical draft. Physical N0 quantum measurement, native Shor order finding,
scalable quantum computation and quantum advantage remain unproven.

Every publication commit must pass the complete repository suite, with its
tested tree and actual count recorded. Before pushing, independently validate
the exact final commit in a fresh isolated clone; verify links, public evidence,
parent-file preservation, privacy and actual Pages deployment state.
Repository GitHub file/PR links are the publication surfaces unless a Pages
deployment is independently established. Historical release test counts are
not current validation results.

No hardware operation, external outreach, version tag or release is authorized
by this note. The prior P1 and N0 lineages are retained separately.
