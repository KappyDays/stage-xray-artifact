"""Reference/Payload landmark regions used by the submitted paper."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping

from .schema import ROOT_PATH, Record, parent_path


RESIDUAL_IDENTITY = "__ROOT_LOCAL_RESIDUAL__"
REGION_SIGNATURE_DOMAIN = "stage-xray:step1:public-region-signature:1"
REGION_CORE_MASKS = (
    "REGION_ADDED",
    "REGION_REMOVED",
    "ANCHOR_TYPE_CHANGED",
    "REFERENCE_PRESENCE_CHANGED",
    "PAYLOAD_PRESENCE_CHANGED",
    "COLLAPSED_SIGNATURE_CHANGED",
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _domain_hash(domain: str, value: Any) -> str:
    return hashlib.sha256(domain.encode("ascii") + b"\x00" + _canonical(value)).hexdigest()


def _inside(path: str, root: str) -> bool:
    return path == root or path.startswith(root + "/")


def _region_id(identity: str, root: str) -> str:
    if identity == RESIDUAL_IDENTITY:
        return f"RESIDUAL@{root}"
    return f"ANCHOR@{identity}"


def _relative(path: str, identity: str, root: str) -> str:
    owner = root if identity == RESIDUAL_IDENTITY else identity
    if path == owner:
        return "."
    prefix = owner + "/"
    if not path.startswith(prefix):
        raise ValueError(f"path {path} is outside region owner {owner}")
    return path[len(prefix) :]


@dataclass(frozen=True, slots=True)
class Region:
    identity: str
    region_id: str
    region_type: str
    parent_identity: str | None
    member_paths: tuple[str, ...]
    canonical_facts: tuple[tuple[tuple[str, Any], ...], ...]
    signature_sha256: str


@dataclass(slots=True)
class StateRegions:
    records: Mapping[str, Record]
    root: str
    anchors: tuple[str, ...]
    owner: dict[str, str]
    regions: dict[str, Region]


def build_regions(
    records: Mapping[str, Record], *, root: str = ROOT_PATH
) -> StateRegions:
    if root not in records:
        raise ValueError(f"scope root is absent: {root}")
    anchors = tuple(
        sorted(
            (
                path
                for path, record in records.items()
                if record.has_authored_references or record.has_authored_payloads
            ),
            key=lambda value: value.encode("utf-8"),
        )
    )
    anchor_set = set(anchors)
    parent_anchor: dict[str, str | None] = {}
    for anchor in anchors:
        current = parent_path(anchor)
        selected: str | None = None
        while current is not None and _inside(current, root):
            if current in anchor_set:
                selected = current
                break
            current = parent_path(current)
        parent_anchor[anchor] = selected

    owner: dict[str, str] = {}
    for path in sorted(records, key=lambda value: value.encode("utf-8")):
        current: str | None = path
        selected_owner = RESIDUAL_IDENTITY
        while current is not None and _inside(current, root):
            if current in anchor_set:
                selected_owner = current
                break
            current = parent_path(current)
        owner[path] = selected_owner

    members: dict[str, list[str]] = defaultdict(list)
    for path, identity in owner.items():
        members[identity].append(path)
    for paths in members.values():
        paths.sort(key=lambda value: value.encode("utf-8"))

    regions: dict[str, Region] = {}
    for identity in sorted(
        members, key=lambda value: _region_id(value, root).encode("utf-8")
    ):
        region_paths = tuple(members[identity])
        facts = [
            {
                "relative_prim_path": _relative(path, identity, root),
                "prim_type_name": records[path].prim_type_name,
                "has_authored_references": records[path].has_authored_references,
                "has_authored_payloads": records[path].has_authored_payloads,
            }
            for path in region_paths
        ]
        facts.sort(key=lambda row: row["relative_prim_path"].encode("utf-8"))
        parent = None if identity == RESIDUAL_IDENTITY else parent_anchor[identity]
        region_type = (
            "ROOT_LOCAL_RESIDUAL_REGION"
            if identity == RESIDUAL_IDENTITY
            else "NESTED_ANCHOR_REGION"
            if parent is not None
            else "ANCHOR_OWNED_REGION"
        )
        regions[identity] = Region(
            identity=identity,
            region_id=_region_id(identity, root),
            region_type=region_type,
            parent_identity=parent,
            member_paths=region_paths,
            canonical_facts=tuple(tuple(fact.items()) for fact in facts),
            signature_sha256=_domain_hash(REGION_SIGNATURE_DOMAIN, facts),
        )

    if len(owner) != len(records) or set(owner) != set(records):
        raise ValueError("region ownership is incomplete")
    if sum(len(region.member_paths) for region in regions.values()) != len(records):
        raise ValueError("region ownership is not exactly once")
    return StateRegions(
        records=records,
        root=root,
        anchors=anchors,
        owner=owner,
        regions=regions,
    )


def compare_regions(
    earlier: StateRegions, later: StateRegions
) -> list[dict[str, Any]]:
    if earlier.root != later.root:
        raise ValueError("region roots differ")
    rows: list[dict[str, Any]] = []
    identities = sorted(
        set(earlier.regions) | set(later.regions),
        key=lambda value: _region_id(value, earlier.root).encode("utf-8"),
    )
    for identity in identities:
        e_region = earlier.regions.get(identity)
        l_region = later.regions.get(identity)
        masks: list[str] = []
        if e_region is None:
            masks.append("REGION_ADDED")
        elif l_region is None:
            masks.append("REGION_REMOVED")
        else:
            if identity != RESIDUAL_IDENTITY:
                e_anchor = earlier.records[identity]
                l_anchor = later.records[identity]
                if e_anchor.prim_type_name != l_anchor.prim_type_name:
                    masks.append("ANCHOR_TYPE_CHANGED")
                if (
                    e_anchor.has_authored_references
                    != l_anchor.has_authored_references
                ):
                    masks.append("REFERENCE_PRESENCE_CHANGED")
                if e_anchor.has_authored_payloads != l_anchor.has_authored_payloads:
                    masks.append("PAYLOAD_PRESENCE_CHANGED")
            if e_region.canonical_facts != l_region.canonical_facts:
                masks.append("COLLAPSED_SIGNATURE_CHANGED")
        masks = [mask for mask in REGION_CORE_MASKS if mask in masks]
        if e_region is None:
            status = "ADDED_REGION"
        elif l_region is None:
            status = "REMOVED_REGION"
        elif masks:
            status = "CHANGED_REGION"
        else:
            status = "UNCHANGED_REGION"
        rows.append(
            {
                "identity": identity,
                "region_id": _region_id(identity, earlier.root),
                "status": status,
                "present_earlier": e_region is not None,
                "present_later": l_region is not None,
                "earlier_region_type": None if e_region is None else e_region.region_type,
                "later_region_type": None if l_region is None else l_region.region_type,
                "earlier_region_prim_count": 0 if e_region is None else len(e_region.member_paths),
                "later_region_prim_count": 0 if l_region is None else len(l_region.member_paths),
                "earlier_signature_sha256": None if e_region is None else e_region.signature_sha256,
                "later_signature_sha256": None if l_region is None else l_region.signature_sha256,
                "core_change_masks": masks,
            }
        )
    return rows


def affected_identities(region_rows: list[dict[str, Any]]) -> set[str]:
    return {
        str(row["identity"])
        for row in region_rows
        if row["status"] != "UNCHANGED_REGION"
    }


def expand_affected_paths(
    earlier: StateRegions,
    later: StateRegions,
    affected: set[str],
) -> set[str]:
    expanded: set[str] = set()
    for identity in affected:
        if identity in earlier.regions:
            expanded.update(earlier.regions[identity].member_paths)
        if identity in later.regions:
            expanded.update(later.regions[identity].member_paths)
    return expanded


def public_region_id(identity: str, root: str = ROOT_PATH) -> str:
    return _region_id(identity, root)
