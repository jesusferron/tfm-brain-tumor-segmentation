# Registro de decisiones iniciales del TFM

Fecha de actualizacion: 2026-05-13

Este documento registra las decisiones ya tomadas durante la fase de pre-diseno. La propuesta de agenda para el tutor se mantiene en `docs/pre-design/temas-a-revisar-con-tutor.md`.

## Decisiones cerradas

### 1. Alcance del dataset

Decision: el TFM se centrara en BraTS-GLI 2024.

Justificacion:

- Es el subconjunto que encaja directamente con el titulo y objetivo del TFM: segmentacion de gliomas en resonancia magnetica multimodal.
- Tiene las cuatro modalidades MRI relevantes (`t1n`, `t1c`, `t2w`, `t2f`) y mascaras `seg` en entrenamiento.
- Localmente hay 1621 casos con mascara si se combinan entrenamiento principal y entrenamiento adicional.
- Permite evaluar regiones BraTS estandar: ET, TC y WT.
- Evita mezclar tareas clinicas distintas. Por ejemplo, BraTS-MEN-RT trabaja meningiomas, `gtv` y principalmente `t1c`, por lo que no es comparable de forma directa con segmentacion multimodal de gliomas.

Uso de otros subconjuntos: BraTS-MEN-RT, BraTS-SSA, BraTS-MET, BraTS-PED y otros se podran mencionar como contexto, limitaciones o trabajo futuro. Solo se incluiran experimentalmente si el diseno principal de BraTS-GLI queda estabilizado.

### 2. Modelos a intentar

Decision: se intentara trabajar con los 5 modelos completos de la propuesta inicial.

Modelos:

- 3D U-Net con bloques residuales.
- Attention U-Net.
- nnU-Net.
- Swin-UNETR.
- TransBTS.

Rol previsto de cada modelo:

- 3D U-Net residual: baseline convolucional controlado, util para entender el rendimiento de una arquitectura local y reproducible dentro del repositorio.
- Attention U-Net: comparativa intermedia para medir si la atencion espacial sobre una U-Net mejora el baseline convolucional.
- nnU-Net: baseline fuerte principal, porque automatiza preprocesamiento, configuracion y entrenamiento segun el dataset, y esta ampliamente aceptado como referencia en segmentacion medica.
- Swin-UNETR: modelo avanzado de referencia, porque representa bien la familia Transformer-UNet que da sentido al titulo del TFM.
- TransBTS: modelo hibrido especifico para segmentacion de tumores cerebrales. Se mantiene en alcance aunque su implementacion consuma tiempo, ya que no hay una restriccion fuerte de calendario.

Riesgo aceptado: entrenar y evaluar 5 modelos 3D completos puede ser costoso. La mitigacion sera ordenar los experimentos por fases: primero pipeline y splits, luego baseline sencillo, despues nnU-Net/Swin-UNETR, y finalmente Attention U-Net/TransBTS si no bloquean el avance.

### 3. Enfoque tecnico

Decision: el repositorio actual sera la entrega del TFM.

Decision recomendada: usar MONAI/PyTorch como base principal de la pipeline propia y usar nnU-Net como baseline externo integrado por scripts, configuracion y documentacion.

Implicacion practica:

- El repositorio debe contener el codigo propio, configuraciones, splits, analisis del dataset, resultados agregados y documentacion.
- No hace falta copiar el codigo fuente de nnU-Net dentro del repositorio.
- Si nnU-Net se usa como herramienta externa, el repositorio debe incluir los scripts de conversion al formato nnU-Net, comandos de ejecucion, version usada, configuracion, folds, rutas esperadas y resultados.

### 4. Entorno de computo

Decision: se usaran Google Colab Pro y un Mac con chip M4 Pro.

Uso recomendado:

- Colab Pro: entrenamientos principales con GPU CUDA, especialmente modelos 3D pesados.
- Mac M4 Pro: analisis exploratorio del dataset, comprobaciones de NIfTI, preparacion de splits, pruebas unitarias, smoke tests y ejecuciones pequenas con CPU/MPS cuando sea viable.

Nota tecnica: el Mac M4 Pro es util para desarrollo local, pero el entorno de referencia para resultados principales deberia ser Colab Pro con GPU, porque la mayoria de pipelines PyTorch/MONAI/nnU-Net para segmentacion 3D estan mas probadas en CUDA.

### 5. Reproducibilidad exigida por el proyecto

Decision: adoptar reproducibilidad practica auditada, no reproducibilidad bit-a-bit.

Nivel objetivo:

- Splits fijos versionados en el repositorio.
- Semillas configuradas en entrenamiento, validacion y generacion de splits.
- Configuraciones por experimento en YAML/JSON.
- Registro de versiones de Python, PyTorch, MONAI, nnU-Net, CUDA/cuDNN cuando aplique, sistema operativo y tipo de GPU/CPU.
- Logs de entrenamiento, metricas agregadas, checkpoints finales y manifiesto por experimento.
- Notebooks o scripts de Colab versionados para poder repetir los entrenamientos principales.
- Scripts locales compatibles con Mac para analisis y pruebas pequenas.

Justificacion: Colab Pro puede asignar GPUs diferentes entre sesiones y el backend MPS de Apple no garantiza resultados numericamente identicos a CUDA. Por eso el objetivo realista es que otro evaluador pueda repetir el protocolo y obtener resultados comparables, aunque no identicos bit a bit.

### 6. Analisis del dataset

Decision: el analisis del dataset sera parte explicita del TFM.

Analisis previsto:

- Verificacion de modalidades por caso.
- Comprobacion de shapes, affines y compatibilidad espacial.
- Distribucion de etiquetas y regiones ET, TC, WT.
- Estadisticas de volumen tumoral.
- Revision de valores de intensidad por modalidad.
- Deteccion de casos atipicos o potencialmente problematicos.
- Resumen de caracteristicas del conjunto de entrenamiento, adicional y validacion.

### 7. Citacion y licencia

Decision: la memoria citara BraTS obligatoriamente.

Implicacion:

- La memoria debe incluir las referencias obligatorias de BraTS-GLI 2024 y la atribucion a Synapse/BraTS.
- El repositorio no debe redistribuir los NIfTI del dataset.
- Se documentaran requisitos de acceso, licencia CC-BY-NC 4.0 y uso no comercial.

## Preguntas que siguen abiertas para el tutor

- Confirmar si la evaluacion con los 5 modelos completos es deseable frente a una comparativa mas pequena pero mas profunda.
- Validar que nnU-Net pueda presentarse como baseline externo, manteniendo el codigo propio separado.
- Confirmar si la contribucion principal sera fusion adaptativa de modalidades, aprendizaje contrastivo o una combinacion por fases.
- Aprobar el protocolo de splits internos y el uso de la validacion publica BraTS solo si existe evaluador o etiquetas accesibles.
- Confirmar metricas obligatorias: Dice y HD95 por ET, TC y WT como minimo.

## Referencias tecnicas consultadas

- MONAI documentation: https://monai.readthedocs.io/en/latest/
- MONAI stable documentation: https://monai.readthedocs.io/
- MONAI Core overview: https://project-monai.github.io/core.html
- MONAI GitHub repository: https://github.com/Project-MONAI/MONAI
- nnU-Net repository and documentation: https://github.com/MIC-DKFZ/nnUNet
- PyTorch MPS backend documentation: https://docs.pytorch.org/docs/stable/notes/mps
