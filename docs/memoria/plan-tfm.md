# Plan global del TFM

> Roadmap del proyecto hasta la entrega, anclado a los criterios de éxito de
> [`decisiones-iniciales.md §10`](../pre-design/decisiones-iniciales.md) y a la estructura de
> manuscrito aprobada por el tutor ([índice](indice-memoria.md)).
> Última revisión: 2026-07-13 (tras la reunión con el tutor; decisiones en
> [`reunion-tutor-2026-06-29.md`](../pre-design/reunion-tutor-2026-06-29.md) y
> [vitácora 2026-07-13](../vitacora/README.md)). No hay restricción fuerte de calendario
> (`decisiones-iniciales.md`), por lo que el plan se ordena por dependencias, no por fechas.

## 1. Criterios de éxito y estado

| Nivel | Definición | Estado |
| :-- | :-- | :-- |
| **Mínimo** | Pipeline reproducible + baseline 3D + evaluación interna BraTS-GLI | ✅ Alcanzado |
| **Objetivo (defendible)** | Baseline fuerte (nnU-Net) + Transformer-UNet (Swin) + ablación de fusión | 🟡 2 de 3 pilares cerrados; falta consolidar la ablación |
| **Ambicioso** | Robustez ante modalidades faltantes / fusión neuronal | ⬜ No iniciado |

Estado por pilar del objetivo defendible:

| Pilar | Estado |
| :-- | :-- |
| Ablación de fusión | 🟡 Resultados preliminares (val, 5000 pasos, 1 semilla). `adaptive_gating` no sostiene aún la hipótesis |
| Transformer-UNet (Swin-UNETR) | ✅ Entrenado en L4 (5000 pasos, 1 semilla): mean Dice val 0.715 (ET 0.567 / TC 0.745 / WT 0.834) |
| Baseline fuerte (nnU-Net) | ✅ Entrenado en A100 (3d_fullres, fold 0, 250 épocas). **Referencia/techo**: mean Dice val 0.835 (ET 0.719 / TC 0.874 / WT 0.913) |

**Mensaje clave:** el TFM ya supera el mínimo y tiene cerrados los pilares 1 y 2. nnU-Net marca el
techo de referencia (mean Dice 0.835) y Swin-UNETR es el mejor de los modelos propios (0.715),
resolviendo el riesgo título vs. evidencia. Falta consolidar el pilar 3 (ablación de fusión), en
duda por el bajo rendimiento de la fusión adaptativa. **Aviso:** la comparativa actual mezcla
presupuestos (nnU-Net a convergencia vs. modelos propios a 5000 pasos); la comparación
arquitectónica justa requiere la corrida final a convergencia para todos.

**Restricciones confirmadas por el alumno (2026-06-26):**

- **Swin-UNETR y nnU-Net son obligatorios** para el scope/título; no se reformula el alcance. El
  track experimental en cloud no es opcional.
- **No se acepta un resultado negativo** de la fusión adaptativa hasta agotar todas las vías dentro
  del alcance. Límite acordado con el tutor (2026-07-13): **2-3 días de ejecución** (corridas largas
  + ajuste de la compuerta: warmup, lr específico, regularización). Superado ese presupuesto sin
  mejora sobre el baseline concat, se puede reportar como resultado negativo defendible.

## 2. Track A — Experimental (cómputo)

Ruta crítica; cada paso habilita el siguiente:

1. ✅ **I/O en cloud resuelto** — copia del dataset al disco local del runtime (el cache de
   preprocesado desbordaba el disco; ver [vitácora 2026-07-14](../vitacora/README.md)).
2. ✅ **Swin-UNETR entrenado** en L4 (Transformer que da nombre al TFM). *(Pilar 2)*
3. ✅ **nnU-Net entrenado y evaluado** como baseline fuerte externo (mean Dice val 0.835). *(Pilar 1)*
4. **Resolver `adaptive_gating`** — corrida larga + warmup / lr específico de la compuerta /
   regularización; decide si la hipótesis es positiva o vira a resultado negativo defendible.
   Independiente; abordable en local. *(Pilar 3)*
5. **Corrida final** — más pasos + multi-semilla (barras de error) → **evaluación sobre el split
   de test reservado** (hasta ahora solo se ha tocado val).
6. *(Ambicioso, opcional)* TransBTS; robustez ante modalidades degradadas/faltantes.

Decisiones de hardware (ver vitácora): **L4 para desarrollo/optimización, A100 solo para las
corridas finales largas.** Cualquier cambio de hiperparámetros se registra en la vitácora con su
justificación.

## 3. Track B — Redacción (sin cómputo)

Seis capítulos de la estructura aprobada (detalle y estado en [`indice-memoria.md`](indice-memoria.md)):

1. Introducción ⬜
2. Marco teórico y estado del arte ⬜
3. Metodología 🟡 (re-nivelar a fases de alto nivel)
4. Desarrollo 🟡 (sólido; absorbe el detalle técnico)
5. Resultados ⬜ (hay datos preliminares de val)
6. Conclusiones ⬜

Tareas transversales:
- Actualizar el README maestro (desactualizado, 2026-05-26).
- Tabla comparativa de repositorios (tutor T1): definir columnas y completar el borrador.
- Preparar los inputs de la reunión con el tutor (reformular las 3 preguntas de tipos de imagen,
  propuesta de reparto cap. 3/4, propuesta de columnas de la tabla T1).

## 4. Dependencias y secuenciación

- **Reunión con el tutor celebrada (2026-07-13):** cerradas las decisiones que condicionaban la
  redacción — reparto Metodología/Desarrollo (validado), nivel de detalle (confirmado), tabla T1
  (una sola tabla), tipos de imagen (tabla modalidad→tejido + ejemplos visuales). Ya no hay bloqueo
  del tutor para avanzar en los capítulos. Detalle en
  [`reunion-tutor-2026-06-29.md`](../pre-design/reunion-tutor-2026-06-29.md).
- El **arreglo de I/O** no depende del tutor y es prerrequisito de Swin + nnU-Net + finales.
- `adaptive_gating` define la narrativa (positiva vs negativa) pero no urge hasta poder hacer una
  corrida larga limpia (tras el I/O), salvo que se quiera diagnosticar ya en local.

### Orden recomendado (dos frentes en paralelo, sin trabajo desperdiciado)

**Inmediato (Track B, cero cómputo):**
- [x] Índice maestro de los 6 capítulos.
- [x] Inputs de la reunión y reunión celebrada (2026-07-13); decisiones cerradas.
- [ ] Re-nivelar el cap. 3 a fases de alto nivel y trasladar el detalle técnico al cap. 4.
- [ ] Actualizar el README maestro.
- [ ] Completar la tabla comparativa (una sola tabla, columnas mínimas).
- [ ] Cap. tipos de imagen: tabla modalidad→tejido/lesión + selección de cortes ilustrativos/analíticos.

**En cuanto se decida gastar GPU (Track A, ruta crítica):**
- [ ] Arreglo de I/O (cache MONAI + copia a runtime).
- [ ] Swin-UNETR (título) y nnU-Net (baseline fuerte).
- [ ] Resolver `adaptive_gating`.
- [ ] Corrida final multi-semilla + evaluación en test.

**Cuando haya resultados consolidados:**
- [ ] Capítulo 5 (Resultados) con la comparativa final.
- [ ] Introducción, Marco teórico/Estado del arte, Conclusiones.

## 5. Riesgos abiertos

- ~~**Título vs. evidencia:**~~ **RESUELTO (2026-07-14):** Swin-UNETR entrenado en L4 y es el mejor
  modelo (mean Dice val 0.715). El pilar 2 queda cubierto.
- **Contribución en duda:** `adaptive_gating` rinde por debajo del baseline en la corrida
  preliminar. Si se confirma, el TFM debe reescribirse como resultado negativo defendible.
- **Resultados aún preliminares:** 5000 pasos, una semilla, sin converger, evaluados en val (no
  test). No reportables como finales. Aplica también a Swin: buen resultado pero probablemente
  infraentrenado a 5000 pasos (62M parámetros).
