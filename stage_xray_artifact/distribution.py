"""Deterministic changed-path distribution across affected regions."""

from __future__ import annotations

from collections import defaultdict
import csv
from pathlib import Path
import statistics
from typing import Any, Mapping

from .regions import StateRegions, public_region_id


def analyze_distribution(
    diff: Mapping[str, tuple[str, ...]],
    earlier: StateRegions,
    later: StateRegions,
    affected: set[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"added": 0, "removed": 0}
    )
    seen: set[str] = set()
    affected_region_ids = {public_region_id(identity, earlier.root) for identity in affected}

    for path, masks in diff.items():
        if "ADDED" in masks:
            state, field, identity = later, "added", later.owner[path]
        elif "REMOVED" in masks:
            state, field, identity = earlier, "removed", earlier.owner[path]
        else:
            continue
        if path in seen:
            raise ValueError(f"duplicate changed path: {path}")
        seen.add(path)
        if path not in state.owner:
            raise ValueError(f"changed path has no region owner: {path}")
        region_id = public_region_id(identity, state.root)
        if region_id not in affected_region_ids:
            raise ValueError(f"changed path belongs to an unaffected region: {path}")
        counts[region_id][field] += 1

    rows: list[dict[str, Any]] = []
    for region_id in affected_region_ids:
        added = counts[region_id]["added"]
        removed = counts[region_id]["removed"]
        total = added + removed
        if total == 0:
            raise ValueError(f"affected region has no added or removed paths: {region_id}")
        rows.append(
            {"region_id": region_id, "added": added, "removed": removed, "total": total}
        )
    rows.sort(key=lambda row: (-row["total"], row["region_id"].encode("utf-8")))

    changed_total = sum(row["total"] for row in rows)
    cumulative = 0
    for rank, row in enumerate(rows, 1):
        cumulative += row["total"]
        row["rank"] = rank
        row["cumulative_total"] = cumulative
        row["cumulative_fraction"] = cumulative / changed_total

    totals = [int(row["total"]) for row in rows]
    top_k: dict[str, dict[str, int | float]] = {}
    for k in (1, 5, 10, 20, 40, len(rows)):
        subtotal = sum(int(row["total"]) for row in rows[:k])
        top_k[str(k)] = {
            "changed_paths": subtotal,
            "fraction": subtotal / changed_total,
        }

    thresholds: dict[str, int] = {}
    for label, threshold in (("50", 0.50), ("75", 0.75), ("90", 0.90)):
        thresholds[label] = next(
            int(row["rank"])
            for row in rows
            if float(row["cumulative_fraction"]) >= threshold
        )

    summary: dict[str, Any] = {
        "schema_version": "stage-xray-region-distribution-3.0",
        "integrity": {
            "affected_region_count": len(rows),
            "unique_changed_path_count": len(seen),
            "added_path_count": sum(int(row["added"]) for row in rows),
            "removed_path_count": sum(int(row["removed"]) for row in rows),
            "changed_path_count": changed_total,
            "status": "PASS",
        },
        "descriptive_statistics": {
            "minimum_changed_paths_per_affected_region": min(totals),
            "median_changed_paths_per_affected_region": statistics.median(totals),
            "mean_changed_paths_per_affected_region": statistics.fmean(totals),
            "maximum_changed_paths_per_affected_region": max(totals),
        },
        "top_k_coverage": top_k,
        "regions_to_reach_percent": thresholds,
        "interpretation_boundary": (
            "Descriptive grouping only; not runtime, human effort, importance, "
            "causality, physical change, automatic prioritization, or operational outcome."
        ),
    }
    return summary, rows


def write_distribution_csv(path: str | Path, rows: list[dict[str, Any]]) -> None:
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        fieldnames = (
            "rank",
            "region_id",
            "added",
            "removed",
            "total",
            "cumulative_total",
            "cumulative_fraction",
        )
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
