"""Versioned train/validation/test split generation."""

from __future__ import annotations

import csv
import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import write_json


SPLIT_ORDER = ("train", "val", "test")
DEFAULT_RATIOS = {"train": 0.70, "val": 0.15, "test": 0.15}


def _as_int(value: Any) -> int:
    if value is None or value == "":
        return 0
    return int(float(value))


def read_qc_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def eligible_qc_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    eligible = []
    for row in rows:
        if row.get("status") != "ok":
            continue
        if str(row.get("missing_files") or "") not in {"", "[]"}:
            continue
        if str(row.get("invalid_label_values") or "[]") != "[]":
            continue
        eligible.append(row)
    return eligible


def volume_bins(rows: list[dict[str, Any]], *, num_bins: int = 4) -> dict[str, str]:
    values = sorted(_as_int(row.get("wt_voxels")) for row in rows if _as_int(row.get("wt_voxels")) > 0)
    if not values:
        return {str(row["case_id"]): "zero" for row in rows}

    case_bins: dict[str, str] = {}
    for row in rows:
        value = _as_int(row.get("wt_voxels"))
        if value <= 0:
            case_bins[str(row["case_id"])] = "zero"
            continue
        lower_or_equal = sum(1 for candidate in values if candidate <= value)
        rank = lower_or_equal / len(values)
        bin_index = min(num_bins, max(1, int((rank * num_bins) + 0.999999)))
        case_bins[str(row["case_id"])] = f"q{bin_index}"
    return case_bins


def stratification_key(row: dict[str, Any], case_bins: dict[str, str]) -> str:
    has_et = _as_int(row.get("et_voxels")) > 0
    return "|".join(
        [
            f"origin={row['origin']}",
            f"et={int(has_et)}",
            f"wt_bin={case_bins[str(row['case_id'])]}",
        ]
    )


def desired_counts(total: int, ratios: dict[str, float]) -> dict[str, int]:
    raw = {split: total * ratios[split] for split in SPLIT_ORDER}
    counts = {split: int(raw[split]) for split in SPLIT_ORDER}
    remaining = total - sum(counts.values())
    ranked = sorted(SPLIT_ORDER, key=lambda split: (raw[split] - counts[split], split), reverse=True)
    for split in ranked[:remaining]:
        counts[split] += 1
    return counts


def _current_counts(group_counts: dict[str, dict[str, int]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for allocation in group_counts.values():
        counts.update(allocation)
    return counts


def _adjust_to_global_targets(
    group_counts: dict[str, dict[str, int]],
    targets: dict[str, int],
    group_sizes: dict[str, int],
    ratios: dict[str, float],
) -> None:
    while True:
        current = _current_counts(group_counts)
        deficits = [split for split in SPLIT_ORDER if current[split] < targets[split]]
        surpluses = [split for split in SPLIT_ORDER if current[split] > targets[split]]
        if not deficits or not surpluses:
            return
        dst = max(deficits, key=lambda split: targets[split] - current[split])
        src = max(surpluses, key=lambda split: current[split] - targets[split])

        candidates = []
        for key, allocation in group_counts.items():
            if allocation[src] <= 0:
                continue
            size = group_sizes[key]
            src_excess = allocation[src] / size - ratios[src]
            dst_deficit = ratios[dst] - allocation[dst] / size
            candidates.append((src_excess + dst_deficit, key))
        if not candidates:
            return
        _, selected_key = max(candidates)
        group_counts[selected_key][src] -= 1
        group_counts[selected_key][dst] += 1


def stratified_split(
    rows: list[dict[str, Any]],
    *,
    seed: int,
    ratios: dict[str, float] | None = None,
    num_volume_bins: int = 4,
) -> dict[str, list[dict[str, Any]]]:
    ratios = ratios or DEFAULT_RATIOS
    if round(sum(ratios.values()), 8) != 1.0:
        raise ValueError(f"Split ratios must sum to 1.0, got {ratios}")

    case_bins = volume_bins(rows, num_bins=num_volume_bins)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[stratification_key(row, case_bins)].append(row | {"volume_bin": case_bins[row["case_id"]]})

    rng = random.Random(seed)
    for items in grouped.values():
        items.sort(key=lambda row: str(row["case_id"]))
        rng.shuffle(items)

    group_counts = {key: desired_counts(len(items), ratios) for key, items in grouped.items()}
    group_sizes = {key: len(items) for key, items in grouped.items()}
    _adjust_to_global_targets(group_counts, desired_counts(len(rows), ratios), group_sizes, ratios)

    splits: dict[str, list[dict[str, Any]]] = {split: [] for split in SPLIT_ORDER}
    for key in sorted(grouped):
        items = grouped[key]
        offset = 0
        for split in SPLIT_ORDER:
            count = group_counts[key][split]
            selected = items[offset : offset + count]
            for row in selected:
                splits[split].append(row | {"stratum": key})
            offset += count

    for split in SPLIT_ORDER:
        splits[split].sort(key=lambda row: (str(row["origin"]), str(row["case_id"])))
    return splits


def validate_splits(splits: dict[str, list[dict[str, Any]]], expected_total: int) -> dict[str, Any]:
    seen: dict[str, str] = {}
    overlaps: list[dict[str, str]] = []
    for split, rows in splits.items():
        for row in rows:
            key = f"{row['origin']}/{row['case_id']}"
            if key in seen:
                overlaps.append({"case": key, "first_split": seen[key], "second_split": split})
            seen[key] = split

    missing_count = expected_total - len(seen)
    return {
        "ok": not overlaps and missing_count == 0,
        "expected_total": expected_total,
        "observed_total": len(seen),
        "missing_count": missing_count,
        "overlaps": overlaps,
    }


def split_distribution(splits: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    distribution: dict[str, Any] = {}
    for split, rows in splits.items():
        distribution[split] = {
            "count": len(rows),
            "origin_counts": dict(Counter(str(row["origin"]) for row in rows)),
            "et_counts": dict(Counter("present" if _as_int(row.get("et_voxels")) > 0 else "absent" for row in rows)),
            "volume_bin_counts": dict(Counter(str(row.get("volume_bin")) for row in rows)),
            "stratum_counts": dict(Counter(str(row.get("stratum")) for row in rows)),
        }
    return distribution


def write_split_outputs(
    splits: dict[str, list[dict[str, Any]]],
    output_dir: Path,
    *,
    source_qc_csv: Path,
    seed: int,
    ratios: dict[str, float],
    num_volume_bins: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    for split, rows in splits.items():
        txt_path = output_dir / f"{split}.txt"
        csv_path = output_dir / f"{split}.csv"
        txt_path.write_text(
            "".join(f"{row['case_id']}\n" for row in rows),
            encoding="utf-8",
        )
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            fieldnames = ["case_id", "origin", "stratum", "volume_bin", "et_voxels", "tc_voxels", "wt_voxels"]
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    validation = validate_splits(splits, expected_total=sum(len(rows) for rows in splits.values()))
    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_qc_csv": source_qc_csv.as_posix(),
        "seed": seed,
        "ratios": ratios,
        "volume_bins": num_volume_bins,
        "split_order": list(SPLIT_ORDER),
        "outputs": {
            split: {
                "txt": (output_dir / f"{split}.txt").as_posix(),
                "csv": (output_dir / f"{split}.csv").as_posix(),
            }
            for split in SPLIT_ORDER
        },
        "distribution": split_distribution(splits),
        "validation": validation,
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def generate_splits_from_qc(
    qc_csv: Path,
    output_dir: Path,
    *,
    seed: int = 20260526,
    ratios: dict[str, float] | None = None,
    num_volume_bins: int = 4,
) -> dict[str, Any]:
    ratios = ratios or DEFAULT_RATIOS
    rows = eligible_qc_rows(read_qc_rows(qc_csv))
    if not rows:
        raise ValueError(f"No eligible QC rows found in {qc_csv}")
    splits = stratified_split(rows, seed=seed, ratios=ratios, num_volume_bins=num_volume_bins)
    return write_split_outputs(
        splits,
        output_dir,
        source_qc_csv=qc_csv,
        seed=seed,
        ratios=ratios,
        num_volume_bins=num_volume_bins,
    )
