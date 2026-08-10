from __future__ import annotations

from pathlib import Path
import unittest

from stage_xray_artifact.manifest import is_excluded_path, verify_manifest


class ManifestTests(unittest.TestCase):
    def test_generated_package_metadata_is_excluded(self) -> None:
        self.assertTrue(
            is_excluded_path(Path("stage_xray_artifact.egg-info") / "PKG-INFO")
        )
        self.assertFalse(is_excluded_path(Path("stage_xray_artifact") / "schema.py"))

    def test_release_manifest(self) -> None:
        root = Path(__file__).resolve().parents[1]
        result = verify_manifest(root)
        self.assertEqual(result["status"], "PASS")
        self.assertGreater(result["verified_file_count"], 20)


if __name__ == "__main__":
    unittest.main()
