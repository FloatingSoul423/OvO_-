from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/architecture/09-AI使用声明-可御风雪可燃冰.md'
OUTPUT = SOURCE.with_suffix('.docx')

def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    el = OxmlElement('w:shd'); el.set(qn('w:fill'), fill); tc_pr.append(el)

def font_run(run, size=10.5, bold=False, color=None):
    run.font.name = '等线'; run.font.size = Pt(size); run.bold = bold
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '等线')
    if color: run.font.color.rgb = RGBColor(*color)

doc = Document()
sec = doc.sections[0]
sec.top_margin = Cm(2.0); sec.bottom_margin = Cm(1.8)
sec.left_margin = Cm(2.2); sec.right_margin = Cm(2.2)
style = doc.styles['Normal']; style.font.name = '等线'; style.font.size = Pt(10.5)
style._element.rPr.rFonts.set(qn('w:eastAsia'), '等线')
style.paragraph_format.space_after = Pt(6)
lines = SOURCE.read_text(encoding='utf-8').splitlines()
i = 0
while i < len(lines):
    line = lines[i].strip()
    if not line: i += 1; continue
    if line.startswith('|'):
        rows=[]
        while i < len(lines) and lines[i].strip().startswith('|'):
            vals=[x.strip() for x in lines[i].strip().strip('|').split('|')]
            if not all(set(x) <= set('-: ') for x in vals): rows.append(vals)
            i += 1
        table=doc.add_table(rows=len(rows), cols=len(rows[0]))
        table.alignment=WD_TABLE_ALIGNMENT.CENTER; table.style='Table Grid'
        for r, vals in enumerate(rows):
            for c, val in enumerate(vals):
                cell=table.cell(r,c); cell.text=val.replace('`','').replace('**','')
                cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                if r==0: shade(cell,'DDE9E3')
                for p in cell.paragraphs:
                    p.paragraph_format.space_after=Pt(2)
                    for run in p.runs: font_run(run,8.6,r==0)
        doc.add_paragraph('')
        continue
    if line.startswith('# '):
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        font_run(p.add_run(line[2:]),19,True,(34,95,73))
        p.paragraph_format.space_after=Pt(14)
    elif line.startswith('## '):
        p=doc.add_paragraph(); font_run(p.add_run(line[3:]),13,True,(34,95,73))
        p.paragraph_format.space_before=Pt(10); p.paragraph_format.space_after=Pt(5)
        if line.startswith('## 3. '): p.paragraph_format.page_break_before = True
    elif line.startswith('> '):
        p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        font_run(p.add_run(line[2:]),9,False,(96,106,102))
    else:
        p=doc.add_paragraph()
        text=line.replace('**','').replace('`','')
        font_run(p.add_run(text),10.5)
    i += 1

footer=sec.footer.paragraphs[0]
footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
font_run(footer.add_run('03组 可御风雪可燃冰  ·  作业4 AI 使用声明  ·  V0.1'),8,False,(125,130,127))
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
doc.save(OUTPUT)
print(OUTPUT)
