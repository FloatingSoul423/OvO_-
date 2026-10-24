"""Export the demand-analysis Markdown sources to polished Word documents."""

from __future__ import annotations

import re
from pathlib import Path

from PIL import Image
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "docs" / "analysis"
SOURCES = [
    ANALYSIS / "需求分析报告V1.0.md",
    ANALYSIS / "修改说明与版本记录表V1.0.md",
    ANALYSIS / "AI使用声明V1.0.md",
]


def clean(text: str) -> str:
    text = re.sub(r"\[([^]]+)]\(([^)]+)\)", r"\1", text)
    text = text.replace("**", "").replace("`", "")
    return text.strip()


def set_font(run, size: float | None = None, bold: bool | None = None, color: str | None = None) -> None:
    run.font.name = "Calibri"
    fonts = run._element.get_or_add_rPr().rFonts
    fonts.set(qn("w:eastAsia"), "宋体")
    fonts.set(qn("w:ascii"), "Calibri")
    fonts.set(qn("w:hAnsi"), "Calibri")
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def shade(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def borders(cell) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    node = tc_pr.first_child_found_in("w:tcBorders")
    if node is None:
        node = OxmlElement("w:tcBorders")
        tc_pr.append(node)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        item = OxmlElement(f"w:{edge}")
        item.set(qn("w:val"), "single")
        item.set(qn("w:sz"), "4")
        item.set(qn("w:color"), "D9D9D9")
        node.append(item)


def repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)


def no_split(row) -> None:
    row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))


def configure(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin, section.bottom_margin = Cm(2.0), Cm(1.8)
    section.left_margin, section.right_margin = Cm(2.2), Cm(2.0)
    section.header_distance, section.footer_distance = Cm(0.9), Cm(0.9)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(28, 35, 42)
    normal.paragraph_format.line_spacing = 1.35
    normal.paragraph_format.space_after = Pt(5)

    for idx, size in ((1, 16), (2, 13), (3, 11)):
        style = doc.styles[f"Heading {idx}"]
        style.font.name = "Microsoft YaHei"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.space_before = Pt(14 if idx == 1 else 9)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.keep_with_next = True

    title = doc.styles["Title"]
    title.font.name = "Microsoft YaHei"
    title._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    title.font.size = Pt(23)
    title.font.bold = True
    title.font.color.rgb = RGBColor(0, 0, 0)
    title.paragraph_format.space_after = Pt(12)
    ppr = title._element.get_or_add_pPr()
    for node in ppr.findall(qn("w:pBdr")):
        ppr.remove(node)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = footer.add_run("03组 可御风雪可燃冰　·　")
    set_font(r, 8, color="737B83")
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)


def add_table(doc: Document, rows: list[list[str]]) -> None:
    cols = max(len(row) for row in rows)
    table = doc.add_table(rows=0, cols=cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    for ridx, values in enumerate(rows):
        row = table.add_row()
        no_split(row)
        if ridx == 0:
            repeat_header(row)
        for cidx, cell in enumerate(row.cells):
            value = clean(values[cidx] if cidx < len(values) else "")
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            borders(cell)
            if ridx == 0:
                shade(cell, "244A69")
            elif ridx % 2 == 0:
                shade(cell, "F3F7FA")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2.5)
            p.paragraph_format.space_after = Pt(2.5)
            p.paragraph_format.line_spacing = 1.15
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if cidx == 0 else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(value)
            set_font(run, 8.3 if cols >= 5 else 8.8, bold=ridx == 0, color="FFFFFF" if ridx == 0 else "1C232A")
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_picture(doc: Document, source: Path, caption: str) -> None:
    with Image.open(source) as img:
        w, h = img.size
    # Keep the explanatory table and paragraph with each model on one page.
    max_w, max_h = 16.4, 13.2
    width_cm = max_w
    height_cm = width_cm * h / w
    if height_cm > max_h:
        height_cm = max_h
        width_cm = height_cm * w / h
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(source), width=Cm(width_cm), height=Cm(height_cm))
    cp = doc.add_paragraph(caption)
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_after = Pt(8)
    cp.paragraph_format.keep_with_next = True
    for run in cp.runs:
        set_font(run, 9, bold=True, color="3F4A54")


def parse_table(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    rows, i = [], start
    while i < len(lines) and lines[i].strip().startswith("|"):
        cells = [part.strip() for part in lines[i].strip().strip("|").split("|")]
        if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            rows.append(cells)
        i += 1
    return rows, i


def export(source: Path) -> Path:
    lines = source.read_text(encoding="utf-8").splitlines()
    title = clean(lines[0][2:])
    metadata = clean(next((line[1:].strip() for line in lines[1:] if line.startswith(">")), ""))
    doc = Document()
    configure(doc)

    cover = doc.add_paragraph(style="Title")
    cover.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cover.paragraph_format.space_before = Pt(105 if "报告" in title else 80)
    cover.add_run(title)
    metadata_display = metadata.replace("　子组：", "\n子组：")
    meta = doc.add_paragraph(metadata_display)
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.paragraph_format.space_before = Pt(28)
    meta.paragraph_format.line_spacing = 1.7
    for run in meta.runs:
        set_font(run, 11, color="4A525A")
    note = doc.add_paragraph("学术成果分享平台　需求分析阶段交付材料")
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    note.paragraph_format.space_before = Pt(55)
    for run in note.runs:
        set_font(run, 12, bold=True, color="244A69")
    doc.add_page_break()

    i = 1
    while i < len(lines):
        raw, line = lines[i], lines[i].strip()
        if not line or line.startswith(">"):
            i += 1
            continue
        if line.startswith("|"):
            rows, i = parse_table(lines, i)
            add_table(doc, rows)
            continue
        image = re.fullmatch(r"!\[([^]]+)]\(([^)]+)\)", line)
        if image:
            path = (source.parent / image.group(2)).resolve()
            add_picture(doc, path, f"图　{image.group(1)}")
            i += 1
            continue
        heading = re.match(r"^(#{2,4})\s+(.*)$", line)
        if heading:
            level = min(3, len(heading.group(1)) - 1)
            label = clean(heading.group(2))
            p = doc.add_paragraph(label, style=f"Heading {level}")
            # Only the first model starts on a fresh page.  Let later models
            # flow naturally so a full preceding page cannot produce a blank
            # page before the next heading.
            if level == 1 and (label.startswith("4 ") or label.startswith("附录")):
                p.paragraph_format.page_break_before = True
            i += 1
            continue
        if re.match(r"^\d+\.\s+", line):
            p = doc.add_paragraph(style="List Number")
            p.add_run(re.sub(r"^\d+\.\s+", "", clean(line)))
        elif line.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            p.add_run(clean(line[2:]))
        else:
            p = doc.add_paragraph(clean(line))
            p.paragraph_format.first_line_indent = Cm(0.74)
        i += 1

    # A table is followed by a spacer paragraph while parsing so later
    # headings do not stick to it.  If the document itself ends in a table,
    # remove only those trailing empty spacers; Word can otherwise push one
    # onto an otherwise blank final page.
    while doc.paragraphs and not doc.paragraphs[-1].text.strip():
        paragraph = doc.paragraphs[-1]._element
        paragraph.getparent().remove(paragraph)
    # Word requires a terminal paragraph after a final table.  Make it
    # intentionally tiny so the section mark stays on the preceding page.
    tail = doc.add_paragraph()
    tail.paragraph_format.space_before = Pt(0)
    tail.paragraph_format.space_after = Pt(0)
    tail.paragraph_format.line_spacing = Pt(1)
    set_font(tail.add_run(" "), 1)

    destination = source.with_suffix(".docx")
    doc.core_properties.title = title
    doc.core_properties.subject = "软件系统分析与设计课程作业3需求分析"
    doc.core_properties.author = "03组 可御风雪可燃冰"
    doc.save(destination)
    return destination


if __name__ == "__main__":
    for item in SOURCES:
        print(export(item))
