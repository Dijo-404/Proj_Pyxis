from backend.app.intelligence.gemma.output_parser import parse_investigation_output
from backend.app.intelligence.gemma.provider import GemmaProvider, LocalFallbackGemmaProvider
from backend.app.schemas.anomaly import AnomalyAssessment
from backend.app.schemas.financial_twin import FinancialTwin
from backend.app.schemas.scenario import GemmaInvestigation
from backend.app.schemas.transaction import TransactionInput


class InvestigationService:
    def __init__(self, provider: GemmaProvider | None = None) -> None:
        self.provider = provider or LocalFallbackGemmaProvider()

    def investigate(self, transaction: TransactionInput, twin: FinancialTwin, anomaly: AnomalyAssessment) -> GemmaInvestigation:
        evidence_package = {
            "current_transaction": transaction.model_dump(mode="json"),
            "customer_twin": twin.model_dump(mode="json"),
            "detected_deviations": anomaly.model_dump(mode="json"),
        }
        return parse_investigation_output(self.provider.investigate(evidence_package))

