#!/usr/bin/env python3
"""Draw the memoria diagrams (pipeline flow and fusion architecture) with matplotlib.

Outputs (docs/memoria/figuras/):
  - fig_pipeline_flujo.png       : experimental pipeline flow (data -> QC -> splits
                                   -> train -> predict -> evaluate).
  - fig_arquitectura_fusion.png  : FusionUNet flow + detail of the fusion block and
                                   its three variants (concat, global_weighted,
                                   adaptive_gating).
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

BLUE = "#cfe3f5"; GREEN = "#d6ecd2"; ORANGE = "#fde9d0"; GREY = "#e8e8e8"; RED = "#f7d4d4"


def box(ax, cx, cy, w, h, text, fc=BLUE, fontsize=10, ec="#33475b"):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                 boxstyle="round,pad=0.02,rounding_size=0.06", fc=fc, ec=ec, lw=1.4))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fontsize, zorder=5)


def arrow(ax, x1, y1, x2, y2, style="-|>"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                 mutation_scale=16, lw=1.6, color="#33475b"))


def pipeline_flow():
    fig, ax = plt.subplots(figsize=(7.2, 8.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 12); ax.axis("off")
    steps = [
        ("Conjunto de datos\nBraTS-GLI 2024\n(4 modalidades + máscara)", BLUE),
        ("Control de calidad (qc)\nintegridad de casos,\nmodalidades y etiquetas", GREEN),
        ("Particiones (splits)\n70 / 15 / 15 estratificado\ntrain · val · test", GREEN),
        ("Entrenamiento (train)\nbucle propio + validación\ncheckpoint best.pt", ORANGE),
        ("Inferencia (predict)\nventana deslizante 128³", ORANGE),
        ("Evaluación (evaluate)\nDice y HD95 por ET/TC/WT", RED),
    ]
    ys = [10.8, 9.0, 7.2, 5.4, 3.6, 1.8]
    for (txt, fc), y in zip(steps, ys):
        box(ax, 5, y, 5.4, 1.3, txt, fc=fc)
    for y0, y1 in zip(ys[:-1], ys[1:]):
        arrow(ax, 5, y0 - 0.65, 5, y1 + 0.65)
    # Config side-input into training
    box(ax, 1.35, 5.4, 2.2, 1.5, "Configuraciones\nYAML\n(dataset / modelo /\nentrenamiento)", fc=GREY, fontsize=8.5)
    arrow(ax, 2.45, 5.4, 2.3, 5.4)
    # test reserved note
    ax.text(8.5, 7.2, "test\nreservado", ha="center", va="center", fontsize=8, style="italic", color="#7a2b2b")
    arrow(ax, 7.75, 7.0, 8.0, 2.2)
    ax.set_title("Flujo del pipeline experimental", fontsize=13, pad=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig_pipeline_flujo.png", dpi=150)
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
