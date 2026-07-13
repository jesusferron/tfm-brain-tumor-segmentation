# Bitacora metodologica del TFM

Ultima actualizacion: 2026-07-13 (reunion con el tutor: decisiones cerradas sobre limites de la fusion adaptativa, secuencia experimental, reparto Metodologia/Desarrollo y estructura de la memoria)

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

- Decidir si el baseline nnU-Net final usara los datos en formato NIfTI 4D intermedio o una conversion directa propia al formato nnU-Net.
- Decidir si el baseline nnU-Net usara `3d_fullres` con un fold concreto, los 5 folds o la configuracion recomendada por nnU-Net segun presupuesto computacional.

### 2026-05-18 - Smoke test minimo para preparar nnU-Net

Actividad realizada: se prepara y ejecuta un smoke test local minimo para comprobar si el dataset BraTS-GLI puede alimentar una configuracion inicial de `nnUNetV2Runner` sin lanzar conversion, preprocesamiento ni entrenamiento.

Objetivo metodologico: transformar la decision teorica sobre nnU-Net en un artefacto reproducible del repositorio. La prueba no busca medir rendimiento, sino confirmar que la estructura local de datos permite generar una entrada pequena y trazable para el siguiente paso de conversion.

Procedimiento seguido:

- Se comprueba que no queda activo ningun proceso largo relacionado con `find`, MONAI, nnU-Net o BraTS generado por el intento anterior.
- Se confirma que el comando disponible en local es `python3`, no `python`.
- Se crea una plantilla minima de entrada MONAI para nnU-Net.
- Se crea una configuracion de smoke test limitada a 3 casos.
- Se crea un script de validacion que inspecciona solo los primeros casos necesarios y verifica presencia de `t1n`, `t1c`, `t2w`, `t2f` y `seg`.
- Se genera un datalist pequeno con 3 casos de entrenamiento y 1 caso de test sin etiqueta, porque nnU-Net gestiona validacion mediante folds internos y la interfaz de conversion de MONAI espera un elemento en `test` para completar la conversion.

Artefactos generados:

- `configs/nnunet/brats_gli_2024_monai_input.yaml`
- `configs/nnunet/brats_gli_2024_smoke.yaml`
- `scripts/nnunet/check_brats_gli_nnunet_smoke.py`
- `outputs/nnunet_smoke/brats_gli_2024_smoke_datalist.json`
- `outputs/nnunet_smoke/input.yaml`

Resultado de ejecucion:

- Python local: `3.13.2`.
- MONAI instalado: no.
- nnU-Net v2 instalado: no.
- Raiz del dataset encontrada: `/Volumes/External M2/Datos/TFM-datasets`.
- Carpetas de entrenamiento encontradas: `training_data1_v2` y `training_data_additional`.
- Casos validos comprobados: 3.
- Items de entrenamiento generados: 3.
- Items de test generados: 1, sin etiqueta y solo para satisfacer el contrato de conversion de MONAI.
- No se ejecuto conversion, preprocesamiento ni entrenamiento.

Comando ejecutado:

```bash
python3 scripts/nnunet/check_brats_gli_nnunet_smoke.py
```

Comando preparado para el siguiente paso, cuando el entorno este listo:

```bash
.venv/bin/python -m monai.apps.nnunet nnUNetV2Runner convert_dataset --input_config outputs/nnunet_smoke/input.yaml
```

Explicacion para la memoria final: este paso documenta una verificacion preliminar de viabilidad tecnica. Antes de usar nnU-Net como baseline fuerte, se comprueba que las modalidades y mascaras de BraTS-GLI pueden representarse en un datalist compatible con el flujo MONAI/nnU-Net. Esta prueba reduce el riesgo de descubrir problemas de estructura de datos durante una conversion completa o durante entrenamiento.

Pendientes:

- Si la conversion funciona, ampliar el generador al split completo definido para el TFM.

### 2026-05-18 - Conversion smoke test con nnUNetV2Runner

Actividad realizada: se crea un entorno Python local aislado, se instalan las dependencias necesarias y se ejecuta la conversion minima de MONAI `nnUNetV2Runner convert_dataset` sobre 3 casos BraTS-GLI.

Objetivo metodologico: verificar que nnU-Net puede ser orquestado desde MONAI con datos BraTS-GLI preparados desde el repositorio, antes de invertir tiempo en planificacion, preprocesamiento completo o entrenamiento.

Entorno utilizado:

- Python: `3.13.2`.
- PyTorch: `2.12.0`.
- MONAI: `1.5.2`.
- nnU-Net v2: `2.7.0`.
- `fire`: `0.7.1`, necesario para usar la CLI de `monai.apps.nnunet`.
- Backend MPS disponible en el Mac: si.

Artefactos anadidos:

- `.venv/`, entorno local ignorado por Git.
- `requirements/nnunet-smoke.txt`, dependencias minimas versionadas para repetir el smoke test.
- `.gitignore`, reglas para evitar versionar NIfTI, preprocesados, checkpoints y `.venv`.

Hallazgo tecnico: `nnUNetV2Runner` no acepta una lista de cuatro rutas NIfTI en el campo `image` del datalist. La version instalada espera que `image` sea un unico NIfTI. Por eso el script de smoke test apila las cuatro modalidades (`t1n`, `t1c`, `t2w`, `t2f`) en un NIfTI 4D temporal y despues MONAI lo separa en canales nnU-Net durante la conversion.

Segundo ajuste tecnico: la ruta de conversion de MONAI espera un conjunto `test` no vacio para completar su flujo sin error. Para el smoke test se genera 1 caso de test sin etiqueta reutilizando una imagen ya apilada. Esto no representa evaluacion experimental; solo satisface el contrato tecnico de conversion.

Comandos ejecutados:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip setuptools wheel
.venv/bin/python -m pip install -r requirements/nnunet-smoke.txt
.venv/bin/python scripts/nnunet/check_brats_gli_nnunet_smoke.py
.venv/bin/python -m monai.apps.nnunet nnUNetV2Runner convert_dataset --input_config outputs/nnunet_smoke/input.yaml
```

Resultado de conversion:

- Dataset nnU-Net generado: `outputs/nnunet_smoke/nnUNet_raw/Dataset724_tfm-brain-tumor-segmentation`.
- `num_input_channels`: 4.
- `num_foreground_classes`: 4.
- `imagesTr`: 12 ficheros, correspondientes a 3 casos x 4 modalidades.
- `labelsTr`: 3 ficheros.
- `imagesTs`: 4 ficheros, correspondientes a 1 caso de test x 4 modalidades.
- `dataset.json` generado con canales `t1n`, `t1c`, `t2w`, `t2f`.
- `pip check`: sin dependencias rotas.
- No se ejecuto `plan_and_process`, preprocesamiento ni entrenamiento.

Explicacion para la memoria final: este resultado valida la viabilidad tecnica de usar nnU-Net como baseline externo reproducible y, si interesa, orquestarlo desde MONAI. Tambien deja claro que la integracion requiere una preparacion especifica de datos multicanal, por lo que debe documentarse como parte del protocolo de reproducibilidad.

Pendientes:

- Decidir si el baseline nnU-Net final usara los datos en formato NIfTI 4D intermedio o una conversion directa propia al formato nnU-Net.
- Definir split definitivo del TFM antes de generar la conversion completa.

### 2026-05-18 - Verificacion de integridad nnU-Net en smoke test

Actividad realizada: se ejecuta la verificacion de integridad y extraccion de fingerprint de nnU-Net sobre el dataset smoke test convertido.

Objetivo metodologico: confirmar que el dataset generado por la ruta MONAI/nnU-Net no solo existe en disco, sino que cumple las expectativas internas de nnU-Net antes de escalar a mas casos.

Procedimiento seguido:

- Se intento inicialmente ejecutar `extract_fingerprints` desde un heredoc de Python.
- El intento se detuvo porque en macOS/Python el multiprocessing con `spawn` no puede reabrir un proceso cuyo script principal es `<stdin>`.
- Se creo un script fisico versionable para ejecutar la misma operacion de forma compatible con multiprocessing.
- Se ejecuto la verificacion con `npfp=1` para mantener el consumo acotado.

Artefacto anadido:

- `scripts/nnunet/verify_brats_gli_nnunet_smoke.py`

Comando ejecutado:

```bash
.venv/bin/python scripts/nnunet/verify_brats_gli_nnunet_smoke.py --clean --npfp 1
```

Resultado:

- `verify_dataset_integrity Done`.
- nnU-Net indica que, si no aparecen errores, el dataset es probablemente correcto.
- Se extrajo el fingerprint de 3 casos.
- Reader/writer usado por nnU-Net: `SimpleITKIO`.
- Artefacto generado: `outputs/nnunet_smoke/nnUNet_preprocessed/Dataset724_tfm-brain-tumor-segmentation/dataset_fingerprint.json`.
- No se ejecuto planificacion de experimentos, preprocesamiento completo ni entrenamiento.

Resumen del fingerprint:

- Espaciado detectado en los 3 casos: `1.0 x 1.0 x 1.0`.
- Canales analizados: 4.
- Shapes tras crop:
  - `[142, 161, 128]`
  - `[146, 184, 139]`
  - `[143, 183, 147]`
- `median_relative_size_after_cropping`: `0.5171138972933509`.

Explicacion para la memoria final: esta prueba cierra la viabilidad tecnica minima de nnU-Net como baseline externo reproducible. La conversion MONAI produce una estructura aceptada por nnU-Net y la verificacion interna no detecta errores en el subconjunto de prueba. El resultado no valida rendimiento ni protocolo experimental final, pero reduce el riesgo tecnico antes de generar splits y conversiones completas.

Pendientes:

- Definir el split definitivo del TFM antes de generar el dataset nnU-Net completo.
- Decidir estrategia final de conversion: NIfTI 4D intermedio via MONAI o conversion directa propia al formato nnU-Net.
- Definir si nnU-Net final usara `3d_fullres` en un fold, 5 folds o configuracion recomendada segun presupuesto computacional.

### 2026-05-26 - Preparacion y depuracion del baseline MONAI en Colab Pro

Actividad realizada: se consolida la pipeline propia MONAI/PyTorch para ejecutar el primer baseline `residual_unet_3d` en Colab Pro con GPU A100, y se depuran los problemas encontrados durante la ejecucion remota.

Objetivo metodologico: pasar de pruebas locales y smoke tests a un protocolo ejecutable en un entorno GPU externo, manteniendo trazabilidad de codigo, configuraciones, splits, dependencias y artefactos minimos. Esta fase no busca todavia obtener el resultado experimental final, sino estabilizar el procedimiento que permitira entrenar el baseline y despues compararlo con las variantes de fusion.

Problemas encontrados en Colab:

- `pip install -r requirements/protocol.txt` fallaba porque el archivo existia localmente pero no estaba versionado en GitHub.
- El clon de Colab tampoco incluia aun componentes necesarios del protocolo, como `tfm_brats`, `configs`, `requirements/protocol.txt` y los splits versionados.
- El QC fallaba porque `configs/dataset/brats_gli_2024.yaml` apuntaba a la ruta local del Mac: `/Volumes/External M2/Datos/TFM-datasets`.
- En Colab el `dataset_root` debe apuntar a la carpeta padre de Drive que contiene `training_data1_v2` y `training_data_additional`, por ejemplo `/content/drive/MyDrive/TFM-datasets`.
- Una ejecucion de entrenamiento larga mostro infrautilizacion: tras unas 7 horas la GPU A100 no superaba aproximadamente 2 GB de memoria y la RAM del sistema rondaba 6.3 GB. Esto sugiere un cuello de botella de entrada/salida o una configuracion de entrenamiento demasiado conservadora, no falta de capacidad de la GPU.

Procedimiento seguido:

- Se versionaron los archivos necesarios para que un clon limpio de GitHub en Colab pueda instalar dependencias y ejecutar la pipeline.
- Se actualizo la guia `docs/colab-pro-baseline-residual-unet.md` con comprobaciones explicitas de raiz del repositorio, presencia de `requirements/protocol.txt`, montaje de Drive y correccion de `dataset_root`.
- Se anadio una celda reproducible para reescribir `dataset_root` dentro del YAML desde Colab usando `PyYAML`.
- Se anadio una comprobacion previa para verificar que Colab ve `training_data1_v2` y `training_data_additional`.
- Se acoto el entrenamiento real con `--max-steps 3000` para evitar lanzamientos abiertos sin control temporal.
- Se optimizo la configuracion `configs/training/colab_pro.yaml` para aprovechar mejor A100: `batch_size: 2`, `amp: true`, `pin_memory: true`, `persistent_workers: true`, `prefetch_factor: 2`, `cudnn_benchmark: true`, menos epocas, validacion menos frecuente y menos batches de validacion.
- Se modifico `tfm_brats/monai_pipeline.py` para registrar progreso en consola y CSV: velocidad, memoria GPU, batch actual, batches totales, pasos restantes y `case_id`.
- Se dejo documentada la alternativa de copiar el dataset desde Google Drive al disco local del runtime (`/content/TFM-datasets`) si la lectura desde Drive limita el entrenamiento.

Decisiones tecnicas:

- Mantener Colab Pro como entorno de entrenamiento inicial para el baseline real.
- No depender de ediciones manuales invisibles en Colab: las rutas y comprobaciones quedan documentadas con comandos copiables.
- Usar entrenamiento acotado por pasos para la primera ejecucion real, antes de lanzar entrenamientos completos.
- Registrar progreso de entrenamiento en `train_log.csv` y no solo en stdout, para poder diagnosticar cuellos de botella si la celda se interrumpe o si se revisa a posteriori.
- Tratar la baja utilizacion de GPU como evidencia para priorizar optimizacion del pipeline de datos y logging antes de aumentar complejidad del modelo.

Commits relacionados:

- `442a55d Add BraTS baseline protocol files`: versiona pipeline, configuraciones, requirements, splits y artefactos pequenos necesarios para Colab.
- `9792c07 Document Colab dataset root update`: documenta la correccion de `dataset_root` en Colab.
- `bde0745 Optimize Colab training loop`: activa AMP, mejoras de `DataLoader`, logging de velocidad/memoria y una configuracion Colab mas acotada.
- `3276a52 Log training case progress`: anade `batch_total`, `remaining_steps` y `case_ids` al log de entrenamiento.

Artefactos relacionados:

- `requirements/protocol.txt`
- `configs/dataset/brats_gli_2024.yaml`
- `configs/training/colab_pro.yaml`
- `configs/training/local_smoke.yaml`
- `configs/model/residual_unet_3d.yaml`
- `outputs/splits/brats_gli_2024_seed20260526/`
- `tfm_brats/cli.py`
- `tfm_brats/monai_pipeline.py`
- `docs/colab-pro-baseline-residual-unet.md`

Comando actual recomendado para Colab:

```bash
%cd /content/tfm-brain-tumor-segmentation
!git pull origin main
!python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/residual_unet_3d.yaml \
  --training-config configs/training/colab_pro.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/residual_unet_3d \
  --max-steps 3000 \
  --device cuda
```

Salida esperada de progreso:

```text
train_step epoch=1 batch=3/568 step=10 remaining=2990 case_ids=BraTS-GLI-... loss=... speed=... step/s, gpu_mem=...GB
```

Validaciones realizadas en local:

- `python3 -m compileall -q tfm_brats scripts/brats_cli.py tests`: correcto.
- `.venv/bin/python -m unittest discover -s tests`: 6 tests correctos.
- Smoke train de 1 paso en CPU con `local_smoke.yaml`: correcto; genera `train_summary.json`, `train_log.csv`, `last.pt` y `best.pt`.

Evidencia metodologica generada:

- La pipeline ya se puede clonar desde GitHub en Colab con los archivos necesarios.
- El entrenamiento registra trazabilidad suficiente para diagnosticar si el cuello de botella esta en carga de datos, CPU, validacion o GPU.
- La primera ejecucion real queda limitada por pasos, lo que facilita comparar tiempos entre variantes de configuracion sin gastar sesiones largas de Colab.

Impacto en la memoria final:

Esta entrada servira para justificar la estrategia de reproducibilidad practica en entorno Colab Pro: control de versiones, configuraciones YAML, splits versionados, comandos documentados, registro de logs y adaptacion del entrenamiento al hardware disponible. Tambien documenta una limitacion real del entorno: Google Drive puede introducir cuellos de botella de lectura, por lo que mover datos al disco local del runtime puede formar parte del protocolo operativo aunque no cambie el dataset experimental.

Pendientes:

- Relanzar el entrenamiento en Colab con el commit `3276a52` o posterior.
- Registrar GPU exacta de `nvidia-smi`, velocidad `step/s`, memoria GPU maxima y tiempo hasta el primer `train_step`.
- Si la velocidad sigue baja, copiar `training_data1_v2` y `training_data_additional` a `/content/TFM-datasets` y repetir con el mismo comando.
- Conservar `train_log.csv`, `train_summary.json` y el resumen de validacion para decidir si el baseline es suficiente o si hay que ajustar `patch_size`, `batch_size`, `samples_per_case` o frecuencia de validacion.

Actualizacion posterior del mismo dia:

- La ejecucion en A100 mostro progreso real en GPU: `gpu_mem=5.43GB`, `batch_size=2`, `samples_per_case=2`, `train_cases=1135`, `val_cases=243`.
- La velocidad observada tras 20 pasos fue aproximadamente `0.209 step/s`, es decir, unos 5 segundos por paso.
- Se concluye que la memoria GPU baja no implica por si sola un error; el indicador relevante pasa a ser el reparto entre espera de datos y computo.
- Se aumenta `samples_per_case` de 2 a 4 en `configs/training/colab_pro.yaml` para procesar mas patches por cada caso leido y amortizar mejor el I/O.
- Se amplia el log de entrenamiento con `patches`, `data_wait_seconds`, `compute_seconds`, `step_seconds` y `patches_per_second`.
- La siguiente decision dependera de esos tiempos: si domina `data_wait`, copiar dataset a `/content/TFM-datasets`; si domina `compute`, ajustar batch efectivo, `patch_size` o numero total de pasos.

### 2026-05-26 - Ampliacion del catalogo de modelos: Swin-UNETR y Attention U-Net

Actividad realizada: se identifica que la corrida actual en Colab Pro (`configs/model/residual_unet_3d.yaml`) solo entrena la primera fase del plan experimental (baseline `residual_unet_3d` con fusion `concat`), de las seis declaradas en `experiment_priority`. Para que la pipeline propia pueda cubrir tambien el modelo Transformer-UNet y la variante intermedia de atencion espacial, se generaliza el factory de modelos y se anaden las configuraciones de Swin-UNETR y Attention U-Net 3D.

Objetivo metodologico: cerrar la brecha entre el plan experimental documentado y lo que el repositorio puede realmente entrenar, sin tocar la pipeline de datos, transforms, optimizador, perdida ni logging. La meta es que un mismo comando `python -m tfm_brats.cli train --model-config <ruta>` baste para entrenar cualquiera de las arquitecturas previstas, manteniendo splits, semilla, hold-out, AMP y registro de progreso identicos entre experimentos.

Procedimiento seguido:

- Se reviso el factory existente `tfm_brats.monai_pipeline.build_model`. Hasta ahora siempre instanciaba `monai.networks.nets.UNet` envuelto en `FusionUNet`, ignorando el campo `model.implementation` declarado en YAML. Por eso un `model-config` con otra arquitectura igualmente terminaba entrenando un U-Net residual.
- Se introdujo un campo nuevo `model.architecture` y se refactorizo `build_model` como dispatcher explicito. Valores soportados: `residual_unet_3d` (alias `fusion_unet`, conserva la logica anterior y las tres fusiones `concat | global_weighted | adaptive_gating`), `swin_unetr` y `attention_unet`. Cualquier otro valor lanza `ValueError`, evitando que un YAML con un nombre inesperado entrene silenciosamente el baseline.
- Se actualizaron los tres YAML existentes (`residual_unet_3d.yaml`, `residual_unet_3d_global_weighted.yaml`, `residual_unet_3d_adaptive_gating.yaml`) para declarar `architecture: residual_unet_3d` de forma explicita. El comportamiento no cambia, pero la configuracion ya no depende de un default implicito.
- Se anadio `configs/model/swin_unetr.yaml` usando `monai.networks.nets.SwinUNETR` con `feature_size=48`, `depths=[2,2,2,2]`, `num_heads=[3,6,12,24]` y sin `use_checkpoint` (se puede activar despues si la memoria de la A100 lo exige).
- Se anadio `configs/model/attention_unet_3d.yaml` usando `monai.networks.nets.AttentionUnet` con cinco niveles (`channels=[16,32,64,128,256]`, `strides=[2,2,2,2]`).
- Verificacion local: `python -m compileall -q tfm_brats` correcto, `unittest discover -s tests` con 6 tests OK, y un smoke de forward con tensor `(1, 4, 96, 96, 96)` para las cinco configuraciones. Todas devuelven `(1, 3, 96, 96, 96)`. Conteo de parametros: residual U-Net 1.19M, Attention U-Net 5.91M, Swin-UNETR 62.19M.

Justificacion metodologica:

- El factory anterior solo soportaba una arquitectura. Introducir un dispatcher no anade un acoplamiento nuevo: simplemente hace explicito lo que ya estaba implicito y permite que el resto de la pipeline (transforms, dataloader, perdida `DiceCELoss`, validacion sliding window, checkpoints, logs) se reuse sin cambios entre modelos.
- Mantener `residual_unet_3d` como default preserva la compatibilidad con cualquier YAML antiguo y con la entrada anterior de la bitacora.
- Anadir `architecture` como campo separado de `name` permite distinguir la familia de modelos (lo que decide el factory) del nombre del experimento (lo que se usa para artefactos y reporting).
- Las opciones de Swin-UNETR y Attention U-Net se exponen via YAML, sin valores hardcodeados, para poder ajustar `feature_size`, `depths`, `dropout`, etc., sin tocar codigo.

Implicaciones para el plan experimental:

- La fase 6 del plan (entrenamiento de baseline fuerte y modelo Transformer-UNet) ya es ejecutable desde la pipeline propia: `configs/model/swin_unetr.yaml` cubre la parte Transformer-UNet alineada con el titulo del TFM.
- La fase 5 (Attention U-Net como variante intermedia) tambien queda cubierta con `configs/model/attention_unet_3d.yaml`.
- La fase 7 (ablacion de fusiones) ya tenia configs (`residual_unet_3d_global_weighted.yaml`, `residual_unet_3d_adaptive_gating.yaml`) pero aun no se ha entrenado: queda explicitamente pendiente.
- nnU-Net y TransBTS siguen sin estar implementados en la pipeline propia y se documentan como fases posteriores.
- Una sola semilla por experimento sigue siendo el modo actual; la repeticion con semillas adicionales se decidira al consolidar resultados, no en esta entrada.

Evidencia generada:

- `tfm_brats/monai_pipeline.py` (funcion `build_model` extendida)
- `configs/model/residual_unet_3d.yaml`
- `configs/model/residual_unet_3d_global_weighted.yaml`
- `configs/model/residual_unet_3d_adaptive_gating.yaml`
- `configs/model/swin_unetr.yaml`
- `configs/model/attention_unet_3d.yaml`

Comandos previstos para Colab Pro tras esta entrada (manteniendo split, dataset y training config actuales):

```bash
python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/attention_unet_3d.yaml \
  --training-config configs/training/colab_pro.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/attention_unet_3d \
  --max-steps 3000 \
  --device cuda
```

```bash
python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/swin_unetr.yaml \
  --training-config configs/training/colab_pro.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/swin_unetr \
  --max-steps 3000 \
  --device cuda
```

```bash
python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/residual_unet_3d_global_weighted.yaml \
  --training-config configs/training/colab_pro.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/residual_unet_3d_global_weighted \
  --max-steps 3000 \
  --device cuda
```

```bash
python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/residual_unet_3d_adaptive_gating.yaml \
  --training-config configs/training/colab_pro.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/residual_unet_3d_adaptive_gating \
  --max-steps 3000 \
  --device cuda
```

Riesgos y observaciones:

- Swin-UNETR es notablemente mas pesado (62M parametros frente a 1.2M del baseline). Con `batch_size=2` y `patch_size=128` puede agotar la memoria de la A100. Si ocurre, la primera mitigacion sera activar `use_checkpoint: true` en `configs/model/swin_unetr.yaml` (gradient checkpointing del propio MONAI); la segunda, reducir `batch_size` a 1 o `patch_size` a 96 en el training config.
- Attention U-Net 3D tiene un coste intermedio (5.9M) y deberia entrar con la misma `colab_pro.yaml` actual sin ajustes.
- El comando documentado en la entrada anterior sigue siendo valido para la fase de baseline; las nuevas configuraciones no lo invalidan, solo extienden el catalogo.
- Los `--max-steps 3000` heredados del baseline son insuficientes para sacar conclusiones experimentales finales, pero son adecuados para verificar que cada arquitectura entrena de forma estable, que se generan `train_summary.json`, `train_log.csv` y checkpoints, y para comparar tiempos por paso entre arquitecturas en la misma GPU.

Impacto en la memoria final:

Esta entrada justifica que la pipeline propia ya cubre tres familias de modelos (U-Net residual con tres fusiones, Attention U-Net y Swin-UNETR Transformer) bajo un protocolo comun. nnU-Net seguira presentandose como baseline fuerte externo y TransBTS como linea hibrida especializada cuya integracion queda como trabajo futuro si el presupuesto computacional lo permite. La memoria podra apoyarse en este registro para argumentar que la eleccion del subconjunto efectivo de modelos no es arbitraria, sino el resultado de priorizar la pregunta de investigacion (fusion adaptativa) y las capacidades reales del entorno de entrenamiento.

Pendientes:

- Entrenar `residual_unet_3d_global_weighted` y `residual_unet_3d_adaptive_gating` (fase 7) con el mismo protocolo que el baseline y consolidar tabla comparativa.
- Entrenar `attention_unet_3d` (fase intermedia de atencion espacial) para evidenciar el escalon entre baseline puro y Transformer-UNet.
- Entrenar `swin_unetr` (fase 6) y registrar memoria GPU pico, `step_seconds` y necesidad o no de `use_checkpoint`.
- Confirmar si nnU-Net externo se ejecutara con `3d_fullres` y un fold, o con configuracion recomendada por nnU-Net, antes de cerrar la comparacion.
- Decidir si se incorpora TransBTS o se documenta como trabajo futuro.

### 2026-05-27 - Sanity check local del baseline en Mac M4 Pro (MPS)

Actividad realizada: se ejecuta un entrenamiento corto del baseline `residual_unet_3d` en el portatil local (MacBook Pro M4 Pro, 12 cores, 24 GB de memoria unificada) usando el backend MPS de PyTorch, para validar la pipeline end-to-end fuera de Colab y aprovechar la noche sin gastar sesion de Colab.

Objetivo metodologico: no buscar metricas reportables, sino confirmar tres cosas antes de la siguiente iteracion en Colab Pro: (1) que el refactor del factory de modelos no rompio el flujo del baseline, (2) que la pipeline (carga, transforms, forward/backward, validacion sliding window, checkpointing y logging) funciona tambien en MPS, y (3) que existe senal de aprendizaje real en regiones BraTS al cabo de unos cuantos steps. La motivacion practica fue que el cuello observado en Colab era I/O de Google Drive, no computo; el M4 Pro lee desde un M.2 externo local rapido y permite comparar comportamiento de la pipeline aislando ese factor.

Procedimiento seguido:

- Se anade `configs/training/mac_m4_pro.yaml` con un perfil conservador adaptado a MPS: `device: mps`, `amp: false` (la pipeline ya fuerza AMP a `False` fuera de CUDA), `patch_size: [96, 96, 96]`, `batch_size: 1`, `samples_per_case: 2`, `num_workers: 6`, `persistent_workers: true`, `prefetch_factor: 2`, `pin_memory: false`, `cudnn_benchmark: false`, `validation_interval: 5`, `validation_batches: 2`.
- Se reutiliza el split versionado `outputs/splits/brats_gli_2024_seed20260526` y el `model-config` ya existente, sin cambios.
- Se lanza el entrenamiento envuelto en `caffeinate -dimsu` para evitar que el sistema entre en suspension y con `tee` a `outputs/train/residual_unet_3d_m4_pro_stdout.log` para conservar stdout adicional al CSV.

Comando ejecutado:

```bash
caffeinate -dimsu .venv/bin/python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/residual_unet_3d.yaml \
  --training-config configs/training/mac_m4_pro.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/residual_unet_3d_m4_pro \
  --max-steps 1500 \
  --device mps \
  2>&1 | tee outputs/train/residual_unet_3d_m4_pro_stdout.log
```

Comportamiento observado durante el entrenamiento:

- Cold start del primer step: `data_wait=21.20s` en step 1 (carga inicial de los workers y caches frias).
- A partir del step 10 la velocidad se estabilizo en aproximadamente `0.48 step/s`, con `compute_seconds=0.50` constante y picos esporadicos de `data_wait` de 3-11 segundos cada 50-100 steps (lecturas NIfTI desde el M.2 amortizadas por el prefetch).
- La loss bajo de `1.25` (step 1) a una media de `0.89` con varianza alta por patch, comportamiento normal de `DiceCELoss` con cropping aleatorio en regiones BraTS.
- Tras 1500 steps (3000 patches, 2 epochs reales sobre 1135 casos de entrenamiento), la validacion sliding window sobre 2 batches del split val produjo:
  - `ET_dice = 0.000`
  - `TC_dice = 0.212`
  - `WT_dice = 0.287`
  - `mean_dice = 0.166`
- Validacion completa en `~30.5s` con `validation_batches=2`.
- Tiempo total del run: aproximadamente 52 minutos.

Interpretacion metodologica:

- El patron `ET < TC < WT` es el esperado en un entrenamiento corto de BraTS. WT es la region mas amplia y facil de detectar (cualquier voxel tumoral cuenta); TC anade necrosis y realce; ET aisla solo el realce, que es la region mas pequena y rara y suele necesitar muchos mas pasos antes de aparecer.
- `mean_dice=0.166` no es una metrica reportable. El estado del arte en BraTS-GLI ronda `0.85-0.90` con entrenamientos de decenas de miles de pasos, AMP, patch_size mayor y batch efectivo grande.
- Lo que si reporta el run, y que justifica su valor metodologico, es senal de aprendizaje real (WT > 0 confirma que el modelo discrimina tumor de fondo) y validacion del flujo completo en un backend distinto al de Colab.

Tambien aparecio una advertencia de PyTorch dentro de `monai.inferers.utils` por usar indexing con secuencias no-tupla (sera incompatible en PyTorch 2.9). No bloquea la ejecucion en la version actual y queda anotada como riesgo a vigilar cuando se actualice MONAI o PyTorch.

Decisiones tecnicas:

- Confirmar que el portatil local sirve como entorno de sanity check y diagnostico de pipeline, no como plataforma de entrenamiento final.
- Mantener Colab Pro como entorno principal para entrenamientos serios: AMP, A100 de 40 GB, batch y patch mayores.
- No usar el M4 Pro para `swin_unetr`: los 62M parametros sin AMP en 24 GB unificados no son una apuesta razonable. Queda explicitamente excluido.
- Para futuras iteraciones rapidas de pipeline (smoke largos, debug de transforms, comparacion relativa de velocidad) sigue siendo util el perfil `mac_m4_pro.yaml`.

Artefactos generados:

- `configs/training/mac_m4_pro.yaml`
- `outputs/train/residual_unet_3d_m4_pro/train_summary.json`
- `outputs/train/residual_unet_3d_m4_pro/train_log.csv`
- `outputs/train/residual_unet_3d_m4_pro/checkpoints/best.pt`
- `outputs/train/residual_unet_3d_m4_pro/checkpoints/last.pt`
- `outputs/train/residual_unet_3d_m4_pro_stdout.log`

Limitaciones del run:

- Solo una semilla y una corrida.
- Validacion limitada a 2 batches de los 243 casos del split val. La estimacion de Dice es ruidosa.
- Sin AMP (forzado por el codigo en backends no-CUDA) ni `cudnn_benchmark`.
- Numero de pasos muy inferior al necesario para curvas estables de Dice por region.

Impacto en la memoria final: este resultado se usara como evidencia de validacion tecnica del pipeline en un backend alternativo (MPS) y como justificacion de por que el entrenamiento experimental se reserva para A100 en Colab. Tambien refuerza la trazabilidad de decisiones reproducibles: cualquier persona con un Mac Apple Silicon puede repetir el sanity check siguiendo el mismo comando.

Pendientes:

- Tras el siguiente entrenamiento real en Colab (mas pasos, AMP), incorporar tabla comparativa Dice ET/TC/WT entre baseline y ablaciones de fusion.
- Decidir si `mac_m4_pro.yaml` se promueve a smoke largo recurrente (por ejemplo, antes de cada PR que toque el pipeline) o si se mantiene como herramienta ad-hoc.
- Vigilar la advertencia de indexing en `monai.inferers.utils` cuando se actualicen PyTorch o MONAI.

## 2026-06-25 - Diagnostico de infrautilizacion del A100 (cuello de botella I/O) y eleccion de hardware

Actividad realizada: analisis de por que la GPU A100 de Colab se infrautiliza durante el entrenamiento y decision sobre que tarjeta usar en cada fase del proyecto.

Objetivo metodologico: separar el coste real del experimento (computo) del coste del cuello de botella (lectura de datos), para no pagar una A100 mientras el limitante es el almacenamiento, y reservar el hardware caro para cuando aporte.

Diagnostico:

- En la ejecucion larga en A100 la GPU no supera aproximadamente 5.4 GB de memoria (de 40 GB disponibles) y `compute_seconds` se mantiene estable en torno a 0.5 s, mientras `data_wait_seconds` presenta picos de 3-11 s cada 50-100 pasos. La velocidad observada fue de aproximadamente `0.209 step/s` (unos 5 s por paso), pero el computo solo consume 0.5 s de ese tiempo.
- Conclusion: el entrenamiento esta limitado por entrada/salida (lectura de NIfTI desde Google Drive), no por computo. El pipeline usa actualmente `monai.data.Dataset` plano, sin estrategia de cache (`CacheDataset`/`PersistentDataset`/`SmartCacheDataset`), y lee desde Drive en cada paso.

Explicacion o justificacion de las decisiones tomadas:

- Mientras el entrenamiento siga limitado por I/O, una tarjeta mas barata ofrece practicamente el mismo throughput que la A100, porque ambas pasan la mayor parte del tiempo esperando datos. Pagar una A100 en esta fase es desperdiciar memoria y computo ociosos.
- El pico real de memoria (~5.4 GB) descarta la necesidad de los 40 GB del A100 para la fase de desarrollo y optimizacion.
- Decisiones de hardware por fase:
  - Fase de optimizacion/desarrollo en cloud: usar una GPU economica. Recomendacion principal `L4` (24 GB, generacion Ada, soporta bf16) por ser el punto dulce que aun corre los 5 modelos incluido `swin_unetr` con holgura. `T4` (16 GB) es valida para los modelos pequenos y como opcion gratuita; `swin_unetr` requeriria `use_checkpoint: true`.
  - A100: se reserva exclusivamente para las corridas finales, largas y ya optimizadas, una vez resuelto el I/O.
- El arreglo de fondo del I/O (independiente de la tarjeta) queda como pendiente prioritario: copiar el dataset al disco local del runtime (`/content/`) en lugar de leer de Drive, y/o introducir cache de MONAI. Es la mayor ganancia individual y condiciona la utilidad de cualquier GPU.

Impacto en la memoria final: documenta una decision de eficiencia computacional (uso responsable de recursos) y aporta una justificacion cuantitativa, no anecdotica, de la eleccion de hardware. Refuerza el criterio de "coste computacional asumible" presente en la pregunta de investigacion.

Pendientes o riesgos abiertos:

- Implementar la optimizacion de I/O (copia a runtime local y/o cache MONAI) antes de las corridas finales en cloud.
- Re-perfilar `step/s` y `data_wait_seconds` tras la optimizacion para cuantificar la mejora y reevaluar si `L4` basta o se necesita `A100` en la fase final.

## 2026-06-25 - Viabilidad de entrenar los 4 modelos pequenos en local (M4 Pro) a 128^3

Actividad realizada: medicion empirica de la viabilidad de entrenar cada arquitectura en el backend MPS del M4 Pro y decision de mover el entrenamiento de los 4 modelos pequenos a local. Esto revisa parcialmente la decision del 2026-05-27 que reservaba el M4 Pro solo para sanity checks.

Objetivo metodologico: aprovechar que en local el dataset reside en SSD M.2 (sin el cuello de botella de Google Drive) para liberar la GPU cloud, y verificar antes de comprometer horas de computo que cada modelo corre end-to-end.

Procedimiento seguido:

- Benchmark sintetico de `forward + backward` (tensores aleatorios, sin dataset) en MPS para los 5 modelos, a 96^3 y a 128^3, midiendo segundos por paso y memoria asignada. Script: `scratchpad/bench_models_mps.py`.
- Resultados a 96^3: los 5 modelos corren. `swin_unetr` a 2.85 s/paso.
- Resultados a 128^3 (resolucion del protocolo):
  - `residual_unet_3d`: 0.57 s/paso, memoria ~0.11 GB.
  - `residual_unet_3d_global_weighted`: 0.65 s/paso.
  - `residual_unet_3d_adaptive_gating`: 0.65 s/paso.
  - `attention_unet_3d`: 2.34 s/paso, ~0.22 GB.
  - `swin_unetr`: 124 s/paso (salto no lineal x40 respecto a 96^3), debido a un fallback de MPS en la atencion por ventanas a resolucion plena.
- La memoria nunca fue el limitante (maximo ~1.5 GB asignado); los 24 GB unificados del M4 Pro sobran. El limitante en local es la velocidad de computo de MPS, no la memoria.

Explicacion o justificacion de las decisiones tomadas:

- Los 4 modelos pequenos (`residual_unet_3d`, `residual_unet_3d_global_weighted`, `residual_unet_3d_adaptive_gating`, `attention_unet_3d`) se entrenan en local a 128^3. Justificacion: a 128^3 todos estan por debajo de 2.4 s/paso de computo puro, la memoria sobra y en local no existe el cuello de botella de I/O, asi que el M4 Pro deja de ser solo un entorno de sanity check y pasa a ser plataforma de entrenamiento valida para estos modelos. Esto libera la GPU cloud para `swin_unetr` y las corridas finales.
- `swin_unetr` queda excluido del entrenamiento local a 128^3 (124 s/paso lo hacen inviable: una corrida de pocos miles de pasos serian dias). Se mantiene la decision previa de entrenarlo en cloud. En local solo seria abordable a 96^3.

Decision de hiperparametros (cambio 96^3 -> 128^3 en local):

- Se crea `configs/training/mac_m4_pro_128.yaml`, identico a `mac_m4_pro.yaml` salvo `patch_size` y `sliding_window_roi_size`, que pasan de `[96, 96, 96]` a `[128, 128, 128]`.
- Justificacion del cambio: igualar la resolucion del protocolo de Colab (`colab_pro.yaml`) para que los resultados de los modelos entrenados en local sean directamente comparables con los entrenados en cloud, sin que la resolucion sea una variable de confusion en la comparacion de estrategias de fusion. El benchmark confirma que el coste (≤2.4 s/paso) es asumible en MPS para estos 4 modelos.
- Resto de hiperparametros sin cambios respecto a `mac_m4_pro.yaml` (lr `1e-4`, weight_decay `1e-5`, `samples_per_case=2`, `batch_size=1`, `amp=false` forzado en MPS, `num_workers=6`). No se ha hecho aun tuning de estos valores; cualquier ajuste futuro se registrara aqui con su justificacion.

Procedimiento de lanzamiento (pase de validacion):

- Antes de comprometer una corrida larga (decenas de miles de pasos), se ejecuta primero un pase de validacion de `--max-steps 300` por modelo sobre datos reales del split de entrenamiento. Justificacion: confirmar que el pipeline completo (carga NIfTI -> transforms -> entrenamiento -> validacion sliding window a 128^3 -> guardado de checkpoints) funciona end-to-end para los 4 modelos antes de invertir horas. Al alcanzar `max_steps` el codigo dispara `stop_training`, que fuerza una pasada de validacion y guarda `best.pt`/`last.pt`, de modo que el pase de 300 pasos ejercita tambien la inferencia y el checkpointing.
- Los 4 entrenamientos se ejecutan de forma secuencial (una sola GPU MPS) en segundo plano.
- Nota metodologica: `mean_dice` tras 300 pasos NO es una metrica reportable (igual que en el sanity check de 1500 pasos del 2026-05-27 dio `0.166`); el objetivo de este pase es exclusivamente validar el flujo, no medir calidad.

Artefactos generados:

- `configs/training/mac_m4_pro_128.yaml`
- `scratchpad/bench_models_mps.py` (benchmark de viabilidad)
- `outputs/train/<modelo>_m4_pro_128/` por cada uno de los 4 modelos (pendiente de ejecucion).

Pendientes o riesgos abiertos:

- Tras validar el flujo con 300 pasos, definir el presupuesto de pasos de la corrida real local y lanzarla.
- Vigilar el aviso de MPS sobre el padding constante de mas de 3 dimensiones (usa implementacion via View Ops, con posible impacto de rendimiento).
- Reevaluar `samples_per_case` y `num_workers` en local a 128^3 si el `data_wait_seconds` resulta alto al leer NIfTI de 4 modalidades desde el SSD externo.

### Resultado del pase de validacion (300 pasos)

Los 4 modelos completaron el pase con codigo de salida 0. El flujo end-to-end (carga NIfTI -> transforms -> entrenamiento -> validacion sliding window a 128^3 -> guardado de `best.pt`/`last.pt`) quedo validado en MPS y `data_wait_seconds` se mantuvo en aproximadamente 0.00 s una vez calentados los workers, confirmando que en local no existe el cuello de botella de I/O.

| Modelo | Pasos | compute/paso | Duracion | mean_dice (ET/TC/WT) |
|---|---|---|---|---|
| `residual_unet_3d` | 300 | ~1.2 s | ~12 min | 0.044 (0.000 / 0.046 / 0.086) |
| `residual_unet_3d_global_weighted` | 300 | ~1.2 s | ~12 min | 0.044 (0.000 / 0.046 / 0.086) |
| `residual_unet_3d_adaptive_gating` | 300 | ~1.2 s | ~12 min | 0.030 (0.000 / 0.025 / 0.066) |
| `attention_unet_3d` | 300 | ~4.75 s | ~25 min | 0.049 (0.000 / 0.054 / 0.095) |

Los valores de Dice NO son reportables (300 pasos, por debajo incluso del sanity check de 1500 pasos del 2026-05-27). `ET=0.0` en los 4 es lo esperado. Las 3 variantes residuales dan casi identico porque las capas de fusion (pocos parametros) apenas se entrenan en 300 pasos; la diferencia entre estrategias de fusion solo puede emerger en la corrida real. `attention_unet_3d` confirma ser el mas lento (~4.75 s/paso), como anticipo el benchmark.

## 2026-06-25 - Lanzamiento de la corrida real local (5000 pasos por modelo)

Actividad realizada: tras validar el flujo, se define el presupuesto de la primera corrida real local y se lanza para los 4 modelos pequenos, en secuencial y desatendida durante la noche.

Objetivo metodologico: obtener la primera corrida comparable entre la fusion por concatenacion (baseline) y las dos estrategias de fusion adaptativa, bajo protocolo identico (mismo dataset, splits, semilla, resolucion 128^3 y resto de hiperparametros), suficiente para que la diferencia entre estrategias empiece a ser detectable.

Decision del presupuesto:

- 5000 pasos por modelo. Justificacion: supera los 3000 pasos recomendados como primera corrida en Colab y los 1500 del sanity check del 2026-05-27, y encaja en una ventana nocturna con la velocidad medida (residuales ~1.2-1.5 s/paso, attention ~4.75 s/paso). Una sola semilla (`20260526`); la robustez con multiples semillas queda como trabajo posterior.
- Estimacion de duracion: ~1.5-2 h por modelo residual y ~7 h attention, total aproximado 12-14 h (terminacion prevista por la manana siguiente). `attention_unet_3d` es el pole position del tiempo total.

Decision de hiperparametros (cambios respecto a `mac_m4_pro_128.yaml`, registrados en `configs/training/mac_m4_pro_128_5k.yaml`):

- `validation_interval`: 5 -> 1. Justificacion: 5000 pasos equivalen a ~4.4 epocas (1135 casos/epoca). Con el valor previo (validar cada 5 epocas) no se dispararia ninguna validacion intermedia y `best.pt` coincidiria con `last.pt`. Validando al final de cada epoca se obtiene una curva de Dice por region y una seleccion real del mejor checkpoint.
- `validation_batches`: 2 -> 8. Justificacion: reducir el ruido en la seleccion de `best.pt` durante el entrenamiento. La validacion intra-entrenamiento sigue siendo orientativa; la evaluacion reportable definitiva se hara aparte con `predict` + `evaluate` sobre el split completo de val/test.
- Resto de hiperparametros sin cambios (lr `1e-4` constante sin scheduler, weight_decay `1e-5`, `samples_per_case=2`, `batch_size=1`, `amp=false`, `num_workers=6`). No se introduce scheduler de learning rate en esta corrida para mantener la comparacion limpia; su evaluacion queda como trabajo futuro.

Procedimiento de lanzamiento:

- Script `scratchpad/run_local_4models_5k.sh`, ejecucion secuencial (una sola GPU MPS) en segundo plano.
- Salidas en `outputs/train/<modelo>_m4_pro_128_5k/` (directorios nuevos, sin sobrescribir los artefactos del pase de validacion de 300 pasos).
- Lanzado tras confirmar que el pase de validacion termino (los 4 con rc=0) y que la GPU quedo libre, para no solapar dos entrenamientos en el mismo backend MPS.

Artefactos generados:

- `configs/training/mac_m4_pro_128_5k.yaml`
- `scratchpad/run_local_4models_5k.sh`
- `outputs/train/<modelo>_m4_pro_128_5k/` por cada uno de los 4 modelos (en ejecucion).

Pendientes o riesgos abiertos:

- Al terminar: revisar `train_summary.json` y `train_log.csv` de los 4, comparar curvas de Dice por region y comprobar si las estrategias de fusion adaptativa muestran ya alguna ventaja sobre el baseline concat.
- Ejecutar `predict` + `evaluate` sobre val/test para obtener la tabla reportable (Dice ET/TC/WT + HD95).
- Si 5000 pasos resultan insuficientes para curvas estables, valorar una corrida mas larga (con scheduler de lr) en cloud (L4) una vez resuelto el I/O.

### Resultados parciales de la corrida (3 de 4 modelos, validacion intra-entrenamiento)

Con 3 modelos terminados, las curvas de `mean_dice` (validacion sobre 8 batches, cada epoca) confirman aprendizaje real (de ~0.04 en el pase de 300 pasos a ~0.6):

| Modelo | best mean_dice | best_epoch | ET | TC | WT |
|---|---|---|---|---|---|
| `residual_unet_3d` (concat) | 0.608 | 5 | 0.216 | 0.787 | 0.821 |
| `residual_unet_3d_global_weighted` | 0.615 | 5 | 0.228 | 0.793 | 0.824 |
| `residual_unet_3d_adaptive_gating` | 0.586 | 4 | 0.193 | 0.627 | 0.743 |

Lectura preliminar (NO concluyente; validacion ruidosa de 8 batches, una semilla, sin converger):

- Las curvas de baseline y `global_weighted` siguen subiendo en la epoca 5 (sin meseta): 5000 pasos se quedan cortos.
- Senal a vigilar: `adaptive_gating` (contribucion principal del TFM) va por detras del baseline y muestra inestabilidad (pico en epoca 4 = 0.586, caida a 0.521 en epoca 5). Penaliza sobre todo TC y WT. Hipotesis a investigar (¿necesita mas pasos, warmup, o lr distinto para la compuerta?), no un veredicto.

## 2026-06-26 - Evaluacion reportable sobre el split val (predict + evaluate)

Actividad realizada: encadenar `predict` + `evaluate` sobre el split de validacion completo para los 4 modelos, en cuanto termine la corrida de 5000 pasos.

Objetivo metodologico: obtener metricas reportables (Dice y HD95 por region ET/TC/WT) sobre el split val completo (243 casos), en lugar de la validacion ruidosa de 8 batches usada durante el entrenamiento para seleccionar checkpoint.

Decisiones:

- Split: `val.csv` (243 casos). El split `test.csv` se mantiene reservado (held out) y no se toca en esta fase.
- Checkpoint por modelo: `best.pt` (el de mayor `mean_dice` durante el entrenamiento).
- Inferencia con sliding window a 128^3 (misma `roi_size` que en entrenamiento, `configs/training/mac_m4_pro_128_5k.yaml`), device MPS.
- El proceso se lanza encadenado (espera el marcador DONE de la corrida 5k) para no solapar dos cargas en la GPU MPS.
- Agregacion final en una tabla comparativa (`outputs/evaluation/comparativa_val_5k.csv`) con Dice y HD95 medios por region y Dice medio entre regiones.

Artefactos generados:

- `scratchpad/run_predict_evaluate_5k.sh`, `scratchpad/aggregate_eval.py`
- `outputs/predictions/<modelo>_val_5k/` (NIfTI de predicciones)
- `outputs/evaluation/<modelo>_val_metrics.csv` y `_summary.json`
- `outputs/evaluation/comparativa_val_5k.csv`

### Resultados reportables sobre el split val completo (243 casos)

Metricas Dice y HD95 medias por region, con el `best.pt` de cada modelo (corrida de 5000 pasos, una semilla). Fuente: `outputs/evaluation/comparativa_val_5k.csv`.

| Modelo | mean Dice | ET | TC | WT | HD95 ET | HD95 TC | HD95 WT |
|---|---|---|---|---|---|---|---|
| `attention_unet_3d` | **0.6546** | 0.452 | 0.698 | 0.814 | 22.24 | 19.69 | 18.74 |
| `residual_unet_3d` (concat, baseline) | 0.6070 | 0.361 | 0.668 | 0.792 | 23.05 | 20.82 | 20.46 |
| `residual_unet_3d_global_weighted` | 0.6058 | 0.371 | 0.657 | 0.790 | 20.46 | 18.21 | 18.01 |
| `residual_unet_3d_adaptive_gating` | 0.5881 | 0.360 | 0.631 | 0.774 | 28.43 | 26.41 | 25.15 |

Interpretacion (preliminar; 5000 pasos sin converger, una sola semilla):

- `attention_unet_3d` es claramente el mejor (Dice 0.655, con ventaja marcada en ET = 0.452). Era esperable por capacidad (5.9M params).
- Respecto a la pregunta de investigacion (¿la fusion adaptativa mejora la fusion por concatenacion?): en esta corrida la respuesta es NO.
  - `global_weighted` queda en empate tecnico con el baseline en Dice (0.6058 vs 0.6070, diferencia dentro del ruido), aunque mejora el HD95 en las tres regiones (fronteras algo mas limpias a igualdad de solapamiento). Es el unico indicio favorable a una fusion ponderada.
  - `adaptive_gating` (contribucion principal del TFM) es la PEOR de la familia residual tanto en Dice (0.588) como en HD95 (28.4/26.4/25.1, claramente mas alto). Subrinde frente al baseline en todas las metricas. Coincide con la inestabilidad ya observada en la validacion intra-entrenamiento (pico en epoca 4, caida en epoca 5).
- Conclusion metodologica: el resultado actual NO valida la hipotesis. Pero no es concluyente: 5000 pasos se quedan cortos (las curvas seguian subiendo), es una sola semilla y la compuerta adaptativa puede requerir warmup, un lr distinto o mas pasos para estabilizarse. Antes de reportar un resultado negativo en la memoria hay que descartar que sea un problema de optimizacion y no de la estrategia en si.

Decision (2026-06-26): se pausa el computo en este punto y se documentan estos resultados como preliminares. Los siguientes pasos (diagnostico de la inestabilidad de `adaptive_gating`, multi-semilla, replica en cloud con mas pasos e inclusion de `swin_unetr`) quedan como trabajo futuro registrado, a retomar cuando se decida. No se lanzan mas entrenamientos por ahora.

Pendientes o riesgos abiertos:

- Investigar la inestabilidad de `adaptive_gating`: corrida mas larga y/o ajuste de hiperparametros de la compuerta (warmup, lr especifico, regularizacion) antes de concluir. Documentar cada ajuste con su justificacion.
- Repetir con varias semillas para distinguir senal de ruido en las diferencias entre estrategias de fusion.
- Una vez resuelto el I/O en cloud, replicar la comparacion en L4/A100 con mas pasos y AMP, e incluir `swin_unetr`.
- El split `test.csv` se reserva para la evaluacion final una vez fijada la configuracion definitiva.
- **PENDIENTE: lanzar la evaluacion sobre el split `test.csv` (243 casos, held out).** Las metricas actuales en `outputs/evaluation/` son todas sobre `val.csv`. El Capitulo 3 de la memoria establece que las cifras finales deben reportarse sobre el conjunto de test reservado (validacion solo para monitorizacion), por lo que el Capitulo 5 sera incoherente hasta generar estas metricas. Reutilizar el flujo `predict` + `evaluate` ya existente (`scratchpad/run_predict_evaluate_5k.sh`, `scratchpad/aggregate_eval.py`) apuntando a `test.csv`, una vez fijada la configuracion definitiva de entrenamiento.

## 2026-06-26 - Plan global del TFM e indice de la memoria (estructura aprobada por el tutor)

Actividad realizada: analisis del estado global del TFM (no solo del codigo) y formalizacion del roadmap y de la estructura del manuscrito.

Objetivo metodologico: situar los resultados experimentales dentro del contrato del TFM (criterios de exito de `decisiones-iniciales.md §10`) y ordenar el trabajo restante por dependencias, antes de gastar mas computo.

Procedimiento y hallazgos:

- Contraste del estado actual con los tres niveles de exito: el TFM supera el nivel **minimo** (pipeline reproducible + baseline 3D + evaluacion interna), pero faltan 2 de los 3 pilares del **objetivo defendible**: el modelo Transformer-UNet (Swin-UNETR, que da nombre al TFM) sin entrenar, y nnU-Net (baseline fuerte) solo con smoke test. El tercer pilar (ablacion de fusion) esta en duda por el bajo rendimiento de `adaptive_gating`.
- Adopcion de la estructura de manuscrito aprobada por el tutor (CON-2026-05-28-M1, recibida 2026-06-25): Introduccion, Marco teorico y estado del arte, Metodologia (fases de alto nivel), Desarrollo (detalle tecnico), Resultados, Conclusiones.
- Identificacion de un desajuste a corregir: el Capitulo 3 actual contiene detalle tecnico que, segun el criterio del tutor, corresponde al Capitulo 4. Pendiente de confirmar el reparto exacto en la reunion.

Artefactos generados:

- `docs/memoria/indice-memoria.md` (indice maestro de los 6 capitulos, con estado y material de partida).
- `docs/memoria/plan-tfm.md` (roadmap completo: criterios de exito, track experimental, track de redaccion, dependencias y riesgos).
- Nota en `docs/memoria/README.md` marcandolo como material legado y apuntando al indice y al plan.

Pendientes o riesgos abiertos: los registrados en `plan-tfm.md` (riesgo titulo vs. evidencia por Swin sin entrenar; contribucion en duda por `adaptive_gating`; resultados aun preliminares sobre val). Inmediato sin computo: actualizar el README maestro e ir preparando los inputs de la reunion con el tutor.

## 2026-07-13 - Reunion con el tutor: cierre de decisiones estrategicas y de estructura

Actividad realizada: se celebra la reunion con el tutor preparada en `docs/pre-design/reunion-tutor-2026-06-29.md` y se cierran las decisiones que quedaban abiertas (bloques A, B, C y D).

Objetivo metodologico: desbloquear el track de redaccion (reparto Metodologia/Desarrollo, tabla comparativa, capitulo de tipos de imagen) y fijar el limite operativo de la exploracion de la fusion adaptativa, para poder retomar el trabajo con criterios acordados y no interpretados.

Decisiones acordadas:

- Secuencia experimental (A.1): validada. Se mantiene arreglo de I/O -> Swin-UNETR en L4/A100 -> nnU-Net como baseline fuerte.
- Limite de la fusion adaptativa (A.2-bis): presupuesto de 2-3 dias de ejecucion para agotar las vias (corridas largas + ajuste de la compuerta: warmup, lr especifico, regularizacion). Si tras ese presupuesto no hay mejora sobre el baseline concat, se reporta como resultado negativo defendible. Este limite acota la restriccion previa del alumno de "no aceptar resultado negativo hasta agotar vias".
- Evaluacion en test (A.3): confirmada. El split `test.csv` (held out) solo se evalua una vez congelada la configuracion definitiva de entrenamiento; hasta entonces solo se usa `val.csv` para monitorizacion.
- Reparto Metodologia/Desarrollo (B.1): validado. El capitulo 3 se aligera a fases de alto nivel (familiarizacion, diseno experimental, protocolo de evaluacion) y el detalle tecnico se consolida en el capitulo 4, eliminando la duplicacion actual (§3.4≈§4.2, §3.5≈§4.5).
- Nivel de detalle (B.2): confirmado. Justificacion clinica/tecnica de cada decision, diagramas de flujo de la pipeline y de arquitectura de los modelos, y pseudocodigo solo cuando aporte sobre la prosa.
- Tabla comparativa de repositorios (C): una sola tabla (no se separan frameworks e implementaciones). El tutor no dio feedback adicional sobre columnas ni facilito un ejemplo propio; se lleva la version minima viable a criterio del alumno.
- Caracterizacion clinica por modalidad (D.1): basta una tabla que relacione cada modalidad (`t1n`, `t1c`, `t2w`, `t2f`) con el tejido/lesion que realza y su relevancia para ET/TC/WT; no se exige descripcion radiologica extensa con referencias clinicas.
- Ejemplos visuales (D.2): se incluyen cortes en la memoria con proposito ilustrativo y analitico (ambos); el numero concreto queda a criterio del alumno.

Impacto en la memoria final: estas decisiones fijan la estructura de los capitulos 3, 4 y del capitulo de tipos de imagen/dataset, el formato de la tabla comparativa del estado del arte y el criterio para cerrar el estudio de ablacion. Se actualizan en consecuencia `docs/pre-design/reunion-tutor-2026-06-29.md`, `docs/memoria/plan-tfm.md` y `docs/memoria/indice-memoria.md`.

Pendientes o riesgos abiertos:

- Track B (sin computo): re-nivelar el capitulo 3 a fases de alto nivel trasladando el detalle al capitulo 4; actualizar el README maestro; completar la tabla comparativa (una tabla, columnas minimas); anadir tabla modalidad->tejido/lesion y seleccionar los cortes axiales ilustrativos/analiticos.
- Track A (computo): implementar el arreglo de I/O y ejecutar la secuencia Swin-UNETR -> nnU-Net; dedicar el presupuesto de 2-3 dias a estabilizar `adaptive_gating` antes de concluir; corrida final multi-semilla y evaluacion sobre `test.csv`.
