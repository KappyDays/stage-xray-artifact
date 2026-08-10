"""Strict loader for the four-field publication-safe record projection."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
from typing import Iterable


FIELDS = (
    "prim_path",
    "prim_type_name",
    "has_authored_references",
    "has_authored_payloads",
)
CSV_FIELDS = (*FIELDS, "path_encoding")
PATH_ENCODING = "PAIR_HIERARCHY_TOKEN_V1"
ROOT_PATH = "/SCALEX_POD"
PUBLIC_PATH = re.compile(r"^/SCALEX_POD(?:/N[0-9]{4})*$")


@dataclass(frozen=True, slots=True)
class Record:
    prim_path: str
    prim_type_name: str
    has_authored_references: bool
    has_authored_payloads: bool

    def logical_tuple(self) -> tuple[str, str, str, str]:
        """Return the exact string-valued logical row used by the storage check."""

        return (
            self.prim_path,
            self.prim_type_name,
            str(self.has_authored_references).lower(),
            str(self.has_authored_payloads).lower(),
        )


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _parse_bool(value: str, *, field: str, line: int) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"line {line}: {field} must be true or false")


def parent_path(path: str) -> str | None:
    parent = path.rpartition("/")[0]
    return parent or None


def validate_parent_closure(paths: Iterable[str], root: str = ROOT_PATH) -> None:
    path_set = set(paths)
    if root not in path_set:
        raise ValueError(f"scope root is absent: {root}")
    for path in path_set:
        if path == root:
            continue
        parent = parent_path(path)
        if parent not in path_set:
            raise ValueError(f"projection lacks parent closure at {path}")


def load_projection(
    path: str | Path,
    *,
    expected_sha256: str | None = None,
    root: str = ROOT_PATH,
) -> list[Record]:
    source = Path(path)
    actual_sha256 = sha256_file(source)
    if expected_sha256 is not None and actual_sha256 != expected_sha256.upper():
        raise ValueError(
            f"input hash mismatch for {source.name}: "
            f"expected {expected_sha256.upper()}, found {actual_sha256}"
        )

    records: list[Record] = []
    seen: set[str] = set()
    with source.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != CSV_FIELDS:
            raise ValueError(
                f"unexpected projection schema in {source.name}: {reader.fieldnames}"
            )
        for line, row in enumerate(reader, 2):
            prim_path = row["prim_path"]
            prim_type_name = row["prim_type_name"]
            if not PUBLIC_PATH.fullmatch(prim_path):
                raise ValueError(f"line {line}: non-public Prim path encoding")
            if prim_path in seen:
                raise ValueError(f"line {line}: duplicate Prim path {prim_path}")
            if not prim_type_name or any(char in prim_type_name for char in "\r\n"):
                raise ValueError(f"line {line}: invalid Prim type name")
            if row["path_encoding"] != PATH_ENCODING:
                raise ValueError(f"line {line}: unexpected path encoding")
            seen.add(prim_path)
            records.append(
                Record(
                    prim_path=prim_path,
                    prim_type_name=prim_type_name,
                    has_authored_references=_parse_bool(
                        row["has_authored_references"],
                        field="has_authored_references",
                        line=line,
                    ),
                    has_authored_payloads=_parse_bool(
                        row["has_authored_payloads"],
                        field="has_authored_payloads",
                        line=line,
                    ),
                )
            )

    ordered_paths = [record.prim_path for record in records]
    if ordered_paths != sorted(ordered_paths, key=lambda value: value.encode("utf-8")):
        raise ValueError(f"projection is not in raw UTF-8 path order: {source.name}")
    validate_parent_closure(ordered_paths, root=root)
    return records


def record_map(records: Iterable[Record]) -> dict[str, Record]:
    result: dict[str, Record] = {}
    for record in records:
        if record.prim_path in result:
            raise ValueError(f"duplicate Prim path: {record.prim_path}")
        result[record.prim_path] = record
    return result
