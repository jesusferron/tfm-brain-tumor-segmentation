#!/usr/bin/env bash
# Encadenado: espera a que termine la corrida de 5000 pasos y luego ejecuta
# predict + evaluate sobre el split val completo para los 4 modelos, con su best.pt.
# Finalmente agrega una tabla comparativa. Ver docs/vitacora/README.md (2026-06-26).
set -u

cd /Users/jesusferron-personal/Repository/tfm-brain-tumor-segmentation
PY=.venv/bin/python
export PYTORCH_ENABLE_MPS_FALLBACK=1

DATASET=configs/dataset/brats_gli_2024.yaml
INFERCFG=configs/training/mac_m4_pro_128_5k.yaml   # roi sliding window 128^3, device mps
SPLITS=outputs/splits/brats_gli_2024_seed20260526
VAL_CSV="$SPLITS/val.csv"
ORCH=outputs/train/_run_local_4models_5k.orchestrator.log

MODELS=(
  "residual_unet_3d"
  "residual_unet_3d_global_weighted"
  "residual_unet_3d_adaptive_gating"
  "attention_unet_3d"
)

# 1) Esperar a que la corrida de 5000 pasos marque DONE (no solapar GPU MPS).
echo "=== ESPERANDO fin de la corrida 5k ($(date)) ==="
for i in $(seq 1 720); do   # hasta ~6h de guarda (720 * 30s)
  if grep -q "=== DONE" "$ORCH" 2>/dev/null; then echo "Corrida 5k terminada ($(date))."; break; fi
  sleep 30
done

mkdir -p outputs/predictions outputs/evaluation
echo ""; echo "=== START predict+evaluate $(date) | val=$(wc -l < "$VAL_CSV") lineas ==="
for m in "${MODELS[@]}"; do
  CKPT="outputs/train/${m}_m4_pro_128_5k/checkpoints/best.pt"
  PRED_DIR="outputs/predictions/${m}_val_5k"
  EVAL_CSV="outputs/evaluation/${m}_val_metrics.csv"
  EVAL_JSON="outputs/evaluation/${m}_val_metrics_summary.json"
  LOG="outputs/evaluation/${m}_predict_evaluate.log"
  echo ""; echo ">>> [$(date)] $m"
  if [ ! -f "$CKPT" ]; then echo "  SKIP: falta $CKPT"; continue; fi

  echo "  predict -> $PRED_DIR"
  $PY -m tfm_brats.cli predict \
    --dataset-config "$DATASET" \
    --model-config "configs/model/${m}.yaml" \
    --training-config "$INFERCFG" \
    --split-csv "$VAL_CSV" \
    --checkpoint "$CKPT" \
    --output-dir "$PRED_DIR" \
    > "$LOG" 2>&1
  rc=$?
  if [ $rc -ne 0 ]; then echo "  FAIL predict (rc=$rc) -- ver $LOG"; continue; fi

  echo "  evaluate -> $EVAL_JSON"
  $PY -m tfm_brats.cli evaluate \
    --dataset-config "$DATASET" \
    --split-csv "$VAL_CSV" \
    --predictions-dir "$PRED_DIR" \
    --output-csv "$EVAL_CSV" \
    --output-json "$EVAL_JSON" \
    >> "$LOG" 2>&1
  rc=$?
  if [ $rc -eq 0 ]; then echo "  OK $m"; else echo "  FAIL evaluate (rc=$rc) -- ver $LOG"; fi
done

echo ""; echo "=== AGREGANDO tabla comparativa ==="
$PY scratchpad/aggregate_eval.py
echo ""; echo "=== DONE $(date) ==="
