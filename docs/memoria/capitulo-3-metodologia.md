# 3. Metodología

## 3.1. Enfoque metodológico

El trabajo se organizó como una secuencia incremental de verificaciones destinada a evitar
entrenamientos costosos sobre datos o configuraciones aún no validados. Primero se acotaron la
pregunta, el conjunto de datos y los comparadores; después se validaron los 1.621 estudios y se
versionaron las particiones. Las pruebas mínimas posteriores comprobaron la carga de datos, la
propagación hacia delante y la retropropagación, la inferencia y el guardado de puntos de control
antes de ampliar el presupuesto de entrenamiento.

La secuencia no fue lineal. Las primeras ejecuciones revelaron un cuello de botella de
entrada/salida en la nube y escasa variación de los pesos de la compuerta basada en la media en un
diagnóstico sobre volúmenes completos. Estos hallazgos llevaron, respectivamente, a copiar los
NIfTI al disco local en las ejecuciones MONAI sobre A100 y a incorporar un descriptor basado en la
media y la desviación típica. La ruta nnU-Net mantuvo los NIfTI crudos en Drive y generó el
preprocesamiento en almacenamiento local. Por último, una sonda de 25.000 pasos fijó en 15.000 pasos
el presupuesto común de las ejecuciones finales. Solo después de congelar las configuraciones se
generaron las predicciones de test. Esta secuencia constituye la **metodología *ad hoc* de carácter
incremental** aplicada en el proyecto; el Capítulo 4 documenta las decisiones técnicas y los
artefactos asociados.

## 3.2. Descripción general de las fases

**Fase 1 — Familiarización y revisión del estado del arte.** Se delimitó el problema clínico, se
revisaron las familias U-Net, Transformer y nnU-Net y se fijaron BraTS-GLI 2024, MONAI y la ablación
de fusión como núcleo experimental. Las decisiones de alcance quedaron registradas el 18 de mayo de
2026 en la documentación previa al diseño y en la bitácora metodológica.

**Fase 2 — Análisis y preparación de los datos.** Se inventariaron los estudios, se verificaron
modalidades, máscaras y geometría, y se generó el reparto 70/15/15. La fase quedó materializada el
26 de mayo en el resumen de control de calidad —1.621 estudios con estado `ok`— y en un
manifiesto de particiones sin identificadores completos solapados. La unidad de reparto fue el
estudio, no el sujeto; esta decisión limita la interpretación de la generalización.

**Fase 3 — Diseño e implementación del *pipeline*.** Se construyeron la interfaz de línea de
comandos, las transformaciones, el bucle de entrenamiento, la factoría de modelos y los bloques de
fusión. Pruebas breves de extremo a extremo verificaron carga, entrenamiento, validación,
inferencia y puntos de control antes de las ejecuciones largas. nnU-Net se mantuvo en una ruta
externa para conservar su planificación y preprocesamiento propios.

**Fase 4 — Experimentación.** Se ejecutó la ablación de cuatro estrategias sobre una Residual U-Net
común, con tres semillas por estrategia, además de Attention U-Net, Swin-UNETR y una ejecución de
nnU-Net. El diseño reduce las diferencias deliberadas de la ablación al bloque de entrada; las
comparaciones entre familias se consideran descriptivas porque no comparten todo el protocolo.

**Fase 5 — Evaluación y análisis de resultados.** Una vez congeladas las configuraciones, se
generaron predicciones sobre los 243 estudios de test y se calcularon Dice y HD95 para ET, TC y WT.
El fichero `outputs/evaluation/final_all_test.csv`, cerrado el 20 de julio, resume los agregados de
tres ejecuciones para los modelos MONAI y de la ejecución única de nnU-Net; los CSV y JSON
individuales conservan las métricas de cada ejecución, y los registros de entrenamiento aportan la
información computacional disponible.

**Tabla 3.** Fases de la metodología *ad hoc* y actividades principales de cada una.

| Fase | Denominación | Actividades principales |
| :-: | :-- | :-- |
| 1 | Familiarización y revisión | Problema clínico y estado del arte; selección de datos, herramientas y familias de modelos |
| 2 | Análisis y preparación de datos | Inventario, control de calidad y partición estratificada por estudio |
| 3 | Diseño e implementación del *pipeline* | Entorno, código, transformaciones, modelos y mecanismos de fusión |
| 4 | Experimentación | Protocolo MONAI, ablación controlada de fusión, varias semillas y referencia nnU-Net |
| 5 | Evaluación y análisis | Inferencia sobre test, métricas por región, variabilidad y huella computacional |

El paso a la Fase 5 quedó condicionado a congelar las configuraciones finales: el test no intervino
en la selección de puntos de control.

## 3.3. Correspondencia entre metodología y desarrollo

La Tabla 4 conserva la correspondencia entre las fases y su desarrollo técnico.

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

El trabajo se desarrolló entre mayo y julio de 2026. Las fases se solaparon porque los diagnósticos
experimentales obligaron a revisar componentes ya implementados.

**Tabla 5.** Cronograma del proyecto por fases y actividades.

| Fase | Actividades | Periodo aproximado |
| :-- | :-- | :-- |
| 1. Familiarización y revisión | Revisión del estado del arte; decisiones de alcance y herramientas; tutorías de encuadre | Mayo 2026 |
| 2. Análisis y preparación de datos | Control de calidad del conjunto; particiones estratificadas reproducibles | Mayo 2026 |
| 3. Diseño e implementación | *Pipeline* MONAI; factoría de modelos; mecanismos de fusión; adaptación de E/S y de nnU-Net | Mayo-junio 2026 |
| 4. Experimentación | Referencias; Swin-UNETR; nnU-Net; sonda de convergencia; ablación y análisis multisemilla | Junio-julio 2026 |
| 5. Evaluación y análisis | Inferencia y métricas sobre test; análisis comparativo y redacción de resultados | Julio 2026 |

El solapamiento principal se produjo entre las fases 3 y 4. Los hitos registrados que modificaron
el desarrollo fueron el diagnóstico del cuello de botella de lectura el 25 de junio; el descarte de
la caché persistente y la copia de los datos al disco local de Colab el 14 de julio; el diagnóstico
de la compuerta y la incorporación del descriptor basado en la media y la desviación típica el 16
de julio; y la sonda de convergencia que fijó el presupuesto final el 17 de julio. La evaluación
conjunta sobre test se cerró el 20 de julio.
