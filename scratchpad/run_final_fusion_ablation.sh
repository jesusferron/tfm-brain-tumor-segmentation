#!/usr/bin/env bash
# Corrida FINAL - ablacion de fusion (M4 Pro, MPS, 128^3, 15000 pasos, cosine LR).
# 4 modelos x 3 semillas. Entrena (best.pt por val) -> predict sobre TEST ->
# evaluate sobre TEST (held-out, cifras reportables). Agrega media+/-std al final.
# Config congelada: mac_m4_pro_128_final.yaml + --max-steps 15000. Presupuesto
# fijado por la sonda de convergencia (docs/vitacora/README.md 2026-07-17).
set -u

cd /Users/jesusferron-personal/Repository/tfm-brain-tumor-segmentation
PY=.venv/bin/python
export PYTORCH_ENABLE_MPS_FALLBACK=1

DATASET=configs/dataset/brats_gli_2024.yaml
TRAINCFG=configs/training/mac_m4_pro_128_final.yaml
SPLITS=outputs/splits/brats_gli_2024_seed20260526
TEST=$SPLITS/test.csv
MAXSTEPS=15000
SEEDS=(20260526 20260527 20260528)

# label | model-config
MODELS=(
  "concat|configs/model/residual_unet_3d.yaml"
  "adaptive_gating_meanstd|configs/model/residual_unet_3d_adaptive_gating_meanstd.yaml"
  "global_weighted|configs/model/residual_unet_3d_global_weighted.yaml"
  "adaptive_gating|configs/model/residual_unet_3d_adaptive_gating.yaml"
)

mkdir -p outputs/train outputs/predictions outputs/evaluation
echo "=== FINAL FUSION ABLATION START $(date) | 4 modelos x ${#SEEDS[@]} semillas | ${MAXSTEPS} pasos ==="

for entry in "${MODELS[@]}"; do
  IFS='|' read -r label model <<< "$entry"
  for seed in "${SEEDS[@]}"; do
    tag="final_${label}_seed${seed}"
    OUT="outputs/train/$tag"; LOG="outputs/train/${tag}_stdout.log"; PRED="outputs/predictions/${tag}_test"
    echo ""; echo ">>> [$(date)] $tag"
    $PY -m tfm_brats.cli train \
      --dataset-config "$DATASET" --model-config "$model" --training-config "$TRAINCFG" \
      --split-dir "$SPLITS" --output-dir "$OUT" --max-steps "$MAXSTEPS" --seed "$seed" > "$LOG" 2>&1
    rc=$?; [ $rc -ne 0 ] && { echo "  <<< FAIL train $tag (rc=$rc)"; continue; }
    $PY -m tfm_brats.cli predict \
      --dataset-config "$DATASET" --model-config "$model" --training-config "$TRAINCFG" \
      --split-csv "$TEST" --checkpoint "$OUT/checkpoints/best.pt" --output-dir "$PRED" >> "$LOG" 2>&1
    rc=$?; [ $rc -ne 0 ] && { echo "  <<< FAIL predict $tag (rc=$rc)"; continue; }
    $PY -m tfm_brats.cli evaluate \
      --dataset-config "$DATASET" --split-csv "$TEST" --predictions-dir "$PRED" \
      --output-csv "outputs/evaluation/${tag}_test_metrics.csv" \
      --output-json "outputs/evaluation/${tag}_test_metrics_summary.json" >> "$LOG" 2>&1
    rc=$?; [ $rc -ne 0 ] && { echo "  <<< FAIL evaluate $tag (rc=$rc)"; continue; }
    echo "  <<< [$(date)] OK $tag"
  done
done

echo ""; echo "=== AGGREGATE (TEST, 3 semillas) $(date) ==="
E=outputs/evaluation
mk() { echo "$E/final_${1}_seed20260526_test_metrics_summary.json,$E/final_${1}_seed20260527_test_metrics_summary.json,$E/final_${1}_seed20260528_test_metrics_summary.json"; }
$PY scripts/aggregate_multiseed.py --out $E/final_fusion_ablation_test.csv \
  --group "concat=$(mk concat)" \
  --group "global_weighted=$(mk global_weighted)" \
  --group "adaptive_gating=$(mk adaptive_gating)" \
  --group "adaptive_gating_meanstd=$(mk adaptive_gating_meanstd)"

touch outputs/train/_final_fusion.DONE
echo "=== FINAL FUSION ABLATION DONE $(date) ==="
