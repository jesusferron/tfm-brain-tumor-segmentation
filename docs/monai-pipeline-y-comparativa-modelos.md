# Pipeline MONAI y comparativa entre modelos

Este documento explica como funciona MONAI dentro del repositorio, que produce cada modelo configurado y como se agregan los resultados de las distintas arquitecturas para responder a la pregunta de investigacion del TFM. Esta pensado como material de apoyo para la memoria final, no como guia operativa (las guias operativas estan en `docs/colab-pro-baseline-residual-unet.md` y en la bitacora).

## 1. Que es MONAI y que aporta al pipeline

MONAI es una libreria construida sobre PyTorch, especializada en imagen medica. **No es un sistema completo de entrenamiento**: no orquesta el bucle de entrenamiento, no decide hiperparametros y no entrena por si sola. Lo que aporta es un conjunto de piezas reutilizables, que en este repositorio se componen dentro de `tfm_brats/monai_pipeline.py`:

```
                    PyTorch (motor de tensores y autograd)
                              |
                              v
        +---------------------------------------------+
        |                   MONAI                     |
        +---------------------------------------------+
        | transforms | data    | networks  | losses   |
        |            |         |           |          |
        | Resamplers | Dataset |  UNet     | DiceLoss |
        | Normaliz.  | DataLoa.| AttentUnet| DiceCE   |
        | RandCrop   | Caching | SwinUNETR | Focal    |
        | RandFlip   | list_   | SegResNet |          |
        | ...        | collate | ...       |          |
        +------------+---------+-----------+----------+
        |  inferers (sliding_window_inference)        |
        |  metrics (DiceMetric, HausdorffDistance)    |
        |  apps (nnUNetV2Runner, bundle, ...)         |
        +---------------------------------------------+
                              |
                              v
                Codigo propio (tfm_brats/monai_pipeline.py)
                -- conecta las piezas en un training loop --
```

En este repositorio, MONAI provee:

- **Transforms** para carga, normalizacion y augmentacion: `LoadImaged`, `EnsureChannelFirstd`, `NormalizeIntensityd`, `RandCropByPosNegLabeld`, `RandFlipd`, `SpatialPadd`, `DivisiblePadd`. Se componen con `Compose`.
- **Datasets y dataloaders** especializados (`monai.data.Dataset`, `list_data_collate`).
- **Arquitecturas pre-implementadas** (`monai.networks.nets`): `UNet`, `AttentionUnet`, `SwinUNETR`.
- **Funciones de perdida** (`monai.losses.DiceCELoss`).
- **Inferencia por sliding window** sobre el volumen completo (`monai.inferers.sliding_window_inference`).

El codigo propio (`tfm_brats/monai_pipeline.py`) escribe el training loop, el factory de modelos (`build_model`), la conversion de etiquetas BraTS a regiones ET/TC/WT (`BratsRegionsd`), el calculo de Dice por region, los checkpoints y los logs.

## 2. Que produce cada modelo configurado

### 2.1 Firma comun de entrada y salida

Todos los modelos del catalogo comparten la misma firma:

```
Entrada:  tensor (B, 4, D, H, W)   <- 4 modalidades MRI (T1n, T1c, T2w, T2f)
Salida:   tensor (B, 3, D, H, W)   <- 3 logits, uno por region BraTS
```

Cada canal de salida corresponde a una **region BraTS**. Son tres mascaras binarias **solapadas**, no clases mutuamente excluyentes:

| Canal | Region | Definicion | Etiquetas originales BraTS |
| --- | --- | --- | --- |
| 0 | ET (Enhancing Tumor) | tumor con realce de contraste | label = 3 |
| 1 | TC (Tumor Core) | nucleo: necrosis + realce + tejido no realzado | labels {1, 3, 4} |
| 2 | WT (Whole Tumor) | toda la lesion visible | labels {1, 2, 3, 4} |

El modelo emite **logits** (numeros reales, posiblemente negativos). Para convertirlos en mascara binaria se aplica `sigmoid` y un umbral de 0.5. La funcion `regions_to_labelmap` recombina las tres mascaras binarias en un unico mapa de etiquetas BraTS (0/1/2/3/4) que se guarda como NIfTI durante la prediccion.

### 2.2 Diferencias entre arquitecturas

Lo unico que cambia entre arquitecturas es **como** se calcula la transformacion interna (4 canales -> 3 canales). El resto del protocolo es identico:

| Componente | `residual_unet_3d` | `attention_unet_3d` | `swin_unetr` | `*_global_weighted` / `*_adaptive_gating` |
| --- | --- | --- | --- | --- |
| Implementacion | `monai.networks.nets.UNet` con bloques residuales | `monai.networks.nets.AttentionUnet` | `monai.networks.nets.SwinUNETR` | `monai.UNet` precedido por un modulo de fusion aprendible |
| Parametros | 1.19 M | 5.91 M | 62.19 M | 1.19 M + ~10-50 parametros extra |
| Mecanismo distintivo | convolucion 3D + conexiones residuales | + attention gates en skip connections | encoder Swin Transformer 3D + decoder tipo U-Net | igual que residual, pero los 4 canales de entrada se reponderan antes de la red |
| Coste por step (estimacion A100 con AMP) | ~0.5 s | ~0.8 s | ~2-4 s | ~0.5 s |

### 2.3 Lo que NO cambia entre arquitecturas

Esta es una decision metodologica deliberada y critica para la validez de la comparacion:

- Las transformaciones MONAI sobre los datos (mismo cropping, mismo flip, misma normalizacion).
- La funcion de perdida (`DiceCELoss` con `sigmoid=True, squared_pred=True`).
- La validacion (`sliding_window_inference` con la misma ventana, overlap y umbral).
- El umbral de prediccion (0.5) y el post-procesado (`regions_to_labelmap`).
- El split del dataset, la semilla y el hold-out.
- Las metricas reportadas (Dice y HD95 por region).

Si cualquiera de estos elementos variase entre arquitecturas, no se podria atribuir la diferencia de metricas a la arquitectura: estaria contaminada por diferencias de protocolo. Por eso el factory `build_model` solo cambia la red, nunca el resto.

### 2.4 Que representa realmente la salida del modelo

Conviene precisar que tipo de prediccion produce la red, porque la formulacion BraTS es facil de malinterpretar.

**El modelo emite una segmentacion densa, no un conjunto de candidatos.** Cada voxel del volumen recibe tres valores reales (logits) que, tras `sigmoid` y umbral 0.5, se convierten en tres mascaras binarias. Esa es ya la respuesta final del modelo. No hay etapa posterior de refinamiento o seleccion de candidatos en el pipeline actual. El flujo es:

```
   logits           tensor (B, 3, D, H, W) en R
   crudos           3 valores reales por voxel (ET / TC / WT)
                                |
                                | sigmoid()
                                v
   probabilidades   tensor (B, 3, D, H, W) en [0, 1]
   por region       prob de pertenecer a ET / TC / WT
                                |
                                | > 0.5
                                v
   mascaras         tensor (B, 3, D, H, W) en {0, 1}
   binarias         este voxel esta en ET? en TC? en WT?
                                |
                                | regions_to_labelmap()
                                v
   etiqueta         tensor (D, H, W) en {0, 1, 2, 3, 4}
   BraTS final      un unico valor por voxel
```

**Las tres regiones BraTS son anidadas, no exclusivas.** Estan en relacion de subconjunto: `ET` esta contenida en `TC`, y `TC` esta contenida en `WT`. Por eso un voxel del tejido con realce pertenece simultaneamente a ET, TC y WT, y el modelo predice las tres probabilidades de forma independiente (de ahi `sigmoid` por canal, no `softmax` entre canales). Esta formulacion *region-based* o *multilabel* es el estandar en BraTS desde 2018; antes se usaba clasificacion multiclase exclusiva sobre las etiquetas originales (1, 2, 3, 4) y daba peores resultados porque esas etiquetas no representan bien la naturaleza anidada de las regiones clinicas relevantes.

**Lo que el modelo NO hace, aunque podria parecer que si:**

- *No clasifica el tipo de tumor.* El dataset BraTS-GLI 2024 contiene exclusivamente gliomas. El modelo aprende a segmentar **sub-regiones internas** de un glioma (ET, TC, WT son partes del **mismo** tumor, no tipos distintos de tumor). No puede distinguir un glioma de un meningioma, una metastasis o cualquier otra patologia que no haya visto en entrenamiento.
- *No detecta presencia de tumor de forma fiable en cerebros sanos.* Todos los casos de entrenamiento contienen tumor, por lo que el modelo no ha aprendido la distribucion de un cerebro normal. Si se le pasara una resonancia sin tumor, su comportamiento no esta definido y muy probablemente alucinaria una segmentacion. Para deteccion de presencia/ausencia haria falta otro tipo de modelo y otro tipo de dataset.
- *No produce un mapa de sospecha que requiera revision voxel a voxel.* La salida es ya una **propuesta de segmentacion**. En un escenario clinico se revisaria por un especialista como tal, no como un primer filtro de candidatos.
- *No aplica reglas heuristicas de post-procesado.* Algunos equipos del challenge BraTS afinan resultados eliminando componentes conexos pequenos, rellenando huecos o reasignando regiones segun volumen. El pipeline actual no lo hace; la prediccion es directamente `sigmoid > 0.5` por canal. Esta decision es metodologicamente mas honesta para comparar arquitecturas, pero penaliza el Dice absoluto frente a equipos que si post-procesan. Queda documentado como limitacion.

**Que pregunta clinica responde la salida.** Dada una resonancia de un caso ya identificado como glioma (por contexto clinico, biopsia u otro estudio previo), el modelo propone donde esta el tumor entero (WT), donde esta su nucleo solido (TC) y donde esta la parte con realce activo (ET). Esa informacion tiene valor clinico concreto: el volumen ET correlaciona con tejido tumoral activo en proliferacion, TC define lo que habitualmente se contemplaria para resecccion o radioterapia, y WT delimita la extension total incluyendo edema peritumoral.

Esta caracterizacion del output es la que conecta el problema tecnico de segmentacion con la pregunta clinica de la memoria: el modelo no decide **si** hay tumor, ni **que tipo** es; **dado** que ya se sabe que hay un glioma, propone **donde** estan sus sub-regiones funcionalmente relevantes.

### 2.5 Artefactos producidos por cada corrida

Para cada entrenamiento (`outputs/train/<nombre>/`):

```
train_summary.json        <- metricas finales: best_metric, mean_dice, ET/TC/WT_dice, tiempos
train_log.csv             <- una fila por step: loss, lr, data_wait, compute, gpu_mem, ...
checkpoints/best.pt       <- pesos con mejor mean_dice en validacion
checkpoints/last.pt       <- pesos del ultimo step
```

Tras ejecutar `predict` y `evaluate` sobre el split `val`:

```
outputs/predictions/<nombre>_val/<case_id>.nii.gz   <- una prediccion por caso
outputs/predictions/<nombre>_val/predictions.csv    <- manifiesto
outputs/evaluation/<nombre>_val_metrics.csv         <- Dice y HD95 por caso
outputs/evaluation/<nombre>_val_metrics_summary.json<- resumen agregado
```

## 3. Como se agregan los resultados entre modelos

Conviene distinguir dos estrategias que suenan parecidas pero responden a preguntas distintas. **Solo una es la correcta para este TFM.**

### 3.1 Opcion A: comparacion (la que aplica al TFM)

Los modelos **no se mezclan**. Cada uno se entrena por separado, se evalua por separado y al final se construye una **tabla comparativa**. La pregunta de investigacion del TFM, segun la propuesta consolidada en la bitacora, es:

> Puede una estrategia de fusion adaptativa de modalidades MRI mejorar la segmentacion 3D de gliomas en BraTS-GLI frente a una fusion por concatenacion estandar, manteniendo un coste computacional asumible y con mejoras consistentes en ET, TC y WT?

Para responder a esa pregunta hay que **medir cada estrategia aislada** y compararlas en una tabla con la forma:

| Modelo | ET_dice | TC_dice | WT_dice | mean_dice | ET_HD95 | TC_HD95 | WT_HD95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `residual_unet_3d` (fusion concat, baseline) |  |  |  |  |  |  |  |
| `residual_unet_3d_global_weighted` |  |  |  |  |  |  |  |
| `residual_unet_3d_adaptive_gating` (contribucion principal) |  |  |  |  |  |  |  |
| `attention_unet_3d` |  |  |  |  |  |  |  |
| `swin_unetr` |  |  |  |  |  |  |  |
| `nnU-Net externo` (baseline fuerte) |  |  |  |  |  |  |  |

La memoria reporta esta tabla y la interpreta: por ejemplo, "la fusion adaptativa mejora WT en X puntos pero degrada ET en Y, mientras que Swin-UNETR domina globalmente a costa de 50x mas computo". **Ese contraste es la respuesta a la pregunta de investigacion.**

Ventajas metodologicas de esta estrategia:

- Responde directamente a la pregunta del TFM.
- Es reproducible y trazable: cada modelo tiene su propia carpeta de artefactos y configuracion.
- Permite atribuir diferencias en metricas a diferencias concretas de arquitectura o de estrategia de fusion.

### 3.2 Opcion B: ensembling (tecnica clasica en BraTS, no aplicable aqui)

El ensembling consiste en promediar las probabilidades (sigmoide de los logits) de varios modelos antes de umbralizar. En cada voxel:

```
prob_final(v) = (prob_residual(v) + prob_attention(v) + prob_swin(v)) / 3
mask(v)       = prob_final(v) > 0.5
```

Esta tecnica suele mejorar el Dice final en BraTS porque los errores de los modelos son parcialmente independientes y se cancelan al promediar. Por eso los equipos ganadores del challenge BraTS suelen reportar ensembles.

**No se aplicara en este TFM**, por tres motivos metodologicos:

1. **Confunde la pregunta de investigacion**. Si se hace ensemble entre arquitecturas, las contribuciones individuales quedan disueltas en el promedio y deja de poder atribuirse la mejora a una estrategia concreta de fusion.
2. **Multiplica el coste de inferencia** sin aportar evidencia sobre fusion de modalidades, que es el eje del trabajo.
3. **Mezcla niveles de abstraccion** que la metodologia mantiene separados: el ensembling combina modelos, no estrategias de fusion.

Un uso valido de promediado dentro del TFM seria distinto: entrenar el **mismo modelo** con varias semillas y reportar media y desviacion estandar de las metricas. Eso refuerza el rigor de la comparacion sin disolver las diferencias entre arquitecturas. Esta variante se considera trabajo opcional segun presupuesto computacional disponible.

### 3.3 Lo que si se comparte entre corridas

Aunque los modelos se entrenan por separado, **el protocolo se mantiene identico entre corridas** para que la comparacion sea valida:

- El dataset BraTS-GLI 2024 y su `dataset_root`.
- El split versionado (`outputs/splits/brats_gli_2024_seed20260526`).
- La semilla (`20260526`).
- Las transformaciones de datos, la funcion de perdida y la inferencia sliding window.
- Las regiones BraTS (ET, TC, WT) y las metricas (Dice, HD95).
- Idealmente, el hardware y las versiones de PyTorch/MONAI. Si se entrena en sesiones distintas con hardware distinto, se declara como limitacion.

Lo que **no** se comparte: pesos, gradientes, predicciones a nivel voxel ni curvas de loss. Cada corrida es independiente.

## 4. Flujo operativo para producir la tabla comparativa

El pipeline del repositorio ya esta preparado para producir la tabla. Para cada modelo del catalogo se ejecuta la misma secuencia, cambiando unicamente `--model-config` y los directorios de salida:

```
1. Entrenar:   python -m tfm_brats.cli train     --model-config <X>.yaml --output-dir outputs/train/<X>
2. Predecir:   python -m tfm_brats.cli predict   --model-config <X>.yaml --checkpoint outputs/train/<X>/checkpoints/best.pt \
                                                  --output-dir outputs/predictions/<X>_val
3. Evaluar:    python -m tfm_brats.cli evaluate  --predictions-dir outputs/predictions/<X>_val \
                                                  --output-csv outputs/evaluation/<X>_val_metrics.csv \
                                                  --output-json outputs/evaluation/<X>_val_metrics_summary.json
```

Una vez ejecutadas las N corridas, la tabla comparativa se construye leyendo los `outputs/evaluation/*_val_metrics_summary.json`. Esa agregacion final es trivial y puede automatizarse con un script de soporte (pendiente).

## 5. Relacion con la pregunta de investigacion

Resumen de como las piezas anteriores responden a la pregunta del TFM:

- **MONAI** aporta las herramientas para construir un protocolo reproducible (transforms, dataloaders, perdida, inferencia, metricas). No introduce sesgos arquitectonicos por si solo.
- **Cada arquitectura** del catalogo (residual U-Net, Attention U-Net, Swin-UNETR, y las dos variantes de fusion sobre residual U-Net) ataca el problema de segmentacion con un grado distinto de capacidad y de mecanismo de combinacion de modalidades. Todas comparten salida (3 regiones BraTS) y protocolo.
- **La comparacion** entre las dos ablaciones de fusion (`global_weighted`, `adaptive_gating`) frente al baseline `concat` responde directamente a la pregunta principal del TFM. Los modelos adicionales (Attention U-Net, Swin-UNETR, nnU-Net) sirven como referencia para contextualizar las mejoras: una mejora pequena de la fusion adaptativa frente a concat puede ser significativa si va acompanada de un coste computacional menor que el de Swin-UNETR.
- **No se hara ensembling**, para no diluir el efecto especifico de cada estrategia de fusion.

## 6. Alcance y aplicabilidad clinica

Esta seccion delimita explicitamente que pregunta responde el modelo y que preguntas quedan fuera de su alcance. Es importante fijarla porque el lenguaje habitual ("deteccion de tumores", "clasificacion de tumores cerebrales") puede sugerir capacidades que la formulacion concreta del problema no proporciona.

### 6.1 Que pregunta responde la salida del modelo

Dado un paciente del que ya se sabe, por contexto clinico, biopsia u otro estudio previo, que tiene un glioma, el modelo propone **donde** estan tres sub-regiones funcionalmente relevantes dentro de la lesion:

- WT (Whole Tumor): extension completa, incluyendo edema peritumoral.
- TC (Tumor Core): nucleo solido (tejido tumoral con y sin realce, mas necrosis).
- ET (Enhancing Tumor): parte que capta contraste en T1c, asociada a tejido activo en proliferacion.

Estas tres regiones son las habitualmente utilizadas en la practica clinica para planificacion quirurgica y radioterapica, y para seguimiento longitudinal de respuesta a tratamiento. El interes clinico de la salida reside en delimitar volumen y localizacion de cada region, no en clasificar la lesion.

### 6.2 Que preguntas NO responde el modelo

Tres limitaciones de alcance que deben quedar explicitas en la memoria final:

- **No detecta presencia o ausencia de tumor de forma fiable.** El dataset BraTS-GLI 2024 contiene exclusivamente casos con tumor confirmado. El modelo no ha sido expuesto a cerebros sanos durante el entrenamiento y, por construccion, no aprende la distribucion del cerebro normal. Aplicado a una resonancia sin tumor su comportamiento no esta definido: lo mas probable es que produzca una segmentacion espuria por sesgo de distribucion. Para deteccion presencia/ausencia haria falta un dataset con clase negativa (cerebros sanos) y una formulacion distinta del problema (clasificacion binaria o deteccion de anomalia), con metricas distintas (sensibilidad, especificidad, AUC) y no Dice/HD95.
- **No discrimina entre tipos de tumor cerebral.** El modelo aprende a segmentar sub-regiones internas de un glioma, no a distinguir un glioma de un meningioma, una metastasis u otras patologias. Las tres salidas ET, TC y WT son **partes anidadas del mismo tumor**, no categorias mutuamente excluyentes de tumores distintos. Si se aplicase a una lesion no-glioma, intentaria segmentarla con las categorias aprendidas para glioma y el resultado no seria clinicamente interpretable. El alcance del TFM se limita explicitamente a gliomas, alineado con el dataset.
- **No sustituye a un especialista.** La salida es una propuesta de segmentacion, no un diagnostico ni una decision clinica. En cualquier uso real, un radiologo o neurocirujano debe revisar y validar la prediccion antes de utilizarla para planificacion o seguimiento. El modelo es un asistente de segmentacion, no un sistema autonomo.

### 6.3 Pre-condiciones de uso

Para que la salida del modelo sea interpretable como una propuesta de segmentacion utilizable, deben cumplirse las siguientes condiciones:

- El caso debe corresponder a un paciente ya diagnosticado de glioma.
- La adquisicion debe contener las cuatro modalidades MRI utilizadas en BraTS-GLI: `T1n`, `T1c`, `T2w`, `T2f`.
- Las modalidades deben estar correctamente co-registradas en el mismo espacio anatomico.
- El protocolo de adquisicion debe ser compatible con el usado por BraTS-GLI 2024 (las grandes diferencias de protocolo introducen *domain shift* que degrada el rendimiento).

Estas pre-condiciones son consistentes con el escenario de uso al que esta orientado el TFM: experimentacion metodologica sobre un benchmark publico y reproducible, no despliegue clinico.

### 6.4 Por que esta delimitacion es importante para la memoria

Una redaccion imprecisa del alcance es un riesgo clasico en TFM de aplicacion clinica. Frases como *"el modelo detecta tumores cerebrales"* o *"clasifica el tipo de tumor"* sobreestiman lo que la formulacion concreta del problema permite. La formulacion precisa, que debe utilizarse de forma consistente en la memoria, es:

> El modelo segmenta tres sub-regiones funcionalmente relevantes (ET, TC, WT) en resonancias magneticas multimodales de pacientes con glioma, generando una propuesta de segmentacion volumetrica que requiere validacion clinica antes de su uso.

Esta delimitacion no es solo cuestion de estilo: condiciona la interpretacion de los resultados (un buen Dice se reporta dentro de gliomas, no como capacidad general de "detectar cualquier tumor"), las limitaciones declaradas (no generaliza fuera de glioma ni a cerebros sanos), y las posibles lineas de trabajo futuro (extension a otros tipos de tumor, deteccion presencia/ausencia, generalizacion a otros protocolos de adquisicion).

## 7. Limitaciones conocidas del enfoque

Estas limitaciones son metodologicas y deben quedar reflejadas en la memoria final:

- Una sola semilla por arquitectura, salvo decision posterior de repetir el baseline con multiples semillas para acotar varianza.
- Comparacion realizada sobre el split `val`. El split `test` se reserva para una evaluacion final unica.
- nnU-Net se ejecuta como baseline externo, no dentro de la pipeline MONAI propia. Aunque comparte dataset y split, su preprocesado interno y su planificacion automatica difieren del resto. Esta diferencia se documenta como ventaja metodologica de nnU-Net (auto-configuracion) y como caveat para la comparacion directa.
- El presupuesto computacional puede impedir entrenar todas las arquitecturas hasta convergencia plena. Si ocurre, se reporta el numero de pasos efectivos por modelo y se comparan resultados a presupuesto fijo, no a convergencia, declarandolo explicitamente.
