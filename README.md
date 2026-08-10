# Stage X-ray Artifact v3.0.0

This repository is the publication-safe artifact for **Stage X-ray: Validated
Structural Comparison of OpenUSD Stages for HPC Digital Twins**. The measured
evidence was produced with NVIDIA Isaac Sim 6.0.0 and its bundled OpenUSD
0.25.11 runtime. The public replay recomputes the paper's central ScaleX-POD
results from two sanitized four-field projections.

## Quick start

Requirements: CPython 3.10 or newer. The public replay uses only the Python
standard library; it does not require Isaac Sim, OpenUSD, a GPU, or network
access.

```bash
python -m stage_xray_artifact reproduce \
  --data data/publication_safe \
  --out build/reproduction \
  --verify
python -m unittest discover -s tests -v
```

PowerShell users can run `./run.ps1`; POSIX shell users can run `./run.sh`.

Successful verification reproduces:

- 16,559 Earlier and 18,283 Later selected Prims;
- 8,906 common, 7,653 removed, and 9,377 added paths;
- 115 aligned regions: 44 added, 30 removed, one changed, and 40 unchanged;
- exactly-once ownership of all 34,842 state-specific records;
- 17,041 expanded paths and exact recovery of all 17,030 differences;
- the affected-region distribution and a dependency-free SVG rendering; and
- ordered four-field equality after JSON, SQLite, and trie reconstruction.

## Evidence levels

| Evidence | Level | Meaning |
|---|---|---|
| Exact diff, regions, assignment, expansion, and second comparison | `RECOMPUTED` | Recalculated from publication-safe records |
| Region distribution and storage reconstruction | `RECOMPUTED` | Fully rerun by the public command |
| Six-process Isaac Sim 6.0.0 extraction repeatability | `RETAINED-AUDIT` | Publication-safe summaries can be audited; private inputs are withheld |
| Whole-Dream-AI containment | `RETAINED-AUDIT` | Aggregate audit is retained; production inputs are withheld |
| Initial production Stage opening and extraction | `NOT-PUBLICLY-REEXECUTABLE` | Requires private Stage assets and resolver configuration |

The artifact does not claim physical change, causality, performance
improvement, operator-effort reduction, automatic repair, or private-path
reconstruction.

## Repository map

- `stage_xray_artifact/`: algorithm and verification code.
- `data/publication_safe/`: pair-stable hierarchy-token projections.
- `data/audit_only/`: publication-safe Isaac Sim 6.0.0 audit summaries.
- `expected/claim_results.json`: frozen acceptance values.
- `docs/AD-AE.md`: artifact description and evaluation workflow.
- `docs/CLAIM_MATRIX.md`: claim-to-artifact mapping.
- `MANIFEST.sha256`: release file-set and byte-integrity commitment.

## License and citation

Code and publication-safe data are released under Apache License 2.0. Use the
immutable GitHub release `v3.0.0` and the metadata in `CITATION.cff` when citing
this artifact.
