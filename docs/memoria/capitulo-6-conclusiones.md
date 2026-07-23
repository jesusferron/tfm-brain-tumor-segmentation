# 6. Conclusiones

## 6.1. Respuesta a la pregunta de investigación

Bajo el protocolo evaluado, las compuertas ligeras no mejoraron de forma consistente la
concatenación: dos de las tres ejecuciones de cada variante fueron comparables al control, pero una
ejecución de cada una presentó un rendimiento muy inferior. La ponderación global aprendida e
independiente de la entrada tampoco mostró una ventaja sistemática; su Dice medio (0,706 ± 0,006)
fue prácticamente igual al de la concatenación (0,706 ± 0,005).

Los registros de validación muestran que las dos ejecuciones débiles permanecieron alejadas de las
demás durante el entrenamiento, no solo al final. En un diagnóstico exploratorio de ejecuciones
preliminares, las compuertas aplicadas a 40 volúmenes completos produjeron pesos con muy poca
variación entre estudios y entropía elevada, sin concentración extrema en una modalidad. Como el
modelo calcula los pesos sobre parches durante el entrenamiento y sobre ventanas durante la
inferencia, el diagnóstico no caracteriza su variación operativa, no se extiende a los puntos de
control finales ni permite identificar la causa de las ejecuciones débiles.

Los mecanismos añadieron entre 4 y 108 parámetros. En MPS, sus tiempos de pared fueron
aproximadamente un 13–21 % superiores a los de concatenación, pero el registro no separa el coste
del bloque de las variaciones de carga, entrada/salida y validación. Tampoco se conservaron medidas
homogéneas de memoria y tiempo de inferencia para todas las configuraciones. Por ello, la ligereza
paramétrica sí quedó cuantificada, mientras que la eficiencia computacional completa no.

La respuesta es negativa dentro de las configuraciones, las tres semillas, el presupuesto de
15.000 pasos y la partición por estudio utilizados. No se extiende a mecanismos espaciales, fusiones
intermedias ni otras señales de condicionamiento, y tampoco establece una tasa general de fallo de
las compuertas.

## 6.2. Grado de cumplimiento de los objetivos

El objetivo principal consistía en diseñar, implementar y evaluar un sistema reproducible que
permitiera determinar si la ponderación adaptativa mejoraba la concatenación, considerando el
rendimiento de segmentación y el coste computacional. Este objetivo se alcanzó en su finalidad
experimental; la dimensión computacional quedó parcialmente caracterizada. La correspondencia entre
cada objetivo, su evidencia y su límite es la siguiente:

1. **Flujo MONAI.** Los módulos de `tfm_brats/`, las configuraciones YAML y las particiones
   versionadas documentan su implementación. Las dependencias del protocolo no quedaron congeladas
   con versiones exactas.
2. **Referencia residual.** `configs/model/residual_unet_3d.yaml` y tres ejecuciones finales
   documentan el modelo común. La selección del punto de control utilizó ocho lotes de validación.
3. **Fusión adaptativa.** Las configuraciones
   `configs/model/residual_unet_3d_adaptive_gating.yaml` y
   `configs/model/residual_unet_3d_adaptive_gating_meanstd.yaml` documentan las dos compuertas. Solo
   se estudiaron pesos globales antes del codificador.
4. **Ablación de fusión.** Doce entrenamientos, la Tabla 12 y
   `outputs/evaluation/final_all_test.csv` registran la comparación. Tres semillas no permiten una
   inferencia estadística sólida.
5. **Segmentación y coste.** Las Tablas 13–14 recogen Dice y HD95, y la Tabla 15, parámetros y
   tiempos. Faltan memoria y tiempo de inferencia homogéneos.
6. **Contextualización.** La Tabla 13 incluye Attention U-Net, Swin-UNETR y nnU-Net. Las diferencias
   de protocolo impiden tratar esa ordenación como una ablación arquitectónica.

El resultado negativo de las compuertas no altera el cumplimiento experimental: el objetivo era
comprobar la hipótesis, no presuponer su confirmación. Tampoco se comparan estas cifras directamente
con la evaluación oficial de BraTS-GLI 2024, que utiliza datos ocultos y métricas *lesion-wise*
distintas de las convenciones internas del trabajo.

## 6.3. Interpretación de la contribución

El trabajo aporta una ablación de cuatro reglas tempranas de fusión sobre una Residual U-Net común,
con tres semillas por regla, y un diagnóstico exploratorio de las compuertas preliminares sobre 40
estudios de validación. Las configuraciones, el evaluador común y las métricas agregadas permiten
rastrear la comparación hasta las Tablas 12–15. El script `scripts/diagnose_adaptive_gating.py`
permite repetir el procedimiento si se recuperan los datos y los puntos de control externos.

El diseño redujo las diferencias deliberadas de la ablación al bloque de fusión, de modo que sus
resultados pueden interpretarse dentro de la variabilidad observada entre semillas. No garantiza un
aislamiento causal perfecto: la optimización es estocástica y la selección del punto de control se
apoyó en un subconjunto de validación.

El resultado negativo también es informativo. La ponderación global permaneció próxima a una
distribución uniforme. En los 40 volúmenes completos del diagnóstico preliminar, las compuertas
también mostraron poca variación entre estudios, aunque esa prueba no registró los pesos sobre los
parches y ventanas empleados por el modelo final. En términos prácticos, la evidencia no justifica
añadir estas compuertas a la Residual U-Net bajo el protocolo evaluado; la concatenación no añadió
parámetros a la red base y, junto con la ponderación global, mostró la menor variabilidad.

Attention U-Net, Swin-UNETR y nnU-Net sitúan numéricamente la ablación, pero no forman parte de esta
ablación controlada porque difieren en entorno o protocolo. La infraestructura desarrollada
conserva configuraciones, particiones y resultados ligeros y permite extender el mismo esquema
experimental a otras reglas de fusión.

## 6.4. Limitaciones

La limitación de mayor impacto afecta a la generalización por sujeto; las restantes acotan la
precisión estadística, la comparabilidad y el alcance técnico:

- **Principal limitación: partición por estudio.** La partición no se agrupó por sujeto. Aunque los
  identificadores completos de los estudios de test no aparecen en entrenamiento o validación, 205
  de los 243 pertenecen a sujetos con otro estudio en alguna de esas particiones. La comparación
  interna conserva valor porque todas las estrategias comparten el reparto, pero las métricas no
  constituyen una estimación independiente de generalización a pacientes completamente nuevos.

- **Validez externa: dominio único.** Solo se utilizaron imágenes post-tratamiento de BraTS-GLI 2024
  con las cuatro modalidades disponibles. No se midió la generalización a otras instituciones,
  protocolos de adquisición o dominios clínicos.

- **Precisión estadística.** Las configuraciones MONAI se evaluaron con tres semillas. Este número
  describe la variabilidad observada, pero no permite estimaciones precisas ni contrastes
  inferenciales sólidos. nnU-Net se evaluó mediante una única ejecución del *fold* 0.

- **Presupuesto y selección de puntos de control.** Las configuraciones MONAI utilizaron 15.000
  pasos, elegidos a partir de una sonda de concatenación. Ese presupuesto no demuestra que cada
  configuración alcanzara individualmente su mejor punto de convergencia. Los puntos de control se
  seleccionaron con un subconjunto fijo de ocho lotes de validación, lo que puede introducir ruido
  en la elección. nnU-Net utilizó 250 épocas y su propio protocolo.

- **Comparación arquitectónica heterogénea.** Las variantes residuales se ejecutaron en MPS;
  Attention U-Net y Swin-UNETR, en CUDA. También variaron el solapamiento de inferencia y, para
  nnU-Net, el preprocesamiento y el entrenamiento. La comparación global es, por ello, descriptiva.

- **Protocolo de evaluación.** La evaluación interna no reproduce las métricas *lesion-wise* ni el
  protocolo oculto del reto. En HD95 se incluyen ceros cuando predicción y referencia están vacías y
  se excluyen infinitos cuando solo una lo está; los denominadores finitos varían entre modelos y
  regiones.

- **Caracterización computacional incompleta.** Se conservaron los parámetros y varios tiempos de
  entrenamiento, pero no medidas homogéneas de memoria máxima y tiempo de inferencia para todos los
  modelos.

- **Trazabilidad parcial de artefactos.** Los puntos de control, los registros de entrenamiento y
  parte de las métricas por estudio de las ejecuciones A100 no están versionados. Las métricas
  agregadas permiten comprobar las tablas, pero no reconstruir todos los análisis desde un clon
  limpio sin recuperar los artefactos externos.

- **Alcance técnico de la fusión.** Las reglas actúan antes del codificador y generan pesos globales
  por modalidad. No se evaluaron mecanismos espaciales, fusiones intermedias, interacciones entre
  modalidades ni estrategias para modalidades ausentes o degradadas.

## 6.5. Líneas de trabajo futuro

La prioridad debería ser repetir la ablación con una partición definida por sujeto desde el inicio y
con más semillas. Esta decisión aborda primero la limitación de mayor impacto: comprobar si la
ordenación observada se mantiene cuando cada paciente aparece en una sola partición. El subconjunto
*post hoc* de 38 estudios no sustituye ese experimento, y un conjunto externo permitiría ampliarlo a
otros centros o protocolos.

Una segunda prioridad, centrada en el mecanismo, sería instrumentar primero las compuertas para
registrar los pesos sobre los parches de entrenamiento y las ventanas de inferencia. Después podría
compararse una señal espacial o basada en características intermedias manteniendo fija la Residual
U-Net. El protocolo debería definir de antemano las variantes, el criterio para identificar
ejecuciones débiles y el análisis de pesos.

El estudio de estabilidad debería aumentar las semillas y analizar conjuntamente pérdidas,
gradientes, métricas de validación y evolución de los pesos. Las variantes de *warmup*, tasa de
aprendizaje específica, regularización de entropía y temperatura ya se exploraron con 5.000 pasos;
una continuación tendría que ampliar esa evidencia en lugar de tratarlas como opciones no probadas.

Después podría completarse la evaluación computacional en un hardware común, registrando tiempo de
entrenamiento e inferencia, memoria máxima y rendimiento por paso. Quedan como extensiones
posteriores las modalidades ausentes o degradadas, varios *folds* de nnU-Net y ablaciones del
presupuesto, el parche y el lote, sin asumir que más cómputo eliminará las diferencias.

El aprendizaje central es que añadir un mecanismo condicionado por la entrada no garantiza una
mejora: en este estudio se asoció con una mayor variabilidad observada entre las semillas
ejecutadas, y la instrumentación disponible no permitió explicar la causa.
