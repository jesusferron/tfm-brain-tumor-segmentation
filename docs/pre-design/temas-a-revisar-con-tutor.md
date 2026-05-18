# Temas revisados con el tutor del TFM

Fecha de preparacion: 2026-05-13
Fecha de revision con tutor: 2026-05-18

Estado: documento actualizado tras la revision con el tutor. Las decisiones vigentes estan consolidadas en `docs/pre-design/decisiones-iniciales.md` y la trazabilidad detallada de las respuestas se mantiene en `docs/pre-design/respuestas-tutor-2026-05-18.md`.

## Contexto analizado

El proyecto parte de una propuesta de TFM sobre segmentacion de tumores cerebrales en resonancia magnetica multimodal usando BraTS 2024, con foco en arquitecturas hibridas Transformer-UNet y una contribucion basada en fusion adaptativa de modalidades MRI.

La evidencia local disponible indica que el repositorio esta todavia en fase de pre-diseno: contiene documentacion de propuesta, glosario, inventario de ficheros BraTS 2024 y verificacion de correspondencia con el dataset local, pero aun no contiene codigo de preprocesamiento, entrenamiento, evaluacion ni experimentos.

## Estado actual del material

- Propuesta base: segmentacion de gliomas en MRI multimodal con comparacion entre Swin-UNETR, nnU-Net, Attention U-Net, TransBTS y 3D U-Net residual.
- Dataset principal: BraTS-GLI 2024.
- Datos locales disponibles para BraTS-GLI:
  - Entrenamiento principal: 1350 casos, con `seg`, `t1c`, `t1n`, `t2f`, `t2w`.
  - Entrenamiento adicional: 271 casos, con las mismas 5 modalidades.
  - Validacion publica: 188 casos, con `t1c`, `t1n`, `t2f`, `t2w` y sin mascara `seg` publica.
- Datos locales adicionales: BraTS-MEN-RT con 500 casos de entrenamiento `t1c` + `gtv` y 70 casos de validacion `t1c`. Este subconjunto no forma parte del nucleo experimental porque representa otra tarea clinica y otro esquema de etiquetas.
- Restricciones documentadas: licencia CC-BY-NC 4.0, uso no comercial, citacion obligatoria de BraTS/Synapse y no redistribucion de datos NIfTI.

## Decisiones tras la revision

### 1. Alcance clinico y experimental

Decision: cerrar el alcance clinico y experimental sobre BraTS-GLI 2024.

Justificacion: BraTS-GLI es el subconjunto que encaja directamente con segmentacion de gliomas en MRI multimodal, contiene las cuatro modalidades relevantes y dispone localmente de 1621 casos con mascara `seg` para entrenamiento y evaluacion interna.

Otros subconjuntos BraTS se dejaran como contexto, limitaciones o trabajo futuro. La razon debe explicarse en la memoria: tienen tareas clinicas, modalidades, etiquetas o protocolos distintos, por lo que mezclarlos en el nucleo experimental diluiria la comparabilidad.

### 2. Numero de modelos

Decision: mantener los 5 modelos al final, pero con roles experimentales claros y ejecucion por fases.

Modelos previstos:

- 3D U-Net con bloques residuales: baseline convolucional controlado.
- Attention U-Net: variante intermedia para medir el efecto de atencion espacial.
- nnU-Net: baseline fuerte principal.
- Swin-UNETR: modelo Transformer-UNet alineado con el titulo del TFM.
- TransBTS: arquitectura hibrida especifica para segmentacion de tumores cerebrales.

Justificacion: los cinco modelos cubren una progresion defendible desde baseline propio hasta baseline fuerte y modelos hibridos/Transformer. El riesgo computacional se controla ejecutando primero pipeline, splits y baseline sencillo, despues nnU-Net/Swin-UNETR y finalmente Attention U-Net/TransBTS si no bloquean el avance.

### 3. Contribucion defendible y acotada

Decision: la contribucion principal sera una estrategia de fusion adaptativa de modalidades MRI.

Comparadores minimos:

- Concatenacion estandar de modalidades.
- Fusion ponderada para comparar pesos/valores de modalidades.
- Fusion adaptativa como propuesta principal.

La idea de que una red neuronal genere pesos de fusion queda como cuestion tecnica pendiente. Debe distinguirse entre dos posibilidades:

- Fusion de modalidades: pesos aplicados a `t1n`, `t1c`, `t2w`, `t2f` dentro del modelo.
- Fusion de salidas/modelos: pesos aplicados a predicciones de distintos modelos, mas cercano a un ensemble.

El aprendizaje contrastivo inter-modal deja de ser nucleo del TFM y queda como extension opcional o trabajo futuro.

### 4. Protocolo de evaluacion

Decision: fijar el protocolo de evaluacion antes de entrenar.

Protocolo aprobado:

- Crear un split interno estratificado y reproducible sobre los 1621 casos con mascara.
- Reservar un hold-out final no tocado.
- Versionar IDs de train/validation/test y semilla de generacion.
- Reportar como minimo Dice y HD95 para ET, TC y WT.
- No tratar la validacion publica BraTS-GLI como test local medible si no hay mascaras o evaluador oficial disponible.

Justificacion de metricas: Dice mide solapamiento volumetrico y HD95 mide error de frontera reduciendo la sensibilidad a outliers extremos. ET, TC y WT son las regiones BraTS estandar y permiten comparar comportamiento en tumor realzante, nucleo tumoral y tumor completo.

Pendiente operativo: definir porcentaje exacto train/validation/test y variables de estratificacion.

### 5. Viabilidad computacional

Decision: disenar la pipeline con entrenamiento por patches 3D, configuraciones versionadas y experimentos escalables.

Secuencia de ejecucion:

1. Smoke tests en Mac o Colab para validar carga de datos, transforms, forward/backward y metricas.
2. Entrenamiento en subset pequeno para estimar memoria, tiempo y estabilidad.
3. Entrenamiento completo en Colab Pro con GPU.

Cada experimento debe registrar configuracion, semilla, entorno, logs, checkpoints relevantes y metricas agregadas.

### 6. Framework tecnico

Decision: MONAI/PyTorch queda aprobado como base tecnica.

nnU-Net se mantiene como baseline fuerte. El tutor sugiere estudiar si puede integrarse dentro del flujo MONAI al ser open source. Si la integracion no es razonable, se mantendra como baseline externo reproducible, documentando version, conversion de datos, comandos, folds, rutas y resultados.

Pendiente tecnico: evaluar la viabilidad real de integrar nnU-Net dentro del flujo MONAI sin convertirlo en un desvio de alcance.

### 7. Preprocesamiento minimo obligatorio

Decision: documentar el preprocesamiento oficial asumido de BraTS-GLI e implementar controles automaticos antes de entrenar.

Minimos obligatorios:

- Verificar presencia de modalidades y mascara cuando aplique.
- Verificar compatibilidad de shape y affine entre modalidades y mascara.
- Aplicar normalizacion z-score por modalidad en voxeles no cero.
- Calcular estadisticas descriptivas por region tumoral.
- Registrar casos atipicos o potencialmente problematicos.

### 8. Pregunta de investigacion

Decision: la formulacion propuesta queda aprobada.

Pregunta:

> Puede una estrategia de fusion adaptativa de modalidades MRI mejorar la segmentacion 3D de gliomas en BraTS-GLI frente a una fusion por concatenacion estandar, manteniendo un coste computacional asumible y con mejoras consistentes en ET, TC y WT?

Esta pregunta debe orientar memoria, experimentos, ablation studies y defensa.

### 9. Criterios de exito

Decision: el objetivo defendible del TFM es baseline fuerte + modelo Transformer-UNet + ablacion de fusion de modalidades.

Niveles de exito:

- Minimo: pipeline reproducible con baseline 3D y evaluacion interna BraTS-GLI.
- Objetivo: baseline fuerte + modelo Transformer-UNet + ablacion de fusion de modalidades.
- Ambicioso: robustez ante modalidades degradadas/faltantes o fusion neuronal de salidas/modelos, solo si el nucleo experimental queda estabilizado.

### 10. Legal, citacion y publicacion

Decision: mantener el repositorio privado hasta la entrega del TFM.

Implicaciones:

- Incluir apartado especifico de licencia, citacion y uso de datos.
- No propagar ni redistribuir los datos NIfTI.
- Mencionar la fuente oficial y requisitos de acceso.
- Versionar codigo, configuraciones, scripts, resultados agregados y splits solo si su publicacion respeta las condiciones del dataset.

## Pendientes tecnicos

| Pendiente | Decision necesaria | Momento recomendado |
| --- | --- | --- |
| Split interno | Porcentaje train/validation/test y variables de estratificacion | Antes de cualquier entrenamiento |
| Fusion ponderada | Pesos por modalidad, por region tumoral o por salida de modelo | Antes de implementar ablaciones |
| Fusion neuronal | Ablacion avanzada o trabajo futuro | Tras baseline y fusion adaptativa minima |
| nnU-Net + MONAI | Integracion tecnica o baseline externo documentado | Antes del primer baseline fuerte |
| Validacion publica BraTS | Uso solo con evaluador oficial o etiquetas disponibles | Antes de reportar resultados finales |

## Proximos entregables

1. Documento de alcance final con pregunta de investigacion, dataset, modelos, metricas y criterios de exito.
2. Script de inventario tecnico de casos BraTS-GLI: modalidades, shapes, affines, etiquetas presentes y estadisticas basicas.
3. Generador de splits reproducibles train/validation/test con hold-out final.
4. Pipeline minima MONAI con carga de caso, transforms, patches 3D y smoke test.
5. Primer baseline medible en subset pequeno.
6. Diseno experimental de ablaciones: concatenacion estandar, fusion ponderada y fusion adaptativa.
7. Evaluacion tecnica de viabilidad para integrar nnU-Net dentro del flujo MONAI.

## Material del repositorio usado

- `docs/specs/propuesta-2-segmentacion-tumores-cerebrales.md`
- `docs/pre-design/decisiones-iniciales.md`
- `docs/pre-design/respuestas-tutor-2026-05-18.md`
- `data/brats_2024_dataset_context.md`
- `data/brats_2024_dataset_properties.json`
- `data/brats_2024_file_inventory.csv`
- `data/brats_2024_local_dataset_match.csv`
- `docs/glossary/README.md`
