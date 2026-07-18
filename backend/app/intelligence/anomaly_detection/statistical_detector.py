from backend.app.schemas.financial_twin import FinancialTwin
from backend.app.schemas.transaction import TransactionInput


def calculate_features(
    transaction: TransactionInput, twin: FinancialTwin, hourly_velocity: int = 1
) -> dict[str, float | int | bool | str | None]:
    p95 = twin.amount_profile.p95 or max(twin.amount_profile.median, 1)
    return {
        "amount_multiplier_vs_p95": round(transaction.amount / p95, 2),
        "amount_percentile": 0.99 if transaction.amount > p95 else 0.5,
        "is_new_beneficiary": bool(
            transaction.beneficiary_id
            and transaction.beneficiary_id not in twin.beneficiary_profile.known_beneficiary_ids
        ),
        "is_new_country": transaction.country not in twin.geography_profile.common_countries,
        "hourly_velocity": hourly_velocity,
    }
