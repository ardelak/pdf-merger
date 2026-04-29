import io
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register a TTF font so non-Latin (e.g. Cyrillic) characters render correctly.
# Arial ships with every Windows installation; change the path if needed.
_FONT_NAME = "Arial"
_FONT_PATH = Path("C:/Windows/Fonts/arial.ttf")
_FONT_BOLD_PATH = Path("C:/Windows/Fonts/arialbd.ttf")
_WATERMARK_FONT = f"{_FONT_NAME}Bold" if _FONT_BOLD_PATH.exists() else _FONT_NAME
if _FONT_BOLD_PATH.exists():
    pdfmetrics.registerFont(TTFont(_WATERMARK_FONT, str(_FONT_BOLD_PATH)))
elif _FONT_PATH.exists():
    pdfmetrics.registerFont(TTFont(_WATERMARK_FONT, str(_FONT_PATH)))
else:
    _WATERMARK_FONT = "Helvetica-Bold"  # Latin-only fallback


def create_watermark(
    filename: str,
    page_width: float,
    page_height: float,
    font_size: int,
    prefix: str,
    postfix: str,
    position: tuple[float, float] | None,
) -> object:
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
    c.setFont(_WATERMARK_FONT, font_size)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    label = f"{prefix}{filename}{postfix}"
    if position is not None:
        x, y = position
    else:
        margin = 15
        text_width = c.stringWidth(label, _WATERMARK_FONT, font_size)
        x = page_width - text_width - margin
        y = page_height - margin - font_size
    c.drawString(x, y, label)
    c.save()
    packet.seek(0)
    return PdfReader(packet).pages[0]


def merge_with_template(
    folder: Path,
    template_path: Path,
    output_folder: Path,
    font_size: int,
    prefix: str,
    postfix: str,
    position: tuple[float, float] | None,
) -> None:
    output_folder.mkdir(exist_ok=True)

    pdf_files = sorted(
        f for f in folder.glob("*.pdf")
        if f.resolve() != template_path.resolve()
    )

    if not pdf_files:
        print("No PDF files found (excluding template).")
        return

    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")

        template_reader = PdfReader(str(template_path))
        original_reader = PdfReader(str(pdf_file))
        writer = PdfWriter()

        for i, page in enumerate(template_reader.pages):
            if i == 0:
                w = float(page.mediabox.width)
                h = float(page.mediabox.height)
                watermark = create_watermark(pdf_file.stem, w, h, font_size, prefix, postfix, position)
                page.merge_page(watermark)
            writer.add_page(page)

        for page in original_reader.pages:
            writer.add_page(page)

        out_path = output_folder / f"merged_{pdf_file.name}"
        with open(out_path, "wb") as f:
            writer.write(f)
        print(f"  -> {out_path.name}")

    print(f"\nDone. {len(pdf_files)} file(s) written to '{output_folder}'.")


if __name__ == "__main__":
    FOLDER = Path(".")               # folder containing source PDFs
    TEMPLATE = Path("template.pdf")  # template file (must be in FOLDER or give full path)
    OUTPUT = Path("output")          # output subfolder

    # --- watermark settings ---
    FONT_SIZE = 20                   # watermark text size in points
    PREFIX = "Шифр: "            # string prepended to filename, e.g. "File: "
    POSTFIX = " (10 класс)"                     # string appended to filename, e.g. " (copy)"
    # Set to (x, y) in PDF points to fix the position, or None to auto-place top-right
    POSITION: tuple[float, float] | None = None

    if not TEMPLATE.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE.resolve()}")

    merge_with_template(FOLDER, TEMPLATE, OUTPUT, FONT_SIZE, PREFIX, POSTFIX, POSITION)
