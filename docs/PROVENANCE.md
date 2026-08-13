# Provenance

## Paper binding

- Artifact version: `4.0.1`
- Paper title: *Stage X-ray: Hierarchy-Organized Structural Comparison for OpenUSD-Based HPC Digital Twins*
- Measurement runtime: NVIDIA Isaac Sim 6.0.0 full Kit
- Bundled OpenUSD: 0.25.11

The artifact is bound to the stable scientific metadata above.

## Measured evidence binding

The publication-safe projections come from frozen run
`stage-xray-isaac600-rerun-20260810-a`.

| Input | Rows | SHA-256 |
|---|---:|---|
| Earlier projection | 16,559 | `9638448242D8B885291CF88C6AAAF87A029E3F85861CA929C7E0785A6A4BBD8D` |
| Later projection | 18,283 | `53B61291A488BB4D68D062A1DC11DD8C3C73653BC8EB21D908E95A08C1E8D2DF` |

The projections are byte-for-byte copies of the verified publication-safe
outputs from that run. `MANIFEST.sha256` binds them to the release.

## Production environment commitment

- Internal build: `6.0.0-rc.59+release.41464.5f2772bc.gl`
- `kit.exe` SHA-256: `EBCD2B1419DE83B6DD62DDCA573BB39DE6B103E3CC514C30182818BC33D84F23`
- Opening: `LoadAll`, no population mask, implicit empty session layer, no
  variant overrides, and no post-open mutation
- Traversal: `Usd.Stage.Traverse()` with the default predicate and no
  instance-proxy expansion
- Fresh processes: three per state, six total

## Recomputed commitments

| Canonical commitment | SHA-256 |
|---|---|
| Original comparison: 17,030 path-and-difference-type results | `EF576AFA06CEB11EBA6A6CE5E883213DB5783619711001CC033F13D215F2FD0B` |
| 34,842 state/path/region ownership rows | `5B832048B2B79552CE7F0D8646ED80A202BEFC240BC10A95713F045E9B8E4508` |
| 115 region comparison rows | `F18F44F8A0BD48B61238077514739B8F993C992D4F3E8A1364EF121766232C30` |
| 17,041 expanded paths | `77CF12FD3B24F387C8A5B201B9C20F64B23C1B50901D8E45ADA9DDC4086D384A` |

These commitments are recomputed by the public replay and frozen in
`expected/claim_results.json`.

## Algorithm authority

Version 4.0.1 implements:

1. exact four-field comparison;
2. Reference/Payload landmark discovery;
3. nearest ancestor-or-self ownership with nested and residual regions;
4. cross-state region identification from the union of landmark paths;
5. affected-region expansion; and
6. exact path-level recomparison of the affected-region context.
