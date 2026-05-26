# Ejecucion Del Baseline En Colab Pro

Este documento describe como ejecutar el primer baseline real del TFM en Colab Pro: `residual_unet_3d` sobre BraTS-GLI 2024.

## Objetivo

Entrenar el baseline `residual_unet_3d`, generar predicciones sobre `val`, calcular metricas `Dice` y `HD95`, y traer de vuelta los artefactos minimos para analizar resultados.

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

## 8. Entrenamiento Real

Si el smoke test funciona, lanza el entrenamiento real:

```bash
!python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/residual_unet_3d.yaml \
  --training-config configs/training/colab_pro.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/residual_unet_3d \
  --device cuda
```

Esto puede tardar horas.

Durante el entrenamiento se iran actualizando:

```text
outputs/train/residual_unet_3d/train_log.csv
outputs/train/residual_unet_3d/train_summary.json
outputs/train/residual_unet_3d/checkpoints/last.pt
outputs/train/residual_unet_3d/checkpoints/best.pt
```

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

## 13. Informacion Que Debes Mandarme

Cuando acabes, mandame:

```text
GPU:
Entrenamiento termino o se corto:
Existe best.pt: si/no
Ultima linea relevante de train_log.csv:
Contenido de train_summary.json:
Contenido de residual_unet_3d_val_metrics_summary.json:
```

No ejecutes evaluacion sobre `test` todavia. El split `test` se reserva para una evaluacion final cuando el baseline y las ablaciones esten decididos.
