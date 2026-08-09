# RFC-0009 Acceptance Evidence

This directory contains the persistent acceptance evidence for:

**RFC-0009: Physical Execution Evidence and Substrate Conformance**

The acceptance summary is:

- `rfc0009-acceptance-summary.json`

The summary records and binds:

- the exact RFC-0009 Draft document identity;
- the exact RFC-0009 conformance-test identity;
- PE-1 through PE-15 conformance coverage;
- PF-1 through PF-10 conformance coverage;
- the RFC-0009 implementation-stack regression;
- the RFC-0008 FPGA regression; and
- the complete repository regression.

At evidence generation time:

- RFC-0009 normative conformance: **25 passed**;
- RFC-0009 implementation stack: **100 passed**;
- RFC-0008 FPGA regression: **51 passed**;
- complete repository regression: **807 passed**;
- aggregate acceptance result: **PASS**.

The acceptance record intentionally identifies the RFC document as
`Draft`, because the evidence was generated before the normative status
transition to `Accepted`.

The evidence establishes acceptance of the RFC-0009 architecture and its
reference implementation.

It does **not** constitute evidence that a physical FPGA execution has
already occurred.

RFC-0009 explicitly separates:

- content identity;
- physical authenticity;
- physical evidence conformance; and
- semantic correctness.

Actual physical-device execution claims require evidence acquired from an
actual substrate execution under the applicable RFC-0009 physical profile.
