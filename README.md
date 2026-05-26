# tfm-brain-tumor-segmentation

Repositorio de protocolo experimental para segmentación BraTS-GLI 2024.

## Comandos principales

Ejecutar desde la raíz del repo con el entorno virtual activo o con `.venv/bin/python`.

```bash
.venv/bin/python -m tfm_brats.cli qc \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --output-csv outputs/qc/brats_gli_2024_qc.csv \
  --output-json outputs/qc/brats_gli_2024_qc_summary.json
```

```bash
.venv/bin/python -m tfm_brats.cli splits \
  --qc-csv outputs/qc/brats_gli_2024_qc.csv \
  --output-dir outputs/splits/brats_gli_2024_seed20260526 \
  --seed 20260526 \
  --ratios 70/15/15
```

```bash
.venv/bin/python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/residual_unet_3d.yaml \
  --training-config configs/training/local_smoke.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/residual_unet_3d
```

```bash
.venv/bin/python -m tfm_brats.cli predict \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/residual_unet_3d.yaml \
  --training-config configs/training/local_smoke.yaml \
  --split-csv outputs/splits/brats_gli_2024_seed20260526/test.csv \
  --checkpoint outputs/train/residual_unet_3d/checkpoints/best.pt \
  --output-dir outputs/predictions/residual_unet_3d_test
```

```bash
.venv/bin/python -m tfm_brats.cli evaluate \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --split-csv outputs/splits/brats_gli_2024_seed20260526/test.csv \
  --predictions-dir outputs/predictions/residual_unet_3d_test \
  --output-csv outputs/evaluation/residual_unet_3d_metrics.csv \
  --output-json outputs/evaluation/residual_unet_3d_metrics_summary.json
```

## Convenciones BraTS

- Modalidades: `t1n`, `t1c`, `t2w`, `t2f`.
- Etiquetas válidas: `0`, `1`, `2`, `3`, `4`.
- Regiones evaluadas: `ET = 3`, `TC = 1/3/4`, `WT = 1/2/3/4`.
- Split por defecto: semilla `20260526`, proporción `70/15/15`, estratificado por origen, presencia de ET y bins de volumen WT.

## Artefactos

Se versionan configuraciones, manifiestos, splits y métricas agregadas. No se versionan NIfTI, predicciones, checkpoints, logs de entrenamiento ni directorios generados por nnU-Net (`nnUNet_raw`, `nnUNet_preprocessed`, `nnUNet_results`).

El protocolo experimental priorizado queda en `configs/experiments/brats_gli_2024_protocol.yaml`.

El entrenamiento guarda `last.pt`, `best.pt`, `train_log.csv` y `train_summary.json`; la validación y predicción usan sliding-window inference.
