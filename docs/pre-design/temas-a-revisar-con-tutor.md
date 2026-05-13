# Temas iniciales para revisar con el tutor del TFM

Fecha de preparacion: 2026-05-13

## Contexto analizado

El proyecto parte de una propuesta de TFM sobre segmentacion de tumores cerebrales en resonancia magnetica multimodal usando BraTS 2024, con foco inicial en arquitecturas hibridas Transformer-UNet y una posible contribucion basada en fusion adaptativa de modalidades MRI y aprendizaje contrastivo inter-modal.

La evidencia local disponible indica que el repositorio esta todavia en fase de pre-diseno: contiene documentacion de propuesta, glosario, inventario de ficheros BraTS 2024 y verificacion de correspondencia con el dataset local, pero aun no contiene codigo de preprocesamiento, entrenamiento, evaluacion ni experimentos.

## Decisiones ya tomadas

Estas decisiones se registran con mas detalle en `docs/pre-design/decisiones-iniciales.md`.

- El TFM se centrara en BraTS-GLI 2024.
- Se intentara trabajar con los 5 modelos completos de la propuesta inicial.
- TransBTS se mantiene en alcance aunque su implementacion consuma tiempo.
- Se usaran Google Colab Pro y un Mac M4 Pro como recursos de computo.
- El repositorio actual sera la entrega del TFM.
- El analisis del dataset y de sus caracteristicas formara parte explicita del TFM.
- La memoria citara BraTS de forma obligatoria y respetara la licencia CC-BY-NC 4.0.
- Se recomienda adoptar reproducibilidad practica auditada: splits, seeds, configs, versiones, logs y manifiestos de experimento.

## Estado actual del material

- Propuesta base: segmentacion de gliomas en MRI multimodal con comparacion entre Swin-UNETR, nnU-Net, Attention U-Net, TransBTS y 3D U-Net residual.
- Dataset principal sugerido: BraTS-GLI 2024.
- Datos locales disponibles para BraTS-GLI:
  - Entrenamiento principal: 1350 casos, con `seg`, `t1c`, `t1n`, `t2f`, `t2w`.
  - Entrenamiento adicional: 271 casos, con las mismas 5 modalidades.
  - Validacion publica: 188 casos, con `t1c`, `t1n`, `t2f`, `t2w` y sin mascara `seg` publica.
- Datos locales adicionales: BraTS-MEN-RT con 500 casos de entrenamiento `t1c` + `gtv` y 70 casos de validacion `t1c`, aunque este subconjunto no encaja directamente con el objetivo principal de gliomas multimodales.
- Restricciones ya documentadas: licencia CC-BY-NC 4.0, uso no comercial, citacion obligatoria de BraTS/Synapse y referencias especificas por coleccion.

## Propuesta de agenda para la primera reunion

### 1. Cerrar el alcance clinico y experimental

Decision actual: el TFM se centrara en BraTS-GLI 2024.

Justificacion: BraTS-GLI es el subconjunto que encaja directamente con segmentacion de gliomas en MRI multimodal, contiene las cuatro modalidades relevantes y dispone localmente de casos con mascara `seg` para entrenamiento y evaluacion interna. Otros subconjuntos de BraTS 2024 representan tareas clinicas y etiquetas distintas, por lo que mezclarlos desde el inicio diluiria el diseno experimental.

Preguntas para el tutor:

- Validar que BraTS-GLI sea el unico dataset principal.
- Confirmar si otros subconjuntos deben aparecer solo como contexto/trabajo futuro.
- Que nivel de profundidad clinica se espera: segmentacion tecnica, utilidad clinica o ambas?

Decision operativa: dejar otros subconjuntos como trabajo futuro o analisis de generalizacion solo si se confirma disponibilidad de etiquetas y el diseno principal queda estabilizado.

### 2. Replantear el numero de modelos

Decision actual: se intentara trabajar con los 5 modelos completos de la propuesta inicial.

Riesgo a revisar con el tutor: entrenar y evaluar correctamente cinco arquitecturas 3D puede ser costoso. La decision se mantiene porque no hay una restriccion fuerte de calendario, pero conviene ordenar los experimentos por fases y definir criterios de parada.

Preguntas para el tutor:

- Validar que comparar los 5 modelos completos es adecuado para el TFM.
- Confirmar nnU-Net como baseline fuerte principal.
- Confirmar Swin-UNETR como modelo avanzado de referencia.
- Confirmar el orden de ejecucion experimental para reducir riesgo.

Recomendacion actualizada: mantener los 5 modelos, pero con roles claros: 3D U-Net residual como baseline controlado, Attention U-Net como mejora atencional intermedia, nnU-Net como baseline fuerte principal, Swin-UNETR como referencia Transformer-UNet y TransBTS como arquitectura hibrida especifica de tumores cerebrales.

### 3. Definir una contribucion defendible y acotada

La idea de fusion adaptativa de modalidades y aprendizaje contrastivo inter-modal es interesante, pero puede abrir demasiado el alcance si se implementan ambas de forma completa.

Preguntas para el tutor:

- Que contribucion es mas defendible para el TFM: fusion adaptativa, aprendizaje contrastivo o ambas?
- La contribucion debe ser arquitectonica, metodologica o principalmente experimental?
- Se valora mas superar ligeramente un baseline o demostrar con ablaciones que el modulo aporta robustez?
- Hace falta apuntar a una contribucion tipo Q1 o basta con un trabajo academico solido y reproducible?

Recomendacion inicial: priorizar fusion adaptativa de modalidades como contribucion principal, porque conecta directamente con MRI multimodal y permite hacer ablaciones claras por modalidad. Tratar el aprendizaje contrastivo como extension opcional si el baseline y la pipeline estan estabilizados.

### 4. Fijar protocolo de evaluacion antes de entrenar

El dataset de validacion BraTS-GLI local no contiene mascaras publicas, asi que no sirve directamente para calcular Dice o HD95 localmente salvo mediante plataforma oficial/evaluador externo. Hay que definir un split interno reproducible a partir de los 1350 + 271 casos con `seg`.

Preguntas para el tutor:

- Que particion se aprueba para train/validation/test interno?
- Se debe usar el additional training data dentro del entrenamiento, como test interno separado o como validacion externa?
- Debemos reservar un test hold-out fijo antes de cualquier ajuste?
- Que metricas son obligatorias: Dice, HD95, sensibilidad, precision, volumen tumoral, calibracion?
- Las metricas deben reportarse para ET, TC y WT siguiendo BraTS?

Recomendacion inicial: crear un split interno estratificado y reproducible sobre los 1621 casos con mascara, reservar un hold-out final no tocado, y reportar Dice + HD95 para ET, TC y WT como minimo.

### 5. Validar viabilidad computacional

Decision actual: se usaran Google Colab Pro y un Mac M4 Pro, sin limite estricto de tiempo.

Los modelos 3D con volumes BraTS completos pueden exigir mucha VRAM y tiempo. Con los recursos disponibles, el planteamiento es viable si se usa Colab Pro para entrenamientos principales y el Mac para analisis, preparacion de datos y pruebas pequenas.

Preguntas para el tutor:

- Se permite entrenar con patches 3D en lugar de volumen completo?
- El tutor prefiere algun formato concreto para registrar experimentos y resultados?
- Hay expectativas sobre checkpoints, logs o trazabilidad de ejecuciones?

Recomendacion actualizada: disenar la pipeline con entrenamiento por patches 3D, configuraciones versionadas y experimentos escalables: primero smoke tests en Mac o Colab, luego subset pequeno y finalmente entrenamiento completo en Colab Pro.

### 6. Acordar framework tecnico

Decision actual: el repositorio actual sera la entrega del TFM.

El repositorio aun no contiene codigo. Conviene construir una base tecnica reproducible y compatible con Colab Pro/Mac M4 Pro.

Preguntas para el tutor:

- Se prefiere MONAI por su soporte de imagen medica y modelos como Swin-UNETR?
- Se permite usar nnU-Net como herramienta externa de baseline aunque tenga su propia estructura?
- El tutor acepta una entrega donde nnU-Net no este copiado dentro del repo, pero si documentado y ejecutado mediante scripts/configuracion propia?
- Que nivel de reproducibilidad ejecutable considera suficiente?

Recomendacion actualizada: usar MONAI/PyTorch para la pipeline propia y nnU-Net como baseline externo documentado, manteniendo conversiones, configuraciones, splits, comandos, logs y resultados dentro del repositorio.

### 7. Definir preprocesamiento minimo obligatorio

Decision actual: el analisis del dataset y de sus caracteristicas sera parte explicita del TFM.

BraTS suele venir registrado y normalizado espacialmente, pero el TFM debe documentar y verificar el flujo real antes de entrenar.

Preguntas para el tutor:

- Podemos asumir que BraTS-GLI ya esta co-registrado, remuestreado y con skull-stripping segun el challenge?
- Que normalizacion de intensidad se espera: z-score por modalidad y caso, percentiles, normalizacion solo en region no cero?
- Se exige revision visual o control de calidad automatico de casos?
- Que estadisticas descriptivas de volumen tumoral y etiquetas considera prioritarias?

Recomendacion actualizada: documentar el preprocesamiento oficial asumido, implementar verificaciones automaticas de presencia de modalidades/mascara, shape/affine compatibles, normalizacion z-score por modalidad en voxeles no cero y estadisticas descriptivas por region tumoral.

### 8. Concretar la pregunta de investigacion

La propuesta actual es amplia. Para orientar memoria, experimentos y defensa, conviene formular una pregunta principal medible.

Preguntas para el tutor:

- La pregunta debe formularse como mejora de precision, robustez o interpretabilidad?
- El modulo de fusion debe evaluarse contra concatenacion simple de modalidades?
- Tiene interes analizar rendimiento cuando falta una modalidad o cuando se degrada una modalidad?

Propuesta de formulacion inicial:

> Puede una estrategia de fusion adaptativa de modalidades MRI mejorar la segmentacion 3D de gliomas en BraTS-GLI frente a una fusion por concatenacion estandar, manteniendo un coste computacional asumible y con mejoras consistentes en ET, TC y WT?

### 9. Establecer criterios de exito del TFM

Conviene pactar con el tutor que se considerara un resultado satisfactorio aunque no se supere el estado del arte.

Preguntas para el tutor:

- Cual es el minimo entregable aceptable: pipeline reproducible + baseline, comparativa, o modulo nuevo con ablaciones?
- Que resultados numericos se consideran suficientes?
- Se valorara negativamente si el modulo nuevo no supera a nnU-Net pero esta bien analizado?
- Que peso tendran metodologia, reproducibilidad y analisis critico frente a metrica final?

Recomendacion inicial: fijar tres niveles de exito:

- Minimo: pipeline reproducible con baseline 3D y evaluacion interna BraTS-GLI.
- Objetivo: baseline fuerte + modelo Transformer-UNet + ablacion de fusion de modalidades.
- Ambicioso: robustez ante modalidades degradadas/faltantes o evaluacion externa.

### 10. Revisar implicaciones legales, citacion y publicacion

Decision actual: BraTS se citara obligatoriamente en la memoria.

El dataset tiene licencia no comercial y requisitos de citacion. Esto no bloquea un TFM, pero debe quedar claro en memoria y repositorio.

Preguntas para el tutor:

- El codigo del repositorio sera publico o privado?
- Se pueden publicar scripts, splits y resultados sin redistribuir datos?
- Hay que incluir una seccion especifica de licencia y uso de datos?

Recomendacion inicial: mantener el repositorio sin datos NIfTI, documentar rutas locales y requisitos de acceso, y versionar solo scripts, configs, splits anonimizados por ID de caso si la licencia lo permite, y resultados agregados.

## Decisiones que conviene cerrar en la reunion

| Decision | Opcion recomendada para arrancar | Riesgo si no se decide |
| --- | --- | --- |
| Dataset principal | BraTS-GLI 2024 | Alcance disperso entre tumores y modalidades |
| Subconjuntos adicionales | Solo contexto/trabajo futuro inicialmente | Sobrecarga experimental |
| Modelos experimentales | Intentar los 5 modelos completos por fases | Comparativa demasiado extensa |
| Contribucion principal | Fusion adaptativa de modalidades | Innovacion dificil de evaluar |
| Aprendizaje contrastivo | Extension opcional | Complejidad alta sin garantia de mejora |
| Evaluacion | Split interno con hold-out + Dice/HD95 ET, TC, WT | Resultados no reproducibles o no comparables |
| Framework | MONAI/PyTorch + nnU-Net baseline | Reimplementacion innecesaria |
| Validacion publica BraTS | Usarla solo si hay evaluador/labels disponibles | Confundir validacion sin mascaras con test medible |
| Generalizacion externa | Opcional, no core del TFM | Dependencia de datos/labels no confirmados |

## Propuesta de proximos entregables

1. Documento de alcance aprobado por el tutor con pregunta de investigacion, datasets, modelos y metricas.
2. Script de inventario tecnico de casos BraTS-GLI: modalidades, shapes, affines, etiquetas presentes y estadisticas basicas.
3. Generador de splits reproducibles train/val/test interno.
4. Pipeline minima MONAI para cargar un caso, aplicar transformaciones y entrenar un baseline en subset pequeno.
5. Primer baseline medible antes de implementar la contribucion.
6. Diseno de ablaciones: concatenacion estandar frente a fusion adaptativa, y posiblemente robustez ante modalidad faltante/degradada.

## Material del repositorio usado para esta propuesta

- `docs/specs/propuesta-2-segmentacion-tumores-cerebrales.md`
- `data/brats_2024_dataset_context.md`
- `data/brats_2024_dataset_properties.json`
- `data/brats_2024_file_inventory.csv`
- `data/brats_2024_local_dataset_match.csv`
- `docs/glossary/README.md`
