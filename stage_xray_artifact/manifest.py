"""Release-manifest construction and verification."""

from __future__ import annotations

from pathlib import Path

from .schema import sha256_file


EXCLUDED_PARTS = {".git", "build", "dist", "__pycache__", ".venv", ".pytest_cache"}
EXCLUDED_FILES = {"MANIFEST.sha256"}


def is_excluded_path(relative: Path) -> bool:
    if relative.name in EXCLUDED_FILES:
        return True
    return any(
        part in EXCLUDED_PARTS or part.endswith(".egg-info")
        for part in relative.parts
    )


def eligible_files(root: str | Path) -> list[Path]:
    base = Path(root).resolve()
    files = []
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(base)
        if is_excluded_path(relative):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(base).as_posix().encode("utf-8"))


def render_manifest(root: str | Path) -> str:
    base = Path(root).resolve()
    return "".join(
        f"{sha256_file(path)}  {path.relative_to(base).as_posix()}\n"
        for path in eligible_files(base)
    )


def verify_manifest(root: str | Path) -> dict[str, int | str]:
    base = Path(root).resolve()
    manifest_path = base / "MANIFEST.sha256"
    if not manifest_path.is_file():
        raise ValueError("MANIFEST.sha256 is missing")
    entries: dict[str, str] = {}
    for line_number, line in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line:
            continue
        if len(line) < 67 or line[64:66] != "  ":
            raise ValueError(f"invalid manifest line {line_number}")
        digest, relative = line[:64], line[66:]
        if relative in entries:
            raise ValueError(f"duplicate manifest path: {relative}")
        entries[relative] = digest.upper()

    actual_files = {
        path.relative_to(base).as_posix(): path for path in eligible_files(base)
    }
    if set(entries) != set(actual_files):
        missing = sorted(set(actual_files) - set(entries))
        stale = sorted(set(entries) - set(actual_files))
        raise ValueError(f"manifest file-set mismatch: missing={missing}, stale={stale}")
    for relative, path in actual_files.items():
        actual = sha256_file(path)
        if actual != entries[relative]:
            raise ValueError(f"manifest hash mismatch: {relative}")
    return {"status": "PASS", "verified_file_count": len(entries)}
