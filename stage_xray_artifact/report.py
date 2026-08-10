"""Deterministic output helpers and exact expected-result comparison."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def write_json(path: str | Path, value: Any) -> None:
    Path(path).write_text(canonical_json(value), encoding="utf-8", newline="\n")


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def compare_expected(actual: Any, expected: Any, path: str = "$") -> list[str]:
    differences: list[str] = []
    if type(actual) is not type(expected):
        return [f"{path}: type {type(actual).__name__} != {type(expected).__name__}"]
    if isinstance(expected, dict):
        if set(actual) != set(expected):
            differences.append(
                f"{path}: keys differ; actual-only={sorted(set(actual)-set(expected))}, "
                f"expected-only={sorted(set(expected)-set(actual))}"
            )
        for key in sorted(set(actual) & set(expected)):
            differences.extend(compare_expected(actual[key], expected[key], f"{path}.{key}"))
    elif isinstance(expected, list):
        if len(actual) != len(expected):
            differences.append(f"{path}: length {len(actual)} != {len(expected)}")
        for index, (a_value, e_value) in enumerate(zip(actual, expected)):
            differences.extend(compare_expected(a_value, e_value, f"{path}[{index}]"))
    elif actual != expected:
        differences.append(f"{path}: {actual!r} != {expected!r}")
    return differences
