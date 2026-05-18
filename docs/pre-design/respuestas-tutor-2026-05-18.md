# Respuestas del tutor y decisiones derivadas

Fecha: 2026-05-18

Origen: respuestas del tutor compartidas por el alumno.

Documentos relacionados:

- `docs/pre-design/decisiones-iniciales.md`
- `docs/pre-design/temas-a-revisar-con-tutor.md`
- `docs/specs/propuesta-2-segmentacion-tumores-cerebrales.md`

## Registro trazable

| ID | Tema | Respuesta del tutor | Decision derivada | Estado |
| --- | --- | --- | --- | --- |
| TUT-2026-05-18-01 | Alcance clinico y experimental | Cerrar el alcance clinico y experimental. Dejar otros subconjuntos como trabajo futuro, explicando el porque. | BraTS-GLI 2024 queda como unico dataset nuclear. Otros subconjuntos se mencionan como contexto, limitacion o trabajo futuro por diferencias de tarea clinica, modalidades, etiquetas y protocolo. | Cerrado |
| TUT-2026-05-18-02 | Numero de modelos | Replantear el numero de modelos; los 5 al final. Explicar el porque. | Se mantienen los 5 modelos con roles definidos: baseline controlado, baseline fuerte, Transformer-UNet, variante atencional e hibrido especifico de tumores cerebrales. | Cerrado |
| TUT-2026-05-18-03 | Contribucion | Definir una contribucion defendible y acotada: fusion adaptativa y otra ponderada para comparar valores. Surge la pregunta de si la fusion puede ser generada por una red neuronal para establecer pesos de resultados de diferentes modelos. | La contribucion principal sera fusion adaptativa de modalidades MRI. Se comparara contra concatenacion estandar y fusion ponderada. La fusion neuronal de pesos queda como cuestion tecnica o ablacion avanzada, separando fusion de modalidades de fusion de salidas/modelos. | Parcialmente cerrado |
| TUT-2026-05-18-04 | Evaluacion | Fijar protocolo antes de entrenar: split interno estratificado y reproducible sobre los 1621 casos con mascara, hold-out final no tocado, reportar Dice + HD95 para ET, TC y WT como minimo y explicar el porque. | El protocolo de evaluacion queda definido antes del entrenamiento. Falta concretar porcentaje exacto y variables de estratificacion. | Cerrado con pendiente operativo |
| TUT-2026-05-18-05 | Viabilidad computacional | Disenar pipeline con entrenamiento por patches 3D, configuraciones versionadas y experimentos escalables: smoke tests en Mac o Colab, subset pequeno y entrenamiento completo en Colab Pro. | La pipeline se implementara por fases y cada experimento tendra configuracion versionada, logs y resultados agregados. | Cerrado |
| TUT-2026-05-18-06 | Framework tecnico | MONAI ok, pero se sugiere meter nnU-Net dentro del MONAI si es factible. | MONAI/PyTorch sera la base. Se evaluara la integracion tecnica de nnU-Net dentro del flujo MONAI; si no es razonable, nnU-Net se mantendra como baseline externo reproducible. | Pendiente de viabilidad |
| TUT-2026-05-18-07 | Preprocesamiento | Documentar preprocesamiento oficial asumido, verificaciones automaticas de modalidades/mascara, shape/affine compatibles, normalizacion z-score por modalidad en voxeles no cero y estadisticas descriptivas por region tumoral. | El preprocesamiento minimo obligatorio queda definido y debe implementarse antes de entrenar. | Cerrado |
| TUT-2026-05-18-08 | Pregunta de investigacion | Propuesta OK. | Se adopta la pregunta: puede una estrategia de fusion adaptativa de modalidades MRI mejorar la segmentacion 3D de gliomas en BraTS-GLI frente a concatenacion estandar, con coste computacional asumible y mejoras consistentes en ET, TC y WT. | Cerrado |
| TUT-2026-05-18-09 | Criterios de exito | Objetivo: baseline fuerte + modelo Transformer-UNet + ablacion de fusion de modalidades. | Se fija como objetivo defendible del TFM. | Cerrado |
| TUT-2026-05-18-10 | Legal, citacion y publicacion | Repositorio privado hasta entrega del TFM. Incluir apartado de licencia y no propagar los datos, solo mencionar la fuente. | El repositorio no redistribuira NIfTI ni datos originales. Se documentaran fuente, licencia, acceso y citacion. | Cerrado |

## Consecuencias para los proximos entregables

1. Actualizar el documento de alcance con la pregunta de investigacion aprobada.
2. Implementar inventario automatico y controles de calidad del dataset.
3. Generar splits internos reproducibles con hold-out final.
4. Crear smoke test de pipeline MONAI con patches 3D.
5. Definir baseline de concatenacion, fusion ponderada y fusion adaptativa.
6. Evaluar la viabilidad de integrar nnU-Net en el flujo MONAI.
