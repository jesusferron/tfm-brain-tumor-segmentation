# Índice de la memoria del TFM

> Estructura aprobada por el tutor (respuesta CON-2026-05-28-M1, recibida 2026-06-25) y confirmada
> por el documento oficial "Instrucciones de memoria de TFM" y por tres TFM de ejemplo del mismo
> máster. Documento maestro que organiza el manuscrito en seis capítulos. El estado de cada
> capítulo y su material de partida en el repositorio se indican en la tabla.
> Convenciones de estilo, profundidad y extensión: [`guia-estilo-y-estructura.md`](guia-estilo-y-estructura.md).
> Roadmap completo del proyecto en [`plan-tfm.md`](plan-tfm.md).

Título de trabajo: **Segmentación de tumores cerebrales en resonancia magnética multimodal
mediante arquitecturas Transformer-UNet híbridas**.

## Estructura aprobada

| # | Capítulo | Contenido | Estado | Material de partida |
| :-: | :-- | :-- | :-- | :-- |
| 1 | **Introducción** | Background (gliomas, segmentación automática 3D), planteamiento del problema, pregunta de investigación, objetivos (general y específicos), organización del documento | ⬜ Pendiente | Objetivos y pregunta ya redactados en [`README.md`](README.md) |
| 2 | **Marco teórico y estado del arte** | Segmentación médica 3D; U-Net y variantes; Transformers en imagen médica (Swin-UNETR, TransBTS); fusión multimodal de modalidades MRI; el reto BraTS; métricas Dice y HD95 | ⬜ Pendiente | Tabla comparativa de repositorios ([borrador](../pre-design/tabla-comparativa-repositorios-borrador.md)) |
| 3 | **Metodología** | **Fases de alto nivel** (familiarización: revisión literaria y evaluación de datos; diseño experimental: entrenamiento de varios modelos y evaluación comparativa; protocolo de evaluación). **Sin detalle técnico** | 🟡 Re-nivelar | [`capitulo-3-metodologia.md`](capitulo-3-metodologia.md) (hoy demasiado técnico) |
| 4 | **Desarrollo** | **Detalle técnico y decisiones**: organización del código, ETL/transforms MONAI, factory de modelos, mecanismos de fusión, entrenamiento/checkpointing/inferencia, hiperparámetros, entornos de cómputo, reproducibilidad | 🟡 Sólido; absorbe el detalle de Metodología | [`capitulo-4-desarrollo.md`](capitulo-4-desarrollo.md) |
| 5 | **Resultados** | Comparativa de modelos (Dice/HD95 por ET/TC/WT); estudio de ablación de fusión; coste computacional; evaluación final sobre el split de test | ⬜ Pendiente (hay datos preliminares de val) | `outputs/evaluation/comparativa_val_5k.csv`, [vitácora](../vitacora/README.md) |
| 6 | **Conclusiones** | Respuesta a la pregunta de investigación, limitaciones, líneas de trabajo futuro | ⬜ Pendiente | — |

Material transversal: aspectos legales/licencia (CC-BY-NC 4.0, cita BraTS), tablas del dataset y
estructura del repositorio (ya redactados en [`README.md`](README.md), a reubicar en los
capítulos correspondientes).

## Decisión de reparto Metodología (cap. 3) ↔ Desarrollo (cap. 4)

El tutor indicó que la **Metodología describe las fases de alto nivel** y que **el detalle técnico,
las decisiones y las configuraciones van al Desarrollo**. El capítulo 3 actual contiene mucho
detalle técnico (transforms concretas, hiperparámetros, inferencia por ventana deslizante) que,
según ese criterio, corresponde al capítulo 4.

**Corroborado por los TFM de ejemplo:** en los tres, la Metodología ocupa solo 2-3 páginas y
describe el *proceso/fases* (metodología ágil, cronograma), nunca las técnicas; todo el detalle
técnico vive en Desarrollo. Refuerza la necesidad de re-nivelar el capítulo 3. Detalle en la
[guía de estilo](guia-estilo-y-estructura.md).

- **Reparto validado por el tutor (2026-07-13):** se re-nivela el capítulo 3 a fases de alto nivel
  y el detalle técnico se traslada al capítulo 4, evitando duplicación. Ya se puede acometer la
  reestructuración sin esperar más confirmación.
- **Acción pendiente:** ejecutar esa re-nivelación en `capitulo-3-metodologia.md` y
  `capitulo-4-desarrollo.md`.

## Decisiones de la reunión con el tutor (2026-07-13)

Reunión celebrada; cerradas las decisiones que condicionaban la redacción (detalle en
[`reunion-tutor-2026-06-29.md`](../pre-design/reunion-tutor-2026-06-29.md)):

1. **Reparto Metodología/Desarrollo:** validado (cap. 3 fases de alto nivel; detalle al cap. 4).
2. **Nivel de detalle:** confirmado (justificación clínica/técnica + diagramas de flujo y
   arquitectura; pseudocódigo solo cuando aporte).
3. **Referencias / TFM modelo:** ya resuelto con los ejemplos de Drive y la guía de estilo.
4. **Tabla comparativa de repositorios:** una sola tabla; columnas mínimas a criterio propio (sin
   ejemplo adicional del tutor).
5. **Tipos de imagen:** basta una tabla modalidad→tejido/lesión y relevancia para ET/TC/WT;
   ejemplos visuales sí, con propósito ilustrativo y analítico; exclusión de BraTS-MEN-RT justificada
   en el capítulo de tipos de imagen/dataset.
