# Glosario del Proyecto

Glosario de términos clave para el TFM de segmentación de tumores cerebrales en resonancia magnética multimodal usando BraTS 2024.

## Dataset, Acceso y Organización

| Término | Definición en este proyecto |
| --- | --- |
| BraTS | Acrónimo de Brain Tumor Segmentation. Familia de challenges y datasets de referencia para segmentación de tumores cerebrales. |
| BraTS 2024 Challenge | Dataset principal del proyecto. Se distribuye mediante Synapse y agrupa varias colecciones de segmentación y recursos auxiliares. |
| BraTS-GLI | Colección de BraTS 2024 centrada en gliomas. Es la colección principal para el objetivo del TFM: segmentación multimodal de tumores cerebrales. |
| BraTS-MEN-RT | Colección de BraTS 2024 para meningiomas en contexto de radioterapia. En el dataset local contiene volúmenes `t1c` y máscaras `gtv`. |
| BraTS-MET | Colección relacionada con metástasis cerebrales. En el inventario local aparece como colección pequeña con ficheros auxiliares. |
| BraTS-PED | Colección pediátrica de BraTS. En el inventario local aparece como colección pequeña con ficheros auxiliares. |
| BraTS-Path | Colección de BraTS orientada a datos de patología. En el inventario local aparece como colección pequeña con ficheros auxiliares. |
| BraTS-SSA | Colección asociada a población de África subsahariana. Es relevante para discutir generalización cross-continental. |
| BraTS-GoAT | Colección relacionada de BraTS 2024 incluida en el inventario, con ficheros auxiliares pequeños. |
| Synapse | Plataforma usada para publicar, controlar acceso y descargar los datos de BraTS 2024. |
| Synapse ID | Identificador estable de entidades en Synapse, por ejemplo `syn53708249` para el proyecto BraTS 2024. |
| Data folder | Carpeta de Synapse que contiene los ficheros descargables del dataset. En este proyecto corresponde a `syn64952546`. |
| Request Access | Flujo de Synapse necesario para solicitar acceso a datos restringidos y aceptar los términos de uso. |
| Post-challenge terms and conditions | Condiciones que deben aceptarse para descargar datos de BraTS 2024 tras el challenge. |
| CC-BY-NC 4.0 | Licencia del dataset. Permite uso con atribución y restringe el uso comercial. |
| MLCube | Formato de empaquetado reproducible de modelos o pipelines de ML. BraTS 2024 incluye recursos MLCube para evaluación y compatibilidad. |
| MedPerf | Plataforma de benchmarking federado mencionada en los requisitos de citación cuando se usan datasets o clientes MedPerf. |
| Inventario de ficheros | Registro tabular de ficheros publicados en Synapse, sus colecciones, IDs, versiones y fechas. En el repo está en `data/brats_2024_file_inventory.csv`. |
| Emparejamiento local | Comprobación de qué ficheros o carpetas descargadas localmente corresponden a los ficheros de Synapse. En el repo está en `data/brats_2024_local_dataset_match.csv`. |
| MD5 | Huella criptográfica usada para verificar que un fichero local coincide exactamente con el fichero esperado. |
| `matched_extracted` | Estado usado en el inventario local cuando un ZIP de Synapse se corresponde con una carpeta ya extraída. |
| `md5_exact` | Método de emparejamiento en el que nombre y contenido local coinciden con el fichero de Synapse mediante MD5. |
| Caso | Unidad de muestra del dataset, normalmente un paciente o estudio, con varias modalidades MRI y, en entrenamiento, una máscara de referencia. |
| Training data | Subconjunto usado para ajustar los modelos. En BraTS-GLI local incluye máscaras `seg`. |
| Additional training data | Subconjunto adicional de entrenamiento de BraTS-GLI con la misma estructura de modalidades esperada que el entrenamiento principal. |
| Validation data | Subconjunto usado para validación o inferencia. En BraTS-GLI local incluye modalidades MRI pero no necesariamente máscaras públicas. |

## Imagen Médica y Modalidades

| Término | Definición en este proyecto |
| --- | --- |
| MRI / RM | Resonancia magnética. Técnica de imagen médica usada como entrada para segmentar tumores cerebrales. |
| MRI multimodal | Uso conjunto de varias secuencias de resonancia magnética como canales de entrada del modelo. |
| Volumen 3D | Imagen médica representada como una matriz tridimensional de vóxeles. |
| Vóxel | Unidad mínima de un volumen 3D, equivalente tridimensional del píxel. |
| Resolución isotrópica | Resolución en la que el tamaño físico del vóxel es igual en los tres ejes. En la propuesta se menciona 1 mm isotrópico. |
| NIfTI | Formato habitual para neuroimagen. En el dataset local aparece comprimido como `.nii.gz`. |
| `.nii.gz` | Fichero NIfTI comprimido con gzip. Es el formato de las modalidades y máscaras volumétricas del dataset local. |
| Modalidad | Secuencia MRI concreta asociada a un caso, por ejemplo `t1n`, `t1c`, `t2w` o `t2f`. |
| `t1n` | T1 nativo o precontraste. Aporta información anatómica estructural sin agente de contraste. |
| `t1c` / T1ce | T1 con contraste. Resalta zonas con captación de contraste y es importante para detectar tumor realzante. |
| `t2w` | Imagen ponderada en T2. Ayuda a visualizar alteraciones tisulares y edema. |
| `t2f` / FLAIR | Secuencia T2-FLAIR. Atenúa líquido cefalorraquídeo y ayuda a delimitar edema y regiones infiltrativas. |
| Canal de entrada | Cada modalidad MRI introducida al modelo como una dimensión o canal distinto. |
| Registro espacial | Alineación de varias modalidades para que cada vóxel represente la misma posición anatómica. |
| Normalización de intensidad | Transformación de intensidades MRI para reducir variaciones entre pacientes, equipos o centros. |
| Preprocesamiento | Conjunto de pasos previos al entrenamiento, como carga NIfTI, normalización, recorte, remuestreo o verificación de modalidades. |

## Tumores, Regiones y Etiquetas

| Término | Definición en este proyecto |
| --- | --- |
| Glioma | Tumor cerebral de origen glial. Es el foco principal de la propuesta con BraTS-GLI. |
| Meningioma | Tumor originado en las meninges. Aparece en la colección BraTS-MEN-RT, especialmente vinculada a radioterapia. |
| Metástasis cerebral | Lesión tumoral en cerebro derivada de un cáncer primario en otra localización. Aparece como colección BraTS-MET. |
| Neuro-Oncología | Área clínica centrada en tumores del sistema nervioso. Es el marco clínico del TFM. |
| Neurorradiólogo | Especialista que interpreta neuroimagen y puede participar en anotaciones o validación de segmentaciones. |
| Segmentación | Tarea de asignar una clase o región anatómica/tumoral a cada vóxel de una imagen. |
| Segmentación semántica 3D | Segmentación vóxel a vóxel de un volumen médico completo. Es el tipo de tarea planteada para BraTS. |
| Máscara de segmentación | Volumen de etiquetas que indica qué región tumoral corresponde a cada vóxel. En BraTS-GLI local aparece como modalidad `seg`. |
| Ground truth | Segmentación de referencia usada para entrenar o evaluar el modelo, normalmente basada en anotación experta. |
| Etiqueta | Valor discreto de una máscara que representa una clase tumoral o fondo. |
| Fondo | Vóxeles que no pertenecen a ninguna región tumoral objetivo. |
| ET | Enhancing Tumor o tumor realzante. Región que capta contraste, especialmente visible en T1 con contraste. |
| TC | Tumor Core o núcleo tumoral. Región central del tumor, incluyendo tumor realzante y componentes centrales no realzantes o necróticos según la definición del challenge. |
| WT | Whole Tumor o tumor completo. Incluye todas las regiones tumorales visibles objetivo, normalmente núcleo tumoral más edema/infiltración. |
| GTV | Gross Tumor Volume. Volumen tumoral macroscópico usado en radioterapia; aparece como máscara `gtv` en BraTS-MEN-RT. |
| Edema | Acumulación de líquido o alteración peritumoral visible en MRI, especialmente relevante para WT. |
| Necrosis | Tejido tumoral no viable que puede formar parte del núcleo tumoral. |
| Región de interés / ROI | Zona del volumen donde se concentra el análisis, entrenamiento o evaluación. |
| Bordes difusos | Límites tumorales poco nítidos, una dificultad clínica y técnica señalada en la propuesta. |
| Heterogeneidad interpaciente | Variabilidad de forma, tamaño, localización e intensidad del tumor entre pacientes. |

## Modelos y Arquitecturas

| Término | Definición en este proyecto |
| --- | --- |
| Deep learning | Familia de métodos de aprendizaje automático basados en redes neuronales profundas. |
| CNN | Red neuronal convolucional. Captura patrones locales mediante convoluciones y es la base de U-Net y 3D U-Net. |
| Transformer | Arquitectura basada en mecanismos de atención que modela relaciones de largo alcance. |
| Self-attention | Mecanismo que permite a una representación ponderar otras posiciones del volumen o de sus características. |
| U-Net | Arquitectura encoder-decoder con conexiones de salto, ampliamente usada en segmentación biomédica. |
| 3D U-Net | Variante de U-Net que opera directamente sobre volúmenes 3D. Es el baseline convolucional propuesto. |
| Encoder | Parte de la red que reduce resolución espacial y extrae representaciones cada vez más abstractas. |
| Decoder | Parte de la red que recupera resolución espacial para producir una máscara de segmentación. |
| Skip connection | Conexión que transfiere características del encoder al decoder para recuperar detalle espacial. |
| Bloque residual | Bloque con conexión de identidad que facilita entrenar redes más profundas. |
| Attention U-Net | Variante de U-Net que incorpora puertas de atención para priorizar regiones relevantes. |
| Puerta de atención | Módulo que modula características espaciales para enfocar el modelo en zonas informativas. |
| Swin Transformer | Transformer jerárquico basado en ventanas desplazadas. Reduce coste computacional frente a atención global pura. |
| Swin-UNETR | Arquitectura híbrida para segmentación 3D que combina Swin Transformer con un decodificador tipo U-Net. |
| nnU-Net | Framework auto-configurable que adapta preprocesamiento, arquitectura y entrenamiento al dataset. |
| TransBTS | Arquitectura de segmentación de tumores cerebrales que combina codificación 3D y Transformer con conexiones multiescala. |
| Baseline | Modelo de referencia usado para comparar mejoras. En la propuesta, 3D U-Net con bloques residuales cumple este papel. |
| Arquitectura híbrida | Modelo que combina componentes convolucionales y Transformer para capturar contexto local y global. |
| Fusión de modalidades | Estrategia para combinar información de `t1n`, `t1c`, `t2w` y `t2f`. |
| Fusión adaptativa | Módulo propuesto que aprende a ponderar dinámicamente las modalidades MRI según la región tumoral o contexto. |
| Aprendizaje contrastivo inter-modal | Técnica propuesta para acercar representaciones compatibles entre modalidades y separar representaciones no equivalentes. |
| Dependencias globales | Relaciones entre regiones distantes del volumen que pueden ser importantes para delimitar tumores complejos. |
| Contexto local | Información de vecindad cercana, especialmente útil para bordes, texturas y detalles anatómicos. |

## Entrenamiento, Evaluación y Diseño Experimental

| Término | Definición en este proyecto |
| --- | --- |
| Entrenamiento supervisado | Entrenamiento con pares imagen-máscara, usando la máscara experta como objetivo. |
| Inferencia | Uso de un modelo entrenado para generar una máscara de segmentación en nuevos casos. |
| Validación | Evaluación durante el desarrollo para ajustar decisiones de modelo y detectar sobreajuste. |
| Test externo | Evaluación en datos no usados durante diseño o entrenamiento, importante para medir generalización. |
| Generalización | Capacidad del modelo para funcionar en pacientes, centros o poblaciones no vistos. |
| Evaluación cross-institutional | Evaluación entre instituciones o centros clínicos distintos para medir robustez ante variabilidad de adquisición. |
| Evaluación cross-continental | Evaluación entre poblaciones o regiones geográficas distintas, por ejemplo usando BraTS-Africa como referencia de generalización. |
| Cross-validation | Estrategia de evaluación que divide el dataset en particiones para estimar rendimiento de forma más robusta. |
| Ablation study | Experimento donde se elimina o modifica un componente para medir su aportación real. |
| Overfitting | Situación en la que el modelo memoriza el entrenamiento y pierde rendimiento en datos nuevos. |
| Data augmentation | Transformaciones aplicadas a imágenes de entrenamiento para mejorar robustez, como rotaciones, recortes o variaciones de intensidad. |
| Patch 3D | Subvolumen usado como unidad de entrenamiento cuando el volumen completo no cabe eficientemente en memoria. |
| Batch size | Número de muestras o patches procesados antes de actualizar pesos del modelo. |
| Función de pérdida | Objetivo optimizado durante entrenamiento. En segmentación médica suelen combinarse Dice loss y pérdidas tipo cross-entropy. |
| Dice | Métrica de solapamiento entre máscara predicha y máscara de referencia. Valores más altos indican mejor segmentación. |
| Hausdorff 95 / HD95 | Métrica de distancia de contorno robusta a outliers extremos. Valores más bajos indican mejor delimitación espacial. |
| Sensibilidad / Recall | Proporción de región tumoral real correctamente detectada. |
| Precisión | Proporción de predicción positiva que corresponde realmente a tumor. |
| Calibración | Grado en que las probabilidades predichas reflejan confianza real. Puede ser relevante si se usan mapas de incertidumbre. |
| Robustez | Capacidad del modelo para mantener rendimiento ante cambios de intensidad, centro, protocolo o población. |

## Uso Clínico y Publicación

| Término | Definición en este proyecto |
| --- | --- |
| Planificación quirúrgica | Uso de la segmentación para apoyar decisiones sobre localización y extensión de una intervención. |
| Radioterapia | Tratamiento que requiere delimitar volúmenes objetivo y órganos de riesgo. En el proyecto aparece especialmente ligado a MEN-RT y GTV. |
| Seguimiento terapéutico | Comparación longitudinal de lesiones para evaluar evolución o respuesta al tratamiento. |
| Biomarcador de imagen | Medida derivada de la imagen, como volumen tumoral, que puede apoyar análisis clínicos. |
| Reproducibilidad | Capacidad de repetir resultados con datos, código, configuración y entorno documentados. |
| Citas obligatorias | Referencias que deben incluirse al usar datos BraTS 2024, según colección y alcance. |
| Q1 | Primer cuartil de impacto en rankings de revistas. La propuesta apunta a revistas Q1 en Computer Science e imagen médica. |
| JCR | Journal Citation Reports. Fuente usada para clasificar revistas por cuartiles. |
| Contribución innovadora | Parte diferencial del TFM: fusión adaptativa de modalidades y aprendizaje contrastivo inter-modal sobre arquitecturas Transformer-UNet híbridas. |

