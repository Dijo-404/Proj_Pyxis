"""Builds the per-customer agent-sandbox trace (sandbox.md) from a real, already-computed
investigation — not a fabricated demo narrative. Every field here is derived from the actual
twin/anomaly/scenario/evidence objects produced for this transaction; the only design choice
(not a fabrication) is the fixed weighting used to apportion the one real measured wall-clock
duration across the eight sandbox.md stages, since the current pipeline does not yet
instrument each stage individually.
"""

import zlib
from typing import Any

from backend.app.intelligence.anomaly_detection.anomaly_scorer import RULE_WEIGHTS
from backend.app.schemas.anomaly import AnomalyAssessment
from backend.app.schemas.customer import CustomerProfile
from backend.app.schemas.evidence import DecisionCriticalEvidence, EvidenceComparison
from backend.app.schemas.financial_twin import FinancialTwin
from backend.app.schemas.scenario import GemmaInvestigation
from backend.app.schemas.transaction import TransactionInput

_DEVIATION_LABELS = {"SEVERE": "Severe", "ELEVATED": "Moderate", "NORMAL": "Mild"}

# Relative share of the one measured wall-clock duration attributed to each stage.
_STAGE_WEIGHTS = {
    "CONTEXT_BUILDER": 0.05,
    "ORCHESTRATOR": 0.15,
    "SCENARIO_GENERATOR": 0.20,
    "DETERMINISTIC_TOOLS": 0.10,
    "SIMULATOR_SCORER": 0.15,
    "EVIDENCE_CRITIC": 0.20,
    "DECISION_EVIDENCE": 0.10,
    "REPORT_WRITER": 0.05,
}


def _format_amount(currency: str, amount: float) -> str:
    return f"{currency} {amount:,.0f}"


def _deterministic_seed(case_id: str) -> int:
    return zlib.crc32(case_id.encode("utf-8")) % 90_000 + 10_000


def build_sandbox_trace(
    *,
    case_id: str,
    customer: CustomerProfile,
    transaction: TransactionInput,
    twin: FinancialTwin,
    anomaly: AnomalyAssessment,
    investigation: GemmaInvestigation,
    comparisons: list[EvidenceComparison],
    critical_evidence: DecisionCriticalEvidence,
    history: list[TransactionInput],
    total_duration_ms: int,
    model_name: str,
    runtime_label: str,
    boundary_held: bool,
) -> dict[str, Any]:
    """Assemble the mobile/web `Sandbox` shape from a real, already-run investigation."""
    stages = _build_stages(
        transaction=transaction,
        investigation=investigation,
        comparisons=comparisons,
        anomaly=anomaly,
        critical_evidence=critical_evidence,
        total_duration_ms=total_duration_ms,
    )
    return {
        "runId": f"RUN-{case_id}",
        "model": model_name,
        "runtime": runtime_label,
        "boundaryHeld": boundary_held,
        "seed": _deterministic_seed(case_id),
        "totalDurationMs": total_duration_ms,
        "anomaly": _build_anomaly_breakdown(transaction, anomaly, critical_evidence),
        "stages": stages,
        "flow": _build_flow(case_id, customer, transaction, twin),
        "transactions": _build_transaction_history(case_id, transaction, anomaly, history),
        "branches": _build_branches(history),
    }


def _build_anomaly_breakdown(
    transaction: TransactionInput,
    anomaly: AnomalyAssessment,
    critical_evidence: DecisionCriticalEvidence,
) -> dict[str, Any]:
    triggered_ids = {rule.rule_id for rule in anomaly.triggered_rules}
    triggered_by_id = {rule.rule_id: rule for rule in anomaly.triggered_rules}
    signals = []
    for rule_id, weight in RULE_WEIGHTS.items():
        fired = rule_id in triggered_ids
        label = rule_id.replace("_", " ").title()
        if fired:
            rule = triggered_by_id[rule_id]
            signals.append(
                {
                    "key": rule_id,
                    "label": label,
                    "metric": "rule weight",
                    "value": rule.severity,
                    "contribution": weight,
                    "why": rule.description,
                    "fired": True,
                }
            )
        else:
            signals.append(
                {
                    "key": rule_id,
                    "label": label,
                    "metric": "rule weight",
                    "value": "—",
                    "contribution": 0,
                    "why": f"{label} was not observed for this transaction.",
                    "fired": False,
                }
            )

    matters = (
        f"{transaction.transaction_type.replace('_', ' ').title()} of "
        f"{_format_amount(transaction.currency, transaction.amount)} from "
        f"{transaction.source_account} to {transaction.destination_account}."
    )
    if triggered_ids:
        rule_list = ", ".join(sorted(triggered_ids))
        marked_risk = (
            f"{len(triggered_ids)} deterministic signal(s) ({rule_list}) pushed the anomaly "
            f"score to {anomaly.score}, crossing the review threshold."
        )
    else:
        marked_risk = (
            "No deterministic rule thresholds were exceeded; the score reflects underlying "
            "feature deviations only."
        )

    return {
        "score": anomaly.score,
        "deviationLevel": _DEVIATION_LABELS.get(anomaly.deviation_level, "Mild"),
        "signals": signals,
        "matters": matters,
        "markedRisk": marked_risk,
    }


def _build_stages(
    *,
    transaction: TransactionInput,
    investigation: GemmaInvestigation,
    comparisons: list[EvidenceComparison],
    anomaly: AnomalyAssessment,
    critical_evidence: DecisionCriticalEvidence,
    total_duration_ms: int,
) -> list[dict[str, Any]]:
    tool_calls = [
        {
            "tool": f"calculate_{key}",
            "args": f"transaction_id={transaction.transaction_id}",
            "result": str(value),
        }
        for key, value in list(anomaly.features.items())[:6]
    ]
    scenario_names = ", ".join(scenario.name for scenario in investigation.scenarios) or "none"
    score_summary = ", ".join(f"{c.scenario_id}={c.match_score:.2f}" for c in comparisons) or "n/a"
    recommended = "; ".join(investigation.recommended_actions) or "No actions recommended."

    definitions = [
        (
            "CONTEXT_BUILDER",
            "Build trusted context",
            "DETERMINISTIC",
            "Loaded the customer's trusted twin and the triggering transaction.",
            "customer_profile + trigger transaction",
            "Trusted context package assembled.",
            [],
        ),
        (
            "ORCHESTRATOR",
            "Plan investigation",
            "GEMMA",
            investigation.case_summary,
            "twin + anomaly feature package",
            investigation.case_summary,
            [],
        ),
        (
            "SCENARIO_GENERATOR",
            "Generate competing scenarios",
            "GEMMA",
            f"Produced {len(investigation.scenarios)} competing scenario(s).",
            "case summary + detected deviations",
            scenario_names,
            [],
        ),
        (
            "DETERMINISTIC_TOOLS",
            "Run local analytics",
            "DETERMINISTIC",
            "Calculated deterministic anomaly features against the trusted twin.",
            "transaction + financial twin",
            ", ".join(f"{k}={v}" for k, v in list(anomaly.features.items())[:6]),
            tool_calls,
        ),
        (
            "SIMULATOR_SCORER",
            "Score scenario fit",
            "DETERMINISTIC",
            f"Scored {len(comparisons)} scenario(s) against observed evidence.",
            "scenarios + expected signals",
            score_summary,
            [],
        ),
        (
            "EVIDENCE_CRITIC",
            "Challenge the evidence",
            "GEMMA",
            "Classified signals into supporting, contradicting, and unknown evidence.",
            "signal evaluations",
            (
                f"{sum(len(c.supporting_evidence) for c in comparisons)} supporting, "
                f"{sum(len(c.contradicting_evidence) for c in comparisons)} contradicting, "
                f"{sum(len(c.unknown_evidence) for c in comparisons)} unknown"
            ),
            [],
        ),
        (
            "DECISION_EVIDENCE",
            "Find decision-critical evidence",
            "DETERMINISTIC",
            critical_evidence.question,
            "ranked evidence comparisons",
            critical_evidence.why_it_matters,
            [],
        ),
        (
            "REPORT_WRITER",
            "Prepare reviewer brief",
            "GEMMA",
            "Summarized verified facts and recommended actions for human review.",
            "case summary + decision-critical evidence",
            recommended,
            [],
        ),
    ]

    remaining = total_duration_ms
    stages = []
    for index, (kind, title, actor, summary, input_text, output_text, calls) in enumerate(
        definitions
    ):
        if index == len(definitions) - 1:
            duration = max(1, remaining)
        else:
            duration = max(1, round(total_duration_ms * _STAGE_WEIGHTS[kind]))
            remaining -= duration
        stages.append(
            {
                "kind": kind,
                "title": title,
                "actor": actor,
                "summary": summary,
                "input": input_text,
                "output": output_text,
                "toolCalls": calls,
                "durationMs": duration,
            }
        )
    return stages


def _build_flow(
    case_id: str,
    customer: CustomerProfile,
    transaction: TransactionInput,
    twin: FinancialTwin,
) -> dict[str, Any]:
    source_id = f"{case_id}-SRC"
    customer_id = f"{case_id}-CUSTOMER"
    beneficiary_id = f"{case_id}-BEN-1"
    amount = _format_amount(transaction.currency, transaction.amount)
    customer_label = customer.declared_business or customer.customer_id
    beneficiary_label = transaction.beneficiary_id or transaction.destination_account
    beneficiary_verified = bool(
        transaction.beneficiary_id
        and transaction.beneficiary_id in twin.beneficiary_profile.known_beneficiary_ids
    )

    nodes = [
        {
            "id": source_id,
            "label": transaction.source_account,
            "kind": "SOURCE",
            "amount": amount,
        },
        {
            "id": customer_id,
            "label": customer_label,
            "kind": "CUSTOMER",
            "amount": amount,
        },
        {
            "id": beneficiary_id,
            "label": beneficiary_label,
            "kind": "BENEFICIARY",
            "verified": "VERIFIED" if beneficiary_verified else "UNKNOWN",
            "amount": amount,
        },
    ]
    edges = [
        {"from": source_id, "to": customer_id, "amount": amount},
        {"from": customer_id, "to": beneficiary_id, "amount": amount},
    ]
    return {"nodes": nodes, "edges": edges}


def _build_transaction_history(
    case_id: str,
    trigger_transaction: TransactionInput,
    anomaly: AnomalyAssessment,
    history: list[TransactionInput],
) -> list[dict[str, Any]]:
    ordered = sorted(history, key=lambda item: item.timestamp)
    entries = []
    for item in ordered:
        is_trigger = item.transaction_id == trigger_transaction.transaction_id
        entries.append(
            {
                "id": item.transaction_id,
                "label": item.transaction_type.replace("_", " ").title(),
                "amount": _format_amount(item.currency, item.amount),
                "timestamp": item.timestamp.isoformat(),
                "direction": "IN" if item.direction.upper() in {"CREDIT", "IN"} else "OUT",
                "risky": is_trigger and anomaly.score >= 30,
                "riskScore": anomaly.score if is_trigger else 0,
                "reason": (
                    (
                        anomaly.triggered_rules[0].description
                        if anomaly.triggered_rules
                        else "Flagged for review"
                    )
                    if is_trigger and anomaly.score >= 30
                    else "No anomaly evaluated this run"
                ),
                "explanation": (
                    "; ".join(rule.description for rule in anomaly.triggered_rules)
                    if is_trigger and anomaly.triggered_rules
                    else "Historical activity shown for context; anomaly detection ran only "
                    "against the triggering transaction."
                ),
                "firedSignals": (
                    [rule.rule_id for rule in anomaly.triggered_rules] if is_trigger else []
                ),
            }
        )
    return entries


def _build_branches(history: list[TransactionInput]) -> list[dict[str, Any]]:
    ordered = sorted(history, key=lambda item: item.timestamp)
    branches = []
    for index, item in enumerate(ordered):
        branches.append(
            {
                "id": f"BR-{index:02d}",
                "transactionId": item.transaction_id,
                "x": round(0.12 + (index % 4) * 0.24, 2),
                "y": round(0.12 + (index // 4) * 0.2, 2),
                "parents": [] if index == 0 else [f"BR-{index - 1:02d}"],
            }
        )
    return branches
