"""Isolated SQLite and dependency fixtures for Member 2 API tests."""

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from backend.app.api.dependencies import get_case_assistant, get_report_writer
from backend.app.core.config import Settings, get_settings
from backend.app.core.database import create_sqlite_engine, get_db, load_member_two_models
from backend.app.main import app
from backend.app.models import Base
from backend.app.schemas.assistant import CaseAnswer
from backend.app.schemas.report import ReportNarrative


class FakeCaseAssistant:
    async def answer(self, *, risk_case: object, question: str) -> CaseAnswer:
        del risk_case, question
        return CaseAnswer(
            answer="The imported risk score and rapid redistribution require review.",
            evidence_references=["CASE-001-EVD-001"],
            missing_evidence=["Verified supplier relationships"],
            disclaimer="This is decision support; a compliance officer makes the decision.",
        )


class FakeReportWriter:
    async def write(self, risk_case: object) -> ReportNarrative:
        del risk_case
        return ReportNarrative(
            executive_summary="The case contains a high-risk imported assessment.",
            risk_assessment="The risk score is an AI recommendation, not a disposition.",
            evidence_analysis="Verified and unverified evidence are identified separately.",
            reviewer_decision="No final decision should be inferred unless recorded.",
            limitations="The report is limited to evidence stored in this case.",
        )


@pytest.fixture
def risk_case_payload() -> dict[str, object]:
    return {
        "case_id": "CASE-001",
        "customer_id": "CUST-001",
        "risk_score": 89,
        "risk_level": "HIGH",
        "anomalies": ["Rapid redistribution", "Five new beneficiaries"],
        "scenarios": [
            {
                "scenario_id": "SCN-LAYERING-001",
                "name": "Transaction Layering",
                "category": "SUSPICIOUS",
                "match_score": 84,
                "description": "Incoming funds were rapidly redistributed.",
            },
            {
                "scenario_id": "SCN-BUSINESS-001",
                "name": "Legitimate Business Payment",
                "category": "LEGITIMATE",
                "match_score": 71,
                "description": "An invoice may explain the incoming payment.",
            },
        ],
        "supporting_evidence": ["Rapid fund redistribution"],
        "contradicting_evidence": ["A matching invoice was provided"],
        "missing_evidence": ["Supplier relationships are not verified"],
        "decision_critical_evidence": {
            "question": "Are the five beneficiaries genuine suppliers?",
            "why_it_matters": "Verification separates business activity from layering.",
            "recommended_action": "Request supplier relationship records.",
        },
        "recommended_actions": ["Verify beneficiary relationships"],
    }


@pytest.fixture
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    load_member_two_models()
    database_engine = create_sqlite_engine(":memory:")
    Base.metadata.create_all(database_engine)
    testing_session = sessionmaker(bind=database_engine, autoflush=False, expire_on_commit=False)
    settings = Settings(
        database_path=tmp_path / "test.db",
        database_auto_create=False,
        document_storage_path=tmp_path / "documents",
        report_output_path=tmp_path / "reports",
    )

    def override_db() -> Generator[Session, None, None]:
        session = testing_session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_case_assistant] = lambda: FakeCaseAssistant()
    app.dependency_overrides[get_report_writer] = lambda: FakeReportWriter()
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        test_client.close()
        app.dependency_overrides.clear()
        Base.metadata.drop_all(database_engine)
        database_engine.dispose()
