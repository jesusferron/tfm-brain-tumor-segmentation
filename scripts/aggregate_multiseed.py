#!/usr/bin/env python3
"""Aggregate per-seed val metrics into mean +/- std per model.

Usage:
  aggregate_multiseed.py --out outputs/evaluation/multiseed_summary.csv \
      --group "concat=fileA.json,fileB.json,fileC.json" \
      --group "meanstd=fileA.json,fileB.json,fileC.json"

Each file is a *_val_metrics_summary.json produced by `tfm_brats.cli evaluate`.
Reports mean Dice (average of ET/TC/WT means) and per-region Dice, as
mean +/- std across the provided seeds.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean, pstdev


REGIONS = ("ET", "TC", "WT")


def _mean_dice(path: Path) -> tuple[float, dict[str, float]]:
    agg = json.loads(path.read_text())["aggregates"]
    per = {r: float(agg[f"{r}_dice"]["mean"]) for r in REGIONS}
    return sum(per.values()) / len(REGIONS), per


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", action="append", required=True, help="NAME=f1,f2,f3")
    parser.add_argument("--out", default="outputs/evaluation/multiseed_summary.csv")
    args = parser.parse_args()

    rows = []
    print(f"{'model':<16}{'n':>3}{'meanDice':>18}{'ET':>16}{'TC':>16}{'WT':>16}")
    for group in args.group:
        name, files = group.split("=", 1)
        paths = [Path(p) for p in files.split(",") if p]
        md, per = [], {r: [] for r in REGIONS}
        for p in paths:
            if not p.is_file():
                print(f"  [warn] missing {p}")
                continue
            m, region = _mean_dice(p)
            md.append(m)
            for r in REGIONS:
                per[r].append(region[r])
        n = len(md)
        if n == 0:
            print(f"{name:<16}{0:>3}  (no files)")
            continue

        def ms(vals):
            return mean(vals), (pstdev(vals) if len(vals) > 1 else 0.0)

        md_m, md_s = ms(md)
        cell = lambda v: f"{ms(v)[0]:.3f}+/-{ms(v)[1]:.3f}"
        print(f"{name:<16}{n:>3}{f'{md_m:.4f}+/-{md_s:.4f}':>18}{cell(per['ET']):>16}{cell(per['TC']):>16}{cell(per['WT']):>16}")
        row = {"model": name, "n_seeds": n, "mean_dice_mean": round(md_m, 4), "mean_dice_std": round(md_s, 4)}
        for r in REGIONS:
            rm, rs = ms(per[r])
            row[f"{r}_dice_mean"] = round(rm, 4)
            row[f"{r}_dice_std"] = round(rs, 4)
        rows.append(row)

    if rows:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nwritten {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
