from backend.app.intelligence.financial_twin.behavior_features import build_behavior_profile
from backend.app.repositories.transaction_repository import TransactionRepository
from backend.app.schemas.financial_twin import BehaviorProfile


class CustomerProfileService:
    def __init__(self, transactions: TransactionRepository) -> None:
        self.transactions = transactions

    def build_profile(self, customer_id: str) -> BehaviorProfile:
        return build_behavior_profile(customer_id, self.transactions.list_for_customer(customer_id))

