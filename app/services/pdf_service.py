from pathlib import Path
from pypdf import PdfReader


def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_parts.append(page_text)

    return "\n".join(text_parts)