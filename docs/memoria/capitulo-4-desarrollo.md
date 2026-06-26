# 4. Desarrollo

> Versión revisada y ampliada del Capítulo 4, contrastada con el código del repositorio
> (`tfm_brats/`, `configs/`). Lista para integrar en la memoria.
> Referencias de implementación citadas como `archivo.py:línea`.

## 4.1. Organización del Código y Flujo de Trabajo

El desarrollo se estructura como un paquete de Python (`tfm_brats/`) acompañado de un árbol de
configuraciones declarativas en YAML (`configs/`), de modo que cada experimento queda definido
por la combinación de tres ficheros de configuración (dataset, modelo y entrenamiento) sin
modificar el código. Los módulos principales son:

- `tfm_brats/brats.py` — convenciones del dataset BraTS-GLI: modalidades, etiquetas, regiones y
  descubrimiento de casos.
- `tfm_brats/splits.py` — generación reproducible de las particiones estratificadas.
- `tfm_brats/monai_pipeline.py` — núcleo del pipeline: transformaciones, *dataloaders*,
  construcción de modelos, bucle de entrenamiento, inferencia y *checkpointing*.
- `tfm_brats/metrics.py` — cálculo de Dice y HD95 por región.
- `tfm_brats/cli.py` — interfaz de línea de comandos que orquesta todo el flujo.

El flujo experimental completo se expone como **cinco subcomandos** de una CLI unificada
(`tfm_brats/cli.py`), que reflejan las fases del trabajo y garantizan su reproducibilidad:

| Subcomando | Función |
| :-- | :-- |
| `qc` | Control de calidad: verifica la integridad de los casos BraTS-GLI (estructura, modalidades, etiquetas) y genera estadísticas. |
| `splits` | Genera las particiones train/val/test versionadas y estratificadas, con su manifiesto de distribución. |
| `train` | Ejecuta el entrenamiento de un modelo a partir de las tres configuraciones; produce *checkpoints*, registro por pasos y resumen. |
| `predict` | Realiza inferencia por ventana deslizante sobre un split y exporta las predicciones en formato NIfTI. |
| `evaluate` | Calcula las métricas Dice y HD95 por región (ET/TC/WT) a partir de las predicciones. |

Esta separación en fases permite asegurar primero la integridad del dataset y la reproducibilidad
del protocolo (qc, splits) antes de invertir cómputo en el entrenamiento, y desacopla la
inferencia de la evaluación métrica para poder recalcular métricas sin repetir la inferencia.

## 4.2. Preprocesamiento (ETL) y Transformaciones MONAI

### 4.2.1. Descubrimiento de casos y origen de los datos

El dataset se referencia mediante una configuración declarativa
(`configs/dataset/brats_gli_2024.yaml`) que especifica la raíz de datos, los directorios de
origen (`training_data1_v2`, `training_data_additional`), las cuatro modalidades y el sufijo de
la máscara. El descubrimiento de casos (`tfm_brats/brats.py`) recorre los directorios de origen,
selecciona las carpetas con el prefijo `BraTS-GLI-` y construye, para cada caso, las rutas a sus
cuatro volúmenes y a su máscara siguiendo el patrón de nombres
`{caso}-{modalidad}.nii.gz` (p. ej. `BraTS-GLI-00000-t1n.nii.gz`).

La localización física de los datos depende del entorno (§3.1): en local residen en un disco
SSD externo, mientras que en Google Colab se acceden desde Google Drive. Dado que la lectura de
volúmenes NIfTI directamente desde Google Drive introduce un cuello de botella de E/S, en el
entorno Colab los datos se copian previamente al almacenamiento local de la sesión antes de
entrenar.

Las particiones generadas por el subcomando `splits` se materializan como ficheros CSV
(`train.csv`, `val.csv`, `test.csv`), que el pipeline consume para construir, por cada caso, un
diccionario con las rutas de imagen (lista de las cuatro modalidades) y de etiqueta
(`tfm_brats/monai_pipeline.py`). De este modo, el conjunto de casos de cada experimento queda
fijado por el split versionado y es trazable.

### 4.2.2. Transformaciones

El pipeline de extracción, transformación y carga (ETL) se construye con transformaciones
nativas de MONAI. Una parte se aplica de forma determinista a todas las particiones y otra
constituye el aumento de datos exclusivo de entrenamiento (detallado en §3.4):

- **Comunes:** `LoadImaged`, `EnsureChannelFirstd`, `BratsRegionsd` (transformación propia que
  genera los tres canales binarios ET/TC/WT a partir de la máscara), `NormalizeIntensityd`
  (`nonzero=True`, `channel_wise=True`) y `EnsureTyped`.
- **Aumento (solo entrenamiento):** `SpatialPadd`, `DivisiblePadd` (`k=16`),
  `RandCropByPosNegLabeld` (razón positivo/negativo 1:1) y `RandFlipd` (p=0,5 en los tres ejes).

### 4.2.3. Carga de datos

Los volúmenes se sirven mediante las clases `Dataset` y `DataLoader` de MONAI, junto con la
función de colación `list_data_collate` (`tfm_brats/monai_pipeline.py`). Actualmente se emplea
un `Dataset` simple **sin mecanismo de caché** (no se utilizan `CacheDataset`,
`PersistentDataset` ni `SmartCacheDataset`); esto simplifica la implementación a costa de
recalcular las transformaciones deterministas en cada época, y queda registrado como posible
optimización futura. El `DataLoader` admite configuración de número de procesos, *pin memory*,
*persistent workers* y *prefetch factor* según el entorno.

## 4.3. Construcción de Modelos: Factory y Arquitecturas

La instanciación de las redes se centraliza en una función *factory*, `build_model`
(`tfm_brats/monai_pipeline.py`), que recibe la configuración del modelo y despacha según el campo
`architecture`. Esto permite que las cinco arquitecturas se definan íntegramente por YAML
(`configs/model/`), compartiendo el mismo punto de entrada de entrenamiento. Todas reciben
**4 canales de entrada** y emiten **3 canales de salida**.

| Modelo | Clase MONAI | Hiperparámetros clave | Parámetros |
| :-- | :-- | :-- | :-: |
| `residual_unet_3d` (baseline) | `UNet` | channels (16, 32, 64, 128); strides (2, 2, 2); `num_res_units=2`; fusión `concat` | ~1,19 M |
| `residual_unet_3d_global_weighted` | `UNet` + `FusionUNet` | igual que baseline + fusión `global_weighted` | ~1,19 M (+4) |
| `residual_unet_3d_adaptive_gating` | `UNet` + `FusionUNet` | igual que baseline + fusión `adaptive_gating` (`fusion_hidden=8`) | ~1,19 M (+48) |
| `attention_unet_3d` | `AttentionUnet` | channels (16, 32, 64, 128, 256); strides (2, 2, 2, 2); kernel 3 | ~5,91 M |
| `swin_unetr` | `SwinUNETR` | `feature_size=48`; depths (2, 2, 2, 2); num_heads (3, 6, 12, 24) | ~62,19 M |

Las tres variantes residuales comparten exactamente la misma red U-Net 3D (mismo número de
parámetros base, ~1,19 M); solo difieren en el bloque de fusión antepuesto, cuyo coste en
parámetros es despreciable (4 en la ponderación global, 48 en la compuerta adaptativa). Este
diseño es el que permite atribuir cualquier diferencia de rendimiento al mecanismo de fusión y no
a la capacidad del modelo. El Swin-UNETR, por su elevado consumo de memoria, admite la activación
de *gradient checkpointing* (`use_checkpoint`) para reducir la huella de VRAM.

## 4.4. Mecanismos de Fusión Multimodal

La contribución central del trabajo es la sustitución de la fusión por concatenación estándar por
un bloque de fusión que pondera las modalidades **a nivel de entrada**, antes de que la U-Net las
procese. Esto se implementa mediante un envoltorio común, `FusionUNet`
(`tfm_brats/monai_pipeline.py`), que aplica el bloque de fusión y, a continuación, la red:

```python
class FusionUNet(nn.Module):
    def __init__(self, fusion, unet):
        super().__init__()
        self.fusion = fusion
        self.unet = unet

    def forward(self, x):
        return self.unet(self.fusion(x))
```

El flujo del tensor es, por tanto: entrada `(B, 4, 128, 128, 128)` → bloque de fusión (reescala
los 4 canales/modalidades) → U-Net 3D → salida `(B, 3, 128, 128, 128)` con los *logits* de ET,
TC y WT. El baseline emplea la fusión `concat`, equivalente a una identidad antes de la red
(la U-Net concatena implícitamente los canales en su primera convolución).

### 4.4.1. Ponderación global estática (`global_weighted`)

La variante de ablación aprende un peso escalar por modalidad, **independiente de la entrada**
(`tfm_brats/monai_pipeline.py`):

```python
class GlobalWeightedFusion(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.logits = nn.Parameter(torch.zeros(channels))

    def forward(self, x):
        weights = torch.softmax(self.logits, dim=0).view(1, -1, 1, 1, 1)
        return x * weights * x.shape[1]
```

Los pesos se obtienen aplicando *softmax* sobre cuatro parámetros aprendibles (uno por
modalidad), por lo que suman 1. La multiplicación final por el número de canales (`x.shape[1]`,
es decir 4) reescala los pesos para que su valor medio sea 1 en lugar de 1/4, preservando la
escala de activación de la entrada. Aporta únicamente **4 parámetros** y representa una
ponderación global y estática: una vez entrenada, todas las imágenes reciben la misma
combinación de modalidades.

### 4.4.2. Compuerta adaptativa (`adaptive_gating`)

La contribución principal hace que los pesos **dependan de cada muestra**
(`tfm_brats/monai_pipeline.py`):

```python
class AdaptiveGatingFusion(nn.Module):
    def __init__(self, channels, hidden=8):
        super().__init__()
        self.gate = nn.Sequential(
            nn.Linear(channels, hidden),
            nn.ReLU(inplace=True),
            nn.Linear(hidden, channels),
        )

    def forward(self, x):
        pooled = x.mean(dim=(2, 3, 4))
        weights = torch.softmax(self.gate(pooled), dim=1).view(x.shape[0], -1, 1, 1, 1)
        return x * weights * x.shape[1]
```

El bloque realiza un *global average pooling* espacial que resume cada modalidad en un escalar
(tensor `(B, 4)`), lo procesa mediante un perceptrón multicapa de dos capas (4 → 8 → 4, con
`fusion_hidden=8`) y normaliza la salida con *softmax* por muestra. El resultado es un conjunto
de pesos por modalidad **específico de cada volumen de entrada**, frente al peso fijo de la
variante global. Igual que antes, se reescala por el número de canales. Su coste es de solo
**48 parámetros** (4×8 + 8×4).

La diferencia conceptual entre ambas variantes es precisamente lo que el estudio de ablación
busca aislar: la `global_weighted` comprueba si basta con reponderar estáticamente las
modalidades, mientras que la `adaptive_gating` evalúa si la dependencia de la entrada
(dinamismo por muestra) justifica su complejidad adicional.

## 4.5. Entrenamiento, *Checkpointing* e Inferencia

El bucle de entrenamiento es propio (§3.1) y emplea la función de pérdida
`DiceCELoss(sigmoid=True, squared_pred=True)` y el optimizador AdamW con los hiperparámetros
descritos en §3.5. Durante el entrenamiento se ejecuta una validación periódica
(`validation_interval`) que calcula la métrica de selección **`mean_dice`**, definida como la
media del Dice de las tres regiones, (ET + TC + WT) / 3 (`tfm_brats/monai_pipeline.py`).

La política de *checkpointing* guarda dos artefactos por modelo
(`tfm_brats/monai_pipeline.py`):

- `last.pt` — estado más reciente, almacenado tras cada validación.
- `best.pt` — estado con el mejor `mean_dice` de validación observado hasta el momento; es el
  *checkpoint* que se usa después para `predict` y `evaluate`.

Cada *checkpoint* incluye, además del estado del modelo y del optimizador, las configuraciones
de modelo y entrenamiento y la traza de época/paso, de modo que es autocontenido y reproducible.

La inferencia (`predict`) reconstruye el modelo desde su configuración, carga el *checkpoint* y
aplica `sliding_window_inference` con los parámetros descritos en §3.6, exportando las
predicciones binarizadas (sigmoide + umbral 0,5) en formato NIfTI. La evaluación (`evaluate`)
consume esas predicciones y produce, por caso, las métricas Dice y HD95 por región, junto con un
resumen agregado.

## 4.6. Restricciones y Alcance Clínico

El sistema segmenta sub-regiones funcionalmente relevantes (ET, TC, WT) en resonancias
magnéticas multimodales de pacientes previamente confirmados con glioma. Es imperativo documentar
que la arquitectura **no discrimina la presencia o ausencia de tumor en cerebros sanos**, ni
diferencia los gliomas de otras patologías como meningiomas o metástasis, dada la ausencia de
estos datos en el entrenamiento y el alcance técnico del trabajo. Su utilidad se circunscribe,
por tanto, a la optimización de la segmentación intra-tumoral dentro del entorno controlado del
dataset BraTS-GLI 2024.
