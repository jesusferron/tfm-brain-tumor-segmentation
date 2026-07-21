#!/usr/bin/env python3
"""Draw the memoria diagrams (project overview and fusion architecture).

Outputs (docs/memoria/figuras/):
  - fig_pipeline_flujo.png       : big picture of the complete experimental design,
                                   including the MONAI and external nnU-Net routes.
  - fig_arquitectura_fusion.png  : FusionUNet flow + detail of the fusion block and
                                   its evaluated variants.
No external binaries required (pure matplotlib).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "docs/memoria/figuras"
OUT.mkdir(parents=True, exist_ok=True)

BLUE = "#cfe3f5"
GREEN = "#d6ecd2"
ORANGE = "#fde9d0"
GREY = "#e8e8e8"
RED = "#f7d4d4"
PURPLE = "#e7dcf3"


def box(ax, cx, cy, w, h, text, fc=BLUE, fontsize=10, ec="#33475b"):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                 boxstyle="round,pad=0.02,rounding_size=0.06", fc=fc, ec=ec, lw=1.4))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fontsize, zorder=5)


def arrow(ax, x1, y1, x2, y2, style="-|>"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                 mutation_scale=16, lw=1.6, color="#33475b"))


def pipeline_flow():
    """Draw the end-to-end experimental design requested for the thesis."""
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 11)
    ax.axis("off")

    # Data preparation shared by all model families.
    box(
        ax,
        2.0,
        9.4,
        3.2,
        1.45,
        "BraTS-GLI 2024\nT1n · T1c · T2w · FLAIR\n+ máscara de referencia",
        fc=BLUE,
        fontsize=9.5,
    )
    box(
        ax,
        6.0,
        9.4,
        3.0,
        1.45,
        "Control de calidad (qc)\nintegridad, dimensiones,\nmodalidades y etiquetas",
        fc=GREEN,
        fontsize=9.2,
    )
    box(
        ax,
        10.2,
        9.4,
        3.7,
        1.55,
        "Particiones 70 / 15 / 15\na nivel de estudio\nentrenamiento · validación · evaluación",
        fc=GREEN,
        fontsize=9.2,
    )
    arrow(ax, 3.6, 9.4, 4.5, 9.4)
    arrow(ax, 7.5, 9.4, 8.35, 9.4)

    # The split feeds two deliberately separate pipelines.
    box(
        ax,
        5.6,
        7.1,
        6.0,
        1.35,
        "Pipeline MONAI compartido\ncarga NIfTI · regiones ET/TC/WT · normalización\naumento (entrenamiento) · parches 128³",
        fc=GREY,
        fontsize=9.2,
    )
    box(
        ax,
        13.0,
        7.1,
        4.3,
        1.65,
        "Pipeline externo nnU-Net\n3d_fullres · fold 0\nplanificación, preprocesado, aumento\ny entrenamiento propios",
        fc=PURPLE,
        fontsize=9.1,
    )
    arrow(ax, 9.5, 8.62, 6.5, 7.78)
    arrow(ax, 11.3, 8.62, 12.5, 7.95)

    # MONAI model branches.
    box(
        ax,
        2.6,
        4.65,
        3.7,
        1.75,
        "Residual U-Net 3D\n+ bloque de fusión\nconcatenación · global · adaptativa\n(media / media+desv.)",
        fc=ORANGE,
        fontsize=9.0,
    )
    box(
        ax,
        6.5,
        4.65,
        3.0,
        1.45,
        "Attention U-Net 3D\ncompuertas de atención\nen conexiones de salto",
        fc=ORANGE,
        fontsize=9.2,
    )
    box(
        ax,
        10.0,
        4.65,
        3.0,
        1.45,
        "Swin-UNETR\ncodificador Transformer\n+ decodificador convolucional",
        fc=ORANGE,
        fontsize=9.2,
    )
    for x in (2.6, 6.5, 10.0):
        arrow(ax, 5.6, 6.42, x, 5.53)

    # Predictions from every branch are evaluated by the same implementation.
    box(
        ax,
        8.0,
        2.35,
        4.5,
        1.1,
        "Predicciones por estudio\nregiones ET · TC · WT",
        fc=BLUE,
        fontsize=9.5,
    )
    for x in (2.6, 6.5, 10.0):
        arrow(ax, x, 3.77, 7.25 + (x - 6.5) * 0.18, 2.92)
    arrow(ax, 13.0, 6.27, 9.75, 2.92)

    box(
        ax,
        8.0,
        0.7,
        4.7,
        1.15,
        "Evaluación común\nDice y HD95 por región\n+ agregación multisemilla cuando n = 3",
        fc=RED,
        fontsize=9.5,
    )
    arrow(ax, 8.0, 1.80, 8.0, 1.28)

    ax.set_title("Visión global del sistema experimental", fontsize=14, pad=10, weight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "fig_pipeline_flujo.png", dpi=180)
    plt.close(fig)


def fusion_architecture():
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_xlim(0, 16); ax.set_ylim(0, 10); ax.axis("off")

    # Top: overall FusionUNet flow
    box(ax, 2.1, 8.2, 3.0, 1.5, "Entrada\n(B, 4, 128³)\nT1n · T1c · T2w · FLAIR", fc=BLUE, fontsize=9)
    box(ax, 6.2, 8.2, 2.6, 1.5, "Bloque de\nfusión", fc=ORANGE, fontsize=10)
    box(ax, 10.4, 8.2, 3.2, 1.5, "Residual U-Net 3D\ncodificador–decodificador\n+ conexiones residuales", fc=GREEN, fontsize=9)
    box(ax, 14.2, 8.2, 2.8, 1.5, "Salida\n(B, 3, 128³)\nET · TC · WT", fc=RED, fontsize=9)
    for x0, x1 in [(3.6, 4.9), (7.5, 9.1), (12.0, 12.8)]:
        arrow(ax, x0, 8.2, x1, 8.2)

    ax.annotate("detalle del bloque de fusión", xy=(6.2, 7.45), xytext=(6.2, 6.7),
                ha="center", fontsize=9, style="italic",
                arrowprops=dict(arrowstyle="-|>", color="#33475b", lw=1.3))

    # Bottom: fusion block detail (adaptive gating) + variants
    box(ax, 2.2, 4.2, 3.0, 1.2, "GAP espacial\n(B, 4, 128³) → (B, 4)", fc=BLUE, fontsize=9)
    box(ax, 6.4, 4.2, 3.0, 1.2, "MLP compuerta\n4 → 8 → 4", fc=ORANGE, fontsize=9)
    box(ax, 10.4, 4.2, 3.0, 1.2, "softmax por muestra\n→ pesos (B, 4)", fc=ORANGE, fontsize=9)
    box(ax, 14.0, 4.2, 3.0, 1.2, "reponderar canales\nx · w · C", fc=GREEN, fontsize=9)
    for x0, x1 in [(3.7, 4.9), (7.9, 8.9), (11.9, 12.5)]:
        arrow(ax, x0, 4.2, x1, 4.2)
    ax.text(8, 5.6, "Bloque de fusión — compuerta adaptativa (adaptive_gating)", ha="center",
            fontsize=10, weight="bold")

    variants = ("Variantes de fusión evaluadas:\n"
                "• concat — identidad (baseline); la U-Net concatena los 4 canales.\n"
                "• global_weighted — un peso por modalidad, fijo (independiente de la entrada).\n"
                "• adaptive_gating — pesos por muestra (esquema inferior); variante media+std enriquece la señal.")
    ax.text(8, 1.7, variants, ha="center", va="center", fontsize=8.6,
            bbox=dict(boxstyle="round,pad=0.5", fc="#f6f6f6", ec="#999"))
    ax.set_title("Arquitectura de fusión multimodal (FusionUNet)", fontsize=13, pad=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig_arquitectura_fusion.png", dpi=150)
    plt.close(fig)


def main():
    pipeline_flow()
    fusion_architecture()
    print("diagramas escritos en", OUT)


if __name__ == "__main__":
    main()
