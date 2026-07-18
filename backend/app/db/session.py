from backend.app.repositories.case_repository import CaseRepository
from backend.app.repositories.customer_repository import CustomerRepository
from backend.app.repositories.transaction_repository import TransactionRepository
from backend.app.repositories.twin_repository import TwinRepository
from backend.app.services.risk_case_service import RiskCaseService
from backend.app.services.transaction_service import TransactionService


customers = CustomerRepository()
transactions = TransactionRepository()
twins = TwinRepository()
cases = CaseRepository()

risk_case_service = RiskCaseService(customers, transactions, twins, cases)
transaction_service = TransactionService(transactions)

