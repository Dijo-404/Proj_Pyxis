"""Risk-case persistence operations."""

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from backend.app.models.case import RiskCase
from backend.app.models.evidence import Evidence
from backend.app.models.scenario import Scenario
from backend.app.schemas.case import RiskCaseImport
from backend.app.schemas.common import EvidenceStatus, EvidenceType


class CaseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, case_id: str) -> RiskCase | None:
        return self.session.get(RiskCase, case_id)

    def list(
        self,
        *,
        status: str | None = None,
        risk_level: str | None = None,
        customer_id: str | None = None,
        minimum_risk_score: float | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[RiskCase]:
        statement: Select[tuple[RiskCase]] = select(RiskCase)
        if status is not None:
            statement = statement.where(RiskCase.status == status)
        if risk_level is not None:
            statement = statement.where(RiskCase.risk_level == risk_level)
        if customer_id is not None:
            statement = statement.where(RiskCase.customer_id == customer_id)
        if minimum_risk_score is not None:
            statement = statement.where(RiskCase.risk_score >= minimum_risk_score)
        statement = statement.order_by(
            RiskCase.priority.asc(), RiskCase.risk_score.desc(), RiskCase.created_at.asc()
        )
        return list(self.session.scalars(statement.offset(offset).limit(limit)).all())

    def add_import(self, payload: RiskCaseImport, *, priority: int) -> RiskCase:
        risk_case = RiskCase(
            case_id=payload.case_id,
            customer_id=payload.customer_id,
            risk_score=payload.risk_score,
            risk_level=payload.risk_level.value,
            priority=priority,
            anomalies=list(payload.anomalies),
            decision_critical_evidence=(
                payload.decision_critical_evidence.model_dump(mode="json", exclude_none=True)
                if payload.decision_critical_evidence
                else None
            ),
            recommended_actions=list(payload.recommended_actions),
        )
        self.session.add(risk_case)

        for position, scenario in enumerate(payload.scenarios, start=1):
            risk_case.scenarios.append(
                Scenario(
                    scenario_id=scenario.scenario_id or f"{payload.case_id}-SCN-{position:03d}",
                    case_id=payload.case_id,
                    name=scenario.name,
                    category=scenario.category.value,
                    match_score=scenario.match_score,
                    description=scenario.description,
                )
            )

        evidence_groups = (
            (
                payload.supporting_evidence,
                EvidenceType.SUPPORTING,
                EvidenceStatus.UNVERIFIED,
                1.0,
            ),
            (
                payload.contradicting_evidence,
                EvidenceType.CONTRADICTING,
                EvidenceStatus.UNVERIFIED,
                1.0,
            ),
            (payload.missing_evidence, EvidenceType.MISSING, EvidenceStatus.MISSING, 0.0),
        )
        evidence_position = 0
        for descriptions, evidence_type, status, confidence in evidence_groups:
            for description in descriptions:
                evidence_position += 1
                risk_case.evidence.append(
                    Evidence(
                        evidence_id=f"{payload.case_id}-EVD-{evidence_position:03d}",
                        case_id=payload.case_id,
                        evidence_type=evidence_type.value,
                        description=description,
                        source_reference="risk_case_import",
                        status=status.value,
                        confidence=confidence,
                        submitted_by="MEMBER_1_RISK_ENGINE",
                    )
                )

        self.session.flush()
        return risk_case
