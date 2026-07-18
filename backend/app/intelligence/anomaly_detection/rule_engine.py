from backend.app.schemas.anomaly import TriggeredRule
from backend.app.schemas.financial_twin import FinancialTwin
from backend.app.schemas.transaction import TransactionInput


def evaluate_rules(transaction: TransactionInput, twin: FinancialTwin, hourly_velocity: int = 1) -> list[TriggeredRule]:
    rules: list[TriggeredRule] = []
    p95 = twin.amount_profile.p95 or max(twin.amount_profile.median, 1)

    if transaction.amount > p95 * 3:
        rules.append(TriggeredRule(rule_id="amount_above_customer_p95", severity="HIGH", description="Amount exceeds customer p95 by configured multiplier."))
    if transaction.beneficiary_id and transaction.beneficiary_id not in twin.beneficiary_profile.known_beneficiary_ids:
        rules.append(TriggeredRule(rule_id="new_beneficiary", severity="MEDIUM", description="Transaction uses a beneficiary outside the trusted profile."))
    if transaction.country not in twin.geography_profile.common_countries:
        rules.append(TriggeredRule(rule_id="new_country", severity="MEDIUM", description="Transaction country is outside the usual geography profile."))
    if hourly_velocity > max(twin.velocity_profile.maximum_normal_hourly_count, 1):
        rules.append(TriggeredRule(rule_id="high_hourly_velocity", severity="HIGH", description="Hourly transaction count exceeds normal customer velocity."))
    if not (twin.time_profile.usual_start_hour <= transaction.timestamp.hour <= twin.time_profile.usual_end_hour):
        rules.append(TriggeredRule(rule_id="unusual_time", severity="LOW", description="Transaction occurred outside usual active hours."))

    return rules

