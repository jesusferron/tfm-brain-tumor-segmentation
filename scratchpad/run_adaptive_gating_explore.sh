#!/usr/bin/env bash
# Exploracion del pilar 3 (adaptive_gating): 4 variantes, 5000 pasos cada una
# (M4 Pro, MPS, 128^3), secuenciales. Cada variante: train -> predict(val) ->
# evaluate(val) -> re-diagnostico de la compuerta.
# Plan y criterio: docs/adaptive-gating-exploration.md
set -u

cd /Users/jesusferron-personal/Repository/tfm-brain-tumor-segmentation
PY=.venv/bin/python
export PYTORCH_ENABLE_MPS_FALLBACK=1

DATASET=configs/dataset/brats_gli_2024.yaml
SPLITS=outputs/splits/brats_gli_2024_seed20260526
VAL=$SPLITS/val.csv
MAXSTEPS=5000
BASECFG=configs/training/mac_m4_pro_128_5k.yaml
STABCFG=configs/training/mac_m4_pro_128_5k_gate_stab.yaml

# name | model-config | training-config
RUNS=(
  "adaptive_gating_orig_stab|configs/model/residual_unet_3d_adaptive_gating.yaml|$STABCFG"
  "adaptive_gating_meanstd|configs/model/residual_unet_3d_adaptive_gating_meanstd.yaml|$BASECFG"
  "adaptive_gating_meanstd_stab|configs/model/residual_unet_3d_adaptive_gating_meanstd.yaml|$STABCFG"
  "adaptive_gating_meanstd_temp_stab|configs/model/residual_unet_3d_adaptive_gating_meanstd_temp.yaml|$STABCFG"
)

mkdir -p outputs/train outputs/predictions outputs/evaluation
DIAG=outputs/evaluation/adaptive_gating_explore_diagnosis.txt
: > "$DIAG"
echo "=== START $(date) | ${#RUNS[@]} variantes | max-steps=$MAXSTEPS | 128^3 | MPS ==="

for entry in "${RUNS[@]}"; do
  IFS='|' read -r name model train <<< "$entry"
  OUT="outputs/train/$name"
  LOG="outputs/train/${name}_stdout.log"
  PRED="outputs/predictions/${name}_val"
  echo ""
  echo ">>> [$(date)] RUN=$name | model=$model | train=$train"

  echo "  - train ..."
  $PY -m tfm_brats.cli train \
    --dataset-config "$DATASET" --model-config "$model" --training-config "$train" \
    --split-dir "$SPLITS" --output-dir "$OUT" --max-steps "$MAXSTEPS" > "$LOG" 2>&1
  rc=$?; [ $rc -ne 0 ] && { echo "  <<< FAIL train $name (rc=$rc) -- ver $LOG"; continue; }

  echo "  - predict(val) ..."
  $PY -m tfm_brats.cli predict \
    --dataset-config "$DATASET" --model-config "$model" --training-config "$train" \
    --split-csv "$VAL" --checkpoint "$OUT/checkpoints/best.pt" \
    --output-dir "$PRED" >> "$LOG" 2>&1
  rc=$?; [ $rc -ne 0 ] && { echo "  <<< FAIL predict $name (rc=$rc) -- ver $LOG"; continue; }

  echo "  - evaluate(val) ..."
  $PY -m tfm_brats.cli evaluate \
    --dataset-config "$DATASET" --split-csv "$VAL" --predictions-dir "$PRED" \
    --output-csv "outputs/evaluation/${name}_val_metrics.csv" \
    --output-json "outputs/evaluation/${name}_val_metrics_summary.json" >> "$LOG" 2>&1
  rc=$?; [ $rc -ne 0 ] && { echo "  <<< FAIL evaluate $name (rc=$rc) -- ver $LOG"; continue; }

  echo "  - diagnose (gate) ..."
  {
    echo "===== $name ($(date)) ====="
    $PY scripts/diagnose_adaptive_gating.py --checkpoint "$OUT/checkpoints/best.pt" \
      --model-config "$model" --max-cases 40 --device cpu 2>/dev/null | grep -Ev "^\[gate\] [0-9]+/"
    echo ""
  } >> "$DIAG" 2>&1

  echo "  <<< [$(date)] OK $name -> outputs/evaluation/${name}_val_metrics_summary.json"
done

echo ""
echo "=== DONE $(date) ==="
echo "Resumen de metricas:"
for entry in "${RUNS[@]}"; do
  IFS='|' read -r name _ _ <<< "$entry"
  f="outputs/evaluation/${name}_val_metrics_summary.json"
  [ -f "$f" ] && echo "  $name: $f" || echo "  $name: (sin resultado)"
done
touch outputs/train/_adaptive_gating_explore.DONE
