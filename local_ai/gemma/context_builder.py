"""Build compact context containing data from exactly one compliance case."""

from typing import Any

from backend.app.models.case import RiskCase

SAFE_EXTRACTED_FIELDS = frozenset(
    {
        "parser_metadata",
        "character_count",
        "invoice_numbers",
        "amount_candidates",
        "date_candidates",
    }
)


def _safe_extracted_data(extracted_data: dict[str, Any]) -> dict[str, Any]:
    """Exclude raw document text from model context."""
    return {key: extracted_data[key] for key in SAFE_EXTRACTED_FIELDS if key in extracted_data}


def build_case_context(risk_case: RiskCase) -> dict[str, Any]:
    """Serialize the current case without unrelated customers or raw documents."""
    return {
        "case": {
            "case_id": risk_case.case_id,
            "customer_id": risk_case.customer_id,
            "risk_score": risk_case.risk_score,
            "risk_level": risk_case.risk_level,
            "status": risk_case.status,
            "priority": risk_case.priority,
            "anomalies": risk_case.anomalies,
            "decision_critical_evidence": risk_case.decision_critical_evidence,
            "recommended_actions": risk_case.recommended_actions,
        },
        "scenarios": [
            {
                "scenario_id": scenario.scenario_id,
                "name": scenario.name,
                "category": scenario.category,
                "match_score": scenario.match_score,
                "description": scenario.description,
            }
            for scenario in risk_case.scenarios
        ],
        "evidence": [
            {
                "evidence_id": evidence.evidence_id,
                "scenario_id": evidence.scenario_id,
                "type": evidence.evidence_type,
                "description": evidence.description,
                "source_reference": evidence.source_reference,
                "status": evidence.status,
                "confidence": evidence.confidence,
                "verification_reason": evidence.verification_reason,
            }
            for evidence in risk_case.evidence
        ],
        "documents": [
            {
                "document_id": document.document_id,
                "document_type": document.document_type,
                "verification_status": document.verification_status,
                "extracted_data": _safe_extracted_data(document.extracted_data),
            }
            for document in risk_case.documents
        ],
        "reviews": [
            {
                "review_id": review.review_id,
                "reviewer_id": review.reviewer_id,
                "action": review.action,
                "reason": review.reason,
                "resulting_status": review.resulting_status,
                "created_at": review.created_at.isoformat(),
            }
            for review in risk_case.reviews
        ],
    }
