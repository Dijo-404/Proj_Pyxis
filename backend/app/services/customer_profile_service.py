from backend.app.intelligence.financial_twin.behavior_features import build_behavior_profile
from backend.app.intelligence.financial_twin.trust_gate import should_learn_transaction
from backend.app.repositories.case_repository import CaseRepository
from backend.app.repositories.transaction_repository import TransactionRepository
from backend.app.schemas.financial_twin import BehaviorProfile
from backend.app.schemas.transaction import TransactionInput


class CustomerProfileService:
    def __init__(self, transactions: TransactionRepository) -> None:
        self.transactions = transactions

    def build_profile(
        self, customer_id: str, case_repository: CaseRepository | None = None
    ) -> BehaviorProfile:
        """Build the behavior profile that feeds the financial twin.

        Trust-gated learning (spec §10): passing `case_repository` restricts the
        history to transactions that either never triggered a case (nothing to
        distrust) or whose case was reviewed, cleared, and scored low-risk. Without
        it, every stored transaction is used — the bootstrap path (first-time twin
        creation) has nothing yet to poison, so it stays ungated.
        """
        history = self.transactions.list_for_customer(customer_id)
        if case_repository is not None:
            history = [
                transaction
                for transaction in history
                if self._is_trusted(transaction, case_repository)
            ]
        return build_behavior_profile(customer_id, history)

    @staticmethod
    def _is_trusted(transaction: TransactionInput, case_repository: CaseRepository) -> bool:
        case = case_repository.get_by_trigger_transaction(transaction.transaction_id)
        if case is None:
            return True
        return should_learn_transaction(case.status, round(case.risk_score))
