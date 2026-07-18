from datetime import datetime, timezone

from backend.app.repositories.case_repository import CaseRepository
from backend.app.repositories.customer_repository import CustomerRepository
from backend.app.repositories.transaction_repository import TransactionRepository
from backend.app.repositories.twin_repository import TwinRepository
from backend.app.schemas.customer import CustomerProfile
from backend.app.schemas.financial_twin import FinancialTwin
from backend.app.schemas.risk_case import RiskCaseResponse
from backend.app.schemas.transaction import TransactionEvaluateRequest, TransactionInput
from backend.app.services.anomaly_service import AnomalyService
from backend.app.services.customer_profile_service import CustomerProfileService
from backend.app.services.financial_twin_service import FinancialTwinService
from backend.app.services.investigation_service import InvestigationService
from backend.app.services.scenario_service import ScenarioService


class RiskCaseService:
    def __init__(
        self,
        customers: CustomerRepository,
        transactions: TransactionRepository,
        twins: TwinRepository,
        cases: CaseRepository,
    ) -> None:
        self.customers = customers
        self.transactions = transactions
        self.twins = twins
        self.cases = cases
        self.profile_service = CustomerProfileService(transactions)
        self.twin_service = FinancialTwinService(twins)
        self.anomaly_service = AnomalyService()
        self.investigation_service = InvestigationService()
        self.scenario_service = ScenarioService()

    def evaluate_transaction(self, request: TransactionEvaluateRequest) -> RiskCaseResponse:
        customer = self.customers.save(request.customer_profile)
        behavior = self.profile_service.build_profile(customer.customer_id)
        twin = self.twin_service.get_or_create(customer, behavior)

        if twin.amount_profile.p95 == 0:
            twin = self.twins.save(FinancialTwin.demo_baseline(customer.customer_id))

        transaction = self.transactions.add(request.transaction)
        anomaly = self.anomaly_service.assess(transaction, twin)
        investigation = self.investigation_service.investigate(transaction, twin, anomaly)
        comparisons, critical_evidence = self.scenario_service.compare(investigation.scenarios, transaction, anomaly)
        current_risk_score = min(100, max(anomaly.score, round(max((item.match_score for item in comparisons), default=0) * 100)))

        risk_case = RiskCaseResponse(
            case_id=self._case_id(transaction),
            customer_id=customer.customer_id,
            trigger_transaction_id=transaction.transaction_id,
            status="OPEN",
            initial_anomaly_score=anomaly.score,
            current_risk_score=current_risk_score,
            risk_level=anomaly.risk_level,
            financial_twin=twin,
            anomaly_assessment=anomaly,
            gemma_investigation=investigation,
            scenarios=investigation.scenarios,
            evidence_comparisons=comparisons,
            decision_critical_evidence=critical_evidence,
            created_at=datetime.now(timezone.utc),
        )
        return self.cases.save(risk_case)

    def get_case(self, case_id: str) -> RiskCaseResponse | None:
        return self.cases.get(case_id)

    def get_twin(self, customer_id: str) -> FinancialTwin | None:
        return self.twins.get(customer_id)

    def rebuild_twin(self, customer: CustomerProfile) -> FinancialTwin:
        self.customers.save(customer)
        behavior = self.profile_service.build_profile(customer.customer_id)
        return self.twin_service.rebuild(customer, behavior)

    def investigate_case(self, case_id: str) -> RiskCaseResponse | None:
        existing = self.cases.get(case_id)
        if existing is None:
            return None
        transaction = self._find_transaction(existing.customer_id, existing.trigger_transaction_id)
        if transaction is None:
            return existing
        investigation = self.investigation_service.investigate(transaction, existing.financial_twin, existing.anomaly_assessment)
        comparisons, critical_evidence = self.scenario_service.compare(investigation.scenarios, transaction, existing.anomaly_assessment)
        updated = existing.model_copy(update={"gemma_investigation": investigation, "scenarios": investigation.scenarios, "evidence_comparisons": comparisons, "decision_critical_evidence": critical_evidence})
        return self.cases.save(updated)

    def _find_transaction(self, customer_id: str, transaction_id: str) -> TransactionInput | None:
        for transaction in self.transactions.list_for_customer(customer_id):
            if transaction.transaction_id == transaction_id:
                return transaction
        return None

    @staticmethod
    def _case_id(transaction: TransactionInput) -> str:
        suffix = transaction.transaction_id.replace("TXN-", "").replace("TX-", "")
        return f"CASE-{suffix}"

