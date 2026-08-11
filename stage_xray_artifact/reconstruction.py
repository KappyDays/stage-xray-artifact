"""Independent logical reconstruction through JSON, SQLite, and a trie."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from typing import Any, Iterable

from .schema import FIELDS, Record


LogicalRow = tuple[str, str, str, str]


def _via_json(source: list[LogicalRow]) -> list[LogicalRow]:
    payload = json.dumps(source, ensure_ascii=True, separators=(",", ":"))
    return [tuple(row) for row in json.loads(payload)]  # type: ignore[list-item]


def _via_sqlite(source: list[LogicalRow]) -> list[LogicalRow]:
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute(
            "CREATE TABLE records (ordinal INTEGER PRIMARY KEY, prim_path TEXT NOT NULL, "
            "prim_type_name TEXT NOT NULL, has_authored_references TEXT NOT NULL, "
            "has_authored_payloads TEXT NOT NULL)"
        )
        connection.executemany(
            "INSERT INTO records VALUES (?, ?, ?, ?, ?)",
            ((ordinal, *record) for ordinal, record in enumerate(source)),
        )
        rows = connection.execute(
            "SELECT prim_path, prim_type_name, has_authored_references, "
            "has_authored_payloads FROM records ORDER BY ordinal"
        ).fetchall()
        return [tuple(row) for row in rows]  # type: ignore[list-item]
    finally:
        connection.close()


def _via_trie(source: list[LogicalRow]) -> list[LogicalRow]:
    trie: dict[str, Any] = {}
    for record in source:
        node = trie
        for part in (part for part in record[0].split("/") if part):
            node = node.setdefault(part, {})
        if "" in node:
            raise ValueError(f"duplicate trie leaf: {record[0]}")
        node[""] = record[1:]

    rebuilt: list[LogicalRow] = []

    def visit(node: dict[str, Any], parts: list[str]) -> None:
        if "" in node:
            rebuilt.append(("/" + "/".join(parts), *node[""]))
        for key in sorted(
            (key for key in node if key), key=lambda value: value.encode("utf-8")
        ):
            visit(node[key], [*parts, key])

    visit(trie, [])
    return rebuilt


def reconstruct_state(records: Iterable[Record]) -> dict[str, Any]:
    source = [record.logical_tuple() for record in records]
    representations = {
        "json": _via_json(source),
        "sqlite": _via_sqlite(source),
        "trie": _via_trie(source),
    }
    equality = {name: decoded == source for name, decoded in representations.items()}
    logical_bytes = json.dumps(
        source, ensure_ascii=True, separators=(",", ":")
    ).encode("utf-8")
    return {
        "record_count": len(source),
        "logical_sequence_sha256": hashlib.sha256(logical_bytes).hexdigest().upper(),
        "representation_equality": equality,
        "status": "PASS" if all(equality.values()) else "FAIL",
    }


def reconstruction_report(
    earlier: Iterable[Record], later: Iterable[Record]
) -> dict[str, Any]:
    report = {
        "schema_version": "stage-xray-independent-storage-reconstruction-4.0",
        "field_order": list(FIELDS),
        "states": {
            "earlier": reconstruct_state(earlier),
            "later": reconstruct_state(later),
        },
        "claim_boundary": (
            "Logical reconstruction of the four publication-safe fields only; not byte "
            "identity, performance, complete OpenUSD semantics, or private-path reconstruction."
        ),
    }
    report["status"] = (
        "PASS"
        if all(state["status"] == "PASS" for state in report["states"].values())
        else "FAIL"
    )
    return report
