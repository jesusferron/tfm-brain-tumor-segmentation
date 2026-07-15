# Exploración de la fusión adaptativa (pilar 3)

Protocolo para agotar las vías de la contribución principal (`adaptive_gating`) dentro del presupuesto acordado con el tutor (**2-3 días de ejecución**) antes de decidir si la hipótesis es positiva o vira a un **resultado negativo defendible**.

## Diagnóstico de partida

Corrida preliminar (val, 5000 pasos, 1 semilla): `adaptive_gating` mean Dice 0.588, **por debajo** del baseline concat (0.607) y de `global_weighted` (0.606), con una **regresión tardía** (mean Dice 0.586 en época 4 → 0.521 en época 5).

El diagnóstico (`scripts/diagnose_adaptive_gating.py`) revela la causa raíz:

- **La compuerta no es adaptativa.** Sobre 30 casos de val produce **pesos idénticos** (t1c=0.332, t2f=0.291, t1n=0.205, t2w=0.172; std entre casos = 0.000). Ha aprendido un peso estático por modalidad, equivalente a `global_weighted` pero con un MLP no lineal por encima.
- Entropía ~1.353 (máx. uniforme 1.386): **no hay colapso** hacia una modalidad; el problema es la ausencia de adaptación.
- Causa: la señal de condicionamiento (media espacial global de las modalidades ya z-score-normalizadas) es casi constante entre casos, así que la compuerta no tiene información por-caso a la que adaptarse. El MLP extra solo añade no convexidad → inestabilidad tardía.

**Consecuencia para la estrategia:** estabilizar la optimización solo igualaría `adaptive_gating` a `global_weighted`. Para que la hipótesis tenga opción real hay que **darle a la compuerta una señal por-caso informativa**.

## Palancas disponibles (todas por config, desactivadas por defecto)

Modelo (arquitectura de la compuerta), en `configs/model/`:
- `fusion_stats: [mean, std]` — condiciona la compuerta con media Y desviación típica por canal. La std sí varía entre casos (extensión de tumor/cerebro): señal por-caso real. *(raíz del problema)*
- `fusion_temperature: T` — softmax más suave (T>1), evita cambios bruscos de la compuerta.

Entrenamiento (optimización de la compuerta), en `configs/training/`:
- `fusion_lr` — lr propio (más bajo) para los parámetros de fusión.
- `fusion_weight_decay` — weight decay propio para la fusión.
- `fusion_warmup_steps` — la compuerta entra desde identidad a lo largo de N pasos.
- `fusion_entropy_weight` — regulariza la entropía de la softmax (evita colapso).

## Configs preparadas

| Config | Qué cambia |
| :-- | :-- |
| `configs/model/residual_unet_3d_adaptive_gating.yaml` | Original (mean, sin knobs) |
| `configs/model/residual_unet_3d_adaptive_gating_meanstd.yaml` | Señal mean+std *(raíz)* |
| `configs/model/residual_unet_3d_adaptive_gating_temp.yaml` | Temperatura 2.0 |
| `configs/model/residual_unet_3d_adaptive_gating_meanstd_temp.yaml` | mean+std + temperatura |
| `configs/training/mac_m4_pro_128_5k_gate_stab.yaml` | fusion_lr 2e-5 + warmup 500 + entropía 0.01 |

## Plan de corridas (5000 pasos, semilla 20260526, para comparabilidad)

Referencias a batir: **concat 0.607**, global_weighted 0.606. Original adaptive_gating 0.588.

| Run | model-config | training-config | Pregunta |
| :-- | :-- | :-- | :-- |
| R1 | adaptive_gating (original) | `..._5k_gate_stab.yaml` | ¿Estabilizar quita la regresión y lo iguala a global_weighted? |
| R2 | `..._meanstd.yaml` | `..._5k.yaml` (base) | ¿La señal por-caso (mean+std) ayuda? |
| R3 | `..._meanstd.yaml` | `..._5k_gate_stab.yaml` | Combinado (mejor apuesta) |
| R4 | `..._meanstd_temp.yaml` | `..._5k_gate_stab.yaml` | Combinado + softmax suave |

Ejemplo de comando (R3), local M4 (~2 h) o L4:

```bash
python -m tfm_brats.cli train \
  --dataset-config configs/dataset/brats_gli_2024.yaml \
  --model-config configs/model/residual_unet_3d_adaptive_gating_meanstd.yaml \
  --training-config configs/training/mac_m4_pro_128_5k_gate_stab.yaml \
  --split-dir outputs/splits/brats_gli_2024_seed20260526 \
  --output-dir outputs/train/adaptive_gating_meanstd_stab \
  --max-steps 5000
```

Tras cada run: `predict` + `evaluate` sobre `val` (mismo flujo que el resto) para la cifra reportable, y `scripts/diagnose_adaptive_gating.py --checkpoint <best.pt> --model-config <la variante>` para ver si la compuerta ya varía entre casos (std > 0) y si desapareció la regresión.

Presupuesto: 4 runs x ~2 h ≈ 8 h; cabe en 2-3 días con margen para multi-semilla de la mejor variante.

## Criterio de decisión

- **Positivo:** si alguna variante supera concat (0.607) en val con margen y se sostiene en multi-semilla → la hipótesis se mantiene; se incluye en la corrida final.
- **Negativo defendible:** si tras estas vías (señal por-caso + estabilización) ninguna supera concat, se reporta como resultado negativo con evidencia: la fusión adaptativa condicionada por descriptores globales no mejora la concatenación en BraTS-GLI, y el diagnóstico explica por qué (la señal de condicionamiento global es poco informativa). Cumple el criterio del tutor de agotar vías dentro del alcance.

## Cómo ejecutar el diagnóstico

```bash
python scripts/diagnose_adaptive_gating.py \
  --checkpoint outputs/train/<run>/checkpoints/best.pt \
  --model-config configs/model/<variante>.yaml \
  --max-cases 40
```

Reporta la curva de validación (detecta regresión tras el mejor epoch) y los pesos de la compuerta por modalidad sobre casos reales (detecta si es estática o ya varía entre casos).
