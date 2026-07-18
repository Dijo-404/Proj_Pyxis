from backend.app.intelligence.financial_twin.twin_builder import build_financial_twin
from backend.app.repositories.twin_repository import TwinRepository
from backend.app.schemas.customer import CustomerProfile
from backend.app.schemas.financial_twin import BehaviorProfile, FinancialTwin


class FinancialTwinService:
    def __init__(self, twins: TwinRepository) -> None:
        self.twins = twins

    def get_or_create(self, customer: CustomerProfile, behavior: BehaviorProfile) -> FinancialTwin:
        existing = self.twins.get(customer.customer_id)
        if existing:
            return existing
        twin = build_financial_twin(customer, behavior, version=1)
        return self.twins.save(twin)

    def rebuild(self, customer: CustomerProfile, behavior: BehaviorProfile) -> FinancialTwin:
        current = self.twins.get(customer.customer_id)
        version = 1 if current is None else current.version + 1
        return self.twins.save(build_financial_twin(customer, behavior, version=version))
