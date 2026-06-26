# Guía de estilo y estructura de la memoria (derivada de TFM de referencia)

> Síntesis de tres TFM de ejemplo del mismo máster (programa 14MBID / VIU; tutora Yudith
> Cardinale en dos de ellos) y del documento oficial "Instrucciones de memoria de TFM".
> Sirve para calibrar estructura, profundidad y estilo de esta memoria. Resuelve la pregunta
> B.3 de la [consulta al tutor](../pre-design/consulta-tutor-2026-05-28.md).
> Ejemplos: detección de caídas con wearables (Aguinaga), ciencia de datos para gestión ágil
> (Pan Gómez), IoT/ML para cultivos (Moratalla).

## Estructura de capítulos (convergente en los 3 ejemplos)

Resumen + Abstract (con palabras clave) → **1. Introducción** (background, planteamiento,
objetivos general/específicos, organización del documento) → **2. Marco teórico y estado del
arte** → **3. Metodología** → **4. Desarrollo** → **5. Resultados/Evaluación** → **6. Conclusiones
y trabajos futuros** → **Referencias** → **Apéndice** (enlace al repositorio).

Páginas preliminares con **Índice general, Índice de figuras, Índice de tablas** (y Lista de
pseudocódigos si se usa).

**Extensión orientativa:** 60-73 páginas. Reparto típico observado: teoría ~14-27 %, metodología
~3 %, desarrollo ~44 %, resultados ~11 %, conclusiones ~4 %.

## El reparto Metodología ↔ Desarrollo (lo que confirman los ejemplos)

Los tres ejemplos y las instrucciones oficiales coinciden, y **validan la guía del tutor (B.1)**:

- **Metodología = breve (2-3 páginas) y NO técnica.** Describe el **proceso de trabajo y las
  fases** (familiarización → diseño experimental → evaluación comparativa), no las técnicas. Los
  ejemplos la apoyan en una metodología ágil (Scrum/iteraciones) + un **cronograma/Gantt con
  tareas y dependencias**. "Metodología = cómo organicé el trabajo", no "qué algoritmos usé".
- **Desarrollo = el núcleo técnico extenso.** Todo el detalle de implementación, decisiones y
  configuraciones. Se organiza **espejando las fases de la metodología**.
- **Marco teórico = el *qué es* de cada técnica** (con fórmulas y figuras citadas). El detalle
  conceptual va aquí, NO en Desarrollo; el Desarrollo solo aplica y referencia.
- **Resultados:** dos ejemplos lo fusionan con Desarrollo; el más experimental (IoT) lo **separa**
  en capítulo propio. **Para esta memoria (experimental) conviene capítulo de Resultados separado**,
  por las tablas de métricas, comparativas de modelos y validación.

## Patrones de escritura a replicar

- **Requisitos numerados (REQ1, REQ2…)** definidos al inicio y **cerrados uno a uno en
  Resultados** ("REQ1 cumplido…"). Da una narrativa muy defendible.
- **Patrón "alternativas → tabla comparativa → decisión justificada"** para cada elección técnica
  (framework, arquitecturas, función de pérdida, optimizador). → encaja directamente con la
  [tabla comparativa de repositorios](../pre-design/tabla-comparativa-repositorios-borrador.md).
- **Tablas de hiperparámetros** con columnas "espacio de búsqueda → mejor → valor final" y
  **tablas de arquitectura capa por capa**.
- **Trazabilidad figura-texto:** toda figura/tabla se anuncia y se interpreta en el texto.
- Documentar las **dificultades reales** (p. ej. memoria/VRAM, cuello de I/O) como parte del relato.
- **Pseudocódigo solo cuando aporta** (p. ej. el bucle de entrenamiento o los bloques de fusión);
  el código completo se enlaza en un apéndice (repo), no se vuelca en la memoria.
- **Cierre con limitaciones + comparación con el estado del arte + trabajos futuros**, enlazando
  resultados ↔ objetivos.

## Citación

- **APA (autor-año) o IEEE numérico [n]**, consistente en todo el documento. ~27-50 referencias.
- Separar **fuentes académicas** (bibliografía: papers peer-reviewed, libros) de **documentación
  técnica/web** (notas a pie con URLs).

## Dónde estos ejemplos se quedan cortos = nuestra oportunidad de diferenciarnos

Los tres ejemplos son flojos en **rigor cuantitativo y bibliografía peer-reviewed** (sobre todo los
dos de desarrollo de software). En una memoria médica experimental debemos superar ese listón:

1. **Métricas cuantitativas serias:** Dice y HD95 por región (ET/TC/WT), no una sola métrica;
   con sus fórmulas en el Marco teórico.
2. **Figuras cualitativas de segmentación** (predicción vs. ground truth superpuestas) — el
   equivalente médico a sus "predicciones de muestra".
3. **Curvas de entrenamiento** (loss / Dice por época / paso).
4. **Comparación numérica explícita con el estado del arte** (leaderboard BraTS, nnU-Net,
   Swin-UNETR), como Aguinaga compara contra el paper de referencia.
5. **Bibliografía con peso de papers** (U-Net, nnU-Net, Swin-UNETR, BraTS, fusión multimodal);
   apuntar por encima de 40 referencias.
6. **Justificar el split por paciente** (no por corte/slice) para evitar fuga de datos — un
   revisor de imagen médica lo va a buscar. Ya se hace (splits estratificados por caso); hay que
   explicitarlo.
7. **Sección de implicación clínica** (qué error es más grave, viabilidad, generalización).
