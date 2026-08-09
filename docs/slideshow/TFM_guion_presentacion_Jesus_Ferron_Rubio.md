# Guion de presentación del TFM

**Alumno:** Jesús Ferrón Rubio  
**Duración orientativa total:** 19:20  
**Uso:** documento independiente; el PowerPoint no contiene notas incrustadas.

## Diapositiva 01 · Segmentación de tumores cerebrales en resonancia magnética multimodal

**Tiempo orientativo:** 0:30

- Presentar el trabajo en una frase: segmentación 3D de gliomas con cuatro secuencias de RM.
- Anticipar el foco: comprobar si una fusión adaptativa ligera mejora una concatenación directa bajo un experimento controlado.

## Diapositiva 02 · Cómo se responde a la pregunta del TFM

**Tiempo orientativo:** 0:40

- Situar el trabajo antes de entrar en detalle: cuatro secuencias de RM deben combinarse para segmentar tres regiones tumorales.
- Explicar que la comparación es controlada porque solo cambia el bloque de fusión.
- Anticipar el criterio: una mejora solo se acepta si aparece de forma consistente en varias semillas y en las métricas finales.

## Diapositiva 03 · Delimitar un glioma es una tarea tridimensional y multimodal

**Tiempo orientativo:** 0:55

- Explicar por qué la segmentación no es una clasificación: hay que asignar una región a cada vóxel del volumen.
- Conectar la dificultad clínica con el reto técnico: combinar señales complementarias y conservar detalle espacial.
- Aclarar que el sistema es apoyo a segmentación, no diagnóstico ni cribado.

## Diapositiva 04 · Cuatro secuencias de entrada; tres regiones anidadas de salida

**Tiempo orientativo:** 1:05

- Dar una frase por modalidad y evitar sugerir una correspondencia exclusiva modalidad-región.
- Explicar que las salidas son tres máscaras multietiqueta anidadas: ET dentro de TC y TC dentro de WT.
- Este carácter complementario motiva la pregunta sobre cómo fusionar los canales.

## Diapositiva 05 · ¿Puede una ponderación explícita y ligera de las modalidades mejorar de forma consistente la segmentación 3D frente a la concatenación?

**Tiempo orientativo:** 1:00

- Leer la pregunta de forma pausada y enfatizar dos términos: consistente y manteniendo fija la arquitectura.
- La hipótesis no se evalúa con una única ejecución: consistencia exige varias semillas.

## Diapositiva 06 · Un experimento de ablación: una variable cambia y el resto se congela

**Tiempo orientativo:** 1:15

- Esta es la diapositiva clave para defender causalidad interna: la ablación residual cambia solo el bloque de entrada.
- Las referencias Swin-UNETR, Attention U-Net y nnU-Net se mostrarán después, pero no forman parte de esta ablación controlada.

## Diapositiva 07 · BraTS-GLI 2024: control de calidad y particiones reproducibles

**Tiempo orientativo:** 1:10

- Destacar el control de calidad completo y las proporciones 70/15/15.
- Explicar la estratificación: origen, presencia de ET y volumen de WT.
- No ocultar el principal límite: el identificador disponible permitió separar estudios, pero no agrupar por paciente antes de entrenar.

## Diapositiva 08 · Un flujo común de datos, predicción y evaluación

**Tiempo orientativo:** 1:00

- Recorrer el diagrama de izquierda a derecha: dataset, QC y splits; ruta MONAI y ruta nnU-Net; predicciones; evaluación común.
- Destacar la separación entre predict y evaluate, que permite recalcular métricas sin repetir inferencia.
- La reproducibilidad se apoya en configuraciones YAML, CLI, manifiestos y métricas versionadas.

## Diapositiva 09 · Cuatro estrategias de fusión antes del mismo codificador

**Tiempo orientativo:** 1:30

- Concatenación deja que la primera convolución aprenda filtros distintos, pero no expone un peso interpretable por modalidad.
- La ponderación global aprende cuatro escalares compartidos por todas las entradas.
- Las compuertas calculan estadísticos globales del parche, pasan por un MLP y aplican softmax para reponderar canales.
- No es atención espacial: el peso es constante dentro de cada parche o ventana.

## Diapositiva 10 · Protocolo común: repetir, congelar y medir por región

**Tiempo orientativo:** 1:05

- Explicar el orden para evitar fuga de información: entrenamiento, selección en validación, congelación y test.
- Dice es la métrica principal; HD95 complementa con información de distancia de superficies.
- Las tres semillas permiten ver estabilidad, aunque siguen siendo pocas para inferencia estadística sólida.

## Diapositiva 11 · Resultado central: la fusión adaptativa no mejora de forma consistente

**Tiempo orientativo:** 1:35

- Primero comparar concatenación y ponderación global: ambas alcanzan 0,706 con dispersión pequeña.
- Después mostrar las compuertas: la media baja a alrededor de 0,59 y la variabilidad aumenta mucho.
- El resultado no dice que toda fusión adaptativa falle; dice que estas compuertas ligeras no mejoran de forma consistente bajo este protocolo.

## Diapositiva 12 · La diferencia está en la estabilidad entre semillas

**Tiempo orientativo:** 1:15

- Leer por filas: las variantes estables están en torno a 0,70 en las tres semillas.
- Cada compuerta tiene dos ejecuciones competitivas y una caída a aproximadamente 0,35.
- Ser prudente con el diagnóstico de pesos: fue exploratorio, sobre volúmenes completos y puntos de control preliminares.

## Diapositiva 13 · Corte axial: comparación cualitativa de las segmentaciones

**Tiempo orientativo:** 1:10

- Señalar primero la referencia manual y explicar los colores: ET en rojo, TC en naranja y WT en amarillo.
- Recorrer las predicciones de izquierda a derecha sin convertir un único caso en evidencia general.
- La imagen permite ver que las métricas agregadas esconden diferencias locales en los límites y en la estructura interna del tumor.

## Diapositiva 14 · Corte axial: ejemplo de una ejecución adaptativa de bajo rendimiento

**Tiempo orientativo:** 1:00

- Comparar la referencia con la concatenación: la extensión principal y la distribución interna son visualmente próximas.
- Después señalar la región roja sobredimensionada de la compuerta adaptativa en su ejecución débil.
- Aclarar que esta figura ilustra el tipo de error de esa corrida concreta; la conclusión procede del análisis multisemilla.

## Diapositiva 15 · Contexto arquitectónico: hay margen más allá de la fusión temprana

**Tiempo orientativo:** 1:20

- Presentar esta ordenación como contexto, no como comparación causal de arquitecturas.
- nnU-Net alcanza 0,829 con su pipeline auto-configurado y una única ejecución.
- Swin-UNETR es el mejor modelo MONAI, con 0,752, y da soporte a la dimensión Transformer-UNet del título.
- La brecha sugiere que optimización, capacidad y pipeline importan más que añadir una regla ligera de fusión temprana.

## Diapositiva 16 · Ligereza paramétrica y trazabilidad experimental

**Tiempo orientativo:** 1:00

- Separar ligereza paramétrica de eficiencia completa: el número de parámetros sí está cuantificado; memoria e inferencia no de forma homogénea.
- Los tiempos de pared incorporan I/O y validación, por lo que no son un microbenchmark del bloque.
- La contribución reproducible incluye el pipeline, las particiones, las configuraciones y los artefactos finales.

## Diapositiva 17 · Conclusión, límites y siguiente paso

**Tiempo orientativo:** 1:30

- Responder con precisión: no bajo estas configuraciones, semillas, presupuesto y partición.
- La ponderación global no aporta mejora; las compuertas adaptativas presentan inestabilidad.
- Cerrar con el valor metodológico: repetir cambió la interpretación de una aparente mejora en una semilla.
- Proponer como prioridad futura un split por paciente y validación externa antes de aumentar la complejidad del mecanismo.

## Diapositiva 18 · Gracias

**Tiempo orientativo:** 0:20

- Finalizar y dejar visible la síntesis numérica durante las preguntas.
- Tener preparados los matices sobre split por paciente, métricas, nnU-Net y diagnóstico de la compuerta.
