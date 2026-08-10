from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from stage_xray_artifact.pipeline import reproduce


class FullReproductionTests(unittest.TestCase):
    def test_full_replay_matches_frozen_claims_and_is_byte_repeatable(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            first = base / "first"
            second = base / "second"
            one = reproduce(
                repo_root=root,
                data_root=root / "data" / "publication_safe",
                output_root=first,
                verify=True,
            )
            two = reproduce(
                repo_root=root,
                data_root=root / "data" / "publication_safe",
                output_root=second,
                verify=True,
            )
            self.assertEqual(one["verification"]["status"], "PASS")
            self.assertEqual(two["verification"]["status"], "PASS")
            retained = one["summary"]["validation"]["retained_audit"]
            self.assertEqual(retained["measurement_runtime"], "NVIDIA Isaac Sim 6.0.0 full Kit")
            self.assertEqual(retained["openusd_version"], "0.25.11")
            self.assertEqual(retained["whole_dream_ai_earlier_selected_prims"], 58097)
            self.assertEqual(retained["whole_dream_ai_later_selected_prims"], 59821)
            first_files = sorted(path.relative_to(first) for path in first.rglob("*") if path.is_file())
            second_files = sorted(path.relative_to(second) for path in second.rglob("*") if path.is_file())
            self.assertEqual(first_files, second_files)
            for relative in first_files:
                self.assertEqual(
                    (first / relative).read_bytes(),
                    (second / relative).read_bytes(),
                    relative.as_posix(),
                )
            svg_root = ET.parse(first / "figure3-reproduced.svg").getroot()
            namespace = {"svg": "http://www.w3.org/2000/svg"}
            self.assertEqual(len(svg_root.findall("svg:rect", namespace)), 76)
            self.assertEqual(len(svg_root.findall("svg:polyline", namespace)), 1)


if __name__ == "__main__":
    unittest.main()
