"""Trust-gated adaptive learning (spec §10) wired into the live twin-rebuild path."""

from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import load_member_two_models
from backend.app.models import Base
from backend.app.repositories.case_repository import CaseRepository
from backend.app.repositories.transaction_repository import TransactionRepository
from backend.app.schemas.case import RiskCaseImport
from backend.app.schemas.common import RiskLevel
from backend.app.schemas.transaction import TransactionInput
from backend.app.services.customer_profile_service import CustomerProfileService


def _session():
    load_member_two_models()
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()


def _transaction(transaction_id: str, amount: float, hour: int = 10) -> TransactionInput:
    return TransactionInput(
        transaction_id=transaction_id,
        customer_id="CUST-TRUST",
        source_account="ACC-1",
        destination_account="ACC-2",
        amount=amount,
        currency="INR",
        transaction_type="BANK_TRANSFER",
        direction="CREDIT",
        timestamp=datetime(2026, 1, 1, hour, 0, 0),
        channel="MOBILE_BANKING",
        country="India",
        status="SUCCESS",
    )


def _import_case(
    session, case_id: str, transaction_id: str, status: str, risk_score: float
) -> None:
    repository = CaseRepository(session)
    imported = repository.add_import(
        RiskCaseImport(
            case_id=case_id,
            customer_id="CUST-TRUST",
            trigger_transaction_id=transaction_id,
            risk_score=risk_score,
            risk_level=RiskLevel.HIGH if risk_score >= 75 else RiskLevel.LOW,
        ),
        priority=3,
    )
    imported.status = status
    session.commit()


def test_never_flagged_transactions_are_always_trusted():
    session = _session()
    transactions = TransactionRepository()
    transactions.add(_transaction("TXN-1", 1000))
    service = CustomerProfileService(transactions)

    profile = service.build_profile("CUST-TRUST", CaseRepository(session))

    assert profile.amount_profile.median == 1000


def test_excludes_transactions_from_unresolved_or_suspicious_cases():
    session = _session()
    transactions = TransactionRepository()
    transactions.add(_transaction("TXN-NORMAL", 1000))
    transactions.add(_transaction("TXN-OPEN", 999999))
    transactions.add(_transaction("TXN-SUSPICIOUS", 888888))
    _import_case(session, "CASE-OPEN", "TXN-OPEN", "OPEN", 90)
    _import_case(session, "CASE-SUSP", "TXN-SUSPICIOUS", "SUSPICIOUS", 90)
    service = CustomerProfileService(transactions)

    profile = service.build_profile("CUST-TRUST", CaseRepository(session))

    # Only the never-flagged transaction should shape the baseline; the two flagged,
    # unresolved/suspicious ones must not poison "normal" with their extreme amounts.
    assert profile.amount_profile.median == 1000


def test_includes_transactions_from_cleared_low_risk_cases():
    session = _session()
    transactions = TransactionRepository()
    transactions.add(_transaction("TXN-NORMAL", 1000))
    transactions.add(_transaction("TXN-CLEARED", 2000))
    _import_case(session, "CASE-CLEARED", "TXN-CLEARED", "CLEARED", 20)
    service = CustomerProfileService(transactions)

    profile = service.build_profile("CUST-TRUST", CaseRepository(session))

    assert profile.amount_profile.median == 1500


def test_excludes_cleared_case_when_risk_score_was_not_low():
    # A case can be reviewed and cleared but still carry a high recorded risk_score;
    # §10 requires the behavioral change to be gradual and sufficiently supported, not
    # just any cleared disposition.
    session = _session()
    transactions = TransactionRepository()
    transactions.add(_transaction("TXN-NORMAL", 1000))
    transactions.add(_transaction("TXN-CLEARED-HIGH", 2000))
    _import_case(session, "CASE-CLEARED-HIGH", "TXN-CLEARED-HIGH", "CLEARED", 80)
    service = CustomerProfileService(transactions)

    profile = service.build_profile("CUST-TRUST", CaseRepository(session))

    assert profile.amount_profile.median == 1000


def test_bootstrap_path_is_ungated_without_a_case_repository():
    # No case_repository passed (the evaluate_transaction bootstrap path) -> everything
    # is used, matching pre-existing behavior. Nothing exists yet to poison.
    transactions = TransactionRepository()
    transactions.add(_transaction("TXN-1", 1000))
    transactions.add(_transaction("TXN-2", 999999))
    service = CustomerProfileService(transactions)

    profile = service.build_profile("CUST-TRUST")

    assert profile.amount_profile.median == 500499.5


def test_rebuild_endpoint_applies_trust_gating(client: TestClient) -> None:
    from backend.app.db.session import risk_case_service

    risk_case_service.transactions.add(_transaction("TXN-EP-NORMAL", 1000))
    risk_case_service.transactions.add(_transaction("TXN-EP-SUSPICIOUS", 999999))
    client.post(
        "/api/v1/cases/import",
        json={
            "case_id": "CASE-EP-SUSPICIOUS",
            "customer_id": "CUST-TRUST",
            "trigger_transaction_id": "TXN-EP-SUSPICIOUS",
            "risk_score": 90,
            "risk_level": "HIGH",
        },
    )

    response = client.post(
        "/api/v1/customers/CUST-TRUST/financial-twin/rebuild",
        json={
            "customer_id": "CUST-TRUST",
            "customer_type": "INDIVIDUAL",
            "country": "India",
            "account_age_months": 12,
            "kyc_status": "VERIFIED",
        },
    )

    assert response.status_code == 200
    twin = response.json()["data"]
    assert twin["amount_profile"]["median"] == 1000
