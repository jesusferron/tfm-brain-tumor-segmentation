import unittest

import numpy as np

from tfm_brats.brats import (
    REGION_ORDER,
    label_value_counts,
    labels_to_regions,
    region_voxel_counts,
    regions_to_labelmap,
)
from tfm_brats.metrics import dice_score, region_metrics


class BratsRegionTests(unittest.TestCase):
    def test_label_mapping_to_et_tc_wt(self):
        label = np.array(
            [
                [[0, 1], [2, 3]],
                [[4, 3], [1, 0]],
            ],
            dtype=np.int16,
        )

        regions = labels_to_regions(label)

        self.assertEqual(REGION_ORDER, ("ET", "TC", "WT"))
        self.assertEqual(regions.shape, (3, 2, 2, 2))
        self.assertEqual(int(regions[0].sum()), 2)
        self.assertEqual(int(regions[1].sum()), 5)
        self.assertEqual(int(regions[2].sum()), 6)

    def test_region_and_label_counts(self):
        label = np.array([0, 1, 1, 2, 3, 3, 4], dtype=np.int16)

        self.assertEqual(label_value_counts(label), {0: 1, 1: 2, 2: 1, 3: 2, 4: 1})
        self.assertEqual(region_voxel_counts(label), {"ET": 2, "TC": 5, "WT": 6})

    def test_regions_to_labelmap_preserves_nested_regions(self):
        regions = np.zeros((3, 3, 3, 3), dtype=np.float32)
        regions[2, 0, 0, 0] = 1.0
        regions[1, 1, 1, 1] = 1.0
        regions[0, 2, 2, 2] = 1.0

        label = regions_to_labelmap(regions)
        remapped = labels_to_regions(label)

        self.assertEqual(label[0, 0, 0], 2)
        self.assertEqual(label[1, 1, 1], 1)
        self.assertEqual(label[2, 2, 2], 3)
        self.assertEqual(int(remapped[0].sum()), 1)
        self.assertEqual(int(remapped[1].sum()), 2)
        self.assertEqual(int(remapped[2].sum()), 3)

    def test_metrics_for_identical_labels(self):
        label = np.zeros((4, 4, 4), dtype=np.int16)
        label[1:3, 1:3, 1:3] = 3

        metrics = region_metrics(label, label)

        self.assertEqual(dice_score(label == 3, label == 3), 1.0)
        self.assertEqual(metrics["ET"]["dice"], 1.0)
        self.assertEqual(metrics["ET"]["hd95"], 0.0)


if __name__ == "__main__":
    unittest.main()
