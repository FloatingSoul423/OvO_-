"""Visual QA fallback on Windows when render_docx.py lacks LibreOffice."""

from pathlib import Path

from pdf2image import convert_from_path
from PIL import Image, ImageOps, ImageDraw
from win32com.client import DispatchEx


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / ".local/course_report_qa"
FILES = [
    ROOT / "docs/research/学术成果分享平台需求调研报告V1.0.docx",
    ROOT / "docs/research/调研依据与执行记录V1.0.docx",
    ROOT / "docs/research/学术成果分享平台现成调研统计报告.docx",
    ROOT / "docs/spec/学术成果分享平台核心规则SPEC初稿V0.1.docx",
]
POPPLER = Path(r"C:\Users\songx\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    app = DispatchEx("Word.Application")
    app.Visible = False
    app.DisplayAlerts = 0
    try:
        for index, source in enumerate(FILES, 1):
            pdf = OUTPUT / f"report_{index}.pdf"
            word = app.Documents.Open(str(source), ReadOnly=True)
            try:
                word.ExportAsFixedFormat(str(pdf), 17)
            finally:
                word.Close(False)
            pages = convert_from_path(str(pdf), dpi=110, poppler_path=str(POPPLER))
            for number, page in enumerate(pages, 1):
                page.save(OUTPUT / f"report_{index}_page_{number:02d}.png")
            thumbs = []
            for number, page in enumerate(pages, 1):
                im = page.convert("RGB")
                im.thumbnail((380, 540))
                card = Image.new("RGB", (400, 570), "white")
                card.paste(im, ((400 - im.width) // 2, 10))
                ImageDraw.Draw(card).text((12, 548), f"Page {number}", fill="#333333")
                thumbs.append(ImageOps.expand(card, border=1, fill="#bbbbbb"))
            columns = min(4, len(thumbs))
            rows = (len(thumbs) + columns - 1) // columns
            contact = Image.new("RGB", (columns * 402, rows * 572), "#f2f2f2")
            for item, thumb in enumerate(thumbs):
                contact.paste(thumb, ((item % columns) * 402, (item // columns) * 572))
            contact.save(OUTPUT / f"report_{index}_contact.png")
            print(f"{source.name}: {len(pages)} pages; contact sheet {OUTPUT / f'report_{index}_contact.png'}")
    finally:
        app.Quit()


if __name__ == "__main__":
    main()
