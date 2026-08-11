# Artifact Description and Artifact Evaluation

This document follows the SC26 AD/AE structure referenced by the HPC-ODA 2026
call. It is self-contained so an evaluator does not need to infer the workflow
from source code.

## Part 1 — Artifact identification

### Contributions

- **C1 — Original record comparison first.** The method compares the complete
  selected four-field record sets before adding hierarchy organization.
- **C2 — Hierarchy organization and traceability.** Reference/Payload landmarks
  create deterministic regions, every selected Prim has exactly one owner, and
  affected-region expansion is linked back to exact paths.
- **C3 — Fixed-condition evidence.** The evaluated pair is characterized by its
  original record comparison, region distribution, second comparison, and four
  stated validation checks.

### Computational artifacts

- **A1 — Replay software:** `stage_xray_artifact/` implements the submitted
  algorithm using only the Python standard library.
- **A2 — Publication-safe inputs:** `data/publication_safe/` contains the two
  ordered, four-field projections with pair-stable hierarchy tokens.
- **A3 — Retained audits:** `data/audit_only/` contains the fixed Isaac Sim
  6.0.0/OpenUSD 0.25.11 environment, aggregate domain audit, and six-process
  repeatability records. These can be integrity-checked but not regenerated
  without withheld production inputs.
- **A4 — Frozen acceptance values:** `expected/claim_results.json` binds the
  paper snapshot and every public replay gate.

| Contribution | Supporting artifacts |
|---|---|
| C1 | A1, A2, A4 |
| C2 | A1, A2, A4 |
| C3 | A1, A2, A3, A4 |

## Part 2 — Expected results

The verified command must exit with status 0 and report `PASS`. The central
expected values are:

- 16,559 / 18,283 selected Prims;
- 8,906 common, 7,653 removed, 9,377 added, and 25,936 union paths;
- 71 / 85 Payload landmarks and zero Reference landmarks in both states;
- 115 regions: 44 added, 30 removed, one changed, 40 unchanged;
- exactly-once ownership of 34,842 state-specific records;
- 17,041 expanded paths, including 11 unchanged context paths;
- exact second-comparison equality for all 17,030 differences;
- 75 affected regions with 4–413 differences per region, median 156, and
  22/41/58 regions needed to reach 50/75/90 percent; and
- JSON, SQLite, and trie reconstruction equality for both ordered projections.

These results support C1–C3 at the publication-safe record level. They do not
reexecute production Stage opening or independently establish physical truth.

## Part 3 — Expected reproduction time

| Phase | Expected time |
|---|---:|
| Setup | 1 minute |
| Artifact execution | under 1 minute |
| Output inspection and claim comparison | 2 minutes |

The complete path is far below the eight-hour SC26 AE budget.

## Part 4 — Artifact setup

### Hardware

- One ordinary CPU core; no GPU or accelerator is required.
- At least 1 GiB free memory and 100 MiB free disk space.

### Software

- CPython 3.10 or newer.
- No third-party Python packages, compiler, container, Isaac Sim, or OpenUSD
  installation is needed for the public replay.

### Recorded production environment

The retained extraction audit was produced with NVIDIA Isaac Sim 6.0.0 full
Kit, internal build `6.0.0-rc.59+release.41464.5f2772bc.gl`, bundled OpenUSD
0.25.11, and the opening contract recorded in
`data/audit_only/environment_summary.json`. This runtime is provenance for the
withheld production extraction; evaluators do not need it for the public replay.

### Dataset/input

`earlier_full_projection.csv` and `later_full_projection.csv` contain exactly
four scientific fields plus one encoding marker. Their release hashes are
verified before parsing. All paths use pair-stable hierarchy tokens; no reverse
mapping is provided.

### Installation and deployment

Clone the tagged release and run commands from its root. Installation is not
required. An editable installation is optional; commands are still run from
the tagged repository root and produce the same results.

## Part 5 — Artifact evaluation workflow

The one-command workflow has these explicit tasks:

1. **T1 — Input and release integrity:** verify the release manifest, input
   hashes, strict schema, path encoding, ordering, uniqueness, and parent
   closure.
2. **T2 — Original record comparison:** compute additions, removals, and
   common-path difference types from the complete selected-record union.
3. **T3 — Hierarchy regions:** find authored Reference/Payload landmarks,
   assign each selected Prim to its nearest ancestor-or-self landmark or the
   residual region, and use the union of landmark paths to identify the
   cross-state regions.
4. **T4 — Expansion and second comparison:** expand every affected region and
   run the same exact comparison on the rebuilt restricted record sets.
5. **T5 — Secondary checks:** calculate the ranked region distribution,
   produce an SVG, and reconstruct the ordered records through JSON, SQLite,
   and a trie.
6. **T6 — Acceptance:** compare every result with A4, scan the publication
   boundary, and write deterministic reports.

Dependency order: `T1 -> T2 -> T3 -> T4 -> T5 -> T6`.

Run:

```bash
python -m stage_xray_artifact reproduce \
  --data data/publication_safe \
  --out build/reproduction \
  --verify
python -m unittest discover -s tests -v
```

The output directory must not already contain files. To repeat the run, choose
a second output directory; the two output trees should be byte-identical.

## Part 6 — Artifact analysis

Read `build/reproduction/reproduction_report.md` first. Then inspect:

- `claim_results.json` for the RQ-ordered values;
- `verification.json` for frozen-value, manifest, and privacy status;
- `region_distribution.csv` and `figure3-reproduced.svg` for the grouping
  result; and
- `storage_reconstruction.json` for representation equality.

The expected-reproduction test runs the complete workflow twice and compares
every generated byte. Any numerical, difference-type, ordering, privacy, or release-file
deviation fails closed.

Official guidance used for this structure:

- <https://hpc-oda.org/workshop2026/>
- <https://sc26.supercomputing.org/program/papers/ad-ae-appendices/>
