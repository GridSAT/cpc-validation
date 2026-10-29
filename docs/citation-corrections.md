# Citation metadata and historical versions

## Recommended citations

- Daghbouche, K. (2026). *CPC Validation (Version v0.7.0)* [Computer software].
  Zenodo. [10.5281/zenodo.23652408](https://doi.org/10.5281/zenodo.23652408).
  Release date: 2026-10-26.
- Daghbouche, K. (2026). *CPC Validation (Version v0.6.0)* [Computer software].
  Zenodo. [10.5281/zenodo.22045319](https://doi.org/10.5281/zenodo.22045319).
  Release date: 2026-08-21.

Author identifier: [ORCID 0000-0002-4351-2861](https://orcid.org/0000-0002-4351-2861).

The [concept DOI](https://doi.org/10.5281/zenodo.22045318) identifies the software
version series. Use the version-specific DOI when citing a particular release.
For v0.2.0, v0.3.0, v0.5.0-frontend.1 and v0.5.0, cite the corresponding GitHub
tag and Karim Daghbouche; no version-specific Zenodo DOI was verified.
Development snapshots retain their declared metadata and are cited by exact commit.

## Historical source snapshots

Use the citations above for the corresponding archived versions. Embedded
metadata in historical source snapshots may differ from current citation
metadata. Original tag objects, source files and publication dates remain
unchanged, including inherited early CFF versions and the v0.7.0 prearchive
DOI-pending comment.

| Historical tag | Original tag object | Original target commit | Embedded CFF version |
|---|---|---|---|
| architecture-v1 | 01dd854eb981cb111463030c6eb2e266aa54a4da | 1153cf098e880758803c2420a7059098b1a18e76 | 0.2.0 |
| ccir-front-end-v1 | aad21d602a823398f3add875484b715e961a32e0 | 50d73c31875280b70edf60a0c39c739fdc43112e | 0.2.0 |
| cpc-backend-qualification-v1 | dfe3c177d23f13fe589732c7699d3876d634211e | 6751d26729fc76d6b4d5661994079e37b5d625bf | 0.2.0 |
| cpc-benchmark-validation-v1 | 88d6b8d27ceb913f62458132b97259c1940ccbd3 | 501d6524c3594a3d18c891791927fc3f4c4c9347 | 0.2.0 |
| cpc-cross-backend-v1 | 620a1b42546fe2fd0b8ae351892baff04e752221 | 5c2261ebb4bb47b6790efb45c306664a8b0075f9 | 0.2.0 |
| cpc-fpga-tri-backend-v1 | 12fe942e1d5a1b643b6551bd9e26f3e432f723a6 | 5d839d61a09092e5135140fb0f7110373bc9d88e | 0.2.0 |
| cpc-open-system-execution-v1 | fd63d6117026cc0088618d0d42688b9599fe1627 | 650effc73f47733032def9ca421f3615db98ddb6 | 0.6.0 |
| cpc-physical-backend-v1 | 1e6afbe4f5111bf7c69a0cc4ded4d79ef8a16a62 | c43d5c0727699cf53ad7fd6db9f08869230be9ba | 0.2.0 |
| cpc-physical-evidence-v1 | 078700a46c9c4c92c6e8484ab803f61753ac56b1 | 1206ecac02a13b9449dc87a854df73924713a8c9 | 0.2.0 |
| cpc-physical-fpga-p1-v1 | d85f67eb1338ff323cbbc837f06964c5d841ca88 | 81fb0c58df2a3ba6339e1a1d0528d83e3f912fcd | 0.5.0 |
| cpc-standard-v1 | 9894f4834bd996dbe3811e59c94f035d3a642e22 | f90365abe7db028cc77a844557363d86bd24d63b | 0.2.0 |
| v0.2.0 | 09a08f6732cb21eb199f6905151eab0530e87565 | c9830879481c77dfff5651e21103f7397ed20a78 | 0.2.0 |
| v0.3.0 | 2c7d1a93484be04995a336a33fa7d1b6e1730713 | 7632d2b0d1b670c132baed443e1418733ad57f07 | 0.2.0 |
| v0.5.0 | bc8171a4305dbd649bb8cd93c9b2fbac2d55f005 | 81fb0c58df2a3ba6339e1a1d0528d83e3f912fcd | 0.5.0 |
| v0.5.0-frontend.1 | 841fed0a48bd6a02b4556a17ab9b66f09a8faf16 | 974efea216d5fb966c9f47d1abb23119f245f375 | 0.2.0 |
| v0.6.0 | 3b0857c9a5915dcc4d7a07ff1962823c9f6d96e8 | 650effc73f47733032def9ca421f3615db98ddb6 | 0.6.0 |
| v0.7.0 | 6fac0a4bbe9be3589b5c916afc649cc76e075b43 | d9ce502fb1f702fcb6503be5e80693e57c6209ab | 0.7.0 |

The unchanged v0.7.0 Zenodo ZIP has SHA-256
5d0abb2b3ef3ca9f63c496d94dd3d4af8654d3a3b2a818b4cab1f56fe1d5dd85.
The unchanged v0.6.0 ZIP has SHA-256
3041f19707ca5418cd1fcb1e3ad4ecd51d880df14b9a5120b7d2cbfce7d17ee6.
The existing v0.6.0 record received its ORCID update on 2026-10-29;
its record ID, DOI, version and archived files remain unchanged.
No new deposit or version was created.

## Metadata validation

CITATION.cff and .zenodo.json provide machine-readable citation metadata.
The Zenodo metadata file deliberately omits fixed version, DOI and date fields
so future releases receive their own identifiers. Run
python verify_authorship_metadata.py and the complete validate.py --full profile.
The regression tests cover metadata consistency, ORCID, DOI and contributor-role
handling while allowing copyright statements and third-party references.

The earlier RFC0003 and RFC0004 branch proposals remain uncommitted because their
full suites fail the compiler-scaling stage with
ValueError: CCIR parity variables must be sorted. Their proposed metadata and
failure logs remain in the private qualification evidence.
