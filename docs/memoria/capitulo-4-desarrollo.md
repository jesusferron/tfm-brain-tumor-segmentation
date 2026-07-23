# 4. Desarrollo

El desarrollo separa una infraestructura MONAI compartida de la ruta externa de nnU-Net y mantiene
fija la Residual U-Net en la ablación de fusión.

## 4.1. Familiarización y selección de herramientas (Fase 1)

Se eligió **MONAI**, sobre PyTorch, porque cubría las necesidades compartidas por los experimentos:
carga de volúmenes NIfTI multicanal, transformaciones 3D, arquitecturas de segmentación, pérdidas y
predicción por ventana deslizante. Su interfaz permitió reutilizar el mismo flujo de datos y
evaluación con la Residual U-Net, Attention U-Net y Swin-UNETR. Se mantuvo un bucle de entrenamiento
propio para imponer el presupuesto por pasos, activar AMP solo en CUDA, validar con una selección
fija de casos y conservar puntos de control y métricas con el mismo formato.

Se seleccionaron **cuatro familias de modelos** con funciones diferentes en el estudio: una
Residual U-Net 3D como soporte común de la ablación de fusión; Attention U-Net 3D como variante
convolucional atencional; Swin-UNETR como arquitectura Transformer-UNet; y nnU-Net como referencia
externa auto-configurable. Dentro de la familia residual se evaluaron cuatro configuraciones de
entrada: concatenación, ponderación global, compuerta adaptativa basada en la media y compuerta
adaptativa basada en media y desviación típica. La comparación de herramientas y repositorios que
motivó esta selección se presenta en el Capítulo 2.

## 4.2. Análisis y preparación de los datos (Fase 2)

Antes de entrenar se ejecutaron tres operaciones: descubrimiento de estudios, control de calidad y
generación de particiones.

### 4.2.1. Conjunto de datos y descubrimiento de estudios

El alcance experimental se limita a **BraTS-GLI 2024 post-tratamiento**, sin mezclar tareas de otras
colecciones BraTS. Cada estudio aporta cuatro volúmenes de RM 3D en formato NIfTI y su máscara de
segmentación. La configuración `configs/dataset/brats_gli_2024.yaml` declara la raíz de datos, los
directorios `training_data1_v2` y `training_data_additional`, las modalidades y el sufijo de la
máscara. El módulo `tfm_brats/brats.py` recorre ambos directorios, selecciona las carpetas con
prefijo `BraTS-GLI-` y construye las rutas mediante el patrón
`{identificador}-{modalidad}.nii.gz`.

### 4.2.2. Control de calidad

Antes de entrenar se ejecutó el subcomando `qc`, que verifica la presencia de las cuatro modalidades
y de la máscara, la coherencia de dimensiones, espaciado y transformaciones afines, y la ausencia de
etiquetas no permitidas. También calcula los volúmenes de ET, TC y WT que después se emplean para la
estratificación. El artefacto `outputs/qc/brats_gli_2024_qc_summary.json` registra los 1.621 estudios
con estado `ok`, sin categorías en `problem_counts`; 1.223 contienen ET y 398 no la contienen.

### 4.2.3. Particiones estratificadas y reproducibles

La partición se generó con `tfm_brats/splits.py` sobre **1.621 estudios** y con la semilla
`20260526`. El algoritmo combina tres factores en una única clave de estratificación: directorio de
origen, presencia o ausencia de ET y volumen de WT discretizado en cuatro cuantiles. El primer
factor conserva la representación de las dos entregas de datos; el segundo distribuye los casos sin
ET; y el tercero reparte la carga tumoral aproximada por WT. Los resultados se materializan en
`outputs/splits/brats_gli_2024_seed20260526/` como ficheros CSV y TXT, junto con un manifiesto que
registra la semilla, las proporciones y la distribución obtenida.

**Tabla 6.** Distribución de las particiones de BraTS-GLI 2024.

| Partición | Estudios | Proporción | Uso |
| :-- | --: | --: | :-- |
| Entrenamiento | 1.135 | 70 % | Ajuste de los parámetros de los modelos MONAI y conjunto de origen de nnU-Net |
| Validación | 243 | 15 % | Monitorización y selección de puntos de control en el *pipeline* MONAI |
| Test | 243 | 15 % | Evaluación final después de congelar las configuraciones |

Validación y test tienen el mismo tamaño, pero desempeñan funciones distintas: el test no intervino
en la selección de `best.pt`. La separación se realizó por identificador completo de **estudio de
imagen**, no mediante agrupación por sujeto. El manifiesto confirma 1.621 identificadores
distribuidos sin solapamientos y cuantiles de WT casi equilibrados en cada partición.

La revisión por sujeto se efectuó después de cerrar las ejecuciones finales y confirmó la presencia
de sujetos en más de una partición. No se modificó retrospectivamente el reparto ni se reentrenaron
los modelos. En su lugar, se mantuvo la comparación interna sobre el reparto común y se añadió el
análisis *post hoc* de la sección 4.5.3. Por ello, el test no constituye una estimación independiente
de generalización a pacientes completamente nuevos.

## 4.3. Diseño e implementación del *pipeline* (Fase 3)

### 4.3.1. Entornos de cómputo

La asignación de hardware se decidió a partir de pruebas a resolución 128³. En MPS, las variantes
residuales necesitaron alrededor de 1,2 s por paso en pruebas de extremo a extremo; Attention U-Net,
unos 4,75 s; y Swin-UNETR alcanzó 124 s por paso en el *benchmark* sintético. Este salto no lineal es
compatible con una ruta poco eficiente o una operación no optimizada en MPS, aunque no se conservó
un perfil que permita demostrar su causa. Con 15.000 pasos por semilla, las variantes residuales
eran viables en local, mientras que Attention U-Net y Swin-UNETR se trasladaron a la A100. La Tabla
7 recoge el reparto final y el tratamiento de la precisión mixta.

**Tabla 7.** Entornos utilizados en las ejecuciones finales.

| Entorno | Dispositivo | Precisión mixta | Uso final |
| :-- | :-- | :-- | :-- |
| Local | Apple M4 Pro, *backend* MPS | Desactivada | Cuatro configuraciones de fusión sobre la Residual U-Net 3D |
| Google Colab | NVIDIA A100, CUDA | AMP activada en el *pipeline* MONAI | Attention U-Net 3D y Swin-UNETR |
| Google Colab | NVIDIA A100, CUDA | Gestionada por nnU-Net | nnU-Net `3d_fullres`, *fold* 0 |

Este reparto introdujo diferencias de dispositivo y precisión entre grupos. En consecuencia, los
tiempos de pared y la comparación global de arquitecturas se interpretan de forma descriptiva. Para
las ejecuciones MONAI en A100, los NIfTI se copiaron al disco local del entorno antes de entrenar.
En la ruta nnU-Net, los NIfTI crudos permanecieron en Drive y se enlazaron durante el preprocesado,
mientras que los datos preprocesados sí se guardaron localmente. La decisión de MONAI se derivó del
diagnóstico de entrada/salida descrito en la sección 4.3.4.

### 4.3.2. Organización del código y flujo de trabajo

El código se organiza como un paquete de Python (`tfm_brats/`) y un árbol de configuraciones YAML
(`configs/`). `brats.py` centraliza nombres de modalidades, regiones y rutas para que el control de
calidad, el entrenamiento y la evaluación no mantengan convenciones independientes. `qc.py` y
`splits.py` preparan los datos; `monai_pipeline.py` reúne carga, transformaciones, modelos,
entrenamiento, inferencia y puntos de control; `metrics.py` calcula Dice y HD95; y `cli.py` expone
estas operaciones por línea de comandos. Los YAML quedan fuera del código para reconstruir modelos
y ejecuciones sin modificar la implementación.

Los experimentos MONAI se describen mediante una configuración de datos, otra de modelo y otra de
entrenamiento. Las ejecuciones finales añadieron argumentos explícitos de la CLI para la semilla, el
dispositivo y, en el perfil local, el límite efectivo de 15.000 pasos. La combinación de YAML y
comando identifica los parámetros de cada ejecución; su reproducción requiere además la misma
revisión de código, las particiones, los datos y un entorno compatible. Los comandos se conservan en
`scratchpad/run_final_fusion_ablation.sh` para la ablación local y en
`notebooks/colab_final_a100.ipynb` para Attention U-Net y Swin-UNETR. nnU-Net utiliza scripts y
comandos nativos independientes, descritos en la sección 4.4.5.

La CLI propia expone cinco subcomandos. La Tabla 8 resume su responsabilidad y deja explícita la
separación entre generar predicciones y evaluarlas.

**Tabla 8.** Subcomandos de la interfaz `tfm_brats/cli.py`.

| Subcomando | Función |
| :-- | :-- |
| `qc` | Comprueba integridad, geometría y etiquetas, y genera estadísticas por estudio. |
| `splits` | Genera las particiones estratificadas y su manifiesto. |
| `train` | Entrena una configuración MONAI y guarda registros y puntos de control. |
| `predict` | Carga un modelo y exporta predicciones NIfTI para una partición. |
| `evaluate` | Lee predicciones ya generadas y calcula Dice y HD95 para ET, TC y WT. |

La separación de `predict` y `evaluate` permite recalcular métricas y agregados a partir de los NIfTI
sin repetir la inferencia. La Figura 1 sitúa esta interfaz común junto a las ramas que no comparten el
mismo bucle de entrenamiento.

![Flujo global del sistema experimental.](figuras/fig_pipeline_flujo.png)

**Figura 1.** Visión global del sistema: BraTS-GLI 2024, control de calidad y particiones; carga y
preprocesamiento; ramas MONAI para Residual U-Net con fusión, Attention U-Net y Swin-UNETR, junto
con la rama externa nnU-Net; y generación de predicciones y evaluación común.

Los datos, las particiones y el evaluador final son comunes a las dos rutas; el entrenamiento MONAI
propio y el flujo auto-configurable de nnU-Net permanecen separados. Dentro de MONAI, solo la rama
residual mantiene fija la arquitectura durante la ablación de fusión.

### 4.3.3. Formulación del problema, modalidades y regiones

Los modelos MONAI reciben un tensor con cuatro canales en el orden T1n, T1c, T2w y T2f, donde T2f
corresponde a FLAIR, y producen tres canales para ET, TC y WT. La Tabla 9 relaciona las entradas con
la información que aportan y las salidas con las etiquetas BraTS utilizadas por el código.

**Tabla 9.** Entradas multimodales y salidas regionales del sistema de segmentación.

| Tipo | Canal o elemento | Información o composición | Relevancia para la segmentación |
| :-- | :-- | :-- | :-- |
| Entrada | T1n | Anatomía y señal T1 sin contraste | Aporta contexto anatómico y alteraciones no definidas por realce |
| Entrada | T1c | Información T1 después de contraste | Ayuda a delimitar el componente con realce, sin sustituir la interpretación conjunta de las modalidades |
| Entrada | T2w | Señal sensible al contenido de agua | Resalta alteraciones ricas en líquido y contribuye a estimar la extensión tumoral |
| Entrada | FLAIR (`t2f`) | Señal T2 con supresión del líquido cefalorraquídeo | Facilita la visualización de hiperintensidades parenquimatosas y del componente periférico de WT |
| Salida | ET, canal 0 | Etiqueta {3} | Región tumoral con realce |
| Salida | TC, canal 1 | Etiquetas {1, 3, 4} | Núcleo tumoral completo |
| Salida | WT, canal 2 | Etiquetas {1, 2, 3, 4} | Extensión tumoral completa |

Ninguna secuencia resume por sí sola la información usada para construir ET, TC y WT; la entrada
combina las cuatro para conservar sus aportaciones complementarias. Los ejemplos del Capítulo 5
muestran simultáneamente las regiones predichas sobre un estudio concreto.

Las regiones se representan como máscaras anidadas, ET ⊂ TC ⊂ WT. `BratsRegionsd` transforma la
máscara de etiquetas en tres canales binarios y la salida se formula como segmentación
multietiqueta. Los *logits* se activan con sigmoide y se umbralizan a 0,5. Al exportar la predicción,
`regions_to_labelmap` fuerza la coherencia de inclusión mediante la unión de ET con TC y de TC con
WT, y reconstruye un mapa NIfTI compatible con la evaluación.

### 4.3.4. Preprocesamiento y aumento de datos

El *pipeline* MONAI usa `LoadImaged`, `EnsureChannelFirstd`, normalización por modalidad sobre
vóxeles no nulos (`NormalizeIntensityd(nonzero=True, channel_wise=True)`) y conversión a tensores.
Durante entrenamiento y validación interna también carga la etiqueta y aplica `BratsRegionsd`. La
inferencia de test usa `build_inference_transforms`, que procesa únicamente la imagen. La máscara se
carga después desde `metrics.py` para evaluar la predicción exportada.

El aumento se limita al entrenamiento. `SpatialPadd` asegura un tamaño mínimo de 128³,
`DivisiblePadd(k=16)` mantiene dimensiones compatibles, `RandCropByPosNegLabeld` extrae dos parches
por estudio con razón positiva/negativa 1:1 y `RandFlipd` aplica volteos independientes con
probabilidad 0,5 en los tres ejes. Validación y test no reciben transformaciones aleatorias y se
procesan como volúmenes completos mediante ventana deslizante.

Los datos se sirven con `Dataset` y `DataLoader` de MONAI y la colación `list_data_collate`. Durante
el desarrollo se añadió `build_cached_dataset`, con modos `none`, `memory` y `persistent`, para
adaptar la lectura al entorno. La primera ejecución de Swin-UNETR con caché persistente elevó el uso
de disco a 188 de los 235 GB disponibles en Colab hacia el paso 1.090. Cada caso preprocesado
ocupaba unos 144–150 MB, por lo que entrenamiento y validación requerían cerca de 200 GB de caché,
además del conjunto original y del sistema. La ejecución se detuvo antes de completar la primera
época y no había un punto de control recuperable.

Se mantuvieron los tres modos en el código, pero las ejecuciones MONAI finales en A100 usaron
`cache_mode: none` y copiaron unos 30 GB de NIfTI desde Google Drive a `/content`. En una ejecución
posterior de Swin-UNETR con datos locales se registró un tiempo de espera de alrededor de 0,0004 s
por paso, frente a picos de 3–11 s observados previamente con otro perfil al leer desde Drive. La
comparación no fue pareada, pero respaldó operativamente el uso del disco local sin llenarlo con
volúmenes preprocesados.

### 4.3.5. Familias de modelos y factoría

La función `build_model` de `monai_pipeline.py` construye las tres familias integradas en la
implementación propia: Residual U-Net, Attention U-Net y Swin-UNETR. nnU-Net no pasa por esta
factoría: se ejecuta con su CLI nativa y conserva su planificación, preprocesamiento y
entrenamiento. La Tabla 10 distingue las cuatro familias y, dentro de la residual, las cuatro
variantes de fusión evaluadas.

**Tabla 10.** Familias y configuraciones finales, ruta de implementación y número de parámetros.

| Familia y configuración | Implementación | Hiperparámetros o rasgo principal | Parámetros |
| :-- | :-- | :-- | --: |
| Residual U-Net + concatenación | MONAI `UNet` + `FusionUNet` | canales (16, 32, 64, 128); `num_res_units=2`; identidad de entrada | 1.190.358 |
| Residual U-Net + ponderación global | MONAI `UNet` + `FusionUNet` | cuatro escalares aprendidos | 1.190.362 (+4) |
| Residual U-Net + compuerta por media | MONAI `UNet` + `FusionUNet` | descriptor 4; MLP 4 → 8 → 4 | 1.190.434 (+76) |
| Residual U-Net + compuerta media+desv. | MONAI `UNet` + `FusionUNet` | descriptor 8; MLP 8 → 8 → 4 | 1.190.466 (+108) |
| Attention U-Net 3D | MONAI `AttentionUnet` | canales (16, 32, 64, 128, 256); cuatro niveles de reducción | 5.910.443 |
| Swin-UNETR | MONAI `SwinUNETR` | `feature_size=48`; profundidades (2, 2, 2, 2); cabezas (3, 6, 12, 24) | 62.191.941 |
| nnU-Net `3d_fullres` | nnU-Net v2, externo | Arquitectura y preprocesamiento auto-configurados | Auto-configurado |

Las cuatro configuraciones residuales mantienen fija una red de aproximadamente 1,19 millones de
parámetros y solo cambian el bloque de entrada. Attention U-Net y, especialmente, Swin-UNETR
aumentan la capacidad. nnU-Net se incluye como referencia, no como una configuración construida por
la factoría ni como parte de la ablación.

La primera versión de `build_model` solo construía la Residual U-Net. Se sustituyó por un
despachador que traduce desde YAML las firmas diferentes de `UNet`, `AttentionUnet` y `SwinUNETR`,
pero conserva para el resto del *pipeline* la misma interfaz de cuatro canales de entrada y tres de
salida. Un *smoke test* con tensores de forma (1, 4, 96, 96, 96) verificó las configuraciones antes
de entrenarlas. Swin-UNETR expone además `use_checkpoint`: se activó en la prueba L4 para reducir
memoria, mientras que las ejecuciones finales A100 usaron la configuración sin *gradient
checkpointing*.

### 4.3.6. Mecanismos de fusión multimodal

La comparación principal modifica únicamente el tratamiento de los cuatro canales antes del
codificador residual. `FusionUNet` aplica un módulo de fusión y entrega el tensor resultante a la
misma U-Net:

```python
class FusionUNet(nn.Module):
    def __init__(self, fusion, unet):
        super().__init__()
        self.fusion = fusion
        self.unet = unet

    def forward(self, x):
        return self.unet(self.fusion(x))
```

La Figura 2 representa esta separación entre el bloque de entrada y la red de segmentación, así
como los descriptores usados por las compuertas.

![Arquitectura de fusión multimodal FusionUNet y detalle de la compuerta adaptativa.](figuras/fig_arquitectura_fusion.png)

**Figura 2.** Arquitectura de la ablación: cuatro modalidades, bloque de fusión anterior al
codificador, Residual U-Net común y tres canales de salida. El detalle de la compuerta muestra la
obtención de pesos globales por modalidad a partir de descriptores de la entrada.

El mecanismo no es espacial ni se introduce en capas intermedias: produce un peso por modalidad
para cada muestra y actúa antes de la primera convolución.

**Concatenación (`concat`).** Se implementa como `nn.Identity()`. No introduce una ponderación
explícita. Los cuatro canales llegan directamente a la primera convolución de la U-Net.

**Ponderación global (`global_weighted`).** Aprende cuatro *logits* independientes de la entrada.
Tras aplicar *softmax*, cada canal se multiplica por su peso y por cuatro para preservar la escala
media de activación. Añade cuatro parámetros y aplica la misma combinación a todos los estudios.

**Compuerta adaptativa basada en la media (`adaptive_gating`).** Resume cada canal mediante su media
espacial y procesa los cuatro descriptores con un MLP 4 → 8 → 4. Sus dos capas contienen 76
parámetros: 40 en la primera y 36 en la segunda, incluidos los sesgos. El *softmax* se calcula por
muestra y sus pesos vuelven a escalarse por cuatro.

**Compuerta basada en media y desviación (`adaptive_gating_meanstd`).** Concatena la media y la
desviación típica de cada modalidad, por lo que el descriptor pasa de cuatro a ocho valores y el MLP
8 → 8 → 4 añade 108 parámetros. La compuerta continúa produciendo pesos globales por modalidad, no
mapas espaciales.

La variante surgió de un diagnóstico realizado con
`scripts/diagnose_adaptive_gating.py` sobre el mejor punto de control de una ejecución preliminar de
5.000 pasos y 30 estudios de validación. El script aplicó la compuerta una vez a cada volumen
completo normalizado, no a los parches de entrenamiento ni a las ventanas de inferencia. En esa
comprobación, los pesos de la compuerta basada en la media fueron indistinguibles a tres decimales
(desviación reportada: 0,000) y el Dice interno descendió de 0,586 en la época 4 a 0,521 en la época
5. Esta coincidencia motivó añadir la desviación típica, sin atribuirle una relación causal con el
deterioro. En las exploraciones posteriores sobre 40 volúmenes completos, el artefacto conservado
redondea las desviaciones por modalidad a 0,000 o 0,001. El resultado caracteriza esas entradas
completas y esos puntos de control preliminares, pero no mide cuánto varían los pesos entre los
parches o ventanas que procesa el modelo final.

También se implementaron temperatura del *softmax*, tasa de aprendizaje específica para la fusión,
activación gradual y regularización de entropía. En las exploraciones de 5.000 pasos, estabilizar la
compuerta basada solo en la media produjo un Dice de validación de 0,594 y no eliminó la regresión
tardía. Las tres variantes basadas en la media y la desviación típica alcanzaron entre 0,650 y 0,661
con la semilla 20260526, pero la repetición con tres semillas no sostuvo esa mejora. La
bitácora y `outputs/evaluation/adaptive_gating_explore_diagnosis.txt` conservan esta secuencia. Por
ello, la ablación final incluyó los dos descriptores, pero mantuvo el protocolo común: temperatura
1, sin tasa específica, activación gradual ni penalización de entropía.

## 4.4. Experimentación (Fase 4)

La evidencia se organizó en una ablación controlada, dos referencias MONAI y una referencia externa
nnU-Net.

### 4.4.1. Configuración de entrenamiento MONAI

Las configuraciones MONAI finales compartieron los hiperparámetros de optimización de la Tabla 11.
El presupuesto se fijó mediante la sonda de concatenación conservada en
`outputs/train/probe_concat_25k`, ejecutada durante 25.000 pasos y validada al final de cada época
sobre ocho estudios fijos. El Dice interno fue 0,686 en el paso 12.485, alcanzó un máximo de 0,691
en el 21.565 y terminó en 0,688. La mejora máxima después del paso 12.485 fue, por tanto, de 0,005 y
fue pequeña respecto de la fluctuación observada en ese subconjunto, sin que se estimara formalmente
su incertidumbre. Se adoptaron 15.000 pasos para cubrir el inicio de la meseta con un presupuesto
común. En el perfil local, cuyo YAML conserva un techo de 25.000, el límite efectivo se impuso con
`--max-steps 15000`.

**Tabla 11.** Hiperparámetros efectivos del protocolo MONAI final.

| Hiperparámetro | Valor |
| :-- | :-- |
| Optimizador | AdamW |
| Tasa de aprendizaje | 1 × 10⁻⁴ |
| Planificación | *Warmup* lineal de 1.000 pasos hasta la tasa base y decaimiento *cosine* hasta el 1 % de ella |
| *Weight decay* | 1 × 10⁻⁵ |
| Función de pérdida | `DiceCELoss(sigmoid=True, squared_pred=True)` |
| Tamaño de parche | 128 × 128 × 128 |
| Tamaño de lote | 1 estudio, con 2 parches generados por estudio |
| Presupuesto | 15.000 pasos, aproximadamente 13 épocas |
| Semillas | 20260526, 20260527 y 20260528 |

Los valores de la Tabla 11 se aplicaron a las seis configuraciones MONAI —cuatro configuraciones
residuales, Attention U-Net y Swin-UNETR, cada una con tres semillas—, pero no a nnU-Net. La
igualdad de hiperparámetros permite una ablación controlada dentro de la familia residual. La
comparación entre familias sigue siendo descriptiva porque cambian el dispositivo, AMP y el
solapamiento de inferencia.

`DiceCELoss` combina el término Dice y la entropía cruzada binaria sobre los tres canales. El
planificador se adoptó para distribuir la tasa de aprendizaje dentro del presupuesto fijado. No se
utiliza su incorporación como evidencia causal de superioridad frente a la tasa constante de las
exploraciones preliminares.

### 4.4.2. Bucle de entrenamiento y selección de puntos de control

`train_one_run` gestiona la carga de lotes, el cálculo de la pérdida, la retropropagación, el paso de
AdamW, el planificador y la validación periódica. En CUDA usa autocast y escalado de gradiente. En
MPS ambas funciones permanecen desactivadas. El entrenamiento se limita por número de pasos, aunque
el registro conserva también la época alcanzada.

Al final de cada época —y al alcanzar el límite de pasos— se calcula `mean_dice`, la media de Dice
de ET, TC y WT. En las pruebas preliminares se aumentó la validación interna de dos a **ocho lotes**
para reducir el ruido sin renunciar a una comprobación al final de cada época. Como el cargador
tiene tamaño de lote uno y no baraja, se usan siempre los ocho primeros estudios de `val.csv`. No se
conservó un *benchmark* que cuantifique el ahorro frente a validar los 243 estudios, por lo que ocho
debe entenderse como un compromiso operativo y no como un tamaño óptimo.

Esta métrica selecciona `best.pt`, mientras que `last.pt` conserva el estado más reciente. El riesgo
aceptado es que la selección dependa de un subconjunto pequeño, con mayor ruido y una composición de
ET, TC y WT potencialmente poco representativa. La evaluación reportable se ejecuta después con
`predict` y `evaluate` sobre la partición completa.

Cada punto de control guarda el estado del modelo y del optimizador, las configuraciones, la época,
el paso global y la mejor métrica observada. `best.pt` es el artefacto utilizado posteriormente por
el subcomando `predict`.

### 4.4.3. Diseño de las comparaciones y reproducibilidad

La **ablación de fusión** constituye la comparación controlada del trabajo. Sus cuatro
configuraciones comparten la Residual U-Net, los estudios y particiones, las transformaciones, la
pérdida, el optimizador, el presupuesto, el entorno MPS y el protocolo de inferencia. Cada una se
entrenó con las tres semillas y sin *ensemble*. El diseño reduce las diferencias deliberadas al
bloque de fusión y permite interpretar los resultados dentro de la variabilidad observada, sin
suponer un aislamiento causal perfecto.

Attention U-Net y Swin-UNETR compartieron entre sí el protocolo MONAI A100, incluidas AMP y tres
semillas. En cambio, la comparación de estas arquitecturas con las residuales no es causal. Además
de la arquitectura, cambian el dispositivo y el solapamiento de inferencia. nnU-Net se separa aún
más de este protocolo, pues utiliza su propio preprocesamiento y entrenamiento y solo una ejecución
del *fold* 0.

La reproducibilidad práctica se apoya en `set_reproducibility`, que propaga cada semilla a Python,
NumPy, PyTorch y MONAI, y en la conservación de particiones, YAML, comandos y métricas. Los puntos
de control pesados y parte de los registros de las ejecuciones A100 permanecen fuera del
repositorio, por lo que su auditoría requiere recuperar esos artefactos externos. Las tres semillas
permiten describir la dispersión de los modelos MONAI, pero no sustituyen un contraste inferencial
con un número mayor de repeticiones.

### 4.4.4. Estudio de ablación de estrategias de fusión

La ablación compara concatenación, ponderación global, compuerta por media y compuerta por media y
desviación típica sobre la misma Residual U-Net. Además de Dice y HD95, se conservaron los pesos de
la variante global. `scripts/diagnose_adaptive_gating.py` se utilizó en las exploraciones
preliminares para calcular pesos medios, desviación y entropía sobre 40 volúmenes completos y
recuperar la curva de validación. El repositorio no conserva una salida equivalente de los puntos de
control finales ni un registro de pesos por parche o ventana. Por tanto, ese diagnóstico documenta
la decisión de diseño, pero no caracteriza la operación de las compuertas finales ni demuestra la
causa del rendimiento. Los resultados se presentan en el Capítulo 5.

### 4.4.5. nnU-Net como referencia externa

nnU-Net se ejecutó fuera de la factoría MONAI. El script
`scripts/nnunet/prepare_brats_gli_nnunet_full.py` convirtió las particiones al formato nativo de
nnU-Net v2 mediante un NIfTI por modalidad y estudio, con nombres de canal `_0000` a `_0003`, y
conservó las etiquetas 0–4. En el entorno A100 se usó el conjunto `Dataset725_BraTSGLI2024`, se
ejecutaron la planificación y el preprocesamiento propios de nnU-Net y se entrenó la configuración
`3d_fullres`, *fold* 0, con `nnUNetTrainer_250epochs`.

Según la bitácora y el registro conservado fuera del repositorio, el *fold* interno dividió los
1.135 estudios proporcionados a nnU-Net en 908 para ajuste y 227 para validación. El repositorio no
incluye `splits_final.json`, por lo que no permite auditar qué estudios integraron cada parte del
*fold*. Tras seleccionar `checkpoint_best.pth`, se regeneró `imagesTs` con los 243 estudios de la
partición test del TFM y se realizó la predicción con la CLI nativa. Solo se efectuó una ejecución,
sin conjunto de cinco *folds* ni *ensemble*. Sus predicciones se evaluaron con el mismo `metrics.py`
que los modelos MONAI para obtener Dice y HD95 comparables, pero su resultado se trata como
referencia contextual por las diferencias de datos efectivos de ajuste, preprocesamiento, pérdida,
optimizador y presupuesto.

## 4.5. Evaluación y análisis de resultados (Fase 5)

### 4.5.1. Inferencia y exportación de predicciones

Los modelos MONAI se infieren con `sliding_window_inference` sobre ventanas 128³. Las variantes
residuales ejecutadas en MPS usan solapamiento **0,25** y tamaño de lote de ventana 1. Attention
U-Net y Swin-UNETR, ejecutados en A100, usan solapamiento **0,50** y tamaño de lote de ventana 2. El
código no especifica `mode`, por lo que MONAI emplea su mezcla constante predeterminada, no mezcla
gaussiana. nnU-Net utiliza su procedimiento de inferencia propio.

El subcomando `predict` reconstruye el modelo MONAI desde su YAML, carga `best.pt`, aplica sigmoide
y umbral 0,5, fuerza el anidamiento ET ⊂ TC ⊂ WT y guarda un NIfTI por estudio. El subcomando
`evaluate` es posterior e independiente, ya que lee esos NIfTI y las máscaras de referencia y calcula
las métricas. Esta separación permite repetir el cálculo sin volver a ejecutar la red.

### 4.5.2. Métricas de evaluación

El rendimiento se cuantifica con Dice y HD95 por región mediante `tfm_brats/metrics.py`:

- **Dice** mide el solapamiento. Se asigna Dice = 1 cuando predicción y referencia están ambas
  vacías, y Dice = 0 cuando solo una de ellas lo está.
- **HD95** calcula el percentil 95 de las distancias simétricas entre superficies usando el espaciado
  real del NIfTI. Si ambas máscaras están vacías se asigna HD95 = 0. Si exactamente una está vacía,
  el resultado es infinito.

Los resúmenes de HD95 conservan los ceros de los casos doblemente vacíos y excluyen los infinitos
del promedio. Por ello, el Capítulo 5 presenta cada media junto al número de estudios con valor
finito. Las métricas son internas y se calculan por región, por lo que no reproducen el protocolo
oculto ni las métricas *lesion-wise* del reto oficial BraTS-GLI 2024.

### 4.5.3. Análisis de sensibilidad por sujeto

La revisión de identificadores de sujeto se realizó una vez concluidos los entrenamientos y
generadas las predicciones finales. Se definió entonces un subconjunto *post hoc* con los 38
estudios de test pertenecientes a 29 sujetos sin presencia en entrenamiento ni validación. No se
creó una nueva partición de entrenamiento: se reutilizaron las predicciones y se recalcularon los
agregados de las cuatro estrategias de fusión. El análisis permite observar si cambia la ordenación
descriptiva en ese subconjunto, pero no sustituye una partición por sujeto planificada antes de
entrenar.

### 4.5.4. Huella computacional

El número de parámetros se obtuvo de los modelos instanciados. En el *pipeline* MONAI, el tiempo de
pared se registra con `perf_counter` desde el inicio del entrenamiento hasta la última validación, y
en CUDA se consulta el máximo de memoria asignada por PyTorch. Esta medida no está disponible de
forma equivalente en MPS. Para nnU-Net, el tiempo se recuperó, según el registro conservado fuera
del repositorio, de las marcas comprendidas entre el inicio de la época 0 y `Training done`. No
incluye planificación, preprocesamiento, validación final completa ni inferencia. Al no existir
tiempos de inferencia y memoria homogéneos para todos los modelos, el Capítulo 5 limita la
comparación computacional a los registros conservados.

## 4.6. Restricciones y alcance clínico

El sistema segmenta ET, TC y WT en resonancias multimodales post-tratamiento de sujetos incluidos en
BraTS-GLI 2024. No se entrenó con cerebros sanos ni con otras patologías, por lo que no debe
interpretarse como un sistema de detección de tumor ni de diagnóstico diferencial. Tampoco se ha
evaluado en otras instituciones o protocolos de adquisición. A ello se añade que el reparto por
estudio no garantiza independencia por sujeto. En consecuencia, los resultados describen el
comportamiento experimental de los modelos dentro de este conjunto y no una validación clínica para
uso asistencial.
