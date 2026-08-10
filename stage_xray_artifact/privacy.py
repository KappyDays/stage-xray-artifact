"""Fail-closed checks for the publication boundary."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .manifest import is_excluded_path
from .schema import load_projection


DENY_COMPONENTS = (
    ("c:", "\\", "users", "\\"),
    ("c:", "/", "users", "/"),
    ("\\", "onedrive", "\\"),
    ("/", "users", "/"),
    ("/", "home", "/"),
)
DENY_LITERALS = tuple("".join(parts) for parts in DENY_COMPONENTS)
TEXT_SUFFIXES = {
    "",
    ".cff",
    ".csv",
    ".gitattributes",
    ".gitignore",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yml",
    ".yaml",
}


def scan_tree(root: str | Path) -> dict[str, Any]:
    base = Path(root).resolve()
    findings: list[dict[str, str | int]] = []
    scanned = 0
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(base)
        if is_excluded_path(relative):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {
            ".gitignore",
            ".gitattributes",
        }:
            continue
        scanned += 1
        text = path.read_text(encoding="utf-8-sig", errors="strict")
        lowered = text.lower()
        for literal in DENY_LITERALS:
            if literal in lowered:
                findings.append(
                    {
                        "file": relative.as_posix(),
                        "line": lowered[: lowered.index(literal)].count("\n") + 1,
                        "rule": f"denied literal: {literal}",
                    }
                )

    data = base / "data" / "publication_safe"
    for name in ("earlier_full_projection.csv", "later_full_projection.csv"):
        load_projection(data / name)
    return {
        "status": "PASS" if not findings else "FAIL",
        "scanned_file_count": scanned,
        "finding_count": len(findings),
        "findings": findings,
    }
