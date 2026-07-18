import json

from pydantic import ValidationError

from backend.app.schemas.scenario import GemmaInvestigation


def parse_investigation_output(raw_output: str) -> GemmaInvestigation:
    try:
        payload = json.loads(raw_output)
        return GemmaInvestigation.model_validate(payload)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValueError("AI_RESULT_UNAVAILABLE") from exc

