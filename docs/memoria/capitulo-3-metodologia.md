# 3. Metodología

> Versión reorganizada por **fases** siguiendo el criterio de la tutora: este capítulo describe
> *qué* fases se siguieron y en qué consiste cada una, de forma general; el *cómo* (detalle
> técnico, decisiones e implementación) se desarrolla en el Capítulo 4, con una sección por fase.
> Nota sobre numeración: las tablas siguen una numeración **consecutiva global** en el orden de
> lectura de la memoria; el Capítulo 2 aporta la primera tabla, por lo que las de este capítulo la
> continúan.

## 3.1. Enfoque metodológico

El trabajo no se ha guiado por una metodología estándar de gestión de proyectos, sino por una
**metodología *ad hoc* de carácter incremental**, definida a la medida de un proyecto de
investigación experimental en aprendizaje profundo aplicado a imagen médica. Su rasgo esencial es
que **cada fase valida sus resultados antes de habilitar la siguiente**, de modo que el esfuerzo
de cómputo —el recurso más caro del proyecto— solo se invierte cuando las etapas previas
garantizan que los datos, el protocolo y el código son correctos y reproducibles.

La metodología se organiza en **cinco fases**, que van de la comprensión del problema a la
obtención y el análisis de los resultados. Las fases son en su mayoría secuenciales, pero
admiten realimentación: los hallazgos de la fase experimental, por ejemplo, motivaron ajustes en
la fase de implementación. Este capítulo describe cada fase en términos generales; el desarrollo
técnico de cada una se recoge en la sección homóloga del Capítulo 4 (véase la correspondencia en
la Tabla 4).

## 3.2. Descripción general de las fases

**Fase 1 — Familiarización y revisión del estado del arte.** Comprensión del problema clínico
(segmentación de gliomas en resonancia magnética multimodal), estudio de la literatura sobre
segmentación médica 3D y arquitecturas relevantes (U-Net y variantes, Transformers, nnU-Net), y
selección justificada del conjunto de datos, del marco de trabajo y de las arquitecturas a
comparar. Esta fase fija el alcance y la pregunta de investigación.

**Fase 2 — Análisis y preparación de los datos.** Inventario del conjunto de datos, controles de
calidad para verificar la integridad de los casos y sus modalidades, y generación de particiones
reproducibles de entrenamiento, validación y test. El objetivo es disponer de una base de datos
verificada y de un protocolo de partición trazable antes de entrenar.

**Fase 3 — Diseño e implementación del *pipeline*.** Construcción del sistema experimental: el
entorno de cómputo, la organización del código, el preprocesamiento y aumento de datos, la
formulación del problema de segmentación y la implementación de las arquitecturas y de los
mecanismos de fusión multimodal que constituyen la contribución del trabajo.

**Fase 4 — Experimentación.** Entrenamiento de las distintas arquitecturas y ejecución del
estudio de ablación de las estrategias de fusión, bajo un protocolo común que aísla la variable
de estudio. Incluye la determinación empírica del presupuesto de entrenamiento y la repetición de
los experimentos con varias semillas para estimar su variabilidad.

**Fase 5 — Evaluación y análisis de resultados.** Inferencia sobre el conjunto de test reservado,
cálculo de las métricas de segmentación por región y análisis comparativo de arquitecturas y
estrategias de fusión, del que se derivan las conclusiones del trabajo.

La Tabla 3 resume las cinco fases y sus actividades principales.

**Tabla 3.** Fases de la metodología *ad hoc* y actividades principales de cada una.

| Fase | Denominación | Actividades principales |
| :-: | :-- | :-- |
| 1 | Familiarización y revisión | Estudio del problema clínico y del estado del arte; selección de dataset, framework y arquitecturas |
| 2 | Análisis y preparación de datos | Inventario, control de calidad y particiones estratificadas y reproducibles |
| 3 | Diseño e implementación del *pipeline* | Entorno, código, preprocesamiento, formulación del problema, arquitecturas y fusión multimodal |
| 4 | Experimentación | Entrenamiento de arquitecturas, estudio de ablación de fusión, multi-semilla |
| 5 | Evaluación y análisis | Inferencia sobre test, métricas por región y análisis comparativo |

## 3.3. Correspondencia entre metodología y desarrollo

Siguiendo el criterio de organizar metodología y desarrollo en torno a las mismas fases, el
Capítulo 4 dedica una sección al desarrollo técnico de cada una. La Tabla 4 establece esa
correspondencia y sirve de guía de lectura entre ambos capítulos.

**Tabla 4.** Correspondencia entre las fases de la metodología (Capítulo 3) y las secciones de
desarrollo técnico (Capítulo 4).

| Fase (Cap. 3) | Sección de desarrollo (Cap. 4) |
| :-- | :-- |
| Fase 1 — Familiarización y revisión | 4.1. Familiarización y selección de herramientas |
| Fase 2 — Análisis y preparación de datos | 4.2. Análisis y preparación de los datos |
| Fase 3 — Diseño e implementación del *pipeline* | 4.3. Diseño e implementación del *pipeline* |
| Fase 4 — Experimentación | 4.4. Experimentación |
| Fase 5 — Evaluación y análisis | 4.5. Evaluación y análisis de resultados |

## 3.4. Cronograma

El trabajo se desarrolló entre mayo y julio de 2026. La Tabla 5 presenta el cronograma por
fases; dado el carácter incremental de la metodología, algunas fases se solapan parcialmente
(por ejemplo, la implementación del *pipeline* continuó ajustándose durante la experimentación a
raíz de los hallazgos obtenidos).

**Tabla 5.** Cronograma del proyecto por fases y actividades.

| Fase | Actividades | Periodo aproximado |
| :-- | :-- | :-- |
| 1. Familiarización y revisión | Revisión del estado del arte; decisiones de alcance y herramientas; tutorías de encuadre | Mayo 2026 |
| 2. Análisis y preparación de datos | Control de calidad del dataset; particiones estratificadas reproducibles | Mayo 2026 |
| 3. Diseño e implementación | *Pipeline* MONAI propio; factory de modelos; mecanismos de fusión; optimización de E/S | Mayo – junio 2026 |
| 4. Experimentación | Baselines y ablación de fusión; Swin-UNETR y nnU-Net; sonda de convergencia; multi-semilla | Junio – julio 2026 |
| 5. Evaluación y análisis | Inferencia y métricas sobre test; análisis comparativo; redacción de resultados | Julio 2026 |

El detalle técnico de cada fase —entorno de cómputo, formato de los datos, transformaciones,
arquitecturas, hiperparámetros, protocolo de inferencia y métricas— se desarrolla en el
Capítulo 4.
