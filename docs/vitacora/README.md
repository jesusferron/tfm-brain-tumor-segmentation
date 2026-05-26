# Bitacora metodologica del TFM

Ultima actualizacion: 2026-05-26

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
