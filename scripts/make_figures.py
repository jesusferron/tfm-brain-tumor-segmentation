#!/usr/bin/env python3
"""Generate qualitative figures for Chapter 5 from local evaluation predictions.

Two figures used in Chapter 5 are generated when all copied prediction artefacts
are available:
  1. A comparison of the manual reference, nnU-Net, Swin-UNETR, Attention U-Net,
     and the concatenation baseline.
  2. A visual illustration of an adaptive-gating low-performance run.

The script reads predictions available below ``outputs/predictions``. Backgrounds
and manual references come from the configured dataset.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np

from tfm_brats.brats import DatasetSpec, build_case_paths
from tfm_brats.config import load_config

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/memoria/figuras"
OUT.mkdir(parents=True, exist_ok=True)
SPEC = DatasetSpec.from_config(load_config(ROOT / "configs/dataset/brats_gli_2024.yaml"))
SPLIT = ROOT / "outputs/splits/brats_gli_2024_seed20260526"

# Region colors (RGBA): WT yellow, TC orange, ET red — drawn nested (WT, then TC, then ET).
COLORS = {"WT": (1.0, 0.85, 0.0, 0.45), "TC": (1.0, 0.5, 0.0, 0.6), "ET": (0.9, 0.0, 0.0, 0.85)}


def gt_regions(gt):
    return {"ET": gt == 3, "TC": np.isin(gt, [1, 3, 4]), "WT": np.isin(gt, [1, 2, 3, 4])}


def pred_regions(p):  # regions_to_labelmap encoding: ET=3, TC-only=1, WT-only=2
    return {"ET": p == 3, "TC": np.isin(p, [1, 3]), "WT": np.isin(p, [1, 2, 3])}


def load_case(case_id, origin):
    case = build_case_paths(SPEC, origin=origin, case_id=case_id)
    t1c = np.asarray(nib.load(str(case.images["t1c"])).dataobj, dtype=np.float32)
    gt = np.asarray(nib.load(str(case.label)).dataobj)
    return t1c, gt


def read_metrics(tag):
    d = {}
    for r in csv.DictReader(open(ROOT / f"outputs/evaluation/{tag}_test_metrics.csv")):
        d[r["case_id"]] = r
    return d


_ORIGIN = {r["case_id"]: r["origin"] for r in csv.DictReader(open(SPLIT / "test.csv"))}


def origin_of(case_id):
    return _ORIGIN[case_id]


def pick_case():
    """A case with all three regions well represented and concat performing well."""
    concat = read_metrics("final_concat_seed20260526")
    best, best_score = None, -1
    for cid, r in concat.items():
        try:
            et, tc, wt = float(r["ET_dice"]), float(r["TC_dice"]), float(r["WT_dice"])
        except ValueError:
            continue
        if min(et, tc, wt) < 0.6 or et > 0.98:  # exclude weak and trivial/empty-ET cases
            continue
        origin = origin_of(cid)
        _, gt = load_case(cid, origin)
        reg = gt_regions(gt)
        et_vox = int(reg["ET"].sum())
        if et_vox < 3000:  # require substantial enhancing tumor for a clear figure
            continue
        score = et_vox  # prefer larger ET for visual clarity
        if score > best_score:
            best, best_score = (cid, origin), score
    return best


def overlay(ax, bg2d, regions2d, title):
    ax.imshow(np.rot90(bg2d), cmap="gray")
    for name in ("WT", "TC", "ET"):  # nested draw order
        mask = np.rot90(regions2d[name])
        rgba = np.zeros((*mask.shape, 4))
        rgba[mask] = COLORS[name]
        ax.imshow(rgba)
    ax.set_title(title, fontsize=11)
    ax.axis("off")


def norm_bg(v):
    lo, hi = np.percentile(v[v > 0], [1, 99]) if (v > 0).any() else (v.min(), v.max())
    return np.clip((v - lo) / (hi - lo + 1e-8), 0, 1)


def comparison_architectures(cid, origin):
    """Compare the manual reference with the available architecture outputs."""
    t1c, gt = load_case(cid, origin)
    reg_gt = gt_regions(gt)
    z = int(np.argmax(reg_gt["WT"].sum(axis=(0, 1))))
    panels = [("Referencia manual", reg_gt)]
    # nnU-Net output uses raw BraTS labels (0-4) -> gt_regions convention.
    nnunet = ROOT / f"outputs/predictions/figA_nnunet/{cid}.nii.gz"
    if nnunet.exists():
        panels.append(("nnU-Net (ref.)", gt_regions(np.asarray(nib.load(nnunet).dataobj))))
    # tfm_brats predictions use the regions_to_labelmap encoding -> pred_regions.
    preds = {
        "Swin-UNETR": ROOT / f"outputs/predictions/figA_swin/{cid}.nii.gz",
        "Attention U-Net": ROOT / f"outputs/predictions/figA_attention/{cid}.nii.gz",
        "Residual + concatenación": ROOT / f"outputs/predictions/final_concat_seed20260526_test/{cid}.nii.gz",
    }
    for name, p in preds.items():
        panels.append((name, pred_regions(np.asarray(nib.load(p).dataobj))))
    fig, axs = plt.subplots(1, len(panels), figsize=(3.7 * len(panels), 4.3))
    for ax, (title, reg) in zip(axs, panels):
        overlay(ax, t1c[:, :, z], {k: v[:, :, z] for k, v in reg.items()}, title)
    legend = [mpatches.Patch(color=COLORS[k][:3], label=k) for k in ("ET", "TC", "WT")]
    fig.legend(handles=legend, loc="lower center", ncol=3, fontsize=10, frameon=False)
    fig.suptitle(f"Comparación cualitativa de arquitecturas — caso {cid} (corte axial z={z})", fontsize=12)
    fig.tight_layout(rect=[0, 0.06, 1, 0.95])
    fig.savefig(OUT / "fig_comparacion_arquitecturas.png", dpi=150)
    plt.close(fig)


def main():
    picked = pick_case()
    if picked is None:
        raise SystemExit("no suitable case found")
    cid, origin = picked
    print("caso elegido:", cid, origin)
    t1c, gt = load_case(cid, origin)
    reg_gt = gt_regions(gt)
    z = int(np.argmax(reg_gt["WT"].sum(axis=(0, 1))))  # axial slice with max WT area
    bg = norm_bg(t1c)[:, :, z]

    concat = np.asarray(nib.load(ROOT / f"outputs/predictions/final_concat_seed20260526_test/{cid}.nii.gz").dataobj)
    adap = np.asarray(nib.load(ROOT / f"outputs/predictions/final_adaptive_gating_seed20260528_test/{cid}.nii.gz").dataobj)
    reg_concat, reg_adap = pred_regions(concat), pred_regions(adap)
    sl = lambda r: {k: v[:, :, z] for k, v in r.items()}

    legend = [mpatches.Patch(color=COLORS[k][:3], label=k) for k in ("ET", "TC", "WT")]

    # Figure used in Chapter 5: one low-performance adaptive-gating run.
    fig, axs = plt.subplots(1, 3, figsize=(12, 4.5))
    overlay(axs[0], t1c[:, :, z], sl(reg_gt), "Referencia manual")
    overlay(axs[1], t1c[:, :, z], sl(reg_concat), "Concatenación (semilla 20260526)")
    overlay(
        axs[2],
        t1c[:, :, z],
        sl(reg_adap),
        "Compuerta adaptativa\n(corrida de bajo rendimiento)",
    )
    fig.legend(handles=legend, loc="lower center", ncol=3, fontsize=10, frameon=False)
    fig.suptitle(
        f"Corrida de bajo rendimiento de la fusión adaptativa — caso {cid} "
        f"(corte axial z={z})",
        fontsize=12,
    )
    fig.tight_layout(rect=[0, 0.06, 1, 0.96])
    fig.savefig(OUT / "fig_colapso_adaptive_gating.png", dpi=150)
    plt.close(fig)

    if (ROOT / "outputs/predictions/figA_swin" / f"{cid}.nii.gz").exists():
        comparison_architectures(cid, origin)
    print("figuras escritas en", OUT)


if __name__ == "__main__":
    main()
