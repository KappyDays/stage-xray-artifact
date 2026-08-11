# Reproducibility and interpretation limits

## Fully public replay

The artifact fully recomputes the original record comparison, landmark regions,
exactly-once assignment, affected-region expansion, second comparison, region
distribution, and storage-reconstruction check from sanitized records.

## Retained audit only

The Isaac Sim 6.0.0/OpenUSD 0.25.11 environment, six fresh-process extraction
result, and enclosing Dream-AI containment result are preserved as final
publication-safe audit summaries. The public artifact cannot independently
reopen the production Stages or regenerate those summaries because the assets
and resolver configuration are withheld.

## Empirical gaps

- Earlier and Later denote the two saved Stage inputs used in the comparison;
  the names do not establish temporal or physical ground truth.
- The evaluated pair contains Payload landmarks but no Reference landmarks.
- The pair contains additions and removals but no common-path type,
  Reference-presence, or Payload-presence changes.
- The selected root is itself a Payload landmark, so this pair has no residual
  region. Synthetic tests exercise residual and Reference branches.
- Pair-stable tokens preserve hierarchy shape only within the measured pair.

## Unsupported interpretations

The artifact does not measure or establish geometry change, physical asset
identity, movement, causality, diagnosis, repair, performance improvement,
review time, operator effort, importance, automatic prioritization, or
operational outcomes.
