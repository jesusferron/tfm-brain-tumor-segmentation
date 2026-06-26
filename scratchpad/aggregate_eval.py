"""Agrega los summary JSON de evaluacion de los 4 modelos en una tabla comparativa.

Lee outputs/evaluation/<modelo>_val_metrics_summary.json y escribe:
  - outputs/evaluation/comparativa_val_5k.csv
  - una tabla por stdout
Metrica: Dice y HD95 medios por region (ET/TC/WT) + Dice medio entre regiones.
"""
import csv
import json
from pathlib import Path

REPO = Path("/Users/jesusferron-personal/Repository/tfm-brain-tumor-segmentation")
REGIONS = ["ET", "TC", "WT"]
MODELS = [
    ("residual_unet_3d", "baseline (concat)"),
    ("residual_unet_3d_global_weighted", "global_weighted"),
    ("residual_unet_3d_adaptive_gating", "adaptive_gating"),
    ("attention_unet_3d", "attention"),
]

rows = []
for key, label in MODELS:
    sj = REPO / "outputs" / "evaluation" / f"{key}_val_metrics_summary.json"
    if not sj.is_file():
        print(f"[WARN] falta {sj}")
        continue
    agg = json.loads(sj.read_text())["aggregates"]
    row = {"model": key, "label": label, "cases": json.loads(sj.read_text()).get("cases")}
    dices = []
    for r in REGIONS:
        d = agg[f"{r}_dice"]["mean"]
        h = agg[f"{r}_hd95"]["mean"]
        row[f"{r}_dice"] = d
        row[f"{r}_hd95"] = h
        dices.append(d)
    row["mean_dice"] = sum(dices) / len(dices) if dices else float("nan")
    rows.append(row)

if not rows:
    print("No hay summaries de evaluacion todavia.")
    raise SystemExit(0)

out_csv = REPO / "outputs" / "evaluation" / "comparativa_val_5k.csv"
fields = ["model", "label", "cases", "mean_dice",
          "ET_dice", "TC_dice", "WT_dice", "ET_hd95", "TC_hd95", "WT_hd95"]
with out_csv.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in fields})

print(f"\n=== Comparativa val (5000 pasos, {rows[0].get('cases')} casos) ===")
hdr = f"{'modelo':<20} {'meanDice':>9} {'ET':>7} {'TC':>7} {'WT':>7} | {'ET_hd95':>8} {'TC_hd95':>8} {'WT_hd95':>8}"
print(hdr)
print("-" * len(hdr))
for r in rows:
    print(f"{r['label']:<20} {r['mean_dice']:>9.4f} "
          f"{r['ET_dice']:>7.3f} {r['TC_dice']:>7.3f} {r['WT_dice']:>7.3f} | "
          f"{r['ET_hd95']:>8.2f} {r['TC_hd95']:>8.2f} {r['WT_hd95']:>8.2f}")
print(f"\nCSV: {out_csv}")
