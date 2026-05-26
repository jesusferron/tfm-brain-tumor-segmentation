import unittest

from tfm_brats.splits import DEFAULT_RATIOS, stratified_split, validate_splits


def synthetic_rows(count=40):
    rows = []
    for index in range(count):
        rows.append(
            {
                "case_id": f"BraTS-GLI-{index:05d}-000",
                "origin": "training_data1_v2" if index < count * 0.75 else "training_data_additional",
                "status": "ok",
                "invalid_label_values": "[]",
                "et_voxels": str(100 if index % 3 else 0),
                "tc_voxels": str(200 + index),
                "wt_voxels": str(1000 + index * 10),
            }
        )
    return rows


class SplitTests(unittest.TestCase):
    def test_stratified_split_has_exact_coverage_and_no_overlap(self):
        rows = synthetic_rows()

        splits = stratified_split(rows, seed=20260526, ratios=DEFAULT_RATIOS)
        validation = validate_splits(splits, expected_total=len(rows))

        self.assertTrue(validation["ok"])
        self.assertEqual(len(splits["train"]), 28)
        self.assertEqual(len(splits["val"]), 6)
        self.assertEqual(len(splits["test"]), 6)

    def test_stratified_split_is_deterministic(self):
        rows = synthetic_rows()

        first = stratified_split(rows, seed=20260526, ratios=DEFAULT_RATIOS)
        second = stratified_split(rows, seed=20260526, ratios=DEFAULT_RATIOS)

        self.assertEqual(
            [row["case_id"] for row in first["train"]],
            [row["case_id"] for row in second["train"]],
        )


if __name__ == "__main__":
    unittest.main()
