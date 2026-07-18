"""Deterministic extraction of common compliance-document fields."""

import re
from typing import Any

INVOICE_PATTERN = re.compile(
    r"\b(?:invoice|inv)[\s#:.-]*([A-Z0-9][A-Z0-9/-]{2,31})\b", re.IGNORECASE
)
AMOUNT_PATTERN = re.compile(
    r"(?:₹|\$|€|£|\b(?:INR|USD|EUR|GBP)\b)\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)",
    re.IGNORECASE,
)
DATE_PATTERN = re.compile(r"\b(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b")


def extract_structured_fields(text: str, metadata: dict[str, Any]) -> dict[str, Any]:
    """Extract transparent candidates; values remain unverified evidence."""
    invoice_numbers = list(dict.fromkeys(INVOICE_PATTERN.findall(text)))[:50]
    amount_candidates = list(dict.fromkeys(AMOUNT_PATTERN.findall(text)))[:100]
    date_candidates = list(dict.fromkeys(DATE_PATTERN.findall(text)))[:100]
    return {
        "parser_metadata": metadata,
        "character_count": len(text),
        "invoice_numbers": invoice_numbers,
        "amount_candidates": amount_candidates,
        "date_candidates": date_candidates,
        "text_preview": text[:2000],
    }
