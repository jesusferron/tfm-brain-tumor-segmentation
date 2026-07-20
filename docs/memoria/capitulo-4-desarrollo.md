# 4. Desarrollo

> Versión reorganizada por **fases**, en correspondencia con la metodología del Capítulo 3: cada
> sección desarrolla el detalle técnico de una fase. Numeración de tablas **consecutiva global**,
> continuando desde el Capítulo 3. Referencias de implementación citadas como `archivo.py`.

## 4.1. Familiarización y selección de herramientas (Fase 1)

La fase inicial fijó el alcance del trabajo y seleccionó las herramientas y arquitecturas. Como
marco de trabajo se eligió **MONAI**, biblioteca especializada en imagen médica construida sobre
PyTorch, por aportar componentes reutilizables y validados para este dominio (transformaciones,
*datasets*, redes y funciones de pérdida específicas de segmentación 3D). MONAI proporciona esos
componentes pero **no orquesta el bucle de entrenamiento**, por lo que el proyecto implementa un
bucle propio (detallado en §4.4.2); esta decisión, tomada en esta fase, otorga control explícito
sobre la precisión mixta, la validación por ventana deslizante y el registro de métricas.

Del estudio del estado del arte (Capítulo 2) se seleccionaron cinco arquitecturas que cubren una
progresión de capacidad y de familia: un **U-Net residual 3D** como *baseline* convolucional
propio, un **Attention U-Net 3D** como variante intermedia, el **Swin-UNETR** como arquitectura
Transformer-UNet que da nombre al trabajo, y **nnU-Net** como *baseline* fuerte de referencia. La
justificación comparativa de estas herramientas frente a otras alternativas se recoge en la tabla
comparativa de repositorios del Capítulo 2.

## 4.2. Análisis y preparación de los datos (Fase 2)

### 4.2.1. Conjunto de datos y descubrimiento de casos

El alcance experimental se limita al subconjunto **BraTS-GLI 2024**, evitando mezclar tareas
clínicas de otras colecciones BraTS. Cada caso aporta cuatro volúmenes MRI 3D en formato NIfTI
(una modalidad por canal) y, cuando está disponible, su máscara de segmentación. El dataset se
referencia mediante una configuración declarativa (`configs/dataset/brats_gli_2024.yaml`) que
especifica la raíz de datos, los dos directorios de origen (`training_data1_v2`,
`training_data_additional`), las cuatro modalidades y el sufijo de la máscara. El descubrimiento
de casos (`tfm_brats/brats.py`) recorre esos directorios, selecciona las carpetas con prefijo
`BraTS-GLI-` y construye, por caso, las rutas a sus cuatro volúmenes y a su máscara según el
patrón `{caso}-{modalidad}.nii.gz`.

### 4.2.2. Control de calidad

Antes de entrenar se ejecuta un control de calidad (subcomando `qc`, §4.3.2) que verifica la
integridad de cada caso: presencia de las cuatro modalidades y de la máscara, consistencia de
dimensiones y etiquetas válidas. Este paso materializa el principio metodológico de asegurar la
integridad de los datos antes de invertir cómputo.

### 4.2.3. Particiones estratificadas y reproducibles

La partición de los datos se realiza de forma **estratificada y reproducible**
(`tfm_brats/splits.py`). El conjunto total (1.621 casos) se divide en proporción **70 / 15 / 15**,
con **estratificación simultánea** por tres factores: origen del caso (directorio de procedencia),
presencia o ausencia de tumor con realce (ET) y volumen tumoral total discretizado en cuatro
cuantiles. Esto asegura distribuciones comparables de tamaño y dificultad entre particiones. Se
fija una **semilla** (`20260526`), de modo que la partición es determinista y se materializa en
disco (`outputs/splits/brats_gli_2024_seed20260526/`) junto con un manifiesto de distribución. La
Tabla 5 resume la distribución resultante.

**Tabla 5.** Distribución de las particiones del conjunto BraTS-GLI 2024.

| Partición | Casos | Proporción | Uso |
| :-- | :-: | :-: | :-- |
| Entrenamiento | 1.135 | 70 % | Ajuste de los parámetros del modelo |
| Validación | 243 | 15 % | Monitorización y selección de *checkpoint* |
| Test | 243 | 15 % | Métricas finales (reservado) |

El **conjunto de validación** se emplea durante el entrenamiento para monitorizar el rendimiento
y seleccionar el mejor *checkpoint*, mientras que el **conjunto de test, completamente reservado**,
se utiliza solo para el reporte de las métricas finales (Capítulo 5). Esta separación evita el
sesgo optimista de informar resultados sobre el mismo conjunto usado para supervisar la
convergencia.

## 4.3. Diseño e implementación del *pipeline* (Fase 3)

### 4.3.1. Entorno de cómputo

El procesamiento se llevó a cabo en dos entornos, resumidos en la Tabla 6. El entorno local se
empleó para el desarrollo del *pipeline* y para el entrenamiento de los modelos ligeros; el
entorno en la nube (Google Colab con acelerador NVIDIA A100) se reservó para el modelo más pesado
(Swin-UNETR) y las corridas finales.

**Tabla 6.** Entornos de cómputo empleados.

| Entorno | Dispositivo | Precisión mixta (AMP) | Uso principal |
| :-- | :-- | :-- | :-- |
| Local | Apple M4 Pro (backend MPS) | Desactivada | Desarrollo y modelos ligeros |
| Nube | NVIDIA A100 (CUDA) | Activada | Swin-UNETR y corridas finales |

La precisión mixta automática (AMP) se activa únicamente en CUDA; en el backend MPS de Apple se
mantiene desactivada por las limitaciones de soporte actuales. Cada resultado del Capítulo 5
indica el entorno y la configuración con que se obtuvo, para garantizar la trazabilidad.

### 4.3.2. Organización del código y flujo de trabajo

El desarrollo se estructura como un paquete de Python (`tfm_brats/`) acompañado de un árbol de
configuraciones declarativas en YAML (`configs/`), de modo que cada experimento queda definido por
la combinación de tres ficheros (dataset, modelo y entrenamiento) sin modificar el código. Los
módulos principales son `brats.py` (convenciones del dataset), `splits.py` (particiones),
`monai_pipeline.py` (núcleo: transformaciones, *dataloaders*, construcción de modelos, bucle de
entrenamiento, inferencia y *checkpointing*), `metrics.py` (Dice y HD95) y `cli.py` (interfaz de
línea de comandos).

El flujo experimental se expone como **cinco subcomandos** de una CLI unificada, que reflejan las
fases operativas del trabajo (Tabla 7). Esta separación permite asegurar primero la integridad del
dataset y del protocolo (`qc`, `splits`) antes de invertir cómputo, y desacopla la inferencia de la
evaluación métrica para recalcular métricas sin repetir la inferencia.

**Tabla 7.** Subcomandos de la interfaz de línea de comandos (`tfm_brats/cli.py`).

| Subcomando | Función |
| :-- | :-- |
| `qc` | Control de calidad: integridad de casos, modalidades y etiquetas; estadísticas. |
| `splits` | Genera las particiones train/val/test versionadas y estratificadas. |
| `train` | Entrena un modelo a partir de las tres configuraciones; produce *checkpoints* y registro. |
| `predict` | Inferencia por ventana deslizante sobre un *split*; exporta predicciones NIfTI. |
| `evaluate` | Calcula Dice y HD95 por región (ET/TC/WT) a partir de las predicciones. |

La Figura 1 representa este flujo de extremo a extremo, desde el conjunto de datos hasta las
métricas, y muestra cómo las configuraciones YAML parametrizan el entrenamiento y cómo el conjunto
de test permanece reservado hasta la evaluación final.

![Flujo del pipeline experimental.](figuras/fig_pipeline_flujo.png)

**Figura 1.** Flujo del pipeline experimental: del conjunto de datos BraTS-GLI 2024 a las métricas
por región, a través de control de calidad, particiones, entrenamiento, inferencia y evaluación.

### 4.3.3. Formulación del problema y regiones clínicas

El modelo recibe un tensor con **cuatro canales** (modalidades T1n, T1c, T2w y FLAIR —denominada
`T2f` en el dataset y el código—) y emite **tres canales de salida**, cada uno asociado a una
subregión anidada del tumor según la convención BraTS. El código procesa y reporta las regiones en
el orden **ET, TC, WT** (`tfm_brats/brats.py`), como recoge la Tabla 8.

**Tabla 8.** Regiones tumorales BraTS, canales de salida y etiquetas incluidas.

| Canal | Región | Etiquetas BraTS | Descripción |
| :-: | :-- | :-- | :-- |
| 0 | **ET** (*Enhancing Tumor*) | {3} | Porción que capta contraste activo |
| 1 | **TC** (*Tumor Core*) | {1, 3, 4} | Núcleo sólido: tejido con y sin realce, más necrosis |
| 2 | **WT** (*Whole Tumor*) | {1, 2, 3, 4} | Extensión completa, incluyendo edema peritumoral |

Las regiones son **estrictamente anidadas** (ET ⊂ TC ⊂ WT), propiedad que se preserva en la
generación de las máscaras y en la reconstrucción del mapa de etiquetas para la evaluación. El
problema se formula como **segmentación multietiqueta** (no clasificación multiclase excluyente),
ya que un vóxel puede pertenecer a varias regiones a la vez; en consecuencia las salidas se activan
con **sigmoide** y se binarizan con **umbral 0,5** de forma independiente por canal.

### 4.3.4. Preprocesamiento y aumento de datos

El *pipeline* de extracción, transformación y carga (ETL) se construye con transformaciones nativas
de MONAI (`monai_pipeline.py`). Una parte se aplica de forma **determinista a todas las
particiones** y otra constituye el **aumento de datos exclusivo de entrenamiento**:

- **Comunes (train/val/test):** `LoadImaged` (carga NIfTI), `EnsureChannelFirstd` (canales al
  frente), `BratsRegionsd` (transformación propia que genera los tres canales binarios ET/TC/WT a
  partir de la máscara), `NormalizeIntensityd` (`nonzero=True`, `channel_wise=True`, normalización
  por canal sobre vóxeles no nulos) y `EnsureTyped` (conversión a tensores).
- **Aumento (solo entrenamiento):** `SpatialPadd` (relleno hasta el tamaño de parche 128³),
  `DivisiblePadd` (`k=16`, requisito de las arquitecturas en U), `RandCropByPosNegLabeld` (recorte
  aleatorio con razón positivo/negativo 1:1, extrayendo dos muestras por caso para enfocar el
  muestreo en regiones tumorales) y `RandFlipd` (volteo aleatorio con probabilidad 0,5 en los tres
  ejes).

Los volúmenes se sirven mediante `Dataset` y `DataLoader` de MONAI con la colación
`list_data_collate`. La lectura de NIfTI directamente desde Google Drive introducía un cuello de
botella de E/S que infrautilizaba la GPU; se resolvió **copiando el dataset al disco local del
runtime** antes de entrenar (una alternativa basada en caché de preprocesado en disco resultó
inviable por el espacio que exige el *split* completo). El conjunto de validación y test no recibe
aumento: se procesa con las transformaciones deterministas y se infiere a resolución completa por
ventana deslizante (§4.5.1).

### 4.3.5. Arquitecturas y *factory* de modelos

La instanciación de las redes se centraliza en una función *factory*, `build_model`
(`monai_pipeline.py`), que despacha según el campo `architecture` de la configuración, de modo que
las cinco arquitecturas se definen íntegramente por YAML (`configs/model/`) compartiendo el mismo
punto de entrada. Todas reciben 4 canales de entrada y emiten 3 de salida (Tabla 9).

**Tabla 9.** Arquitecturas comparadas y sus parámetros.

| Modelo | Clase MONAI | Hiperparámetros clave | Parámetros |
| :-- | :-- | :-- | :-: |
| Residual U-Net 3D (*baseline*) | `UNet` | channels (16, 32, 64, 128); strides (2, 2, 2); `num_res_units=2`; fusión `concat` | ~1,19 M |
| + `global_weighted` | `UNet` + `FusionUNet` | *baseline* + fusión ponderada global | ~1,19 M (+4) |
| + `adaptive_gating` | `UNet` + `FusionUNet` | *baseline* + compuerta adaptativa (`fusion_hidden=8`) | ~1,19 M (+48) |
| Attention U-Net 3D | `AttentionUnet` | channels (16, 32, 64, 128, 256); strides (2, 2, 2, 2); kernel 3 | ~5,91 M |
| Swin-UNETR | `SwinUNETR` | `feature_size=48`; depths (2, 2, 2, 2); num_heads (3, 6, 12, 24) | ~62,19 M |

Las tres variantes residuales comparten exactamente la misma U-Net 3D (~1,19 M parámetros); solo
difieren en el bloque de fusión antepuesto, cuyo coste es despreciable (4 parámetros en la
ponderación global, 48 en la compuerta adaptativa). Este diseño es el que permite atribuir
cualquier diferencia de rendimiento al mecanismo de fusión y no a la capacidad del modelo. El
Swin-UNETR admite *gradient checkpointing* (`use_checkpoint`) para reducir la huella de VRAM.

### 4.3.6. Mecanismos de fusión multimodal

La contribución central del trabajo es sustituir la fusión por concatenación estándar por un
bloque que pondera las modalidades **a nivel de entrada**, antes de que la U-Net las procese,
mediante un envoltorio común `FusionUNet` (`monai_pipeline.py`) que aplica el bloque de fusión y a
continuación la red:

```python
class FusionUNet(nn.Module):
    def __init__(self, fusion, unet):
        super().__init__()
        self.fusion = fusion
        self.unet = unet

    def forward(self, x):
        return self.unet(self.fusion(x))
```

El *baseline* emplea la fusión `concat`, equivalente a una identidad antes de la red (la U-Net
concatena implícitamente los canales en su primera convolución). La Figura 2 resume la arquitectura
`FusionUNet` y el detalle interno de la compuerta adaptativa. Se estudian tres alternativas:

![Arquitectura de fusión multimodal FusionUNet y detalle de la compuerta adaptativa.](figuras/fig_arquitectura_fusion.png)

**Figura 2.** Arquitectura de fusión multimodal (`FusionUNet`): flujo entrada → bloque de fusión →
Residual U-Net 3D → salida (arriba) y detalle de la compuerta adaptativa (abajo), con las tres
variantes evaluadas.

**Ponderación global estática (`global_weighted`).** Aprende un peso escalar por modalidad,
**independiente de la entrada**, vía *softmax* sobre cuatro parámetros; reescala por el número de
canales para preservar la escala de activación. Una vez entrenada, todas las imágenes reciben la
misma combinación de modalidades (solo 4 parámetros).

**Compuerta adaptativa (`adaptive_gating`).** Hace que los pesos **dependan de cada muestra**: un
*global average pooling* espacial resume cada modalidad en un escalar, un perceptrón de dos capas
(4 → 8 → 4) lo procesa y un *softmax* por muestra produce los pesos (48 parámetros):

```python
class AdaptiveGatingFusion(nn.Module):
    def __init__(self, channels, hidden=8):
        super().__init__()
        self.gate = nn.Sequential(
            nn.Linear(channels, hidden), nn.ReLU(inplace=True), nn.Linear(hidden, channels),
        )

    def forward(self, x):
        pooled = x.mean(dim=(2, 3, 4))
        weights = torch.softmax(self.gate(pooled), dim=1).view(x.shape[0], -1, 1, 1, 1)
        return x * weights * x.shape[1]
```

**Variante con descriptor enriquecido (`adaptive_gating_meanstd`).** Al diagnosticar que la
compuerta anterior producía pesos casi idénticos entre casos (su señal de condicionamiento —la
media global de las modalidades normalizadas— es casi constante), se añadió una variante que
condiciona la compuerta con la **media y la desviación típica** por canal, buscando una señal
realmente dependiente de cada caso. El análisis de estas variantes constituye el estudio de
ablación (§4.4.4 y Capítulo 5).

La diferencia conceptual es precisamente lo que la ablación busca aislar: `global_weighted`
comprueba si basta con reponderar estáticamente las modalidades, mientras que las variantes de
`adaptive_gating` evalúan si la dependencia de la entrada justifica su complejidad adicional.

## 4.4. Experimentación (Fase 4)

### 4.4.1. Configuración de entrenamiento e hiperparámetros

Todos los modelos comparten la configuración de optimización de la Tabla 10, de manera que cualquier
diferencia en las métricas sea atribuible a la arquitectura y a su estrategia de fusión, y no a los
hiperparámetros. El presupuesto de entrenamiento (número de pasos) se fijó empíricamente mediante
una **sonda de convergencia**: una corrida larga del *baseline* mostró que la métrica de validación
alcanza su meseta en torno a los 12.000–15.000 pasos, por lo que se adoptaron **15.000 pasos** para
las corridas finales (una exploración preliminar previa se había realizado a 5.000 pasos, que
resultaron insuficientes para converger).

**Tabla 10.** Hiperparámetros del protocolo de entrenamiento final.

| Hiperparámetro | Valor |
| :-- | :-- |
| Optimizador | AdamW |
| Tasa de aprendizaje | 1 × 10⁻⁴ con planificador *cosine* y *warmup* (1.000 pasos) hasta el 1 % |
| *Weight decay* | 1 × 10⁻⁵ |
| Función de pérdida | `DiceCELoss(sigmoid=True, squared_pred=True)` |
| Tamaño de parche | 128 × 128 × 128 |
| *Batch size* | 1 (con 2 muestras por caso) |
| Pasos de entrenamiento | 15.000 (≈ 13 épocas) |
| Semillas | 3 (20260526, 20260527, 20260528) |

La función de pérdida **DiceCELoss** combina el coeficiente Dice (con `squared_pred=True`) y la
entropía cruzada, aplicando internamente la sigmoide a los *logits*. A diferencia de la exploración
preliminar (tasa constante), el protocolo final incorpora un **planificador *cosine* con
calentamiento**, que mejora la convergencia en el presupuesto fijado.

### 4.4.2. Bucle de entrenamiento y *checkpointing*

El bucle de entrenamiento es propio (`monai_pipeline.py`, `train_one_run`) y gestiona de forma
explícita la iteración por pasos, el cálculo de la pérdida, la retropropagación, el paso del
optimizador (con escalado de gradiente en AMP) y la validación periódica. Durante la validación se
calcula la métrica de selección **`mean_dice`**, media del Dice de las tres regiones, (ET + TC +
WT) / 3. La política de *checkpointing* guarda dos artefactos por modelo: `last.pt` (estado más
reciente) y `best.pt` (mejor `mean_dice` de validación observado), siendo este último el que se usa
para la inferencia. Cada *checkpoint* es autocontenido: incluye el estado del modelo y del
optimizador, las configuraciones y la traza de época/paso.

### 4.4.3. Diseño experimental y reproducibilidad

El protocolo aísla rigurosamente la variable de estudio: cada modelo se entrena de forma
independiente y **no se aplica *ensembling***, de modo que cualquier variación en las métricas se
atribuya al mecanismo interno de la red y a su fusión. Todos los experimentos comparten el mismo
dataset y particiones (semilla `20260526`), las mismas transformaciones, la misma función de
pérdida e hiperparámetros y el mismo protocolo de inferencia y métricas. Para estimar la
variabilidad, cada configuración final se entrena con **tres semillas** y se reportan media y
desviación típica. La reproducibilidad se asegura fijando una semilla global que se propaga a todas
las fuentes de aleatoriedad (`set_reproducibility`: `random`, NumPy, PyTorch CPU/CUDA y el control
de determinismo de MONAI) y versionando particiones y configuraciones.

### 4.4.4. Estudio de ablación de estrategias de fusión

El estudio de ablación compara, sobre la **misma** U-Net residual 3D, las cuatro estrategias de
fusión de §4.3.6 (concatenación, ponderación global, compuerta adaptativa y su variante con
descriptor media+desviación). Al ser idéntica la red subyacente, la comparación mide exclusivamente
el efecto de la estrategia de fusión. Los resultados y su análisis se presentan en el Capítulo 5;
la conclusión metodológica sobre si la fusión adaptativa justifica su complejidad se discute allí y
en el Capítulo 6.

## 4.5. Evaluación y análisis de resultados (Fase 5)

### 4.5.1. Inferencia por ventana deslizante

La inferencia sobre validación y test se realiza mediante **ventana deslizante**
(`sliding_window_inference` de MONAI), que procesa volúmenes completos por parches sin exceder la
memoria. Sus parámetros son: tamaño de ventana (ROI) 128³, solapamiento 0,5, mezcla de parches
gaussiana y tamaño de lote de ventana según el entorno. Tras la inferencia, los *logits* se activan
con sigmoide y se binarizan con umbral 0,5. La evaluación (`evaluate`) reconstruye el modelo desde
su configuración, carga el *checkpoint* `best.pt`, exporta las predicciones en NIfTI y calcula las
métricas por caso y su resumen agregado.

### 4.5.2. Métricas de evaluación

El rendimiento se cuantifica con dos métricas estandarizadas, calculadas por región
(`tfm_brats/metrics.py`):

- **Coeficiente Dice**, que mide el solapamiento volumétrico. Por convención se asigna Dice = 1
  cuando predicción y referencia están ambas vacías, y Dice = 0 cuando solo una lo está.
- **Distancia de Hausdorff al percentil 95 (HD95)**, distancia simétrica entre superficies en
  milímetros (usando el *spacing* real del vóxel). Cuando una de las máscaras está vacía la
  distancia es indefinida (∞); esos casos se excluyen del promedio y se contabilizan aparte, por lo
  que las tablas del Capítulo 5 reportan, junto a la media de HD95, el número de casos finitos sobre
  el total —dato necesario para interpretar la métrica en regiones frecuentemente ausentes como ET—.

El análisis comparativo de arquitecturas y estrategias de fusión a partir de estas métricas
constituye el Capítulo 5.

## 4.6. Restricciones y alcance clínico

El sistema segmenta subregiones funcionalmente relevantes (ET, TC, WT) en resonancias magnéticas
multimodales de pacientes previamente confirmados con glioma. Es imperativo documentar que la
arquitectura **no discrimina la presencia o ausencia de tumor en cerebros sanos**, ni diferencia
los gliomas de otras patologías como meningiomas o metástasis, dada la ausencia de estos datos en
el entrenamiento y el alcance técnico del trabajo. Su utilidad se circunscribe, por tanto, a la
optimización de la segmentación intratumoral dentro del entorno controlado del dataset BraTS-GLI
2024.
