# Bitacora metodologica del TFM

Ultima actualizacion: 2026-05-18

Este documento registra, de forma incremental, la metodologia seguida durante el TFM. Su objetivo no es duplicar la memoria final, sino conservar la trazabilidad de lo que se decide, por que se decide, como se ejecuta y que evidencia queda disponible para justificarlo despues en el documento final.

La bitacora se actualizara conforme avancen las investigaciones, implementaciones y experimentos. Cada entrada debe dejar suficiente contexto para poder reconstruir la logica metodologica sin depender de memoria informal.

## Uso de la bitacora

Cada nueva entrada debe incluir, cuando aplique:

- Fecha.
- Actividad realizada.
- Objetivo metodologico.
- Procedimiento seguido.
- Explicacion o justificacion de las decisiones tomadas.
- Evidencia generada: scripts, configuraciones, splits, tablas, metricas, logs o documentos relacionados.
- Impacto en la memoria final del TFM.
- Pendientes o riesgos abiertos.

La regla practica es que cualquier decision que afecte al alcance, dataset, preprocesamiento, entrenamiento, evaluacion, comparacion experimental, reproducibilidad o limitaciones debe quedar registrada aqui.

## Marco metodologico vigente

### Problema de investigacion

El TFM estudia la segmentacion 3D de gliomas en resonancia magnetica multimodal. La pregunta aprobada es:

> Puede una estrategia de fusion adaptativa de modalidades MRI mejorar la segmentacion 3D de gliomas en BraTS-GLI frente a una fusion por concatenacion estandar, manteniendo un coste computacional asumible y con mejoras consistentes en ET, TC y WT?

Esta pregunta condiciona la metodologia: no basta con entrenar modelos, sino que hay que comparar estrategias de fusion de modalidades bajo un protocolo reproducible y con metricas adecuadas para segmentacion medica.

### Alcance del dataset

El nucleo experimental queda limitado a BraTS-GLI 2024. Esta acotacion evita mezclar tareas clinicas distintas y mantiene la comparabilidad entre casos, modalidades y regiones tumorales.

Explicacion metodologica: BraTS-GLI contiene las cuatro modalidades relevantes (`t1n`, `t1c`, `t2w`, `t2f`) y mascaras de segmentacion para entrenamiento. Otros subconjuntos BraTS pueden aportar contexto o trabajo futuro, pero no deben mezclarse en el experimento principal porque tienen objetivos clinicos, modalidades, etiquetas o protocolos diferentes.

### Enfoque experimental

La metodologia se organiza por fases:

1. Analisis e inventario del dataset.
2. Controles de calidad y preprocesamiento minimo.
3. Generacion de splits reproducibles.
4. Smoke tests de carga, transforms, forward/backward y metricas.
5. Entrenamiento de baseline sencillo.
6. Entrenamiento de baseline fuerte y modelo Transformer-UNet.
7. Ablacion de estrategias de fusion: concatenacion estandar, fusion ponderada y fusion adaptativa.
8. Analisis comparativo final y redaccion de resultados.

Explicacion metodologica: esta secuencia reduce el riesgo de entrenar modelos costosos sobre datos mal validados. Primero se asegura la integridad del dataset y la reproducibilidad del protocolo; despues se escala desde pruebas pequenas hasta experimentos completos.

### Modelos previstos y funcion metodologica

- 3D U-Net residual: baseline convolucional controlado.
- Attention U-Net: variante intermedia para estudiar el efecto de atencion espacial.
- nnU-Net: baseline fuerte de referencia en segmentacion medica.
- Swin-UNETR: arquitectura Transformer-UNet alineada con el titulo del TFM.
- TransBTS: arquitectura hibrida especifica para segmentacion de tumores cerebrales.

Explicacion metodologica: los modelos no se incorporan solo por cantidad, sino para cubrir una progresion experimental: baseline propio, baseline fuerte, modelo Transformer-UNet y variante hibrida especializada. Si el coste computacional obliga a priorizar, el objetivo defendible sera baseline fuerte + Transformer-UNet + ablacion de fusion de modalidades.

### Evaluacion

La evaluacion debe definirse antes de entrenar. El protocolo minimo incluye:

- Split interno estratificado y reproducible sobre los casos con mascara.
- Hold-out final no tocado hasta la evaluacion final.
- Versionado de IDs de train, validation y test.
- Registro de semilla y configuracion.
- Reporte minimo de Dice y HD95 para ET, TC y WT.

Explicacion metodologica: Dice mide solapamiento volumetrico y HD95 mide error de frontera reduciendo el peso de outliers extremos. Reportar ET, TC y WT permite analizar si la mejora afecta de forma consistente a las regiones BraTS relevantes, no solo al promedio global.

### Reproducibilidad

El objetivo es reproducibilidad practica auditada, no reproducibilidad bit-a-bit. Cada experimento debe registrar:

- Codigo y configuracion usados.
- Versiones de librerias relevantes.
- Entorno de ejecucion.
- Semillas.
- Split utilizado.
- Logs y metricas agregadas.
- Checkpoints o artefactos necesarios para interpretar resultados.

Explicacion metodologica: Colab Pro puede asignar GPUs distintas y los backends CUDA/MPS/CPU pueden introducir diferencias numericas. Por eso se busca que otra persona pueda repetir el protocolo y obtener resultados comparables, aunque no identicos bit a bit.

### Restricciones legales y de publicacion

El repositorio no debe redistribuir los datos NIfTI originales. La memoria debe citar la fuente de BraTS, respetar las condiciones de acceso y documentar la licencia correspondiente.

Explicacion metodologica: las restricciones de datos afectan a la reproducibilidad publica. Se pueden publicar codigo, configuraciones, scripts, splits permitidos y resultados agregados, pero no los datos originales si la licencia o el proceso de acceso no lo permite.

## Entradas

### 2026-05-18 - Apertura de la bitacora metodologica

Actividad realizada: se crea la estructura inicial de la bitacora en `docs/vitacora` y se consolida el marco metodologico vigente a partir de las decisiones iniciales y de la revision con el tutor.

Objetivo metodologico: disponer de un registro vivo que conecte las decisiones tecnicas del repositorio con la futura redaccion de la memoria del TFM.

Procedimiento seguido:

- Revision de la propuesta del TFM.
- Revision de las decisiones iniciales consolidadas.
- Revision de las respuestas del tutor del 2026-05-18.
- Extraccion de los elementos metodologicos que condicionan el resto del trabajo.

Decisiones registradas:

- BraTS-GLI 2024 queda como dataset nuclear.
- La contribucion principal sera fusion adaptativa de modalidades MRI.
- La comparacion minima incluira concatenacion estandar y fusion ponderada.
- El aprendizaje contrastivo inter-modal queda fuera del nucleo experimental.
- MONAI/PyTorch sera la base tecnica principal.
- nnU-Net se mantiene como baseline fuerte, integrado si es viable o documentado como herramienta externa.
- La evaluacion se basara como minimo en Dice y HD95 para ET, TC y WT.
- Se requiere split interno reproducible con hold-out final.

Explicacion para la memoria final: esta fase corresponde al cierre del diseno metodologico previo a la implementacion. Su valor es justificar que el TFM no parte de una exploracion abierta sin control, sino de una pregunta de investigacion acotada, un dataset principal, comparadores definidos y criterios de evaluacion establecidos antes de entrenar.

Evidencia relacionada:

- `docs/specs/propuesta-2-segmentacion-tumores-cerebrales.md`
- `docs/pre-design/decisiones-iniciales.md`
- `docs/pre-design/temas-a-revisar-con-tutor.md`
- `docs/pre-design/respuestas-tutor-2026-05-18.md`

Pendientes:

- Definir porcentajes exactos de train, validation y test.
- Definir variables de estratificacion para los splits.
- Implementar inventario automatico y controles de calidad del dataset.
- Validar con un smoke test la ejecucion reproducible de nnU-Net como baseline externo, preferiblemente orquestado mediante la interfaz `monai.apps.nnunet` si no introduce friccion tecnica.
- Concretar la formulacion tecnica de la fusion ponderada y la fusion adaptativa.

### 2026-05-18 - Decision sobre integracion de nnU-Net y MONAI

Actividad realizada: se revisa si nnU-Net puede ejecutarse integrado dentro del flujo MONAI o si conviene tratarlo como baseline externo reproducible.

Fuentes revisadas:

- MONAI en PyPI: https://pypi.org/project/monai/
- Documentacion de `monai.apps.nnunet`: https://monai.readthedocs.io/en/stable/apps.html
- Tutorial oficial de MONAI para nnU-Net: https://github.com/Project-MONAI/tutorials/blob/main/nnunet/README.md
- Documentacion oficial de nnU-Net v2: https://github.com/MIC-DKFZ/nnUNet/blob/master/documentation/getting-started/installation-and-setup.md

Conclusion tecnica: si, es posible ejecutar nnU-Net desde MONAI. MONAI incluye `monai.apps.nnunet.nnUNetV2Runner`, una interfaz para usar nnU-Net v2 desde comandos/Python de MONAI. Esta interfaz permite convertir el dataset al formato esperado por nnU-Net, ejecutar planificacion y preprocesamiento, entrenar, validar, buscar configuraciones, hacer prediccion y gestionar resultados. Tambien existen utilidades para empaquetar modelos nnU-Net como MONAI Bundle y usar wrappers de inferencia.

Matiz metodologico: esta integracion no convierte nnU-Net en un modelo propio entrenado con la misma pipeline MONAI que el resto de arquitecturas. En la practica, MONAI actua como capa de orquestacion sobre `nnunetv2`, que conserva su propio formato de datos, planificacion automatica, preprocesamiento, estructura de carpetas, folds, checkpoints y comandos.

Decision: nnU-Net se tratara como baseline externo reproducible. Si el smoke test lo permite, se usara la interfaz `monai.apps.nnunet` como forma preferente de orquestarlo desde el repositorio, pero la metodologia lo describira como baseline nnU-Net externo, no como una arquitectura implementada dentro de la pipeline MONAI propia.

Justificacion:

- Mantiene el valor metodologico de nnU-Net como baseline fuerte auto-configurable.
- Evita forzar sus decisiones internas de preprocesamiento y planificacion dentro de la pipeline propia, lo que podria alterar la comparabilidad con la referencia nnU-Net.
- Reduce riesgo tecnico y coste de implementacion.
- Permite documentar versiones, comandos, carpetas, folds, configuraciones y resultados de forma reproducible.
- Deja la pipeline MONAI/PyTorch propia para los modelos y ablaciones de fusion de modalidades, que son el nucleo experimental del TFM.

Implicacion practica:

- Se instalara PyTorch segun el hardware antes de instalar `monai` y `nnunetv2`.
- Se preparara una configuracion versionada para `nnUNetV2Runner` o, si falla, scripts equivalentes con comandos oficiales `nnUNetv2_*`.
- Se registraran `nnUNet_raw`, `nnUNet_preprocessed`, `nnUNet_results`, version de MONAI, version de nnU-Net, configuracion entrenada, fold(s), semilla cuando aplique, logs y metricas.
- La primera prueba sera un smoke test corto, por ejemplo con una configuracion de pocas epocas o un subconjunto, antes de ejecutar entrenamiento completo.

Impacto en la memoria final: nnU-Net se presentara como baseline fuerte externo y reproducible. MONAI se describira como framework principal para la pipeline propia y, si se usa `nnUNetV2Runner`, como mecanismo tecnico de orquestacion para facilitar reproducibilidad sin modificar la naturaleza de nnU-Net.

Pendientes:

- Crear un `input.yaml` minimo para BraTS-GLI compatible con `nnUNetV2Runner`.
- Probar conversion del dataset y verificacion de integridad.
- Decidir si el baseline nnU-Net usara `3d_fullres` con un fold concreto, los 5 folds o la configuracion recomendada por nnU-Net segun presupuesto computacional.
