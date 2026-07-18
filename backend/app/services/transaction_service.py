from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionInput


class TransactionService:
    def __init__(self, transactions: TransactionRepository) -> None:
        self.transactions = transactions

    def import_transactions(self, payload: list[TransactionInput]) -> int:
        for transaction in payload:
            self.transactions.add(transaction)
        return len(payload)

