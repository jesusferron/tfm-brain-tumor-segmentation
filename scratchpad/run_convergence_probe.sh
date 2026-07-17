#!/usr/bin/env bash
# Sonda de convergencia: concat a 25000 pasos con cosine LR, para ver donde
# mesetea el val y fijar el presupuesto de la corrida final. M4 Pro, MPS, 128^3.
set -u
cd /Users/jesusferron-personal/Repository/tfm-brain-tumor-segmentation
PY=.venv/bin/python
export PYTORCH_ENABLE_MPS_FALLBACK=1
echo "=== PROBE START $(date) ==="
$PY -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/residual_unet_3d.yaml \
  --training-config configs/training/mac_m4_pro_128_final.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/probe_concat_25k \
  --max-steps 25000 > outputs/train/probe_concat_25k_stdout.log 2>&1
echo "rc=$?"
touch outputs/train/_probe.DONE
echo "=== PROBE DONE $(date) ==="
