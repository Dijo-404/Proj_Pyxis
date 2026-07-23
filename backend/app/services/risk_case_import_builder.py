"""Converts a live risk-engine investigation (RiskCaseResponse) into the DB-backed
RiskCaseImport contract, so the twin/anomaly/scenario/evidence pipeline that actually
computes something feeds the persisted case that reviewers see, decide on, and get a
report for — instead of the two staying disconnected.
"""

from backend.app.intelligence.sandbox.trace_builder import build_sandbox_trace
from backend.app.schemas.case import DecisionCriticalEvidence as ImportCriticalEvidence
from backend.app.schemas.case import RiskCaseImport
from backend.app.schemas.common import RiskLevel, ScenarioCategory
from backend.app.schemas.customer import CustomerProfile
from backend.app.schemas.risk_case import RiskCaseResponse
from backend.app.schemas.scenario import ScenarioImport
from backend.app.schemas.transaction import TransactionInput


def _format_amount(currency: str, amount: float) -> str:
    return f"{currency} {amount:,.0f}"


def build_risk_case_import(
    *,
    risk_case: RiskCaseResponse,
    customer: CustomerProfile,
    transaction: TransactionInput,
    history: list[TransactionInput],
    total_duration_ms: int,
    model_name: str = "stub",
    runtime_label: str = "Local fallback (no live Gemma call yet)",
    boundary_held: bool = True,
) -> RiskCaseImport:
    twin = risk_case.financial_twin
    anomaly = risk_case.anomaly_assessment
    investigation = risk_case.gemma_investigation
    comparisons = risk_case.evidence_comparisons
    critical = risk_case.decision_critical_evidence

    comparison_by_scenario = {comparison.scenario_id: comparison for comparison in comparisons}
    scenarios = [
        ScenarioImport(
            scenario_id=scenario.scenario_id,
            name=scenario.name,
            category=ScenarioCategory(scenario.category),
            match_score=round(comparison_by_scenario[scenario.scenario_id].match_score * 100)
            if scenario.scenario_id in comparison_by_scenario
            else 0,
            description=scenario.description,
        )
        for scenario in investigation.scenarios
    ]

    supporting_evidence: list[str] = []
    contradicting_evidence: list[str] = []
    missing_evidence: list[str] = []
    for comparison in comparisons:
        for signal in comparison.signals:
            explanation = signal.explanation or f"{signal.signal} evaluated as {signal.status}."
            if signal.status in {"MATCH", "PARTIAL"}:
                supporting_evidence.append(explanation)
            elif signal.status == "CONTRADICT":
                contradicting_evidence.append(explanation)
            else:
                missing_evidence.append(explanation)

    financial_twin_metrics = _build_twin_metrics(transaction, twin, anomaly)
    investigation_steps = _build_investigation_steps(anomaly, investigation, comparisons, critical)
    scenario_evidence = {
        comparison.scenario_id: {
            "supporting": comparison.supporting_evidence,
            "contradicting": comparison.contradicting_evidence,
            "unknown": comparison.unknown_evidence,
        }
        for comparison in comparisons
    }
    evidence_matrix = _build_evidence_matrix(comparisons)
    sandbox = build_sandbox_trace(
        case_id=risk_case.case_id,
        customer=customer,
        transaction=transaction,
        twin=twin,
        anomaly=anomaly,
        investigation=investigation,
        comparisons=comparisons,
        critical_evidence=critical,
        history=history,
        total_duration_ms=total_duration_ms,
        model_name=model_name,
        runtime_label=runtime_label,
        boundary_held=boundary_held,
    )

    return RiskCaseImport(
        case_id=risk_case.case_id,
        customer_id=risk_case.customer_id,
        customer_name=customer.declared_business or customer.customer_id,
        customer_type=customer.customer_type,
        business=customer.declared_business or "Not provided",
        trigger_transaction_id=risk_case.trigger_transaction_id,
        trigger_summary=investigation.case_summary,
        trigger_amount=_format_amount(transaction.currency, transaction.amount),
        location=transaction.country or customer.country or "Not provided",
        risk_score=float(risk_case.current_risk_score),
        risk_level=RiskLevel(risk_case.risk_level),
        anomalies=[rule.description for rule in anomaly.triggered_rules],
        scenarios=scenarios,
        supporting_evidence=supporting_evidence,
        contradicting_evidence=contradicting_evidence,
        missing_evidence=missing_evidence,
        decision_critical_evidence=ImportCriticalEvidence(
            question=critical.question,
            why_it_matters=critical.why_it_matters,
            recommended_action=critical.recommended_action,
        ),
        recommended_actions=investigation.recommended_actions,
        workspace_data={
            "anomaly_score": anomaly.score,
            "financial_twin": financial_twin_metrics,
            "investigation": investigation_steps,
            "scenario_evidence": scenario_evidence,
            "evidence_matrix": evidence_matrix,
            # Populated by the counterfactual-analysis engine (spec §19).
            "counterfactual": [],
            "sandbox": sandbox,
        },
    )


def _build_twin_metrics(transaction, twin, anomaly) -> list[dict[str, object]]:
    p95 = twin.amount_profile.p95 or max(twin.amount_profile.median, 1)
    hourly_velocity = anomaly.features.get("hourly_velocity", 0)
    is_new_beneficiary = bool(anomaly.features.get("is_new_beneficiary"))
    is_new_country = bool(anomaly.features.get("is_new_country"))
    in_active_hours = (
        twin.time_profile.usual_start_hour
        <= transaction.timestamp.hour
        <= twin.time_profile.usual_end_hour
    )
    return [
        {
            "label": "Transaction amount",
            "normal": _format_amount(transaction.currency, p95),
            "current": _format_amount(transaction.currency, transaction.amount),
            "deviated": transaction.amount > p95,
        },
        {
            "label": "Hourly transaction count",
            "normal": str(twin.velocity_profile.maximum_normal_hourly_count),
            "current": str(hourly_velocity),
            "deviated": hourly_velocity > twin.velocity_profile.maximum_normal_hourly_count,
        },
        {
            "label": "Beneficiary trust",
            "normal": f"{twin.beneficiary_profile.known_beneficiary_ratio:.0%} known",
            "current": "New beneficiary" if is_new_beneficiary else "Known beneficiary",
            "deviated": is_new_beneficiary,
        },
        {
            "label": "Transaction country",
            "normal": ", ".join(twin.geography_profile.common_countries) or "—",
            "current": transaction.country,
            "deviated": is_new_country,
        },
        {
            "label": "Active hours",
            "normal": (
                f"{twin.time_profile.usual_start_hour:02d}:00–"
                f"{twin.time_profile.usual_end_hour:02d}:00"
            ),
            "current": f"{transaction.timestamp.hour:02d}:00",
            "deviated": not in_active_hours,
        },
    ]


def _build_investigation_steps(anomaly, investigation, comparisons, critical) -> list[dict[str, object]]:
    top = max(comparisons, key=lambda c: c.match_score, default=None)
    top_scenario = next(
        (s for s in investigation.scenarios if top and s.scenario_id == top.scenario_id), None
    )
    return [
        {
            "label": "Collected trusted context",
            "done": True,
            "detail": "Loaded the customer's financial twin and the triggering transaction.",
        },
        {
            "label": "Detected deviation",
            "done": True,
            "detail": f"Anomaly score {anomaly.score}/100 ({anomaly.deviation_level.title()}).",
        },
        {
            "label": "Generated competing scenarios",
            "done": True,
            "detail": f"{len(investigation.scenarios)} scenario(s) considered.",
        },
        {
            "label": "Compared evidence",
            "done": True,
            "detail": (
                f"Top match: {top_scenario.name} ({top.match_score:.0%})."
                if top and top_scenario
                else "No scenario comparisons were available."
            ),
        },
        {
            "label": "Identified decision-critical evidence",
            "done": True,
            "detail": critical.question,
        },
    ]


def _build_evidence_matrix(comparisons) -> list[dict[str, object]]:
    signal_order: list[str] = []
    seen: set[str] = set()
    for comparison in comparisons:
        for signal in comparison.signals:
            if signal.signal not in seen:
                seen.add(signal.signal)
                signal_order.append(signal.signal)

    rows = []
    for signal_name in signal_order:
        by_scenario: dict[str, str] = {}
        for comparison in comparisons:
            match = next((s for s in comparison.signals if s.signal == signal_name), None)
            if match is not None:
                by_scenario[comparison.scenario_id] = match.status
        rows.append({"signal": signal_name, "byScenario": by_scenario})
    return rows
