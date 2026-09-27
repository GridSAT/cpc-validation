# MS-DP-P E2 -> E3 Prospective Lineage Amendment

**Status:** prospective lineage amendment
**Purpose:** bridge the corrected public E2 implementation to the historical frozen E3 design without rewriting historical E3 provenance
**Execution authorization:** none
**Stochastic records authorized:** none
**Historical evidence rewrite:** forbidden

## 1. Historical E2 identity retained by frozen E3

The frozen E3 design remains historically bound to the original E2 implementation identities:

- historical E2 source SHA256:
  `248b348caa925c67700f379a30e37ed4f597b5e55bbf3d75b69579bd694d0c5b`
- historical E2 tests SHA256:
  `51202923e0771977720880626b94f59c3753d51f69ea9d180b77ec325cc455d6`
- E2 documentation SHA256:
  `9b8b6850c64cdb8a502201b1fde7174ef80e85369e17052c2ca43acfe66fec87`

The frozen E3 design SHA256 remains:

`2ea4e318e73d2722af38772078cf9c06fdcccad24615e99119a32097a3739b8c`

No historical E3 manifest, checkpoint, source seal, result, validation object, or execution identity is modified or reinterpreted by this amendment.

## 2. Corrected public E2 identity

The public E2 implementation published after prospective resource-accounting correction has:

- corrected E2 source SHA256:
  `8e3be9e6a382b418de1bdd083ceb3b6d2de85bffc705ea3a01d686e0596f0235`
- corrected E2 tests SHA256:
  `d76e24e7492ff0ac884a8bcc50f789b2776531a6c853f1e3650ec250d3dc3b72`

The E2 documentation is unchanged.

The correction removes only an unused final modular squaring in
`compile_scale_constants`, changing the executed modular-squaring count from
`J+1` to the declared exact count `J` while preserving the returned scale
constant sequence and all ordinary serialized outputs.

## 3. E3-consumed E2 API equivalence

The E3 implementation consumes the following E2 symbols:

- `DEFAULT_DELTA`
- `canonical_cycle`
- `required_highest_scale`
- `unwrap_local_phases`

AST comparison between the historical and corrected E2 source establishes that
all four definitions are identical.

The only changed top-level E2 symbol is:

- `compile_scale_constants`

E3 does not import or call `compile_scale_constants`.

Therefore the corrected E2 implementation is behaviorally equivalent to the
historical E2 implementation over the E2 API surface actually consumed by E3.

## 4. Prospective lineage rule

For prospective Git publication and validation only, E3 may depend on the
corrected public E2 source identity

`8e3be9e6a382b418de1bdd083ceb3b6d2de85bffc705ea3a01d686e0596f0235`

provided that:

1. the E3-consumed API remains exactly the four symbols listed above;
2. those definitions remain identical to the historical E2 definitions;
3. no E3 code begins consuming `compile_scale_constants` without a new review;
4. historical E3 provenance continues to reference its original E2 hashes;
5. no historical E3 result is relabeled as having been produced from the corrected E2 source.

This amendment establishes lineage compatibility only. It does not establish
clean-clone E3 reproducibility, stochastic validation, physical realization,
native synthesis, scalability, computational advantage, or any execution
authorization.

## 5. Evidence

The read-only equivalence audit established:

- `E3_IMPORTED_API_AST_EQUIVALENT = True`
- `CHANGED_TOP_LEVEL_SYMBOLS = ['compile_scale_constants']`
- audit result: `PASS`

Audit package SHA256:

`51ca1a62214ba3fecd58e11de604c135fa95252e28bd607c52fdc49d3ab2cb37`

This evidence supports only the prospective lineage statement above.

## 6. Hard boundaries

This amendment does not:

- reopen or rerun any historical E3/E4/E5 execution;
- reopen consumed E5-v1;
- convert E5-R1 recovery into prospective evidence;
- alter frozen tolerances or historical evidence;
- authorize FPGA programming;
- authorize physical N0 acquisition;
- establish physical N0 validation.

The physical N0 authorization boundaries remain unchanged.
