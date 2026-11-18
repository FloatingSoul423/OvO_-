"""Export the six Markdown coursework files to consistently styled DOCX."""
from pathlib import Path
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).parent
NAMES = [
    "01-数据库设计说明书-可御风雪可燃冰",
    "04-UI设计说明书-可御风雪可燃冰",
    "06-接口设计说明书-可御风雪可燃冰",
    "08-组内过程记录-可御风雪可燃冰",
    "09-AI使用声明-可御风雪可燃冰",
    "10-其他构件设计说明书-可御风雪可燃冰",
]

def font(style, name="Microsoft YaHei", size=10.5, bold=None):
    style.font.name = name
    style.font.size = Pt(size)
    style.font.color.rgb = RGBColor(0, 0, 0)
    if bold is not None: style.font.bold = bold
    style._element.rPr.rFonts.set(qn("w:eastAsia"), name)

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)

def borders(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    b = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        e = OxmlElement(f"w:{side}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "4")
        e.set(qn("w:color"), "D9D9D9")
        b.append(e)
    tcPr.append(b)

def inline(p, text):
    # Keep official reference URLs readable in Word; internal paths stay in Markdown.
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1（\2）", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    parts = re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text)
    for part in parts:
        if not part: continue
        if part.startswith("**") and part.endswith("**"):
            r = p.add_run(part[2:-2]); r.bold = True
        elif part.startswith("`") and part.endswith("`"):
            r = p.add_run(part[1:-1]); r.font.name = "Consolas"; r.font.size = Pt(8.5)
        else: p.add_run(part)

def make(name):
    src = ROOT / (name + ".md")
    lines = src.read_text(encoding="utf-8").splitlines()
    match = re.search(r"V\d+\.\d+", "\n".join(lines[:5]))
    version = match.group(0) if match else "初稿"
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Inches(8.5); sec.page_height = Inches(11)
    sec.top_margin = Inches(.8); sec.bottom_margin = Inches(.75)
    sec.left_margin = Inches(.85); sec.right_margin = Inches(.85)
    styles = doc.styles
    font(styles["Normal"], size=9.5)
    styles["Normal"].paragraph_format.space_after = Pt(6)
    styles["Normal"].paragraph_format.line_spacing = 1.25
    for sty, size in [("Title", 21), ("Heading 1", 15), ("Heading 2", 12), ("Heading 3", 10.5)]:
        font(styles[sty], size=size, bold=True)
        styles[sty].paragraph_format.space_before = Pt(12)
        styles[sty].paragraph_format.space_after = Pt(6)
    title_ppr = styles["Title"]._element.get_or_add_pPr()
    for border in title_ppr.findall(qn("w:pBdr")):
        title_ppr.remove(border)
    title = lines[0].removeprefix("# ").strip()
    doc.add_paragraph(title, "Title")
    doc.add_paragraph(f"03组 可御风雪可燃冰  ·  作业5构件设计  ·  {version} 初稿  ·  2026-11-18")
    doc.add_paragraph("成员与分工：待团队据实填写    签认：待联合评审")
    h1 = [x[3:] for x in lines if x.startswith("## ")]
    if h1:
        doc.add_heading("目录", level=1)
        for i, h in enumerate(h1, 1): doc.add_paragraph(f"{i}  {h}", style="Normal")
    doc.add_page_break()
    i = 1
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1; continue
        if line.startswith("<!--"):
            i += 1; continue
        if line.startswith("!["):
            m = re.match(r"!\[([^\]]+)\]\(([^)]+)\)", line)
            if m:
                path = ROOT / m.group(2)
                if path.exists() and path.suffix.lower() in (".png", ".jpg", ".jpeg"):
                    width = 5.1 if "ER核心视图" in path.name else 6.7
                    doc.add_picture(str(path), width=Inches(width))
                elif path.exists() and path.suffix.lower() == ".svg":
                    png = path.with_suffix(".png")
                    if png.exists(): doc.add_picture(str(png), width=Inches(6.7))
                    else: doc.add_paragraph(f"{m.group(1)}：见同目录导出图")
            i += 1; continue
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            rows.pop(1)
            cols = max(len(r) for r in rows)
            table = doc.add_table(rows=len(rows), cols=cols)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.autofit = True
            if cols == 4 and rows[0][0] == "字段":
                for col, width in zip(table.columns, (1.2, 1.05, 2.45, 1.9)):
                    col.width = Inches(width)
            header_trpr = table.rows[0]._tr.get_or_add_trPr()
            repeat = OxmlElement("w:tblHeader")
            repeat.set(qn("w:val"), "true")
            header_trpr.append(repeat)
            for ri, cells in enumerate(rows):
                for ci in range(cols):
                    cell = table.cell(ri, ci)
                    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                    borders(cell)
                    if ri == 0: shade(cell, "DCEAF5")
                    elif ri % 2 == 0: shade(cell, "F7FAFC")
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_after = Pt(2)
                    inline(p, cells[ci] if ci < len(cells) else "")
                    for run in p.runs:
                        run.font.size = Pt(8)
                        if ri == 0: run.bold = True
            doc.add_paragraph("")
            continue
        if line.startswith("### "): doc.add_heading(line[4:], level=2)
        elif line.startswith("## "): doc.add_heading(line[3:], level=1)
        elif line.startswith("# "): pass
        elif line.startswith("- "):
            p = doc.add_paragraph(style="List Bullet"); inline(p, line[2:])
        elif re.match(r"^\d+\. ", line):
            p = doc.add_paragraph(style="List Number"); inline(p, re.sub(r"^\d+\. ", "", line))
        else:
            p = doc.add_paragraph(); inline(p, line)
        i += 1
    footer = sec.footer.paragraphs[0]; footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("可御风雪可燃冰 · 构件设计初稿 · 2026-11-18")
    out = ROOT / (name + ".docx")
    doc.save(out)
    print(out)

for name in NAMES: make(name)
