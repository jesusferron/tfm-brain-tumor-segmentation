# Bitacora metodologica del TFM

Ultima actualizacion: 2026-07-17 (Track A: scheduler cosine anadido y sonda de convergencia -> presupuesto final fijado en 15000 pasos; concat convergido ~0.69 vs 0.607 a 5000 pasos)

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

## 2026-07-14 - Arreglo de I/O: cache MONAI seleccionable por configuracion

Actividad realizada: se implementa una estrategia de cache seleccionable por configuracion en la pipeline de datos para eliminar el cuello de botella de I/O diagnosticado el 2026-06-25 (A100 infrautilizado leyendo NIfTI desde Google Drive: `compute` ~0.5 s/paso frente a picos de `data_wait` de 3-11 s). Es el primer paso de la ruta critica del Track A (prerrequisito de Swin-UNETR y nnU-Net).

Objetivo metodologico: que el entrenamiento en cloud deje de estar limitado por la lectura desde Drive, de modo que la GPU (L4 para desarrollo, A100 para corridas finales) se aproveche de verdad, sin cambiar el dataset experimental, los splits, la semilla ni la resolucion.

Procedimiento seguido:

- Se anade `build_cached_dataset` en `tfm_brats/monai_pipeline.py`, que construye el dataset MONAI segun `cache_mode`:
  - `none` (por defecto): `monai.data.Dataset` plano; conserva exactamente el comportamiento anterior. Adecuado cuando los datos residen en SSD local (sin cuello de I/O).
  - `memory`: `CacheDataset` en RAM, con `cache_rate` o `cache_num` para acotar (el split completo de train no cabe en RAM).
  - `persistent`: `PersistentDataset` que cachea a disco local (`cache_dir`). Es el arreglo para el cuello de Drive: tras la primera epoca, el prefijo determinista de las transforms (carga NIfTI + normalizacion de intensidad + padding) se sirve desde disco local en lugar de releer y renormalizar desde Drive.
- `build_dataloader` y `train_one_run` propagan los parametros de cache. En modo `persistent` se usan subdirectorios separados `train/` y `val/` bajo `cache_dir`.
- El prefijo cacheado es el determinista; MONAI reejecuta las transforms aleatorias (`RandCropByPosNegLabeld`, `RandFlipd`) en cada paso, de modo que la augmentation no se ve afectada.
- Se registran `cache_mode`, `cache_rate`, `cache_num` y `cache_dir` en `train_summary.json` y en la linea de setup del log, para trazabilidad.
- `configs/training/colab_pro.yaml` pasa a `cache_mode: persistent` con `cache_dir: /content/tfm_cache/colab_pro` (disco local del runtime). Los perfiles locales (`mac_m4_pro*.yaml`) se mantienen en `none` porque en local no hay cuello de I/O.
- Se actualiza `docs/colab-pro-baseline-residual-unet.md` (nueva seccion 7c) documentando las dos optimizaciones complementarias: copiar el dataset a `/content` y activar el cache persistente en disco local.

Justificacion de las decisiones:

- El cache persistente en disco local es la opcion recomendada para BraTS-GLI: el split de train (1135 casos) no cabe en RAM como `CacheDataset` completo (cada caso preprocesado ~140 MB), pero si cabe en el disco del runtime.
- `cache_dir` debe estar en disco local (`/content`), nunca en Drive; en Drive el cache seria tan lento como el problema que resuelve.
- Mantener `none` como defecto preserva la retrocompatibilidad de todos los YAML y tests existentes.

Verificacion (local, backend CPU, sobre datos reales del split):

- Test unitario nuevo `tests/test_dataloader_cache.py` (5 casos: cada modo + rutas de error). Suite completa: 11 tests OK (antes 6).
- `compileall` correcto sobre `tfm_brats` y `tests`.
- Corrida real de 2 pasos con `cache_mode: persistent`:
  - RUN 1 (construye cache): `data_wait` ~1.0 s/paso, ~0.85 step/s; se generan 2 ficheros `.pt` (uno por caso de train).
  - RUN 2 (reutiliza cache): `data_wait` cae a ~0.07 s/paso, velocidad ~6.5 step/s (mejora ~7x en I/O); los `.pt` no se reescriben (mtime intacto) y la loss es identica a RUN 1 (misma semilla; el cache preserva la correccion del prefijo determinista).
  - RUN 3 (`cache_mode: none`, defecto): entrena sin cambios respecto al comportamiento previo.
- La mejora medida (~7x) es sobre SSD local, donde el I/O ya era pequeno; sobre Google Drive, donde `data_wait` dominaba, el efecto esperado es mayor.

Evidencia generada:

- `tfm_brats/monai_pipeline.py` (`build_cached_dataset`, `build_dataloader` y `train_one_run` extendidos)
- `tests/test_dataloader_cache.py`
- `configs/training/colab_pro.yaml` (`cache_mode: persistent`, `cache_dir`)
- `docs/colab-pro-baseline-residual-unet.md` (seccion 7c)

Impacto en la memoria final: documenta una decision de eficiencia computacional que materializa el diagnostico del 2026-06-25 y da soporte al criterio de "coste computacional asumible" de la pregunta de investigacion. Habilita las corridas de Swin-UNETR y nnU-Net del Track A.

Pendientes o riesgos abiertos:

- Ejecutar en Colab la secuencia recomendada (copia a `/content` + cache persistente) y re-perfilar `data_wait_seconds` y `steps_per_second` tras la primera epoca para cuantificar la mejora real en cloud y decidir si L4 basta o hace falta A100 en la fase final.
- Vigilar el espacio en disco de `/content` al cachear el split completo; si se agota, reducir el split cacheado o limpiar `cache_dir`.
- En backends con multiprocessing por `spawn` (macOS), `cache_mode: memory` con `num_workers>0` recachearia por worker; por eso en local se usa `none` (y `persistent` seria la alternativa si se quisiera cache en local).

## 2026-07-14 - Perfil L4 y config de Swin-UNETR con gradient checkpointing

Actividad realizada: se prepara el segundo paso de la ruta critica del Track A (entrenar el Transformer-UNet que da nombre al TFM) creando un perfil de entrenamiento para GPU L4 y una variante del modelo Swin-UNETR con gradient checkpointing, para que quepa en 24 GB.

Objetivo metodologico: dejar listo, verificado y documentado el camino para lanzar Swin-UNETR en cloud sin ensayo-error de memoria, respetando la decision de hardware del 2026-06-25 (L4 para desarrollo, A100 para corridas finales).

Procedimiento y decisiones:

- `configs/training/colab_l4.yaml`: perfil para L4 (24 GB). Difiere de `colab_pro.yaml` en `batch_size: 1` (frente a 2) para que el modelo mas pesado quepa en 24 GB, y en `cache_dir: /content/tfm_cache/colab_l4`. Mantiene patch 128, `samples_per_case: 2`, AMP, validacion cada epoca con 8 batches y `cache_mode: persistent`. La resolucion 128 se conserva para comparabilidad con el resto de corridas.
- `configs/model/swin_unetr_l4.yaml`: identico a `swin_unetr.yaml` salvo `use_checkpoint: true`. El gradient checkpointing de MONAI intercambia computo por memoria; es la primera mitigacion documentada para el coste de memoria de los 62M parametros de Swin en L4. En A100 (40 GB) puede usarse `swin_unetr.yaml` sin checkpointing (mas rapido).
- `docs/colab-pro-baseline-residual-unet.md`: nueva seccion 8b con smoke test y corrida de Swin en L4, y el escalado si hay OOM (bajar patch a 96, o pasar a A100 sin checkpointing).

Justificacion:

- Se mantiene una sola resolucion (128) entre modelos para no introducir la resolucion como variable de confusion en la comparacion de estrategias de fusion y arquitecturas.
- `batch_size: 1` en L4 es el valor seguro para el peor caso (Swin); los modelos pequenos tambien caben con holgura. La corrida final unificada y multi-semilla (pendiente) fijara el protocolo definitivo.
- No se cambian lr, weight_decay ni el resto de hiperparametros respecto a los perfiles previos; cualquier ajuste futuro se registrara aqui.

Verificacion (local, CPU):

- `configs/training/colab_l4.yaml` y `configs/model/swin_unetr_l4.yaml` cargan y parsean correctamente via `tfm_brats.config.load_config`.
- `build_model` construye Swin-UNETR con `use_checkpoint: true` (62.19M parametros) y ejecuta forward + backward correctos a patch 64 en CPU, con salida `(1, 3, 64, 64, 64)`.
- No se ha ejecutado en GPU todavia: el pico real de memoria y `step_seconds` en L4 se mediran en la primera corrida en Colab.

Evidencia generada:

- `configs/training/colab_l4.yaml`
- `configs/model/swin_unetr_l4.yaml`
- `docs/colab-pro-baseline-residual-unet.md` (seccion 8b)

Impacto en la memoria final: habilita el pilar 2 del objetivo defendible (Transformer-UNet). El detalle de gradient checkpointing y el perfil por hardware alimentan el capitulo de Desarrollo y la discusion de coste computacional.

Pendientes o riesgos abiertos:

- Ejecutar el smoke test de Swin en L4 y, si pasa, la corrida de 5000 pasos; registrar GPU, pico `gpu_memory_gb`, `step_seconds` y si hizo falta bajar el patch.
- Si L4 no basta ni con checkpointing a patch 96, escalar a A100 con `swin_unetr.yaml` + `colab_pro.yaml`.
- Tras Swin, continuar con nnU-Net (pilar 1) y luego el presupuesto de 2-3 dias para `adaptive_gating` (pilar 3).

## 2026-07-14 - Baseline fuerte nnU-Net: conversor del split completo y flujo en cloud

Actividad realizada: se prepara el pilar 1 del objetivo defendible (baseline fuerte nnU-Net) mas alla del smoke test del 2026-05-18. Se implementa un conversor que transforma los splits versionados del TFM al formato nativo de nnU-Net v2 y se documenta el flujo completo de entrenamiento y evaluacion en cloud, reutilizando el `evaluate` del TFM para obtener metricas comparables.

Objetivo metodologico: que nnU-Net entrene sobre exactamente el mismo split `train` que el resto de modelos y se evalue sobre el mismo `val`/`test`, con Dice y HD95 por ET/TC/WT calculados por el mismo codigo, de modo que el baseline fuerte sea directamente comparable con los modelos MONAI (residuales, attention, Swin).

Decisiones cerradas (resuelven pendientes abiertos desde 2026-05-18):

- Conversion directa al formato nnU-Net v2, no el apilado 4D via `nnUNetV2Runner` del smoke test. Cada modalidad se enlaza con symlink usando el naming de canal de nnU-Net (`{case_id}_0000..0003.nii.gz`); no se duplican datos (opcion `--link-mode copy` si el runtime no permite symlink). Motivo: el apilado 4D de 1135+243 casos duplicaria cientos de GB y anadiria un paso fragil; la conversion directa es el camino estandar y eficiente en disco.
- Uso de la CLI nativa `nnUNetv2_*` en lugar del `nnUNetV2Runner` de MONAI. La friccion del runner (apilado 4D) hace preferible la ruta oficial para el run completo; el smoke test ya demostro la viabilidad tecnica.
- Etiquetas 0-4 preservadas. Inspeccion local de casos reales confirma que BraTS-GLI 2024 usa etiquetas 0,1,2,3,4 consecutivas (0=fondo, 1=NCR, 2=ED, 3=ET, 4=RC; label 1 raro pero presente). nnU-Net las acepta como problema multiclase estandar. Al preservarlas, el mapa predicho usa el mismo esquema entero que el ground truth y el `evaluate` del TFM funciona sin conversor de predicciones.
- Identificador nnU-Net = `case_id`. El `case_id` no contiene `_`, asi que el parseo `{id}_{canal}` de nnU-Net es inambiguo y la prediccion sale como `{case_id}.nii.gz`, exactamente lo que espera el `evaluate` del TFM. Sin renombrado intermedio.
- Split `val` a `imagesTs` (imagenes sin etiqueta): queda fuera de los folds internos de nnU-Net, held out del entrenamiento. El split `test` no se toca hasta la evaluacion final.
- `3d_fullres`, fold 0 (baseline de un solo fold; el ensemble de 5 folds queda fuera del presupuesto). Trainer reducido `nnUNetTrainer_250epochs` (el defecto son 1000 epocas, dias en una GPU); 250 epocas es el compromiso de presupuesto, con el 1000-epocas como opcion canonica documentada.

Verificacion (local, sin ejecutar nnU-Net):

- `compileall` correcto del conversor.
- Ejecucion del conversor con `--max-cases 2` a un directorio temporal: genera `imagesTr` (2x4 symlinks con naming correcto apuntando a los NIfTI reales), `labelsTr` (`{case_id}.nii.gz`), `imagesTs` con casos de `val` distintos de `train` (sin fuga), y `dataset.json` con `channel_names` {0:t1n,1:t1c,2:t2w,3:t2f} y `labels` {background:0,NCR:1,ED:2,ET:3,RC:4}.
- Comprobacion de que los symlinks resuelven a NIfTI validos: 4 canales con shape identica y label con la misma shape y valores dentro de 0-4.
- No se ejecuto `plan_and_preprocess`, entrenamiento ni prediccion en local (requieren GPU y horas; se haran en Colab).

Evidencia generada:

- `scripts/nnunet/prepare_brats_gli_nnunet_full.py`
- `configs/nnunet/brats_gli_2024_full.yaml`
- `requirements/nnunet.txt`
- `docs/nnunet-baseline.md` (flujo completo en cloud: convertir -> plan/preprocess -> train -> predict val -> evaluate)

Impacto en la memoria final: habilita el pilar 1 (baseline fuerte). El detalle de conversion, esquema de etiquetas y protocolo de comparabilidad (mismo split, mismas metricas) alimenta el capitulo de Desarrollo y la discusion de resultados, donde nnU-Net actuara como referencia frente a la que situar Swin-UNETR y las estrategias de fusion.

Pendientes o riesgos abiertos:

- Ejecutar el flujo en Colab (preferible A100) y registrar tiempo, pico de memoria y metricas de `val`; comparar con Swin y los residuales.
- Confirmar que `nnUNetv2_plan_and_preprocess --verify_dataset_integrity` acepta el dataset generado (esperado, etiquetas declaradas y consecutivas); si detecta algo, ajustar `dataset.json`.
- Decidir, a la vista del tiempo real, si se sube a 1000 epocas o se mantiene 250 para el baseline reportable.
- Evaluacion final sobre `test` solo con la configuracion congelada (regenerar `imagesTs` con `--test-split test.csv`).

## 2026-07-14 - Correccion del arreglo de I/O: cache persistente agota el disco de Colab

Actividad realizada: durante el primer entrenamiento real de Swin-UNETR en L4 (paso ~1090 de la corrida de 5000), Colab reporto disco casi lleno (188 GB de 235 GB). Se diagnostica la causa y se revisa la estrategia de I/O introducida el 2026-07-14.

Diagnostico: el fallo lo causa el cache persistente (`cache_mode: persistent`) sobre el split completo. `PersistentDataset` guarda el prefijo determinista de las transforms (imagen de 4 canales float32 a resolucion completa + label de 3 canales) como `.pt`, ~150 MB por caso (medido en la verificacion local: 144 MB/caso). Con 1135 casos de train + 243 de val (~1378), el cache ocupa ~200 GB, que sumado a la copia del dataset y al sistema agota el disco de Colab (~235 GB). Era el riesgo anotado en la entrada de I/O del 2026-07-14, ahora materializado a escala completa.

Decision (revision de la entrada de I/O del 2026-07-14): en cloud se usa `cache_mode: none` y se confia unicamente en copiar el dataset al disco local del runtime (`/content`). Justificacion: el objetivo del arreglo de I/O era evitar la lectura lenta desde Google Drive; copiar el dataset a SSD local ya elimina ese cuello por si solo (en las corridas locales del M4, leyendo de SSD con `cache_mode: none`, `data_wait_seconds` ya era ~0 tras calentar los workers). El cache anadia un ahorro marginal (recomputar la normalizacion, barato frente al forward/backward) a cambio de ~200 GB de disco que Colab no tiene. La copia del dataset ocupa ~30 GB, holgada.

El mecanismo de cache seleccionable (`build_cached_dataset`, `cache_mode` none|memory|persistent) se mantiene en el codigo: es correcto y util cuando el dataset vive en almacenamiento lento y hay disco de sobra, o para un subconjunto (`memory` + `cache_num`). Solo se cambia el valor por defecto de las configs de cloud.

Cambios aplicados:

- `configs/training/colab_l4.yaml` y `configs/training/colab_pro.yaml`: `cache_mode: persistent` -> `cache_mode: none` (se elimina `cache_dir`), con comentario explicando el motivo.
- `docs/colab-pro-baseline-residual-unet.md` (seccion 7c): la copia del dataset a `/content` pasa a ser el arreglo de I/O; se documenta por que NO se usa cache en cloud (el split completo no cabe en disco).
- `notebooks/colab_swin_unetr_l4.ipynb`: se actualizan los textos que mencionaban el cache persistente.

Recuperacion inmediata en la sesion afectada: parar el entrenamiento, `rm -rf /content/tfm_cache` para liberar disco, `git pull` y relanzar la celda 8. Se pierden los ~1090 pasos porque la epoca 1 (~1135 pasos) no habia cerrado y no se habia guardado checkpoint.

Impacto en la memoria final: matiza la decision de eficiencia de I/O. La leccion (copiar a disco local vs cachear preprocesado, y el limite de disco del entorno) es material util para la discusion de coste computacional y reproducibilidad en el capitulo de Desarrollo.

Pendientes o riesgos abiertos:

- Relanzar Swin-UNETR en L4 con `cache_mode: none` y confirmar en `train_log.csv` que `data_wait_seconds` se mantiene bajo leyendo desde `/content`.
- Vigilar el disco tambien en el flujo nnU-Net: su preprocesado genera su propia copia; con symlinks en `imagesTr` el crudo no se duplica, pero `nnUNet_preprocessed` si ocupa. Revisar espacio antes de entrenar.

## 2026-07-14 - Swin-UNETR entrenado en L4: mejor modelo, cierra el pilar 2

Actividad realizada: primera corrida completa de Swin-UNETR en cloud (GPU L4) con el perfil `colab_l4.yaml` (`cache_mode: none`, dataset copiado a `/content`, gradient checkpointing) y evaluacion reportable sobre el split `val` completo (243 casos) con el `evaluate` del TFM. Es el pilar 2 del objetivo defendible: el Transformer-UNet que da nombre al TFM.

Objetivo metodologico: entrenar y situar Swin-UNETR frente a los modelos convolucionales bajo el mismo protocolo (mismo split, misma resolucion 128, mismas metricas Dice/HD95 por ET/TC/WT), y confirmar que el arreglo de I/O permite entrenar en cloud sin cuello de lectura.

Configuracion de la corrida:

- Modelo: `configs/model/swin_unetr_l4.yaml` (SwinUNETR 62.19M, `feature_size=48`, `use_checkpoint: true`).
- Entrenamiento: `configs/training/colab_l4.yaml`, 5000 pasos, `batch_size=1`, `samples_per_case=2`, patch 128, AMP, lr `1e-4`, 1 semilla (`20260526`).
- Duracion ~2.75 h (9889 s). Pico de memoria GPU ~12.85 GB de 24 (holgura amplia).
- I/O: `data_wait_seconds` ~0.0004 s por paso (frente a picos de 3-11 s leyendo de Drive). El cuello pasa a ser el computo (~1.92 s/paso). El arreglo de I/O (copia a disco local, sin cache) queda validado en cloud.

Resultados reportables (val, 243 casos). Fuente: `outputs/evaluation/swin_unetr_l4_val_metrics_summary.json`.

| Region | Dice media | Dice mediana | HD95 media (casos finitos) | HD95 mediana |
|---|---|---|---|---|
| ET | 0.567 | 0.750 | 6.39 (190/243) | 2.45 |
| TC | 0.745 | 0.833 | 11.00 (233/243) | 4.00 |
| WT | 0.834 | 0.887 | 10.55 (242/243) | 3.61 |

mean Dice (media de las tres regiones): 0.715.

Comparativa con los modelos previos (val, 5000 pasos, 1 semilla):

| Modelo | mean Dice | ET | TC | WT |
|---|---|---|---|---|
| **swin_unetr_l4** | **0.715** | **0.567** | **0.745** | **0.834** |
| attention_unet_3d | 0.655 | 0.452 | 0.698 | 0.814 |
| residual_unet_3d (concat) | 0.607 | 0.361 | 0.668 | 0.792 |
| residual + global_weighted | 0.606 | 0.371 | 0.657 | 0.790 |
| residual + adaptive_gating | 0.588 | 0.360 | 0.631 | 0.774 |

Interpretacion:

- Swin-UNETR es el mejor modelo con margen claro, especialmente en ET (0.567 vs 0.452 del siguiente), la region mas dificil. Cierra el pilar 2 y resuelve el mayor riesgo del TFM (titulo vs. evidencia).
- Matiz media/mediana en ET: media 0.567 pero mediana 0.750. La media la arrastran casos con poco o ningun tumor realzante, donde un falso positivo hunde el Dice; la mediana refleja el comportamiento tipico. En la memoria se reportaran ambas.
- HD95 sobre casos finitos: ET 190/243, TC 233/243, WT 242/243. Los casos infinitos corresponden a ausencia de la region en prediccion o en ground truth. Las medias de HD95 se calculan solo sobre finitos; hay que declararlo explicitamente.
- No es un resultado final: 5000 pasos, 1 semilla, sobre val (no test). Swin (62M) esta probablemente infraentrenado a 5000 pasos; su margen podria crecer en la corrida final mas larga.

Artefactos: `outputs/train/swin_unetr_l4/` (train_summary.json, train_log.csv, checkpoints/best.pt), `outputs/evaluation/swin_unetr_l4_val_metrics{.csv,_summary.json}`. Copiados a Google Drive (`TFM-resultados/swin_unetr_l4/`) para persistencia.

Impacto en la memoria final: aporta el resultado central del capitulo de Resultados (Swin-UNETR como mejor arquitectura) y da soporte al titulo. La comparativa alimenta la tabla principal del capitulo 5.

Pendientes o riesgos abiertos:

- Entrenar el baseline fuerte nnU-Net (pilar 1), ya preparado, preferiblemente en A100.
- Dedicar el presupuesto de 2-3 dias a `adaptive_gating` (pilar 3) antes de concluir.
- Corrida final unificada (mas pasos + multi-semilla) y evaluacion sobre `test` con la configuracion congelada; solo entonces las cifras son finales.

## 2026-07-15 - nnU-Net 3d_fullres en curso: tiempos y observacion de hardware

Actividad realizada: se lanza el entrenamiento del baseline nnU-Net (`3d_fullres`, fold 0, `nnUNetTrainer_250epochs`) en Colab con A100, tras convertir el split completo (paso 6) y preprocesar (paso 8). Se anotan tiempos y utilizacion de GPU para la decision de hardware.

Datos observados:

- `plan_and_preprocess` completado sin error de integridad. Disco tras preprocesar: 120 GB usados de 236 (117 GB libres); margen suficiente para el entrenamiento (solo escribe checkpoints).
- Memoria GPU en entrenamiento: ~8.6 GB de 40. Es el presupuesto de VRAM que nnU-Net planifica por defecto para `3d_fullres` (~8 GB); no usa mas aunque la GPU tenga 40. Confirma que la memoria no es criterio para elegir GPU con nnU-Net.
- Utilizacion de GPU oscilante: muestras de 19% (183 W) y 83% (330 W). El pipeline es mayormente GPU-bound con stalls periodicos de carga de datos (augmentation de nnU-Net, CPU). No es GPU ociosa.
- Tiempo por epoca: 66.4 s (una "epoca" de nnU-Net = 250 iteraciones fijas). Total estimado 250 x 66.4 s ~= 4.6 h + validacion interna final ~= 5 h.

Observacion de hardware (matiz sobre la decision del 2026-06-25):

- A diferencia de nuestra pipeline MONAI (limitada por I/O de Drive), nnU-Net lee el preprocesado desde disco local y su cuello alterna entre GPU y CPU. Con ~66 s/epoca y util oscilante, la A100 aporta: una L4 (menos computo) se estima en ~100-130 s/epoca (~7-9 h), aproximadamente el doble. Para el baseline de una sola vez la A100 es defendible; para repeticiones, L4 cambia coste por ~2x de tiempo. No es un veredicto tajante (la util oscila); la referencia real es el tiempo/epoca.
- El presupuesto fijo de ~8 GB de VRAM de nnU-Net hace el baseline reproducible en hardware modesto (T4/L4 caben de sobra en memoria); util material para la discusion de coste computacional de la memoria.

Pendiente: al terminar (~5 h), ejecutar predict sobre `val` + evaluate con el CLI del TFM y anadir nnU-Net a la comparativa junto a Swin-UNETR; registrar las metricas reportables.

### Resultados reportables de nnU-Net sobre val (243 casos)

Fuente: `outputs/evaluation/nnunet_3dfullres_val_metrics_summary.json`. Cierra el pilar 1.

| Region | Dice media | Dice mediana | HD95 media (finitos) | HD95 mediana |
|---|---|---|---|---|
| ET | 0.719 | 0.891 | 3.08 (207/243) | 1.00 |
| TC | 0.874 | 0.930 | 3.47 (238/243) | 1.41 |
| WT | 0.913 | 0.947 | 2.97 (242/243) | 1.41 |

mean Dice: 0.835.

Comparativa completa (val, 243 casos):

| Modelo | mean Dice | ET | TC | WT | HD95 ET | HD95 TC | HD95 WT |
|---|---|---|---|---|---|---|---|
| **nnU-Net 3d_fullres** (250 ep) | **0.835** | 0.719 | 0.874 | 0.913 | 3.08 | 3.47 | 2.97 |
| swin_unetr_l4 (5000 pasos) | 0.715 | 0.567 | 0.745 | 0.834 | 6.39 | 11.00 | 10.55 |
| attention_unet_3d (5000) | 0.655 | 0.452 | 0.698 | 0.814 | 22.24 | 19.69 | 18.74 |
| residual_unet_3d concat (5000) | 0.607 | 0.361 | 0.668 | 0.792 | 23.05 | 20.82 | 20.46 |
| residual + global_weighted (5000) | 0.606 | 0.371 | 0.657 | 0.790 | 20.46 | 18.21 | 18.01 |
| residual + adaptive_gating (5000) | 0.588 | 0.360 | 0.631 | 0.774 | 28.43 | 26.41 | 25.15 |

Interpretacion:

- nnU-Net es el mejor con margen y actua como techo de referencia (baseline fuerte), sobre todo en HD95 (medianas ~1-1.4 mm; fronteras mucho mas limpias) y en ET (0.719).
- Matiz metodologico critico: la comparacion NO es justa por presupuesto. nnU-Net entreno a convergencia (250 epocas x 250 iteraciones) frente a los 5000 pasos (~4.4 epocas) de los modelos MONAI, infraentrenados. Parte de la ventaja de nnU-Net es mayor entrenamiento, no solo arquitectura. La comparacion arquitectonica justa exige la corrida final a convergencia para todos los modelos; hasta entonces, nnU-Net se reporta como referencia/techo, no como competidor en igualdad de condiciones.
- Se mantiene el matiz media/mediana (los casos sin ET hunden la media) y el HD95 sobre finitos (ET 207/243) que ya se anoto para Swin.

Artefactos: `outputs/evaluation/nnunet_3dfullres_val_metrics{.csv,_summary.json}` y el modelo en `nnUNet_results/Dataset725_BraTSGLI2024`, copiados a Google Drive (`TFM-resultados/nnunet_3dfullres/`).

Estado de pilares tras esta entrada: pilar 1 (baseline fuerte) y pilar 2 (Transformer-UNet) cerrados; queda el pilar 3 (ablacion de fusion), pendiente del presupuesto de 2-3 dias para `adaptive_gating`.

## 2026-07-16 - Pilar 3: diagnostico de `adaptive_gating` y variantes para la exploracion

Actividad realizada: se prepara la exploracion de la fusion adaptativa (contribucion principal, pilar 3) dentro del presupuesto de 2-3 dias acordado con el tutor. Se diagnostica por que la corrida preliminar quedo por debajo del baseline, se anaden palancas de ajuste por configuracion y se define un plan de corridas con criterio de decision.

Objetivo metodologico: antes de gastar el presupuesto, entender la causa del bajo rendimiento y preparar variantes que ataquen la causa real, para poder concluir con fundamento si la hipotesis se sostiene o vira a resultado negativo defendible.

Diagnostico (script nuevo `scripts/diagnose_adaptive_gating.py`, sobre el checkpoint de la corrida de 5000 pasos y 30 casos reales de val):

- Curva de validacion: mean Dice sube monotono hasta epoca 4 (0.586) y **regresa en epoca 5 (0.521)** en las tres regiones. Inestabilidad tardia confirmada (el baseline concat seguia subiendo).
- Comportamiento de la compuerta: produce **pesos identicos en los 30 casos** (t1c=0.332, t2f=0.291, t1n=0.205, t2w=0.172; desviacion entre casos = 0.000). Entropia ~1.353 (max uniforme 1.386): no hay colapso hacia una modalidad.
- Hallazgo clave: **la compuerta "adaptativa" no es adaptativa.** Ha aprendido un peso estatico por modalidad, equivalente a `global_weighted` con un MLP no lineal encima. Causa: su senal de condicionamiento (media espacial global de las modalidades ya z-score-normalizadas) es casi constante entre casos, asi que no tiene informacion por-caso a la que adaptarse; el MLP extra solo aporta no convexidad e inestabilidad. Esto explica por que en los preliminares adaptive_gating (0.588) ~= global_weighted (0.606) ~= concat (0.607).

Implicacion estrategica: estabilizar la optimizacion solo igualaria adaptive_gating a global_weighted. Para que la hipotesis tenga opcion real hay que dar a la compuerta una senal por-caso informativa. Por eso las variantes cubren dos frentes: (a) senal mas rica y (b) estabilizacion.

Palancas anadidas (todas por config, desactivadas por defecto, retrocompatibles):

- Modelo: `fusion_stats` (por defecto `[mean]`; opcion `[mean, std]` anade desviacion tipica por canal, que si varia entre casos = senal por-caso real, atacando la causa raiz) y `fusion_temperature` (softmax mas suave).
- Entrenamiento: `fusion_lr` y `fusion_weight_decay` (grupo de optimizador propio para los parametros de fusion), `fusion_warmup_steps` (la compuerta entra desde identidad) y `fusion_entropy_weight` (regulariza la entropia de la softmax). El log gana la columna `fusion_entropy` para vigilar en vivo; el summary registra todos los knobs.

Cambios de codigo: `AdaptiveGatingFusion` (descriptores mean/std, temperatura, buffer no persistente `warmup_alpha`, `last_entropy`); `build_model` (lee los knobs de modelo); `train_one_run` (grupos de optimizador para fusion, warmup por paso, termino de entropia en la loss, logging y summary). `warmup_alpha` es buffer no persistente, asi que los checkpoints antiguos siguen cargando con strict=True.

Configs preparadas: `configs/model/residual_unet_3d_adaptive_gating_meanstd.yaml`, `..._temp.yaml`, `..._meanstd_temp.yaml`; `configs/training/mac_m4_pro_128_5k_gate_stab.yaml` (fusion_lr 2e-5 + warmup 500 + entropia 0.01). Plan de 4 corridas y criterio de decision en `docs/adaptive-gating-exploration.md`.

Verificacion local:

- 17 tests OK (6 previos + 5 de cache + 6 nuevos de la compuerta en `tests/test_adaptive_gating.py`: dimension de entrada mean vs mean+std, forma de salida, entropia, warmup_alpha=0 = identidad, temperatura, ausencia de warmup_alpha en el state_dict).
- `compileall` correcto.
- El checkpoint antiguo de adaptive_gating carga con el codigo nuevo (buffer no persistente).
- Smoke real (CPU, variante meanstd + config estabilizada): imprime los knobs, entrena, valida, guarda checkpoint; la columna `fusion_entropy` se loguea por paso (~1.36) y el summary registra fusion_lr/warmup/entropy/temperature.
- No se han ejecutado todavia las corridas de 5000 pasos de las variantes: es lo que consume el presupuesto y se lanzara a continuacion.

Impacto en la memoria final: el diagnostico (la compuerta condicionada por descriptores globales no puede ser adaptativa porque su senal es casi constante) es un resultado en si mismo, util tanto si la exploracion vira a positivo (con mean+std) como si se cierra en negativo defendible. Alimenta la discusion de la contribucion en el capitulo de Resultados/Conclusiones.

Pendientes o riesgos abiertos:

- Ejecutar las 4 corridas del plan (R1-R4, ~2 h cada una en M4/L4), evaluar en val y re-diagnosticar (¿la compuerta ya varia entre casos con mean+std? ¿desaparece la regresion?).
- Si alguna supera concat (0.607) con margen, confirmar con multi-semilla e incluir en la corrida final.
- Si ninguna supera concat, cerrar como resultado negativo defendible con la evidencia del diagnostico.

### Resultados de la exploracion (4 variantes, val, 5000 pasos, 1 semilla)

Ejecutadas en local (M4 Pro, MPS) via `scratchpad/run_adaptive_gating_explore.sh` (train + predict + evaluate + re-diagnostico por variante). Fuente: `outputs/evaluation/adaptive_gating_*_val_metrics_summary.json` y `outputs/evaluation/adaptive_gating_explore_diagnosis.txt`.

| Variante | mean Dice | ET | TC | WT | HD95 ET/TC/WT | Curva val | Compuerta |
|---|---|---|---|---|---|---|---|
| R2 mean+std (base) | 0.661 | 0.512 | 0.685 | 0.785 | 13.7/14.5/22.6 | monotona (sin regresion) | estatica |
| R3 mean+std + estab. | 0.653 | 0.519 | 0.677 | 0.763 | 11.6/11.7/12.6 | leve caida ep.5 (-0.019) | estatica |
| R4 mean+std + temp + estab. | 0.650 | 0.511 | 0.673 | 0.765 | 11.6/11.5/11.6 | leve caida ep.5 (-0.031) | estatica |
| R1 orig + estab. | 0.594 | 0.343 | 0.662 | 0.777 | 21.6/21.2/26.8 | cae fuerte ep.5 (-0.125) | estatica |

Referencias previas (val, 5000 pasos): concat 0.607, global_weighted 0.606, adaptive_gating original 0.588, attention_unet 0.655.

Hallazgos:

- Las tres variantes mean+std superan a concat (0.607) y a global_weighted (0.606) con margen (~+0.045 a +0.054), de forma consistente en tres configuraciones de entrenamiento distintas: la mejora la aporta la senal de condicionamiento mean+std, no los knobs de optimizacion. R2 (0.661) iguala/supera al attention_unet (0.655) con 1.2M params (vs 5.9M).
- Estabilizar la compuerta original mean-only (R1) NO la rescata: 0.594, por debajo de concat y con la regresion tardia intacta (de hecho peor, -0.125). Confirma que el problema no era solo de optimizacion.
- La estabilizacion sobre mean+std (R3/R4) no sube el Dice respecto a la base (R2) pero mejora mucho el HD95 (fronteras limpias: ~11.6 mm vs 22.6 mm en WT); R4 (temperatura 2.0) da el HD95 mas equilibrado y la entropia mas alta (1.381).
- MATIZ CRITICO: en las 4 variantes la compuerta sigue siendo casi estatica entre casos (std de pesos ~0.001; domina t2w en los 40 casos). mean+std lleva a un mejor pesado estatico por modalidad, NO a adaptatividad por-caso. La mejora es de rendimiento, no evidencia de que el modelo explote variacion por-caso.

Interpretacion para la memoria: respuesta matizada a la pregunta de investigacion. Una compuerta parametrizada y condicionada por descriptores globales (mean+std) mejora la concatenacion y el pesado estatico simple (~+0.05 mean Dice), pero lo hace via un mejor pesado estatico aprendido (enfasis en t2w), no mediante adaptatividad por-caso. El resultado es positivo en rendimiento pero no valida la "fusion adaptativa" en sentido literal; debe redactarse con esa precision.

Decision: la senal positiva (superar concat con margen, consistente en 3 configs) cumple el primer criterio del plan, pero falta el segundo (multi-semilla). Antes de darlo por bueno en la corrida final hay que confirmar con varias semillas la mejor variante (R2 por Dice y curva estable, o R3 por HD95) frente a concat/global_weighted, para descartar que el margen sea especifico de la semilla 20260526.

Pendiente inmediato: multi-semilla (p. ej. 3 semillas) de la mejor variante mean+std y de concat como control; si el margen se sostiene, la fusion mean+std entra en la corrida final unificada.

## 2026-07-16 - Pilar 3, multi-semilla: el margen de mean+std no es robusto

Actividad realizada: se confirma con multi-semilla el segundo criterio del plan. Se entrenan concat (`residual_unet_3d`) y la mejor variante `mean+std` (`residual_unet_3d_adaptive_gating_meanstd`, config base) con 2 semillas nuevas (20260527, 20260528), reutilizando la semilla A (20260526), para 3 semillas por modelo. Flujo train(`--seed`) + predict + evaluate sobre val, via `scratchpad/run_multiseed_meanstd_vs_concat.sh`; agregacion con `scripts/aggregate_multiseed.py`.

Objetivo metodologico: descartar que el margen de +0.05 de mean+std sobre concat (observado con una sola semilla) fuera especifico de la semilla. Es el criterio que faltaba antes de dar la contribucion por buena.

Resultados (val, mean Dice por semilla y agregado). Fuente: `outputs/evaluation/multiseed_meanstd_vs_concat.csv` y summaries por semilla.

| Modelo | semilla A (20260526) | 20260527 | 20260528 | Agregado (3 semillas) |
|---|---|---|---|---|
| concat | 0.607 | 0.629 | 0.629 | **0.621 +/- 0.025** |
| mean+std | 0.661 | **0.246** | 0.673 | **0.527 +/- 0.198** |

Detalle del colapso (mean+std, semilla 20260527): ET 0.079, TC 0.189, WT 0.471; HD95 ~68/71/50 mm. Entrenamiento efectivamente roto. Las otras dos semillas de mean+std (0.661, 0.673) si superan a concat.

Interpretacion (revierte la lectura preliminar de una sola semilla):

- La fusion adaptativa mean+std NO mejora de forma robusta a la concatenacion. Su media a 3 semillas (0.527) queda por debajo de concat (0.621) y su varianza es ~8x mayor (0.198 vs 0.025).
- El patron es inestabilidad dependiente de semilla: mean+std a veces iguala/supera a concat (2 de 3 semillas ~0.66-0.67) pero colapsa en ~1 de cada 3. Es la manifestacion, a nivel de semilla, de la misma inestabilidad de la compuerta ya vista (regresion de la epoca 5, diagnostico del gate estatico).
- concat es estable y reproducible; la compuerta adaptativa introduce un riesgo de colapso que un metodo defendible no deberia tener.
- El "margen positivo" de la semilla A era ruido de semilla. Esto valida por que el tutor exigio multi-semilla y por que no se acepta un resultado de una sola semilla.

Conclusion metodologica: con la evidencia acumulada (compuerta estatica en el diagnostico + inestabilidad dependiente de semilla en multi-semilla + estabilizacion que no rescata a la variante original), la hipotesis de que la fusion adaptativa mejora la concatenacion NO se sostiene de forma robusta en este montaje. Es la base de un **resultado negativo defendible**, dentro del criterio acordado con el tutor de agotar vias (se probaron: estabilizacion via warmup/lr/entropia, condicionamiento mas rico mean+std, temperatura, y multi-semilla).

Estado del presupuesto (2-3 dias): consumido ~1 dia (exploracion de 4 variantes + multi-semilla). Queda margen para UNA ultima via si se quiere ser exhaustivo antes de cerrar en negativo: multi-semilla de la variante estabilizada (mean+std + `gate_stab`), por si la estabilizacion reduce la varianza entre semillas. Valor esperado bajo (la compuerta sigue siendo estatica), pero es la unica via no agotada.

Artefactos: `outputs/evaluation/multiseed_*_val_metrics_summary.json`, `outputs/evaluation/multiseed_meanstd_vs_concat.csv`, `scratchpad/run_multiseed_meanstd_vs_concat.sh`, `scripts/aggregate_multiseed.py`.

Pendiente / decision abierta: cerrar el pilar 3 como resultado negativo defendible, o gastar la ultima via (multi-semilla de la variante estabilizada) antes de cerrar. Decision del alumno.

## 2026-07-17 - Pilar 3 CERRADO: resultado negativo defendible (ultima via agotada)

Actividad realizada: se ejecuta la ultima via acordada antes de cerrar en negativo: multi-semilla (3 semillas) de la variante ESTABILIZADA `mean+std` + `gate_stab`, por si la estabilizacion evitaba el colapso por semilla de la variante base. 2 semillas nuevas (20260527, 20260528) reutilizando la semilla A (R3, 0.653). Via `scratchpad/run_multiseed_meanstd_stab.sh`.

Resultado final del pilar 3 (val, 3 semillas por modelo). Fuente: `outputs/evaluation/multiseed_pillar3_final.csv`.

| Modelo | mean Dice (3 semillas) | semilla A | 20260527 | 20260528 |
|---|---|---|---|---|
| concat | 0.621 +/- 0.025 | 0.607 | 0.629 | 0.629 |
| mean+std (base) | 0.527 +/- 0.198 | 0.661 | 0.246 | 0.673 |
| mean+std + estabilizacion | 0.521 +/- 0.199 | 0.653 | 0.246 | 0.670 |

Hallazgo decisivo: la estabilizacion NO evita el colapso. La semilla 20260527 se hunde (ET ~0.076, mean ~0.246) tanto en la variante base como en la estabilizada; es la MISMA semilla la que colapsa en ambas. Es un fallo del mecanismo de compuerta ante la inicializacion/orden de augmentation que warmup + lr bajo + entropia no corrigen.

Veredicto (pilar 3 cerrado): resultado NEGATIVO DEFENDIBLE. La fusion adaptativa no mejora de forma robusta a la concatenacion en este montaje:

- concat es estable y reproducible (0.621 +/- 0.025).
- La fusion adaptativa (mean+std, con o sin estabilizacion) queda por debajo de media (0.52-0.53) y con varianza ~8x mayor, por colapsar en 1 de cada 3 semillas.
- Evidencia mecanicista coherente: el diagnostico mostro que la compuerta es estatica (no adaptativa de verdad); el "positivo" de una sola semilla era ruido; la estabilizacion no rescata la robustez.

Vias agotadas dentro del alcance y presupuesto (2-3 dias, consumido ~1.5 dias): (1) estabilizacion via warmup/lr/entropia; (2) condicionamiento mas rico mean+std; (3) temperatura; (4) multi-semilla de la variante base; (5) multi-semilla de la variante estabilizada. Cumple el criterio del tutor de no aceptar el negativo hasta agotar vias.

Impacto en la memoria final: la respuesta a la pregunta de investigacion es negativa y esta respaldada por evidencia solida (diagnostico + multi-semilla + ablacion de estabilizacion). Es un resultado valido y publicable: una fusion adaptativa por compuerta condicionada por descriptores globales no supera a la concatenacion estandar en BraTS-GLI y ademas introduce inestabilidad de entrenamiento dependiente de semilla. La concatenacion se confirma como baseline de fusion robusto. Se redactara en Resultados/Conclusiones con esta precision, y la contribucion se reformula de "mejora" a "estudio critico de estrategias de fusion multimodal".

Estado de pilares: los tres resueltos. Pilar 1 (nnU-Net, referencia 0.835) y pilar 2 (Swin-UNETR, mejor modelo propio 0.715) cerrados en positivo; pilar 3 (ablacion de fusion) cerrado en negativo defendible. El objetivo defendible del TFM queda cubierto.

Pendientes: corrida final unificada (mas pasos a convergencia + multi-semilla) de los modelos que iran a la tabla final, y evaluacion sobre el split `test` reservado con la configuracion congelada; luego redaccion de los capitulos con los numeros finales.

## 2026-07-17 - Track A: scheduler cosine y sonda de convergencia

Actividad realizada: se prepara la corrida final (alcance completo, 3 semillas, A100 para Swin, decidido por el alumno). Se anade un scheduler de LR cosine con warmup a la pipeline y se ejecuta una sonda de convergencia para fijar el presupuesto de pasos con evidencia en vez de a ojo.

Cambios de codigo: `train_one_run` gana `lr_scheduler` (none|cosine), `lr_warmup_steps`, `lr_min_factor`. Cosine: warmup lineal y luego decaimiento coseno hasta `lr_min_factor`*base sobre el total de pasos, por grupo de parametros (respeta un `fusion_lr` distinto). Por defecto `none` (retrocompatible). Verificado con smoke (warmup 5 pasos -> pico -> cosine) y 17 tests OK. Config `configs/training/mac_m4_pro_128_final.yaml` (cosine, warmup 1000, patch 128).

Sonda: concat a 25000 pasos con cosine, M4 Pro MPS, validando por epoca (8 batches). Resultado (`outputs/train/probe_concat_25k`):

| epoca | paso | mean_dice (val 8b) |
|---|---|---|
| 5 | 5675 | 0.625 |
| 9 | 10215 | 0.651 |
| 11 | 12485 | 0.686 |
| 15 | 17025 | 0.685 |
| 19 | 21565 | 0.691 (best) |
| 22 | 25000 | 0.688 |

Conclusion: la curva mesetea en la epoca ~11 (paso ~12500). De la epoca 11 a la 19 solo sube +0.005 (ruido de la validacion de 8 batches). Convergido, concat pasa de 0.607 (5000 pasos) a ~0.69: la ganancia real (~+0.08) esta sobre todo en TC/WT (que saturan ~0.87) y algo en ET (~0.32, ruidoso). Confirma que 5000 pasos infra-entrenaban.

Decision de presupuesto: corrida final a **15000 pasos** (~13 epocas) con cosine LR sobre 15000 y warmup 1000. Captura toda la ganancia (la meseta) y recorta ~40% frente a 25000. best.pt se selecciona por validacion como siempre.

Estimacion de coste de la matriz completa a 15000 pasos:
- Modelos residuales (~1.2 s/paso en M4): ~5 h/run. Ablacion de fusion (concat, global_weighted, adaptive_gating, adaptive_gating_meanstd) x 3 semillas = 12 runs ~= 3 dias en local (tandas nocturnas).
- Attention U-Net es lento en MPS (~4.75 s/paso -> ~20 h/run): se movera a cloud junto con Swin.
- Swin-UNETR x 3 semillas: A100 (a convergencia).
- nnU-Net: se reutiliza el existente como referencia (1 corrida); multi-fold queda fuera para acotar coste de A100.

Pendiente: aprobar el reparto local/cloud y lanzar; luego predict + evaluate sobre `test` (no val) y agregacion multi-semilla para las tablas finales.
