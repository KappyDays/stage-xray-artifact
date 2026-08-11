# Stage X-ray Artifact v4.0.0

This is the clean submission release for *Stage X-ray: Validated Structural
Comparison of OpenUSD Stages for HPC Digital Twins*.

## Highlights

- Binds retained production evidence to NVIDIA Isaac Sim 6.0.0, bundled
  OpenUSD 0.25.11, and six fresh full-Kit processes.
- Replays landmark-based region construction, affected-region
  expansion, second comparison, distribution analysis, and JSON/SQLite/trie
  reconstruction checks.
- Aligns the public API and documentation with the manuscript terms
  `original record comparison`, `landmark`, `region`, and `difference type`.
- Uses publication-safe four-field projections for the public replay.
- Requires only CPython 3.10 or newer and the Python standard library.
- Includes an integrity manifest, privacy gate, deterministic golden results,
  synthetic edge-case tests, and AD/AE guidance.

## Reproduce

```shell
python -m stage_xray_artifact reproduce --data data/publication_safe --out build/reproduction --verify
python -m unittest discover -s tests -v
```

The expected headline result is exact recovery of all 17,030 differences from
75 affected regions, with zero missing, extra, or duplicated differences.
