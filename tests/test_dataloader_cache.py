import tempfile
import unittest
from pathlib import Path

from monai.transforms import Compose, EnsureTyped

from tfm_brats.monai_pipeline import build_cached_dataset


class BuildCachedDatasetTests(unittest.TestCase):
    def setUp(self):
        self.items = [{"value": float(i)} for i in range(4)]
        self.transform = Compose([EnsureTyped(keys=["value"])])

    def test_none_returns_plain_dataset(self):
        dataset = build_cached_dataset(self.items, self.transform, cache_mode="none")
        self.assertEqual(type(dataset).__name__, "Dataset")

    def test_memory_returns_cache_dataset(self):
        dataset = build_cached_dataset(
            self.items, self.transform, cache_mode="memory", cache_rate=0.5
        )
        self.assertEqual(type(dataset).__name__, "CacheDataset")

    def test_persistent_returns_persistent_dataset_and_creates_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir = Path(tmp) / "pcache"
            dataset = build_cached_dataset(
                self.items, self.transform, cache_mode="persistent", cache_dir=cache_dir
            )
            self.assertEqual(type(dataset).__name__, "PersistentDataset")
            self.assertTrue(cache_dir.is_dir())

    def test_persistent_without_cache_dir_raises(self):
        with self.assertRaises(ValueError):
            build_cached_dataset(self.items, self.transform, cache_mode="persistent")

    def test_unknown_mode_raises(self):
        with self.assertRaises(ValueError):
            build_cached_dataset(self.items, self.transform, cache_mode="bogus")


if __name__ == "__main__":
    unittest.main()
