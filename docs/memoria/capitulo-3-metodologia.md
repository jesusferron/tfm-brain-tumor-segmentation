# 3. Metodología

> Versión revisada y ampliada del Capítulo 3, contrastada con el código del repositorio
> (`tfm_brats/`, `configs/`, `outputs/splits/`). Lista para integrar en la memoria.
> Referencias de implementación citadas como `archivo.py:línea`.

## 3.1. Framework y Entorno de Computación

La metodología se fundamenta en el framework **MONAI**, especializado en imagen médica y
construido sobre PyTorch. MONAI aporta un conjunto de componentes reutilizables
(transformaciones, *datasets*, redes y funciones de pérdida) pero no orquesta el bucle de
entrenamiento por sí mismo. Por ello, el proyecto implementa un **bucle de entrenamiento
propio** (`tfm_brats/monai_pipeline.py`, función `train_one_run`), que gestiona de forma
explícita la iteración por épocas, el cálculo de la pérdida, la retropropagación, el paso del
optimizador y la validación periódica. Esta decisión otorga control total sobre la precisión
mixta, la validación por ventana deslizante y el registro de métricas, a costa de no apoyarse
en los *engines* de alto nivel de MONAI ni en PyTorch Lightning.

El procesamiento se ha llevado a cabo en **dos entornos de cómputo**, ambos empleados durante el
desarrollo y la experimentación del trabajo:

| Entorno | Dispositivo | Precisión mixta (AMP) |
| :-- | :-- | :-- |
| Local | Apple M4 Pro (backend MPS) | Desactivada |
| Colab Pro | NVIDIA A100 (CUDA) | Activada |

El entorno local se ha utilizado para el desarrollo del pipeline y la ejecución de experimentos
sobre el backend MPS de Apple, mientras que el entorno Google Colab Pro, equipado con
aceleradores **NVIDIA A100**, ha permitido el procesamiento sobre GPU CUDA con mayor capacidad de
memoria. La precisión mixta automática (AMP) se activa únicamente en el entorno CUDA; en el
backend MPS de Apple se mantiene desactivada por las limitaciones de soporte actuales. **Cada
resultado cuantitativo reportado en el Capítulo 5 indica explícitamente el entorno y la
configuración con que se obtuvo**, para garantizar la trazabilidad y evitar comparaciones entre
regímenes de entrenamiento heterogéneos.

## 3.2. Conjunto de Datos y Particiones

El alcance experimental se limita al subconjunto **BraTS-GLI 2024**, evitando mezclar tareas
clínicas distintas de otras colecciones BraTS. Cada caso aporta cuatro volúmenes MRI 3D en
formato NIfTI (una modalidad por canal) y, cuando está disponible, su máscara de segmentación.
Los casos provienen de dos directorios de la distribución oficial (`training_data1_v2` y
`training_data_additional`), que se unifican antes de particionar.

La partición de los datos se realiza de forma **estratificada y reproducible**
(`tfm_brats/splits.py`), con las siguientes características:

- **Tamaño total:** 1.621 casos.
- **Proporción 70 / 15 / 15**, resultando en **1.135 entrenamiento, 243 validación y 243 test**.
- **Estratificación** simultánea por tres factores: origen del caso (directorio de procedencia),
  presencia o ausencia de tumor con realce (ET), y volumen tumoral total discretizado en cuatro
  cuantiles (q1–q4). Esto asegura que las tres particiones mantengan distribuciones comparables
  de tamaño y dificultad.
- **Semilla fija** `20260526`, de modo que la partición es determinista y se materializa en
  disco (`outputs/splits/brats_gli_2024_seed20260526/`) junto con un manifiesto que documenta la
  distribución por estrato.

El **conjunto de validación** se emplea durante el entrenamiento para la monitorización
periódica del rendimiento, mientras que el **conjunto de test, completamente reservado**, se
utiliza para el reporte de las métricas finales. Esta separación evita el sesgo optimista que
supondría informar resultados sobre el mismo conjunto usado para supervisar la convergencia.

## 3.3. Formulación del Problema y Regiones Clínicas

El modelo recibe un tensor de entrada con **cuatro canales**, correspondientes a las cuatro
modalidades MRI: T1 nativa (T1n), T1 con contraste (T1c), T2 (T2w) y FLAIR (denominada **T2f**
en el dataset y el código). Emite un tensor con **tres canales de salida**, cada uno asociado a
una subregión anidada del tumor según la convención BraTS. El código procesa y reporta las
regiones en el orden **ET, TC, WT** (`tfm_brats/brats.py`, `REGION_ORDER`), que se corresponde
con los canales 0, 1 y 2 de la salida:

| Canal | Región | Etiquetas BraTS incluidas | Descripción |
| :-: | :-- | :-- | :-- |
| 0 | **ET** (Enhancing Tumor) | {3} | Porción que capta contraste activo |
| 1 | **TC** (Tumor Core) | {1, 3, 4} | Núcleo sólido: tejido con y sin realce, más necrosis |
| 2 | **WT** (Whole Tumor) | {1, 2, 3, 4} | Extensión completa, incluyendo edema peritumoral |

Las regiones son **estrictamente anidadas** (ET ⊂ TC ⊂ WT), propiedad que se preserva tanto en
la generación de las máscaras de entrenamiento como en la reconstrucción del mapa de etiquetas
para la evaluación.

El problema se formula como **segmentación multietiqueta** (no como clasificación multiclase
excluyente), ya que un mismo vóxel puede pertenecer simultáneamente a las tres regiones. En
consecuencia, las salidas se activan con una función **sigmoide** y se binarizan con un
**umbral de 0,5** (`monai_pipeline.py`), de manera independiente por canal.

## 3.4. Preprocesamiento y Aumento de Datos

El pipeline de preprocesamiento se construye con transformaciones nativas de MONAI
(`monai_pipeline.py`). Una parte se aplica de forma **determinista a todas las particiones**, y
otra constituye el **aumento de datos exclusivo de entrenamiento**:

**Transformaciones comunes (entrenamiento, validación y test):**

1. `LoadImaged` — carga de los volúmenes NIfTI.
2. `EnsureChannelFirstd` — disposición de canales al frente.
3. `BratsRegionsd` (transformación propia) — conversión de la máscara de etiquetas única a los
   tres canales binarios ET / TC / WT.
4. `NormalizeIntensityd` con `nonzero=True` y `channel_wise=True` — normalización de intensidad
   por canal sobre los vóxeles no nulos.
5. `EnsureTyped` — conversión a tensores de PyTorch.

**Aumento de datos (solo entrenamiento):**

6. `SpatialPadd` — relleno hasta el tamaño de parche (128³).
7. `DivisiblePadd` con `k = 16` — garantiza dimensiones divisibles por 16, requisito de las
   arquitecturas en U.
8. `RandCropByPosNegLabeld` — recorte aleatorio ponderado con razón positivo/negativo 1:1,
   extrayendo varias muestras por caso (2 en el entorno MPS, 4 en Colab) para enfocar el
   muestreo en regiones tumorales.
9. `RandFlipd` — volteo aleatorio con probabilidad 0,5 de forma independiente en los tres ejes
   espaciales.

El conjunto de validación y el de test **no reciben ningún aumento de datos**: se procesan con
las transformaciones deterministas y se infieren a resolución completa mediante ventana
deslizante (§3.6).

## 3.5. Configuración de Entrenamiento e Hiperparámetros

Todos los modelos comparten la misma configuración de optimización, de manera que cualquier
diferencia en las métricas sea atribuible a la arquitectura y a su estrategia de fusión, y no a
los hiperparámetros:

| Hiperparámetro | Valor |
| :-- | :-- |
| Optimizador | AdamW |
| Tasa de aprendizaje | 1 × 10⁻⁴ (**constante, sin *scheduler***) |
| *Weight decay* | 1 × 10⁻⁵ |
| Función de pérdida | `DiceCELoss(sigmoid=True, squared_pred=True)` |
| Tamaño de parche | 128 × 128 × 128 |
| *Batch size* | 2 (Colab) / 1 (MPS) |
| Épocas máximas | 30 |
| Pasos máximos (sanity local) | 5.000 |

La función de pérdida **DiceCELoss** combina el coeficiente Dice (con predicciones al cuadrado
en el denominador, `squared_pred=True`) y la entropía cruzada, aplicando internamente la
activación sigmoide a los *logits*. No se emplea ningún planificador de tasa de aprendizaje: la
tasa permanece fija durante todo el entrenamiento.

## 3.6. Inferencia y Métricas de Evaluación

La inferencia sobre validación y test se realiza mediante **ventana deslizante**
(`sliding_window_inference` de MONAI), que permite procesar volúmenes completos por parches sin
exceder la memoria disponible. Sus parámetros son:

- **Tamaño de ventana (ROI):** 128 × 128 × 128.
- **Solapamiento:** 0,5 (Colab) / 0,25 (MPS).
- **Mezcla de parches:** gaussiana (valor por defecto de MONAI).
- **Tamaño de lote de la ventana:** 2 (Colab) / 1 (MPS).

Tras la inferencia, los *logits* se transforman con sigmoide y se binarizan con umbral 0,5. El
rendimiento se cuantifica con dos métricas estandarizadas, calculadas por región
(`tfm_brats/metrics.py`):

- **Coeficiente Dice**, que mide el solapamiento volumétrico. Por convención se asigna Dice = 1
  cuando predicción y referencia están ambas vacías (acierto perfecto del *negativo*), y Dice = 0
  cuando solo una de las dos está vacía.
- **Distancia de Hausdorff al percentil 95 (HD95)**, distancia simétrica entre superficies
  expresada en milímetros (empleando el *spacing* real del vóxel). Cuando una de las dos máscaras
  está vacía, la distancia es indefinida (∞); estos casos **se excluyen del promedio** y se
  contabilizan aparte. Por ello las tablas de resultados reportan, junto a la media, el número de
  casos finitos sobre el total (p. ej. 184/243 en ET), dato necesario para interpretar
  correctamente la métrica en regiones frecuentemente ausentes como ET.

## 3.7. Diseño Experimental y Reproducibilidad

El protocolo experimental compara distintas arquitecturas y estrategias de fusión **aislando
rigurosamente la variable de estudio**. Cada modelo se entrena de forma completamente
independiente y **no se aplica *ensembling*** (promediado de probabilidades entre
arquitecturas), de modo que cualquier variación en las métricas pueda atribuirse exclusivamente
al mecanismo interno de la red y a su estrategia de fusión. Para garantizar la validez de la
comparación, todos los experimentos comparten:

- el mismo dataset (**BraTS-GLI 2024**) y las **mismas particiones** (semilla `20260526`);
- las mismas transformaciones de preprocesamiento y aumento de datos (§3.4);
- la misma función de pérdida e hiperparámetros de optimización (§3.5);
- el mismo protocolo de inferencia por ventana deslizante y las mismas métricas (§3.6).

Las arquitecturas contrastadas se detallan en el Capítulo 4 (modelo base Residual U-Net 3D con
fusión por concatenación, las variantes de fusión adaptativa y ponderación global, Attention
U-Net 3D y Swin-UNETR).

La **reproducibilidad** se asegura fijando una semilla global única (`20260526`) que se propaga
a todas las fuentes de aleatoriedad relevantes (`set_reproducibility` en `monai_pipeline.py`):
`random`, NumPy, PyTorch (CPU y CUDA) y el control de determinismo de MONAI
(`set_determinism`). Combinado con la materialización en disco de las particiones y el
versionado de las configuraciones (`configs/`), esto permite reproducir cualquier experimento a
partir del repositorio.
