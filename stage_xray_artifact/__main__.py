"""Command-line interface for the Stage X-ray artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .manifest import verify_manifest
from .pipeline import reproduce
from .privacy import scan_tree
from .report import load_json


REQUIRED_ROOT_PATHS = (
    Path("MANIFEST.sha256"),
    Path("data/publication_safe/earlier_full_projection.csv"),
    Path("data/publication_safe/later_full_projection.csv"),
    Path("expected/claim_results.json"),
)


def find_repository_root() -> Path:
    candidates = (Path.cwd().resolve(), Path(__file__).resolve().parents[1])
    for candidate in candidates:
        if all((candidate / relative).is_file() for relative in REQUIRED_ROOT_PATHS):
            return candidate
    raise RuntimeError(
        "artifact files were not found; run this command from the tagged "
        "repository root"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m stage_xray_artifact",
        description="Reproduce and verify the Stage X-ray paper artifact.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    replay = subparsers.add_parser("reproduce", help="run the complete public replay")
    replay.add_argument("--data", default="data/publication_safe")
    replay.add_argument("--out", required=True)
    replay.add_argument("--verify", action="store_true")

    subparsers.add_parser("verify-manifest", help="verify every release file hash")
    subparsers.add_parser("privacy-scan", help="scan the release boundary")
    subparsers.add_parser("show-claims", help="print the frozen expected claims")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = find_repository_root()
    if args.command == "reproduce":
        result = reproduce(
            repo_root=root,
            data_root=root / args.data,
            output_root=root / args.out,
            verify=args.verify,
        )
        print(json.dumps(result["verification"], indent=2, sort_keys=True))
        return 0
    if args.command == "verify-manifest":
        print(json.dumps(verify_manifest(root), indent=2, sort_keys=True))
        return 0
    if args.command == "privacy-scan":
        result = scan_tree(root)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "PASS" else 1
    if args.command == "show-claims":
        print(json.dumps(load_json(root / "expected" / "claim_results.json"), indent=2, sort_keys=True))
        return 0
    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
