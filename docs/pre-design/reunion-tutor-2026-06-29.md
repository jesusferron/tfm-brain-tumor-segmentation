# Preparación de la reunión con el tutor — 2026-06-29

Fecha de la reunión: **2026-06-29**.
Origen: la respuesta del tutor del 2026-06-25 (consulta 2026-05-28) cerró los bloques 1 y 2 y dejó
varios subpuntos diferidos a esta reunión. Además, desde entonces hay avances experimentales que
introducen **decisiones estratégicas nuevas** que conviene consultar.

Documentos de apoyo: [`consulta-tutor-2026-05-28.md`](consulta-tutor-2026-05-28.md),
[`decisiones-iniciales.md`](decisiones-iniciales.md),
[índice de la memoria](../memoria/indice-memoria.md), [plan del TFM](../memoria/plan-tfm.md),
[vitácora](../vitacora/README.md).

## 0. Estado de partida (resumen para abrir la reunión)

Contra los criterios de éxito de `decisiones-iniciales.md §10`:

- **Nivel mínimo: alcanzado.** Pipeline reproducible (qc, splits, train, predict, evaluate),
  baseline 3D entrenado y evaluación interna sobre BraTS-GLI.
- **Nivel objetivo (defendible): 1 de 3 pilares en marcha.**
  - Ablación de fusión: resultados **preliminares** (4 modelos convolucionales, split val, 5000
    pasos, 1 semilla).
  - Transformer-UNet (Swin-UNETR): **sin entrenar** (inviable en local; requiere cloud).
  - Baseline fuerte (nnU-Net): **solo smoke test** de conversión.

Tablas de resultados preliminares (val, 243 casos) en `outputs/evaluation/comparativa_val_5k.csv`
y en la vitácora (2026-06-26).

---

## Bloque A — Decisiones estratégicas (PRIORITARIAS)

Son nuevas respecto a la consulta anterior y condicionan el resto del TFM.

### A.1. Riesgo título ↔ evidencia: Swin-UNETR sin entrenar

El título del TFM es *"…arquitecturas Transformer-UNet híbridas"* y Swin-UNETR es el modelo
Transformer que lo respalda. Hoy **no está entrenado**: en el backend MPS local cuesta ~124 s/paso
(inviable), así que requiere GPU cloud. Los únicos resultados actuales son de U-Nets
convolucionales.

- **CONFIRMADO (decisión del alumno):** Swin-UNETR y nnU-Net son **obligatorios** para este scope y
  título. No se reformula el alcance.
- **Implicación:** el track experimental en cloud (optimizar I/O → Swin-UNETR → nnU-Net) es de
  obligado cumplimiento, no opcional. Ver plan del TFM.
- **A informar en reunión:** plan y secuencia para entrenarlos (I/O fix + L4/A100).

### A.2. Resultado preliminar NEGATIVO de la contribución principal

La pregunta de investigación es si la **fusión adaptativa** mejora a la **concatenación**. En la
corrida preliminar (val, 5000 pasos, 1 semilla):

| Modelo | mean Dice | ET | TC | WT |
| :-- | :-: | :-: | :-: | :-: |
| attention_unet_3d | 0.655 | 0.452 | 0.698 | 0.814 |
| residual_unet_3d (concat, baseline) | 0.607 | 0.361 | 0.668 | 0.792 |
| residual + global_weighted | 0.606 | 0.371 | 0.657 | 0.790 |
| **residual + adaptive_gating** (contribución) | **0.588** | 0.360 | 0.631 | 0.774 |

La fusión adaptativa queda **por debajo** del baseline en todas las métricas e inestable. **No es
concluyente** (pocos pasos, una semilla, sin converger; puede ser un problema de optimización de la
compuerta, no de la estrategia).

- **CONFIRMADO (decisión del alumno):** **no se acepta un resultado negativo** hasta agotar todas
  las vías dentro del alcance (con límites razonables de tiempo y coste).
- **Estrategia derivada:** invertir en hacer funcionar la fusión adaptativa — corridas más largas
  (hasta converger) + ajuste de la compuerta (warmup, lr específico, regularización), antes de
  plantear cualquier conclusión negativa.
- **A acordar en reunión:** los **límites de tiempo y coste** que delimitan "agotar las vías"
  (cuántas corridas/GPU-horas antes de dar por cerrada la exploración).

### A.3. Evaluación final sobre test

Todas las métricas actuales son sobre **val**. La metodología fija que las cifras finales se
reporten sobre **test** (reservado). 

- **A consultar / informar:** se ejecutará la evaluación en test solo cuando la configuración de
  entrenamiento esté congelada, para no "quemar" el hold-out.

---

## Bloque B — Estructura de la memoria

### B.1. Reparto Metodología (cap. 3) ↔ Desarrollo (cap. 4) — *propuesta concreta*

El tutor indicó (M1) que **Metodología = fases de alto nivel** y **Desarrollo = detalle técnico**.
El capítulo 3 actual está demasiado técnico. Propuesta de reparto:

| Contenido | Va a | Justificación |
| :-- | :-- | :-- |
| Fases del trabajo (familiarización, diseño experimental, evaluación comparativa) | Metodología | Es exactamente lo que pidió el tutor |
| Formulación del problema y regiones ET/TC/WT (qué y por qué) | Metodología | Marco conceptual del experimento |
| Protocolo de evaluación: qué miden Dice y HD95 y por qué | Metodología | Decisión metodológica de alto nivel |
| Entornos de cómputo, AMP/MPS, transforms concretas, hiperparámetros, parámetros de la ventana deslizante, mecánica de la semilla | Desarrollo | Detalle técnico (gran parte ya está duplicada en el cap. 4) |

Nota: hoy los capítulos 3 y 4 **duplican** mucho contenido técnico (§3.4≈§4.2, §3.5≈§4.5). El
reparto consiste sobre todo en **aligerar el cap. 3**, porque el cap. 4 ya tiene el detalle.

- **A consultar:** ¿valida este reparto? ¿La formulación del problema y las definiciones de métrica
  van en Metodología o también en Desarrollo?

### B.2. Nivel de detalle

- **CONFIRMADO:** **incluir diagramas** (de flujo de la pipeline y de arquitectura de los modelos).
  Nivel mínimo: justificación clínica y técnica de cada decisión; pseudocódigo solo cuando aporte
  sobre la prosa (p. ej. los bloques de fusión).
- **A consultar (opcional):** validar que el nivel propuesto es el esperado.

### B.3. Referencias / TFM modelo

- **RESUELTO Y REVISADO:** el alumno dispone de ejemplos de TFM facilitados (carpeta de Google
  Drive: `https://drive.google.com/drive/folders/1G--fabxrsIzDv912TXgXrYm9C5fNucOM`) más el
  documento oficial "Instrucciones de memoria de TFM". Los tres ejemplos han sido analizados;
  síntesis y convenciones en [`../memoria/guia-estilo-y-estructura.md`](../memoria/guia-estilo-y-estructura.md).
- **Refuerzo para B.1:** los tres ejemplos **confirman** el reparto que pidió el tutor (Metodología
  breve y de proceso, 2-3 págs; detalle técnico en Desarrollo). La propuesta de re-nivelar el
  capítulo 3 queda así respaldada por evidencia, no solo por interpretación.

---

## Bloque C — Tabla comparativa de repositorios

El borrador está listo en [`tabla-comparativa-repositorios-borrador.md`](tabla-comparativa-repositorios-borrador.md)
(filas = repositorios evaluados: MONAI, nnU-Net, Swin-UNETR, TransBTS, Attention U-Net, U-Net
residual; columnas = identidad, técnica, encaje BraTS/MONAI, madurez, decisión).

- **A consultar:**
  1. ¿Frameworks e implementaciones en una sola tabla o en dos?
  2. ¿Qué columnas son esenciales y cuáles sobran? (llevar la versión mínima viable).
  3. **Pedir al menos un ejemplo del tutor** para alinear formato y profundidad.
  4. Formato definitivo: markdown en la memoria, CSV versionado, o ambos.

---

## Bloque D — Tipos de imagen (preguntas reformuladas)

No se respondieron en la consulta escrita; reformuladas para la reunión:

- **D.1 (caracterización clínica):** ¿basta con una tabla que relacione cada modalidad (T1n, T1c,
  T2w, T2f) con el tejido/lesión que realza y su relevancia para ET/TC/WT, o espera una
  descripción radiológica más extensa con referencias clínicas?
- **D.2 (ejemplos visuales):** ¿incluimos cortes axiales por modalidad y por región tumoral en la
  memoria, o se dejan solo en el análisis exploratorio del repositorio? Si van en la memoria,
  ¿cuántos y con qué propósito (ilustrativo o analítico)?
- **D.3 (exclusión de BraTS-MEN-RT):** **CONFIRMADO** — se justifica en el capítulo de **tipos de
  imagen/dataset**.

---

## Material para enseñar en la reunión

- Índice de la memoria (6 capítulos) y plan del TFM: `docs/memoria/indice-memoria.md`, `plan-tfm.md`.
- Capítulos 3 y 4 redactados.
- Tabla preliminar de resultados (val): `outputs/evaluation/comparativa_val_5k.csv`.
- Vitácora con la trazabilidad completa de las corridas y decisiones.
- Borrador de la tabla comparativa de repositorios.

## Decisiones (estado actualizado 2026-06-26)

Ya cerradas por el alumno (se informan al tutor, no se debaten salvo objeción):

- [x] A.1 Swin-UNETR y nnU-Net **obligatorios** para el scope/título.
- [x] A.2 **No** aceptar resultado negativo hasta agotar vías dentro del alcance.
- [x] B.2 Incluir **diagramas** (flujo + arquitectura).
- [x] B.3 Ejemplos de TFM ya facilitados (Drive); pendiente revisarlos internamente.
- [x] D.3 Exclusión de BraTS-MEN-RT → capítulo de tipos de imagen/dataset.

Pendientes de cerrar EN la reunión:

- [ ] A.2-bis Acordar los **límites de tiempo/coste** para la exploración de la fusión adaptativa.
- [ ] B.1 Reparto Metodología/Desarrollo (validar la propuesta).
- [ ] C Columnas y formato de la tabla comparativa (pedir ejemplo del tutor).
- [ ] D.1 Nivel de caracterización clínica por modalidad.
- [ ] D.2 Ejemplos visuales en la memoria: ¿sí/no, cuántos, con qué propósito?
