# 1. Introducción

La segmentación tridimensional de gliomas mediante resonancia magnética (RM) combina T1n, T1c, T2w
y FLAIR porque cada secuencia destaca componentes distintos de la
lesión. La decisión estudiada en este trabajo no consiste solo en introducir las cuatro modalidades
en una red, sino en determinar si una ponderación explícita y dependiente de la entrada mejora su
combinación sin cambiar la arquitectura de segmentación ni aumentar sustancialmente su coste.

## 1.1. Contexto y motivación

La RM es la principal técnica de imagen empleada para evaluar gliomas. Su contraste entre tejidos
blandos aporta información para caracterizar la lesión, planificar la cirugía y la radioterapia y
seguir la evolución de la enfermedad. Estas funciones son especialmente relevantes ante la
heterogeneidad biológica de los gliomas y la necesidad de preservar estructuras funcionales del
sistema nervioso central durante el tratamiento (Langen et al., 2017; Khalighi et al., 2024).

La evaluación de los gliomas mediante RM tiene un carácter multiparamétrico. En segmentación
automática se emplean habitualmente cuatro secuencias convencionales: T1 nativa (T1n), T1 con
contraste (T1c), T2 ponderada (T2w) y recuperación de la inversión atenuada por fluido (FLAIR). La
secuencia T1n proporciona una referencia anatómica de base, mientras que T1c permite identificar las
regiones que realzan tras la administración de contraste, asociado al aumento de permeabilidad de la
barrera hematoencefálica. Sin embargo, ese realce no representa por sí solo toda la extensión del
tejido tumoral biológicamente activo. Las secuencias T2w y FLAIR son sensibles al aumento del
contenido de agua. En particular, FLAIR suprime la señal del líquido cefalorraquídeo y facilita la
visualización de alteraciones peritumorales que pueden incluir edema e infiltración. Ninguna
modalidad describe por sí sola toda la lesión, por lo que se combinan para delimitar sus subregiones
(Langen et al., 2017; Kouli et al., 2022). En este experimento, las regiones objetivo son el tumor
realzante (ET), el núcleo tumoral (TC) y el tumor completo (WT), de acuerdo con la definición de
BraTS-GLI 2024 (de Verdier et al., 2024).

Cuando se requiere una cuantificación volumétrica, la delimitación manual de estas regiones por
especialistas resulta compleja y costosa. Los límites difusos, la heterogeneidad de intensidades y
la extensión tridimensional favorecen la variabilidad entre observadores e incluso entre anotaciones
de un mismo profesional, además de consumir un tiempo considerable. La segmentación automática se
plantea, por tanto, como herramienta de apoyo capaz de reducir la carga de trabajo y proporcionar
estimaciones más consistentes. Aun así, el problema no está resuelto: el rendimiento disminuye en
algunas subregiones y la generalización a imágenes de otros centros continúa siendo un reto (Kouli
et al., 2022). Además, unas métricas favorables no garantizan por sí solas la utilidad clínica, que
requiere evaluación por especialistas (Hoebel et al., 2024).

El aprendizaje profundo se ha aplicado al diagnóstico, la clasificación y la segmentación de
tumores cerebrales (Gao et al., 2022; Kouli et al., 2022). Su incorporación a la práctica clínica
exige robustez ante variaciones en escáneres, protocolos y poblaciones, validación externa,
interpretabilidad e integración en los flujos de trabajo (Khalighi et al., 2024).

El trabajo compara cuatro reglas de fusión temprana de T1n, T1c, T2w y FLAIR. La variable
experimental principal es el bloque que precede al codificador; la Residual U-Net 3D, los datos y el
entrenamiento se mantienen fijos. Se analiza así **si un mecanismo de fusión adaptativa mejora la
delimitación de ET, TC y WT frente a la concatenación convencional**, con un coste computacional
asumible. El alcance se restringe a la segmentación de pacientes previamente diagnosticados: no se
abordan el cribado, la detección del tumor ni el diagnóstico diferencial.

## 1.2. Planteamiento del problema

Las modalidades T1n, T1c, T2w y FLAIR proporcionan contrastes complementarios, pero su contribución
a la segmentación no es uniforme ni existe una correspondencia exclusiva entre una modalidad y una
región tumoral. Algunas estructuras resultan más visibles en determinadas secuencias, mientras que
la información de las restantes puede ser parcialmente redundante o ayudar a resolver ambigüedades.
Estudios recientes muestran, por ejemplo, una mayor relevancia de FLAIR para delimitar la extensión
hiperintensa peritumoral y de T1c para identificar tejido realzante, aunque la combinación de
modalidades suele proporcionar resultados más robustos (Ruffle et al., 2023). Esta complementariedad
es la base del enfoque multimodal de BraTS-GLI 2024, conjunto empleado en este trabajo, que
proporciona RM multiparamétrica y anotaciones expertas para evaluar algoritmos de segmentación
(de Verdier et al., 2024).

Una estrategia habitual para integrar estas secuencias consiste en alinearlas y concatenarlas como
canales de un único tensor de entrada. Esta fusión temprana es sencilla y añade un coste
computacional mínimo. La concatenación no impone pesos iguales a las modalidades: la primera
convolución puede aprender filtros distintos para cada canal. Lo que no ofrece es un coeficiente
separado y observable que reajuste la contribución de cada modalidad para cada entrada; esa
contribución queda representada de forma implícita en los filtros aprendidos.

La literatura ha explorado mecanismos de fusión más elaborados para aprovechar las relaciones entre
modalidades, como la combinación en distintos niveles de la red o los módulos de atención que
recalibran las representaciones. Liu et al. (2022) combinaron fusión a nivel de imagen y de
características, y Zhou et al. (2022) propusieron un mecanismo de atención que modela la relevancia de
las modalidades, su distribución espacial y sus correlaciones. Estos trabajos respaldan el interés
por una integración adaptativa, aunque sus arquitecturas son más complejas y no permiten concluir
que cualquier mecanismo de atención supere necesariamente a la concatenación (Liu et al., 2022; Zhou
et al., 2022).

La pregunta central consiste en **determinar si una ponderación explícita y ligera de las
modalidades aporta una mejora medible cuando se mantiene fija la arquitectura de segmentación**.
Para reducir las variables de comparación se utiliza la misma Residual U-Net 3D y el mismo protocolo
de entrenamiento en cuatro configuraciones: concatenación directa, ponderación global aprendida e
independiente de la entrada, compuerta adaptativa basada en la media y una extensión condicionada
por la media y la desviación típica de cada modalidad.

La ponderación global aprende un coeficiente por modalidad compartido por todas las entradas. Las
compuertas adaptativas, en cambio, generan esos coeficientes a partir del tensor tridimensional
procesado. Los pesos se aplican antes del codificador y permanecen constantes en el espacio dentro
de cada parche o ventana de inferencia; el mecanismo depende de la entrada, pero no constituye
atención espacial ni específica por subregión.

La ponderación global se incluyó como comparador intermedio para separar dos hipótesis: si basta con
aprender una jerarquía común entre modalidades o si conviene adaptarla al contenido de cada entrada.

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

1. Construir un *pipeline* reproducible con MONAI para cargar los volúmenes de RM multimodales,
   transformar las etiquetas en las regiones objetivo, normalizar las intensidades por modalidad y
   aplicar aumento de datos durante el entrenamiento.
2. Implementar y entrenar una Residual U-Net 3D que reciba las cuatro modalidades concatenadas como
   canales de entrada, estableciendo el modelo base de las comparaciones.
3. Diseñar e integrar, antes del codificador, una compuerta adaptativa ligera que estime un peso por
   modalidad en función del contenido de la entrada y lo aplique a los canales.
4. Realizar un estudio de ablación controlado que compare concatenación directa, ponderación global
   aprendida e independiente de la entrada y dos variantes adaptativas —una basada en la media y
   otra en la media y la desviación típica—, manteniendo constantes la arquitectura base, las
   particiones y el protocolo de entrenamiento.
5. Evaluar las variantes de fusión mediante Dice y HD95 para ET, TC y WT, y analizar su huella
   computacional a partir del número de parámetros y de los registros disponibles de tiempo y
   memoria.
6. Contextualizar los resultados comparándolos con arquitecturas de referencia de mayor complejidad
   (Attention U-Net y Swin-UNETR) y con la referencia externa nnU-Net.

## 1.4. Organización del documento

Los capítulos 1 y 2 delimitan la pregunta de investigación y sus fundamentos. Los capítulos 3 y 4
separan el proceso metodológico de su implementación en el sistema MONAI y en la ruta externa de
nnU-Net. Los capítulos 5 y 6 presentan los resultados, responden a la pregunta y exponen sus
limitaciones. La memoria se completa con las referencias bibliográficas y un apéndice de
reproducibilidad.
