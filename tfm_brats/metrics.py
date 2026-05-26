"""Segmentation metrics for BraTS ET/TC/WT regions."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from .brats import REGION_ORDER, labels_to_regions
from .config import write_json


def dice_score(prediction: np.ndarray, target: np.ndarray) -> float:
    pred = prediction.astype(bool, copy=False)
    ref = target.astype(bool, copy=False)
    pred_sum = int(pred.sum())
    ref_sum = int(ref.sum())
    if pred_sum == 0 and ref_sum == 0:
        return 1.0
    if pred_sum == 0 or ref_sum == 0:
        return 0.0
    intersection = int(np.logical_and(pred, ref).sum())
    return float((2.0 * intersection) / (pred_sum + ref_sum))


def _surface(mask: np.ndarray) -> np.ndarray:
    from scipy import ndimage

    binary = mask.astype(bool, copy=False)
    if not binary.any():
        return binary
    eroded = ndimage.binary_erosion(binary, structure=np.ones((3, 3, 3), dtype=bool), border_value=0)
    return np.logical_xor(binary, eroded)


def hd95(prediction: np.ndarray, target: np.ndarray, spacing: tuple[float, float, float]) -> float:
    """Compute symmetric 95th percentile Hausdorff distance in millimetres."""
    from scipy import ndimage

    pred = prediction.astype(bool, copy=False)
    ref = target.astype(bool, copy=False)
    if not pred.any() and not ref.any():
        return 0.0
    if not pred.any() or not ref.any():
        return math.inf

    pred_surface = _surface(pred)
    ref_surface = _surface(ref)
    pred_to_ref = ndimage.distance_transform_edt(~ref_surface, sampling=spacing)[pred_surface]
    ref_to_pred = ndimage.distance_transform_edt(~pred_surface, sampling=spacing)[ref_surface]
    distances = np.concatenate([pred_to_ref, ref_to_pred])
    if distances.size == 0:
        return 0.0
    return float(np.percentile(distances, 95))


def ensure_region_channels(array: np.ndarray) -> np.ndarray:
    """Return a 3-channel ET/TC/WT boolean array from labels or region channels."""
    data = np.asarray(array)
    if data.ndim == 4 and data.shape[0] == len(REGION_ORDER):
        return data > 0.5
    if data.ndim == 4 and data.shape[-1] == len(REGION_ORDER):
        return np.moveaxis(data, -1, 0) > 0.5
    if data.ndim == 4 and data.shape[0] == 1:
        data = data[0]
    return labels_to_regions(np.rint(data).astype(np.int16), dtype=bool)


def region_metrics(
    prediction: np.ndarray,
    target: np.ndarray,
    *,
    spacing: tuple[float, float, float] = (1.0, 1.0, 1.0),
) -> dict[str, dict[str, float]]:
    pred_regions = ensure_region_channels(prediction)
    target_regions = ensure_region_channels(target)
    metrics: dict[str, dict[str, float]] = {}
    for index, name in enumerate(REGION_ORDER):
        metrics[name] = {
            "dice": dice_score(pred_regions[index], target_regions[index]),
            "hd95": hd95(pred_regions[index], target_regions[index], spacing),
        }
    return metrics


def _load_nifti(path: Path) -> tuple[np.ndarray, tuple[float, float, float]]:
    try:
        import nibabel as nib
    except ImportError as err:
        raise RuntimeError("nibabel is required for evaluation.") from err

    image = nib.load(str(path))
    spacing = tuple(float(value) for value in image.header.get_zooms()[:3])
    return np.asarray(image.dataobj), spacing


def evaluate_prediction_files(
    cases: list[dict[str, str]],
    *,
    predictions_dir: Path,
    output_csv: Path,
    output_json: Path,
    prediction_suffix: str = ".nii.gz",
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for case in cases:
        case_id = case["case_id"]
        prediction_path = predictions_dir / f"{case_id}{prediction_suffix}"
        label_path = Path(case["label"])
        if not prediction_path.is_file():
            raise FileNotFoundError(f"Missing prediction for {case_id}: {prediction_path}")
        prediction, _ = _load_nifti(prediction_path)
        target, spacing = _load_nifti(label_path)
        metrics = region_metrics(prediction, target, spacing=spacing)
        row = {
            "case_id": case_id,
            "origin": case.get("origin", ""),
            "prediction": prediction_path.as_posix(),
            "label": label_path.as_posix(),
        }
        for region_name in REGION_ORDER:
            row[f"{region_name}_dice"] = metrics[region_name]["dice"]
            row[f"{region_name}_hd95"] = metrics[region_name]["hd95"]
        rows.append(row)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "case_id",
        "origin",
        "prediction",
        "label",
        "ET_dice",
        "ET_hd95",
        "TC_dice",
        "TC_hd95",
        "WT_dice",
        "WT_hd95",
    ]
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    aggregates: dict[str, dict[str, float]] = {}
    for region_name in REGION_ORDER:
        for metric_name in ("dice", "hd95"):
            values = [float(row[f"{region_name}_{metric_name}"]) for row in rows]
            finite_values = [value for value in values if math.isfinite(value)]
            aggregates[f"{region_name}_{metric_name}"] = {
                "mean": float(np.mean(finite_values)) if finite_values else math.inf,
                "median": float(np.median(finite_values)) if finite_values else math.inf,
                "count": len(values),
                "finite_count": len(finite_values),
            }

    summary = {
        "predictions_dir": predictions_dir.as_posix(),
        "output_csv": output_csv.as_posix(),
        "cases": len(rows),
        "aggregates": aggregates,
    }
    write_json(output_json, summary)
    return summary
