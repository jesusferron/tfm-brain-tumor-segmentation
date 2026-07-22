# 1. Introducción

El diagnóstico apoyado en técnicas de imagen médica constituye uno de los pilares de la práctica
clínica moderna. Modalidades como la radiografía, la tomografía computarizada, la resonancia
magnética o la tomografía por emisión de positrones permiten examinar de forma no invasiva la
anatomía y determinadas propiedades fisiológicas o metabólicas de los tejidos. En oncología, estas
técnicas intervienen en la detección y caracterización de lesiones, la planificación terapéutica,
la evaluación de la respuesta al tratamiento y el seguimiento longitudinal. No obstante, sus
resultados no deben interpretarse de forma aislada, sino integrarse con la información clínica,
histopatológica y molecular del paciente.

## 1.1. Contexto y motivación

En particular, la imagen médica desempeña una función central en neuro-oncología, debido a la
complejidad anatómica del sistema nervioso central, la heterogeneidad de los tumores cerebrales y la
necesidad de preservar estructuras funcionales durante el tratamiento. Entre estos tumores, los
gliomas constituyen un grupo heterogéneo con diferentes características biológicas, grados de
agresividad y pronósticos. La resonancia magnética (MRI, por sus siglas en inglés) es la principal
técnica de imagen empleada en su evaluación, ya que proporciona un elevado contraste entre tejidos
blandos y aporta información relevante para la caracterización de la lesión, la planificación
quirúrgica y radioterápica y el seguimiento de la enfermedad (Langen et al., 2017; Khalighi et al.,
2024).

La evaluación de los gliomas mediante MRI tiene un carácter multiparamétrico. En segmentación
automática se emplean habitualmente cuatro secuencias convencionales: T1 nativa (T1n), T1 con
contraste (T1c), T2 ponderada (T2w) y recuperación de la inversión atenuada por fluido (FLAIR). La
secuencia T1n proporciona una referencia anatómica de base, mientras que T1c permite identificar las
regiones que realzan tras la administración de contraste, asociado al aumento de permeabilidad de la
barrera hematoencefálica. Sin embargo, ese realce no representa por sí solo toda la extensión del
tejido tumoral biológicamente activo. Las secuencias T2w y FLAIR son sensibles al aumento del
contenido de agua. En particular, FLAIR suprime la señal del líquido cefalorraquídeo y facilita la
visualización de alteraciones peritumorales que pueden incluir edema e infiltración. Ninguna
modalidad describe por sí sola toda la lesión. Su combinación proporciona información complementaria
para delimitar el tumor y sus subregiones (Langen et al., 2017; Kouli et al., 2022).

Cuando se requiere una cuantificación volumétrica, la delimitación manual de estas regiones por
especialistas resulta compleja y costosa. Los límites difusos, la heterogeneidad de intensidades y
la extensión tridimensional favorecen la variabilidad entre observadores e incluso entre anotaciones
de un mismo profesional, además de consumir un tiempo considerable. La segmentación automática se
plantea, por tanto, como herramienta de apoyo capaz de reducir la carga de trabajo y proporcionar
estimaciones más consistentes. Aun así, el problema no está completamente resuelto, ya que el
rendimiento disminuye en algunas subregiones y la generalización a imágenes de otros centros sigue
siendo un reto (Kouli et al., 2022). Asimismo, unas métricas favorables no garantizan por sí solas la
utilidad clínica de una segmentación, lo que hace necesaria su evaluación por especialistas (Hoebel
et al., 2024).

En los últimos años, el aprendizaje profundo ha ampliado sus aplicaciones en neuro-oncología
(detección y clasificación de tumores, segmentación de lesiones, predicción de características
moleculares y estimación del pronóstico), con estudios que respaldan su potencial como apoyo a la
interpretación radiológica (Gao et al., 2022). Sin embargo, su incorporación a la práctica clínica
exige modelos robustos ante variaciones en escáneres, protocolos y poblaciones, además de validación
externa, interpretabilidad e integración en los flujos de trabajo (Khalighi et al., 2024).

Dentro de este contexto, el presente Trabajo de Fin de Máster se centra en la **segmentación
automática tridimensional de gliomas a partir de imágenes MRI multimodales**. El sistema se aplica
exclusivamente a pacientes previamente diagnosticados y no pretende realizar cribado, determinar la
presencia de un tumor ni diferenciar los gliomas de otras patologías. La investigación estudia cómo
combinar la información complementaria de las secuencias T1n, T1c, T2w y FLAIR. Concretamente,
analiza **si un mecanismo de fusión adaptativa mejora la delimitación de las subregiones tumorales
frente a la concatenación convencional de modalidades**, manteniendo un coste computacional
asumible.

## 1.2. Planteamiento del problema

Las modalidades T1n, T1c, T2w y FLAIR proporcionan contrastes complementarios, pero su contribución
a la segmentación no es uniforme ni existe una correspondencia exclusiva entre una modalidad y una
región tumoral. Algunas estructuras resultan más visibles en determinadas secuencias, mientras que
la información de las restantes puede ser parcialmente redundante o ayudar a resolver ambigüedades.
Estudios recientes muestran, por ejemplo, una mayor relevancia de FLAIR para delimitar la extensión
hiperintensa peritumoral y de T1c para identificar tejido realzante, aunque la combinación de
modalidades suele proporcionar resultados más robustos (Ruffle et al., 2023). Esta complementariedad
es la base del enfoque multimodal de BraTS-GLI 2024, conjunto empleado en este trabajo, que
proporciona MRI multiparamétrica y anotaciones expertas para evaluar algoritmos de segmentación
(de Verdier et al., 2024).

Una estrategia habitual para integrar estas secuencias consiste en alinearlas y concatenarlas como
canales de un único tensor de entrada. Esta fusión temprana es sencilla, introduce un coste
computacional mínimo y permite que las primeras capas convolucionales aprendan filtros distintos por
canal. Por tanto, no es correcto afirmar que asigne necesariamente el mismo peso a todas las
modalidades. Su limitación es que no incorpora un mecanismo explícito que estime y reajuste la
contribución relativa de cada modalidad en función del contenido de la entrada, sino que dicha
contribución queda representada de forma implícita en los filtros aprendidos.

La literatura ha explorado mecanismos de fusión más elaborados para aprovechar las relaciones entre
modalidades, como la combinación en distintos niveles de la red o los módulos de atención que
recalibran las representaciones. Liu et al. (2022) combinaron fusión a nivel de imagen y de
características, y Zhou et al. (2022) propusieron un mecanismo de atención que modela la relevancia de
las modalidades, su distribución espacial y sus correlaciones. Estos trabajos respaldan el interés
por una integración adaptativa, aunque sus arquitecturas son más complejas y no permiten concluir
que cualquier mecanismo de atención supere necesariamente a la concatenación (Liu et al., 2022; Zhou
et al., 2022).

La problemática central de este TFM consiste, por tanto, en **determinar si una ponderación explícita
y ligera de las modalidades aporta una mejora medible cuando se mantiene fija la arquitectura de
segmentación**. Para aislar esta variable se utiliza la misma Residual U-Net 3D y el mismo protocolo
de entrenamiento en cuatro configuraciones: concatenación directa, ponderación global estática,
compuerta adaptativa basada en la media y una extensión condicionada por la media y la desviación
típica de cada modalidad. La ponderación global aprende un coeficiente por modalidad compartido por
todas las entradas, mientras que las compuertas adaptativas generan los coeficientes a partir del
tensor tridimensional procesado. Esos coeficientes se aplican antes del codificador y permanecen
constantes en el espacio dentro de cada parche o ventana de inferencia. Por tanto, el mecanismo es
dependiente de la entrada, pero no constituye una atención espacial ni específica por subregión. La
inclusión de la ponderación global permite distinguir dos posibilidades: que baste con aprender una
jerarquía general entre modalidades o que resulte beneficioso adaptar dicha ponderación al contenido
de cada muestra.

A partir de este planteamiento, la pregunta de investigación se formula así:

> ¿Puede una ponderación explícita y ligera de las modalidades T1n, T1c, T2w y FLAIR —en particular,
> una compuerta adaptativa condicionada por la entrada— mejorar de forma consistente la segmentación
> 3D de ET, TC y WT en BraTS-GLI 2024 frente a la concatenación directa de canales, manteniendo fija
> la arquitectura Residual U-Net 3D y un coste computacional asumible?

La evaluación se realiza mediante el coeficiente Dice y la distancia de Hausdorff al percentil 95
(HD95) para ET, TC y WT. La huella computacional se analiza mediante el número de parámetros y los
registros disponibles de tiempo de entrenamiento y memoria, explicitando las diferencias entre
entornos. Este aspecto resulta especialmente relevante en segmentación volumétrica, donde el
incremento de complejidad de los mecanismos de atención puede traducirse en un consumo considerable
de memoria y tiempo (Shaker et al., 2024).

El alcance experimental se limita a las imágenes post-tratamiento de BraTS-GLI 2024 que contienen las
cuatro modalidades requeridas. **El modelo no se ha entrenado ni validado para realizar cribado,
diagnosticar la presencia de un tumor, diferenciar los gliomas de otras patologías o trabajar con
secuencias ausentes**, y sus resultados deben interpretarse dentro del entorno controlado del
*benchmark*. La evidencia muestra que el rendimiento sobre datos BraTS puede disminuir al aplicar los
modelos a imágenes clínicas externas con distintas resoluciones o protocolos (Berkley et al., 2023).
En consecuencia, el trabajo evalúa una estrategia computacional de segmentación y no una herramienta
lista para uso clínico.

## 1.3. Objetivos

**Objetivo principal.** Diseñar, implementar y evaluar un sistema reproducible de segmentación
tridimensional basado en aprendizaje profundo para **determinar si** una ponderación adaptativa y
ligera de las modalidades T1n, T1c, T2w y FLAIR mejora la delimitación de las regiones ET, TC y WT en
BraTS-GLI 2024 frente a la concatenación directa de canales, considerando tanto el rendimiento de
segmentación como el coste computacional.

**Objetivos específicos:**

1. Construir un *pipeline* reproducible con MONAI para cargar los volúmenes MRI multimodales,
   transformar las etiquetas en las regiones objetivo, normalizar las intensidades por modalidad y
   aplicar aumento de datos durante el entrenamiento.
2. Implementar y entrenar una Residual U-Net 3D que reciba las cuatro modalidades concatenadas como
   canales de entrada, estableciendo el modelo base de las comparaciones.
3. Diseñar e integrar, antes del codificador, una compuerta adaptativa ligera que estime un peso por
   modalidad en función del contenido de la entrada y lo aplique a los canales.
4. Realizar un estudio de ablación controlado que compare concatenación directa, ponderación global
   estática y dos variantes de ponderación adaptativa —basadas en la media y en
   media+desviación—, manteniendo constantes la arquitectura base, las particiones y el protocolo de
   entrenamiento.
5. Evaluar las variantes de fusión mediante Dice y HD95 para ET, TC y WT, y analizar su huella
   computacional a partir del número de parámetros y de los registros disponibles de tiempo y
   memoria.
6. Contextualizar los resultados comparándolos con arquitecturas de referencia de mayor complejidad
   (Attention U-Net y Swin-UNETR) y con el *baseline* externo nnU-Net.

El trabajo persigue **responder** la pregunta de investigación, sea la respuesta afirmativa o
negativa.

## 1.4. Organización del documento

La memoria se estructura en seis capítulos que avanzan desde la contextualización del problema hasta
la evaluación experimental de la solución.

- **Capítulo 1, Introducción.** Presenta el papel de la imagen médica y la inteligencia artificial en
  neuro-oncología, delimita el problema, formula la pregunta de investigación y fija los objetivos.
- **Capítulo 2, Marco teórico y estado del arte.** Desarrolla los fundamentos de la segmentación 3D
  de imagen médica, las arquitecturas U-Net y sus variantes, los mecanismos de atención, los modelos
  basados en Transformers y las estrategias de fusión multimodal. Presenta el *benchmark* BraTS y
  formaliza las métricas Dice y HD95.
- **Capítulo 3, Metodología.** Expone las fases de alto nivel del trabajo (familiarización, análisis y
  preparación de datos, diseño e implementación, experimentación y evaluación), centrándose en el
  proceso y dejando el detalle técnico para el capítulo siguiente.
- **Capítulo 4, Desarrollo.** Describe la materialización técnica de cada fase, incluida la
  organización del repositorio, el *pipeline* MONAI, las arquitecturas, los mecanismos de fusión, la
  configuración del entrenamiento, la inferencia por ventana deslizante y las medidas de
  reproducibilidad.
- **Capítulo 5, Resultados.** Compara las estrategias de fusión y las arquitecturas mediante Dice y
  HD95 por región sobre el conjunto de test, y examina el coste computacional.
- **Capítulo 6, Conclusiones.** Sintetiza los hallazgos, responde a la pregunta de investigación,
  valora el cumplimiento de los objetivos y expone limitaciones y líneas de trabajo futuro.

Tras estos capítulos se incluyen la relación completa de referencias bibliográficas y un apéndice de
reproducibilidad.
