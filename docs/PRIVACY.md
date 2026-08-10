# Privacy and publication boundary

The release contains hierarchy-preserving pair tokens, not production Prim
names. It intentionally excludes:

- production OpenUSD Stages and their dependencies;
- raw Prim paths and private path lists;
- resolver roots, resolver values, and asset locations;
- reverse token maps and raw target identifiers;
- credentials, browser state, host home-directory paths, and local commands;
- private extraction outputs.

`python -m stage_xray_artifact privacy-scan` fails on host-path markers and
validates every path in both public projections against the token grammar.
`MANIFEST.sha256` binds the exact release file set after that scan.

The retained Isaac Sim 6.0.0 audit summaries contain counts, timing summaries,
process IDs, runtime commitments, and cryptographic commitments. They do not
provide the underlying private inputs.
