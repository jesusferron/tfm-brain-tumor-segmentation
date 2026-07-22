# 6. Conclusiones

Este capítulo sintetiza los principales resultados del trabajo, responde a la pregunta de
investigación formulada en el Capítulo 1, valora el grado de cumplimiento de los objetivos y delimita
el alcance de las conclusiones. Finalmente, presenta las principales limitaciones del estudio y las
líneas de trabajo que se derivan de ellas.

## 6.1. Respuesta a la pregunta de investigación

La pregunta de investigación planteaba si una ponderación explícita y ligera de las modalidades
T1n, T1c, T2w y FLAIR —en particular, una compuerta adaptativa condicionada por la entrada— podía
mejorar de forma consistente la segmentación 3D de ET, TC y WT frente a la concatenación directa,
manteniendo fija la Residual U-Net 3D y un coste computacional asumible.

Los resultados obtenidos no aportan evidencia de una mejora consistente. La concatenación alcanzó
un Dice medio de 0,706 ± 0,005 y la ponderación global estática obtuvo 0,706 ± 0,006. La diferencia
entre ambas medias fue inferior a 0,001 y cambió de signo entre semillas. Por tanto, en las
ejecuciones realizadas no se observó una ventaja sistemática asociada a la ponderación global.

Las dos variantes adaptativas presentaron medias inferiores, de 0,586 ± 0,169 y 0,592 ± 0,171,
debido principalmente a una corrida de bajo rendimiento en cada configuración. Las restantes
corridas obtuvieron valores próximos a los de las estrategias no adaptativas. Con tres repeticiones
por variante no es posible estimar una probabilidad general de fallo, establecer diferencias
estadísticamente significativas ni determinar la causa de esas ejecuciones. Sí puede concluirse que,
dentro del presupuesto evaluado, las variantes adaptativas mostraron una variabilidad entre semillas
mayor que la concatenación y la ponderación global.

El análisis de las compuertas aporta información adicional. Los pesos generados por cada modelo
variaron muy poco entre estudios y mantuvieron una entropía elevada, próxima al máximo correspondiente
a cuatro modalidades. Por tanto, no se produjo una concentración sistemática en una única modalidad.
La escasa variación entre entradas es compatible con que los descriptores globales empleados
proporcionaran una señal limitada para condicionar la fusión. Esta observación, sin embargo, no
demuestra por sí sola la causa del bajo rendimiento de algunas ejecuciones.

Los bloques de fusión fueron ligeros en número de parámetros: añadieron entre 4 y 108 parámetros
respecto a la Residual U-Net con concatenación. En las ejecuciones locales se observaron tiempos de
pared superiores para las variantes ponderadas, aunque las diferencias de carga, entrada/salida y
validación impiden atribuir ese incremento exclusivamente al bloque de fusión. Además, no se
conservaron medidas homogéneas de memoria y tiempo de inferencia para todas las configuraciones. En
consecuencia, puede afirmarse que las estrategias son ligeras desde el punto de vista paramétrico,
pero no establecer una comparación completa de eficiencia computacional.

La respuesta a la pregunta de investigación es, por tanto, negativa dentro de las configuraciones,
el presupuesto y la partición utilizados: no se obtuvo evidencia de que la ponderación adaptativa
ligera evaluada mejore de forma consistente la concatenación directa. Esta conclusión se limita al
mecanismo implementado y al montaje experimental del trabajo, y no supone que cualquier forma de
fusión adaptativa de modalidades deba producir el mismo resultado.

## 6.2. Grado de cumplimiento de los objetivos

El objetivo principal consistía en diseñar, implementar y evaluar un sistema reproducible que
permitiera determinar si la ponderación adaptativa mejoraba la concatenación, considerando el
rendimiento de segmentación y el coste computacional. Este objetivo se alcanzó en su finalidad
experimental: el sistema fue construido, las estrategias se compararon y la pregunta de
investigación pudo responderse. La caracterización del coste quedó limitada por la disponibilidad
incompleta de medidas homogéneas de memoria y tiempo de inferencia.

Respecto a los objetivos específicos, el grado de cumplimiento fue el siguiente:

1. Se construyó un *pipeline* con MONAI que integra la carga y verificación de los volúmenes, la
   transformación de etiquetas, la normalización, el aumento de datos, el entrenamiento, la
   inferencia y la evaluación. Las configuraciones, semillas y particiones quedaron registradas para
   permitir una reproducibilidad práctica del flujo experimental.

2. Se implementó y entrenó una Residual U-Net 3D con concatenación directa de las cuatro modalidades,
   utilizada como referencia común del estudio de fusión.

3. Se diseñó e integró antes del codificador una compuerta adaptativa ligera, condicionada por
   descriptores globales de la entrada. También se evaluó una extensión que incorpora la media y la
   desviación típica por modalidad.

4. Se completó una ablación controlada de cuatro estrategias de fusión sobre la misma Residual U-Net:
   concatenación, ponderación global, compuerta adaptativa basada en la media y compuerta basada en
   media y desviación típica. Estas configuraciones compartieron datos, arquitectura,
   hiperparámetros, presupuesto de entrenamiento y protocolo de inferencia.

5. La evaluación mediante Dice y HD95 para ET, TC y WT se completó para todas las configuraciones.
   También se cuantificaron los parámetros y los tiempos disponibles. Este objetivo se cumplió
   parcialmente en su dimensión computacional, porque no se dispuso de registros homogéneos de
   memoria y tiempo de inferencia para toda la comparación.

6. Los resultados se contextualizaron mediante Attention U-Net, Swin-UNETR y nnU-Net. Esta
   contextualización permitió situar el rendimiento observado, aunque no constituye una ablación
   causal de arquitecturas debido a las diferencias de entorno, inferencia y, en nnU-Net, de
   preprocesamiento y entrenamiento.

El signo negativo del resultado de la fusión adaptativa no implica el incumplimiento del objetivo
principal. El propósito del trabajo era determinar empíricamente si se producía la mejora, no
presuponerla.

En la contextualización arquitectónica, la ordenación descriptiva de las medias observadas fue
nnU-Net, con 0,829; Swin-UNETR, con 0,752 ± 0,017; Attention U-Net, con 0,735 ± 0,006; y la Residual
U-Net con concatenación, con 0,706 ± 0,005. Dentro de la ablación residual, la ponderación global
obtuvo 0,706 ± 0,006 y las compuertas adaptativas, afectadas por una corrida de bajo rendimiento cada
una, 0,586 ± 0,169 y 0,592 ± 0,171. nnU-Net procede de una única corrida del *fold* 0 y de su propio
*pipeline*.
Swin-UNETR obtuvo el mayor promedio entre las configuraciones basadas en MONAI y superó a Attention
U-Net en dos de las tres semillas, mientras que Attention U-Net presentó menor variabilidad. Esta
ordenación no permite afirmar superioridad estadística ni atribuir las diferencias exclusivamente a
la arquitectura.

Tampoco se establece una comparación numérica directa con los resultados oficiales de BraTS-GLI
2024, ya que el reto utiliza una evaluación oculta y métricas *lesion-wise*, mientras que este
trabajo emplea una partición interna y convenciones propias para los casos vacíos.

## 6.3. Interpretación de la contribución

La principal contribución del trabajo es una comparación controlada y reproducible de estrategias
ligeras de fusión multimodal sobre una arquitectura común. Este diseño permite separar el efecto del
mecanismo de fusión de las diferencias atribuibles a la red de segmentación.

La ponderación global aprendió coeficientes próximos a una distribución uniforme y no produjo una
mejora consistente respecto a la concatenación. En las compuertas adaptativas, el diagnóstico
realizado sobre estudios de validación mostró que los pesos variaban muy poco entre entradas y que
no se concentraban de forma sistemática en una única modalidad. Este comportamiento sugiere que los
descriptores globales empleados aportaron una señal limitada para adaptar la fusión a cada entrada,
aunque no permite identificar por sí solo la causa de las corridas de bajo rendimiento.

Desde una perspectiva práctica, la concatenación fue la alternativa más parsimoniosa del estudio,
ya que no requirió parámetros adicionales y presentó, junto con la ponderación global, la menor
variabilidad entre semillas. La evidencia obtenida no justifica añadir las compuertas evaluadas a
esta Residual U-Net bajo el protocolo utilizado. Esta conclusión no debe extrapolarse a mecanismos
de atención espacial, fusión de características intermedias o diseños adaptativos con señales de
condicionamiento diferentes.

La comparación de arquitecturas desempeñó una función contextual. Las cifras describen el
rendimiento obtenido por cada configuración, pero las diferencias de protocolo impiden atribuir la
ordenación observada exclusivamente a la arquitectura. En particular, nnU-Net utilizó su propio
proceso de planificación, preprocesamiento y entrenamiento, por lo que actúa como una referencia
externa y no como parte de una ablación causal.

Otra aportación es la infraestructura reproducible desarrollada para configurar experimentos,
registrar métricas, generar predicciones y comparar resultados. Esta infraestructura facilita la
extensión del estudio a nuevas estrategias de fusión y conserva la trazabilidad entre
configuraciones, puntos de control y resultados.

## 6.4. Limitaciones

Las conclusiones deben interpretarse considerando las siguientes limitaciones:

- **Dominio único.** El estudio se realizó exclusivamente sobre imágenes post-tratamiento de
  BraTS-GLI 2024 con las cuatro modalidades disponibles. No se evaluó la generalización a otras
  instituciones, protocolos de adquisición o dominios clínicos.

- **Partición por estudio.** La partición no se agrupó por sujeto. Aunque los identificadores
  completos de los estudios de test no aparecen en entrenamiento o validación, 205 de los 243
  estudios pertenecen a sujetos con otro estudio en alguna de esas particiones. Esta circunstancia
  no invalida la comparación interna entre estrategias, ya que todas utilizaron la misma partición,
  pero limita la interpretación de las métricas como estimación de la generalización a pacientes
  completamente nuevos.

- **Número de repeticiones.** Las configuraciones basadas en MONAI se evaluaron con tres semillas.
  Este número permite describir la variabilidad observada, pero no realizar estimaciones precisas ni
  contrastes inferenciales sólidos. nnU-Net se evaluó mediante una única corrida del *fold* 0.

- **Presupuesto y selección de puntos de control.** Las configuraciones MONAI utilizaron un
  presupuesto de 15.000 pasos, elegido a partir de una sonda de la configuración de concatenación.
  Este presupuesto no demuestra que cada configuración alcanzara individualmente su mejor punto de
  convergencia. Además, sus puntos de control se seleccionaron mediante un subconjunto fijo de ocho
  lotes de validación, lo que redujo el coste durante el entrenamiento, pero puede introducir ruido
  en la elección del mejor modelo. nnU-Net utilizó 250 épocas y su propio protocolo.

- **Protocolo de evaluación.** La evaluación interna no reproduce exactamente las métricas
  *lesion-wise* ni el protocolo oculto del reto oficial. En HD95, los promedios incluyen valores cero
  cuando predicción y referencia están vacías y excluyen los infinitos cuando solo una lo está, por
  lo que los denominadores finitos varían entre modelos y regiones.

- **Comparación arquitectónica heterogénea.** Las variantes residuales se ejecutaron en MPS,
  Attention U-Net y Swin-UNETR en CUDA, se utilizaron diferentes solapamientos durante la inferencia
  y nnU-Net empleó su propio preprocesamiento y protocolo de entrenamiento. Por ello, la comparación
  global de arquitecturas es descriptiva.

- **Caracterización computacional incompleta.** Aunque se dispone del número de parámetros y de
  varios tiempos de entrenamiento, faltan mediciones homogéneas de memoria máxima y tiempo de
  inferencia para todos los modelos.

- **Alcance de la fusión.** Las estrategias estudiadas actúan únicamente antes del codificador y
  generan pesos globales por modalidad. No se evaluaron mecanismos espaciales, fusiones en niveles
  intermedios, interacciones entre modalidades ni estrategias específicas para modalidades ausentes
  o degradadas.

## 6.5. Líneas de trabajo futuro

Una primera línea consiste en estudiar mecanismos de fusión aplicados a características
intermedias. La atención cruzada entre modalidades o las compuertas con información espacial podrían
capturar relaciones que los descriptores globales evaluados no representan. Estas alternativas
deberían compararse manteniendo fija la red base y definiendo de antemano el protocolo de ablación.

También sería conveniente profundizar en la estabilidad de la optimización. Un estudio posterior
podría ampliar el número de semillas, definir criterios previos para identificar corridas de bajo
rendimiento y analizar conjuntamente las trayectorias de pérdida, los gradientes y la evolución de
los pesos. Las variantes de *warmup*, tasa de aprendizaje específica, regularización de entropía y
temperatura ya se estudiaron preliminarmente con 5.000 pasos; cualquier continuación de esa vía
debería ampliar de forma explícita esa evidencia en lugar de presentar esas intervenciones como no
exploradas.

La evaluación computacional podría completarse mediante un protocolo común que registre tiempo de
entrenamiento e inferencia, memoria máxima, rendimiento por paso y consumo de recursos en el mismo
hardware. Para la comparación arquitectónica también sería útil establecer criterios de parada o
presupuestos adaptados a cada modelo, evitando interpretar un presupuesto fijo como garantía de
convergencia equivalente.

Si el alcance del trabajo se amplía hacia la generalización a pacientes nuevos, esta debería
evaluarse mediante particiones definidas por sujeto desde el inicio del ciclo experimental y, cuando
sea posible, mediante conjuntos externos. Esta ampliación respondería a una pregunta distinta de la
ablación controlada realizada en el presente trabajo y permitiría medir de forma más rigurosa la
capacidad de generalización.

Otras extensiones relevantes son la evaluación ante modalidades ausentes o degradadas y la
repetición de nnU-Net con varios *folds* o ejecuciones para cuantificar su variabilidad. También
podría estudiarse de forma controlada el efecto de ampliar el presupuesto de entrenamiento, el
tamaño de parche o el lote, sin presuponer que el aumento de cómputo eliminará las diferencias
observadas.

En síntesis, el trabajo proporciona un *pipeline* reproducible y una evaluación controlada de varias
estrategias ligeras de fusión multimodal. Bajo el montaje estudiado, las compuertas adaptativas no
ofrecieron una mejora consistente frente a la concatenación y mostraron una variabilidad mayor entre
las ejecuciones realizadas. La concatenación constituye, por tanto, la referencia más parsimoniosa
para este experimento, mientras que el posible valor de mecanismos adaptativos más expresivos queda
abierto para investigaciones posteriores.
