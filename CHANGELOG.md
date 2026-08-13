# Changelog

## v4.0.1 — 2026-08-13

- Synchronized the paper title and citation metadata with the final manuscript.
- Aligned the artifact description with the manuscript's two contributions and
  replaced reader-facing RQ labels with result-stage headings.
- Standardized reader-facing `recomparison` and `extra difference` terminology.
- Added explicit paper-element mappings and manuscript-aligned Figure 3 axes
  and cumulative-threshold markers.
- Preserved the measured inputs, algorithm, numerical results, public schema,
  evidence levels, privacy boundary, and deterministic replay gates from
  v4.0.0.

## v4.0.0 — 2026-08-11

- Aligned public terminology and schema names with the final manuscript:
  original record comparison, landmark, region, and difference type.
- Replaced public `ANCHOR` identifiers with `LANDMARK` identifiers and removed
  `aligned region` and `exact baseline` terminology.
- Clarified Earlier/Later as comparison-side names without asserting temporal
  or physical ground truth.
- Marked whole-Dream-AI counts as retained supporting audit values that are not
  directly reported in the manuscript.
- Preserved the measured inputs, numerical results, evidence levels, privacy
  boundary, and deterministic replay gates from v3.0.0.

## v3.0.0 — 2026-08-11

- Published the submission artifact for the paper.
- Bound retained production evidence to NVIDIA Isaac Sim 6.0.0, bundled
  OpenUSD 0.25.11, and six fresh full-Kit processes.
- Added a standard-library public replay from publication-safe four-field
  projections.
- Added exact claim gates, deterministic outputs, privacy and manifest checks,
  synthetic branch coverage, and AD/AE documentation.
- Separated publicly recomputed results from retained audits that depend on
  withheld production inputs.
