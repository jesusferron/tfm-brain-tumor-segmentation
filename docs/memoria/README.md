# Memoria del TFM - borrador incremental

Ultima actualizacion: 2026-05-26

Titulo de trabajo: **Segmentacion de tumores cerebrales en resonancia magnetica multimodal mediante arquitecturas Transformer-UNet hibridas**.

Este documento centraliza la memoria del TFM en construccion. No sustituye a la plantilla final de la universidad, pero organiza el contenido tecnico que ya esta decidido o parcialmente validado en el repositorio. La prioridad actual es consolidar el capitulo de metodologia, las tablas sobre el repositorio/dataset y la descripcion del tipo de imagen, porque son elementos que deben quedar claros antes de entrenar modelos.

## Evaluacion de la peticion del tutor

La peticion del tutor encaja principalmente en el capitulo de **Materiales y metodos** de la memoria. Conviene tratarla como parte metodologica y no como anexo aislado, porque justifica la trazabilidad del experimento:

| Elemento solicitado | Donde debe aparecer en la memoria | Estado actual |
| --- | --- | --- |
| Documento de metodologia | Capitulo de Materiales y metodos | Borrador definido en este documento y trazado en `docs/vitacora/README.md` |
| Tablas de repositorio | Materiales y metodos, reproducibilidad y anexos | Incluidas tablas del dataset BraTS/Synapse, correspondencia local y estructura del repositorio |
| Tipo de imagen | Materiales y metodos, descripcion del dataset y preprocesamiento | Incluida descripcion de NIfTI 3D multimodal, modalidades MRI y mascaras |
| Restricciones de publicacion | Aspectos eticos, legales y reproducibilidad | Documentado que no se redistribuyen NIfTI originales |

La decision metodologica importante es separar tres conceptos:

- **Repositorio de datos**: origen Synapse/BraTS y colecciones disponibles.
- **Repositorio del proyecto**: codigo, configuraciones, documentacion y artefactos reproducibles versionados.
- **Imagen medica usada**: volumen MRI 3D en formato NIfTI comprimido, con cuatro modalidades por caso y mascara cuando esta disponible.

## Resumen del trabajo

El TFM estudia la segmentacion 3D de gliomas en resonancia magnetica multimodal. El alcance experimental se limita a **BraTS-GLI 2024**, evitando mezclar tareas clinicas distintas de otros subconjuntos BraTS. La pregunta de investigacion aprobada es:

> Puede una estrategia de fusion adaptativa de modalidades MRI mejorar la segmentacion 3D de gliomas en BraTS-GLI frente a una fusion por concatenacion estandar, manteniendo un coste computacional asumible y con mejoras consistentes en ET, TC y WT?

La contribucion principal se acota a una estrategia de **fusion adaptativa de modalidades MRI**, comparada contra:

- Concatenacion estandar de modalidades.
- Fusion ponderada como comparador controlado.
- Baselines de segmentacion 3D, incluyendo nnU-Net como baseline fuerte externo reproducible.

## Objetivos

### Objetivo general

Disenar, implementar y evaluar una metodologia reproducible para segmentacion automatica 3D de gliomas en MRI multimodal, comparando estrategias de fusion de modalidades sobre BraTS-GLI 2024.

### Objetivos especificos

1. Analizar la estructura del dataset BraTS 2024 y justificar la eleccion de BraTS-GLI como nucleo experimental.
2. Construir un inventario reproducible del dataset local y verificar modalidades, mascaras, formatos y restricciones de publicacion.
3. Definir un protocolo experimental con splits internos reproducibles, hold-out final y metricas de evaluacion fijadas antes del entrenamiento.
4. Implementar una pipeline MONAI/PyTorch para entrenamiento por patches 3D y evaluacion de modelos.
5. Usar nnU-Net como baseline fuerte reproducible, documentando conversion, versiones, configuracion y resultados.
6. Comparar concatenacion, fusion ponderada y fusion adaptativa de modalidades MRI.
7. Reportar Dice y HD95 para ET, TC y WT, junto con coste computacional y limitaciones.

## Materiales y metodos

### Diseno metodologico

La metodologia se plantea por fases para reducir el riesgo de entrenamientos costosos sobre datos no verificados:

| Fase | Objetivo | Evidencia en repositorio |
| --- | --- | --- |
| 1. Inventario del dataset | Identificar colecciones, casos, modalidades y restricciones | `data/brats_2024_dataset_context.md`, `data/brats_2024_dataset_properties.json`, `data/brats_2024_file_inventory.csv` |
| 2. Correspondencia local | Confirmar que los paquetes descargados coinciden con los datos esperados | `data/brats_2024_local_dataset_match.csv` |
| 3. Preprocesamiento y controles | Verificar presencia de modalidades, mascaras, shape y affine | Pendiente de ampliar al dataset completo |
| 4. Smoke tests | Validar carga y conversion minima antes de entrenar | `scripts/nnunet/check_brats_gli_nnunet_smoke.py`, `scripts/nnunet/verify_brats_gli_nnunet_smoke.py` |
| 5. Splits reproducibles | Crear train/validation/test interno sobre casos con mascara | Pendiente |
| 6. Entrenamiento | Entrenar baseline sencillo, baseline fuerte y Transformer-UNet | Pendiente |
| 7. Ablacion de fusion | Comparar concatenacion, fusion ponderada y fusion adaptativa | Pendiente |
| 8. Analisis final | Comparar metricas, coste computacional y limitaciones | Pendiente |

Esta organizacion permite que cada resultado experimental se pueda rastrear hasta una configuracion, un script y un conjunto de datos claramente identificado.

### Dataset

El dataset de referencia es **BraTS 2024 Challenge**, disponible mediante Synapse. La memoria debe citar la fuente oficial de BraTS y el identificador del proyecto Synapse `syn53708249`. El acceso requiere usuario registrado, aceptacion de terminos post-challenge y cumplimiento de licencia **CC-BY-NC 4.0**.

Aunque BraTS 2024 agrupa varias colecciones, el TFM usa solo **BraTS-GLI** como nucleo experimental. Los demas subconjuntos se pueden mencionar como contexto, limitaciones o trabajo futuro, pero no se mezclan en el experimento principal por diferencias de tarea clinica, modalidades, etiquetas y protocolo.

#### Tabla de colecciones BraTS 2024

| Coleccion | Synapse ID | Ficheros listados | Tamano listado | Uso en este TFM |
| --- | --- | ---: | ---: | --- |
| BraTS-GLI | `syn59059776` | 5 | 44.80 GiB | Dataset principal |
| BraTS-GoAT | `syn68156890` | 2 | 16.46 KiB | Fuera del nucleo experimental |
| BraTS-MEN-RT | `syn59059779` | 5 | 12.08 GiB | Contexto/trabajo futuro |
| BraTS-MET | `syn68156869` | 2 | 2.11 KiB | Contexto/trabajo futuro |
| BraTS-PED | `syn68156871` | 2 | 1.85 KiB | Contexto/trabajo futuro |
| BraTS-Path | `syn59761935` | 2 | 867 B | Contexto/trabajo futuro |
| BraTS-SSA | `syn59059780` | 2 | 867 B | Contexto/trabajo futuro |
| MLCube Resources | `syn61956466` | 4 | 117.08 MiB | Recursos auxiliares |

Fuente reproducible en el repositorio: `data/brats_2024_dataset_context.md` y `data/brats_2024_dataset_properties.json`.

#### Tabla de correspondencia local

La siguiente tabla resume los paquetes de imagen encontrados localmente y su correspondencia con los ficheros BraTS/Synapse. El directorio local usado para el inventario fue `/Volumes/External M2/Datos/TFM-datasets`.

| Paquete Synapse | Carpeta local | Casos | NIfTI | Modalidades / etiquetas | Estado |
| --- | --- | ---: | ---: | --- | --- |
| BraTS2024-BraTS-GLI-TrainingData.zip | `training_data1_v2` | 1350 | 6750 | `seg`, `t1c`, `t1n`, `t2f`, `t2w` | Completo |
| BraTS2024-BraTS-GLI-AdditionalTrainingData.zip | `training_data_additional` | 271 | 1355 | `seg`, `t1c`, `t1n`, `t2f`, `t2w` | Completo |
| BraTS2024-BraTS-GLI-ValidationData.zip | `validation_data` | 188 | 752 | `t1c`, `t1n`, `t2f`, `t2w` | Completo, sin mascara local |
| BraTS2024-MEN-RT-TrainingData.zip | `BraTS-MEN-RT-Train-v2` | 500 | 1000 | `gtv`, `t1c` | Fuera del nucleo |
| BraTS2024-MEN-RT-ValidationData.zip | `BraTS-MEN-RT-Val-v1` | 70 | 70 | `t1c` | Fuera del nucleo |

Para el experimento principal se consideran inicialmente los **1621 casos con mascara** de BraTS-GLI, combinando entrenamiento principal y entrenamiento adicional. La validacion publica de BraTS-GLI contiene imagenes sin mascara local, por lo que no debe usarse como test medible salvo que exista evaluador oficial o etiquetas accesibles bajo las condiciones del reto.

### Tipo de imagen

Las imagenes usadas son volumenes de **resonancia magnetica cerebral 3D multimodal** en formato **NIfTI comprimido (`.nii.gz`)**. Cada caso BraTS-GLI de entrenamiento contiene cuatro modalidades MRI y una mascara de segmentacion.

| Elemento | Tipo | Sufijo local | Papel metodologico |
| --- | --- | --- | --- |
| T1 nativo | MRI 3D | `t1n` | Contraste anatomico estructural sin contraste |
| T1 con contraste | MRI 3D | `t1c` | Realce tumoral y region enhancing tumor |
| T2 | MRI 3D | `t2w` | Senal de tejido y componentes tumorales |
| FLAIR / T2-FLAIR | MRI 3D | `t2f` | Edema/infiltracion y tumor completo |
| Mascara | Segmentacion 3D | `seg` | Etiqueta supervisada para entrenamiento/evaluacion |

Los cuatro volumenes de un caso se tratan como canales de entrada de una misma muestra 3D. En la pipeline propia MONAI/PyTorch se podran cargar como lista de modalidades y concatenarse en el eje de canal. Para el smoke test de nnU-Net via MONAI fue necesario generar un NIfTI 4D temporal con las cuatro modalidades apiladas, porque la interfaz probada de `nnUNetV2Runner` esperaba un unico campo `image` por caso.

Aspectos que deben quedar documentados en la memoria final:

- Formato de fichero: `.nii.gz`.
- Naturaleza: MRI cerebral 3D multimodal.
- Modalidades por caso: `t1n`, `t1c`, `t2w`, `t2f`.
- Etiqueta supervisada: `seg` en entrenamiento y entrenamiento adicional.
- Resolucion y espaciado: el smoke test de nnU-Net detecto `1.0 x 1.0 x 1.0` en los 3 casos verificados; se debe ampliar la verificacion al dataset completo.
- Regiones de evaluacion: ET, TC y WT.
- Normalizacion prevista: z-score por modalidad en voxeles no cero.

### Preprocesamiento previsto

El preprocesamiento minimo obligatorio antes de entrenar incluye:

1. Verificar presencia de las cuatro modalidades por caso.
2. Verificar presencia de mascara `seg` en los casos usados para entrenamiento y evaluacion interna.
3. Comprobar compatibilidad de `shape` y `affine` entre modalidades y mascara.
4. Aplicar normalizacion z-score por modalidad en voxeles no cero.
5. Generar estadisticas descriptivas por region tumoral.
6. Registrar casos descartados o atipicos, si aparecen.

La implementacion completa esta pendiente. El smoke test ya valida que, en un subconjunto minimo de 3 casos, las modalidades existen, tienen shapes compatibles y pueden apilarse en un volumen multicanal.

### Protocolo experimental

El protocolo se fijara antes del entrenamiento completo. El minimo metodologico acordado es:

| Componente | Decision |
| --- | --- |
| Dataset nuclear | BraTS-GLI 2024 |
| Casos supervisados iniciales | 1621 casos con mascara |
| Split | Interno, estratificado y reproducible |
| Hold-out | Final no tocado hasta evaluacion final |
| Semillas | Versionadas junto con los splits |
| Metricas | Dice y HD95 |
| Regiones | ET, TC y WT |
| Entrenamiento | Patches 3D, configuraciones versionadas |
| Entorno principal | Colab Pro con GPU CUDA para entrenamientos completos |
| Entorno auxiliar | Mac M4 Pro para inventario, smoke tests y analisis local |

Pendiente operativo: definir porcentajes exactos de train/validation/test y variables de estratificacion. Hasta que esto este cerrado, no debe considerarse final ningun resultado de entrenamiento completo.

### Modelos y comparadores

Los modelos tienen roles experimentales distintos:

| Modelo | Rol en el TFM | Estado |
| --- | --- | --- |
| 3D U-Net residual | Baseline convolucional controlado | Pendiente |
| Attention U-Net | Variante intermedia con atencion espacial | Pendiente |
| nnU-Net v2 | Baseline fuerte externo reproducible | Smoke test de conversion e integridad realizado |
| Swin-UNETR | Modelo Transformer-UNet alineado con el titulo | Pendiente |
| TransBTS | Arquitectura hibrida especifica para tumores cerebrales | Pendiente |

La comparacion principal no debe basarse solo en el numero de modelos, sino en la pregunta de investigacion. Por tanto, la ablacion de fusion de modalidades es central:

| Estrategia de fusion | Funcion experimental |
| --- | --- |
| Concatenacion estandar | Baseline de fusion habitual |
| Fusion ponderada | Comparador controlado para estudiar pesos por modalidad |
| Fusion adaptativa | Contribucion principal del TFM |

### nnU-Net como baseline fuerte

nnU-Net se tratara como baseline externo reproducible. MONAI puede actuar como capa de orquestacion mediante `monai.apps.nnunet.nnUNetV2Runner`, pero nnU-Net conserva su propia estructura de datos, planificacion, preprocesamiento, folds, checkpoints y resultados.

Smoke test realizado:

| Elemento | Resultado |
| --- | --- |
| Python | 3.13.2 |
| PyTorch | 2.12.0 |
| MONAI | 1.5.2 |
| nnU-Net v2 | 2.7.0 |
| Casos de entrenamiento convertidos | 3 |
| Canales de entrada | 4 (`t1n`, `t1c`, `t2w`, `t2f`) |
| Ficheros `imagesTr` generados | 12 |
| Ficheros `labelsTr` generados | 3 |
| Ficheros `imagesTs` generados | 4 |
| Integridad nnU-Net | Verificacion completada sin error |
| Fingerprint | Extraido para 3 casos |

Artefactos relacionados:

- `configs/nnunet/brats_gli_2024_smoke.yaml`
- `configs/nnunet/brats_gli_2024_monai_input.yaml`
- `scripts/nnunet/check_brats_gli_nnunet_smoke.py`
- `scripts/nnunet/verify_brats_gli_nnunet_smoke.py`
- `outputs/nnunet_smoke/brats_gli_2024_smoke_datalist.json`
- `outputs/nnunet_smoke/input.yaml`

Este resultado no mide rendimiento. Su valor metodologico es demostrar que el repositorio ya puede preparar una entrada minima BraTS-GLI compatible con MONAI/nnU-Net y que la conversion producida pasa una verificacion interna de nnU-Net.

## Repositorio del proyecto

El repositorio es parte de la entrega del TFM y debe permitir auditar codigo, configuraciones, documentacion y resultados agregados sin redistribuir datos medicos originales.

### Tabla de estructura del repositorio

| Ruta | Tipo de contenido | Funcion en la memoria/reproducibilidad |
| --- | --- | --- |
| `README.md` | Entrada general del proyecto | Pendiente de ampliar con instrucciones generales |
| `data/` | Metadatos, inventarios y correspondencia local | Evidencia del analisis del dataset y acceso a datos |
| `docs/specs/` | Propuesta tecnica del TFM | Trazabilidad del alcance inicial |
| `docs/pre-design/` | Decisiones previas y respuestas del tutor | Justificacion de decisiones metodologicas |
| `docs/vitacora/` | Bitacora metodologica | Registro incremental de decisiones y pruebas |
| `docs/memoria/` | Borrador de memoria | Documento acumulativo para la redaccion final |
| `configs/` | Configuraciones YAML | Parametrizacion reproducible de pruebas y experimentos |
| `scripts/` | Scripts ejecutables | Automatizacion de inventario, conversion, verificacion y futuros entrenamientos |
| `requirements/` | Dependencias versionadas | Reproduccion de entornos concretos |
| `outputs/` | Artefactos pequenos versionables y salidas locales | Solo se versionan salidas ligeras; datos pesados y NIfTI quedan ignorados |
| `.gitignore` | Reglas de exclusion | Evita versionar NIfTI originales, preprocesados, checkpoints y `.venv` |

### Tabla de artefactos actuales

| Artefacto | Descripcion | Estado |
| --- | --- | --- |
| `data/brats_2024_dataset_context.md` | Resumen legible de fuente, acceso, colecciones y citas BraTS | Versionado |
| `data/brats_2024_dataset_properties.json` | Metadatos estructurados del dataset y match local | Versionado |
| `data/brats_2024_file_inventory.csv` | Inventario de ficheros publicados en Synapse | Versionado |
| `data/brats_2024_local_dataset_match.csv` | Correspondencia entre ficheros Synapse y descarga local | Versionado |
| `docs/pre-design/decisiones-iniciales.md` | Decisiones cerradas del diseno metodologico | Versionado |
| `docs/pre-design/respuestas-tutor-2026-05-18.md` | Respuestas del tutor y decisiones derivadas | Versionado |
| `docs/vitacora/README.md` | Bitacora metodologica del TFM | Versionado |
| `configs/nnunet/*.yaml` | Configuracion del smoke test nnU-Net/MONAI | Versionado |
| `requirements/nnunet-smoke.txt` | Dependencias minimas del smoke test | Versionado |
| `scripts/nnunet/*.py` | Preparacion y verificacion de smoke test nnU-Net | Versionado |
| `outputs/nnunet_smoke/*.json` y `*.yaml` | Datalist e input reproducibles del smoke test | Versionado |
| `outputs/nnunet_smoke/source/` | NIfTI temporales generados para smoke test | Ignorado por Git |
| `outputs/nnunet_smoke/nnUNet_*` | Salidas internas de nnU-Net | Ignorado por Git |

## Reproducibilidad y control de versiones

La reproducibilidad objetivo es practica y auditada, no bit-a-bit. Cada experimento debe registrar:

- Commit del repositorio.
- Configuracion YAML/JSON usada.
- Split y semilla.
- Versiones de Python, PyTorch, MONAI, nnU-Net y CUDA/cuDNN cuando aplique.
- Hardware usado.
- Logs, metricas agregadas y checkpoints finales.
- Comandos de ejecucion.

El repositorio no debe incluir:

- NIfTI originales del dataset.
- NIfTI generados pesados.
- Checkpoints grandes.
- Directorios `nnUNet_raw`, `nnUNet_preprocessed` y `nnUNet_results`.
- Entornos virtuales.

Estas exclusiones estan reflejadas en `.gitignore`.

## Aspectos legales, licencia y citacion

BraTS 2024 se accede mediante Synapse y esta documentado en el repositorio con identificador `syn53708249`. El uso indicado en los metadatos locales es **CC-BY-NC 4.0**, por lo que el trabajo debe mantenerse en un contexto no comercial y citar los manuscritos requeridos por BraTS.

La memoria debe incluir como minimo:

- Fuente de datos: Brain Tumor Segmentation (BraTS) Challenge project through Synapse ID `syn53708249`.
- Subconjunto usado: BraTS-GLI 2024.
- Condiciones de acceso: usuario Synapse registrado y aceptacion de terminos.
- Restriccion de publicacion: no redistribuir los datos NIfTI originales.
- Referencias obligatorias: manuscrito BraTS-GLI 2024 y, si aplica, MedPerf/MLCube segun el uso final.

## Pendientes inmediatos

1. Definir porcentajes exactos de train/validation/test.
2. Definir variables de estratificacion del split interno.
3. Implementar inventario automatico completo de shapes, affines, espaciado y valores de etiquetas.
4. Confirmar la correspondencia exacta entre etiquetas crudas de `seg` y regiones ET, TC, WT para BraTS-GLI 2024.
5. Crear configs de entrenamiento para baseline 3D U-Net y pipeline MONAI.
6. Decidir si la conversion final de nnU-Net usara NIfTI 4D intermedio via MONAI o conversion directa al formato nnU-Net.
7. Actualizar este documento cuando existan splits versionados y primeros resultados.

## Relacion con otros documentos

| Documento | Uso |
| --- | --- |
| `docs/specs/propuesta-2-segmentacion-tumores-cerebrales.md` | Propuesta y alcance inicial del TFM |
| `docs/pre-design/decisiones-iniciales.md` | Decisiones cerradas tras revision |
| `docs/pre-design/respuestas-tutor-2026-05-18.md` | Trazabilidad de feedback del tutor |
| `docs/vitacora/README.md` | Registro cronologico de metodologia y pruebas |
| `data/brats_2024_dataset_context.md` | Contexto dataset, acceso, colecciones y citas |
| `data/brats_2024_dataset_properties.json` | Fuente estructurada para tablas de memoria |

