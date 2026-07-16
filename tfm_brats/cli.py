"""Command-line interface for the BraTS-GLI protocol."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from .brats import DatasetSpec
from .config import load_config
from .metrics import evaluate_prediction_files
from .monai_pipeline import monai_items_from_split, predict_split, train_one_run
from .qc import run_qc
from .splits import DEFAULT_RATIOS, generate_splits_from_qc


DEFAULT_DATASET_CONFIG = "configs/dataset/brats_gli_2024.yaml"
DEFAULT_QC_CSV = "outputs/qc/brats_gli_2024_qc.csv"
DEFAULT_QC_JSON = "outputs/qc/brats_gli_2024_qc_summary.json"
DEFAULT_SPLIT_DIR = "outputs/splits/brats_gli_2024_seed20260526"


def load_dataset_spec(path: str | Path) -> DatasetSpec:
    return DatasetSpec.from_config(load_config(path))


def parse_ratios(raw: str) -> dict[str, float]:
    parts = [float(value) for value in raw.split("/")]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("Ratios must use train/val/test format, e.g. 70/15/15")
    total = sum(parts)
    if total <= 0:
        raise argparse.ArgumentTypeError("Ratios must be positive")
    return {
        "train": parts[0] / total,
        "val": parts[1] / total,
        "test": parts[2] / total,
    }


def cmd_qc(args: argparse.Namespace) -> int:
    spec = load_dataset_spec(args.dataset_config)
    summary = run_qc(
        spec,
        output_csv=Path(args.output_csv),
        output_json=Path(args.output_json),
        max_cases=args.max_cases,
        collect_intensity_stats=not args.skip_intensity_stats,
        progress_every=args.progress_every,
    )
    print(f"QC cases: {summary['total_cases']}")
    print(f"QC status counts: {summary['status_counts']}")
    print(f"QC CSV: {summary['outputs']['csv']}")
    print(f"QC JSON: {summary['outputs']['json']}")
    if args.fail_on_problems and int(summary["status_counts"].get("problem", 0)) > 0:
        return 4
    return 0


def cmd_splits(args: argparse.Namespace) -> int:
    manifest = generate_splits_from_qc(
        Path(args.qc_csv),
        Path(args.output_dir),
        seed=args.seed,
        ratios=args.ratios,
        num_volume_bins=args.volume_bins,
    )
    print(f"Split manifest: {Path(args.output_dir) / 'manifest.json'}")
    for split, details in manifest["distribution"].items():
        print(f"{split}: {details['count']} cases")
    if not manifest["validation"]["ok"]:
        print(f"Split validation failed: {manifest['validation']}")
        return 5
    return 0


def cmd_train(args: argparse.Namespace) -> int:
    os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/matplotlib")
    os.environ.setdefault("XDG_CACHE_HOME", "/private/tmp")
    spec = load_dataset_spec(args.dataset_config)
    model_config_raw = load_config(args.model_config)
    training_config_raw = load_config(args.training_config)
    model_config = model_config_raw.get("model", model_config_raw)
    training_config = training_config_raw.get("training", training_config_raw)
    if args.device:
        training_config["device"] = args.device
    if args.seed is not None:
        training_config["seed"] = args.seed
    summary = train_one_run(
        spec=spec,
        model_config=model_config,
        training_config=training_config,
        split_dir=Path(args.split_dir),
        output_dir=Path(args.output_dir),
        max_steps=args.max_steps,
        max_train_cases=args.max_train_cases,
        max_val_cases=args.max_val_cases,
    )
    print(f"Training steps: {summary['global_step']}")
    print(f"Last loss: {summary['loss_last']}")
    print(f"Summary: {Path(args.output_dir) / 'train_summary.json'}")
    return 0


def cmd_evaluate(args: argparse.Namespace) -> int:
    spec = load_dataset_spec(args.dataset_config)
    cases = monai_items_from_split(spec, Path(args.split_csv), max_cases=args.max_cases)
    summary = evaluate_prediction_files(
        cases,
        predictions_dir=Path(args.predictions_dir),
        output_csv=Path(args.output_csv),
        output_json=Path(args.output_json),
        prediction_suffix=args.prediction_suffix,
    )
    print(f"Evaluated cases: {summary['cases']}")
    print(f"Metrics CSV: {args.output_csv}")
    print(f"Metrics JSON: {args.output_json}")
    return 0


def cmd_predict(args: argparse.Namespace) -> int:
    os.environ.setdefault("MPLCONFIGDIR", "/private/tmp/matplotlib")
    os.environ.setdefault("XDG_CACHE_HOME", "/private/tmp")
    spec = load_dataset_spec(args.dataset_config)
    model_config_raw = load_config(args.model_config)
    inference_config_raw = load_config(args.training_config)
    model_config = model_config_raw.get("model", model_config_raw)
    inference_config = inference_config_raw.get("training", inference_config_raw)
    if args.device:
        inference_config["device"] = args.device
    summary = predict_split(
        spec=spec,
        model_config=model_config,
        inference_config=inference_config,
        split_csv=Path(args.split_csv),
        checkpoint_path=Path(args.checkpoint),
        output_dir=Path(args.output_dir),
        max_cases=args.max_cases,
        device_name=args.device,
    )
    print(f"Predicted cases: {summary['cases']}")
    print(f"Predictions: {args.output_dir}")
    print(f"Summary: {Path(args.output_dir) / 'prediction_summary.json'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tfm-brats")
    subparsers = parser.add_subparsers(dest="command", required=True)

    qc = subparsers.add_parser("qc", help="scan BraTS-GLI integrity and statistics")
    qc.add_argument("--dataset-config", default=DEFAULT_DATASET_CONFIG)
    qc.add_argument("--output-csv", default=DEFAULT_QC_CSV)
    qc.add_argument("--output-json", default=DEFAULT_QC_JSON)
    qc.add_argument("--max-cases", type=int)
    qc.add_argument("--skip-intensity-stats", action="store_true")
    qc.add_argument("--progress-every", type=int, default=25)
    qc.add_argument("--fail-on-problems", action="store_true")
    qc.set_defaults(func=cmd_qc)

    splits = subparsers.add_parser("splits", help="create versioned train/val/test splits")
    splits.add_argument("--qc-csv", default=DEFAULT_QC_CSV)
    splits.add_argument("--output-dir", default=DEFAULT_SPLIT_DIR)
    splits.add_argument("--seed", type=int, default=20260526)
    splits.add_argument("--ratios", type=parse_ratios, default=DEFAULT_RATIOS)
    splits.add_argument("--volume-bins", type=int, default=4)
    splits.set_defaults(func=cmd_splits)

    train = subparsers.add_parser("train", help="run minimal MONAI/PyTorch training")
    train.add_argument("--dataset-config", default=DEFAULT_DATASET_CONFIG)
    train.add_argument("--model-config", default="configs/model/residual_unet_3d.yaml")
    train.add_argument("--training-config", default="configs/training/local_smoke.yaml")
    train.add_argument("--split-dir", default=DEFAULT_SPLIT_DIR)
    train.add_argument("--output-dir", default="outputs/train/residual_unet_3d")
    train.add_argument("--max-steps", type=int)
    train.add_argument("--max-train-cases", type=int)
    train.add_argument("--max-val-cases", type=int)
    train.add_argument("--device")
    train.add_argument("--seed", type=int, help="Override the training-config seed (for multi-seed runs).")
    train.set_defaults(func=cmd_train)

    predict = subparsers.add_parser("predict", help="export NIfTI predictions for a split")
    predict.add_argument("--dataset-config", default=DEFAULT_DATASET_CONFIG)
    predict.add_argument("--model-config", default="configs/model/residual_unet_3d.yaml")
    predict.add_argument("--training-config", default="configs/training/local_smoke.yaml")
    predict.add_argument("--split-csv", default=f"{DEFAULT_SPLIT_DIR}/val.csv")
    predict.add_argument("--checkpoint", default="outputs/train/residual_unet_3d/checkpoints/best.pt")
    predict.add_argument("--output-dir", default="outputs/predictions/residual_unet_3d_val")
    predict.add_argument("--max-cases", type=int)
    predict.add_argument("--device")
    predict.set_defaults(func=cmd_predict)

    evaluate = subparsers.add_parser("evaluate", help="compute Dice and HD95 for ET/TC/WT")
    evaluate.add_argument("--dataset-config", default=DEFAULT_DATASET_CONFIG)
    evaluate.add_argument("--split-csv", default=f"{DEFAULT_SPLIT_DIR}/test.csv")
    evaluate.add_argument("--predictions-dir", required=True)
    evaluate.add_argument("--output-csv", default="outputs/evaluation/brats_gli_2024_metrics.csv")
    evaluate.add_argument("--output-json", default="outputs/evaluation/brats_gli_2024_metrics_summary.json")
    evaluate.add_argument("--prediction-suffix", default=".nii.gz")
    evaluate.add_argument("--max-cases", type=int)
    evaluate.set_defaults(func=cmd_evaluate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
