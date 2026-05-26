"""Quality-control scan for BraTS-GLI cases."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from .brats import CasePaths, DatasetSpec, discover_cases, label_value_counts, region_voxel_counts
from .config import write_json


def _json_list(values: Any) -> str:
    return json.dumps(values, separators=(",", ":"))


def _shape(image: Any) -> tuple[int, int, int]:
    if len(image.shape) < 3:
        raise ValueError(f"Expected at least 3 dimensions, got shape {image.shape}")
    return tuple(int(value) for value in image.shape[:3])


def _spacing(image: Any) -> tuple[float, float, float]:
    zooms = image.header.get_zooms()[:3]
    return tuple(float(value) for value in zooms)


def _affine_hash(affine: np.ndarray) -> str:
    rounded = np.round(np.asarray(affine, dtype=np.float64), decimals=5)
    payload = rounded.tobytes()
    return hashlib.sha1(payload).hexdigest()[:16]


def _same_shape(shapes: list[tuple[int, int, int]]) -> bool:
    return bool(shapes) and len(set(shapes)) == 1


def _same_spacing(spacings: list[tuple[float, float, float]]) -> bool:
    return bool(spacings) and all(np.allclose(spacings[0], spacing) for spacing in spacings[1:])


def _same_affine(affines: list[np.ndarray]) -> bool:
    return bool(affines) and all(np.allclose(affines[0], affine) for affine in affines[1:])


def _intensity_stats(data: np.ndarray) -> dict[str, float | int]:
    finite = np.isfinite(data)
    nonzero = finite & (data != 0)
    values = data[nonzero]
    if values.size == 0:
        return {
            "nonzero_voxels": 0,
            "mean": math.nan,
            "std": math.nan,
            "min": math.nan,
            "p01": math.nan,
            "median": math.nan,
            "p99": math.nan,
            "max": math.nan,
        }
    return {
        "nonzero_voxels": int(values.size),
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
        "min": float(np.min(values)),
        "p01": float(np.percentile(values, 1)),
        "median": float(np.percentile(values, 50)),
        "p99": float(np.percentile(values, 99)),
        "max": float(np.max(values)),
    }


def _empty_modality_fields(modality: str) -> dict[str, Any]:
    return {
        f"{modality}_path": "",
        f"{modality}_shape": "",
        f"{modality}_spacing": "",
        f"{modality}_nonzero_voxels": "",
        f"{modality}_mean": "",
        f"{modality}_std": "",
        f"{modality}_min": "",
        f"{modality}_p01": "",
        f"{modality}_median": "",
        f"{modality}_p99": "",
        f"{modality}_max": "",
    }


def scan_case(
    case: CasePaths,
    spec: DatasetSpec,
    *,
    collect_intensity_stats: bool = True,
) -> dict[str, Any]:
    """Scan one case and return a flat CSV-ready row."""
    try:
        import nibabel as nib
    except ImportError as err:
        raise RuntimeError("nibabel is required for QC scans.") from err

    row: dict[str, Any] = {
        "case_id": case.case_id,
        "origin": case.origin,
        "case_dir": case.case_dir.as_posix(),
        "status": "ok",
        "problems": "",
        "missing_files": "",
        "shape_consistent": "",
        "spacing_consistent": "",
        "affine_consistent": "",
        "reference_shape": "",
        "reference_spacing": "",
        "reference_affine_hash": "",
        "label_shape": "",
        "label_spacing": "",
        "label_values": "",
        "invalid_label_values": "",
        "label_0_voxels": "",
        "label_1_voxels": "",
        "label_2_voxels": "",
        "label_3_voxels": "",
        "label_4_voxels": "",
        "et_voxels": "",
        "tc_voxels": "",
        "wt_voxels": "",
        "has_et": "",
        "voxel_volume_mm3": "",
        "et_volume_mm3": "",
        "tc_volume_mm3": "",
        "wt_volume_mm3": "",
    }
    for modality in spec.modalities:
        row.update(_empty_modality_fields(modality))

    expected_paths = [*case.images.values(), case.label]
    missing = [path.name for path in expected_paths if not path.is_file()]
    if missing:
        row["status"] = "problem"
        row["missing_files"] = _json_list(missing)
        row["problems"] = _json_list(["missing_files"])
        return row

    problems: list[str] = []
    shapes: list[tuple[int, int, int]] = []
    spacings: list[tuple[float, float, float]] = []
    affines: list[np.ndarray] = []

    loaded_images: dict[str, Any] = {}
    for modality, path in case.images.items():
        image = nib.load(str(path))
        loaded_images[modality] = image
        shape = _shape(image)
        spacing = _spacing(image)
        shapes.append(shape)
        spacings.append(spacing)
        affines.append(np.asarray(image.affine))
        row[f"{modality}_path"] = path.as_posix()
        row[f"{modality}_shape"] = _json_list(shape)
        row[f"{modality}_spacing"] = _json_list([round(value, 6) for value in spacing])

    label_image = nib.load(str(case.label))
    label_shape = _shape(label_image)
    label_spacing = _spacing(label_image)
    shapes.append(label_shape)
    spacings.append(label_spacing)
    affines.append(np.asarray(label_image.affine))
    row["label_shape"] = _json_list(label_shape)
    row["label_spacing"] = _json_list([round(value, 6) for value in label_spacing])

    shape_consistent = _same_shape(shapes)
    spacing_consistent = _same_spacing(spacings)
    affine_consistent = _same_affine(affines)
    row["shape_consistent"] = shape_consistent
    row["spacing_consistent"] = spacing_consistent
    row["affine_consistent"] = affine_consistent
    row["reference_shape"] = _json_list(shapes[0])
    row["reference_spacing"] = _json_list([round(value, 6) for value in spacings[0]])
    row["reference_affine_hash"] = _affine_hash(affines[0])
    if not shape_consistent:
        problems.append("shape_mismatch")
    if not spacing_consistent:
        problems.append("spacing_mismatch")
    if not affine_consistent:
        problems.append("affine_mismatch")

    label_data = np.asarray(label_image.dataobj)
    label_data = np.rint(label_data).astype(np.int16, copy=False)
    counts = label_value_counts(label_data)
    label_values = sorted(counts)
    invalid_values = [value for value in label_values if value not in spec.valid_labels]
    row["label_values"] = _json_list(label_values)
    row["invalid_label_values"] = _json_list(invalid_values)
    for label_value in range(5):
        row[f"label_{label_value}_voxels"] = counts.get(label_value, 0)
    region_counts = region_voxel_counts(label_data)
    row["et_voxels"] = region_counts["ET"]
    row["tc_voxels"] = region_counts["TC"]
    row["wt_voxels"] = region_counts["WT"]
    row["has_et"] = region_counts["ET"] > 0
    voxel_volume = float(np.prod(label_spacing))
    row["voxel_volume_mm3"] = voxel_volume
    row["et_volume_mm3"] = float(region_counts["ET"] * voxel_volume)
    row["tc_volume_mm3"] = float(region_counts["TC"] * voxel_volume)
    row["wt_volume_mm3"] = float(region_counts["WT"] * voxel_volume)
    if invalid_values:
        problems.append("invalid_label_values")

    if collect_intensity_stats:
        for modality, image in loaded_images.items():
            data = np.asarray(image.dataobj, dtype=np.float32)
            stats = _intensity_stats(data)
            for key, value in stats.items():
                row[f"{modality}_{key}"] = value

    if problems:
        row["status"] = "problem"
        row["problems"] = _json_list(problems)
    else:
        row["problems"] = _json_list([])
    return row


def qc_fieldnames(modalities: tuple[str, ...]) -> list[str]:
    base = [
        "case_id",
        "origin",
        "case_dir",
        "status",
        "problems",
        "missing_files",
        "shape_consistent",
        "spacing_consistent",
        "affine_consistent",
        "reference_shape",
        "reference_spacing",
        "reference_affine_hash",
        "label_shape",
        "label_spacing",
        "label_values",
        "invalid_label_values",
        "label_0_voxels",
        "label_1_voxels",
        "label_2_voxels",
        "label_3_voxels",
        "label_4_voxels",
        "et_voxels",
        "tc_voxels",
        "wt_voxels",
        "has_et",
        "voxel_volume_mm3",
        "et_volume_mm3",
        "tc_volume_mm3",
        "wt_volume_mm3",
    ]
    modality_fields: list[str] = []
    for modality in modalities:
        modality_fields.extend(_empty_modality_fields(modality).keys())
    return [*base, *modality_fields]


def write_qc_outputs(
    rows: list[dict[str, Any]],
    spec: DatasetSpec,
    output_csv: Path,
    output_json: Path,
    *,
    collect_intensity_stats: bool,
) -> dict[str, Any]:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = qc_fieldnames(spec.modalities)
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    status_counts = Counter(str(row["status"]) for row in rows)
    origin_counts = Counter(str(row["origin"]) for row in rows)
    problem_counts: Counter[str] = Counter()
    label_value_union: set[int] = set()
    for row in rows:
        for problem in json.loads(str(row.get("problems") or "[]")):
            problem_counts[str(problem)] += 1
        raw_values = str(row.get("label_values") or "[]")
        for value in json.loads(raw_values):
            label_value_union.add(int(value))

    et_positive = sum(1 for row in rows if str(row.get("has_et")).lower() == "true")
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "name": spec.name,
            "dataset_root": spec.dataset_root.as_posix(),
            "training_roots": list(spec.training_roots),
            "modalities": list(spec.modalities),
            "label_suffix": spec.label_suffix,
            "expected_case_prefix": spec.expected_case_prefix,
            "valid_labels": sorted(spec.valid_labels),
        },
        "outputs": {
            "csv": output_csv.as_posix(),
            "json": output_json.as_posix(),
        },
        "collect_intensity_stats": collect_intensity_stats,
        "total_cases": len(rows),
        "status_counts": dict(status_counts),
        "origin_counts": dict(origin_counts),
        "problem_counts": dict(problem_counts),
        "label_values_union": sorted(label_value_union),
        "cases_with_et": et_positive,
        "cases_without_et": len(rows) - et_positive,
    }
    write_json(output_json, summary)
    return summary


def run_qc(
    spec: DatasetSpec,
    output_csv: Path,
    output_json: Path,
    *,
    max_cases: int | None = None,
    collect_intensity_stats: bool = True,
    progress_every: int = 25,
) -> dict[str, Any]:
    cases = discover_cases(spec, max_cases=max_cases)
    rows: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        rows.append(
            scan_case(case, spec=spec, collect_intensity_stats=collect_intensity_stats)
        )
        if progress_every and (index == len(cases) or index % progress_every == 0):
            print(f"QC scanned {index}/{len(cases)} cases", flush=True)
    return write_qc_outputs(
        rows,
        spec=spec,
        output_csv=output_csv,
        output_json=output_json,
        collect_intensity_stats=collect_intensity_stats,
    )
