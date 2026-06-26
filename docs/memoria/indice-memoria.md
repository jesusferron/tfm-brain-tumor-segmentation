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

- **Acción pendiente:** re-nivelar el capítulo 3 a fases de alto nivel y trasladar el detalle
  técnico al capítulo 4, evitando duplicación.
- **Confirmar el reparto exacto en la reunión** (tema 1 de la reunión pendiente; ver
  [`consulta-tutor-2026-05-28.md`](../pre-design/consulta-tutor-2026-05-28.md)). No se invierte
  esfuerzo grande en la reestructuración hasta confirmarlo.

## Pendiente de la reunión con el tutor

Bloquea o condiciona varias decisiones de redacción (ver consulta 2026-05-28):

1. Reparto exacto Metodología/Desarrollo.
2. Nivel de detalle objetivo (justificación clínica/técnica, pseudocódigo, diagramas de flujo).
3. Referencias o TFM modelo para estilo y profundidad.
4. Columnas (aspectos evaluados) de la tabla comparativa de repositorios.
5. Tres preguntas del bloque de tipos de imagen (caracterización clínica por modalidad,
   ejemplos visuales en la memoria, ubicación de la justificación para excluir BraTS-MEN-RT).
