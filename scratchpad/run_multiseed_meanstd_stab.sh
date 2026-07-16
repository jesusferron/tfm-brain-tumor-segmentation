#!/usr/bin/env bash
# Ultima via del pilar 3: multi-semilla de la variante ESTABILIZADA
# (mean+std + gate_stab), por si la estabilizacion evita el colapso entre
# semillas que hundio a la variante base. 2 semillas nuevas; la semilla A
# (20260526) ya esta (R3 de la exploracion, adaptive_gating_meanstd_stab).
# Al final agrega concat / meanstd(base) / meanstd_stab a 3 semillas.
set -u

cd /Users/jesusferron-personal/Repository/tfm-brain-tumor-segmentation
PY=.venv/bin/python
export PYTORCH_ENABLE_MPS_FALLBACK=1

DATASET=configs/dataset/brats_gli_2024.yaml
MODEL=configs/model/residual_unet_3d_adaptive_gating_meanstd.yaml
TRAINCFG=configs/training/mac_m4_pro_128_5k_gate_stab.yaml
SPLITS=outputs/splits/brats_gli_2024_seed20260526
VAL=$SPLITS/val.csv
MAXSTEPS=5000
SEEDS=(20260527 20260528)

mkdir -p outputs/train outputs/predictions outputs/evaluation
echo "=== START $(date) | meanstd_stab multi-semilla | seeds=${SEEDS[*]} ==="

for seed in "${SEEDS[@]}"; do
  tag="multiseed_meanstd_stab_seed${seed}"
  OUT="outputs/train/$tag"; LOG="outputs/train/${tag}_stdout.log"; PRED="outputs/predictions/${tag}_val"
  echo ""; echo ">>> [$(date)] $tag | seed=$seed"
  $PY -m tfm_brats.cli train \
    --dataset-config "$DATASET" --model-config "$MODEL" --training-config "$TRAINCFG" \
    --split-dir "$SPLITS" --output-dir "$OUT" --max-steps "$MAXSTEPS" --seed "$seed" > "$LOG" 2>&1
  rc=$?; [ $rc -ne 0 ] && { echo "  <<< FAIL train $tag (rc=$rc)"; continue; }
  $PY -m tfm_brats.cli predict \
    --dataset-config "$DATASET" --model-config "$MODEL" --training-config "$TRAINCFG" \
    --split-csv "$VAL" --checkpoint "$OUT/checkpoints/best.pt" --output-dir "$PRED" >> "$LOG" 2>&1
  rc=$?; [ $rc -ne 0 ] && { echo "  <<< FAIL predict $tag (rc=$rc)"; continue; }
  $PY -m tfm_brats.cli evaluate \
    --dataset-config "$DATASET" --split-csv "$VAL" --predictions-dir "$PRED" \
    --output-csv "outputs/evaluation/${tag}_val_metrics.csv" \
    --output-json "outputs/evaluation/${tag}_val_metrics_summary.json" >> "$LOG" 2>&1
  rc=$?; [ $rc -ne 0 ] && { echo "  <<< FAIL evaluate $tag (rc=$rc)"; continue; }
  echo "  <<< [$(date)] OK $tag"
done

echo ""; echo "=== AGGREGATE $(date) (3 semillas por modelo) ==="
E=outputs/evaluation
$PY scripts/aggregate_multiseed.py --out $E/multiseed_pillar3_final.csv \
  --group "concat=$E/residual_unet_3d_val_metrics_summary.json,$E/multiseed_residual_unet_3d_seed20260527_val_metrics_summary.json,$E/multiseed_residual_unet_3d_seed20260528_val_metrics_summary.json" \
  --group "meanstd_base=$E/adaptive_gating_meanstd_val_metrics_summary.json,$E/multiseed_meanstd_seed20260527_val_metrics_summary.json,$E/multiseed_meanstd_seed20260528_val_metrics_summary.json" \
  --group "meanstd_stab=$E/adaptive_gating_meanstd_stab_val_metrics_summary.json,$E/multiseed_meanstd_stab_seed20260527_val_metrics_summary.json,$E/multiseed_meanstd_stab_seed20260528_val_metrics_summary.json"

touch outputs/train/_multiseed_stab.DONE
echo "=== DONE $(date) ==="
