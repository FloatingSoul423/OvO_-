"""Render the SRS via local Word and inspectable PDF contact sheets on Windows."""

from pathlib import Path

import pdfplumber
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
from win32com.client import DispatchEx


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/srs/OvO-SRS-V0.4.docx"
OUT = ROOT / ".local/srs_qa"
POPPLER = Path(r"C:\Users\songx\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pdf = OUT / "OvO-SRS-V0.4.pdf"
    app = DispatchEx("Word.Application")
    app.Visible = False
    app.DisplayAlerts = 0
    try:
        word = app.Documents.Open(str(SOURCE), ReadOnly=True)
        try:
            word.ExportAsFixedFormat(str(pdf), 17)
        finally:
            word.Close(False)
    finally:
        app.Quit()

    document = pdfplumber.open(pdf)
    card_count = 0
    sparse = []
    overflow = []
    for start in range(0, len(document.pages), 16):
        rendered = convert_from_path(str(pdf), dpi=72, first_page=start + 1, last_page=min(start + 16, len(document.pages)), poppler_path=str(POPPLER))
        group = []
        for offset, im in enumerate(rendered):
            page_no = start + offset + 1
            page = document.pages[page_no - 1]
            words = page.extract_words()
            if len(words) < 5:
                sparse.append(page_no)
            if any(w["x0"] < 12 or w["top"] < 12 or w["x1"] > page.width - 12 or w["bottom"] > page.height - 12 for w in words):
                overflow.append(page_no)
            im.thumbnail((245, 345))
            card = Image.new("RGB", (260, 375), "white")
            card.paste(im, ((260 - im.width) // 2, 4))
            ImageDraw.Draw(card).text((10, 354), f"Page {page_no}", fill="#333333")
            group.append(card)
            card_count += 1
        if start == 0 or start + 16 >= len(document.pages):
            for page_no in (1, 2, 3, 4, len(document.pages)):
                if start < page_no <= start + 16:
                    full = convert_from_path(str(pdf), dpi=140, first_page=page_no, last_page=page_no, poppler_path=str(POPPLER))[0]
                    full.save(OUT / f"page_{page_no:03d}.png")
        sheet = Image.new("RGB", (1040, 1500), "#e9ecef")
        for offset, card in enumerate(group):
            sheet.paste(card, ((offset % 4) * 260, (offset // 4) * 375))
        sheet.save(OUT / f"contact_{start // 16 + 1:02d}.png")
    print(f"pages={len(document.pages)}; sparse={sparse}; margin_overflow={overflow}; contacts={(card_count+15)//16}")


if __name__ == "__main__":
    main()
