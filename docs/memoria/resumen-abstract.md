# Resumen

La segmentación automática de gliomas en resonancia magnética multimodal puede facilitar la
cuantificación de las regiones tumorales, pero exige integrar información complementaria de las
secuencias T1 nativa, T1 con contraste, T2 y FLAIR. Este Trabajo de Fin de Máster estudia si una
ponderación explícita, adaptativa y ligera de estas modalidades mejora la segmentación 3D frente a
su concatenación directa. Para ello se construyó un *pipeline* reproducible basado en MONAI y
PyTorch sobre BraTS-GLI 2024, con control de calidad, particiones versionadas, entrenamiento por
parches, inferencia por ventana deslizante y evaluación mediante Dice y HD95 para el tumor
realzante (ET), el núcleo tumoral (TC) y el tumor completo (WT).

La comparación principal mantuvo fija una Residual U-Net 3D y evaluó, con tres semillas y un
presupuesto común de 15.000 pasos, la concatenación, una ponderación global estática y dos
compuertas adaptativas. La concatenación alcanzó un Dice medio de 0,706 ± 0,005 y la ponderación
global 0,706 ± 0,006. Las variantes adaptativas obtuvieron 0,586 ± 0,169 y 0,592 ± 0,171,
respectivamente; en cada una apareció una corrida de bajo rendimiento entre las tres repeticiones.
Por tanto, en las condiciones evaluadas no se obtuvo evidencia de que las compuertas propuestas
mejoren de forma consistente la concatenación. El análisis de sus pesos mostró además muy poca
variación entre estudios, resultado compatible con una señal de condicionamiento limitada, aunque
no permite establecer la causa del rendimiento observado.

Como contextualización arquitectónica, Swin-UNETR obtuvo 0,752 ± 0,017 y Attention U-Net
0,735 ± 0,006. Una única corrida de nnU-Net `3d_fullres`, empleada como referencia externa, alcanzó
0,829. Estas cifras se interpretan descriptivamente porque nnU-Net utiliza un protocolo propio y
porque no todas las familias comparten exactamente el entorno y la inferencia. La partición de
evaluación se generó por estudio, no por sujeto, por lo que existe solapamiento longitudinal de
sujetos entre particiones y los resultados no representan una estimación independiente de
generalización a pacientes nuevos. Esto no invalida la comparación interna bajo el reparto común,
pero limita la interpretación clínica de sus valores. La conclusión se restringe a los mecanismos
de fusión temprana y al protocolo analizado: la concatenación fue la alternativa más parsimoniosa y
una de las de menor variabilidad, sin que ello implique que otras formulaciones de fusión adaptativa
sean ineficaces.

**Palabras clave:** segmentación de gliomas; resonancia magnética multimodal; BraTS-GLI 2024;
aprendizaje profundo; fusión adaptativa; MONAI; segmentación 3D.

# Abstract

Automatic glioma segmentation from multimodal magnetic resonance imaging may support quantitative
assessment of tumour regions, but it requires integrating complementary information from native T1,
contrast-enhanced T1, T2, and FLAIR sequences. This Master's Thesis investigates whether an
explicit, lightweight, input-conditioned weighting of these modalities improves 3D segmentation
over direct channel concatenation. A reproducible MONAI- and PyTorch-based pipeline was developed
for BraTS-GLI 2024, covering quality control, versioned data partitions, patch-based training,
sliding-window inference, and evaluation with Dice and HD95 for enhancing tumour (ET), tumour core
(TC), and whole tumour (WT).

The main comparison kept a 3D Residual U-Net fixed and evaluated direct concatenation, static global
weighting, and two adaptive gates using three seeds and a common budget of 15,000 training steps.
Concatenation achieved a mean Dice of 0.706 ± 0.005, while static global weighting achieved
0.706 ± 0.006. The two adaptive variants reached 0.586 ± 0.169 and 0.592 ± 0.171, respectively;
each exhibited one low-performance run among the three repetitions. Under the evaluated conditions,
the experiments therefore provided no evidence that the proposed gates consistently improve upon
concatenation. Their learned weights also varied very little across studies, which is compatible
with a limited conditioning signal but does not establish the cause of the observed performance.

For architectural context, Swin-UNETR achieved 0.752 ± 0.017 and Attention U-Net 0.735 ± 0.006. A
single nnU-Net `3d_fullres` run, used as an external reference, achieved 0.829. These results are
interpreted descriptively because nnU-Net follows its own pipeline and the model families do not all
share exactly the same execution and inference settings. The evaluation partition was created at
the study level rather than the subject level; longitudinal subject overlap therefore exists across
partitions, and the reported values are not an independent estimate of generalisation to unseen
patients. This does not invalidate the internal comparison under the common split, but it limits the
clinical interpretation of those values. The conclusion is restricted to the early-fusion
mechanisms and protocol examined here: concatenation was the most parsimonious option and one of the
least variable, without implying that other adaptive-fusion formulations are ineffective.

**Keywords:** glioma segmentation; multimodal magnetic resonance imaging; BraTS-GLI 2024; deep
learning; adaptive fusion; MONAI; 3D segmentation.
