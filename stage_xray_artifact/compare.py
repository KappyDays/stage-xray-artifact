"""Exact comparison of four-field selected-Prim records."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping

from .schema import Record


CHANGE_LABELS = (
    "ADDED",
    "REMOVED",
    "TYPE_CHANGED",
    "REFERENCE_PRESENCE_CHANGED",
    "PAYLOAD_PRESENCE_CHANGED",
)


def compare_records(
    earlier: Mapping[str, Record],
    later: Mapping[str, Record],
    *,
    candidates: Iterable[str] | None = None,
) -> dict[str, tuple[str, ...]]:
    """Return every path whose membership or retained fields differ."""

    paths = set(earlier) | set(later) if candidates is None else set(candidates)
    unknown = paths.difference(set(earlier) | set(later))
    if unknown:
        raise ValueError(f"candidate set contains {len(unknown)} unknown paths")

    result: dict[str, tuple[str, ...]] = {}
    for path in sorted(paths, key=lambda value: value.encode("utf-8")):
        masks: list[str] = []
        if path not in earlier:
            masks.append("ADDED")
        elif path not in later:
            masks.append("REMOVED")
        else:
            if earlier[path].prim_type_name != later[path].prim_type_name:
                masks.append("TYPE_CHANGED")
            if (
                earlier[path].has_authored_references
                != later[path].has_authored_references
            ):
                masks.append("REFERENCE_PRESENCE_CHANGED")
            if (
                earlier[path].has_authored_payloads
                != later[path].has_authored_payloads
            ):
                masks.append("PAYLOAD_PRESENCE_CHANGED")
        if masks:
            result[path] = tuple(masks)
    return result


def membership_counts(
    earlier: Mapping[str, Record], later: Mapping[str, Record]
) -> dict[str, int]:
    e_paths = set(earlier)
    l_paths = set(later)
    return {
        "earlier": len(e_paths),
        "later": len(l_paths),
        "common": len(e_paths & l_paths),
        "removed": len(e_paths - l_paths),
        "added": len(l_paths - e_paths),
        "union": len(e_paths | l_paths),
        "unique_path_membership_difference": len(e_paths ^ l_paths),
    }


def mask_counts(diff: Mapping[str, tuple[str, ...]]) -> dict[str, int]:
    counts = Counter(mask for masks in diff.values() for mask in masks)
    return {label: counts[label] for label in CHANGE_LABELS}
