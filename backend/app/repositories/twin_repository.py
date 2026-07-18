from backend.app.schemas.financial_twin import FinancialTwin


class TwinRepository:
    def __init__(self) -> None:
        self._twins: dict[str, FinancialTwin] = {}

    def save(self, twin: FinancialTwin) -> FinancialTwin:
        self._twins[twin.customer_id] = twin
        return twin

    def get(self, customer_id: str) -> FinancialTwin | None:
        return self._twins.get(customer_id)
