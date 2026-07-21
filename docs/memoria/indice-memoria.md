# Índice de la memoria del TFM

> Estructura aprobada por el tutor (respuesta CON-2026-05-28-M1, recibida el 2026-06-25) y
> contrastada con las instrucciones oficiales y los TFM de referencia. Última actualización:
> 2026-07-21.

Título de trabajo: **Segmentación de tumores cerebrales en resonancia magnética multimodal
mediante arquitecturas Transformer-UNet híbridas**.

## Estructura del documento

La memoria se organiza en seis capítulos, precedidos por el resumen y el *abstract*, y seguidos por
las referencias bibliográficas y el apéndice de reproducibilidad.

| Orden | Sección | Contenido | Estado | Fuente |
| :-: | :-- | :-- | :-- | :-- |
| — | **Resumen y Abstract** | Síntesis, palabras clave y principales resultados en español e inglés | ✅ Redactado | [`resumen-abstract.md`](resumen-abstract.md) |
| 1 | **Introducción** | Contexto clínico y de IA, problema, pregunta de investigación, objetivos y organización | ✅ Texto revisado | [`capitulo-1-introduccion.md`](capitulo-1-introduccion.md) |
| 2 | **Marco teórico y estado del arte** | Segmentación 3D, U-Net, atención, Transformers, nnU-Net, fusión multimodal, BraTS y métricas | ✅ Texto revisado | [`capitulo-2-marco-teorico.md`](capitulo-2-marco-teorico.md) |
| 3 | **Metodología** | Metodología *ad hoc* de cinco fases y cronograma, sin duplicar el detalle técnico | ✅ Reorganizado y redactado | [`capitulo-3-metodologia.md`](capitulo-3-metodologia.md) |
| 4 | **Desarrollo** | Implementación por fases: datos, entorno, MONAI, modelos, fusión, entrenamiento, inferencia y métricas | ✅ Reorganizado y redactado | [`capitulo-4-desarrollo.md`](capitulo-4-desarrollo.md) |
| 5 | **Resultados** | Ablación de fusión, comparación descriptiva de arquitecturas, HD95, coste y análisis cualitativo | ✅ Resultados finales incorporados | [`capitulo-5-resultados.md`](capitulo-5-resultados.md), `outputs/evaluation/final_all_test.csv` |
| 6 | **Conclusiones** | Respuesta acotada, cumplimiento de objetivos, contribución, limitaciones y trabajo futuro | ✅ Redactado con alcance prudente | [`capitulo-6-conclusiones.md`](capitulo-6-conclusiones.md) |
| — | **Referencias bibliográficas** | Bibliografía completa en formato autor-año | ✅ Revisadas; 34 fuentes | [`capitulo-7-referencias.md`](capitulo-7-referencias.md) |
| — | **Apéndice A. Reproducibilidad** | Repositorio, commit, comandos, artefactos, condiciones de acceso y límites | ✅ Redactado; pendiente fijar commit final | [`apendice-reproducibilidad.md`](apendice-reproducibilidad.md) |

Convenciones de estilo, extensión y maquetación:
[`guia-estilo-y-estructura.md`](guia-estilo-y-estructura.md). Estado de cierre y tareas pendientes:
[`plan-tfm.md`](plan-tfm.md).

## Metodología y desarrollo

La separación acordada con el tutor ya está aplicada:

- el Capítulo 3 describe las cinco fases y el cronograma a alto nivel;
- el Capítulo 4 desarrolla las decisiones, configuraciones e implementación de cada fase;
- los detalles técnicos no se duplican de forma sistemática entre ambos capítulos.

El material transversal solicitado también está integrado: la tabla comparativa de herramientas se
encuentra en el Capítulo 2; los datos, modalidades y flujo experimental en el Capítulo 4; las
comparaciones cuantitativas y cualitativas en el Capítulo 5; y las condiciones de reproducción y de
acceso a los datos en el Apéndice A.

## Estado de figuras y tablas

- Tablas del texto principal numeradas consecutivamente de la Tabla 1 a la Tabla 15, más la Tabla
  A.1 del apéndice.
- Figuras utilizadas numeradas de la Figura 1 a la Figura 4.
- La Figura 1 presenta la visión global del sistema y separa la ruta MONAI del *pipeline* propio de
  nnU-Net.
- Las Figuras 3 y 4 utilizan terminología coherente con el análisis descriptivo de las corridas.

## Integración y entrega final

Los contenidos Markdown ya están integrados en un borrador reproducible basado en la plantilla
oficial. Antes de la entrega todavía deben completarse los datos formales de portada, actualizarse
en Word el índice general, el índice de figuras y el índice de tablas, fijarse la referencia de
versión del apéndice y exportarse el PDF definitivo.
