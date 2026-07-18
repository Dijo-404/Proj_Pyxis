from backend.app.repositories.customer_repository import CustomerRepository
from backend.app.repositories.risk_engine_case_repository import RiskEngineCaseRepository
from backend.app.repositories.transaction_repository import TransactionRepository
from backend.app.repositories.twin_repository import TwinRepository
from backend.app.services.risk_case_service import RiskCaseService
from backend.app.services.transaction_service import TransactionService

customers = CustomerRepository()
transactions = TransactionRepository()
twins = TwinRepository()
cases = RiskEngineCaseRepository()

risk_case_service = RiskCaseService(customers, transactions, twins, cases)
transaction_service = TransactionService(transactions)
