"""Local OCR fallback for image-only PDF pages."""

from pathlib import Path


def extract_pdf_text_with_ocr(path: Path) -> str:
    """Run PyMuPDF's local Tesseract integration for an image-only PDF."""
    try:
        import fitz
    except ImportError as error:
        raise RuntimeError("PyMuPDF is required for PDF OCR") from error

    extracted_pages: list[str] = []
    try:
        with fitz.open(path) as document:
            for page in document:
                text_page = page.get_textpage_ocr()
                extracted_pages.append(page.get_text(textpage=text_page))
    except Exception as error:
        raise RuntimeError(
            "local OCR failed; verify that Tesseract and its language data are installed"
        ) from error
    return "\n\n".join(extracted_pages).strip()
