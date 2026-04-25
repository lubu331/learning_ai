from pathlib import Path
import base64
import fitz
from pypdf import PdfReader


def extract_pdf_text(pdf_path: Path) -> str:
    """
    First tries normal PDF text extraction.
    If the PDF is image-based/scanned, returns empty text.
    """
    reader = PdfReader(str(pdf_path))
    text_parts = []

    for page in reader.pages:
        text_parts.append(page.extract_text() or "")

    return "\n".join(text_parts).strip()


def pdf_to_images_base64(pdf_path: Path, max_pages: int = 3) -> list[str]:
    """
    Converts image-based PDF pages to base64 PNG images for Ollama vision models.
    """
    doc = fitz.open(str(pdf_path))
    images = []

    for page_index in range(min(len(doc), max_pages)):
        page = doc[page_index]
        pix = page.get_pixmap(dpi=180)
        img_bytes = pix.tobytes("png")
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        images.append(img_b64)

    return images