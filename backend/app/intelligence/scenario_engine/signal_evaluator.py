from backend.app.schemas.anomaly import AnomalyAssessment
from backend.app.schemas.evidence import SignalEvaluation
from backend.app.schemas.scenario import ExpectedSignal
from backend.app.schemas.transaction import TransactionInput


def evaluate_signal(
    signal: ExpectedSignal, transaction: TransactionInput, anomaly: AnomalyAssessment
) -> SignalEvaluation:
    features = anomaly.features
    name = signal.signal

    if name == "large_incoming_transaction":
        status = "MATCH" if features.get("amount_multiplier_vs_p95", 0) >= 3 else "PARTIAL"
        observed = str(transaction.amount)
    elif name in {
        "new_beneficiaries",
        "verified_supplier_relationships",
        "missing_supplier_verification",
    }:
        status = (
            "UNKNOWN"
            if name.startswith("verified")
            else ("MATCH" if features.get("is_new_beneficiary") else "CONTRADICT")
        )
        observed = transaction.beneficiary_id
    elif name == "rapid_outgoing_transfers":
        status = "MATCH" if features.get("hourly_velocity", 0) > 4 else "UNKNOWN"
        observed = str(features.get("hourly_velocity"))
    elif name == "weak_business_explanation":
        status = "PARTIAL"
        observed = None
    elif name in {"invoice_exists", "incomplete_documentation"}:
        status = "UNKNOWN"
        observed = None
    elif name == "business_profile_alignment":
        status = "PARTIAL"
        observed = None
    else:
        status = "UNKNOWN"
        observed = None

    return SignalEvaluation(
        signal=name,
        status=status,
        weight=signal.weight,
        observed_value=observed,
        explanation=f"{name} evaluated as {status.lower().replace('_', ' ')}.",
    )
