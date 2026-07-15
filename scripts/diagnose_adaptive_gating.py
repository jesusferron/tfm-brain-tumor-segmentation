#!/usr/bin/env python3
"""Diagnose the adaptive-gating fusion: instability and modality collapse.

Two views:

1. Validation curve (from ``train_log.csv``): prints Dice per region per epoch
   and flags whether the run regressed after its best epoch (the instability
   observed in the 5000-step run: peak at epoch 4, drop at epoch 5).

2. Gate behaviour (from a checkpoint + real cases): runs the learned gate on
   normalized val images and reports, per modality, the softmax weight it
   assigns, plus the mean gate entropy. A collapsed gate (one modality near 1,
   entropy near 0) starves the U-Net of the other modalities and is the
   suspected cause of the instability. Uniform reference: weight 0.25 per
   modality, entropy ln(4)=1.386.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tfm_brats.brats import DatasetSpec  # noqa: E402
from tfm_brats.config import load_config  # noqa: E402
from tfm_brats.monai_pipeline import (  # noqa: E402
    build_inference_transforms,
    load_model_checkpoint,
    monai_items_from_split,
)


def analyze_curve(log_path: Path) -> None:
    if not log_path.is_file():
        print(f"[curve] train_log.csv not found at {log_path}; skipping curve analysis.")
        return
    rows = [r for r in csv.DictReader(log_path.open()) if r.get("event") == "validation"]
    if not rows:
        print(f"[curve] no validation rows in {log_path}.")
        return
    print(f"[curve] validation history from {log_path}:")
    print(f"  {'epoch':>5} {'ET':>8} {'TC':>8} {'WT':>8} {'mean':>8}")
    means = []
    for r in rows:
        mean = float(r["mean_dice"]) if r.get("mean_dice") else float("nan")
        means.append(mean)
        print(
            f"  {r['epoch']:>5} "
            f"{float(r['ET_dice'] or 'nan'):>8.4f} {float(r['TC_dice'] or 'nan'):>8.4f} "
            f"{float(r['WT_dice'] or 'nan'):>8.4f} {mean:>8.4f}"
        )
    best_idx = int(np.nanargmax(means))
    print(f"[curve] best epoch = {rows[best_idx]['epoch']} (mean={means[best_idx]:.4f})")
    if best_idx < len(means) - 1:
        drop = means[best_idx] - means[-1]
        print(
            f"[curve] INSTABILITY: mean Dice regressed by {drop:.4f} after the best epoch "
            f"({means[best_idx]:.4f} -> {means[-1]:.4f}). Consistent with gate destabilizing late training."
        )
    else:
        print("[curve] best epoch is the last one: still improving or stable (no late regression).")


def analyze_gate(args: argparse.Namespace) -> None:
    import torch

    spec = DatasetSpec.from_config(load_config(args.dataset_config))
    model_config = load_config(args.model_config)
    model_config = model_config.get("model", model_config)
    if str(model_config.get("fusion", "")).lower() != "adaptive_gating":
        print(f"[gate] model-config fusion is not adaptive_gating; skipping gate analysis.")
        return

    device = torch.device(args.device)
    model, payload = load_model_checkpoint(
        checkpoint_path=Path(args.checkpoint), model_config=model_config, device=device
    )
    gate = model.fusion
    temperature = float(getattr(gate, "temperature", 1.0))
    items = monai_items_from_split(spec, Path(args.split_csv), max_cases=args.max_cases)
    transform = build_inference_transforms(model_config)

    modalities = list(spec.modalities)
    weights_all = []
    entropies = []
    with torch.no_grad():
        for i, item in enumerate(items, start=1):
            image = transform(item)["image"].unsqueeze(0).to(device)  # (1,4,H,W,D)
            descriptors = gate._descriptors(image) if hasattr(gate, "_descriptors") else image.mean(dim=(2, 3, 4))
            w = torch.softmax(gate.gate(descriptors) / temperature, dim=1)[0].cpu().numpy()
            weights_all.append(w)
            entropies.append(float(-(w * np.log(np.clip(w, 1e-8, None))).sum()))
            print(f"[gate] {i}/{len(items)} {item['case_id']}: " + ", ".join(f"{m}={wi:.3f}" for m, wi in zip(modalities, w)))

    weights_all = np.stack(weights_all)  # (N,4)
    mean_w = weights_all.mean(axis=0)
    std_w = weights_all.std(axis=0)
    dominant = np.bincount(weights_all.argmax(axis=1), minlength=len(modalities))
    max_uniform_entropy = math.log(len(modalities))

    print("\n[gate] summary over", len(items), "cases (temperature =", temperature, "):")
    print(f"  {'modality':>6} {'mean_w':>8} {'std_w':>8} {'dominant#':>10}  (uniform=0.250)")
    for j, m in enumerate(modalities):
        print(f"  {m:>6} {mean_w[j]:>8.3f} {std_w[j]:>8.3f} {int(dominant[j]):>10}")
    mean_entropy = float(np.mean(entropies))
    print(f"  mean gate entropy = {mean_entropy:.3f}  (uniform max = {max_uniform_entropy:.3f})")

    peak = float(mean_w.max())
    if peak > 0.6 or mean_entropy < 0.6 * max_uniform_entropy:
        print(
            f"[gate] COLLAPSE SIGNAL: gate concentrates on '{modalities[int(mean_w.argmax())]}' "
            f"(mean weight {peak:.3f}) / low entropy. Consider temperature>1, warmup, lower fusion_lr, or entropy reg."
        )
    else:
        print("[gate] no strong collapse: weights reasonably spread across modalities.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", default="outputs/train/residual_unet_3d_adaptive_gating_m4_pro_128_5k/checkpoints/best.pt")
    parser.add_argument("--model-config", default="configs/model/residual_unet_3d_adaptive_gating.yaml")
    parser.add_argument("--dataset-config", default="configs/dataset/brats_gli_2024.yaml")
    parser.add_argument("--split-csv", default="outputs/splits/brats_gli_2024_seed20260526/val.csv")
    parser.add_argument("--log-csv", default=None, help="Defaults to <checkpoint>/../../train_log.csv")
    parser.add_argument("--max-cases", type=int, default=40)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--skip-gate", action="store_true", help="Only analyze the validation curve.")
    args = parser.parse_args()

    log_csv = Path(args.log_csv) if args.log_csv else Path(args.checkpoint).resolve().parents[1] / "train_log.csv"
    analyze_curve(log_csv)
    print()
    if not args.skip_gate:
        analyze_gate(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
