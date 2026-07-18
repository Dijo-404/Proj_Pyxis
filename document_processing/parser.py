"""Deterministic local parsing for supported compliance documents."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from document_processing.ocr import extract_pdf_text_with_ocr

SUPPORTED_EXTENSIONS = frozenset({".csv", ".json", ".md", ".pdf", ".txt"})


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


def parse_document(path: Path) -> ParsedDocument:
    """Extract local text without sending document data to another service."""
    extension = path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"unsupported document extension: {extension or '<none>'}")

    if extension != ".pdf":
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            raise ValueError("document contains no readable text")
        return ParsedDocument(text=text, metadata={"extension": extension, "pages": 1})

    try:
        import fitz
    except ImportError as error:
        raise RuntimeError("PyMuPDF is required to parse PDF documents") from error

    with fitz.open(path) as document:
        page_count = document.page_count
        text = "\n\n".join(page.get_text() for page in document).strip()

    used_ocr = False
    if not text:
        text = extract_pdf_text_with_ocr(path)
        used_ocr = True
    if not text:
        raise ValueError("document contains no readable text after local OCR")
    return ParsedDocument(
        text=text,
        metadata={"extension": extension, "pages": page_count, "used_ocr": used_ocr},
    )
