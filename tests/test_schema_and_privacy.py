from __future__ import annotations

import csv
from pathlib import Path
import tempfile
import unittest

from stage_xray_artifact.privacy import scan_tree
from stage_xray_artifact.schema import CSV_FIELDS, load_projection


class SchemaAndPrivacyTests(unittest.TestCase):
    @staticmethod
    def _write_minimal_public_projection(path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerow(
                {
                    "prim_path": "/SCALEX_POD",
                    "prim_type_name": "Xform",
                    "has_authored_references": "false",
                    "has_authored_payloads": "false",
                    "path_encoding": "PAIR_HIERARCHY_TOKEN_V1",
                }
            )

    def test_raw_prim_name_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.csv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n")
                writer.writeheader()
                writer.writerow(
                    {
                        "prim_path": "/" + "World/PrivateName",
                        "prim_type_name": "Xform",
                        "has_authored_references": "false",
                        "has_authored_payloads": "false",
                        "path_encoding": "PAIR_HIERARCHY_TOKEN_V1",
                    }
                )
            with self.assertRaisesRegex(ValueError, "non-public Prim path encoding"):
                load_projection(path)

    def test_release_tree_passes_privacy_scan(self) -> None:
        root = Path(__file__).resolve().parents[1]
        result = scan_tree(root)
        self.assertEqual(result["status"], "PASS", result["findings"])

    def test_host_home_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = root / "data" / "publication_safe"
            for name in ("earlier_full_projection.csv", "later_full_projection.csv"):
                self._write_minimal_public_projection(data / name)
            (root / "private-path.txt").write_text(
                "host root: " + "C:" + "\\Users\\Example\\project",
                encoding="utf-8",
            )

            result = scan_tree(root)

            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["finding_count"], 1)
            self.assertEqual(result["findings"][0]["file"], "private-path.txt")


if __name__ == "__main__":
    unittest.main()
