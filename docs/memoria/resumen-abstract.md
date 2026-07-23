# Resumen

La resonancia magnética permite observar los gliomas y medir su extensión. Para ello deben
delimitarse las distintas zonas del tumor en imágenes tridimensionales, una tarea manual lenta y que
requiere experiencia. Ningún tipo de imagen muestra por sí solo toda la lesión, por lo que suelen
combinarse cuatro secuencias complementarias: T1, T1 con contraste, T2 y FLAIR. Este Trabajo de Fin
de Máster estudia si ajustar automáticamente la importancia de cada secuencia mejora la segmentación
frente a combinarlas directamente.

Sobre 1.621 estudios con máscara de BraTS-GLI 2024 se implementó un sistema MONAI con particiones
versionadas y configuraciones YAML. Manteniendo fijos la Residual U-Net 3D, los datos y el
entrenamiento, se compararon cuatro formas de combinar las imágenes: concatenación directa,
ponderación global aprendida e independiente de la entrada y dos métodos adaptativos. Cada
estrategia se entrenó con tres semillas. El
rendimiento se midió principalmente con Dice, una puntuación entre 0 y 1 que indica cuánto coincide
el resultado automático con la segmentación de referencia; cuanto mayor es el valor, mejor es la
coincidencia.

La concatenación directa y la ponderación global aprendida obtuvieron un Dice medio de 0,706. Los
métodos adaptativos quedaron alrededor de 0,59 y fueron más variables, con una ejecución
de bajo rendimiento en cada caso. Un diagnóstico exploratorio de ejecuciones preliminares sobre 40
volúmenes completos mostró pesos casi constantes entre estudios; como el modelo opera con parches y
ventanas, esta comprobación no determina su variación durante la segmentación ni describe los
puntos de control finales. En cualquier caso, los métodos adaptativos no ofrecieron una mejora
consistente. Otros modelos, incluido uno basado en Transformers, se evaluaron únicamente como
referencia para situar este resultado en un contexto más amplio.

Los datos se separaron por estudio de imagen y no por paciente, de modo que exploraciones de una
misma persona pueden aparecer en conjuntos diferentes. El reparto permite comparar las estrategias
entre sí, pero no medir de forma independiente el rendimiento en pacientes nuevos ni demostrar
utilidad clínica. En las condiciones analizadas, la concatenación directa fue la opción más sencilla
y una de las más estables. Esta conclusión se limita a los métodos estudiados y no descarta otros
diseños adaptativos.

**Palabras clave:** segmentación de gliomas; resonancia magnética multimodal; BraTS-GLI 2024;
aprendizaje profundo; fusión adaptativa; MONAI; segmentación 3D.

# Abstract

Magnetic resonance imaging makes it possible to observe gliomas and assess their extent. This
requires delineating different tumour regions in three-dimensional images, a slow manual task that
demands expertise. No single type of image shows the entire lesion, so four complementary MRI
sequences are commonly combined: T1, contrast-enhanced T1, T2, and FLAIR. This Master's Thesis
examines whether automatically adjusting the importance of each sequence improves segmentation
compared with combining them directly.

A MONAI system with versioned data splits and YAML configurations was implemented using 1,621
labelled studies from BraTS-GLI 2024. Four ways of combining the images were compared while keeping
the same 3D Residual U-Net, data, and training: direct concatenation, learned global,
input-independent weighting, and two adaptive methods. Each strategy was trained with three seeds.
Performance was measured mainly with Dice, a score between 0 and 1 that indicates how closely the
automatic result matches the reference segmentation; a higher value means greater agreement.

Direct concatenation and learned global, input-independent weighting both achieved a mean Dice
score of 0.706. The adaptive methods scored around 0.59 and were more variable, with one
low-performing run in each case. An exploratory diagnostic of preliminary runs on 40 full volumes
found nearly constant weights across studies; because the model operates on patches and sliding
windows, this check does not establish how much the weights vary during segmentation or describe
the final checkpoints. In any case, the adaptive methods did not provide a consistent improvement.
Other models, including a Transformer-based model, were evaluated only as references to place this
result in a broader context.

The data were split by imaging study rather than by patient, so scans from the same person may
appear in different sets. This supports a comparison between the strategies, but it does not
independently measure performance on new patients or demonstrate clinical usefulness. Under the
evaluated conditions, direct concatenation was the simplest option and one of the most stable. This
conclusion is limited to the methods studied and does not rule out other adaptive designs.

**Keywords:** glioma segmentation; multimodal magnetic resonance imaging; BraTS-GLI 2024; deep
learning; adaptive fusion; MONAI; 3D segmentation.
