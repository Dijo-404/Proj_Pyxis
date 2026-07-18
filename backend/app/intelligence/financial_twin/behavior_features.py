from collections import Counter, defaultdict
from statistics import median

from backend.app.schemas.financial_twin import (
    AmountProfile,
    BehaviorProfile,
    BeneficiaryProfile,
    GeographyProfile,
    TimeProfile,
    VelocityProfile,
)
from backend.app.schemas.transaction import TransactionInput


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0
    ordered = sorted(values)
    index = min(len(ordered) - 1, round((pct / 100) * (len(ordered) - 1)))
    return ordered[index]


def build_behavior_profile(customer_id: str, transactions: list[TransactionInput]) -> BehaviorProfile:
    if not transactions:
        return BehaviorProfile.for_empty_customer(customer_id)

    amounts = [transaction.amount for transaction in transactions]
    dates = {transaction.timestamp.date() for transaction in transactions}
    hourly_counts: dict[tuple[object, int], int] = defaultdict(int)
    beneficiaries = [transaction.beneficiary_id for transaction in transactions if transaction.beneficiary_id]
    countries = [transaction.country for transaction in transactions]
    hours = [transaction.timestamp.hour for transaction in transactions]

    for transaction in transactions:
        hourly_counts[(transaction.timestamp.date(), transaction.timestamp.hour)] += 1

    country_counts = Counter(countries)
    common_countries = [country for country, _ in country_counts.most_common()]
    home_country = common_countries[0] if common_countries else None
    international_count = sum(1 for country in countries if home_country and country != home_country)

    return BehaviorProfile(
        customer_id=customer_id,
        amount_profile=AmountProfile(
            median=float(median(amounts)),
            p95=float(percentile(amounts, 95)),
            trusted_min=float(min(amounts)),
            trusted_max=float(percentile(amounts, 95) * 1.2),
        ),
        velocity_profile=VelocityProfile(
            average_transactions_per_day=round(len(transactions) / max(len(dates), 1), 2),
            maximum_normal_hourly_count=max(hourly_counts.values(), default=0),
        ),
        beneficiary_profile=BeneficiaryProfile(
            known_beneficiaries=len(set(beneficiaries)),
            known_beneficiary_ratio=round(len(beneficiaries) / len(transactions), 2),
            known_beneficiary_ids=sorted(set(beneficiaries)),
        ),
        geography_profile=GeographyProfile(
            common_countries=common_countries,
            international_transfer_frequency=round(international_count / len(transactions), 2),
        ),
        time_profile=TimeProfile(usual_start_hour=min(hours), usual_end_hour=max(hours)),
    )

