# 2. Marco Teórico y Estado del Arte

> Reescritura y ampliación del Capítulo 2 a partir del borrador del documento de trabajo. Se
> conservan las citas del borrador y se añaden la sección del *benchmark* BraTS y la formalización de
> las métricas (que el índice exige). La tabla de estrategias de fusión pasa a ser la **Tabla 1** de
> la numeración consecutiva global y se referencia en el texto. Se neutraliza el posicionamiento del
> trabajo para no presuponer el signo del resultado.

## 2.1. Redes neuronales convolucionales en la segmentación biomédica

La evolución del aprendizaje profundo en visión artificial médica dio un salto cualitativo con las
Redes Completamente Convolucionales (FCN), que sustituyeron las capas densas finales por
convoluciones para permitir la predicción densa a nivel de píxel o vóxel. Sobre esta base, la
arquitectura **U-Net** (Ronneberger et al., 2015) se consolidó como estándar de referencia por su
estructura simétrica: un camino de contracción (codificador) que captura el contexto semántico y un
camino de expansión (decodificador) que recupera la resolución espacial mediante **conexiones de
salto** (*skip connections*), las cuales reinyectan detalle de alta resolución en el decodificador.

En imágenes médicas volumétricas, la extensión natural es la **U-Net 3D**, que reemplaza los *kernels*
de convolución bidimensionales por operadores tridimensionales. Esto permite explotar la coherencia
espacial inter-corte inherente a los volúmenes de MRI, evitando la pérdida de información de las
aproximaciones basadas en cortes 2D independientes. Sobre esta familia se apoya, además, **nnU-Net**,
un marco auto-configurable que adapta automáticamente el preprocesamiento, la arquitectura y los
hiperparámetros al conjunto de datos, y que constituye un *baseline* fuerte de referencia en
segmentación médica (Isensee et al., 2021).

## 2.2. Conexiones residuales y mecanismos de atención

A medida que las redes aumentan en profundidad para capturar abstracciones de alto nivel, se agrava
el problema del desvanecimiento del gradiente. Las arquitecturas tipo **Residual U-Net** mitigan este
fenómeno incorporando **conexiones residuales** de identidad dentro de los bloques convolucionales,
que facilitan la propagación directa del gradiente hacia las capas iniciales, mejoran la convergencia
y permiten aprender funciones residuales con menor coste de optimización.

Por otro lado, la **Attention U-Net** (Oktay et al., 2018) introduce **compuertas de atención**
(*attention gates*) en las conexiones de salto. Estas compuertas utilizan las características del decodificador para filtrar las
activaciones procedentes del codificador, suprimiendo regiones irrelevantes del fondo y resaltando
las zonas de interés antes de la concatenación, lo que resulta especialmente útil ante la alta
variabilidad en forma y tamaño de las lesiones tumorales.

## 2.3. Transformers de visión en imagen médica

A pesar del éxito de las CNN, la convolución convencional está limitada por su campo receptivo local,
lo que dificulta modelar relaciones contextuales de largo alcance dentro del volumen. Para superar
esta limitación se ha adaptado el paradigma de los **Transformers** a la segmentación 3D. La
arquitectura **Swin-UNETR** (Hatamizadeh et al., 2022) emplea un codificador Swin Transformer 3D
jerárquico, que calcula la autoatención mediante ventanas locales desplazadas de forma eficiente;
esto captura interacciones multiescala globales y locales, conectándose con un decodificador
convolucional para generar máscaras densas de alta resolución. Es la arquitectura Transformer-UNet
que da nombre a este trabajo.

## 2.4. Estrategias de fusión multimodal

La integración de múltiples modalidades suele clasificarse en tres categorías, resumidas en la
Tabla 1.

**Tabla 1.** Estrategias de fusión multimodal en segmentación de imagen médica.

| Estrategia de fusión | Mecanismo operativo | Limitaciones clave |
| :-- | :-- | :-- |
| Fusión temprana (*early fusion*) | Concatenación directa de las secuencias (T1n, T1c, T2w, FLAIR) en la entrada, creando un único tensor multicanal. | No incorpora un mecanismo explícito que reajuste la contribución relativa de cada modalidad según la entrada. |
| Fusión tardía (*late fusion*) | Entrenamiento de redes independientes por secuencia y combinación posterior de sus mapas de probabilidad. | Multiplica el coste computacional e ignora las correlaciones cruzadas en etapas tempranas. |
| Fusión intermedia / adaptativa | Ponderación o procesamiento dinámico de canales mediante compuertas o bloques de atención durante la codificación. | Requiere un diseño cuidadoso para equilibrar expresividad y consumo de memoria. |

Como se resume en la Tabla 1, la fusión temprana por concatenación es la opción más simple y
eficiente, mientras que las fusiones intermedias o adaptativas persiguen aprovechar mejor las
relaciones entre modalidades a costa de mayor complejidad. Este trabajo se sitúa en la frontera entre
la fusión temprana y la adaptativa: propone un mecanismo ligero de compuerta adaptativa (*adaptive
gating*) y lo somete a un estudio de ablación controlado **para evaluar si mejora la concatenación
tradicional**, sin presuponer que lo haga. El resultado de esa evaluación se presenta en el
Capítulo 5.

## 2.5. El reto BraTS y las métricas de evaluación

El *Brain Tumor Segmentation Challenge* (**BraTS**) es la iniciativa de referencia para evaluar
algoritmos de segmentación de tumores cerebrales, al proporcionar grandes conjuntos de MRI
multiparamétrica con anotaciones expertas y un protocolo de evaluación común (Bakas et al., 2018). La
edición **BraTS-GLI 2024** aborda la segmentación de gliomas en MRI post-tratamiento y define las
cuatro modalidades y las subregiones tumorales empleadas en este trabajo (de Verdier et al., 2024).
Las subregiones evaluadas son el tumor realzante (ET), el núcleo tumoral (TC) y el tumor completo
(WT), definidas de forma anidada.

La calidad de la segmentación se cuantifica con dos métricas estandarizadas en el reto:

- **Coeficiente de Dice**, que mide el solapamiento volumétrico entre la predicción y la referencia;
  toma valores en [0, 1], donde 1 indica solapamiento perfecto. Es la métrica principal de exactitud
  regional.
- **Distancia de Hausdorff al percentil 95 (HD95)**, que mide la discrepancia entre las superficies de
  ambas máscaras en milímetros, descartando el 5 % de distancias más extremas para reducir la
  sensibilidad a valores atípicos. Complementa al Dice al capturar errores de frontera que el
  solapamiento volumétrico puede no reflejar.

Ambas métricas se calculan de forma independiente por región (ET, TC, WT), lo que permite analizar el
comportamiento del modelo en cada subestructura. Su formalización operativa y las convenciones
adoptadas (casos vacíos, casos con distancia indefinida) se detallan en el Capítulo 4.
