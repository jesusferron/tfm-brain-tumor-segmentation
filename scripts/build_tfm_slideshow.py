#!/usr/bin/env python3
"""Build the TFM defense deck from the VIU corporate PowerPoint template."""

from __future__ import annotations

import csv
import glob
import json
import os
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = next((ROOT / "docs" / "slideshow").glob("Presentaci*n corporativa*.pptx"))
OUTPUT = ROOT / "docs" / "slideshow" / "TFM_presentacion_Jesus_Ferron_Rubio.pptx"
FIGURES = ROOT / "docs" / "memoria" / "figuras"
EVAL = ROOT / "outputs" / "evaluation"

FONT = "Arial"
ORANGE = RGBColor(0xE6, 0x4F, 0x12)
ORANGE_2 = RGBColor(0xEB, 0x72, 0x43)
ORANGE_3 = RGBColor(0xF1, 0x96, 0x72)
ORANGE_4 = RGBColor(0xF5, 0xB8, 0xA1)
PALE = RGBColor(0xFD, 0xEC, 0xE8)
INK = RGBColor(0x16, 0x17, 0x1A)
NAVY = RGBColor(0x16, 0x24, 0x3A)
MID = RGBColor(0x61, 0x64, 0x68)
LIGHT = RGBColor(0xCD, 0xCF, 0xCE)
LIGHTER = RGBColor(0xF3, 0xF3, 0xF2)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x2E, 0x7D, 0x32)
RED = RGBColor(0xB6, 0x24, 0x18)


def inch(value: float):
    return Inches(value)


def set_shape_text(
    shape,
    text: str,
    *,
    size: float = 16,
    color: RGBColor = INK,
    bold: bool = False,
    align=PP_ALIGN.LEFT,
    valign=MSO_ANCHOR.MIDDLE,
    margin: float = 0.08,
    font: str = FONT,
    italic: bool = False,
):
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = inch(margin)
    tf.margin_right = inch(margin)
    tf.margin_top = inch(margin)
    tf.margin_bottom = inch(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    p.space_before = Pt(0)
    p.space_after = Pt(0)
    p.line_spacing = 1.0
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    return shape


def add_text(slide, text, x, y, w, h, **kwargs):
    shape = slide.shapes.add_textbox(inch(x), inch(y), inch(w), inch(h))
    return set_shape_text(shape, text, **kwargs)


def add_box(
    slide,
    x,
    y,
    w,
    h,
    *,
    fill=WHITE,
    line=LIGHT,
    radius=True,
    text=None,
    size=15,
    color=INK,
    bold=False,
    align=PP_ALIGN.LEFT,
    valign=MSO_ANCHOR.MIDDLE,
    margin=0.15,
):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(kind, inch(x), inch(y), inch(w), inch(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line
    shape.line.width = Pt(1)
    if text is not None:
        set_shape_text(
            shape,
            text,
            size=size,
            color=color,
            bold=bold,
            align=align,
            valign=valign,
            margin=margin,
        )
    return shape


def add_circle(slide, x, y, d, text, *, fill=ORANGE, color=WHITE, size=16, bold=True):
    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, inch(x), inch(y), inch(d), inch(d))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    set_shape_text(shape, text, size=size, color=color, bold=bold, align=PP_ALIGN.CENTER, margin=0)
    return shape


def add_title(slide, section: str, title: str, subtitle: str | None = None, *, color=INK):
    add_text(slide, section.upper(), 0.55, 0.32, 9.8, 0.22, size=8.5, color=ORANGE, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, title, 0.55, 0.56, 11.0, 0.48, size=24, color=color, bold=True, valign=MSO_ANCHOR.TOP)
    if subtitle:
        add_text(slide, subtitle, 0.58, 1.03, 11.2, 0.35, size=10.5, color=MID, valign=MSO_ANCHOR.TOP)
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inch(0.55), inch(1.34), inch(0.85), inch(0.05))
    line.fill.solid()
    line.fill.fore_color.rgb = ORANGE
    line.line.fill.background()


def add_footer(slide, number: int, source: str | None = None, *, light=False):
    color = WHITE if light else MID
    if source:
        add_text(slide, source, 0.55, 7.08, 11.7, 0.16, size=7.5, color=color, valign=MSO_ANCHOR.TOP)
    # The corporate master already prints the year at the bottom-right.
    add_text(slide, f"{number:02d}", 12.48, 6.78, 0.30, 0.18, size=7.5, color=color, bold=True, align=PP_ALIGN.RIGHT, valign=MSO_ANCHOR.TOP)


def add_metric_chip(slide, x, y, w, title, detail, fill=PALE):
    add_box(slide, x, y, w, 0.76, fill=fill, line=fill)
    add_text(slide, title, x + 0.14, y + 0.08, w - 0.28, 0.24, size=14, color=ORANGE, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, detail, x + 0.14, y + 0.35, w - 0.28, 0.27, size=9.2, color=INK, valign=MSO_ANCHOR.TOP)


def add_picture_contain(slide, path: Path, x, y, w, h, *, border=LIGHT):
    with Image.open(path) as im:
        iw, ih = im.size
    scale = min(w / iw, h / ih)
    pw, ph = iw * scale, ih * scale
    px, py = x + (w - pw) / 2, y + (h - ph) / 2
    if border:
        add_box(slide, x, y, w, h, fill=WHITE, line=border, radius=False)
    return slide.shapes.add_picture(str(path), inch(px), inch(py), inch(pw), inch(ph))


def add_chevron(slide, x, y, w=0.3, h=0.5, color=ORANGE):
    shape = slide.shapes.add_shape(MSO_SHAPE.CHEVRON, inch(x), inch(y), inch(w), inch(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def remove_placeholders(slide):
    for shape in list(slide.shapes):
        if shape.is_placeholder:
            shape._element.getparent().remove(shape._element)


def set_notes(slide, duration: str, points: list[str]):
    tf = slide.notes_slide.notes_text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = f"Tiempo orientativo: {duration}"
    for point in points:
        p = tf.add_paragraph()
        p.text = point
        p.level = 0


def add_fusion_bar_chart(slide, x, y, w, h, rows):
    labels = [
        ("Concatenación", ORANGE),
        ("Ponderación\nglobal", ORANGE_2),
        ("Compuerta\nmedia", ORANGE_3),
        ("Compuerta\nmedia+desv.", ORANGE_4),
    ]
    values = [float(r["mean_dice_mean"]) for r in rows]
    errors = [float(r["mean_dice_std"]) for r in rows]
    y0, ymax = 0.30, 0.80
    chart_bottom = y + h - 0.85
    chart_top = y + 0.25
    chart_h = chart_bottom - chart_top
    axis = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, inch(x + 0.55), inch(chart_top), inch(x + 0.55), inch(chart_bottom))
    axis.line.color.rgb = MID
    base = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, inch(x + 0.55), inch(chart_bottom), inch(x + w), inch(chart_bottom))
    base.line.color.rgb = MID
    for tick in [0.4, 0.5, 0.6, 0.7, 0.8]:
        ty = chart_bottom - (tick - y0) / (ymax - y0) * chart_h
        grid = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, inch(x + 0.55), inch(ty), inch(x + w), inch(ty))
        grid.line.color.rgb = LIGHT
        grid.line.dash_style = MSO_LINE_DASH_STYLE.DASH
        add_text(slide, f"{tick:.1f}".replace(".", ","), x, ty - 0.10, 0.45, 0.2, size=8, color=MID, align=PP_ALIGN.RIGHT)
    slot = (w - 0.75) / 4
    for i, ((label, color), value, err) in enumerate(zip(labels, values, errors)):
        bx = x + 0.78 + i * slot + slot * 0.19
        bw = slot * 0.62
        by = chart_bottom - (value - y0) / (ymax - y0) * chart_h
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inch(bx), inch(by), inch(bw), inch(chart_bottom - by))
        bar.fill.solid()
        bar.fill.fore_color.rgb = color
        bar.line.fill.background()
        e_top = chart_bottom - (min(ymax, value + err) - y0) / (ymax - y0) * chart_h
        e_bottom = chart_bottom - (max(y0, value - err) - y0) / (ymax - y0) * chart_h
        errline = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, inch(bx + bw / 2), inch(e_top), inch(bx + bw / 2), inch(e_bottom))
        errline.line.color.rgb = INK
        errline.line.width = Pt(1.5)
        for ey in [e_top, e_bottom]:
            cap = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, inch(bx + bw * 0.28), inch(ey), inch(bx + bw * 0.72), inch(ey))
            cap.line.color.rgb = INK
            cap.line.width = Pt(1.5)
        add_text(slide, f"{value:.3f}".replace(".", ","), bx - 0.08, by - 0.31, bw + 0.16, 0.25, size=10, color=INK, bold=True, align=PP_ALIGN.CENTER)
        add_text(slide, label, bx - 0.25, chart_bottom + 0.10, bw + 0.5, 0.55, size=8.2, color=INK, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.TOP)


def add_architecture_bar_chart(slide, x, y, w, h, rows):
    ordered = [
        ("nnU-Net", "nnunet_3dfullres", NAVY),
        ("Swin-\nUNETR", "swin_unetr", ORANGE),
        ("Attention\nU-Net", "attention_unet_3d", ORANGE_2),
        ("Residual +\nconcat.", "concat", ORANGE_3),
        ("Residual +\nglobal", "global_weighted", ORANGE_4),
        ("Adapt.\nmedia", "adaptive_gating", LIGHT),
        ("Adapt.\nmedia+desv.", "adaptive_gating_meanstd", LIGHT),
    ]
    lookup = {r["model"]: r for r in rows}
    y0, ymax = 0.45, 0.90
    chart_bottom = y + h - 0.75
    chart_top = y + 0.28
    chart_h = chart_bottom - chart_top
    axis = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, inch(x + 0.52), inch(chart_top), inch(x + 0.52), inch(chart_bottom))
    axis.line.color.rgb = MID
    base = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, inch(x + 0.52), inch(chart_bottom), inch(x + w), inch(chart_bottom))
    base.line.color.rgb = MID
    for tick in [0.5, 0.6, 0.7, 0.8, 0.9]:
        ty = chart_bottom - (tick - y0) / (ymax - y0) * chart_h
        grid = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, inch(x + 0.52), inch(ty), inch(x + w), inch(ty))
        grid.line.color.rgb = LIGHT
        grid.line.dash_style = MSO_LINE_DASH_STYLE.DASH
        add_text(slide, f"{tick:.1f}".replace(".", ","), x, ty - 0.10, 0.43, 0.2, size=8, color=MID, align=PP_ALIGN.RIGHT)
    slot = (w - 0.66) / len(ordered)
    for i, (label, key, color) in enumerate(ordered):
        value = float(lookup[key]["mean_dice_mean"])
        bx = x + 0.66 + i * slot + slot * 0.16
        bw = slot * 0.68
        by = chart_bottom - (value - y0) / (ymax - y0) * chart_h
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inch(bx), inch(by), inch(bw), inch(chart_bottom - by))
        bar.fill.solid()
        bar.fill.fore_color.rgb = color
        bar.line.fill.background()
        add_text(slide, f"{value:.3f}".replace(".", ","), bx - 0.12, by - 0.27, bw + 0.24, 0.22, size=8.5, color=INK, bold=True, align=PP_ALIGN.CENTER)
        add_text(slide, label, bx - 0.18, chart_bottom + 0.08, bw + 0.36, 0.48, size=7.2, color=INK, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.TOP)


def load_data():
    with (EVAL / "final_all_test.csv").open(newline="", encoding="utf-8") as f:
        all_rows = list(csv.DictReader(f))
    with (EVAL / "final_fusion_ablation_test.csv").open(newline="", encoding="utf-8") as f:
        fusion_rows = list(csv.DictReader(f))
    seed_values = {}
    for model in ["concat", "global_weighted", "adaptive_gating", "adaptive_gating_meanstd"]:
        vals = []
        for path in sorted(glob.glob(str(EVAL / f"final_{model}_seed*_test_metrics_summary.json"))):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            aggregates = data["aggregates"]
            value = sum(aggregates[k]["mean"] for k in ["ET_dice", "TC_dice", "WT_dice"]) / 3
            seed = Path(path).stem.split("_seed", 1)[1].split("_", 1)[0]
            vals.append((seed, value))
        seed_values[model] = vals
    return all_rows, fusion_rows, seed_values


def build_deck():
    all_rows, fusion_rows, seeds = load_data()
    prs = Presentation(str(TEMPLATE))
    prs.core_properties.title = "Segmentación de tumores cerebrales en resonancia magnética multimodal"
    prs.core_properties.subject = "Presentación de defensa del Trabajo Fin de Máster"
    prs.core_properties.author = "Jesús Ferrón Rubio"
    prs.core_properties.keywords = "TFM, BraTS-GLI 2024, segmentación 3D, fusión multimodal, MONAI"

    layouts = {
        "cover": prs.slides[0].slide_layout,
        "section": prs.slides[1].slide_layout,
        "white": prs.slides[2].slide_layout,
        "white_blob": prs.slides[5].slide_layout,
        "gray": prs.slides[6].slide_layout,
        "orange": prs.slides[7].slide_layout,
        "split": prs.slides[8].slide_layout,
        "final": prs.slides[9].slide_layout,
    }

    # Update the dated example text embedded in the corporate layouts.
    for master in prs.slide_masters:
        for layout in master.slide_layouts:
            for shape in layout.shapes:
                if getattr(shape, "has_text_frame", False) and "09/03/2022" in shape.text:
                    date_color = WHITE if layout in (layouts["cover"], layouts["orange"], layouts["final"]) else INK
                    set_shape_text(shape, "2026", size=9, color=date_color, align=PP_ALIGN.RIGHT, margin=0)

    # Remove sample slides while preserving their masters and layouts.
    sld_id_lst = prs.slides._sldIdLst
    for sld_id in list(sld_id_lst):
        prs.part.drop_rel(sld_id.rId)
        sld_id_lst.remove(sld_id)

    def new(layout_name):
        slide = prs.slides.add_slide(layouts[layout_name])
        remove_placeholders(slide)
        return slide

    # 01 — Cover
    slide = new("cover")
    card = add_box(slide, 0.55, 0.50, 7.75, 2.15, fill=WHITE, line=ORANGE, radius=True)
    card.fill.transparency = 3
    add_text(slide, "TRABAJO FIN DE MÁSTER", 0.82, 0.70, 5.8, 0.25, size=9, color=ORANGE, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "Segmentación de tumores cerebrales\nen resonancia magnética multimodal", 0.80, 0.95, 7.05, 0.92, size=23, color=INK, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "mediante arquitecturas Transformer-UNet híbridas", 0.82, 1.90, 6.85, 0.30, size=12, color=MID, valign=MSO_ANCHOR.TOP)
    add_text(slide, "Jesús Ferrón Rubio", 0.82, 2.24, 3.3, 0.25, size=11, color=INK, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "Máster Universitario en Big Data y Ciencia de Datos · Curso 2025–2026", 3.28, 2.24, 4.5, 0.27, size=8.5, color=MID, align=PP_ALIGN.RIGHT, valign=MSO_ANCHOR.TOP)
    add_footer(slide, 1, "Directora: Yudith Coromoto Cardinale Villarreal", light=True)
    set_notes(slide, "0:40", [
        "Presentar el trabajo en una frase: segmentación 3D de gliomas con cuatro secuencias de RM.",
        "Anticipar el foco: comprobar si una fusión adaptativa ligera mejora una concatenación directa bajo un experimento controlado.",
    ])

    # 02 — Takeaways
    slide = new("white")
    add_title(slide, "Mapa de la defensa", "Tres ideas para llevarse")
    takeaways = [
        ("01", "Pregunta controlada", "Solo cambia la regla de fusión; la Residual U-Net 3D, los datos y el entrenamiento permanecen fijos."),
        ("02", "Resultado negativo útil", "Las compuertas adaptativas rondan 0,59 Dice y son inestables; concatenación y ponderación global alcanzan 0,706."),
        ("03", "Alcance prudente", "La evidencia compara configuraciones dentro de BraTS-GLI; no demuestra generalización por paciente ni utilidad clínica."),
    ]
    for i, (num, head, body) in enumerate(takeaways):
        x = 0.70 + i * 4.15
        add_box(slide, x, 1.78, 3.72, 4.25, fill=WHITE, line=LIGHT, radius=True)
        add_circle(slide, x + 0.22, 2.00, 0.62, num, size=11)
        add_text(slide, head, x + 0.25, 2.85, 3.10, 0.43, size=17, color=INK, bold=True, valign=MSO_ANCHOR.TOP)
        add_text(slide, body, x + 0.25, 3.43, 3.15, 1.75, size=12.2, color=MID, valign=MSO_ANCHOR.TOP)
        add_box(slide, x + 0.25, 5.43, 2.1, 0.35, fill=PALE, line=PALE, text=["DISEÑO", "EVIDENCIA", "LÍMITES"][i], size=8.5, color=ORANGE, bold=True, align=PP_ALIGN.CENTER, margin=0)
    add_footer(slide, 2)
    set_notes(slide, "0:50", [
        "Usar esta diapositiva como contrato de la presentación: diseño, evidencia y límites.",
        "No desarrollar todavía los números; se justificarán después con la metodología y los resultados.",
    ])

    # 03 — Clinical/computational problem
    slide = new("gray")
    add_title(slide, "01 · Problema", "Delimitar un glioma es una tarea tridimensional y multimodal")
    add_circle(slide, 5.35, 2.05, 2.55, "3D", fill=ORANGE, size=32)
    add_text(slide, "Volumen completo", 5.10, 4.75, 3.05, 0.28, size=11, color=INK, bold=True, align=PP_ALIGN.CENTER)
    cards = [
        (0.72, 1.85, "MANUAL", "Lenta, experta y sujeta a variabilidad entre observadores."),
        (9.08, 1.85, "HETEROGÉNEA", "Los límites y la señal cambian entre subregiones y estudios."),
        (0.72, 4.78, "MULTIMODAL", "Ninguna secuencia resume por sí sola toda la lesión."),
        (9.08, 4.78, "GENERALIZACIÓN", "El rendimiento puede caer entre centros, protocolos y poblaciones."),
    ]
    for x, y, head, body in cards:
        add_box(slide, x, y, 3.55, 1.30, fill=WHITE, line=WHITE)
        add_text(slide, head, x + 0.18, y + 0.14, 3.10, 0.25, size=10, color=ORANGE, bold=True, valign=MSO_ANCHOR.TOP)
        add_text(slide, body, x + 0.18, y + 0.47, 3.10, 0.62, size=11.3, color=INK, valign=MSO_ANCHOR.TOP)
    add_footer(slide, 3, "Contexto: Langen et al. (2017); Kouli et al. (2022); Khalighi et al. (2024)")
    set_notes(slide, "1:05", [
        "Explicar por qué la segmentación no es una clasificación: hay que asignar una región a cada vóxel del volumen.",
        "Conectar la dificultad clínica con el reto técnico: combinar señales complementarias y conservar detalle espacial.",
        "Aclarar que el sistema es apoyo a segmentación, no diagnóstico ni cribado.",
    ])

    # 04 — Modalities and target regions
    slide = new("white")
    add_title(slide, "01 · Problema", "Cuatro secuencias de entrada; tres regiones anidadas de salida")
    modalities = [
        ("T1n", "Referencia anatómica", ORANGE),
        ("T1c", "Realce tras contraste", ORANGE_2),
        ("T2w", "Contenido de agua", ORANGE_3),
        ("FLAIR", "Componente periférico", ORANGE_4),
    ]
    for i, (abbr, detail, color) in enumerate(modalities):
        x = 0.60 + i * 3.05
        add_box(slide, x, 1.78, 2.72, 1.34, fill=WHITE, line=color)
        add_circle(slide, x + 0.16, 1.98, 0.72, abbr, fill=color, size=11)
        add_text(slide, detail, x + 1.00, 2.04, 1.48, 0.55, size=11.2, color=INK, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "Fusión multimodal", 4.72, 3.45, 3.9, 0.35, size=15, color=ORANGE, bold=True, align=PP_ALIGN.CENTER)
    for i in range(3):
        add_chevron(slide, 5.58 + i * 0.72, 3.91, 0.42, 0.48, ORANGE)
    regions = [
        ("ET", "Tumor realzante", "{3}", ORANGE),
        ("TC", "Núcleo tumoral", "{1, 3, 4}", ORANGE_2),
        ("WT", "Tumor completo", "{1, 2, 3, 4}", ORANGE_3),
    ]
    for i, (abbr, detail, labels, color) in enumerate(regions):
        x = 1.24 + i * 4.08
        add_box(slide, x, 4.65, 3.55, 1.38, fill=PALE, line=color)
        add_circle(slide, x + 0.18, 4.93, 0.72, abbr, fill=color, size=13)
        add_text(slide, detail, x + 1.05, 4.84, 2.15, 0.30, size=13, color=INK, bold=True, valign=MSO_ANCHOR.TOP)
        add_text(slide, f"Etiquetas BraTS {labels}", x + 1.05, 5.23, 2.15, 0.26, size=9.2, color=MID, valign=MSO_ANCHOR.TOP)
    add_text(slide, "ET ⊂ TC ⊂ WT", 5.38, 6.32, 2.6, 0.30, size=13, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, 4, "Convención regional de BraTS-GLI 2024")
    set_notes(slide, "1:15", [
        "Dar una frase por modalidad y evitar sugerir una correspondencia exclusiva modalidad-región.",
        "Explicar que las salidas son tres máscaras multietiqueta anidadas: ET dentro de TC y TC dentro de WT.",
        "Este carácter complementario motiva la pregunta sobre cómo fusionar los canales.",
    ])

    # 05 — Research question
    slide = new("orange")
    add_text(slide, "PREGUNTA DE INVESTIGACIÓN", 0.65, 0.60, 5.0, 0.30, size=9, color=WHITE, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "¿Puede una ponderación explícita y ligera de las modalidades mejorar de forma consistente la segmentación 3D frente a la concatenación?", 0.70, 1.55, 11.70, 2.30, size=28, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "Manteniendo fija la Residual U-Net 3D y un coste computacional asumible", 2.05, 4.18, 9.25, 0.45, size=14, color=WHITE, align=PP_ALIGN.CENTER)
    add_box(slide, 3.42, 5.08, 6.50, 0.82, fill=WHITE, line=WHITE, text="Hipótesis: la adaptación por entrada aportará una mejora reproducible", size=12.5, color=ORANGE, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, 5, light=True)
    set_notes(slide, "1:00", [
        "Leer la pregunta de forma pausada y enfatizar dos términos: consistente y manteniendo fija la arquitectura.",
        "La hipótesis no se evalúa con una única ejecución: consistencia exige varias semillas.",
    ])

    # 06 — Controlled design
    slide = new("white_blob")
    add_title(slide, "02 · Diseño", "Un experimento de ablación: una variable cambia y el resto se congela")
    add_text(slide, "SOLO CAMBIA", 4.92, 2.28, 3.85, 0.38, size=13, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "LA FUSIÓN", 4.62, 2.75, 4.45, 0.78, size=30, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    fixed = [
        ("01", "Residual U-Net 3D", "≈1,19 M parámetros"),
        ("02", "Datos y particiones", "Mismo train / val / test"),
        ("03", "Entrenamiento", "15.000 pasos · misma pérdida"),
        ("04", "Evaluación", "Dice y HD95 en 243 estudios"),
    ]
    for i, (num, head, sub) in enumerate(fixed):
        y = 1.70 + i * 1.12
        add_circle(slide, 0.72, y, 0.54, num, size=9)
        add_text(slide, head, 1.45, y - 0.01, 2.65, 0.28, size=14, color=INK, bold=True, valign=MSO_ANCHOR.TOP)
        add_text(slide, sub, 1.45, y + 0.33, 2.55, 0.24, size=9.5, color=MID, valign=MSO_ANCHOR.TOP)
        if i < 3:
            line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, inch(0.99), inch(y + 0.55), inch(0.99), inch(y + 1.08))
            line.line.color.rgb = LIGHT
    add_box(slide, 6.75, 5.30, 5.20, 0.70, fill=WHITE, line=ORANGE, text="4 estrategias × 3 semillas = 12 entrenamientos", size=13, color=INK, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, 6)
    set_notes(slide, "1:15", [
        "Esta es la diapositiva clave para defender causalidad interna: la ablación residual cambia solo el bloque de entrada.",
        "Las referencias Swin-UNETR, Attention U-Net y nnU-Net se mostrarán después, pero no forman parte de esta ablación controlada.",
    ])

    # 07 — Dataset and splits
    slide = new("white")
    add_title(slide, "02 · Diseño", "BraTS-GLI 2024: control de calidad y particiones reproducibles")
    add_text(slide, "1.621", 0.70, 1.68, 3.10, 0.72, size=36, color=ORANGE, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "estudios post-tratamiento con 4 modalidades y máscara", 0.72, 2.37, 3.40, 0.68, size=12, color=INK, valign=MSO_ANCHOR.TOP)
    add_box(slide, 0.70, 3.30, 3.58, 1.18, fill=PALE, line=PALE)
    add_text(slide, "QC: 1.621 / 1.621", 0.92, 3.52, 2.98, 0.28, size=15, color=GREEN, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "modalidades, geometría, afín y etiquetas válidas", 0.92, 3.91, 2.98, 0.30, size=9.5, color=MID, valign=MSO_ANCHOR.TOP)
    # Split bar
    bar_x, bar_y, bar_w, bar_h = 4.82, 2.15, 7.25, 0.72
    widths = [0.70 * bar_w, 0.15 * bar_w, 0.15 * bar_w]
    colors = [ORANGE, ORANGE_3, LIGHT]
    names = ["TRAIN", "VAL", "TEST"]
    counts = ["1.135", "243", "243"]
    cur = bar_x
    for width, color, name, count in zip(widths, colors, names, counts):
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, inch(cur), inch(bar_y), inch(width), inch(bar_h))
        shape.fill.solid(); shape.fill.fore_color.rgb = color; shape.line.fill.background()
        set_shape_text(shape, f"{name}\n{count}", size=10.5, color=WHITE if color != LIGHT else INK, bold=True, align=PP_ALIGN.CENTER, margin=0)
        cur += width
    add_text(slide, "70 %", 4.86, 1.78, widths[0] - 0.1, 0.25, size=10, color=ORANGE, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "15 %", 4.82 + widths[0], 1.78, widths[1], 0.25, size=10, color=ORANGE_3, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "15 %", 4.82 + widths[0] + widths[1], 1.78, widths[2], 0.25, size=10, color=MID, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "Estratificación", 4.84, 3.40, 2.1, 0.30, size=13, color=INK, bold=True, valign=MSO_ANCHOR.TOP)
    chips = ["origen", "presencia de ET", "cuartil de WT"]
    for i, chip in enumerate(chips):
        add_box(slide, 4.82 + i * 2.18, 3.85, 1.92, 0.52, fill=LIGHTER, line=LIGHT, text=chip, size=9.5, color=INK, bold=True, align=PP_ALIGN.CENTER, margin=0)
    add_box(slide, 4.82, 4.86, 7.25, 1.12, fill=WHITE, line=RED)
    add_text(slide, "LÍMITE DE VALIDEZ", 5.05, 5.05, 1.65, 0.25, size=9, color=RED, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "La separación es por estudio, no por paciente: el test compara configuraciones, pero no estima de forma independiente la generalización a sujetos nuevos.", 6.68, 5.01, 5.07, 0.64, size=10.5, color=INK, valign=MSO_ANCHOR.TOP)
    add_footer(slide, 7, "Fuente: outputs/qc/brats_gli_2024_qc_summary.json y manifiesto de particiones")
    set_notes(slide, "1:10", [
        "Destacar el control de calidad completo y las proporciones 70/15/15.",
        "Explicar la estratificación: origen, presencia de ET y volumen de WT.",
        "No ocultar el principal límite: el identificador disponible permitió separar estudios, pero no agrupar por paciente antes de entrenar.",
    ])

    # 08 — Pipeline
    slide = new("white")
    add_title(slide, "03 · Implementación", "Un flujo común de datos, predicción y evaluación")
    add_picture_contain(slide, FIGURES / "fig_pipeline_flujo.png", 2.12, 1.47, 9.20, 5.35, border=None)
    add_box(slide, 0.60, 1.77, 1.42, 1.13, fill=PALE, line=PALE, text="YAML\nversionados", size=13, color=ORANGE, bold=True, align=PP_ALIGN.CENTER)
    add_box(slide, 0.60, 3.12, 1.42, 1.13, fill=PALE, line=PALE, text="CLI\n5 comandos", size=13, color=ORANGE, bold=True, align=PP_ALIGN.CENTER)
    add_box(slide, 0.60, 4.47, 1.42, 1.13, fill=PALE, line=PALE, text="Artefactos\ntrazables", size=13, color=ORANGE, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, 8, "Fuente: Figura 1 de la memoria · implementación en tfm_brats/")
    set_notes(slide, "1:10", [
        "Recorrer el diagrama de izquierda a derecha: dataset, QC y splits; ruta MONAI y ruta nnU-Net; predicciones; evaluación común.",
        "Destacar la separación entre predict y evaluate, que permite recalcular métricas sin repetir inferencia.",
        "La reproducibilidad se apoya en configuraciones YAML, CLI, manifiestos y métricas versionadas.",
    ])

    # 09 — Fusion strategies
    slide = new("white")
    add_title(slide, "03 · Implementación", "Cuatro estrategias de fusión antes del mismo codificador")
    add_picture_contain(slide, FIGURES / "fig_arquitectura_fusion.png", 1.80, 1.45, 9.75, 5.45, border=None)
    add_box(slide, 0.55, 2.10, 1.30, 1.00, fill=WHITE, line=ORANGE, text="0\nparámetros", size=10.5, color=INK, bold=True, align=PP_ALIGN.CENTER)
    add_box(slide, 0.55, 3.30, 1.30, 1.00, fill=WHITE, line=ORANGE_2, text="+4\nparámetros", size=10.5, color=INK, bold=True, align=PP_ALIGN.CENTER)
    add_box(slide, 11.55, 2.10, 1.22, 1.00, fill=WHITE, line=ORANGE_3, text="+76\nparámetros", size=10.5, color=INK, bold=True, align=PP_ALIGN.CENTER)
    add_box(slide, 11.55, 3.30, 1.22, 1.00, fill=WHITE, line=ORANGE_4, text="+108\nparámetros", size=10.5, color=INK, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, 9, "Fuente: Figura 2 de la memoria · configuración final de FusionUNet")
    set_notes(slide, "1:30", [
        "Concatenación deja que la primera convolución aprenda filtros distintos, pero no expone un peso interpretable por modalidad.",
        "La ponderación global aprende cuatro escalares compartidos por todas las entradas.",
        "Las compuertas calculan estadísticos globales del parche, pasan por un MLP y aplican softmax para reponderar canales.",
        "No es atención espacial: el peso es constante dentro de cada parche o ventana.",
    ])

    # 10 — Training and metrics
    slide = new("split")
    add_title(slide, "04 · Evaluación", "Protocolo común: repetir, congelar y medir por región")
    steps = [
        ("01", "Entrenar", "15.000 pasos por semilla"),
        ("02", "Seleccionar", "mejor checkpoint con validación"),
        ("03", "Congelar", "test no interviene en la selección"),
        ("04", "Inferir", "ventana deslizante sobre 243 estudios"),
    ]
    for i, (num, head, sub) in enumerate(steps):
        y = 1.65 + i * 1.08
        add_circle(slide, 0.65, y, 0.55, num, size=9)
        add_text(slide, head, 1.42, y - 0.01, 2.0, 0.28, size=14, color=INK, bold=True, valign=MSO_ANCHOR.TOP)
        add_text(slide, sub, 3.18, y, 3.05, 0.31, size=10.5, color=MID, valign=MSO_ANCHOR.TOP)
        if i < 3:
            add_chevron(slide, 0.79, y + 0.65, 0.28, 0.30, LIGHT)
    add_text(slide, "MÉTRICAS", 7.15, 1.62, 2.0, 0.26, size=9, color=ORANGE, bold=True, valign=MSO_ANCHOR.TOP)
    add_metric_chip(slide, 7.12, 2.05, 2.48, "Dice ↑", "Solapamiento; 1 es coincidencia perfecta")
    add_metric_chip(slide, 9.88, 2.05, 2.48, "HD95 ↓", "Discrepancia de superficie en milímetros", fill=WHITE)
    add_text(slide, "ET · TC · WT", 7.18, 3.35, 5.10, 0.52, size=24, color=INK, bold=True, align=PP_ALIGN.CENTER)
    add_box(slide, 7.12, 4.15, 5.25, 1.00, fill=WHITE, line=ORANGE, text="3 semillas por configuración\nmedia ± desviación estándar poblacional", size=12, color=INK, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "Métrica principal de decisión: Dice medio de ET, TC y WT", 7.15, 5.50, 5.15, 0.55, size=11.5, color=MID, align=PP_ALIGN.CENTER)
    add_footer(slide, 10)
    set_notes(slide, "1:05", [
        "Explicar el orden para evitar fuga de información: entrenamiento, selección en validación, congelación y test.",
        "Dice es la métrica principal; HD95 complementa con información de distancia de superficies.",
        "Las tres semillas permiten ver estabilidad, aunque siguen siendo pocas para inferencia estadística sólida.",
    ])

    # 11 — Central result
    slide = new("white")
    add_title(slide, "05 · Resultados", "Resultado central: la fusión adaptativa no mejora de forma consistente")
    add_fusion_bar_chart(slide, 0.65, 1.55, 8.15, 4.95, fusion_rows)
    add_box(slide, 9.15, 1.82, 3.55, 1.28, fill=PALE, line=ORANGE)
    add_text(slide, "0,706", 9.45, 1.99, 1.28, 0.45, size=26, color=ORANGE, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "concat. ≈ global", 10.67, 2.08, 1.75, 0.35, size=12, color=INK, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "misma media y baja dispersión", 9.45, 2.53, 2.95, 0.27, size=9.5, color=MID, valign=MSO_ANCHOR.TOP)
    add_box(slide, 9.15, 3.38, 3.55, 1.52, fill=WHITE, line=RED)
    add_text(slide, "≈0,59", 9.45, 3.61, 1.22, 0.45, size=25, color=RED, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "adaptativas", 10.65, 3.68, 1.75, 0.35, size=12, color=INK, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "σ ≈ 0,17 por una corrida débil en cada variante", 9.45, 4.15, 2.90, 0.50, size=9.5, color=MID, valign=MSO_ANCHOR.TOP)
    add_box(slide, 9.15, 5.24, 3.55, 0.82, fill=ORANGE, line=ORANGE, text="Respuesta a la hipótesis: NO", size=14, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, 11, "Dice medio en test; barras = media de 3 semillas; error = desviación estándar")
    set_notes(slide, "1:35", [
        "Primero comparar concatenación y ponderación global: ambas alcanzan 0,706 con dispersión pequeña.",
        "Después mostrar las compuertas: la media baja a alrededor de 0,59 y la variabilidad aumenta mucho.",
        "El resultado no dice que toda fusión adaptativa falle; dice que estas compuertas ligeras no mejoran de forma consistente bajo este protocolo.",
    ])

    # 12 — Seed instability and qualitative example
    slide = new("white")
    add_title(slide, "05 · Resultados", "La diferencia está en la estabilidad entre semillas")
    labels = [
        ("Concat.", seeds["concat"], ORANGE),
        ("Global", seeds["global_weighted"], ORANGE_2),
        ("Adapt. media", seeds["adaptive_gating"], ORANGE_3),
        ("Adapt. media+desv.", seeds["adaptive_gating_meanstd"], ORANGE_4),
    ]
    for i, (label, vals, color) in enumerate(labels):
        y = 1.55 + i * 0.56
        add_text(slide, label, 0.62, y, 1.55, 0.28, size=9.5, color=INK, bold=True, valign=MSO_ANCHOR.TOP)
        for j, (seed, value) in enumerate(vals):
            x = 2.18 + j * 1.22
            fill = RED if value < 0.5 else color
            add_box(slide, x, y - 0.05, 1.02, 0.38, fill=fill, line=fill, text=f"{value:.3f}".replace(".", ","), size=9.2, color=WHITE, bold=True, align=PP_ALIGN.CENTER, margin=0)
        if i == 0:
            for j, (seed, _) in enumerate(vals):
                add_text(slide, seed[-2:], 2.18 + j * 1.22, 1.25, 1.02, 0.20, size=7.5, color=MID, align=PP_ALIGN.CENTER)
    add_text(slide, "Semilla (dos últimas cifras)", 2.14, 1.03, 3.47, 0.20, size=7.5, color=MID, align=PP_ALIGN.CENTER)
    add_picture_contain(slide, FIGURES / "fig_colapso_adaptive_gating.png", 5.88, 1.50, 6.82, 3.12, border=LIGHT)
    add_box(slide, 0.62, 4.18, 5.00, 1.58, fill=PALE, line=PALE)
    add_text(slide, "Diagnóstico exploratorio", 0.86, 4.43, 2.65, 0.30, size=14, color=ORANGE, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "En 40 volúmenes preliminares, los pesos variaron poco entre estudios. Pero el modelo calcula pesos sobre parches y ventanas: el diagnóstico no caracteriza los checkpoints finales ni identifica la causa.", 0.86, 4.85, 4.45, 0.66, size=10.5, color=INK, valign=MSO_ANCHOR.TOP)
    add_box(slide, 5.88, 4.92, 6.82, 0.84, fill=WHITE, line=RED, text="Una semilla débil por variante basta para invalidar una mejora «consistente»", size=12.5, color=RED, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, 12, "Ejemplo post hoc: BraTS-GLI-02273-100; no es una muestra representativa")
    set_notes(slide, "1:35", [
        "Leer por filas: las variantes estables están en torno a 0,70 en las tres semillas.",
        "Cada compuerta tiene dos ejecuciones competitivas y una caída a aproximadamente 0,35.",
        "La imagen ilustra una sobresegmentación concreta; no se usa como prueba independiente.",
        "Ser prudente con el diagnóstico de pesos: fue exploratorio, sobre volúmenes completos y puntos de control preliminares.",
    ])

    # 13 — Architectural context
    slide = new("white")
    add_title(slide, "05 · Resultados", "Contexto arquitectónico: hay margen más allá de la fusión temprana")
    add_architecture_bar_chart(slide, 0.62, 1.55, 9.55, 4.95, all_rows)
    add_box(slide, 10.42, 1.85, 2.32, 1.02, fill=NAVY, line=NAVY, text="nnU-Net\n0,829", size=16, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_box(slide, 10.42, 3.10, 2.32, 1.02, fill=ORANGE, line=ORANGE, text="Swin-UNETR\n0,752 ± 0,017", size=14, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_box(slide, 10.42, 4.42, 2.32, 1.20, fill=PALE, line=ORANGE)
    add_text(slide, "LECTURA", 10.64, 4.60, 1.50, 0.22, size=8.5, color=ORANGE, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "El margen no se agota con cuatro pesos en la entrada.", 10.64, 4.92, 1.78, 0.45, size=10, color=INK, bold=True, valign=MSO_ANCHOR.TOP)
    add_box(slide, 0.67, 6.45, 12.02, 0.42, fill=LIGHTER, line=LIGHTER, text="Comparación descriptiva, no ablación: nnU-Net usa su propio pipeline y las arquitecturas se ejecutaron en entornos distintos.", size=9.2, color=MID, align=PP_ALIGN.CENTER, margin=0)
    add_footer(slide, 13, "Fuente: outputs/evaluation/final_all_test.csv")
    set_notes(slide, "1:20", [
        "Presentar esta ordenación como contexto, no como comparación causal de arquitecturas.",
        "nnU-Net alcanza 0,829 con su pipeline auto-configurado y una única ejecución.",
        "Swin-UNETR es el mejor modelo MONAI, con 0,752, y da soporte a la dimensión Transformer-UNet del título.",
        "La brecha sugiere que optimización, capacidad y pipeline importan más que añadir una regla ligera de fusión temprana.",
    ])

    # 14 — Cost and reproducibility
    slide = new("split")
    add_title(slide, "06 · Contribución", "Ligereza paramétrica y trazabilidad experimental")
    add_text(slide, "COSTE DE LA FUSIÓN", 0.62, 1.58, 2.6, 0.25, size=9, color=ORANGE, bold=True, valign=MSO_ANCHOR.TOP)
    cost_cards = [
        ("+4", "global"),
        ("+76", "media"),
        ("+108", "media+desv."),
    ]
    for i, (value, label) in enumerate(cost_cards):
        x = 0.65 + i * 1.90
        add_box(slide, x, 2.02, 1.65, 1.20, fill=PALE, line=ORANGE)
        add_text(slide, value, x + 0.15, 2.18, 1.35, 0.44, size=24, color=ORANGE, bold=True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.TOP)
        add_text(slide, label, x + 0.15, 2.70, 1.35, 0.24, size=9.5, color=INK, bold=True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.TOP)
    add_text(slide, "sobre 1.190.358 parámetros de la red base", 0.68, 3.40, 5.28, 0.30, size=10.5, color=MID, align=PP_ALIGN.CENTER)
    add_box(slide, 0.65, 4.00, 5.52, 1.22, fill=WHITE, line=LIGHT)
    add_text(slide, "Tiempo MPS observado", 0.87, 4.20, 2.35, 0.28, size=12, color=INK, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "concat.: 4,99–5,00 h  |  ponderadas: 5,65–6,02 h", 0.87, 4.62, 4.90, 0.28, size=10.5, color=MID, valign=MSO_ANCHOR.TOP)
    add_text(slide, "No es un benchmark aislado; no atribuye el incremento solo al bloque.", 0.87, 4.94, 4.90, 0.22, size=8.5, color=RED, italic=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "REPRODUCIBILIDAD", 7.05, 1.58, 2.6, 0.25, size=9, color=ORANGE, bold=True, valign=MSO_ANCHOR.TOP)
    reps = [
        ("01", "Splits y manifiesto", "semilla y estratos versionados"),
        ("02", "Configuraciones YAML", "datos, modelos y entrenamiento"),
        ("03", "CLI reproducible", "qc · splits · train · predict · evaluate"),
        ("04", "Artefactos finales", "CSV y resúmenes JSON por ejecución"),
    ]
    for i, (num, head, sub) in enumerate(reps):
        y = 2.00 + i * 0.92
        add_circle(slide, 7.10, y, 0.48, num, size=8)
        add_text(slide, head, 7.75, y - 0.02, 2.12, 0.26, size=12.5, color=INK, bold=True, valign=MSO_ANCHOR.TOP)
        add_text(slide, sub, 9.92, y - 0.01, 2.55, 0.31, size=9.3, color=MID, valign=MSO_ANCHOR.TOP)
    add_box(slide, 7.08, 5.80, 5.36, 0.55, fill=ORANGE, line=ORANGE, text="12 ejecuciones de ablación rastreables de configuración a métrica", size=10.5, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, 14, "Código y artefactos: tfm_brats/, configs/ y outputs/")
    set_notes(slide, "1:10", [
        "Separar ligereza paramétrica de eficiencia completa: el número de parámetros sí está cuantificado; memoria e inferencia no de forma homogénea.",
        "Los tiempos de pared incorporan I/O y validación, por lo que no son un microbenchmark del bloque.",
        "La contribución reproducible incluye el pipeline, las particiones, las configuraciones y los artefactos finales.",
    ])

    # 15 — Conclusions
    slide = new("white")
    add_title(slide, "07 · Cierre", "Conclusión, límites y siguiente paso")
    add_box(slide, 8.25, 1.65, 4.05, 4.12, fill=ORANGE, line=ORANGE)
    add_text(slide, "RESPUESTA", 8.72, 2.18, 3.10, 0.28, size=10, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "NO", 8.72, 2.64, 3.10, 1.05, size=45, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_text(slide, "bajo el protocolo evaluado", 8.53, 3.82, 3.48, 0.38, size=12, color=WHITE, align=PP_ALIGN.CENTER)
    conclusions = [
        ("CONCLUSIÓN", "La concatenación es la opción más sencilla y una de las más estables; la ponderación global es equivalente."),
        ("LÍMITES", "3 semillas; 15.000 pasos; split por estudio; sin validación externa ni demostración de utilidad clínica."),
        ("TRABAJO FUTURO", "Agrupar por paciente, validar externamente y explorar fusión espacial o intermedia con más repeticiones."),
    ]
    for i, (head, body) in enumerate(conclusions):
        y = 1.70 + i * 1.45
        add_text(slide, head, 0.68, y, 1.60, 0.25, size=9, color=ORANGE, bold=True, valign=MSO_ANCHOR.TOP)
        add_text(slide, body, 2.08, y - 0.02, 5.40, 0.78, size=11.5, color=INK, bold=(i == 0), valign=MSO_ANCHOR.TOP)
        if i < 2:
            line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, inch(0.70), inch(y + 1.05), inch(7.55), inch(y + 1.05))
            line.line.color.rgb = LIGHT
    add_box(slide, 7.52, 6.07, 4.78, 0.70, fill=PALE, line=ORANGE, text="Un resultado negativo multisemilla es más informativo que una mejora aislada", size=11.5, color=ORANGE, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, 15)
    set_notes(slide, "1:30", [
        "Responder con precisión: no bajo estas configuraciones, semillas, presupuesto y partición.",
        "La ponderación global no aporta mejora; las compuertas adaptativas presentan inestabilidad.",
        "Cerrar con el valor metodológico: repetir cambió la interpretación de una aparente mejora en una semilla.",
        "Proponer como prioridad futura un split por paciente y validación externa antes de aumentar la complejidad del mecanismo.",
    ])

    # 16 — Q&A
    slide = new("final")
    add_box(slide, 0.58, 0.55, 7.25, 1.55, fill=WHITE, line=ORANGE)
    add_text(slide, "Gracias", 0.88, 0.76, 3.2, 0.50, size=30, color=INK, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "Preguntas y discusión", 0.90, 1.38, 4.5, 0.28, size=13, color=ORANGE, bold=True, valign=MSO_ANCHOR.TOP)
    add_text(slide, "Jesús Ferrón Rubio", 0.90, 1.73, 3.0, 0.22, size=9.5, color=MID, valign=MSO_ANCHOR.TOP)
    add_box(slide, 8.62, 5.78, 3.65, 0.64, fill=ORANGE, line=WHITE, text="Dice 0,706 · 12 ejecuciones · 1 conclusión", size=10.5, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_footer(slide, 16, light=True)
    set_notes(slide, "0:20", [
        "Finalizar y dejar visible la síntesis numérica durante las preguntas.",
        "Tener preparados los matices sobre split por paciente, métricas, nnU-Net y diagnóstico de la compuerta.",
    ])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUTPUT))
    print(OUTPUT)
    print(f"slides={len(prs.slides)}")


if __name__ == "__main__":
    build_deck()
