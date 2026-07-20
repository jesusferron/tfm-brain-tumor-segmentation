# 6. Conclusiones

> Capítulo de cierre: respuesta a la pregunta de investigación, grado de cumplimiento de los
> objetivos, interpretación de la contribución, limitaciones y líneas de trabajo futuro. No
> introduce tablas nuevas; se apoya en los resultados del Capítulo 5.

## 6.1. Respuesta a la pregunta de investigación

La pregunta que guio el trabajo fue si **una estrategia de fusión adaptativa de las modalidades
MRI puede mejorar la segmentación 3D de gliomas en BraTS-GLI frente a la fusión por concatenación
estándar**, manteniendo un coste computacional asumible y con mejoras consistentes en las tres
regiones (ET, TC, WT).

A la luz de los resultados sobre el conjunto de test (Capítulo 5), la respuesta es **negativa**. La
fusión por concatenación (Dice medio 0,706 ± 0,005) y la ponderación global estática (0,706 ± 0,006)
son estadísticamente indistinguibles, y **ninguna de las variantes de fusión adaptativa las supera**:
ambas obtienen medias inferiores (0,586 y 0,592) y, sobre todo, resultan **inestables**, colapsando
en una de cada tres semillas. El colapso ocurre además en semillas distintas para cada variante, lo
que descarta que se trate de una inicialización desafortunada puntual y apunta a una fragilidad
intrínseca del mecanismo. En consecuencia, no solo no se cumple la condición de mejora consistente
en ET/TC/WT, sino que la fusión adaptativa **empeora la robustez** respecto a la concatenación.

Este resultado negativo es, no obstante, un **desenlace científicamente válido y bien fundamentado**:
se sostiene sobre una evaluación en un conjunto de test reservado, con modelos entrenados hasta
convergencia y repetidos con múltiples semillas, y va acompañado de un diagnóstico que explica el
porqué (§6.3).

## 6.2. Grado de cumplimiento de los objetivos

Frente a los tres niveles de éxito definidos al inicio del trabajo (Capítulo 1), el balance es el
siguiente:

- **Nivel mínimo — alcanzado.** Se construyó un *pipeline* reproducible de extremo a extremo (control
  de calidad, particiones versionadas, entrenamiento, inferencia y evaluación), se entrenó un
  *baseline* 3D y se evaluó internamente sobre BraTS-GLI 2024.
- **Nivel objetivo (defendible) — alcanzado.** Se cubrieron sus tres pilares: un **baseline fuerte**
  (nnU-Net, Dice medio 0,829, referencia del trabajo), un **Transformer-UNet** (Swin-UNETR, 0,752, el
  mejor de los modelos propios) y un **estudio de ablación** de las estrategias de fusión. Que el
  tercer pilar arroje un resultado negativo no invalida el nivel: el objetivo era estudiar la
  fusión con rigor, y ese estudio se completó.
- **Nivel ambicioso — no abordado.** La robustez ante modalidades ausentes o degradadas y la fusión
  neuronal más profunda quedan como trabajo futuro (§6.5).

En términos de arquitecturas, los resultados confirman la jerarquía esperada (nnU-Net > Swin-UNETR >
Attention U-Net > U-Net residual) y respaldan la orientación Transformer-UNet que da nombre al
trabajo, si bien los valores absolutos de los modelos propios (~0,75 el mejor) se sitúan por debajo
del estado del arte en BraTS (~0,85–0,90), diferencia atribuible al presupuesto de entrenamiento y a
las decisiones de resolución y tamaño de lote adoptadas por restricciones de cómputo (§6.4).

## 6.3. Interpretación de la contribución: un estudio crítico de la fusión multimodal

La contribución del trabajo se reformula, a la vista de los resultados, de una *propuesta de mejora*
a un **estudio crítico de estrategias de fusión multimodal**. Su valor reside en tres aportaciones:

1. **Evidencia rigurosa de un resultado negativo.** Una idea a priori razonable —ponderar las
   modalidades de forma adaptativa según cada caso— se evalúa con un protocolo sólido (test
   reservado, convergencia, multi-semilla) y se demuestra que no aporta mejora y sí inestabilidad.
   Documentar resultados negativos con rigor tiene valor metodológico, pues evita que otros repitan
   una vía improductiva.
2. **Diagnóstico del porqué.** Se identificó que la compuerta adaptativa, incluso cuando no colapsa,
   aprende pesos casi idénticos entre casos: su señal de condicionamiento —un resumen global de las
   modalidades ya normalizadas— es prácticamente constante, por lo que la compuerta degenera en una
   ponderación estática equivalente a la variante global, pero pagando el sobrecoste de una
   optimización inestable. La variante enriquecida con media y desviación típica se diseñó para
   dotarla de una señal por caso y tampoco evitó el colapso.
3. **Confirmación de una línea base robusta.** El estudio establece que, en este montaje, la
   **concatenación es una estrategia de fusión simple, estable y suficiente**, frente a alternativas
   más complejas que no la superan.

## 6.4. Limitaciones

Los resultados deben interpretarse dentro de las siguientes limitaciones:

- **Dominio único.** El trabajo se circunscribe a BraTS-GLI 2024; no se evaluó la generalización a
  otras colecciones o instituciones.
- **Rendimiento por debajo del estado del arte.** Por restricciones de cómputo, el entrenamiento usó
  un presupuesto de 15.000 pasos, parche 128³ y lote efectivo pequeño; los valores absolutos de los
  modelos propios son, por ello, inferiores a los de configuraciones de referencia con
  entrenamientos mucho más largos y mayor lote.
- **nnU-Net como referencia de una sola corrida.** El *baseline* fuerte se entrenó con un único
  *fold* y una semilla; actúa como techo orientativo, no como medida con barras de error.
- **Fusión únicamente a nivel de entrada.** Las estrategias estudiadas reponderan los canales antes
  de la red; no se exploraron fusiones a nivel de características intermedias, que podrían comportarse
  de forma distinta.
- **Heterogeneidad de entornos.** Los modelos ligeros se entrenaron en MPS (sin AMP) y los pesados en
  CUDA (con AMP); aunque el protocolo experimental es común, los tiempos no son directamente
  comparables entre entornos.

## 6.5. Líneas de trabajo futuro

- **Fusión a nivel de características.** Explorar mecanismos de fusión más profundos (atención
  cruzada entre modalidades en las capas intermedias) en lugar de la reponderación a la entrada, así
  como técnicas que estabilicen la compuerta adaptativa (regularización, *warmup* específico) si se
  desea rescatar esa vía.
- **Robustez ante modalidades ausentes o degradadas** (nivel ambicioso), de alto interés clínico
  cuando no se dispone de las cuatro secuencias MRI.
- **Aproximación al estado del arte** aumentando el presupuesto de entrenamiento, el tamaño de lote y
  la resolución, para situar los modelos propios en su rendimiento potencial.
- **Ampliación del abanico de arquitecturas** (por ejemplo, TransBTS u otras híbridas) y
  **consolidación estadística** de nnU-Net con validación cruzada por *folds* y múltiples semillas.
- **Validación de la generalización** en conjuntos externos a BraTS-GLI para evaluar la
  transferibilidad de las conclusiones.

En síntesis, el trabajo entrega un *pipeline* reproducible y una comparación rigurosa de
arquitecturas y estrategias de fusión sobre BraTS-GLI 2024, y responde a su pregunta de
investigación con un resultado negativo sólido: la fusión adaptativa, tal como se ha formulado, no
mejora a la concatenación estándar y compromete la robustez del entrenamiento.
