from backend.app.intelligence.gemma.output_parser import parse_investigation_output
from backend.app.intelligence.gemma.provider import (
    RETRY_HINT,
    GemmaProvider,
    LocalFallbackGemmaProvider,
)
from backend.app.schemas.anomaly import AnomalyAssessment
from backend.app.schemas.financial_twin import FinancialTwin
from backend.app.schemas.scenario import GemmaInvestigation
from backend.app.schemas.transaction import TransactionInput
from backend.app.services.errors import ApplicationError


class InvestigationService:
    """Runs the Investigation Orchestrator / Scenario Generator role.

    Ground rule: Gemma output must be structured JSON, validated with Pydantic; invalid
    output triggers a stricter retry, then a graceful "AI result unavailable" state —
    here, that graceful state is the deterministic fallback provider, so the pipeline
    always produces a usable (if generic) investigation rather than erroring out.
    """

    def __init__(
        self, provider: GemmaProvider | None = None, fallback: GemmaProvider | None = None
    ) -> None:
        self.provider = provider or LocalFallbackGemmaProvider()
        self.fallback = fallback or LocalFallbackGemmaProvider()

    def investigate(
        self, transaction: TransactionInput, twin: FinancialTwin, anomaly: AnomalyAssessment
    ) -> GemmaInvestigation:
        evidence_package = {
            "current_transaction": transaction.model_dump(mode="json"),
            "customer_twin": twin.model_dump(mode="json"),
            "detected_deviations": anomaly.model_dump(mode="json"),
        }

        for package in (evidence_package, {**evidence_package, "_retry_hint": RETRY_HINT}):
            try:
                return parse_investigation_output(self.provider.investigate(package))
            except (ValueError, ApplicationError):
                continue

        # Both the initial attempt and the stricter retry failed (network error or
        # invalid/unvalidatable output) — degrade gracefully instead of raising.
        return parse_investigation_output(self.fallback.investigate(evidence_package))
