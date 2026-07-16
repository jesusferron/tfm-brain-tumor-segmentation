#!/usr/bin/env bash
# Multi-semilla para confirmar el margen de la fusion mean+std sobre concat.
# 2 modelos x 2 semillas NUEVAS (la semilla A 20260526 ya esta calculada y se
# reutiliza en la agregacion). Cada run: train(--seed) -> predict(val) -> evaluate.
# M4 Pro, MPS, 128^3, 5000 pasos, config base (sin knobs de estabilizacion) para
# comparar en igualdad con la semilla A. Ver docs/adaptive-gating-exploration.md.
set -u

cd /Users/jesusferron-personal/Repository/tfm-brain-tumor-segmentation
PY=.venv/bin/python
export PYTORCH_ENABLE_MPS_FALLBACK=1

DATASET=configs/dataset/brats_gli_2024.yaml
TRAINCFG=configs/training/mac_m4_pro_128_5k.yaml
SPLITS=outputs/splits/brats_gli_2024_seed20260526
VAL=$SPLITS/val.csv
MAXSTEPS=5000
SEEDS=(20260527 20260528)

# label | model-config
MODELS=(
  "residual_unet_3d|configs/model/residual_unet_3d.yaml"
  "meanstd|configs/model/residual_unet_3d_adaptive_gating_meanstd.yaml"
)

mkdir -p outputs/train outputs/predictions outputs/evaluation
echo "=== START $(date) | multi-semilla | seeds=${SEEDS[*]} | max-steps=$MAXSTEPS ==="

for entry in "${MODELS[@]}"; do
  IFS='|' read -r label model <<< "$entry"
  for seed in "${SEEDS[@]}"; do
    tag="multiseed_${label}_seed${seed}"
    OUT="outputs/train/$tag"
    LOG="outputs/train/${tag}_stdout.log"
    PRED="outputs/predictions/${tag}_val"
    echo ""
    echo ">>> [$(date)] $tag | model=$model | seed=$seed"
    $PY -m tfm_brats.cli train \
      --dataset-config "$DATASET" --model-config "$model" --training-config "$TRAINCFG" \
      --split-dir "$SPLITS" --output-dir "$OUT" --max-steps "$MAXSTEPS" --seed "$seed" > "$LOG" 2>&1
    rc=$?; [ $rc -ne 0 ] && { echo "  <<< FAIL train $tag (rc=$rc) -- ver $LOG"; continue; }
    $PY -m tfm_brats.cli predict \
      --dataset-config "$DATASET" --model-config "$model" --training-config "$TRAINCFG" \
      --split-csv "$VAL" --checkpoint "$OUT/checkpoints/best.pt" --output-dir "$PRED" >> "$LOG" 2>&1
    rc=$?; [ $rc -ne 0 ] && { echo "  <<< FAIL predict $tag (rc=$rc) -- ver $LOG"; continue; }
    $PY -m tfm_brats.cli evaluate \
      --dataset-config "$DATASET" --split-csv "$VAL" --predictions-dir "$PRED" \
      --output-csv "outputs/evaluation/${tag}_val_metrics.csv" \
      --output-json "outputs/evaluation/${tag}_val_metrics_summary.json" >> "$LOG" 2>&1
    rc=$?; [ $rc -ne 0 ] && { echo "  <<< FAIL evaluate $tag (rc=$rc) -- ver $LOG"; continue; }
    echo "  <<< [$(date)] OK $tag"
  done
done

echo ""
echo "=== AGGREGATE $(date) (3 semillas por modelo: A=20260526 + ${SEEDS[*]}) ==="
CONCAT_A=outputs/evaluation/residual_unet_3d_val_metrics_summary.json
MEANSTD_A=outputs/evaluation/adaptive_gating_meanstd_val_metrics_summary.json
$PY scripts/aggregate_multiseed.py \
  --out outputs/evaluation/multiseed_meanstd_vs_concat.csv \
  --group "concat=$CONCAT_A,outputs/evaluation/multiseed_residual_unet_3d_seed20260527_val_metrics_summary.json,outputs/evaluation/multiseed_residual_unet_3d_seed20260528_val_metrics_summary.json" \
  --group "meanstd=$MEANSTD_A,outputs/evaluation/multiseed_meanstd_seed20260527_val_metrics_summary.json,outputs/evaluation/multiseed_meanstd_seed20260528_val_metrics_summary.json"

touch outputs/train/_multiseed.DONE
echo "=== DONE $(date) ==="
