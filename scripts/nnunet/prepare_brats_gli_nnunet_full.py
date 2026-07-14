#!/usr/bin/env python3
"""Convert the versioned BraTS-GLI splits into nnU-Net v2 raw format.

Unlike the smoke-test path (which stacked the four modalities into a 4D NIfTI
for the MONAI ``nnUNetV2Runner``), this converter writes nnU-Net v2's native
multi-channel layout directly from the *same* TFM split CSVs, so the nnU-Net
baseline trains on exactly the TFM train split and is evaluated on the TFM
val/test split. No data is duplicated by default: each modality file is
symlinked into ``imagesTr``/``imagesTs`` with the nnU-Net channel naming.

Design decisions (see docs/nnunet-baseline.md and the vitacora):

- Labels are kept as-is (0..4). BraTS-GLI 2024 uses consecutive integer labels
  0,1,2,3,4, which nnU-Net v2 accepts as a plain multi-class problem. Keeping
  the raw labels means the predicted label map uses the same integer scheme as
  the ground truth, so the TFM ``evaluate`` (which maps labels -> ET/TC/WT)
  works on nnU-Net predictions with no custom converter and yields metrics
  directly comparable to the MONAI models.
- The case id is used verbatim as the nnU-Net case identifier (it contains no
  underscore, so nnU-Net's ``{id}_{channel}`` parsing is unambiguous). Thus a
  prediction for the val split lands at ``{case_id}.nii.gz``, exactly what the
  TFM evaluate step expects.
- The val split goes to ``imagesTs`` (images only); it is never part of
  nnU-Net's internal cross-validation folds, so it stays held out from training.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Ensure the repo root (which contains the ``tfm_brats`` package) is importable
# when this script is invoked directly (``python scripts/nnunet/...``).
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tfm_brats.brats import DatasetSpec, build_case_paths  # noqa: E402
from tfm_brats.config import load_config  # noqa: E402
from tfm_brats.monai_pipeline import read_split_csv  # noqa: E402


def _link_or_copy(src: Path, dst: Path, *, mode: str) -> None:
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    if mode == "copy":
        import shutil

        shutil.copy2(src, dst)
    else:  # symlink (default)
        os.symlink(src.resolve(), dst)


def _channel_names(spec: DatasetSpec) -> dict[str, str]:
    return {str(index): modality for index, modality in enumerate(spec.modalities)}


def _labels_block(spec: DatasetSpec) -> dict[str, int]:
    # Human-readable names for BraTS-GLI 2024 labels; values must match the files.
    names = {0: "background", 1: "NCR", 2: "ED", 3: "ET", 4: "RC"}
    labels = {}
    for value in sorted(spec.valid_labels):
        labels[names.get(value, f"label{value}")] = int(value)
    return labels


def _convert_split(
    spec: DatasetSpec,
    split_csv: Path,
    images_dir: Path,
    labels_dir: Path | None,
    *,
    mode: str,
    max_cases: int | None,
) -> int:
    rows = read_split_csv(split_csv, max_cases=max_cases)
    images_dir.mkdir(parents=True, exist_ok=True)
    if labels_dir is not None:
        labels_dir.mkdir(parents=True, exist_ok=True)
    for row in rows:
        case = build_case_paths(spec, origin=row["origin"], case_id=row["case_id"])
        for channel, modality in enumerate(spec.modalities):
            src = case.images[modality]
            if not src.is_file():
                raise FileNotFoundError(f"Missing modality file: {src}")
            dst = images_dir / f"{case.case_id}_{channel:04d}.nii.gz"
            _link_or_copy(src, dst, mode=mode)
        if labels_dir is not None:
            if not case.label.is_file():
                raise FileNotFoundError(f"Missing label file: {case.label}")
            _link_or_copy(case.label, labels_dir / f"{case.case_id}.nii.gz", mode=mode)
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-config", default="configs/dataset/brats_gli_2024.yaml")
    parser.add_argument("--split-dir", default="outputs/splits/brats_gli_2024_seed20260526")
    parser.add_argument("--train-split", default="train.csv")
    parser.add_argument("--test-split", default="val.csv", help="Split exported to imagesTs (held out).")
    parser.add_argument("--nnunet-raw", default="outputs/nnunet_full/nnUNet_raw")
    parser.add_argument("--dataset-id", type=int, default=725)
    parser.add_argument("--dataset-name", default="BraTSGLI2024")
    parser.add_argument("--link-mode", choices=["symlink", "copy"], default="symlink")
    parser.add_argument("--max-cases", type=int, help="Limit cases per split (for local verification).")
    args = parser.parse_args()

    spec = DatasetSpec.from_config(load_config(args.dataset_config))
    split_dir = Path(args.split_dir)
    dataset_dir = Path(args.nnunet_raw) / f"Dataset{args.dataset_id:03d}_{args.dataset_name}"
    images_tr = dataset_dir / "imagesTr"
    labels_tr = dataset_dir / "labelsTr"
    images_ts = dataset_dir / "imagesTs"

    print(f"Dataset root: {spec.dataset_root}")
    print(f"nnU-Net dataset dir: {dataset_dir}")
    print(f"Link mode: {args.link_mode}")

    num_training = _convert_split(
        spec, split_dir / args.train_split, images_tr, labels_tr,
        mode=args.link_mode, max_cases=args.max_cases,
    )
    num_test = _convert_split(
        spec, split_dir / args.test_split, images_ts, None,
        mode=args.link_mode, max_cases=args.max_cases,
    )

    dataset_json = {
        "channel_names": _channel_names(spec),
        "labels": _labels_block(spec),
        "numTraining": num_training,
        "file_ending": ".nii.gz",
        "name": f"Dataset{args.dataset_id:03d}_{args.dataset_name}",
        "description": "BraTS-GLI 2024 converted from the TFM versioned splits (labels 0-4 preserved).",
    }
    (dataset_dir / "dataset.json").write_text(json.dumps(dataset_json, indent=2) + "\n", encoding="utf-8")

    print(f"imagesTr channels written: {num_training} cases x {len(spec.modalities)} = {num_training * len(spec.modalities)} files")
    print(f"labelsTr written: {num_training}")
    print(f"imagesTs channels written: {num_test} cases x {len(spec.modalities)} = {num_test * len(spec.modalities)} files")
    print(f"dataset.json labels: {dataset_json['labels']}")
    print(f"dataset.json channel_names: {dataset_json['channel_names']}")
    print("")
    print("Next (native nnU-Net v2 CLI, with nnUNet_raw/nnUNet_preprocessed/nnUNet_results exported):")
    print(f"  nnUNetv2_plan_and_preprocess -d {args.dataset_id} --verify_dataset_integrity")
    print(f"  nnUNetv2_train {args.dataset_id} 3d_fullres 0")
    print(f"  nnUNetv2_predict -i {images_ts} -o <PRED_DIR> -d {args.dataset_id} -c 3d_fullres -f 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
