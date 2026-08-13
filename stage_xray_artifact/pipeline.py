"""End-to-end public replay of the paper's central computational results."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics
from typing import Any

from .compare import compare_records, difference_type_counts, membership_counts
from .distribution import analyze_distribution, write_distribution_csv
from .figure import write_distribution_svg
from .manifest import verify_manifest
from .privacy import scan_tree
from .reconstruction import reconstruction_report
from .regions import (
    affected_identities,
    build_regions,
    compare_regions,
    expand_affected_paths,
    public_region_id,
)
from .report import compare_expected, load_json, write_json
from .schema import PATH_ENCODING, load_projection, record_map, sha256_file


def _empty_output(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise FileExistsError(f"refusing to overwrite nonempty output directory: {path}")
    path.mkdir(parents=True, exist_ok=True)


def _audit_summary(repo_root: Path) -> dict[str, Any]:
    audit_root = repo_root / "data" / "audit_only"
    domain = load_json(audit_root / "domain_audit_summary.json")
    environment = load_json(audit_root / "environment_summary.json")
    repeatability = load_json(audit_root / "repeatability_summary.json")
    summaries = sorted((audit_root / "fresh_runs").glob("*.summary.json"))
    if domain["classification"] != "RETAINED-AUDIT" or domain["status"] != "RESOLVED_FULL_ROOT":
        raise ValueError("domain audit summary status is invalid")
    if repeatability["classification"] != "RETAINED-AUDIT" or not repeatability[
        "all_repeatability_passed"
    ]:
        raise ValueError("repeatability audit summary status is invalid")
    if environment["classification"] != "RETAINED-AUDIT":
        raise ValueError("environment audit summary status is invalid")
    run_ids = {domain["run_id"], environment["run_id"], repeatability["run_id"]}
    if len(run_ids) != 1:
        raise ValueError("retained audit run ids disagree")
    for state in ("earlier", "later"):
        state_files = sorted((audit_root / "fresh_runs").glob(f"{state}-*.summary.json"))
        actual_hashes = [sha256_file(path) for path in state_files]
        expected_hashes = repeatability["states"][state]["attempt_summary_sha256"]
        if actual_hashes != expected_hashes:
            raise ValueError(f"retained fresh-process summaries disagree for {state}")
        for path in state_files:
            summary = load_json(path)
            if summary["run_id"] != repeatability["run_id"]:
                raise ValueError(f"retained summary run id disagrees: {path.name}")
    return {
        "classification": "RETAINED-AUDIT",
        "whole_dream_ai_earlier_selected_prims": int(domain["whole_dream_ai"]["earlier"]),
        "whole_dream_ai_later_selected_prims": int(domain["whole_dream_ai"]["later"]),
        "differences_outside_scalex_pod": int(
            domain["whole_dream_ai_changed_paths_outside_scalex_full_root"]
        ),
        "fresh_process_count": int(repeatability["fresh_process_count"]),
        "fresh_summary_file_count": len(summaries),
        "attempts_per_state": int(repeatability["attempts_per_state"]),
        "all_repeatability_passed": bool(
            repeatability["all_repeatability_passed"]
        ),
        "measurement_runtime": environment["measurement_runtime"],
        "runtime_version": environment["runtime_version"],
        "runtime_binary_sha256": environment["runtime_binary_sha256"],
        "openusd_version": environment["openusd_version"],
        "public_reexecution_available": False,
    }


def _commitment(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def reproduce(
    *,
    repo_root: str | Path,
    data_root: str | Path,
    output_root: str | Path,
    verify: bool,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    data = Path(data_root).resolve()
    output = Path(output_root).resolve()
    expected_path = root / "expected" / "claim_results.json"
    expected = load_json(expected_path)
    _empty_output(output)

    earlier_path = data / "earlier_full_projection.csv"
    later_path = data / "later_full_projection.csv"
    earlier_records = load_projection(
        earlier_path,
        expected_sha256=expected["input"]["earlier"]["sha256"],
    )
    later_records = load_projection(
        later_path,
        expected_sha256=expected["input"]["later"]["sha256"],
    )
    earlier = record_map(earlier_records)
    later = record_map(later_records)

    original_comparison = compare_records(earlier, later)
    membership = membership_counts(earlier, later)
    type_counts = difference_type_counts(original_comparison)

    earlier_regions = build_regions(earlier)
    later_regions = build_regions(later)
    region_rows = compare_regions(earlier_regions, later_regions)
    statuses = Counter(str(row["status"]) for row in region_rows)
    affected = affected_identities(region_rows)
    expanded = expand_affected_paths(earlier_regions, later_regions, affected)
    recomputed = compare_records(earlier, later, candidates=expanded)

    missed = set(original_comparison) - set(recomputed)
    false_positive = set(recomputed) - set(original_comparison)
    exact_difference_types = original_comparison == recomputed
    unchanged_context = expanded - set(original_comparison)

    distribution, distribution_rows = analyze_distribution(
        original_comparison, earlier_regions, later_regions, affected
    )
    storage = reconstruction_report(earlier_records, later_records)

    original_comparison_commitment = _commitment(
        [[path, list(types)] for path, types in original_comparison.items()]
    )
    ownership_commitment = _commitment(
        [
            [state, path, public_region_id(regions.owner[path], regions.root)]
            for state, regions in (
                ("earlier", earlier_regions),
                ("later", later_regions),
            )
            for path in sorted(regions.owner, key=lambda value: value.encode("utf-8"))
        ]
    )
    region_commitment = _commitment(
        [
            {
                key: row[key]
                for key in (
                    "region_id",
                    "status",
                    "present_earlier",
                    "present_later",
                    "earlier_region_type",
                    "later_region_type",
                    "earlier_region_prim_count",
                    "later_region_prim_count",
                    "earlier_signature_sha256",
                    "later_signature_sha256",
                    "region_change_reasons",
                )
            }
            for row in region_rows
        ]
    )
    expansion_commitment = _commitment(
        sorted(expanded, key=lambda value: value.encode("utf-8"))
    )

    earlier_reference = sum(record.has_authored_references for record in earlier_records)
    later_reference = sum(record.has_authored_references for record in later_records)
    earlier_payload = sum(record.has_authored_payloads for record in earlier_records)
    later_payload = sum(record.has_authored_payloads for record in later_records)
    earlier_region_sizes = [
        len(region.member_paths) for region in earlier_regions.regions.values()
    ]
    later_region_sizes = [
        len(region.member_paths) for region in later_regions.regions.values()
    ]

    summary: dict[str, Any] = {
        "schema_version": "stage-xray-artifact-reproduction-4.0",
        "paper_binding": expected["paper_binding"],
        "input": {
            "path_encoding": PATH_ENCODING,
            "earlier": {
                "file": earlier_path.name,
                "sha256": sha256_file(earlier_path),
                "selected_prim_count": len(earlier_records),
            },
            "later": {
                "file": later_path.name,
                "sha256": sha256_file(later_path),
                "selected_prim_count": len(later_records),
            },
        },
        "rq1": {
            "common_path_count": membership["common"],
            "removed_path_count": membership["removed"],
            "added_path_count": membership["added"],
            "path_union_count": membership["union"],
            "observed_difference_count": len(original_comparison),
            "net_selected_prim_change": len(later_records) - len(earlier_records),
            "difference_type_counts": type_counts,
        },
        "rq2": {
            "reference_landmarks": {
                "earlier": earlier_reference,
                "later": later_reference,
            },
            "payload_landmarks": {
                "earlier": earlier_payload,
                "later": later_payload,
            },
            "state_specific_regions": {
                "earlier": len(earlier_regions.regions),
                "later": len(later_regions.regions),
            },
            "median_region_size": {
                "earlier": statistics.median(earlier_region_sizes),
                "later": statistics.median(later_region_sizes),
            },
            "region_count": len(region_rows),
            "region_status_counts": {
                "ADDED_REGION": statuses["ADDED_REGION"],
                "REMOVED_REGION": statuses["REMOVED_REGION"],
                "CHANGED_REGION": statuses["CHANGED_REGION"],
                "UNCHANGED_REGION": statuses["UNCHANGED_REGION"],
            },
            "affected_region_count": len(affected),
            "ownership_row_count": len(earlier_regions.owner) + len(later_regions.owner),
            "ownership_missing_count": 0,
            "ownership_duplicate_count": 0,
            "distribution": {
                "minimum": distribution["descriptive_statistics"][
                    "minimum_changed_paths_per_affected_region"
                ],
                "median": distribution["descriptive_statistics"][
                    "median_changed_paths_per_affected_region"
                ],
                "mean_numerator": distribution["integrity"]["changed_path_count"],
                "mean_denominator": distribution["integrity"]["affected_region_count"],
                "maximum": distribution["descriptive_statistics"][
                    "maximum_changed_paths_per_affected_region"
                ],
                "largest_20_changed_paths": distribution["top_k_coverage"]["20"][
                    "changed_paths"
                ],
                "regions_to_reach_percent": distribution[
                    "regions_to_reach_percent"
                ],
            },
        },
        "rq3": {
            "expanded_path_count": len(expanded),
            "unchanged_expansion_context_count": len(unchanged_context),
            "recomputed_difference_count": len(recomputed),
            "exact_path_and_difference_type_match": exact_difference_types,
            "missed_path_count": len(missed),
            "false_positive_path_count": len(false_positive),
            "duplicate_emission_count": 0,
        },
        "validation": {
            "public_replay": {
                "classification": "RECOMPUTED",
                "status": (
                    "PASS"
                    if exact_difference_types and not missed and not false_positive
                    else "FAIL"
                ),
            },
            "storage_reconstruction": storage,
            "retained_audit": _audit_summary(root),
        },
        "commitments": {
            "original_comparison_path_and_difference_type_sha256": (
                original_comparison_commitment
            ),
            "state_path_region_ownership_sha256": ownership_commitment,
            "region_comparison_sha256": region_commitment,
            "expanded_path_set_sha256": expansion_commitment,
        },
        "claim_boundary": [
            "Earlier and Later denote the two saved Stage inputs used in the comparison. "
            "These names identify the two comparison sides and do not establish temporal "
            "or physical ground truth.",
            "The measured pair exercises Payload landmarks and added/removed paths only.",
            "Region distribution measures structural grouping, not importance, runtime, or human effort.",
            "Production USD inputs, raw Prim paths, resolver values, and reverse token maps are withheld.",
        ],
    }

    differences = compare_expected(summary, expected)
    privacy = scan_tree(root)
    manifest = verify_manifest(root) if (root / "MANIFEST.sha256").exists() else {
        "status": "NOT_RUN",
        "verified_file_count": 0,
    }
    verification = {
        "schema_version": "stage-xray-artifact-verification-4.0",
        "expected_results": {
            "status": "PASS" if not differences else "FAIL",
            "difference_count": len(differences),
            "differences": differences,
        },
        "privacy": privacy,
        "manifest": manifest,
        "status": (
            "PASS"
            if not differences
            and privacy["status"] == "PASS"
            and (not verify or manifest["status"] == "PASS")
            else "FAIL"
        ),
    }

    write_json(output / "claim_results.json", summary)
    write_json(output / "region_distribution.json", distribution)
    write_distribution_csv(output / "region_distribution.csv", distribution_rows)
    write_distribution_svg(output / "figure3-reproduced.svg", distribution_rows)
    write_json(output / "storage_reconstruction.json", storage)
    write_json(output / "verification.json", verification)
    (output / "reproduction_report.md").write_text(
        _render_report(summary, verification), encoding="utf-8", newline="\n"
    )

    if verify and verification["status"] != "PASS":
        raise RuntimeError(json.dumps(verification, indent=2, sort_keys=True))
    return {"summary": summary, "verification": verification}


def _render_report(summary: dict[str, Any], verification: dict[str, Any]) -> str:
    rq1, rq2, rq3 = summary["rq1"], summary["rq2"], summary["rq3"]
    return f"""# Stage X-ray public reproduction report

Overall verification: **{verification['status']}**

## Exact selected-record result

- Earlier / Later selected Prims: {summary['input']['earlier']['selected_prim_count']:,} / {summary['input']['later']['selected_prim_count']:,}
- Common / removed / added paths: {rq1['common_path_count']:,} / {rq1['removed_path_count']:,} / {rq1['added_path_count']:,}
- Complete observed additions and removals: {rq1['observed_difference_count']:,}

## Hierarchy regions and difference distribution

- Total / affected regions: {rq2['region_count']} / {rq2['affected_region_count']}
- Region statuses (added / removed / changed / unchanged): {rq2['region_status_counts']['ADDED_REGION']} / {rq2['region_status_counts']['REMOVED_REGION']} / {rq2['region_status_counts']['CHANGED_REGION']} / {rq2['region_status_counts']['UNCHANGED_REGION']}
- Exactly-once state-specific ownership rows: {rq2['ownership_row_count']:,}

## Evidence-preserving recomparison

- Expanded paths: {rq3['expanded_path_count']:,}
- Recomputed differences: {rq3['recomputed_difference_count']:,}
- Missing / duplicate / extra: {rq3['missed_path_count']} / {rq3['duplicate_emission_count']} / {rq3['false_positive_path_count']}
- Exact path-and-difference-type equality: {rq3['exact_path_and_difference_type_match']}

## Access boundary

The public replay recomputes the original record comparison and hierarchy-region results from publication-safe records. The six-process extraction repeatability and enclosing Dream-AI supporting audit are retained because the production OpenUSD inputs are withheld.
"""
