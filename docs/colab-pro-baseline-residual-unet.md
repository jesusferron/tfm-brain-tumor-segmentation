# Ejecucion Del Baseline En Colab Pro

Este documento describe como ejecutar el primer baseline real del TFM en Colab Pro: `residual_unet_3d` sobre BraTS-GLI 2024, y como reutilizar exactamente el mismo flujo para las demas arquitecturas del catalogo (`attention_unet_3d`, `swin_unetr`) y para las ablaciones de fusion (`residual_unet_3d_global_weighted`, `residual_unet_3d_adaptive_gating`).

## Objetivo

Entrenar el baseline `residual_unet_3d`, generar predicciones sobre `val`, calcular metricas `Dice` y `HD95`, y traer de vuelta los artefactos minimos para analizar resultados. Una vez validado el baseline, las mismas celdas sirven para entrenar el resto de configs cambiando `--model-config` y `--output-dir`.

No uses el split `test` todavia. Primero validamos el baseline sobre `val`.

## Artefactos Que Debes Devolver

Minimo necesario:

```text
outputs/train/residual_unet_3d/train_summary.json
outputs/train/residual_unet_3d/train_log.csv
outputs/evaluation/residual_unet_3d_val_metrics_summary.json
```

Tambien dime:

- GPU que aparece en `nvidia-smi`.
- Si el entrenamiento termino o se corto.
- Ultima linea relevante de `outputs/train/residual_unet_3d/train_log.csv`.
- Si se genero `outputs/train/residual_unet_3d/checkpoints/best.pt`.

Opcional, pero util:

```text
outputs/train/residual_unet_3d/checkpoints/best.pt
outputs/evaluation/residual_unet_3d_val_metrics.csv
```

No hace falta devolver todas las predicciones NIfTI salvo que necesitemos inspeccionar casos concretos:

```text
outputs/predictions/residual_unet_3d_val/
```

## 1. Preparar Colab

Abre un notebook nuevo en Colab Pro.

Ve a:

```text
Runtime > Change runtime type
```

Selecciona:

- Hardware accelerator: `GPU`
- Runtime shape: el mas alto disponible, si aparece esa opcion.

Comprueba la GPU:

```python
!nvidia-smi
```

Si aparece una GPU NVIDIA, puedes continuar.

## 2. Montar Google Drive

Colab no ve tu disco externo local. El dataset debe estar accesible desde Google Drive.

Monta Drive:

```python
from google.colab import drive
drive.mount('/content/drive')
```

La estructura esperada del dataset es:

```text
/content/drive/MyDrive/TFM-datasets/
  training_data1_v2/
  training_data_additional/
  validation_data/
```

Y dentro de cada caso supervisado:

```text
BraTS-GLI-xxxxx-xxx/
  BraTS-GLI-xxxxx-xxx-t1n.nii.gz
  BraTS-GLI-xxxxx-xxx-t1c.nii.gz
  BraTS-GLI-xxxxx-xxx-t2w.nii.gz
  BraTS-GLI-xxxxx-xxx-t2f.nii.gz
  BraTS-GLI-xxxxx-xxx-seg.nii.gz
```

## 3. Preparar El Repo

Si el repo esta en GitHub y es publico:

```bash
%cd /content
!git clone TU_URL_DEL_REPO tfm-brain-tumor-segmentation
%cd /content/tfm-brain-tumor-segmentation
```

Si el repo es privado, GitHub no acepta tu contrasena normal por HTTPS. Usa un Personal Access Token de GitHub.

Recomendado:

1. En GitHub, crea un token en `Settings > Developer settings > Personal access tokens`.
2. Mejor si es un token fine-grained.
3. Dale acceso solo a este repo.
4. Permiso minimo para clonar: `Contents: Read-only`.
5. Ponle expiracion corta.

En Colab, usa Secrets para no escribir el token dentro del comando `git clone`.

Primero crea un secret en Colab:

```text
Secrets > Add new secret
Name: GITHUB_TOKEN
Value: tu_token_de_github
```

Primera celda:

```python
import os
from google.colab import userdata

os.environ["GITHUB_TOKEN"] = userdata.get("GITHUB_TOKEN")
```

Segunda celda:

```python
from pathlib import Path

Path("/content/git_askpass.py").write_text(
    """#!/usr/bin/env python3
import os
import sys

prompt = sys.argv[1].lower()
if "username" in prompt:
    print("x-access-token")
else:
    print(os.environ["GITHUB_TOKEN"])
""",
    encoding="utf-8",
)
```

Tercera celda:

```bash
!chmod 700 /content/git_askpass.py
%env GIT_ASKPASS=/content/git_askpass.py
%env GIT_TERMINAL_PROMPT=0
%cd /content
!git clone https://github.com/OWNER/tfm-brain-tumor-segmentation.git
%cd /content/tfm-brain-tumor-segmentation
```

Cambia `OWNER` por tu usuario u organizacion de GitHub.

Si no esta en GitHub, sube un `.zip` del repo a Drive y descomprimelo en `/content`.

Comprueba que estas en la raiz del repo:

```bash
!pwd
!ls
!ls requirements/protocol.txt
```

Deberias ver carpetas como:

```text
configs
docs
outputs
requirements
scripts
tfm_brats
```

Y el ultimo comando debe mostrar:

```text
requirements/protocol.txt
```

Si `!ls requirements/protocol.txt` falla, no estas en la raiz del repo o el repo no se ha clonado/subido completo. Vuelve a la carpeta correcta antes de seguir:

```bash
%cd /content/tfm-brain-tumor-segmentation
!pwd
!ls requirements/protocol.txt
```

Si no recuerdas donde quedo el repo en Colab, localiza el archivo y entra en la carpeta que contiene `requirements`:

```bash
!find /content -maxdepth 4 -path "*/requirements/protocol.txt" -print
```

## 4. Instalar Dependencias

Desde la raiz del repo:

```bash
%cd /content/tfm-brain-tumor-segmentation
!ls requirements/protocol.txt
!pip install -r requirements/protocol.txt
```

Comprueba PyTorch, MONAI y CUDA:

```bash
!python -c "import torch, monai, nibabel; print('torch', torch.__version__); print('cuda', torch.cuda.is_available())"
```

Debe salir:

```text
cuda True
```

## 5. Ajustar Ruta Del Dataset

El archivo del repo trae por defecto la ruta local del Mac. En Colab debes cambiarla a la ruta de Drive antes de ejecutar QC.

Primero comprueba que Drive esta montado y que existe la carpeta padre del dataset:

```bash
!ls "/content/drive/MyDrive/TFM-datasets"
```

Debe mostrar, como minimo:

```text
training_data1_v2
training_data_additional
validation_data
```

Si tu carpeta se llama distinto, localiza `training_data1_v2`:

```bash
!find "/content/drive/MyDrive" -maxdepth 4 -type d -name "training_data1_v2" -print
```

La ruta que debes usar como `dataset_root` es la carpeta padre de `training_data1_v2`. Por ejemplo, si el `find` devuelve:

```text
/content/drive/MyDrive/TFM-datasets/training_data1_v2
```

entonces `dataset_root` debe ser:

```yaml
dataset_root: "/content/drive/MyDrive/TFM-datasets"
```

Actualiza el YAML desde Colab:

```python
from pathlib import Path
import yaml

dataset_root = "/content/drive/MyDrive/TFM-datasets"

config_path = Path("configs/dataset/brats_gli_2024.yaml")
config = yaml.safe_load(config_path.read_text())
config["dataset_root"] = dataset_root
config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
print(config_path.read_text())
```

Si el `find` anterior mostro otra carpeta padre, cambia el valor de `dataset_root` en esa celda.

Comprueba que Colab ve los dos roots supervisados:

```bash
!python - <<'PY'
import yaml
from pathlib import Path

config = yaml.safe_load(Path("configs/dataset/brats_gli_2024.yaml").read_text())
root = Path(config["dataset_root"])
print("dataset_root:", root)
for name in config["training_roots"]:
    path = root / name
    print(path, "OK" if path.is_dir() else "MISSING")
PY
```

## 6. Verificacion Rapida Del Dataset

Ejecuta un QC pequeno antes de entrenar:

```bash
!python -m tfm_brats.cli qc \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --output-csv outputs/qc/colab_qc_sample.csv \
  --output-json outputs/qc/colab_qc_sample_summary.json \
  --max-cases 3 \
  --skip-intensity-stats \
  --progress-every 1 \
  --fail-on-problems
```

Debe terminar con algo parecido a:

```text
QC cases: 3
QC status counts: {'ok': 3}
```

Si falla aqui, no lances el entrenamiento.

## 7. Smoke Test En GPU

Antes del entrenamiento largo, ejecuta 2 pasos para validar carga, transforms, forward, loss, backward, validacion y checkpoint:

```bash
!python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/residual_unet_3d.yaml \
  --training-config configs/training/local_smoke.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/residual_unet_3d_colab_smoke \
  --max-steps 2 \
  --max-train-cases 2 \
  --max-val-cases 1 \
  --device cuda
```

Debe generar:

```text
outputs/train/residual_unet_3d_colab_smoke/train_summary.json
outputs/train/residual_unet_3d_colab_smoke/train_log.csv
outputs/train/residual_unet_3d_colab_smoke/checkpoints/best.pt
outputs/train/residual_unet_3d_colab_smoke/checkpoints/last.pt
```

## 7b. Catalogo De Modelos Disponibles

La pipeline propia (`tfm_brats.monai_pipeline.build_model`) selecciona la arquitectura segun el campo `model.architecture` del YAML. Todos los configs comparten el mismo `dataset-config`, `training-config` y `split-dir`. Solo cambia `--model-config` y `--output-dir`.

| Config | Arquitectura | Parametros | Notas |
| --- | --- | --- | --- |
| `configs/model/residual_unet_3d.yaml` | `residual_unet_3d` (fusion `concat`) | ~1.2M | Baseline propio. |
| `configs/model/residual_unet_3d_global_weighted.yaml` | `residual_unet_3d` (fusion `global_weighted`) | ~1.2M | Ablacion de fusion ponderada por modalidad. |
| `configs/model/residual_unet_3d_adaptive_gating.yaml` | `residual_unet_3d` (fusion `adaptive_gating`) | ~1.2M | Ablacion de fusion adaptativa (contribucion principal). |
| `configs/model/attention_unet_3d.yaml` | `attention_unet` | ~5.9M | Variante intermedia con attention gates en skip connections. |
| `configs/model/swin_unetr.yaml` | `swin_unetr` | ~62M | Transformer-UNet alineado con el titulo del TFM. Mas pesado en memoria. |

Todos producen logits de forma `(B, 3, D, H, W)` para las tres regiones BraTS (`ET`, `TC`, `WT`). El protocolo de entrenamiento, perdida (`DiceCELoss`), validacion sliding window y checkpointing es identico entre arquitecturas.

Recomendaciones por arquitectura:

- `attention_unet_3d`: cabe con la `colab_pro.yaml` actual (`batch_size=2`, `patch_size=128`) sin ajustes.
- `swin_unetr`: 62M parametros. Si la A100 reporta OOM o memoria muy ajustada, activar `use_checkpoint: true` en `configs/model/swin_unetr.yaml`; si sigue sin caber, reducir `batch_size` a 1 o `patch_size` a `[96, 96, 96]` en el training config.
- Ablaciones de fusion: mismo coste que el baseline, comparables en tiempo por paso.

## 7c. Optimizacion De I/O (recomendado antes del entrenamiento real)

En corridas anteriores el A100 estaba infrautilizado: el `compute` por paso era ~0.5 s pero `data_wait` presentaba picos de 3-11 s cada pocos pasos. El cuello no era la GPU sino la lectura de NIfTI desde Google Drive (ver [vitacora 2026-06-25](vitacora/README.md)).

**El arreglo es copiar el dataset al disco local del runtime.** Drive es lento por acceso aleatorio; el disco local (`/content`) es SSD y las lecturas son rapidas. En las corridas locales del M4 (dataset en SSD, sin cache) `data_wait_seconds` ya se mantenia en ~0 tras calentar los workers, asi que copiar a `/content` basta para eliminar el cuello. Hazlo una vez por sesion:

```bash
!mkdir -p /content/TFM-datasets
!rsync -ah --info=progress2 "/content/drive/MyDrive/TFM-datasets/training_data1_v2" /content/TFM-datasets/
!rsync -ah --info=progress2 "/content/drive/MyDrive/TFM-datasets/training_data_additional" /content/TFM-datasets/
```

Y apunta `dataset_root` al disco local (misma celda del paso 5):

```python
dataset_root = "/content/TFM-datasets"
```

La copia ocupa unos ~30 GB, holgada en el disco de Colab (~235 GB).

**Por que NO se usa cache de preprocesado (`cache_mode`) en cloud.** MONAI puede cachear el prefijo determinista de las transforms, pero cachear el split completo (imagen 4 canales float32 a resolucion completa, ~150 MB por caso x ~1378 casos) ocupa **~200 GB** y agota el disco de Colab (fallo real observado: sin espacio hacia el paso ~1090). Por eso las configs de cloud usan `cache_mode: none`: con el dataset ya en disco local, la cache no aporta y solo consume disco. La cache seria util si el dataset viviese en almacenamiento lento y hubiese disco de sobra, que no es el caso aqui.

Tras la primera epoca, mira `train_log.csv`: con el dataset en local, `data_wait_seconds` debe estar cerca de 0 y `steps_per_second` alto. Ese es el indicador de que el I/O no es el limitante.

## 8. Entrenamiento Real

Si el smoke test funciona, lanza un primer entrenamiento acotado. Este perfil usa `amp`, mayor batch efectivo y validacion menos frecuente para aprovechar mejor A100. Aplica antes la optimizacion de I/O de la seccion 7c.

```bash
!python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/residual_unet_3d.yaml \
  --training-config configs/training/colab_pro.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/residual_unet_3d \
  --max-steps 3000 \
  --device cuda
```

Esto puede tardar horas, pero debe imprimir lineas `train_step` con batch, pasos restantes, `case_id`, patches, tiempo de espera de datos, tiempo de computo, velocidad, memoria GPU y validaciones. Si `data_wait` domina claramente a `compute`, normalmente el cuello de botella esta en lectura desde Google Drive o transformaciones CPU.

Durante el entrenamiento se iran actualizando:

```text
outputs/train/residual_unet_3d/train_log.csv
outputs/train/residual_unet_3d/train_summary.json
outputs/train/residual_unet_3d/checkpoints/last.pt
outputs/train/residual_unet_3d/checkpoints/best.pt
```

Puedes monitorizar desde otra celda:

```bash
!tail -n 20 outputs/train/residual_unet_3d/train_log.csv
```

Si `data_wait` sigue dominando a `compute`, es que no se aplico (o no surtio efecto) la optimizacion de I/O de la seccion 7c: confirma que copiaste el dataset a `/content/TFM-datasets` y que `dataset_root` apunta ahi (no a Drive). La primera epoca todavia paga la descompresion inicial de cada NIfTI; la lectura se estabiliza a partir de la segunda.

## 8b. Perfil L4 Y Swin-UNETR (Transformer-UNet)

Segun la decision de hardware de la vitacora (2026-06-25), **L4 (24 GB) es la GPU de desarrollo/optimizacion** y A100 se reserva para las corridas finales largas. Para trabajar en L4 se usa el perfil `configs/training/colab_l4.yaml`, que trae `cache_mode: none` y `batch_size: 1` para que quepa el modelo mas pesado.

En Runtime > Change runtime type, elige `L4` si esta disponible. Aplica antes la optimizacion de I/O de la seccion 7c (copia del dataset a `/content`).

Swin-UNETR es el Transformer-UNet que da nombre al TFM (62M parametros). En L4 (24 GB) hay que activar gradient checkpointing, ya incluido en `configs/model/swin_unetr_l4.yaml` (`use_checkpoint: true`), que intercambia computo por memoria para que quepa a patch 128.

Smoke test de Swin en L4 (2 pasos) antes de la corrida larga:

```bash
!python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/swin_unetr_l4.yaml \
  --training-config configs/training/colab_l4.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/swin_unetr_l4_smoke \
  --max-steps 2 --max-train-cases 2 --max-val-cases 1 \
  --device cuda
```

Corrida de Swin-UNETR en L4:

```bash
!python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/swin_unetr_l4.yaml \
  --training-config configs/training/colab_l4.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/swin_unetr_l4 \
  --max-steps 5000 \
  --device cuda
```

Vigila en `train_log.csv` la columna `gpu_memory_gb` (pico) y `step_seconds`. Escalado si aparece OOM aun con checkpointing: reducir `patch_size` a `[96, 96, 96]` en `colab_l4.yaml`, o pasar a A100 con `configs/model/swin_unetr.yaml` (sin checkpointing, mas rapido) y `configs/training/colab_pro.yaml`. Al terminar, ejecuta `predict` + `evaluate` sobre `val` como en las secciones 10 y 11, con `--model-config configs/model/swin_unetr_l4.yaml` y `--output-dir outputs/train/swin_unetr_l4`.

## 9. Revisar Entrenamiento

Cuando termine, muestra el resumen:

```bash
!cat outputs/train/residual_unet_3d/train_summary.json
```

Muestra las ultimas lineas del log:

```bash
!tail -n 20 outputs/train/residual_unet_3d/train_log.csv
```

Comprueba checkpoints:

```bash
!ls -lh outputs/train/residual_unet_3d/checkpoints
```

Debe existir:

```text
best.pt
last.pt
```

## 10. Generar Predicciones En Validacion

Usa `best.pt` para predecir el split `val`:

```bash
!python -m tfm_brats.cli predict \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/residual_unet_3d.yaml \
  --training-config configs/training/colab_pro.yaml \
  --split-csv outputs/splits/brats_gli_2024_seed20260526/val.csv \
  --checkpoint outputs/train/residual_unet_3d/checkpoints/best.pt \
  --output-dir outputs/predictions/residual_unet_3d_val \
  --device cuda
```

Esto genera un `.nii.gz` por caso de validacion y un manifiesto:

```text
outputs/predictions/residual_unet_3d_val/prediction_summary.json
outputs/predictions/residual_unet_3d_val/predictions.csv
```

## 11. Evaluar Validacion

Calcula Dice y HD95:

```bash
!python -m tfm_brats.cli evaluate \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --split-csv outputs/splits/brats_gli_2024_seed20260526/val.csv \
  --predictions-dir outputs/predictions/residual_unet_3d_val \
  --output-csv outputs/evaluation/residual_unet_3d_val_metrics.csv \
  --output-json outputs/evaluation/residual_unet_3d_val_metrics_summary.json
```

Muestra el resumen:

```bash
!cat outputs/evaluation/residual_unet_3d_val_metrics_summary.json
```

## 12. Descargar Artefactos

Descarga como minimo:

```text
outputs/train/residual_unet_3d/train_summary.json
outputs/train/residual_unet_3d/train_log.csv
outputs/evaluation/residual_unet_3d_val_metrics_summary.json
```

Tambien es recomendable descargar:

```text
outputs/evaluation/residual_unet_3d_val_metrics.csv
outputs/train/residual_unet_3d/checkpoints/best.pt
```

Puedes comprimirlos:

```bash
!zip -r residual_unet_3d_results.zip \
  outputs/train/residual_unet_3d/train_summary.json \
  outputs/train/residual_unet_3d/train_log.csv \
  outputs/evaluation/residual_unet_3d_val_metrics.csv \
  outputs/evaluation/residual_unet_3d_val_metrics_summary.json
```

Si quieres incluir el checkpoint:

```bash
!zip -r residual_unet_3d_results_with_checkpoint.zip \
  outputs/train/residual_unet_3d/train_summary.json \
  outputs/train/residual_unet_3d/train_log.csv \
  outputs/train/residual_unet_3d/checkpoints/best.pt \
  outputs/evaluation/residual_unet_3d_val_metrics.csv \
  outputs/evaluation/residual_unet_3d_val_metrics_summary.json
```

## 12b. Repetir El Flujo Para Otras Arquitecturas

Cuando el baseline `residual_unet_3d` haya cerrado los pasos 7 a 11, puedes lanzar las demas arquitecturas reutilizando exactamente las mismas celdas. Solo cambian `--model-config` y `--output-dir`. El resto (dataset, training config, split, semilla, AMP, logging) se mantiene identico para que los experimentos sean comparables.

Ejecutalas de una en una, no en paralelo, y al terminar cada una repite las secciones 10 (predict sobre `val`) y 11 (evaluate) apuntando a su propio `--output-dir`, `--checkpoint` y rutas de evaluacion.

Attention U-Net 3D:

```bash
!python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/attention_unet_3d.yaml \
  --training-config configs/training/colab_pro.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/attention_unet_3d \
  --max-steps 3000 \
  --device cuda
```

Swin-UNETR (Transformer-UNet):

```bash
!python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/swin_unetr.yaml \
  --training-config configs/training/colab_pro.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/swin_unetr \
  --max-steps 3000 \
  --device cuda
```

Si Swin-UNETR da OOM, edita primero `configs/model/swin_unetr.yaml` y pon `use_checkpoint: true`. Si aun no cabe, baja `batch_size` en `configs/training/colab_pro.yaml` a 1 o usa `patch_size: [96, 96, 96]`.

Ablacion de fusion ponderada:

```bash
!python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/residual_unet_3d_global_weighted.yaml \
  --training-config configs/training/colab_pro.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/residual_unet_3d_global_weighted \
  --max-steps 3000 \
  --device cuda
```

Ablacion de fusion adaptativa (contribucion principal):

```bash
!python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/residual_unet_3d_adaptive_gating.yaml \
  --training-config configs/training/colab_pro.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/residual_unet_3d_adaptive_gating \
  --max-steps 3000 \
  --device cuda
```

Para cada arquitectura, una vez completado el entrenamiento, ejecuta `predict` y `evaluate` igual que en las secciones 10 y 11 pero sustituyendo el nombre. Por ejemplo, para Attention U-Net:

```bash
!python -m tfm_brats.cli predict \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/attention_unet_3d.yaml \
  --training-config configs/training/colab_pro.yaml \
  --split-csv outputs/splits/brats_gli_2024_seed20260526/val.csv \
  --checkpoint outputs/train/attention_unet_3d/checkpoints/best.pt \
  --output-dir outputs/predictions/attention_unet_3d_val \
  --device cuda

!python -m tfm_brats.cli evaluate \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --split-csv outputs/splits/brats_gli_2024_seed20260526/val.csv \
  --predictions-dir outputs/predictions/attention_unet_3d_val \
  --output-csv outputs/evaluation/attention_unet_3d_val_metrics.csv \
  --output-json outputs/evaluation/attention_unet_3d_val_metrics_summary.json
```

Mismos artefactos minimos esperados por experimento:

```text
outputs/train/<nombre>/train_summary.json
outputs/train/<nombre>/train_log.csv
outputs/train/<nombre>/checkpoints/best.pt
outputs/evaluation/<nombre>_val_metrics_summary.json
```

## 13. Informacion Que Debes Mandarme

Cuando acabes el baseline, mandame:

```text
GPU:
Entrenamiento termino o se corto:
Existe best.pt: si/no
Ultima linea relevante de train_log.csv:
Contenido de train_summary.json:
Contenido de residual_unet_3d_val_metrics_summary.json:
```

Si ademas has corrido otras arquitecturas, repite el mismo bloque por cada una sustituyendo el nombre. Por ejemplo, para Swin-UNETR mandame:

```text
GPU:
Entrenamiento termino o se corto:
Existe best.pt en outputs/train/swin_unetr/checkpoints: si/no
GPU memory pico (de train_log.csv columna gpu_memory_gb):
step_seconds tipico:
Ultima linea relevante de train_log.csv:
Contenido de train_summary.json:
Contenido de swin_unetr_val_metrics_summary.json:
Activaste use_checkpoint o ajustaste batch_size/patch_size: si/no y por que:
```

No ejecutes evaluacion sobre `test` todavia. El split `test` se reserva para una evaluacion final cuando el baseline y las ablaciones esten decididos.
