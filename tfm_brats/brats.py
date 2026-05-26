"""BraTS-GLI dataset conventions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np


MODALITIES = ("t1n", "t1c", "t2w", "t2f")
LABEL_SUFFIX = "seg"
VALID_LABELS = frozenset({0, 1, 2, 3, 4})

REGION_LABELS: dict[str, tuple[int, ...]] = {
    "ET": (3,),
    "TC": (1, 3, 4),
    "WT": (1, 2, 3, 4),
}
REGION_ORDER = ("ET", "TC", "WT")


@dataclass(frozen=True)
class CasePaths:
    case_id: str
    origin: str
    case_dir: Path
    images: dict[str, Path]
    label: Path


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    dataset_root: Path
    training_roots: tuple[str, ...]
    modalities: tuple[str, ...]
    label_suffix: str
    expected_case_prefix: str
    valid_labels: frozenset[int]

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "DatasetSpec":
        training_roots = config.get("training_roots")
        if isinstance(training_roots, dict):
            roots = tuple(str(key) for key in training_roots)
        elif isinstance(training_roots, list):
            roots = tuple(str(item) for item in training_roots)
        else:
            raise ValueError("dataset config requires training_roots as a list or mapping")

        modalities = tuple(str(item) for item in config.get("modalities", MODALITIES))
        valid_labels = frozenset(int(item) for item in config.get("valid_labels", sorted(VALID_LABELS)))
        return cls(
            name=str(config.get("name", "brats_gli_2024")),
            dataset_root=Path(str(config["dataset_root"])),
            training_roots=roots,
            modalities=modalities,
            label_suffix=str(config.get("label_suffix", LABEL_SUFFIX)),
            expected_case_prefix=str(config.get("expected_case_prefix", "BraTS-GLI-")),
            valid_labels=valid_labels,
        )


def case_file(case_dir: Path, suffix: str) -> Path:
    return case_dir / f"{case_dir.name}-{suffix}.nii.gz"


def iter_case_dirs(dataset_root: Path, training_roots: Iterable[str], prefix: str = "BraTS-GLI-"):
    for origin in training_roots:
        root = dataset_root / origin
        if not root.is_dir():
            raise FileNotFoundError(f"Training root does not exist: {root}")
        for case_dir in sorted(root.iterdir()):
            if case_dir.is_dir() and case_dir.name.startswith(prefix):
                yield origin, case_dir


def build_case_paths(spec: DatasetSpec, origin: str, case_id: str) -> CasePaths:
    case_dir = spec.dataset_root / origin / case_id
    images = {modality: case_file(case_dir, modality) for modality in spec.modalities}
    label = case_file(case_dir, spec.label_suffix)
    return CasePaths(case_id=case_id, origin=origin, case_dir=case_dir, images=images, label=label)


def discover_cases(spec: DatasetSpec, max_cases: int | None = None) -> list[CasePaths]:
    cases: list[CasePaths] = []
    for origin, case_dir in iter_case_dirs(
        spec.dataset_root, spec.training_roots, spec.expected_case_prefix
    ):
        cases.append(build_case_paths(spec, origin=origin, case_id=case_dir.name))
        if max_cases is not None and len(cases) >= max_cases:
            break
    return cases


def labels_to_regions(label: np.ndarray, dtype: np.dtype | type = np.uint8) -> np.ndarray:
    """Convert a BraTS label map into ET/TC/WT binary region channels."""
    regions = [np.isin(label, REGION_LABELS[name]) for name in REGION_ORDER]
    return np.stack(regions, axis=0).astype(dtype, copy=False)


def regions_to_labelmap(regions: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    """Convert ET/TC/WT region channels into a nested label map for evaluation.

    The inverse mapping cannot recover labels 1 and 4 separately from TC, so the
    decoded map preserves BraTS regions instead: WT-only -> 2, TC -> 1, ET -> 3.
    """
    data = np.asarray(regions)
    if data.ndim != 4:
        raise ValueError(f"Expected 4D region channels, got shape {data.shape}")
    if data.shape[0] == len(REGION_ORDER):
        channels = data
    elif data.shape[-1] == len(REGION_ORDER):
        channels = np.moveaxis(data, -1, 0)
    else:
        raise ValueError(f"Expected ET/TC/WT channels on first or last axis, got {data.shape}")

    et = channels[0] > threshold
    tc = (channels[1] > threshold) | et
    wt = (channels[2] > threshold) | tc
    label = np.zeros(wt.shape, dtype=np.uint8)
    label[wt] = 2
    label[tc] = 1
    label[et] = 3
    return label


def region_voxel_counts(label: np.ndarray) -> dict[str, int]:
    regions = labels_to_regions(label, dtype=np.uint8)
    return {name: int(regions[index].sum()) for index, name in enumerate(REGION_ORDER)}


def label_value_counts(label: np.ndarray) -> dict[int, int]:
    values, counts = np.unique(label.astype(np.int16, copy=False), return_counts=True)
    return {int(value): int(count) for value, count in zip(values, counts)}


def case_to_monai_item(case: CasePaths) -> dict[str, Any]:
    return {
        "case_id": case.case_id,
        "origin": case.origin,
        "image": [path.as_posix() for path in case.images.values()],
        "label": case.label.as_posix(),
    }
