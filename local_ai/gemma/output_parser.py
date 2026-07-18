"""Strict parsing for local Gemma case-assistant and report output."""

import json

from pydantic import ValidationError

from backend.app.schemas.assistant import CaseAnswer
from backend.app.schemas.report import ReportNarrative
from backend.app.services.errors import LocalAIUnavailableError


def extract_json_object(raw_output: str) -> str:
    """Extract one JSON object while tolerating a surrounding Markdown fence."""
    stripped = raw_output.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3 and lines[-1].strip() == "```":
            stripped = "\n".join(lines[1:-1]).strip()

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start < 0 or end < start:
        raise LocalAIUnavailableError("local Gemma did not return a JSON object")
    candidate = stripped[start : end + 1]
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as error:
        raise LocalAIUnavailableError("local Gemma returned malformed JSON") from error
    if not isinstance(parsed, dict):
        raise LocalAIUnavailableError("local Gemma output must be a JSON object")
    return json.dumps(parsed)


def parse_case_answer(raw_output: str) -> CaseAnswer:
    try:
        return CaseAnswer.model_validate_json(extract_json_object(raw_output))
    except ValidationError as error:
        raise LocalAIUnavailableError(
            "local Gemma answer did not match the required schema"
        ) from error


def parse_report_narrative(raw_output: str) -> ReportNarrative:
    try:
        return ReportNarrative.model_validate_json(extract_json_object(raw_output))
    except ValidationError as error:
        raise LocalAIUnavailableError(
            "local Gemma report did not match the required schema"
        ) from error
