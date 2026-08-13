# Claim-to-artifact matrix

`RECOMPUTED` means a public evaluator recalculates the value from the two
sanitized projections. `RETAINED-AUDIT` means the artifact preserves a final
publication-safe audit record but the private source measurement cannot be
rerun. `NOT-PUBLICLY-REEXECUTABLE` marks a deliberately withheld input tier.

| Paper element | Manuscript-linked result or retained supporting audit | Artifact source | Public level | Acceptance gate |
|---|---|---|---|---|
| Table II | Four-field selected-Prim record schema | Projection CSVs and `docs/DATA_DICTIONARY.md` | RECOMPUTED | Strict schema and field-order checks |
| Table III | 16,559 / 18,283 selected Prims; 8,906 common, 7,653 removed, 9,377 added, and 25,936 union paths | `compare.py` and the two projections | RECOMPUTED | Strict row counts, hashes, and five difference-type totals |
| Table IV | 71 / 85 Payload landmarks, zero Reference landmarks; 115 regions and 44/30/1/40 status partition | `regions.py` and the projections | RECOMPUTED | Landmark counts, union identities, and canonical region records |
| Table IV | 34,842 exactly-once ownership rows | `regions.py` | RECOMPUTED | No missing or duplicate owner |
| Table IV | 17,041 expanded paths and exact 17,030/17,030 recomparison | `regions.py` and `compare.py` | RECOMPUTED | Zero missing, extra, or duplicate difference |
| Fig. 3 | 75 affected regions and ranked distribution | `distribution.py`, `region_distribution.csv`, and `figure3-reproduced.svg` | RECOMPUTED | 17,030 paths assigned once; 4--413 and 22/41/58 gates |
| Table V | JSON/SQLite/trie equality | `reconstruction.py` | RECOMPUTED | Ordered equality for both states |
| Table V | Isaac Sim 6.0.0, OpenUSD 0.25.11, fixed opening contract, and three fresh processes per state | `data/audit_only/environment_summary.json`, `repeatability_summary.json`, and six summaries | RETAINED-AUDIT | Runtime commitments and six final summaries |
| Fig. 1 | Conceptual workflow and its displayed aggregate counts | The comparison, region, expansion, and recomparison outputs above | MIXED | All displayed counts are covered by their corresponding acceptance gates |
| Fig. 2 | Spatial context only | Production rendering and Stages withheld | NOT-PUBLICLY-REEXECUTABLE | Privacy boundary documented |
| Supporting audit, not directly reported | 58,097 / 59,821 whole-Dream-AI population and zero differences outside ScaleX-POD | `data/audit_only/domain_audit_summary.json` | RETAINED-AUDIT | Final aggregate audit values |
| Initial Stage opening and record extraction | Production Stage opening and four-field extraction | Withheld Stage assets and resolver configuration | NOT-PUBLICLY-REEXECUTABLE | Maintainer-only procedure |

The recomparison deliberately reuses the same exact comparison function on
affected-region records. It validates preservation and return to the
original record comparison; it is not an implementation-independent oracle.
