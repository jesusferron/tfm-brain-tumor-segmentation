# Plan global del TFM

> Estado de cierre del proyecto experimental y del manuscrito. Última revisión: 2026-07-21. La
> estructura aprobada se mantiene en [`indice-memoria.md`](indice-memoria.md) y la trazabilidad
> cronológica en [`../vitacora/README.md`](../vitacora/README.md).

## 1. Estado ejecutivo

| Bloque | Estado | Evidencia principal |
| :-- | :-- | :-- |
| *Pipeline* reproducible MONAI | ✅ Completo | `tfm_brats/`, `configs/`, `tests/` |
| Control de calidad y particiones | ✅ Completo | `outputs/qc/`, `outputs/splits/brats_gli_2024_seed20260526/` |
| Ablación de fusión, tres semillas | ✅ Completa | `outputs/evaluation/final_all_test.csv` |
| Attention U-Net y Swin-UNETR, tres semillas | ✅ Completos | resúmenes finales en `outputs/evaluation/` |
| nnU-Net `3d_fullres`, *fold* 0 | ✅ Una corrida completa | métricas y artefactos de nnU-Net |
| Capítulos 1–6 | ✅ Textos revisados | `docs/memoria/capitulo-*.md` |
| Resumen, *abstract* y apéndice | ✅ Redactados | `resumen-abstract.md`, `apendice-reproducibilidad.md` |
| Bibliografía | ✅ Revisada | 34 referencias, sin citas huérfanas en los capítulos con citas |
| Formato oficial | 🟡 Borrador maquetado | `TFM_memoria_maquetada_borrador.docx`; faltan datos formales de portada |
| PDF de entrega | 🟡 Control visual superado | PDF temporal de 57 páginas; falta actualizar índices y exportar la versión final |

El alcance ambicioso —robustez ante modalidades ausentes o degradadas y mecanismos de fusión
intermedia o espacial— no se ejecutó y queda como trabajo futuro.

## 2. Resultados experimentales cerrados

La comparación principal se realizó sobre la partición denominada `test`, formada por 243 estudios.
La partición fue generada a nivel de estudio y presenta solapamiento longitudinal de sujetos con
entrenamiento o validación; por ello los resultados se interpretan como comparación interna y no
como generalización independiente a pacientes nuevos.

### Ablación de fusión sobre Residual U-Net 3D

| Estrategia | n | Dice medio |
| :-- | :-: | :-: |
| Concatenación | 3 | 0,706 ± 0,005 |
| Ponderación global | 3 | 0,706 ± 0,006 |
| Compuerta adaptativa | 3 | 0,586 ± 0,169 |
| Compuerta adaptativa media+desviación | 3 | 0,592 ± 0,171 |

La conclusión cerrada es descriptiva y acotada: no se obtuvo evidencia de que las compuertas
evaluadas mejoren de forma consistente la concatenación bajo este presupuesto. Cada variante
adaptativa presentó una corrida de bajo rendimiento entre tres repeticiones; con este tamaño
muestral no se estima una probabilidad general de fallo ni se establece su causa.

### Contextualización de arquitecturas

| Arquitectura | n | Dice medio | Interpretación |
| :-- | :-: | :-: | :-- |
| nnU-Net `3d_fullres`, *fold* 0 | 1 | 0,829 | Referencia externa con protocolo propio |
| Swin-UNETR | 3 | 0,752 ± 0,017 | Mayor media entre las configuraciones MONAI |
| Attention U-Net 3D | 3 | 0,735 ± 0,006 | Menor dispersión que Swin-UNETR |
| Residual U-Net + concatenación | 3 | 0,706 ± 0,005 | Base controlada de la ablación |

Esta ordenación no demuestra superioridad estadística ni permite atribuir todas las diferencias a la
arquitectura. nnU-Net usa planificación y entrenamiento propios; además, las ejecuciones locales y
A100 no conservaron un protocolo homogéneo de tiempo, memoria e inferencia.

## 3. Track experimental

- [x] Resolver el cuello de botella de E/S mediante copia al disco local del *runtime*.
- [x] Ejecutar la Residual U-Net y las cuatro estrategias de fusión con 15.000 pasos y tres semillas.
- [x] Ejecutar Attention U-Net y Swin-UNETR en A100 con tres semillas.
- [x] Entrenar nnU-Net `3d_fullres`, *fold* 0, durante 250 épocas y evaluarlo con el evaluador común.
- [x] Agregar Dice y HD95 por ET, TC y WT.
- [x] Conservar métricas ligeras y figuras reproducibles en el repositorio.
- [ ] Repetir con separación por sujeto, validación externa o evaluación oficial; trabajo futuro, no
  requisito para cerrar el experimento actual.

No se planifican más entrenamientos para la versión actual del TFM salvo que la revisión del tutor
requiera expresamente modificar el protocolo experimental.

## 4. Track de manuscrito y entrega

- [x] Mantener la estructura aprobada de seis capítulos.
- [x] Separar Metodología, a alto nivel, de Desarrollo, con detalle técnico.
- [x] Incorporar resultados finales de fusión, Attention U-Net, Swin-UNETR y nnU-Net.
- [x] Redactar conclusiones compatibles con el alcance y las limitaciones.
- [x] Generar la visión global del sistema y las comparaciones cualitativas.
- [x] Redactar resumen, *abstract* y palabras clave.
- [x] Redactar el apéndice de reproducibilidad y límites de versionado.
- [x] Completar la revisión formal y ampliar la bibliografía del estado del arte.
- [x] Retirar las notas editoriales internas de los capítulos antes de maquetar.
- [x] Integrar los Markdown en la plantilla oficial de la universidad.
- [x] Generar la portada provisional y los campos automáticos del índice general, el índice de
  figuras y el índice de tablas.
- [ ] Sustituir `PENDIENTE_COMMIT_FINAL` por el hash exacto de entrega y comprobar el acceso al remoto.
- [x] Exportar un PDF temporal y revisar saltos, pies de figura, tablas, enlaces, tipografía y
  numeración; no se detectaron elementos fuera de los márgenes.
- [ ] Completar los datos oficiales de portada, actualizar todos los campos en Microsoft Word y
  exportar el PDF definitivo.

El [`README.md`](README.md) de esta carpeta se conserva como material legado y no representa el
estado actual.

## 5. Limitaciones que deben permanecer visibles

1. La separación de datos se realizó por estudio, no por sujeto.
2. Las configuraciones MONAI tienen tres semillas; no se realizaron contrastes de hipótesis ni se
   definieron márgenes de equivalencia.
3. nnU-Net corresponde a una sola corrida del *fold* 0 y no es una ablación controlada de
   arquitectura.
4. El presupuesto de 15.000 pasos no demuestra convergencia individual de todas las familias.
5. La implementación interna de HD95 excluye del promedio los casos infinitos y conserva los casos
   doblemente vacíos como cero; debe reportarse junto con los denominadores finitos.
6. Las métricas internas no reproducen exactamente la evaluación oficial *lesion-wise* de
   BraTS-GLI 2024.
7. Los tiempos, la memoria y la inferencia no se registraron de forma homogénea en todos los
   entornos.
8. No existe validación externa ni evaluación clínica.

## 6. Criterio de cierre

El proyecto experimental está cerrado. El TFM estará listo para entrega cuando se cumplan
simultáneamente estas condiciones:

- la plantilla oficial contenga todas las secciones y los índices automáticos;
- el repositorio apunte al commit final y sea accesible para el tribunal;
- el PDF haya pasado una revisión visual completa;
- no queden notas editoriales, marcadores pendientes salvo los declarados como trabajo futuro, ni
  afirmaciones más fuertes que la evidencia disponible.
