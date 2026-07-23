# Apéndice A. Reproducibilidad

Este apéndice identifica el código, las configuraciones, los comandos y los artefactos necesarios
para auditar el trabajo. No sustituye las condiciones de acceso al conjunto BraTS-GLI 2024 ni
permite reconstruir los entrenamientos pesados sin disponer de los datos y del entorno de cómputo.

## A.1. Repositorio y versión de entrega

- Repositorio remoto configurado:
  [https://github.com/jesusferron/tfm-brain-tumor-segmentation](https://github.com/jesusferron/tfm-brain-tumor-segmentation).
- Rama de trabajo: `main`.
- SHA de referencia al iniciar esta revisión:
  `89c778d211264fab2ae835f60b10347e677783c9`.

El SHA anterior precede a las correcciones editoriales de la entrega y **debe sustituirse por el SHA
del commit final** después de integrarlas. La reproducción no debe depender de la posición móvil de
`main`. Una vez congelada la entrega, el marcador `<SHA_FINAL>` de los siguientes comandos debe
reemplazarse por ese identificador completo. Esta es la única actualización documental que no puede
cerrarse antes de aceptar las correcciones y crear el commit que las contenga:

```bash
git clone https://github.com/jesusferron/tfm-brain-tumor-segmentation.git
cd tfm-brain-tumor-segmentation
git checkout <SHA_FINAL>
test "$(git rev-parse HEAD)" = "<SHA_FINAL>"
```

## A.2. Entorno

Las dependencias del *pipeline* MONAI se recogen en `requirements/protocol.txt` y las de nnU-Net en
`requirements/nnunet.txt`. El 23 de julio de 2026, el entorno local disponible durante la revisión
reportó Python 3.13.2, PyTorch 2.12.0 y MONAI 1.5.2; nnU-Net sí está fijado como
`nnunetv2==2.7.0`. Los resúmenes de las ejecuciones finales no guardaron una instantánea de paquetes
y `requirements/protocol.txt` no fija versiones, por lo que las tres primeras cifras documentan el
entorno reconstruido, no demuestran la versión efectiva de cada ejecución local o A100. Esta
carencia impide una reconstrucción binaria exacta y debe conservarse como límite de
reproducibilidad.

Una instalación local básica se prepara mediante:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements/protocol.txt
.venv/bin/python -m pip install -r requirements/nnunet.txt
```

Las rutas de los datos se configuran en `configs/dataset/brats_gli_2024.yaml` y deben adaptarse al
sistema donde se ejecute el proyecto. Las configuraciones de entrenamiento distinguen los entornos
MPS y CUDA; no debe asumirse que los tiempos obtenidos en ambos son directamente comparables.

## A.3. Control de calidad y particiones

Desde la raíz del repositorio, el inventario y control de calidad se ejecutan con:

```bash
.venv/bin/python -m tfm_brats.cli qc \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --output-csv outputs/qc/brats_gli_2024_qc.csv \
  --output-json outputs/qc/brats_gli_2024_qc_summary.json \
  --fail-on-problems
```

Las particiones versionadas se regeneran mediante:

```bash
.venv/bin/python -m tfm_brats.cli splits \
  --qc-csv outputs/qc/brats_gli_2024_qc.csv \
  --output-dir outputs/splits/brats_gli_2024_seed20260526 \
  --seed 20260526 \
  --ratios 70/15/15
```

La separación se realizó a nivel de estudio. Debido al carácter longitudinal de BraTS-GLI 2024,
no constituye una separación independiente por sujeto.

## A.4. Entrenamiento, inferencia y evaluación MONAI

El siguiente comando reproduce la estructura de una ejecución final de la Residual U-Net con
concatenación. Para las demás variantes se sustituyen la configuración del modelo, el directorio de
salida y la semilla.

```bash
.venv/bin/python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/residual_unet_3d.yaml \
  --training-config configs/training/mac_m4_pro_128_final.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/final_concat_seed20260526 \
  --max-steps 15000 \
  --seed 20260526
```

Las configuraciones principales de la ablación son:

- `configs/model/residual_unet_3d.yaml`;
- `configs/model/residual_unet_3d_global_weighted.yaml`;
- `configs/model/residual_unet_3d_adaptive_gating.yaml`;
- `configs/model/residual_unet_3d_adaptive_gating_meanstd.yaml`.

Attention U-Net y Swin-UNETR emplean, respectivamente,
`configs/model/attention_unet_3d.yaml` y `configs/model/swin_unetr.yaml`, junto con
`configs/training/colab_a100_final.yaml` en las ejecuciones A100.

La inferencia y la evaluación de una ejecución se realizan con:

```bash
.venv/bin/python -m tfm_brats.cli predict \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/residual_unet_3d.yaml \
  --training-config configs/training/mac_m4_pro_128_final.yaml \
  --split-csv outputs/splits/brats_gli_2024_seed20260526/test.csv \
  --checkpoint outputs/train/final_concat_seed20260526/checkpoints/best.pt \
  --output-dir outputs/predictions/final_concat_seed20260526_test

.venv/bin/python -m tfm_brats.cli evaluate \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --split-csv outputs/splits/brats_gli_2024_seed20260526/test.csv \
  --predictions-dir outputs/predictions/final_concat_seed20260526_test \
  --output-csv outputs/evaluation/final_concat_seed20260526_test_metrics.csv \
  --output-json outputs/evaluation/final_concat_seed20260526_test_metrics_summary.json
```

## A.5. Ruta externa nnU-Net

nnU-Net se ejecuta como un *pipeline* externo, con planificación, preprocesamiento, aumentos y
entrenamiento propios. Para reproducir la ejecución final deben definirse primero sus tres directorios
de trabajo en disco local:

```bash
export nnUNet_raw=/content/nnUNet_raw
export nnUNet_preprocessed=/content/nnUNet_preprocessed
export nnUNet_results=/content/nnUNet_results
```

La conversión parte de las particiones versionadas. En la reproducción final, `imagesTr` y
`labelsTr` proceden de `train.csv`, mientras que `imagesTs` se genera directamente a partir de
`test.csv`:

```bash
.venv/bin/python scripts/nnunet/prepare_brats_gli_nnunet_full.py \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --train-split train.csv \
  --test-split test.csv \
  --nnunet-raw "$nnUNet_raw" \
  --dataset-id 725 \
  --dataset-name BraTSGLI2024

.venv/bin/nnUNetv2_plan_and_preprocess -d 725 --verify_dataset_integrity
.venv/bin/nnUNetv2_train 725 3d_fullres 0 -tr nnUNetTrainer_250epochs

.venv/bin/nnUNetv2_predict \
  -i "$nnUNet_raw/Dataset725_BraTSGLI2024/imagesTs" \
  -o /content/nnunet_pred_test \
  -d 725 -c 3d_fullres -f 0 \
  -tr nnUNetTrainer_250epochs \
  -chk checkpoint_best.pth

.venv/bin/python -m tfm_brats.cli evaluate \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --split-csv outputs/splits/brats_gli_2024_seed20260526/test.csv \
  --predictions-dir /content/nnunet_pred_test \
  --output-csv outputs/evaluation/nnunet_3dfullres_test_metrics.csv \
  --output-json outputs/evaluation/nnunet_3dfullres_test_metrics_summary.json
```

La guía operativa completa, incluida la comprobación preliminar sobre validación, se conserva en
`docs/nnunet-baseline.md`. La referencia reportada en la memoria corresponde únicamente al *fold* 0
y no proporciona variabilidad entre repeticiones. Los comandos anteriores llegan hasta la evaluación
común sobre los 243 estudios de test de la que procede el Dice medio 0,829.

## A.6. Verificación y figuras

Durante esta revisión se comprobó que las rutas relativas citadas en este apéndice existen en el
árbol de trabajo, `compileall` terminó sin errores y las 17 pruebas unitarias finalizaron
correctamente. Las rutas bajo `/content` son destinos del entorno Colab y no se comprobaron como
rutas locales. Estas verificaciones se ejecutaron en el entorno existente, no desde un clon limpio
del commit final, porque ese commit todavía no estaba congelado. Por tanto, los siguientes comandos
constituyen también la lista que debe repetirse después de sustituir `<SHA_FINAL>` en el Apartado
A.1:

```bash
.venv/bin/python -m compileall -q tfm_brats scripts tests
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/draw_diagrams.py
.venv/bin/python scripts/make_figures.py
```

`scripts/make_figures.py` requiere que las predicciones NIfTI utilizadas por las comparaciones
cualitativas estén disponibles en las rutas esperadas bajo `outputs/predictions/`. Esas predicciones
no están versionadas, de modo que las figuras no pueden regenerarse a partir de un clon limpio sin
recuperar antes los artefactos externos.

## A.7. Artefactos y política de versionado

La Tabla A.1 diferencia los artefactos necesarios para auditar el trabajo de aquellos que no pueden
distribuirse en el repositorio por tamaño o por las condiciones de acceso a los datos.

**Tabla A.1.** Artefactos del proyecto y política de versionado.

| Tipo | Contenido | Política |
| :-- | :-- | :-- |
| Código y pruebas | `tfm_brats/`, `scripts/`, `tests/` | Versionado |
| Configuraciones | `configs/dataset/`, `configs/model/`, `configs/training/`, `configs/nnunet/` | Versionado |
| Trazabilidad de datos | Resúmenes de QC y particiones bajo `outputs/qc/` y `outputs/splits/` | Versionado |
| Resultados ligeros | Agregados CSV/JSON y métricas por estudio conservadas bajo `outputs/evaluation/` | Versionado parcial; faltan los CSV por estudio de Attention U-Net y Swin-UNETR |
| Memoria y figuras | `docs/memoria/` y scripts generadores | Versionado |
| Datos médicos | Volúmenes NIfTI originales y derivados | No versionado |
| Salidas pesadas | Predicciones NIfTI, *checkpoints*, directorios `outputs/train/` y artefactos internos de nnU-Net | No versionado |
| Registros externos | Artefactos completos de las ejecuciones A100 y nnU-Net conservados fuera del repositorio | No versionado; su ubicación depende del entorno del autor |

El repositorio conserva el código, las configuraciones y los agregados principales, pero no
constituye por sí solo un paquete autocontenido de reproducción: los datos protegidos, las salidas
pesadas, parte de los registros y seis CSV por estudio deben recuperarse o conservarse por separado.

El fichero `.gitignore` excluye explícitamente los NIfTI, *checkpoints*, predicciones, entornos
virtuales y directorios generados por nnU-Net.

## A.8. Condiciones de acceso a los datos y límites de reproducción

BraTS-GLI 2024 se obtuvo a través del [proyecto oficial del reto en
Synapse](https://www.synapse.org/Synapse:syn53708249) y está sujeto a sus condiciones de acceso y uso.
El repositorio no redistribuye las imágenes, máscaras ni derivados que permitan reconstruir los
datos originales. Cada persona que reproduzca los experimentos debe solicitar su propio acceso,
aceptar las condiciones vigentes en la plataforma y respetar los requisitos de uso y citación del
conjunto; no debe inferirse una licencia general de los datos a partir de las licencias del software.

En el momento de redactar este apéndice el repositorio no contiene un fichero `LICENSE` para el
código. Antes de hacerlo público debe definirse explícitamente la licencia del software; la licencia
del código no modifica ni sustituye la licencia de los datos.

La reproducción exacta también está limitada por el coste de entrenar modelos 3D, la posible
variabilidad no determinista de algunas operaciones CUDA/MPS, la ausencia de los *checkpoints*
pesados en Git y la instrumentación incompleta y heterogénea de tiempo y memoria entre entornos.
