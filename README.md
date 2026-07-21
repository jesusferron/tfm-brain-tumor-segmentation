# tfm-brain-tumor-segmentation

Repositorio del Trabajo de Fin de Máster sobre segmentación tridimensional de gliomas en MRI
multimodal con BraTS-GLI 2024. El estudio compara estrategias ligeras de fusión de las modalidades
T1n, T1c, T2w y FLAIR sobre una Residual U-Net 3D y contextualiza sus resultados mediante
Attention U-Net, Swin-UNETR y nnU-Net.

## Estado del proyecto

La fase experimental está cerrada. Las configuraciones basadas en MONAI se entrenaron con tres
semillas y 15.000 pasos; nnU-Net se utilizó como referencia externa mediante una corrida del
*fold* 0. Los resultados finales se encuentran en
[`outputs/evaluation/final_all_test.csv`](outputs/evaluation/final_all_test.csv).

| Configuración | n | Dice medio |
| :-- | :-: | :-: |
| nnU-Net `3d_fullres`, *fold* 0 | 1 | 0,829 |
| Swin-UNETR | 3 | 0,752 ± 0,017 |
| Attention U-Net 3D | 3 | 0,735 ± 0,006 |
| Residual U-Net + concatenación | 3 | 0,706 ± 0,005 |
| Residual U-Net + ponderación global | 3 | 0,706 ± 0,006 |
| Residual U-Net + compuerta adaptativa | 3 | 0,586 ± 0,169 |
| Residual U-Net + compuerta media+desviación | 3 | 0,592 ± 0,171 |

La ablación no encontró una mejora consistente de las ponderaciones explícitas frente a la
concatenación. Las variantes adaptativas presentaron una corrida de bajo rendimiento entre las tres
ejecutadas y una variabilidad entre semillas mayor. Esta conclusión se limita a los mecanismos, el
presupuesto y la partición empleados; no se extrapola a otras formas de fusión adaptativa.

La partición es disjunta por identificador completo de estudio, pero no está agrupada por sujeto.
Por tanto, permite una comparación interna de las estrategias de fusión bajo una partición común,
pero no constituye una evaluación independiente de generalización a pacientes nuevos.

## Memoria y trazabilidad

- Los seis capítulos y las referencias están en [`docs/memoria/`](docs/memoria/).
- La bitácora cronológica de decisiones y experimentos está en
  [`docs/vitacora/README.md`](docs/vitacora/README.md).
- Las configuraciones de los experimentos están en [`configs/`](configs/).
- Los datos originales, predicciones volumétricas y *checkpoints* no se distribuyen en el
  repositorio.

## Entorno y pruebas

Las dependencias del protocolo MONAI se enumeran en
[`requirements/protocol.txt`](requirements/protocol.txt). Las pruebas unitarias pueden ejecutarse
con:

```bash
python -m unittest discover -s tests -v
```

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
