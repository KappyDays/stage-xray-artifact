# Claim-to-artifact matrix

`RECOMPUTED` means a public evaluator recalculates the value from the two
sanitized projections. `RETAINED-AUDIT` means the artifact preserves a final
publication-safe audit record but the private source measurement cannot be
rerun. `NOT-PUBLICLY-REEXECUTABLE` marks a deliberately withheld input tier.

| Paper result or check | Artifact source | Public level | Acceptance gate |
|---|---|---|---|
| 16,559 / 18,283 selected Prims | Two projection CSVs | RECOMPUTED | Strict row counts and hashes |
| 8,906 common, 7,653 removed, 9,377 added, 25,936 union | `compare.py` + projections | RECOMPUTED | Exact counts and five-label mask totals |
| 71 / 85 Payload landmarks, zero Reference landmarks | `regions.py` + projections | RECOMPUTED | Landmark flags counted directly |
| 115 aligned regions and 44/30/1/40 status partition | `regions.py` | RECOMPUTED | Starting-path alignment and canonical facts |
| 34,842 exactly-once ownership rows | `regions.py` | RECOMPUTED | No missing or duplicate owner |
| 75 affected regions and ranked distribution | `distribution.py` | RECOMPUTED | 17,030 paths assigned once; 4–413 and 22/41/58 gates |
| 17,041 expansion and exact 17,030/17,030 second comparison | `regions.py` + `compare.py` | RECOMPUTED | Zero miss, extra, or duplicate |
| JSON/SQLite/trie equality | `reconstruction.py` | RECOMPUTED | Ordered equality for both states |
| Isaac Sim 6.0.0, OpenUSD 0.25.11, and fixed opening contract | `data/audit_only/environment_summary.json` | RETAINED-AUDIT | Runtime and binary commitments |
| Three fresh processes per state | `data/audit_only/repeatability_summary.json` and six summaries | RETAINED-AUDIT | Six summaries and final pass record |
| 58,097 / 59,821 whole-Dream-AI population and zero differences outside ScaleX-POD | `data/audit_only/domain_audit_summary.json` | RETAINED-AUDIT | Final aggregate audit values |
| Initial Stage opening and record extraction | Withheld Stage assets and resolver configuration | NOT-PUBLICLY-REEXECUTABLE | Maintainer-only procedure |

The second comparison deliberately reuses the same exact comparison function
on affected-region records. It validates preservation and return to the
baseline; it is not an implementation-independent oracle.
