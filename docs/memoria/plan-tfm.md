# Plan global del TFM

> Roadmap del proyecto hasta la entrega, anclado a los criterios de éxito de
> [`decisiones-iniciales.md §10`](../pre-design/decisiones-iniciales.md) y a la estructura de
> manuscrito aprobada por el tutor ([índice](indice-memoria.md)).
> Última revisión: 2026-06-26. No hay restricción fuerte de calendario
> (`decisiones-iniciales.md`), por lo que el plan se ordena por dependencias, no por fechas.

## 1. Criterios de éxito y estado

| Nivel | Definición | Estado |
| :-- | :-- | :-- |
| **Mínimo** | Pipeline reproducible + baseline 3D + evaluación interna BraTS-GLI | ✅ Alcanzado |
| **Objetivo (defendible)** | Baseline fuerte (nnU-Net) + Transformer-UNet (Swin) + ablación de fusión | 🟡 1 de 3 pilares en marcha |
| **Ambicioso** | Robustez ante modalidades faltantes / fusión neuronal | ⬜ No iniciado |

Estado por pilar del objetivo defendible:

| Pilar | Estado |
| :-- | :-- |
| Ablación de fusión | 🟡 Resultados preliminares (val, 5000 pasos, 1 semilla). `adaptive_gating` no sostiene aún la hipótesis |
| Transformer-UNet (Swin-UNETR) | ⬜ Sin entrenar (da nombre al TFM; ~124 s/paso en MPS → requiere cloud) |
| Baseline fuerte (nnU-Net) | ⬜ Solo smoke test de conversión |

**Mensaje clave:** el TFM ya supera el mínimo; faltan 2 de los 3 pilares del objetivo defendible
(Transformer y baseline fuerte), y el tercero (ablación) está en duda por el bajo rendimiento
actual de la fusión adaptativa.

**Restricciones confirmadas por el alumno (2026-06-26):**

- **Swin-UNETR y nnU-Net son obligatorios** para el scope/título; no se reformula el alcance. El
  track experimental en cloud no es opcional.
- **No se acepta un resultado negativo** de la fusión adaptativa hasta agotar todas las vías dentro
  del alcance (con límites de tiempo y coste a acordar con el tutor). Esto fija la estrategia del
  pilar de ablación: invertir en corridas largas + ajuste de la compuerta antes de concluir.

## 2. Track A — Experimental (cómputo)

Ruta crítica; cada paso habilita el siguiente:

1. **Optimizar el I/O en cloud** — cache MONAI (`CacheDataset`/`PersistentDataset`) + copia del
   dataset al disco local del runtime de Colab. Prerrequisito de cualquier entrenamiento serio en
   GPU (hoy el A100 está infrautilizado por lectura desde Drive; ver [vitácora 2026-06-25](../vitacora/README.md)).
2. **Swin-UNETR en L4/A100** — entrena el Transformer que da nombre al TFM. *(Pilar 2)*
3. **nnU-Net entrenado y evaluado** como baseline fuerte externo. *(Pilar 1)*
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

- Hay una **reunión con el tutor pendiente** que condiciona varias decisiones de redacción
  (reparto Metodología/Desarrollo, nivel de detalle, formato de la tabla T1, tipos de imagen).
  No conviene invertir fuerte en capítulos cuya estructura el tutor va a ajustar.
- El **arreglo de I/O** no depende del tutor y es prerrequisito de Swin + nnU-Net + finales.
- `adaptive_gating` define la narrativa (positiva vs negativa) pero no urge hasta poder hacer una
  corrida larga limpia (tras el I/O), salvo que se quiera diagnosticar ya en local.

### Orden recomendado (dos frentes en paralelo, sin trabajo desperdiciado)

**Inmediato (Track B, cero cómputo, destraba al tutor):**
- [x] Índice maestro de los 6 capítulos.
- [ ] Actualizar el README maestro.
- [ ] Inputs de la reunión: propuesta de reparto cap. 3/4, columnas de la tabla T1, reformular las
      3 preguntas de tipos de imagen.

**En cuanto se decida gastar GPU (Track A, ruta crítica):**
- [ ] Arreglo de I/O (cache MONAI + copia a runtime).
- [ ] Swin-UNETR (título) y nnU-Net (baseline fuerte).
- [ ] Resolver `adaptive_gating`.
- [ ] Corrida final multi-semilla + evaluación en test.

**Cuando haya resultados consolidados:**
- [ ] Capítulo 5 (Resultados) con la comparativa final.
- [ ] Introducción, Marco teórico/Estado del arte, Conclusiones.

## 5. Riesgos abiertos

- **Título vs. evidencia:** el título promete arquitecturas Transformer-UNet y Swin-UNETR aún no
  está entrenado. Riesgo alto hasta cerrar el pilar 2.
- **Contribución en duda:** `adaptive_gating` rinde por debajo del baseline en la corrida
  preliminar. Si se confirma, el TFM debe reescribirse como resultado negativo defendible.
- **Resultados aún preliminares:** 5000 pasos, una semilla, sin converger, evaluados en val (no
  test). No reportables como finales.
