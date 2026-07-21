# 3. Metodología

Este capítulo presenta el enfoque metodológico seguido para desarrollar el trabajo. La metodología
se organiza en cinco fases y describe, a un nivel general, qué actividades se realizaron y cómo se
relacionaron entre sí. El detalle técnico de las decisiones, adaptaciones e implementaciones se
reserva para el Capítulo 4, que reproduce la misma estructura por fases.

## 3.1. Enfoque metodológico

El trabajo no se ha guiado por una metodología estándar de gestión de proyectos, sino por una
**metodología *ad hoc* de carácter incremental**, definida para un proyecto de investigación
experimental en aprendizaje profundo aplicado a imagen médica. Cada fase incorporó comprobaciones
antes de comprometer nuevos recursos de cómputo: primero se verificaron los datos y las particiones;
después, el funcionamiento del *pipeline* y de los modelos; y, finalmente, el protocolo de
entrenamiento, inferencia y evaluación.

La metodología se organiza en **cinco fases**, desde la comprensión del problema hasta el análisis
de los resultados. Aunque existe una secuencia principal, las fases admiten realimentación. Por
ejemplo, los primeros experimentos revelaron limitaciones de entrada/salida y del mecanismo de
compuerta, lo que motivó adaptaciones posteriores del *pipeline* y nuevas variantes de fusión. El
desarrollo técnico de cada fase se recoge en la sección homóloga del Capítulo 4.

## 3.2. Descripción general de las fases

**Fase 1 — Familiarización y revisión del estado del arte.** Comprensión del problema clínico de la
segmentación de gliomas en resonancia magnética multimodal, revisión de arquitecturas relevantes
(U-Net y variantes, Transformers y nnU-Net) y selección justificada del conjunto de datos, del marco
de trabajo y de las familias de modelos. Esta fase fija el alcance y la pregunta de investigación.

**Fase 2 — Análisis y preparación de los datos.** Inventario del conjunto de datos, controles de
calidad para verificar la integridad de los estudios y sus modalidades, y generación de particiones
estratificadas y reproducibles de entrenamiento, validación y test. La partición se definió por
estudio de imagen, no por sujeto. Por ello, los identificadores completos no se repiten entre
particiones, pero un mismo sujeto puede aportar estudios a más de una de ellas; esta circunstancia
se tiene en cuenta al interpretar la generalización.

**Fase 3 — Diseño e implementación del *pipeline*.** Construcción del sistema experimental: entorno
de cómputo, organización del código, preprocesamiento y aumento de datos, formulación del problema
de segmentación, familias de modelos y mecanismos de fusión multimodal. Esta fase incluyó las
adaptaciones necesarias para ejecutar el mismo flujo MONAI con varias arquitecturas y para preparar
nnU-Net como referencia externa.

**Fase 4 — Experimentación.** Entrenamiento de los modelos y ejecución del estudio de ablación de
las estrategias de fusión. La comparación causal se restringe a las cuatro estrategias construidas
sobre la misma Residual U-Net 3D, que comparten datos, arquitectura, optimización y protocolo de
inferencia. Las configuraciones MONAI se repitieron con tres semillas; nnU-Net se ejecutó una sola
vez con su propio protocolo y se empleó como referencia contextual.

**Fase 5 — Evaluación y análisis de resultados.** Inferencia sobre la partición de test, cálculo de
Dice y HD95 por región, análisis de la variabilidad entre semillas y estudio de la huella
computacional con los registros disponibles. La comparación de las estrategias de fusión es la
principal del trabajo; la comparación entre familias de modelos es descriptiva debido a sus
diferencias de entorno, inferencia y entrenamiento.

La Tabla 3 resume las cinco fases y las actividades que delimitan cada una.

**Tabla 3.** Fases de la metodología *ad hoc* y actividades principales de cada una.

| Fase | Denominación | Actividades principales |
| :-: | :-- | :-- |
| 1 | Familiarización y revisión | Problema clínico y estado del arte; selección de datos, herramientas y familias de modelos |
| 2 | Análisis y preparación de datos | Inventario, control de calidad y partición estratificada por estudio |
| 3 | Diseño e implementación del *pipeline* | Entorno, código, transformaciones, modelos y mecanismos de fusión |
| 4 | Experimentación | Protocolo MONAI, ablación controlada de fusión, multi-semilla y referencia nnU-Net |
| 5 | Evaluación y análisis | Inferencia sobre test, métricas por región, variabilidad y huella computacional |

La tabla muestra la separación entre la preparación del sistema y su evaluación: el test no se usa
para seleccionar puntos de control, y la interpretación de los resultados se realiza después de
congelar las configuraciones finales. Esta reserva se aplica a los estudios completos; no equivale a
una separación independiente por sujeto.

## 3.3. Correspondencia entre metodología y desarrollo

El Capítulo 4 dedica una sección al desarrollo técnico de cada fase. La Tabla 4 establece la
correspondencia entre ambos capítulos y sirve como guía de lectura.

**Tabla 4.** Correspondencia entre las fases de la metodología (Capítulo 3) y las secciones de
desarrollo técnico (Capítulo 4).

| Fase (Cap. 3) | Sección de desarrollo (Cap. 4) |
| :-- | :-- |
| Fase 1 — Familiarización y revisión | 4.1. Familiarización y selección de herramientas |
| Fase 2 — Análisis y preparación de datos | 4.2. Análisis y preparación de los datos |
| Fase 3 — Diseño e implementación del *pipeline* | 4.3. Diseño e implementación del *pipeline* |
| Fase 4 — Experimentación | 4.4. Experimentación |
| Fase 5 — Evaluación y análisis | 4.5. Evaluación y análisis de resultados |

Esta correspondencia mantiene en el presente capítulo la descripción metodológica general y
concentra en el siguiente los parámetros, componentes de código y decisiones de ejecución.

## 3.4. Cronograma

El trabajo se desarrolló entre mayo y julio de 2026. La Tabla 5 presenta el cronograma por fases;
dado el carácter incremental de la metodología, algunas actividades se solaparon y los hallazgos de
experimentación motivaron revisiones de implementación.

**Tabla 5.** Cronograma del proyecto por fases y actividades.

| Fase | Actividades | Periodo aproximado |
| :-- | :-- | :-- |
| 1. Familiarización y revisión | Revisión del estado del arte; decisiones de alcance y herramientas; tutorías de encuadre | Mayo 2026 |
| 2. Análisis y preparación de datos | Control de calidad del conjunto; particiones estratificadas reproducibles | Mayo 2026 |
| 3. Diseño e implementación | *Pipeline* MONAI; *factory* de modelos; mecanismos de fusión; adaptación de E/S y de nnU-Net | Mayo – junio 2026 |
| 4. Experimentación | Baselines; Swin-UNETR; nnU-Net; sonda de convergencia; ablación y multi-semilla | Junio – julio 2026 |
| 5. Evaluación y análisis | Inferencia y métricas sobre test; análisis comparativo y redacción de resultados | Julio 2026 |

El solapamiento principal se produjo entre las fases 3 y 4: las pruebas de rendimiento condujeron a
copiar los datos al disco local en la nube, y el diagnóstico de la compuerta original llevó a
incorporar el descriptor media+desviación. El detalle de estas adaptaciones se desarrolla en el
Capítulo 4.
