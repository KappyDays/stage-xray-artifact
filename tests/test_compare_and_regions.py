from __future__ import annotations

import unittest

from stage_xray_artifact.compare import compare_records
from stage_xray_artifact.regions import RESIDUAL_IDENTITY, build_regions, compare_regions
from stage_xray_artifact.schema import ROOT_PATH, Record, record_map


def row(path: str, kind: str = "Xform", ref: bool = False, payload: bool = False) -> Record:
    return Record(path, kind, ref, payload)


class CompareAndRegionTests(unittest.TestCase):
    def test_all_three_common_path_field_change_labels(self) -> None:
        earlier = record_map([row(ROOT_PATH, "Xform", False, False)])
        later = record_map([row(ROOT_PATH, "Mesh", True, True)])
        self.assertEqual(
            compare_records(earlier, later),
            {
                ROOT_PATH: (
                    "TYPE_CHANGED",
                    "REFERENCE_PRESENCE_CHANGED",
                    "PAYLOAD_PRESENCE_CHANGED",
                )
            },
        )

    def test_residual_and_nested_landmark_regions(self) -> None:
        records = record_map(
            [
                row(ROOT_PATH),
                row(f"{ROOT_PATH}/N0001", payload=True),
                row(f"{ROOT_PATH}/N0001/N0001", "Mesh"),
                row(f"{ROOT_PATH}/N0001/N0002", ref=True),
                row(f"{ROOT_PATH}/N0001/N0002/N0001", "Scope"),
            ]
        )
        built = build_regions(records)
        self.assertEqual(len(built.regions), 3)
        self.assertEqual(built.owner[ROOT_PATH], RESIDUAL_IDENTITY)
        nested = built.regions[f"{ROOT_PATH}/N0001/N0002"]
        self.assertEqual(nested.region_type, "NESTED_LANDMARK_REGION")
        self.assertEqual(nested.parent_identity, f"{ROOT_PATH}/N0001")
        self.assertEqual(len(nested.member_paths), 2)

    def test_region_change_is_based_on_canonical_member_facts(self) -> None:
        landmark = f"{ROOT_PATH}/N0001"
        member = f"{landmark}/N0001"
        earlier = build_regions(
            record_map([row(ROOT_PATH), row(landmark, payload=True), row(member, "Mesh")])
        )
        later = build_regions(
            record_map([row(ROOT_PATH), row(landmark, payload=True), row(member, "Scope")])
        )
        statuses = {
            item["region_id"]: item["status"]
            for item in compare_regions(earlier, later)
        }
        self.assertEqual(statuses[f"LANDMARK@{landmark}"], "CHANGED_REGION")


if __name__ == "__main__":
    unittest.main()
