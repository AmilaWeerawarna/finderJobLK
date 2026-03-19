from __future__ import annotations

import re


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file using PyMuPDF (fitz).

    Works best for text-based PDFs. If the PDF is scanned (image-only),
    it may return very little text.
    """
    try:
        import fitz  # PyMuPDF
    except Exception as e:
        raise RuntimeError(
            "PyMuPDF is not installed. Add PyMuPDF to requirements.txt and install dependencies."
        ) from e

    doc = fitz.open(pdf_path)
    parts = []
    for page in doc:
        parts.append(page.get_text("text"))
    doc.close()

    text = "\n".join(parts)
    text = re.sub(r"\s+", " ", text).strip()
    return text
