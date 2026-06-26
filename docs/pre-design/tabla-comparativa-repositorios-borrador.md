# Tabla comparativa de repositorios (borrador para reunion)

Fecha: 2026-06-25
Estado: borrador para llevar a la reunion con el tutor. La estructura definitiva (columnas, filas y formato) se cerrara con sus ejemplos.

Origen: el tutor aclaro en su respuesta del 2026-06-25 que por "tablas del repositorio" se referia a una tabla comparativa con los repositorios evaluados como filas y los aspectos evaluados como columnas (`docs/pre-design/consulta-tutor-2026-05-28.md`, CON-2026-05-28-T1).

## Objetivo de la tabla

Documentar de forma trazable que repositorios/implementaciones se revisaron como candidatos para el TFM y bajo que criterios se decidio usarlos, descartarlos o tratarlos como referencia. La tabla vive en el capitulo de Marco teorico y estado del arte y se referencia desde el de Desarrollo cuando se justifique cada eleccion tecnica.

## Propuesta de columnas (aspectos evaluados)

Agrupadas por familia. La idea es discutir con el tutor cuales mantener y cuales mover a notas a pie.

### A. Identidad del repositorio

| Columna | Descripcion | Por que esta |
| --- | --- | --- |
| Nombre | Nombre canonico (ej. MONAI, nnU-Net, Swin-UNETR, TransBTS). | Identificacion. |
| Autor / mantenedor | Equipo u organizacion responsable. | Atribucion y credibilidad. |
| URL / version | Repositorio publico y version/commit usado. | Reproducibilidad. |
| Licencia | Apache 2.0, MIT, BSD, GPL, no comercial, etc. | Restricciones de uso, especialmente con datos CC-BY-NC. |

### B. Caracterizacion tecnica

| Columna | Descripcion | Por que esta |
| --- | --- | --- |
| Tipo | Framework (MONAI), arquitectura concreta (Swin-UNETR), pipeline auto-configurable (nnU-Net) o utilidad. | Permite no mezclar peras con manzanas en filas. |
| Arquitectura(s) que provee | Si aplica: U-Net 3D, Attention U-Net, Swin-UNETR, etc. | Trazabilidad arquitectonica. |
| Framework base | PyTorch, TensorFlow, JAX. | Compatibilidad con el resto del pipeline. |
| Soporte 3D nativo | Si/No/Parcial. | Critico para BraTS 3D. |
| Soporte multimodal | Si/No/Limitado. | BraTS-GLI usa 4 modalidades MRI. |

### C. Encaje con BraTS y MONAI

| Columna | Descripcion | Por que esta |
| --- | --- | --- |
| Compatibilidad BraTS | Soporta directamente el formato/etiquetas, requiere conversion o no aplica. | Coste de adopcion. |
| Integracion con MONAI | Nativo, posible via wrapper o externo. | Decision pendiente sobre nnU-Net dentro de MONAI. |
| Preprocesamiento incluido | Que provee de fabrica (normalizacion, resampling, cropping). | Evita reimplementar. |
| Metricas Dice/HD95 incluidas | Si/No/Parcial. | Alineacion con el protocolo del TFM. |

### D. Madurez y reproducibilidad

| Columna | Descripcion | Por que esta |
| --- | --- | --- |
| Mantenimiento | Actividad reciente (ultimo commit, releases). | Riesgo de bit-rot. |
| Documentacion | Nivel (tutoriales, API docs, ejemplos BraTS). | Coste de entrada. |
| Reproducibilidad | Configs, semillas, splits documentados. | Requisito del TFM. |
| Adopcion | Citas relevantes, uso en BraTS challenge, stars (referencial, no determinante). | Senal de robustez. |

### E. Decision para el TFM

| Columna | Descripcion | Por que esta |
| --- | --- | --- |
| Rol en el TFM | Framework base, baseline fuerte, modelo Transformer, modelo hibrido, referencia conceptual, descartado. | Conecta la tabla con el diseno experimental. |
| Decision | Usado / descartado / a evaluar. | Trazabilidad de la decision. |
| Motivo de la decision | Justificacion breve (encaje, licencia, coste, mantenimiento). | Defensa de la eleccion. |

## Filas candidatas (repositorios a incluir)

Borrador inicial, a confirmar con el tutor. Algunos son frameworks y otros son implementaciones puntuales: si se prefiere, se pueden separar en dos tablas.

| Repositorio | Rol previsto |
| --- | --- |
| MONAI (Project-MONAI/MONAI) | Framework base de la pipeline propia. |
| nnU-Net (MIC-DKFZ/nnUNet) | Baseline fuerte de referencia (interno o externo). |
| Swin-UNETR (en MONAI; tambien Project-MONAI/research-contributions) | Modelo Transformer-UNet del catalogo. |
| TransBTS (Wenxuan-1119/TransBTS) | Modelo hibrido especifico para tumores cerebrales. |
| Attention U-Net (ozan-oktay/Attention-Gated-Networks o variante MONAI) | Variante atencional intermedia. |
| 3D U-Net residual (variante implementada en `tfm_brats/monai_pipeline.py`) | Baseline convolucional controlado. |
| BraTS challenge winners (referencias) | Contexto del estado del arte; no se ejecutan. |

## Version minima viable

Si la tabla anterior resulta excesiva, esta es la version minima que aporta valor por si sola y se puede ampliar despues:

| Repositorio | Tipo | Licencia | Framework | Soporte 3D / multimodal | Integracion con MONAI | Rol en TFM | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MONAI | Framework | Apache 2.0 | PyTorch | Si / Si | Nativo | Pipeline base | Usado |
| nnU-Net | Pipeline auto-config | Apache 2.0 | PyTorch | Si / Si | Externo (estudio de integracion pendiente) | Baseline fuerte | Usado |
| Swin-UNETR | Arquitectura | Apache 2.0 (via MONAI) | PyTorch / MONAI | Si / Si | Nativo | Modelo Transformer-UNet | Usado |
| TransBTS | Arquitectura | Apache 2.0 | PyTorch | Si / Si | No (portado manual) | Hibrido especifico tumores | A evaluar |
| Attention U-Net | Arquitectura | MIT (impl. original) / Apache 2.0 (impl. MONAI) | PyTorch / MONAI | Si / Si | Nativo | Variante atencional intermedia | Usado |

## Formato y ubicacion

- Borrador y trazabilidad: este documento en `docs/pre-design/`.
- Version definitiva: tabla en el capitulo de Marco teorico y estado del arte de la memoria, con la version compacta. La version extendida puede quedar como anexo.
- Datos crudos (URLs, versiones, commits): CSV versionado en `data/` o en una subcarpeta `docs/memoria/tablas/` si conviene mantener juntos los artefactos de la memoria.

## Preguntas concretas para la reunion

1. Confirmar si la tabla cubre frameworks e implementaciones juntas o se separan en dos.
2. Validar las columnas: cuales son esenciales, cuales sobran y cuales faltan.
3. Ver al menos un ejemplo del tutor para alinear formato y profundidad.
4. Decidir formato definitivo (markdown en la memoria, CSV versionado, ambos).
