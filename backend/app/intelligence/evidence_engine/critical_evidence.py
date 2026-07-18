from backend.app.schemas.evidence import DecisionCriticalEvidence, EvidenceComparison


def find_decision_critical_evidence(
    comparisons: list[EvidenceComparison],
) -> DecisionCriticalEvidence:
    unknown_signals = [
        signal
        for comparison in comparisons
        for signal in comparison.signals
        if signal.status == "UNKNOWN"
    ]
    if not unknown_signals:
        return DecisionCriticalEvidence(
            question="What additional verified evidence would clarify this case?",
            why_it_matters=(
                "The current evidence does not expose a single unresolved high-impact signal."
            ),
            recommended_action="Review supporting documents and beneficiary relationships.",
        )

    top_signal = max(unknown_signals, key=lambda signal: signal.weight)
    readable = top_signal.signal.replace("_", " ")
    return DecisionCriticalEvidence(
        question=f"Can the {readable} be verified?",
        why_it_matters=(
            f"The unresolved signal '{readable}' has the highest scenario weight among "
            "unknown evidence."
        ),
        recommended_action=f"Collect and verify records related to {readable}.",
    )
