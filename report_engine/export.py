"""Atomically export rendered reports to institution-controlled local storage."""

import os
from pathlib import Path
from tempfile import NamedTemporaryFile


def export_html(html: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=destination.parent,
        prefix=f".{destination.name}.",
        delete=False,
    ) as temporary:
        temporary.write(html)
        temporary_path = Path(temporary.name)
    try:
        os.replace(temporary_path, destination)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
    return destination


def export_pdf(html: str, destination: Path) -> Path:
    """Render a PDF locally with WeasyPrint and atomically publish it."""
    try:
        from weasyprint import HTML
    except ImportError as error:
        raise RuntimeError("WeasyPrint is required for PDF report export") from error

    destination.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        mode="wb",
        dir=destination.parent,
        prefix=f".{destination.name}.",
        delete=False,
    ) as temporary:
        temporary_path = Path(temporary.name)
    try:
        HTML(string=html).write_pdf(temporary_path)
        os.replace(temporary_path, destination)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
    return destination
