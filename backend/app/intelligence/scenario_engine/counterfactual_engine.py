"""Counterfactual analysis (spec §19): "what information matters most before making a
decision?" — deterministically re-scores the case under the assumption that specific
unresolved (UNKNOWN) signals get verified, one at a time, cumulatively, ranked by how
much weight each signal carries across the scenarios it appears in.

This is pure deterministic re-scoring, matching the project's ground rule that
deterministic code does the math; Gemma never invents these numbers. Each step assumes
verification resolves in the exculpatory direction — the same assumption spec §19's own
worked example uses ("if invoice is verified", "if beneficiaries are verified suppliers"),
i.e. towards MATCH for LEGITIMATE/UNCERTAIN scenarios and towards CONTRADICT for
SUSPICIOUS scenarios, since a SUSPICIOUS scenario's "unknown" signal being cleared is what
resolving it in the customer's favor looks like.
"""

from backend.app.intelligence.scenario_engine.match_scorer import calculate_match_score
from backend.app.schemas.evidence import CounterfactualStep, EvidenceComparison, SignalEvaluation
from backend.app.schemas.scenario import Scenario

MAX_STEPS = 3

_SIGNAL_LABELS = {
    "invoice_exists": "If the invoice is verified",
    "incomplete_documentation": "If the missing documentation is provided",
    "verified_supplier_relationships": "If the supplier relationships are verified",
    "rapid_outgoing_transfers": "If the rapid outgoing transfers are explained",
    "missing_supplier_verification": "If the supplier verification is completed",
    "business_profile_alignment": "If the business profile alignment is confirmed",
    "weak_business_explanation": "If a stronger business explanation is provided",
}


def _label_for(signal_name: str) -> str:
    return _SIGNAL_LABELS.get(signal_name, f"If {signal_name.replace('_', ' ')} is verified")


def _rank_resolvable_signals(comparisons: list[EvidenceComparison]) -> list[str]:
    """Unique UNKNOWN signal names ranked by total weight across scenarios, descending."""
    weight_by_signal: dict[str, float] = {}
    for comparison in comparisons:
        for signal in comparison.signals:
            if signal.status == "UNKNOWN" and signal.weight > 0:
                weight_by_signal[signal.signal] = (
                    weight_by_signal.get(signal.signal, 0) + signal.weight
                )
    return sorted(weight_by_signal, key=lambda name: weight_by_signal[name], reverse=True)


def _resolve_signal(
    signal: SignalEvaluation, category: str, resolved: set[str]
) -> SignalEvaluation:
    if signal.signal not in resolved or signal.status != "UNKNOWN":
        return signal
    new_status = "CONTRADICT" if category == "SUSPICIOUS" else "MATCH"
    return signal.model_copy(update={"status": new_status})


def compute_counterfactual(
    *,
    comparisons: list[EvidenceComparison],
    scenarios: list[Scenario],
    anomaly_score: int,
    current_risk_score: int,
    max_steps: int = MAX_STEPS,
) -> list[CounterfactualStep]:
    category_by_scenario = {scenario.scenario_id: scenario.category for scenario in scenarios}
    ranked_signals = _rank_resolvable_signals(comparisons)[:max_steps]
    if not ranked_signals:
        return []

    steps: list[CounterfactualStep] = []
    resolved: set[str] = set()
    previous_risk = current_risk_score

    for signal_name in ranked_signals:
        resolved.add(signal_name)
        suspicious_match_scores = []
        for comparison in comparisons:
            category = category_by_scenario.get(comparison.scenario_id, "UNCERTAIN")
            new_signals = [_resolve_signal(s, category, resolved) for s in comparison.signals]
            if category == "SUSPICIOUS":
                # Only a suspicious-scenario match should push risk up; a strong match
                # against a LEGITIMATE/UNCERTAIN scenario explains the transaction away
                # and must not itself be read as risk.
                suspicious_match_scores.append(calculate_match_score(new_signals))

        new_risk = min(
            100, max(anomaly_score, round(max(suspicious_match_scores, default=0) * 100))
        )
        steps.append(
            CounterfactualStep(
                condition=_label_for(signal_name), from_score=previous_risk, to_score=new_risk
            )
        )
        previous_risk = new_risk

    return steps
