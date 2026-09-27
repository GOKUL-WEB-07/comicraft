"""Export the comic as a readable PDF with one panel per page."""

from pathlib import Path
from uuid import uuid4

from fpdf import FPDF

EXPORTS_DIR = Path(__file__).resolve().parents[1] / "static" / "exports"


def _safe(text: str) -> str:
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _paragraph(pdf: FPDF, label: str, value: str):
    if not value:
        return
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 6, _safe(label))
    pdf.set_font("Helvetica", "", 11)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 6, _safe(value))
    pdf.ln(3)


def save_comic_pdf(comic_title: str, summary: str, layout: list[dict]) -> str:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    name = f"comic-{uuid4().hex}.pdf"
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.set_margins(18, 18, 18)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.multi_cell(0, 14, "ComicCraft")
    pdf.set_font("Helvetica", "B", 19)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 11, _safe(comic_title))
    pdf.ln(5)
    _paragraph(pdf, "The story", summary)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 8, "A five-panel comic created with ComicCraft")

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 10, _safe(f"Panel {panel['panel_number']}: {panel['title']}"))
        pdf.ln(3)
        image_y = pdf.get_y()
        # The square illustration fits inside a landscape-width panel on A4.
        pdf.image(str(panel["image_path"]), x=31, y=image_y, w=148, h=148)
        pdf.set_y(image_y + 154)
        _paragraph(pdf, "Scene", panel["scene_description"])
        _paragraph(pdf, "Narration", panel["narration"])
        _paragraph(pdf, "Dialogue", panel["dialogue"])
    pdf.output(str(EXPORTS_DIR / name))
    return f"/static/exports/{name}"
