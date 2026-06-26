#!/usr/bin/env bash
# Pase de validacion (~300 pasos) de los 4 modelos pequenos en local (M4 Pro, MPS, 128^3).
# Secuencial: una sola GPU MPS. Ver docs/vitacora/README.md (entrada 2026-06-25).
set -u

cd /Users/jesusferron-personal/Repository/tfm-brain-tumor-segmentation
PY=.venv/bin/python
export PYTORCH_ENABLE_MPS_FALLBACK=1

DATASET=configs/dataset/brats_gli_2024.yaml
TRAINCFG=configs/training/mac_m4_pro_128.yaml
SPLITS=outputs/splits/brats_gli_2024_seed20260526
MAXSTEPS=300

MODELS=(
  "residual_unet_3d"
  "residual_unet_3d_global_weighted"
  "residual_unet_3d_adaptive_gating"
  "attention_unet_3d"
)

mkdir -p outputs/train
echo "=== START $(date) | 4 modelos | max-steps=$MAXSTEPS | 128^3 | MPS ==="
for m in "${MODELS[@]}"; do
  OUT="outputs/train/${m}_m4_pro_128"
  LOG="outputs/train/${m}_m4_pro_128_stdout.log"
  echo ""
  echo ">>> [$(date)] MODEL=$m -> $OUT"
  $PY -m tfm_brats.cli train \
    --dataset-config "$DATASET" \
    --model-config "configs/model/${m}.yaml" \
    --training-config "$TRAINCFG" \
    --split-dir "$SPLITS" \
    --output-dir "$OUT" \
    --max-steps "$MAXSTEPS" \
    > "$LOG" 2>&1
  rc=$?
  if [ $rc -eq 0 ]; then
    echo "<<< [$(date)] OK $m (rc=0)"
  else
    echo "<<< [$(date)] FAIL $m (rc=$rc) -- ver $LOG"
  fi
done
echo ""
echo "=== DONE $(date) ==="
