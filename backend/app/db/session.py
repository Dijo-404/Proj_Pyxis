from app.repositories.case_repository import CaseRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.twin_repository import TwinRepository
from app.services.risk_case_service import RiskCaseService
from app.services.transaction_service import TransactionService


customers = CustomerRepository()
transactions = TransactionRepository()
twins = TwinRepository()
cases = CaseRepository()

risk_case_service = RiskCaseService(customers, transactions, twins, cases)
transaction_service = TransactionService(transactions)

