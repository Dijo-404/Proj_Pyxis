"""Render validated structured report data into local HTML."""

from collections.abc import Mapping
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

TEMPLATE_DIRECTORY = Path(__file__).parent / "templates"


def render_investigation_report(context: Mapping[str, object]) -> str:
    """Render HTML with strict variables and automatic escaping."""
    environment = Environment(
        loader=FileSystemLoader(TEMPLATE_DIRECTORY),
        autoescape=select_autoescape(("html", "xml")),
        undefined=StrictUndefined,
    )
    return environment.get_template("investigation_report.html").render(**context)
