"""Specialized case-scoped evidence critique using the local assistant."""

from backend.app.models.case import RiskCase
from backend.app.schemas.assistant import CaseAnswer
from local_ai.gemma.case_assistant import CaseAssistant


class EvidenceCritic:
    def __init__(self, assistant: CaseAssistant) -> None:
        self.assistant = assistant

    async def critique(self, risk_case: RiskCase) -> CaseAnswer:
        return await self.assistant.answer(
            risk_case=risk_case,
            question=(
                "Challenge the leading scenario. Identify contradictory, unverified, and "
                "missing evidence, citing only evidence IDs in this case."
            ),
        )
