# PROPUESTA 2

## Segmentación de Tumores Cerebrales en Resonancia Magnética Multimodal mediante Arquitecturas Transformer-UNet Híbridas

**Contexto:** PROJENER.AI SL — IA Aplicada a Medicina — Investigación Q1 Computer Science

**Área:** Neuroimagen / Neuro-Oncología

---

## Descripción y Relevancia Clínica

La segmentación precisa de gliomas en imágenes de resonancia magnética (MRI) multimodal es crítica para la planificación quirúrgica, radioterapia y seguimiento terapéutico. Los gliomas presentan formas irregulares, bordes difusos y heterogeneidad entre pacientes que dificultan la segmentación automática. Las arquitecturas puramente convolucionales capturan contexto local pero pierden relaciones de largo alcance. Este TFM propone una arquitectura híbrida que combine la eficiencia local de U-Net con la capacidad de modelar dependencias globales de los Transformers, incorporando un módulo de fusión adaptativa entre las 4 modalidades de MRI.

---

## Modelos de IA Propuestos (4-5)

| Nº | Modelo y Justificación |
|----|------------------------|
| 1 | **Swin-UNETR** — Transformer jerárquico con decodificador U-Net para segmentación volumétrica 3D |
| 2 | **nnU-Net (self-configuring)** — framework auto-adaptativo que ajusta automáticamente arquitectura e hiperparámetros al dataset |
| 3 | **Attention U-Net con puertas de atención** — focalización espacial aprendida para regiones de interés |
| 4 | **TransBTS (Transformer for Brain Tumor Segmentation)** — encoder Transformer 3D con skip connections multiescala |
| 5 | **3D U-Net con bloques residuales** — baseline convolucional puro para comparación justa |

---

## Revistas Q1 Objetivo (Indexadas en Computer Science — JCR)

- Expert Systems with Applications (Q1, CS-AI)
- Pattern Recognition (Q1, CS-AI)
- Neurocomputing (Q1, CS-AI)
- Computerized Medical Imaging and Graphics (Q1, CS-AI/Radiology)

---

## Dataset

| Campo | Detalle |
|-------|---------|
| **Nombre** | BraTS 2024 (Brain Tumor Segmentation Challenge) |
| **Enlace** | https://www.synapse.org/Synapse:syn53708249/wiki/627500 |
| **Descripción** | Dataset de referencia mundial con >2,000 casos de gliomas con 4 modalidades de MRI: T1 nativo, T1 con contraste (T1ce), T2, FLAIR. Cada caso tiene segmentaciones manuales de neuroradiólogos expertos en 3 regiones: tumor realzante (ET), núcleo tumoral (TC) y tumor completo (WT). Resolución 240×240×155 vóxeles normalizados a 1mm isotrópico. Se complementa con BraTS-Africa (https://www.synapse.org/Synapse:syn51514108) para evaluación de generalización cross-continental. |

---

## Contribución Innovadora (Justificación Q1)

Módulo de fusión adaptativa de modalidades MRI que aprende a ponderar dinámicamente T1, T1ce, T2 y FLAIR según la región tumoral que se está segmentando, combinado con aprendizaje contrastivo inter-modal que mejora la representación de bordes tumorales difusos y evaluado con protocolo cross-institutional.
