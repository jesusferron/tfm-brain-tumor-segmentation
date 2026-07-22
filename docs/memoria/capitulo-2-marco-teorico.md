# 2. Marco teórico y estado del arte

Este capítulo presenta los fundamentos necesarios para situar la aportación del TFM. Primero se
describe la evolución desde las redes completamente convolucionales hasta las arquitecturas 3D con
conexiones residuales, atención y *Transformers*. A continuación se ordena la literatura sobre
fusión multimodal distinguiendo dos decisiones que a menudo se confunden. La primera es **en qué
etapa** se integran las modalidades; la segunda, **mediante qué regla** se combinan. Por último, se
introduce el *benchmark* BraTS-GLI 2024, se formalizan las métricas de evaluación, se delimita el
análisis de coste computacional y se justifican las implementaciones consideradas en el trabajo.
Esta revisión permite concretar la brecha abordada, que consiste en comprobar de forma controlada si
una ponderación ligera y dependiente de la entrada aporta ventajas frente a la concatenación, sin
cambiar la red de segmentación que recibe las modalidades.

## 2.1. De las redes completamente convolucionales a U-Net 3D

La segmentación semántica asigna una clase a cada elemento de una imagen. En MRI volumétrica, la
entrada puede representarse como un tensor con $M$ modalidades y tres dimensiones espaciales, y
la salida como uno o varios mapas de probabilidad con la misma correspondencia anatómica. Las
**redes completamente convolucionales** (FCN) sustituyeron las capas densas finales de los
clasificadores por operadores convolucionales y mecanismos de remuestreo, haciendo posible una
predicción densa de extremo a extremo (Long et al., 2015). Su principal dificultad era recuperar
con precisión la localización espacial después de las sucesivas reducciones de resolución del
codificador.

U-Net respondió a ese problema con una estructura aproximadamente simétrica formada por un camino
de contracción y otro de expansión. Las conexiones de salto trasladan al decodificador
características de alta resolución producidas por el codificador, de forma que la decisión final
combina contexto semántico y detalle espacial (Ronneberger et al., 2015). Esta organización resulta
especialmente adecuada para imagen biomédica, donde las estructuras de interés pueden ser pequeñas
y el número de ejemplos anotados suele ser limitado.

La extensión **U-Net 3D** reemplaza los operadores bidimensionales por convoluciones, normalizaciones
y remuestreos tridimensionales. Así se modela la continuidad entre cortes en lugar de tratar cada
plano como una observación independiente. Çiçek et al. (2016) mostraron que esta formulación permite
aprender segmentación volumétrica incluso a partir de anotaciones escasas, mientras que V-Net
desarrolló otra arquitectura completamente convolucional 3D e introdujo una función objetivo basada
en Dice para afrontar el fuerte desequilibrio entre fondo y lesión (Milletari et al., 2016).

El procesamiento 3D conserva más contexto anatómico, pero incrementa de manera pronunciada la
memoria ocupada por las activaciones. Por ello, los sistemas volumétricos suelen entrenarse sobre
parches y reconstruir la predicción completa mediante ventanas solapadas. El tamaño de parche pasa a
ser una decisión conjunta de contexto, resolución y memoria. Un parche mayor aporta más información
global, pero limita el tamaño del lote o la capacidad de la red. Esta tensión explica por qué una
arquitectura teóricamente más expresiva no es necesariamente la mejor bajo un presupuesto de
cómputo fijo.

## 2.2. Refinamientos convolucionales: residuos, atención y auto-configuración

Sobre la estructura básica de U-Net se han desarrollado mejoras que actúan sobre distintos
componentes del sistema. Esta sección revisa tres especialmente relevantes para el diseño y la
interpretación de los experimentos: las conexiones residuales, que facilitan la optimización de
redes profundas; las compuertas de atención, que seleccionan las características transmitidas por
las conexiones de salto; y nnU-Net, que automatiza decisiones de configuración del *pipeline*
completo. Aunque las tres propuestas parten de la familia U-Net, no resuelven el mismo problema ni
equivalen a estrategias de fusión multimodal. Esta distinción permite justificar el uso de una
Residual U-Net como base del estudio, de Attention U-Net como referencia arquitectónica y de
nnU-Net como referencia externa.

### 2.2.1. Conexiones residuales

Las redes profundas pueden resultar difíciles de optimizar porque cada bloque debe aprender una
transformación completa y el gradiente atraviesa una cadena larga de operaciones. Una conexión
residual reformula un bloque como

$$
\mathbf{y}=\mathcal{F}(\mathbf{x};\theta)+\mathbf{x},
$$

donde $\mathcal{F}$ aprende el residuo respecto de la identidad. Este camino directo facilita la
propagación de información y gradientes y permite entrenar redes considerablemente más profundas
(He et al., 2016). En una **Residual U-Net**, estos bloques se incorporan al codificador y al
decodificador sin eliminar las conexiones de salto entre ambos caminos. Se preserva así la
estructura multiescala de U-Net y se mejora la optimización interna de cada nivel.

Las conexiones residuales no deben confundirse con una estrategia de fusión multimodal. Un bloque
residual modifica cómo se transforman las características dentro de la red. Por su parte, la fusión
determina cómo llegan al modelo las distintas secuencias MRI. Esta independencia permite mantener
fija una Residual U-Net 3D y cambiar únicamente la regla de combinación de modalidades, que es el
diseño del estudio de ablación de este TFM.

### 2.2.2. Compuertas de atención

Las conexiones de salto de U-Net transmiten tanto señales relevantes como activaciones de fondo.
**Attention U-Net** incorpora compuertas que utilizan una señal de contexto procedente del
decodificador para modular espacialmente las características del codificador antes de combinarlas
(Oktay et al., 2018). El mecanismo dirige capacidad hacia regiones compatibles con el objetivo y
puede reducir respuestas irrelevantes sin exigir una red de localización separada. El trabajo
original se validó sobre segmentación abdominal. Su utilidad en gliomas debe, por tanto, evaluarse
experimentalmente y no asumirse por traslación directa entre dominios.

Esta atención sobre conexiones de salto tampoco equivale a ponderar modalidades. La primera asigna
relevancia a posiciones y características internas. Por el contrario, una compuerta de modalidad
decide cuánto contribuye cada secuencia de entrada. Attention U-Net se incluye en este TFM como
referencia arquitectónica contextual, mientras que la hipótesis principal se estudia sobre una red
residual fija.

### 2.2.3. nnU-Net como *pipeline* auto-configurable

nnU-Net no es solamente una nueva variante de U-Net. Es un método auto-configurable que obtiene una
«huella» del conjunto de datos y, a partir de ella, adapta el preprocesamiento, la configuración 2D
o 3D, el tamaño de parche y de lote, el entrenamiento, el posprocesado y la inferencia. Su propuesta
es que una parte sustancial del rendimiento depende de decisiones de ingeniería coherentes con cada
conjunto de datos, no solo de introducir módulos arquitectónicos novedosos (Isensee et al., 2021).

Esta distinción es relevante para interpretar comparaciones. Un resultado de nnU-Net refleja un
sistema completo auto-configurado, mientras que las variantes de fusión del TFM comparten un
*pipeline* MONAI y modifican una única variable. nnU-Net constituye por ello un *baseline* externo
fuerte para contextualizar el nivel alcanzado, pero no forma parte de la ablación causal entre
reglas de fusión.

## 2.3. *Transformers* y arquitecturas híbridas para segmentación 3D

El mecanismo de autoatención de los *Transformers* relaciona cada elemento de una secuencia con los
demás y facilita el modelado de dependencias de largo alcance (Vaswani et al., 2017). Vision
Transformer trasladó esta idea a imágenes al dividirlas en parches, proyectarlos como *tokens* y
procesarlos mediante un codificador Transformer (Dosovitskiy et al., 2021). En segmentación médica
3D, la ventaja potencial es incorporar contexto distribuido por el volumen. Sin embargo, la
contrapartida es que la autoatención global crece cuadráticamente con el número de *tokens*, que puede
ser muy elevado en datos volumétricos.

Swin Transformer limita la atención a ventanas locales y desplaza esas ventanas entre bloques para
permitir intercambio de información entre regiones vecinas. Además, construye una jerarquía de
características con distintas resoluciones, apropiada para tareas densas y con una complejidad más
controlada respecto al número de elementos de la imagen (Liu et al., 2021). Esta combinación de
jerarquía y ventanas desplazadas acerca el comportamiento de un Transformer a la representación
multiescala que requieren los decodificadores tipo U-Net.

En imagen médica se han propuesto varias formas de integrar este paradigma. **UNETR** emplea un
Transformer como codificador de una secuencia de parches volumétricos y conecta representaciones de
distintas profundidades con un decodificador convolucional (Hatamizadeh et al., 2022). **Swin UNETR**
reemplaza ese codificador por una jerarquía Swin 3D y conserva un decodificador con conexiones de
salto. Fue presentado por Tang et al. (2022) dentro de un marco de preentrenamiento autosupervisado.
La implementación utilizada en este TFM corresponde a la arquitectura disponible en MONAI y se
entrena con el protocolo definido para el proyecto, sin atribuirle por ello los resultados del
preentrenamiento del artículo original.

**TransBTS** adopta otra solución híbrida. Una CNN extrae representaciones espaciales 3D y un
Transformer situado en la parte profunda modela relaciones globales antes de la decodificación
(Wang et al., 2021). En paralelo, propuestas como UNETR++ buscan reducir el coste de la atención 3D
mediante bloques más eficientes (Shaker et al., 2024). En conjunto, estas arquitecturas amplían el
campo receptivo y la capacidad de modelar contexto, pero suelen exigir más parámetros, memoria o
tiempo que una U-Net compacta. Por ello, CNN, modelos híbridos y Transformers puros deben compararse
bajo datos, presupuesto y protocolo compatibles; la familia arquitectónica, por sí sola, no
garantiza un resultado superior.

## 2.4. Fusión multimodal en MRI

Las secuencias T1n, T1c, T2w y FLAIR observan el mismo volumen desde contrastes complementarios. La
fusión multimodal especifica cómo se ponen en relación esas fuentes. Para ordenar sus variantes es
necesario separar dos ejes. El primero es la **etapa de fusión**, es decir, el punto del flujo en el
que se unen las modalidades; el segundo, la **regla de combinación**, que define la operación
concreta aplicada en ese punto. «Adaptativa» describe una regla dependiente de los datos, no una etapa
por sí misma.

Según la etapa, se distinguen tres categorías principales. En la **fusión temprana**, las
modalidades se combinan antes del extractor o en sus primeras capas. Es eficiente y permite aprender
interacciones desde el inicio, aunque normalmente presupone que todas las secuencias están
disponibles y alineadas. En la **fusión intermedia**, cada modalidad dispone de una rama propia —o
de un procesamiento parcialmente separado— y las características se integran en uno o varios
niveles. Esta opción puede preservar representaciones específicas de cada contraste, a cambio de
mayor complejidad. En la **fusión tardía**, cada modalidad genera predicciones que se combinan al
final. Ofrece modularidad, pero replica gran parte del cálculo y retrasa las interacciones entre
secuencias. Los diseños híbridos pueden emplear más de una etapa, como muestran propuestas que
combinan fusión a nivel de imagen, características o contexto global (Liu et al., 2022; Wang et al.,
2021; Zhou et al., 2022).

A partir de estas definiciones, la Tabla 1 sintetiza las tres categorías. La columna de reglas
incluye ejemplos posibles y no establece una correspondencia exclusiva. Una ponderación aprendida,
por ejemplo, puede aplicarse tanto a la entrada como a características intermedias.

**Tabla 1.** Etapas de fusión multimodal en segmentación de imagen médica.

| Etapa | Representación que se combina | Reglas habituales | Ventajas | Limitaciones |
| :-- | :-- | :-- | :-- | :-- |
| Temprana (*early fusion*) | Imágenes o canales antes del codificador | Concatenación, suma o ponderación de modalidades | Integración sencilla; reutiliza un único extractor; coste adicional reducido | Dependencia de modalidades presentes y registradas. Menor separación explícita de rasgos específicos |
| Intermedia (*feature-level fusion*) | Características de ramas específicas en uno o varios niveles | Concatenación, suma, atención cruzada o compuertas | Modela relaciones multiescala y conserva representaciones por modalidad | Más parámetros y activaciones. Aumenta la complejidad de entrenamiento e integración |
| Tardía (*decision-level fusion*) | Mapas de probabilidad o decisiones de modelos separados | Media, voto, producto o ensamblado aprendido | Modularidad y posibilidad de especialización por modalidad | Duplica cálculo. Las modalidades no interactúan durante la extracción temprana de rasgos |

La comparación muestra que la etapa no determina por sí sola el grado de adaptación. La fusión
temprana puede ser una concatenación sin pesos explícitos o una ponderación condicionada por la
entrada. De igual modo, una fusión intermedia puede usar coeficientes fijos. La decisión relevante
depende del equilibrio buscado entre interacción multimodal, coste y facilidad para aislar el efecto
experimental.

### 2.4.1. Reglas de combinación temprana

Sean $\mathbf{x}_1,\ldots,\mathbf{x}_M$ las modalidades registradas de una muestra. La
**concatenación** forma $\mathbf{x}=[\mathbf{x}_1;\ldots;\mathbf{x}_M]$ y deja que la primera capa
aprenda filtros diferentes para cada canal. No realiza una media ni impone matemáticamente el mismo
peso a todas las modalidades. Su rasgo distintivo es que carece de un parámetro separado e
interpretable que reajuste de forma explícita su contribución.

Una **ponderación global estática** aprende un vector de parámetros compartido por todas las
muestras. Si $\boldsymbol{\alpha}=\operatorname{softmax}(\boldsymbol{\theta})$, cada canal puede
reescalarse como

$$
\widetilde{\mathbf{x}}_m=M\alpha_m\mathbf{x}_m.
$$

El factor $M$ conserva la escala de la identidad cuando los pesos se inicializan uniformemente.
Esta regla puede descubrir una jerarquía promedio entre secuencias, pero aplica la misma jerarquía a
todos los casos.

Una **ponderación condicionada por la entrada** calcula
$\boldsymbol{\alpha}(\mathbf{x})=\operatorname{softmax}(g(\phi(\mathbf{x})))$, donde
$\phi$ resume cada modalidad y $g$ genera sus coeficientes. En este TFM, los descriptores
son estadísticas globales de intensidad y se obtiene un peso por modalidad y muestra. Los pesos se
aplican antes del codificador y son constantes en las tres dimensiones espaciales dentro de cada
entrada procesada. Por tanto, la propuesta es adaptativa respecto del caso, pero no constituye
atención espacial, atención por vóxel ni atención específica de ET, TC o WT.

### 2.4.2. Evolución del estado del arte y brecha estudiada

Los primeros sistemas profundos para tumor cerebral ya mostraron el valor de combinar escalas y
modalidades. Havaei et al. (2017) utilizaron caminos convolucionales con distinto contexto para
segmentar gliomas, y DeepMedic integró dos trayectorias 3D multiescala y un campo aleatorio
condicional para refinar lesiones cerebrales (Kamnitsas et al., 2017). Más adelante, la solución de
Myronenko (2019) combinó una red encoder-decoder 3D con regularización mediante autoencoder y puso de
manifiesto que las CNN volumétricas cuidadosamente entrenadas seguían siendo referencias muy
competitivas.

La investigación posterior ha trasladado la fusión a representaciones más ricas. Liu et al. (2022)
combinaron información a nivel de imagen y de características; Zhou et al. (2022) propusieron una
red de tri-atención que relaciona relevancia modal, distribución espacial y correlaciones entre
características. Otro frente aborda modalidades ausentes, para evitar que un sistema entrenado con
cuatro secuencias falle cuando alguna no está disponible (Ruffle et al., 2023). TransBTS representa,
a su vez, la integración del contexto multimodal dentro de una arquitectura híbrida
CNN-Transformer (Wang et al., 2021).

Estos trabajos demuestran que la fusión puede realizarse en múltiples niveles, pero también
introducen simultáneamente ramas, mecanismos de atención o codificadores diferentes. En esas
condiciones resulta difícil atribuir una mejora exclusivamente a la ponderación de modalidades. La
brecha que aborda este TFM es deliberadamente más acotada y consiste en aportar evidencia controlada
sobre si una regla temprana, global por muestra y de muy pocos parámetros supera a la concatenación y
a una ponderación estática cuando la Residual U-Net 3D, los datos y el entrenamiento se mantienen
fijos. El objetivo no es reivindicar una nueva familia general de fusión ni resolver el escenario de
modalidades ausentes, sino medir de forma reproducible el valor añadido de esa decisión concreta.

## 2.5. BraTS-GLI 2024 y evaluación de la segmentación

La interpretación de los resultados exige considerar conjuntamente el escenario en el que se
obtienen y las métricas empleadas. Esta sección presenta, en primer lugar, las particularidades de
BraTS-GLI 2024 como *benchmark* de gliomas post-tratamiento y distingue la evaluación interna del
TFM del protocolo oficial del reto. A continuación, define Dice y HD95, dos medidas complementarias
que resumen, respectivamente, el solapamiento de las regiones segmentadas y el error en sus límites.
Este marco permite comprender el alcance de los valores reportados en el Capítulo 5 y evita
atribuirles una validez clínica u oficial superior a la respaldada por el protocolo.

### 2.5.1. Del *benchmark* BraTS al escenario post-tratamiento

BraTS estableció un marco común para comparar segmentación multimodal de tumores cerebrales mediante
datos anotados, regiones objetivo y métricas compartidas (Menze et al., 2015). La edición
**BraTS-GLI 2024** se centra en gliomas post-tratamiento y reúne estudios MRI multicéntricos, un
escenario donde los cambios terapéuticos aumentan la heterogeneidad visual y la dificultad de
delimitación (de Verdier et al., 2024). Las cuatro secuencias utilizadas por este TFM son T1n, T1c,
T2w y FLAIR, y la evaluación se expresa de manera consistente para las regiones anidadas ET, TC y
WT.

El contexto post-tratamiento tiene además carácter longitudinal. El seguimiento clínico puede
producir más de un estudio del mismo sujeto en momentos distintos. Esta propiedad es relevante para
interpretar la independencia de las observaciones y para diseñar particiones, aunque el
procedimiento concreto de separación pertenece a los capítulos de metodología y desarrollo. El
marco teórico se limita aquí a señalar que el «caso» de imagen y el «sujeto» no tienen por qué ser
unidades equivalentes (de Verdier et al., 2024).

BraTS-GLI emplea una evaluación oficial sobre datos ocultos y métricas **por lesión**. Los resultados
internos de este trabajo, en cambio, proceden del conjunto de test local y calculan las métricas
sobre la máscara completa de cada región. Esta evaluación es adecuada para comparar de manera
homogénea los experimentos del TFM, pero sus valores no deben presentarse como resultados del
servidor oficial ni compararse de forma directa con una clasificación oficial sin reproducir su
protocolo lesion-wise (de Verdier et al., 2024).

### 2.5.2. Coeficiente Dice y distancia HD95

Para una región $r$, sean $P_r$ el conjunto de vóxeles predichos y $G_r$ la referencia. El
**coeficiente Dice** se define como

$$
\operatorname{Dice}(P_r,G_r)=\frac{2\lvert P_r\cap G_r\rvert}
{\lvert P_r\rvert+\lvert G_r\rvert}.
$$

Dice toma valores entre 0 y 1 y mide el solapamiento. Un valor de 1 representa una coincidencia
perfecta. Es sensible a errores relativos en regiones pequeñas y no informa directamente de la
distancia física entre fronteras (Dice, 1945; Taha & Hanbury, 2015).

Para complementar el solapamiento se emplea la **distancia de Hausdorff al percentil 95**. Sean
$\partial P_r$ y $\partial G_r$ las superficies de ambas máscaras y
$d(a,S)=\min_{s\in S}\lVert a-s\rVert_2$ la distancia de un punto a una superficie, calculada con
el espaciado físico de la imagen. Entonces,

$$
\operatorname{HD95}(P_r,G_r)=Q_{0.95}\!\left(
\{d(p,\partial G_r):p\in\partial P_r\}\cup
\{d(g,\partial P_r):g\in\partial G_r\}
\right),
$$

donde $Q_{0.95}$ es el percentil 95 del conjunto simétrico de distancias. Frente al máximo
clásico de Hausdorff, el percentil reduce la influencia de unos pocos valores extremos. Su unidad es
el milímetro y un valor menor indica fronteras más próximas (Huttenlocher et al., 1993; Taha &
Hanbury, 2015).

Los casos vacíos requieren convenciones explícitas. En la evaluación interna, si predicción y
referencia están vacías, se asigna Dice = 1 y HD95 = 0. Si solo una está vacía, se asigna Dice = 0 y
HD95 infinita. Los valores infinitos se conservan a nivel de caso para identificar el fallo, pero se
excluyen de los agregados finitos de HD95. Estas reglas, junto con el cálculo separado para ET, TC y
WT, evitan que una implementación implícita altere la interpretación de los resultados.

## 2.6. Coste computacional y reproducibilidad

La calidad de segmentación no basta para valorar una arquitectura. En un problema 3D deben
considerarse al menos cuatro dimensiones de coste. El **número de parámetros** aproxima la capacidad
del modelo y el tamaño de sus pesos; la **memoria máxima del acelerador** incluye también
activaciones, gradientes y estados del optimizador, por lo que depende del parche, el lote y la
precisión numérica; el **tiempo de entrenamiento** refleja el coste de obtener el modelo; y el
**tiempo de inferencia** condiciona su uso posterior. Dos redes con un número parecido de parámetros
pueden diferir notablemente en memoria o latencia por la forma de sus operaciones.

Las medidas temporales solo son comparables si se documentan hardware, versiones de software,
tamaño de entrada, precisión, lote y procedimiento de medida. Además, el entrenamiento es
estocástico y el tiempo hasta alcanzar una solución presenta variabilidad. Los principios de
*benchmarking* de MLPerf subrayan la necesidad de fijar tanto el sistema como el objetivo medido
(Mattson et al., 2020). Del mismo modo, publicar configuraciones, particiones, semillas y código
favorece que otros investigadores puedan reconstruir y comprobar los hallazgos (Pineau et al.,
2021).

En este TFM, estas magnitudes cumplen dos funciones distintas. Dentro de la ablación de fusión,
permiten verificar si el mecanismo añadido es realmente ligero frente a la misma Residual U-Net.
En la comparación contextual entre arquitecturas, ayudan a explicar las diferencias de escala, pero
no corrigen por sí solas cambios de hardware o protocolo. Por ello, los tiempos obtenidos en
entornos distintos se documentan como evidencia descriptiva y no como una clasificación universal
de eficiencia.

## 2.7. Implementaciones y repositorios considerados

La elección de software se realizó conforme a cinco criterios: correspondencia con las familias
arquitectónicas relevantes, soporte de tensores 3D y entradas multicanal, disponibilidad de una
implementación pública identificable, esfuerzo de integración con el *pipeline* y licencia del
código. MONAI aporta componentes específicos de imagen médica sobre PyTorch y una interfaz común
para transformaciones, redes e inferencia (Cardoso et al., 2022). nnU-Net y TransBTS se evaluaron a
partir de sus repositorios oficiales. El primero constituye un sistema externo auto-configurable y
el segundo una alternativa híbrida especializada.

La Tabla 2 aplica esos criterios a las opciones que influyeron en el diseño. «Multimodal» significa
aquí que la implementación admite las modalidades como canales o dispone de un flujo específico
para ellas, lo que no implica que incorpore ponderación explícita. La licencia indicada corresponde
al **software** consultado. El acceso y uso de BraTS-GLI se rigen por las condiciones propias del
conjunto de datos y no se deducen de la licencia de estos repositorios.

**Tabla 2.** Comparación de implementaciones y repositorios relevantes para el TFM.

| Componente y fuente de implementación | Tipo | Soporte 3D y multimodal | Integración y reproducibilidad | Licencia del software | Decisión razonada |
| :-- | :-- | :-- | :-- | :-- | :-- |
| MONAI ([`Project-MONAI/MONAI`](https://github.com/Project-MONAI/MONAI)) | *Framework* de imagen médica sobre PyTorch | Operadores 3D y entradas multicanal | Integración directa; API común para datos, modelos e inferencia | Apache-2.0 | Seleccionado como base del *pipeline* propio |
| Residual U-Net 3D (configuración propia de `monai.networks.nets.UNet`) | CNN encoder-decoder con unidades residuales | Sí; cuatro canales de entrada | Integración directa y control de una única regla de fusión | Dependencia MONAI: Apache-2.0; código del TFM: sin licencia declarada | Seleccionada como *baseline* y soporte de la ablación |
| Attention U-Net 3D (`monai.networks.nets.AttentionUnet`) | CNN con compuertas en conexiones de salto | Sí; cuatro canales de entrada | Integración directa en el mismo *pipeline* MONAI | Apache-2.0 | Seleccionada como referencia atencional contextual |
| Swin UNETR (`monai.networks.nets.SwinUNETR`) | Híbrido Transformer jerárquico y decodificador convolucional | Sí; cuatro canales de entrada | Integración directa, con mayor demanda prevista de memoria y cómputo | Apache-2.0 | Seleccionada como referencia Transformer contextual |
| nnU-Net v2 ([`MIC-DKFZ/nnUNet`](https://github.com/MIC-DKFZ/nnUNet)) | *Pipeline* auto-configurable | Sí; configuración 3D y múltiples canales | Flujo externo propio; requiere conversión de datos y conserva su planificación automática | Apache-2.0 | Seleccionado como *baseline* externo fuerte |
| TransBTS ([`Rubics-Xuan/TransBTS`](https://github.com/Rubics-Xuan/TransBTS)) | Arquitectura híbrida CNN-Transformer para segmentación multimodal | Sí; diseñada para volúmenes MRI multimodales | Repositorio oficial con entorno PyTorch independiente y adaptación manual al protocolo actual | Apache-2.0 | No ejecutada: el coste de portado añadía otra variable sin reforzar la ablación principal |

La tabla muestra que las cuatro configuraciones de fusión se apoyan en una única implementación
residual dentro de MONAI, condición necesaria para atribuir sus diferencias a la regla de entrada.
Attention U-Net y Swin UNETR amplían el contexto arquitectónico usando la misma infraestructura,
mientras nnU-Net conserva su flujo externo porque su auto-configuración forma parte del propio
método. TransBTS aporta una referencia pertinente para el estado del arte, pero integrarla habría
mezclado el estudio de fusión con un cambio simultáneo de codificador y de entorno. Esta decisión
reduce amplitud experimental, pero fortalece la validez interna de la comparación principal.

## 2.8. Posicionamiento del TFM

El estado del arte presenta tres niveles de decisión relacionados pero independientes. El primero
es la **arquitectura de segmentación**, desde U-Net 3D y sus variantes residuales o atencionales hasta
nnU-Net y los modelos Transformer. El segundo es la **fusión multimodal**, definida por una etapa y
una regla de combinación. El tercero es el **protocolo de evaluación**, que debe medir ET, TC y WT
con Dice y HD95, declarar sus convenciones y acompañar la exactitud con coste computacional.

El TFM se sitúa en la intersección de esos tres niveles con una pregunta intencionadamente limitada.
No pretende demostrar que la atención sea superior en general ni competir de forma directa con la
clasificación oficial de BraTS. Su contribución consiste en comparar concatenación, ponderación
global estática y dos compuertas condicionadas por estadísticas de la entrada antes del mismo
codificador residual, repetir la comparación con varias semillas y documentar el coste añadido. Las
arquitecturas Attention U-Net, Swin UNETR y nnU-Net proporcionan contexto, no sustituyen ese
contraste controlado. De este modo, tanto un resultado positivo como uno negativo responden al
objetivo científico de determinar si la adaptación propuesta aporta una mejora consistente y a qué
coste bajo el protocolo definido.
