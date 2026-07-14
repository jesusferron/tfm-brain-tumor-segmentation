# Baseline fuerte nnU-Net v2 (BraTS-GLI 2024)

nnU-Net se usa como **baseline externo reproducible** (pilar 1 del objetivo defendible), no como un modelo dentro de la pipeline MONAI propia. Este documento describe el flujo completo en cloud: convertir los splits del TFM al formato nnU-Net, planificar/preprocesar, entrenar, predecir sobre `val` y evaluar con el mismo `evaluate` del TFM para obtener métricas directamente comparables (Dice y HD95 por ET/TC/WT).

Referencia de datos y configuración: [`configs/nnunet/brats_gli_2024_full.yaml`](../configs/nnunet/brats_gli_2024_full.yaml). Conversor: [`scripts/nnunet/prepare_brats_gli_nnunet_full.py`](../scripts/nnunet/prepare_brats_gli_nnunet_full.py).

## Decisiones metodológicas

- **Conversión directa al formato nnU-Net v2** (no el apilado 4D del smoke test). Cada modalidad se enlaza (symlink) con el naming de canal de nnU-Net (`{case_id}_0000..0003.nii.gz`), sin duplicar datos.
- **Mismo split que el resto del TFM.** `imagesTr`/`labelsTr` = split `train` (1135 casos); `imagesTs` = split `val` (243 casos), que queda **fuera** de los folds internos de nnU-Net (held out del entrenamiento). El split `test` no se toca hasta la evaluación final.
- **Etiquetas 0-4 preservadas** (BraTS-GLI 2024: 0=fondo, 1=NCR, 2=ED, 3=ET, 4=RC). Como el mapa predicho usa el mismo esquema entero que el ground truth, el `evaluate` del TFM (que mapea etiquetas → ET/TC/WT) funciona sobre las predicciones nnU-Net **sin conversor adicional** y produce métricas comparables con los modelos MONAI.
- **Identificador nnU-Net = `case_id`.** Así la predicción de cada caso de `val` sale como `{case_id}.nii.gz`, exactamente lo que espera el `evaluate` del TFM.
- **`3d_fullres`, fold 0.** Baseline de un solo fold (el ensemble de 5 folds queda fuera del presupuesto de cómputo). Se documenta como decisión.
- **Épocas reducidas (`nnUNetTrainer_250epochs`).** El trainer por defecto de nnU-Net son 1000 épocas (días en una sola GPU). 250 épocas es un compromiso de presupuesto; el 1000-épocas por defecto es el nnU-Net canónico y queda como opción si el tiempo lo permite.

## 0. Prerrequisitos en Colab

Igual que en la [guía de Colab](colab-pro-baseline-residual-unet.md): GPU (L4 o A100), Drive montado, repo clonado (con token), dependencias del protocolo instaladas y **dataset copiado a `/content/TFM-datasets`** con `dataset_root` apuntando ahí (secciones 1-5 de esa guía). nnU-Net es pesado; usa A100 si está disponible.

Instala además nnU-Net v2:

```python
!pip install -r requirements/nnunet.txt
!python -c "import nnunetv2; print('nnunetv2', nnunetv2.__version__)"
```

## 1. Convertir los splits del TFM al formato nnU-Net

```python
!python scripts/nnunet/prepare_brats_gli_nnunet_full.py --dataset-config configs/dataset/brats_gli_2024.yaml --split-dir outputs/splits/brats_gli_2024_seed20260526 --train-split train.csv --test-split val.csv --nnunet-raw /content/nnUNet_raw --dataset-id 725 --dataset-name BraTSGLI2024 --link-mode symlink
```

Debe reportar 1135 casos de entrenamiento (x4 canales), 1135 labels y 243 casos en `imagesTs`, y escribir `dataset.json`. Si el runtime no permite symlink al dataset, usa `--link-mode copy` (duplica en disco).

## 2. Exportar variables de entorno de nnU-Net

nnU-Net trabaja con tres carpetas en disco local del runtime (nunca Drive):

```python
import os
os.environ["nnUNet_raw"] = "/content/nnUNet_raw"
os.environ["nnUNet_preprocessed"] = "/content/nnUNet_preprocessed"
os.environ["nnUNet_results"] = "/content/nnUNet_results"
print("nnU-Net env listo")
```

## 3. Planificar y preprocesar (con verificación de integridad)

```python
!nnUNetv2_plan_and_preprocess -d 725 --verify_dataset_integrity
```

La verificación confirma que las etiquetas de los ficheros están declaradas en `dataset.json` y que shapes/affines son consistentes. Si falla aquí, no entrenes.

## 4. Entrenar `3d_fullres`, fold 0 (250 épocas)

```python
!nnUNetv2_train 725 3d_fullres 0 -tr nnUNetTrainer_250epochs
```

Es la fase larga (varias horas en A100). nnU-Net hace su propia validación interna sobre el 20% del split `train` (fold 0) y guarda `checkpoint_best.pth` y `checkpoint_final.pth`. Vigila que la GPU no dé OOM (nnU-Net auto-ajusta el batch, suele caber). Para el nnU-Net canónico, omite `-tr` (1000 épocas).

## 5. Predecir sobre `val` (held out)

```python
!nnUNetv2_predict -i /content/nnUNet_raw/Dataset725_BraTSGLI2024/imagesTs -o /content/nnunet_pred_val -d 725 -c 3d_fullres -f 0 -tr nnUNetTrainer_250epochs -chk checkpoint_best.pth
```

Genera un `{case_id}.nii.gz` por caso de `val` en `/content/nnunet_pred_val` (mismo esquema de etiquetas 0-4 que el ground truth).

## 6. Evaluar con el `evaluate` del TFM (métricas comparables)

Reutiliza el mismo comando que el resto de modelos; las predicciones ya están nombradas por `case_id`:

```python
!python -m tfm_brats.cli evaluate --dataset-config configs/dataset/brats_gli_2024.yaml --split-csv outputs/splits/brats_gli_2024_seed20260526/val.csv --predictions-dir /content/nnunet_pred_val --output-csv outputs/evaluation/nnunet_3dfullres_val_metrics.csv --output-json outputs/evaluation/nnunet_3dfullres_val_metrics_summary.json
!cat outputs/evaluation/nnunet_3dfullres_val_metrics_summary.json
```

El resumen da Dice y HD95 por ET/TC/WT, comparable directamente con `swin_unetr_l4` y los modelos residuales.

## 7. Descargar artefactos

Mínimo a devolver: el JSON de métricas y el resumen del entrenamiento de nnU-Net.

```python
!zip -r nnunet_3dfullres_results.zip outputs/evaluation/nnunet_3dfullres_val_metrics.csv outputs/evaluation/nnunet_3dfullres_val_metrics_summary.json /content/nnUNet_results/Dataset725_BraTSGLI2024
from google.colab import files
files.download('nnunet_3dfullres_results.zip')
```

## Evaluación final sobre `test`

Cuando la configuración esté congelada y toque el hold-out: re-ejecuta el paso 1 con `--test-split test.csv` (regenera `imagesTs` con los casos de test), predice igual que el paso 5 y evalúa con `--split-csv .../test.csv`. No antes.

## Qué mandarme al terminar

```text
GPU (nvidia-smi):
plan_and_preprocess termino sin error: si/no
Entrenamiento: epocas completadas / se corto:
Pico de memoria GPU:
Contenido de nnunet_3dfullres_val_metrics_summary.json:
```
