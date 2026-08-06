from __future__ import annotations

import argparse
import copy
import io
import os
import re
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_TYPES_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
WORDPROCESSING_DRAWING_NS = (
    "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
)


def qualified(namespace: str, name: str) -> str:
    return f"{{{namespace}}}{name}"


def register_namespaces(xml_bytes: bytes) -> None:
    seen: set[tuple[str, str]] = set()
    for _, namespace in ET.iterparse(io.BytesIO(xml_bytes), events=("start-ns",)):
        prefix, uri = namespace
        if namespace in seen or prefix == "xml":
            continue
        seen.add(namespace)
        ET.register_namespace(prefix, uri)


def parse_xml(xml_bytes: bytes) -> ET.Element:
    register_namespaces(xml_bytes)
    return ET.fromstring(xml_bytes)


def serialize_xml(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def parent_map(root: ET.Element) -> dict[ET.Element, ET.Element]:
    return {child: parent for parent in root.iter() for child in parent}


def unwrap_elements(root: ET.Element, tag: str) -> None:
    parents = parent_map(root)
    for element in list(root.iter(tag)):
        parent = parents.get(element)
        if parent is None:
            continue
        position = list(parent).index(element)
        for child in list(element):
            parent.insert(position, child)
            position += 1
        parent.remove(element)


def remove_elements(root: ET.Element, tags: set[str]) -> None:
    parents = parent_map(root)
    for element in list(root.iter()):
        if element.tag not in tags:
            continue
        parent = parents.get(element)
        if parent is not None:
            parent.remove(element)


def accept_revisions(root: ET.Element, preserve_comments: bool) -> None:
    unwrap_elements(root, qualified(WORD_NS, "ins"))
    unwrap_elements(root, qualified(WORD_NS, "moveTo"))
    if preserve_comments:
        parents = parent_map(root)
        for deletion in list(root.iter(qualified(WORD_NS, "del"))):
            parent = parents.get(deletion)
            if parent is None:
                continue
            position = list(parent).index(deletion)
            preserved: list[ET.Element] = []
            for element in deletion.iter():
                if element.tag in {
                    qualified(WORD_NS, "commentRangeStart"),
                    qualified(WORD_NS, "commentRangeEnd"),
                }:
                    preserved.append(copy.deepcopy(element))
                elif element.tag == qualified(WORD_NS, "r") and any(
                    child.tag == qualified(WORD_NS, "commentReference")
                    for child in element.iter()
                ):
                    preserved.append(copy.deepcopy(element))
            for element in preserved:
                parent.insert(position, element)
                position += 1
    remove_elements(
        root,
        {
            qualified(WORD_NS, "del"),
            qualified(WORD_NS, "moveFrom"),
            qualified(WORD_NS, "pPrChange"),
            qualified(WORD_NS, "rPrChange"),
            qualified(WORD_NS, "tblPrChange"),
            qualified(WORD_NS, "tblGridChange"),
            qualified(WORD_NS, "trPrChange"),
            qualified(WORD_NS, "tcPrChange"),
            qualified(WORD_NS, "sectPrChange"),
        },
    )


def remove_comment_markup(root: ET.Element) -> None:
    marker_tags = {
        qualified(WORD_NS, "commentRangeStart"),
        qualified(WORD_NS, "commentRangeEnd"),
        qualified(WORD_NS, "commentReference"),
    }
    remove_elements(root, marker_tags)
    parents = parent_map(root)
    for run in list(root.iter(qualified(WORD_NS, "r"))):
        if len(run) != 0:
            continue
        parent = parents.get(run)
        if parent is not None:
            parent.remove(run)


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(
        node.text or "" for node in paragraph.iter(qualified(WORD_NS, "t"))
    )


def paragraph_style(paragraph: ET.Element) -> str:
    style = paragraph.find(
        f"./{qualified(WORD_NS, 'pPr')}/{qualified(WORD_NS, 'pStyle')}"
    )
    return style.get(qualified(WORD_NS, "val"), "") if style is not None else ""


def text_nodes(paragraph: ET.Element) -> list[ET.Element]:
    return list(paragraph.iter(qualified(WORD_NS, "t")))


def replace_text(paragraph: ET.Element, old: str, new: str) -> int:
    replacements = 0
    while True:
        nodes = text_nodes(paragraph)
        combined = "".join(node.text or "" for node in nodes)
        start = combined.find(old)
        if start < 0:
            return replacements
        end = start + len(old)
        offsets: list[tuple[ET.Element, int, int]] = []
        cursor = 0
        for node in nodes:
            node_text = node.text or ""
            offsets.append((node, cursor, cursor + len(node_text)))
            cursor += len(node_text)
        start_entry = next(entry for entry in offsets if entry[2] > start)
        end_entry = next(entry for entry in offsets if entry[2] >= end)
        start_node, start_from, _ = start_entry
        end_node, end_from, _ = end_entry
        start_local = start - start_from
        end_local = end - end_from
        if start_node is end_node:
            current = start_node.text or ""
            start_node.text = current[:start_local] + new + current[end_local:]
        else:
            start_node.text = (start_node.text or "")[:start_local] + new
            end_node.text = (end_node.text or "")[end_local:]
            clearing = False
            for node in nodes:
                if node is start_node:
                    clearing = True
                    continue
                if node is end_node:
                    break
                if clearing:
                    node.text = ""
        replacements += 1


def set_paragraph_text(paragraph: ET.Element, text: str) -> None:
    paragraph_properties = paragraph.find(qualified(WORD_NS, "pPr"))
    for child in list(paragraph):
        if child is not paragraph_properties:
            paragraph.remove(child)
    run = ET.SubElement(paragraph, qualified(WORD_NS, "r"))
    text_element = ET.SubElement(run, qualified(WORD_NS, "t"))
    if text.startswith(" ") or text.endswith(" "):
        text_element.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    text_element.text = text


def clone_paragraph_with_text(paragraph: ET.Element, text: str) -> ET.Element:
    cloned = copy.deepcopy(paragraph)
    set_paragraph_text(cloned, text)
    return cloned


def direct_body_paragraphs(body: ET.Element) -> list[ET.Element]:
    return [child for child in body if child.tag == qualified(WORD_NS, "p")]


def find_paragraph(body: ET.Element, prefix: str) -> ET.Element:
    for paragraph in direct_body_paragraphs(body):
        if paragraph_text(paragraph).startswith(prefix):
            return paragraph
    raise ValueError(f"Paragraph not found: {prefix}")


def find_any_paragraph(root: ET.Element, prefix: str) -> ET.Element:
    for paragraph in root.iter(qualified(WORD_NS, "p")):
        if paragraph_text(paragraph).startswith(prefix):
            return paragraph
    raise ValueError(f"Paragraph not found: {prefix}")


def remove_paragraph(body: ET.Element, paragraph: ET.Element) -> None:
    body.remove(paragraph)


def insert_after(body: ET.Element, reference: ET.Element, elements: list[ET.Element]) -> None:
    position = list(body).index(reference) + 1
    for element in elements:
        body.insert(position, element)
        position += 1


def apply_content_corrections(root: ET.Element, preserve_comments: bool) -> None:
    body = root.find(qualified(WORD_NS, "body"))
    if body is None:
        raise ValueError("Document body not found")

    replace_text(
        find_any_paragraph(root, "Cardinale Villarreal"),
        "Jesus Gil Ruiz",
        "Jesús Gil Ruiz",
    )

    introduction_heading = find_paragraph(body, "1. Introducción")
    first_context = find_paragraph(body, "La resonancia magnética")
    if not preserve_comments:
        body_children = list(body)
        start = body_children.index(introduction_heading)
        end = body_children.index(first_context)
        for child in body_children[start + 1 : end]:
            if child.tag == qualified(WORD_NS, "p") and not paragraph_text(child).strip():
                body.remove(child)

    summary_paragraph = find_paragraph(body, "En resumen, la segmentación tridimensional")
    if preserve_comments:
        summary_target = find_paragraph(body, "La ponderación global se incluyó")
        body.remove(summary_paragraph)
        insert_after(body, summary_target, [summary_paragraph])
    else:
        remove_paragraph(body, summary_paragraph)

    first_region_definition = find_paragraph(body, "La evaluación de los gliomas")
    replace_text(
        first_region_definition,
        "el tumor realzante (ET), el núcleo tumoral (TC) y el tumor completo (WT)",
        "el tumor realzante, el núcleo tumoral y el tumor completo",
    )

    for paragraph in direct_body_paragraphs(body):
        if paragraph_style(paragraph).startswith("Ttulo1") and paragraph_text(paragraph).startswith(
            "2."
        ):
            chapter_two_heading = paragraph
            break
    else:
        raise ValueError("Chapter 2 heading not found")

    introduction_children = list(body)[
        list(body).index(introduction_heading) : list(body).index(chapter_two_heading)
    ]
    intro_replacements = {
        "segmentación 3D de ET, TC y WT": (
            "segmentación 3D del tumor realzante, del núcleo tumoral y del tumor completo"
        ),
        "para ET, TC y WT": (
            "para el tumor realzante, el núcleo tumoral y el tumor completo"
        ),
        "las regiones ET, TC y WT": (
            "las regiones correspondientes al tumor realzante, al núcleo tumoral y al tumor completo"
        ),
    }
    for child in introduction_children:
        if child.tag != qualified(WORD_NS, "p"):
            continue
        for old, new in intro_replacements.items():
            replace_text(child, old, new)

    heading_replacements = {
        "1.1. Planteamiento del problema": "1.1. Planteamiento del problema",
        "1.2. Objetivos": "1.2. Objetivos",
        "1.3. Organización del documento": "1.3. Organización del documento",
    }
    for expected in heading_replacements.values():
        find_paragraph(body, expected)

    organization = find_paragraph(body, "A continuación, el documento se organiza")
    set_paragraph_text(
        organization,
        "El documento se organiza en seis capítulos. Tras esta introducción, el Capítulo 2 presenta "
        "el marco teórico, el estado del arte y el marco tecnológico; el Capítulo 3 describe la "
        "metodología y el diseño experimental; el Capítulo 4 detalla el desarrollo y la "
        "implementación; el Capítulo 5 expone y analiza los resultados; y el Capítulo 6 recoge las "
        "conclusiones, las limitaciones y las líneas futuras. Finalmente, el Apéndice A detalla los "
        "elementos necesarios para reproducir los experimentos, incluidas las versiones, las "
        "configuraciones, los comandos y los artefactos del proyecto.",
    )
    redundant_organization = find_paragraph(body, "Los capítulos 3 y 4 separan")
    remove_paragraph(body, redundant_organization)

    set_paragraph_text(
        chapter_two_heading,
        "2. Marco teórico, estado del arte y marco tecnológico",
    )

    technology_placeholder = find_paragraph(body, "Describir qué es MONAI")
    technology_paragraphs = [
        (
            "MONAI (Medical Open Network for AI) es un marco de código abierto especializado en "
            "inteligencia artificial para imagen médica y construido sobre PyTorch. Proporciona "
            "componentes reutilizables para cargar y transformar imágenes, definir redes y funciones "
            "de pérdida, entrenar modelos y realizar inferencia sobre volúmenes de gran tamaño "
            "(Cardoso et al., 2022). Su diseño modular permite mantener una interfaz común para "
            "arquitecturas diferentes sin ocultar las decisiones experimentales del proyecto."
        ),
        (
            "En el sistema propio, MONAI aporta la lectura de volúmenes NIfTI multicanal, las "
            "transformaciones 3D, las implementaciones de Residual U-Net, Attention U-Net y "
            "Swin-UNETR, y la inferencia por ventanas deslizantes. PyTorch proporciona los tensores, "
            "la diferenciación automática y la ejecución sobre los dispositivos disponibles. El "
            "bucle de entrenamiento se implementó de forma explícita para controlar el presupuesto "
            "por pasos, la precisión mixta, la validación, los puntos de control y el registro de "
            "métricas. nnU-Net se mantuvo como herramienta externa porque su planificación y "
            "preprocesamiento auto-configurables forman parte del método comparado."
        ),
        (
            "Las ejecuciones se repartieron entre un ordenador personal con Apple M4 Pro, mediante "
            "Metal Performance Shaders (MPS), y Google Colab con una GPU NVIDIA A100 y CUDA. Git y "
            "GitHub se utilizaron para versionar el código, las configuraciones YAML, las particiones "
            "y la documentación; los datos clínicos y los artefactos pesados permanecieron fuera del "
            "repositorio. Esta separación entre código, configuración, datos y resultados sustenta "
            "la trazabilidad descrita en el Apéndice A."
        ),
    ]
    set_paragraph_text(technology_placeholder, technology_paragraphs[0])
    insert_after(
        body,
        technology_placeholder,
        [
            clone_paragraph_with_text(technology_placeholder, text)
            for text in technology_paragraphs[1:]
        ],
    )

    for paragraph in direct_body_paragraphs(body):
        text = paragraph_text(paragraph)
        if text == "3.2. Descripción general de las fases":
            set_paragraph_text(paragraph, "3.1. Descripción general de las fases")
        elif text == "3.3. Correspondencia entre metodología y desarrollo":
            set_paragraph_text(paragraph, "3.2. Correspondencia entre metodología y desarrollo")
        elif text == "3.4. Cronograma":
            set_paragraph_text(paragraph, "3.3. Cronograma")

    methodology_summary = find_paragraph(body, "La Tabla 3 resume")
    set_paragraph_text(
        methodology_summary,
        "La Tabla 3 sintetiza la finalidad y las actividades principales de las cinco fases.",
    )

    quality_control = find_paragraph(body, "Antes de entrenar se ejecutó el subcomando qc")
    replace_text(
        quality_control,
        "los volúmenes de ET, TC y WT",
        "los volúmenes correspondientes al tumor realzante (ET), al núcleo tumoral (TC) y al tumor completo (WT)",
    )

    split_paragraph = find_paragraph(body, "La partición se generó con tfm_brats/splits.py")
    replace_text(
        split_paragraph,
        "La Tabla 6 muestra ....",
        "La Tabla 6 resume el número de estudios, la proporción y el uso asignado a cada partición.",
    )

    compute_environment = find_paragraph(body, "La asignación de hardware")
    replace_text(
        compute_environment,
        "En MPS,",
        "En Metal Performance Shaders (MPS),",
    )


def remove_empty_methodology_heading(root: ET.Element) -> None:
    body = root.find(qualified(WORD_NS, "body"))
    if body is None:
        return
    methodology = next(
        paragraph
        for paragraph in direct_body_paragraphs(body)
        if paragraph_style(paragraph).startswith("Ttulo1")
        and paragraph_text(paragraph) == "3. Metodología"
    )
    phase_heading = next(
        paragraph
        for paragraph in direct_body_paragraphs(body)
        if paragraph_style(paragraph).startswith("Ttulo2")
        and paragraph_text(paragraph) == "3.1. Descripción general de las fases"
    )
    children = list(body)
    start = children.index(methodology)
    end = children.index(phase_heading)
    for child in children[start + 1 : end]:
        if (
            child.tag == qualified(WORD_NS, "p")
            and paragraph_style(child).startswith("Ttulo2")
            and not paragraph_text(child).strip()
        ):
            body.remove(child)


def add_paragraph_property(paragraph: ET.Element, name: str) -> None:
    paragraph_properties = paragraph.find(qualified(WORD_NS, "pPr"))
    if paragraph_properties is None:
        paragraph_properties = ET.Element(qualified(WORD_NS, "pPr"))
        paragraph.insert(0, paragraph_properties)
    if paragraph_properties.find(qualified(WORD_NS, name)) is None:
        ET.SubElement(paragraph_properties, qualified(WORD_NS, name))


def set_paragraph_alignment(paragraph: ET.Element, value: str) -> None:
    paragraph_properties = paragraph.find(qualified(WORD_NS, "pPr"))
    if paragraph_properties is None:
        paragraph_properties = ET.Element(qualified(WORD_NS, "pPr"))
        paragraph.insert(0, paragraph_properties)
    alignment = paragraph_properties.find(qualified(WORD_NS, "jc"))
    if alignment is None:
        alignment = ET.SubElement(paragraph_properties, qualified(WORD_NS, "jc"))
    alignment.set(qualified(WORD_NS, "val"), value)


def math_text_run(text: str) -> ET.Element:
    run = ET.Element(qualified(WORD_NS, "r"))
    run_properties = ET.SubElement(run, qualified(WORD_NS, "rPr"))
    fonts = ET.SubElement(run_properties, qualified(WORD_NS, "rFonts"))
    for attribute in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(qualified(WORD_NS, attribute), "Cambria Math")
    text_element = ET.SubElement(run, qualified(WORD_NS, "t"))
    text_element.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    text_element.text = text
    return run


def convert_math_to_visible_text(root: ET.Element, preserve_comments: bool) -> None:
    replacements = {
        "M": "M",
        "F": "ℱ",
        "x1,…,xM": "x₁, …, x_M",
        "x=[x1;…;xM]": "x = [x₁; …; x_M]",
        "α=softmax(θ)": "α = softmax(θ)",
        "xm=Mαmxm.": "x̃ₘ = M αₘ xₘ.",
        "α(x)=softmax(g(ϕ(x)))": "α(x) = softmax(g(ϕ(x)))",
        "ϕ": "ϕ",
        "g": "g",
        "r": "r",
        "Pr": "Pᵣ",
        "Gr": "Gᵣ",
        "Dice(Pr,Gr)=2|Pr∩Gr||Pr|+|Gr|.": (
            "Dice(Pᵣ, Gᵣ) = 2|Pᵣ ∩ Gᵣ| / (|Pᵣ| + |Gᵣ|)."
        ),
        "∂Pr": "∂Pᵣ",
        "∂Gr": "∂Gᵣ",
        "d(a,S)=mins∈Sa-s2": "d(a, S) = min{‖a − s‖₂ : s ∈ S}",
        "HD95(Pr,Gr)=Q0.95\u200b{d(p,∂Gr):p∈∂Pr}∪{d(g,∂Pr):g∈∂Gr},": (
            "HD95(Pᵣ, Gᵣ) = Q₀.₉₅({d(p, ∂Gᵣ) : p ∈ ∂Pᵣ} ∪ "
            "{d(g, ∂Pᵣ) : g ∈ ∂Gᵣ}),"
        ),
        "Q0.95": "Q₀.₉₅",
    }

    parents = parent_map(root)
    for math in list(root.iter(qualified(MATH_NS, "oMath"))):
        raw_text = "".join(
            element.text or ""
            for element in math.iter(qualified(MATH_NS, "t"))
        )
        if raw_text not in replacements:
            raise ValueError(f"Unknown equation: {raw_text}")
        parent = parents.get(math)
        if parent is None:
            continue
        if parent.tag == qualified(MATH_NS, "oMathPara"):
            paragraph = parents[parent]
            position = list(paragraph).index(parent)
            paragraph.remove(parent)
            paragraph.insert(position, math_text_run(replacements[raw_text]))
            set_paragraph_alignment(paragraph, "center")
        else:
            position = list(parent).index(math)
            parent.remove(math)
            parent.insert(position, math_text_run(replacements[raw_text]))

    body = root.find(qualified(WORD_NS, "body"))
    if body is None:
        raise ValueError("Document body not found")
    residual_intro = find_paragraph(body, "Las redes profundas pueden resultar difíciles")
    children = list(body)
    position = children.index(residual_intro)
    following = children[position + 1]
    if following.tag == qualified(WORD_NS, "p") and not paragraph_text(following).strip():
        equation_paragraph = following
    else:
        equation_paragraph = clone_paragraph_with_text(residual_intro, "")
        body.insert(position + 1, equation_paragraph)
    if preserve_comments:
        insertion_position = 1 if equation_paragraph.find(qualified(WORD_NS, "pPr")) is not None else 0
        equation_paragraph.insert(insertion_position, math_text_run("y = ℱ(x; θ) + x,"))
    else:
        set_paragraph_text(equation_paragraph, "y = ℱ(x; θ) + x,")
    set_paragraph_alignment(equation_paragraph, "center")


def add_row_property(row: ET.Element, name: str) -> None:
    row_properties = row.find(qualified(WORD_NS, "trPr"))
    if row_properties is None:
        row_properties = ET.Element(qualified(WORD_NS, "trPr"))
        row.insert(0, row_properties)
    if row_properties.find(qualified(WORD_NS, name)) is None:
        ET.SubElement(row_properties, qualified(WORD_NS, name))


def move_table_captions_and_keep_content(root: ET.Element) -> None:
    body = root.find(qualified(WORD_NS, "body"))
    if body is None:
        raise ValueError("Document body not found")
    for table in list(body.findall(qualified(WORD_NS, "tbl"))):
        children = list(body)
        table_index = children.index(table)
        if table_index + 1 >= len(children):
            continue
        caption = children[table_index + 1]
        if not (
            caption.tag == qualified(WORD_NS, "p")
            and paragraph_text(caption).startswith("Tabla ")
        ):
            continue
        body.remove(caption)
        body.insert(table_index, caption)
        add_paragraph_property(caption, "keepNext")
        add_paragraph_property(caption, "keepLines")

        rows = table.findall(qualified(WORD_NS, "tr"))
        for row in rows:
            add_row_property(row, "cantSplit")
        if rows:
            add_row_property(rows[0], "tblHeader")
        if len(rows) <= 8:
            table_paragraphs = list(table.iter(qualified(WORD_NS, "p")))
            for paragraph in table_paragraphs[:-1]:
                add_paragraph_property(paragraph, "keepNext")
        elif rows:
            for paragraph in rows[0].iter(qualified(WORD_NS, "p")):
                add_paragraph_property(paragraph, "keepNext")

    children = list(body)
    for index, child in enumerate(children[:-1]):
        if child.tag != qualified(WORD_NS, "p"):
            continue
        has_drawing = any(
            element.tag
            in {
                qualified(WORDPROCESSING_DRAWING_NS, "inline"),
                qualified(WORDPROCESSING_DRAWING_NS, "anchor"),
            }
            for element in child.iter()
        )
        if not has_drawing:
            continue
        next_child = children[index + 1]
        if (
            next_child.tag == qualified(WORD_NS, "p")
            and paragraph_text(next_child).startswith("Figura ")
        ):
            add_paragraph_property(child, "keepNext")
            add_paragraph_property(next_child, "keepLines")


def compact_cover(root: ET.Element) -> None:
    body = root.find(qualified(WORD_NS, "body"))
    if body is None:
        return
    children = list(body)
    date_paragraph = next(
        child
        for child in children
        if child.tag == qualified(WORD_NS, "p")
        and paragraph_text(child).startswith("Fecha:")
    )
    first_table = next(child for child in children if child.tag == qualified(WORD_NS, "tbl"))
    children = list(body)
    start = children.index(date_paragraph)
    end = children.index(first_table)
    empty_paragraphs = [
        child
        for child in children[start + 1 : end]
        if child.tag == qualified(WORD_NS, "p") and not paragraph_text(child).strip()
    ]
    for paragraph in empty_paragraphs[:-4]:
        body.remove(paragraph)


def prepare_fields_and_settings(parts: dict[str, bytes], root: ET.Element) -> None:
    for field_character in root.iter(qualified(WORD_NS, "fldChar")):
        if field_character.get(qualified(WORD_NS, "fldCharType")) == "begin":
            field_character.set(qualified(WORD_NS, "dirty"), "true")

    settings_name = "word/settings.xml"
    settings = parse_xml(parts[settings_name])
    remove_elements(settings, {qualified(WORD_NS, "trackRevisions")})
    update_fields = settings.find(qualified(WORD_NS, "updateFields"))
    if update_fields is None:
        update_fields = ET.SubElement(settings, qualified(WORD_NS, "updateFields"))
    update_fields.set(qualified(WORD_NS, "val"), "true")
    parts[settings_name] = serialize_xml(settings)


def remove_comment_parts(parts: dict[str, bytes]) -> None:
    removed_parts = {
        "word/comments.xml",
        "word/commentsIds.xml",
        "word/commentsExtended.xml",
        "word/commentsExtensible.xml",
        "word/people.xml",
    }
    for part in removed_parts:
        parts.pop(part, None)

    relationships_name = "word/_rels/document.xml.rels"
    relationships = parse_xml(parts[relationships_name])
    for relationship in list(relationships):
        relationship_type = relationship.get("Type", "")
        if "comments" in relationship_type or relationship_type.endswith("/people"):
            relationships.remove(relationship)
    parts[relationships_name] = serialize_xml(relationships)

    content_types_name = "[Content_Types].xml"
    content_types = parse_xml(parts[content_types_name])
    removed_names = {f"/{part}" for part in removed_parts}
    for override in list(content_types):
        if override.get("PartName") in removed_names:
            content_types.remove(override)
    parts[content_types_name] = serialize_xml(content_types)


def mark_comments_resolved(parts: dict[str, bytes]) -> None:
    comments_extended_name = "word/commentsExtended.xml"
    comments_extended = parse_xml(parts[comments_extended_name])
    for comment in list(comments_extended):
        done_attribute = next(
            (name for name in comment.attrib if name.endswith("}done")),
            None,
        )
        if done_attribute is None:
            namespace = comment.tag.split("}")[0].removeprefix("{")
            done_attribute = qualified(namespace, "done")
        comment.set(done_attribute, "1")
    parts[comments_extended_name] = serialize_xml(comments_extended)


def validate_document(parts: dict[str, bytes], preserve_comments: bool) -> None:
    for name, contents in parts.items():
        if name.endswith(".xml") or name.endswith(".rels"):
            ET.fromstring(contents)
    document = ET.fromstring(parts["word/document.xml"])
    unresolved = []
    for paragraph in document.iter(qualified(WORD_NS, "p")):
        text = paragraph_text(paragraph)
        if re.search(r"COMPLETAR|ACOMODAR|Describir qué es MONAI|\.\.\.\.", text):
            unresolved.append(text)
    if unresolved:
        raise ValueError(f"Unresolved placeholders: {unresolved}")
    forbidden_tags = {
        qualified(WORD_NS, "ins"),
        qualified(WORD_NS, "del"),
    }
    if not preserve_comments:
        forbidden_tags.update(
            {
                qualified(WORD_NS, "commentRangeStart"),
                qualified(WORD_NS, "commentRangeEnd"),
                qualified(WORD_NS, "commentReference"),
            }
        )
    if any(element.tag in forbidden_tags for element in document.iter()):
        raise ValueError("Tracked changes or comments remain in document.xml")


def write_docx(parts: dict[str, bytes], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=output_path.parent, suffix=".docx", delete=False
    ) as temporary_file:
        temporary_path = Path(temporary_file.name)
    try:
        with zipfile.ZipFile(
            temporary_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as archive:
            for name, contents in parts.items():
                archive.writestr(name, contents)
        os.replace(temporary_path, output_path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def resolve_document(
    input_path: Path, output_path: Path, preserve_comments: bool = False
) -> None:
    with zipfile.ZipFile(input_path) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}

    document = parse_xml(parts["word/document.xml"])
    accept_revisions(document, preserve_comments)
    if not preserve_comments:
        remove_comment_markup(document)
    apply_content_corrections(document, preserve_comments)
    remove_empty_methodology_heading(document)
    convert_math_to_visible_text(document, preserve_comments)
    compact_cover(document)
    move_table_captions_and_keep_content(document)
    prepare_fields_and_settings(parts, document)
    parts["word/document.xml"] = serialize_xml(document)
    if preserve_comments:
        mark_comments_resolved(parts)
    else:
        remove_comment_parts(parts)
    validate_document(parts, preserve_comments)
    write_docx(parts, output_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--preserve-comments", action="store_true")
    arguments = parser.parse_args()
    resolve_document(
        arguments.input,
        arguments.output,
        preserve_comments=arguments.preserve_comments,
    )


if __name__ == "__main__":
    main()
