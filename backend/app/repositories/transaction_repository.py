from backend.app.schemas.transaction import TransactionInput


class TransactionRepository:
    def __init__(self) -> None:
        self._transactions: dict[str, list[TransactionInput]] = {}

    def add(self, transaction: TransactionInput) -> TransactionInput:
        self._transactions.setdefault(transaction.customer_id, []).append(transaction)
        return transaction

    def list_for_customer(self, customer_id: str) -> list[TransactionInput]:
        return list(self._transactions.get(customer_id, []))

