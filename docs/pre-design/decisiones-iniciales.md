# Registro de decisiones iniciales del TFM

Fecha de actualizacion: 2026-05-18

Este documento registra las decisiones ya tomadas durante la fase de pre-diseno. La agenda historica revisada con el tutor se mantiene en `docs/pre-design/temas-a-revisar-con-tutor.md`.

Trazabilidad:

- 2026-05-13: registro inicial de decisiones de pre-diseno.
- 2026-05-18: respuestas del tutor incorporadas como decisiones cerradas. Registro fuente: `docs/pre-design/respuestas-tutor-2026-05-18.md`.

## Decisiones cerradas

### 1. Alcance del dataset

Decision: el alcance clinico y experimental del TFM se cierra sobre BraTS-GLI 2024.

Justificacion:

- Es el subconjunto que encaja directamente con el titulo y objetivo del TFM: segmentacion de gliomas en resonancia magnetica multimodal.
- Tiene las cuatro modalidades MRI relevantes (`t1n`, `t1c`, `t2w`, `t2f`) y mascaras `seg` en entrenamiento.
- Localmente hay 1621 casos con mascara si se combinan entrenamiento principal y entrenamiento adicional.
- Permite evaluar regiones BraTS estandar: ET, TC y WT.
- Evita mezclar tareas clinicas distintas. Por ejemplo, BraTS-MEN-RT trabaja meningiomas, `gtv` y principalmente `t1c`, por lo que no es comparable de forma directa con segmentacion multimodal de gliomas.

Uso de otros subconjuntos: BraTS-MEN-RT, BraTS-SSA, BraTS-MET, BraTS-PED y otros se mencionaran como contexto, limitaciones o trabajo futuro, explicando que representan tareas clinicas, modalidades, etiquetas y protocolos distintos. No forman parte del nucleo experimental del TFM.

### 2. Modelos a intentar

Decision: se replantea el numero de modelos y se mantienen los 5 modelos como alcance final, siempre con roles experimentales claros y una ejecucion por fases.

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

Justificacion: los 5 modelos cubren un baseline convolucional controlado, un baseline fuerte aceptado en segmentacion medica, una familia Transformer-UNet alineada con el titulo del TFM, una variante atencional intermedia y una arquitectura hibrida especifica de tumores cerebrales.

Riesgo aceptado: entrenar y evaluar 5 modelos 3D completos puede ser costoso. La mitigacion sera ordenar los experimentos por fases: primero pipeline y splits, luego baseline sencillo, despues nnU-Net/Swin-UNETR, y finalmente Attention U-Net/TransBTS si no bloquean el avance.

### 3. Contribucion principal

Decision: la contribucion defendible y acotada sera una estrategia de fusion adaptativa de modalidades MRI, comparada contra concatenacion estandar y contra una fusion ponderada.

Pregunta de investigacion aprobada:

> Puede una estrategia de fusion adaptativa de modalidades MRI mejorar la segmentacion 3D de gliomas en BraTS-GLI frente a una fusion por concatenacion estandar, manteniendo un coste computacional asumible y con mejoras consistentes en ET, TC y WT?

Implicacion experimental:

- La concatenacion de modalidades sera el baseline de fusion estandar.
- La fusion ponderada servira como comparador controlado para separar el efecto de asignar pesos de la complejidad de un modulo adaptativo.
- La fusion adaptativa sera la contribucion principal y debera evaluarse mediante ablaciones.
- El aprendizaje contrastivo inter-modal deja de ser nucleo del TFM y queda como extension opcional o trabajo futuro.

Cuestion tecnica abierta: estudiar si una red neuronal puede generar los pesos de fusion a partir de las modalidades o de las salidas de diferentes modelos. Esta idea debe separarse explicitamente de la contribucion principal si se convierte en una fusion de predicciones tipo ensemble.

### 4. Enfoque tecnico

Decision: el repositorio actual sera la entrega del TFM.

Decision tecnica: usar MONAI/PyTorch como base principal de la pipeline propia. nnU-Net se mantiene como baseline fuerte; se estudiara integrarlo dentro del flujo tecnico basado en MONAI si es factible y, si no lo es, se ejecutara como herramienta externa documentada.

Implicacion practica:

- El repositorio debe contener el codigo propio, configuraciones, splits, analisis del dataset, resultados agregados y documentacion.
- No hace falta copiar el codigo fuente de nnU-Net dentro del repositorio.
- Si nnU-Net se usa como herramienta externa, el repositorio debe incluir los scripts de conversion al formato nnU-Net, comandos de ejecucion, version usada, configuracion, folds, rutas esperadas y resultados.
- Si se integra con MONAI, la integracion debe quedar justificada, versionada y reproducible sin modificar el objetivo experimental.

### 5. Entorno de computo

Decision: se usaran Google Colab Pro y un Mac con chip M4 Pro.

Uso recomendado:

- Colab Pro: entrenamientos principales con GPU CUDA, especialmente modelos 3D pesados.
- Mac M4 Pro: analisis exploratorio del dataset, comprobaciones de NIfTI, preparacion de splits, pruebas unitarias, smoke tests y ejecuciones pequenas con CPU/MPS cuando sea viable.

Nota tecnica: el Mac M4 Pro es util para desarrollo local, pero el entorno de referencia para resultados principales deberia ser Colab Pro con GPU, porque la mayoria de pipelines PyTorch/MONAI/nnU-Net para segmentacion 3D estan mas probadas en CUDA.

### 6. Protocolo de evaluacion

Decision: fijar el protocolo de evaluacion antes de entrenar.

Protocolo minimo:

- Crear un split interno estratificado y reproducible sobre los 1621 casos con mascara.
- Reservar un hold-out final no tocado para evaluacion final.
- Versionar los IDs de train/validation/test y la semilla de generacion.
- No usar la validacion publica BraTS-GLI como test medible local si no hay mascaras o evaluador oficial disponible.
- Reportar como minimo Dice y HD95 para ET, TC y WT.

Justificacion: ET, TC y WT son las regiones BraTS estandar y permiten comparar el comportamiento del modelo en realce tumoral, nucleo tumoral y tumor completo. Dice mide solapamiento volumetrico y HD95 aporta sensibilidad a errores de frontera sin depender tanto de outliers extremos como Hausdorff maximo.

Pendiente operativo: definir el porcentaje exacto train/validation/test y las variables de estratificacion antes de generar los splits versionados.

### 7. Viabilidad computacional

Decision: disenar la pipeline para entrenamiento por patches 3D, configuraciones versionadas y experimentos escalables.

Escalado experimental:

- Fase 1: smoke tests en Mac o Colab para validar carga de datos, transforms, forward/backward y metricas.
- Fase 2: entrenamiento en subset pequeno para estimar memoria, tiempo y estabilidad.
- Fase 3: entrenamiento completo en Colab Pro con GPU.

Implicacion: cada experimento debe tener configuracion versionada, semilla, entorno de ejecucion, logs y resultados agregados.

### 8. Reproducibilidad exigida por el proyecto

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

### 9. Analisis y preprocesamiento del dataset

Decision: el analisis del dataset sera parte explicita del TFM.

Analisis previsto:

- Verificacion de modalidades por caso.
- Comprobacion de shapes, affines y compatibilidad espacial.
- Distribucion de etiquetas y regiones ET, TC, WT.
- Estadisticas de volumen tumoral.
- Revision de valores de intensidad por modalidad.
- Deteccion de casos atipicos o potencialmente problematicos.
- Resumen de caracteristicas del conjunto de entrenamiento, adicional y validacion.

Preprocesamiento minimo obligatorio:

- Documentar el preprocesamiento oficial asumido de BraTS-GLI.
- Verificar automaticamente presencia de modalidades y mascara cuando aplique.
- Verificar compatibilidad de shape y affine entre modalidades y mascara.
- Aplicar normalizacion z-score por modalidad en voxeles no cero.
- Generar estadisticas descriptivas por region tumoral.

### 10. Criterios de exito

Decision: el objetivo defendible del TFM es entregar baseline fuerte, modelo Transformer-UNet y ablacion de fusion de modalidades.

Niveles de exito:

- Minimo: pipeline reproducible con baseline 3D y evaluacion interna BraTS-GLI.
- Objetivo: baseline fuerte + modelo Transformer-UNet + ablacion de fusion de modalidades.
- Ambicioso: analisis de robustez ante modalidades degradadas/faltantes o fusion neuronal de salidas/modelos, solo si el nucleo experimental queda estabilizado.

### 11. Citacion, licencia y publicacion

Decision: la memoria citara BraTS obligatoriamente.

Implicacion:

- La memoria debe incluir las referencias obligatorias de BraTS-GLI 2024 y la atribucion a Synapse/BraTS.
- El repositorio no debe redistribuir los NIfTI del dataset.
- Se documentaran requisitos de acceso, licencia CC-BY-NC 4.0 y uso no comercial.
- El repositorio permanecera privado hasta la entrega del TFM.
- Solo se publicaran codigo, configuraciones, scripts, splits permitidos y resultados agregados; los datos se mencionaran mediante fuente y requisitos de acceso.

## Cuestiones tecnicas pendientes

- Definir el porcentaje exacto del split interno y los criterios de estratificacion.
- Evaluar si la integracion de nnU-Net dentro del flujo MONAI es tecnicamente razonable o si conviene mantenerlo como baseline externo reproducible.
- Concretar si la fusion ponderada sera por modalidad, por region tumoral o por salida de modelo.
- Decidir si la idea de una red neuronal que genere pesos de fusion entra como ablacion avanzada o queda como trabajo futuro.

## Referencias tecnicas consultadas

- MONAI documentation: https://monai.readthedocs.io/en/latest/
- MONAI stable documentation: https://monai.readthedocs.io/
- MONAI Core overview: https://project-monai.github.io/core.html
- MONAI GitHub repository: https://github.com/Project-MONAI/MONAI
- nnU-Net repository and documentation: https://github.com/MIC-DKFZ/nnUNet
- PyTorch MPS backend documentation: https://docs.pytorch.org/docs/stable/notes/mps
