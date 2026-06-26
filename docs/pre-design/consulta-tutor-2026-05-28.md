# Consulta al tutor del TFM

Fecha de envio: 2026-05-28
Fecha de respuesta: 2026-06-25 (parcial, bloques 1 y 2; bloque 3 pendiente y varios subpuntos diferidos a reunion)
Reunion de seguimiento: 2026-06-29 — preparacion en [`reunion-tutor-2026-06-29.md`](reunion-tutor-2026-06-29.md)

Origen: tras la revision del 2026-05-18, el tutor pidio enfasis en metodologia, tablas del repositorio y tipos de imagen. Este documento recoge las preguntas enviadas y dejara registradas las respuestas para trazabilidad.

Documentos relacionados:

- `docs/pre-design/decisiones-iniciales.md`
- `docs/pre-design/temas-a-revisar-con-tutor.md`
- `docs/pre-design/respuestas-tutor-2026-05-18.md`

## Estado de partida

- Decisiones de alto nivel cerradas: BraTS-GLI 2024 como nucleo, 5 modelos por fases, fusion adaptativa como contribucion principal, Dice y HD95 sobre ET/TC/WT, splits versionados con hold-out, MONAI/PyTorch + nnU-Net como baseline fuerte.
- Avances tecnicos: pipeline MONAI documentada (`docs/monai-pipeline-y-comparativa-modelos.md`), baseline residual 3D verificado en Colab y en Mac M4 Pro (`docs/colab-pro-baseline-residual-unet.md`, `docs/vitacora`), catalogo de modelos extendido con Swin-UNETR y Attention U-Net.
- Inventario disponible: `data/brats_2024_file_inventory.csv`, `data/brats_2024_local_dataset_match.csv`, `data/brats_2024_dataset_properties.json`, `data/brats_2024_dataset_context.md`.

## Preguntas enviadas

### Bloque 1: metodologia

| ID | Pregunta |
| --- | --- |
| CON-2026-05-28-M1 | Estructura esperada del capitulo de metodologia: un unico capitulo o division en diseno experimental + pipeline tecnica + protocolo de evaluacion. |
| CON-2026-05-28-M2 | Nivel de detalle requerido para formalizar las decisiones: justificacion clinica, justificacion tecnica, pseudocodigo, diagramas de flujo. |
| CON-2026-05-28-M3 | Referencias o TFM previos que puedan usarse como modelo de estilo y profundidad. |

### Bloque 2: tablas del repositorio

| ID | Pregunta |
| --- | --- |
| CON-2026-05-28-T1 | Tipo de tablas esperadas: inventario del dataset, experimentos (configuracion, semilla, metricas, recursos) o ambas. |
| CON-2026-05-28-T2 | Columnas minimas por tabla y formato en el repositorio (CSV versionado, tabla en memoria, ambos). |
| CON-2026-05-28-T3 | Ejemplo o referencia de como otro alumno estructuro estas tablas. |

### Bloque 3: tipos de imagen

| ID | Pregunta |
| --- | --- |
| CON-2026-05-28-I1 | Nivel de caracterizacion clinica por modalidad MRI (que tejido realza, que lesion resalta, relevancia en glioma) y su relacion con ET/TC/WT. |
| CON-2026-05-28-I2 | Inclusion de ejemplos visuales (cortes axiales por modalidad y region tumoral) en la memoria o solo en el analisis exploratorio del repositorio. |
| CON-2026-05-28-I3 | Ubicacion adecuada para justificar la exclusion de BraTS-MEN-RT: capitulo de tipos de imagen o capitulo de alcance. |

## Respuestas del tutor

Respuesta recibida el 2026-06-25. Cubre los bloques 1 y 2; el bloque 3 (tipos de imagen) no se respondio. Varios subpuntos quedaron diferidos a la reunion.

| ID | Respuesta del tutor | Decision derivada | Estado |
| --- | --- | --- | --- |
| CON-2026-05-28-M1 | El manuscrito completo debe seguir la estructura: Introduccion (background, planteamiento, objetivos, organizacion del documento), Marco teorico y estado del arte, Metodologia (capitulo propio si alcanza tres paginas o seccion del siguiente capitulo), Desarrollo, Resultados y Conclusiones. La Metodologia describe de manera general las fases seguidas (familiarizacion: revision literaria, trabajos relacionados, evaluacion de datos; diseno experimental: entrenamiento de varios modelos y evaluacion comparativa; etc.). El detalle tecnico y las decisiones van al capitulo de Desarrollo. | Adoptar el indice propuesto. La Metodologia describe fases de alto nivel sin detalle tecnico. El detalle (decisiones, justificaciones, configuraciones) se traslada al capitulo de Desarrollo. Confirmar el reparto exacto en la reunion. | Cerrado con aclaracion en reunion |
| CON-2026-05-28-M2 | Hasta el nivel que el alumno decida. Se hablara en la reunion. | Definir el nivel de detalle en la reunion. Mientras tanto, asumir como minimo: justificacion clinica y tecnica de cada decision, diagramas de flujo para la pipeline y pseudocodigo solo cuando aporte sobre la prosa. | Pendiente de reunion |
| CON-2026-05-28-M3 | No se respondio explicitamente. Se hablara en la reunion. | Solicitar referencias concretas (TFM previos, tesis o capitulos modelo) en la reunion. | Pendiente de reunion |
| CON-2026-05-28-T1 | El tutor aclaro que se referia a una tabla comparativa de repositorios: filas = repositorios evaluados, columnas = aspectos evaluados. No se referia ni al inventario del dataset ni al tracking de experimentos. | Construir una tabla comparativa de repositorios revisados (por ejemplo MONAI, nnU-Net, Swin-UNETR, TransBTS, Attention U-Net y otros consultados) frente a los aspectos evaluados (licencia, framework, modalidades soportadas, integracion con MONAI, mantenimiento, reproducibilidad, etc.). Inventario del dataset y tracking de experimentos siguen siendo utiles internamente pero no son lo que pidio. | Cerrado con reinterpretacion |
| CON-2026-05-28-T2 | Diferido a reunion: se veran ejemplos. | Llevar a la reunion una propuesta de columnas (aspectos evaluados) para validar y refinar con ejemplos. | Pendiente de reunion |
| CON-2026-05-28-T3 | Diferido a reunion: el tutor mostrara ejemplos. | Pedir ejemplos concretos en la reunion y, una vez vistos, ajustar formato y columnas. | Pendiente de reunion |
| CON-2026-05-28-I1 | Sin respuesta. | Reformular y plantear en la reunion. | Abierto |
| CON-2026-05-28-I2 | Sin respuesta. | Reformular y plantear en la reunion. | Abierto |
| CON-2026-05-28-I3 | Sin respuesta. | Reformular y plantear en la reunion. | Abierto |

## Temas a confirmar en la reunion

1. Reparto exacto entre los capitulos de Metodologia y Desarrollo (que va en cada uno y donde se ubican las decisiones cerradas en `decisiones-iniciales.md`).
2. Nivel de detalle objetivo (justificacion clinica/tecnica, pseudocodigo, diagramas de flujo) — propuesta inicial pendiente de validar.
3. Referencias o TFM modelo para estilo y profundidad.
4. Columnas (aspectos evaluados) de la tabla comparativa de repositorios y ejemplos del tutor.
5. Tres preguntas del bloque de tipos de imagen (caracterizacion clinica por modalidad, inclusion de ejemplos visuales en la memoria, ubicacion de la justificacion para excluir BraTS-MEN-RT).

## Material adjunto sugerido al tutor

Ninguno por ahora. Si pide contexto adicional, los documentos relevantes son los listados en "Estado de partida".

## Proximos pasos

1. Preparar el indice de la memoria en `docs/memoria/` siguiendo la estructura aprobada: Introduccion, Marco teorico y estado del arte, Metodologia, Desarrollo, Resultados, Conclusiones.
2. Esbozar la tabla comparativa de repositorios con una propuesta inicial de columnas (aspectos evaluados) para llevar a la reunion como punto de partida.
3. Reformular las tres preguntas del bloque de tipos de imagen y dejarlas listas para la reunion.
4. Consolidar las decisiones cerradas (M1 y T1) en `decisiones-iniciales.md` cuando se confirmen en la reunion.
