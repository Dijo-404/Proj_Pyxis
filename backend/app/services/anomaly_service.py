from backend.app.intelligence.anomaly_detection.anomaly_scorer import score_transaction
from backend.app.schemas.anomaly import AnomalyAssessment
from backend.app.schemas.financial_twin import FinancialTwin
from backend.app.schemas.transaction import TransactionInput


class AnomalyService:
    def assess(
        self, transaction: TransactionInput, twin: FinancialTwin, hourly_velocity: int = 6
    ) -> AnomalyAssessment:
        return score_transaction(transaction, twin, hourly_velocity=hourly_velocity)
