from backend.app.schemas.customer import CustomerProfile
from backend.app.schemas.financial_twin import BehaviorProfile, BusinessProfile, FinancialTwin


def build_financial_twin(
    customer: CustomerProfile, behavior: BehaviorProfile, version: int = 1
) -> FinancialTwin:
    return FinancialTwin(
        customer_id=customer.customer_id,
        version=version,
        amount_profile=behavior.amount_profile,
        velocity_profile=behavior.velocity_profile,
        beneficiary_profile=behavior.beneficiary_profile,
        geography_profile=behavior.geography_profile,
        time_profile=behavior.time_profile,
        business_profile=BusinessProfile(
            business_type=customer.declared_business,
            expected_monthly_turnover=customer.declared_monthly_turnover,
        ),
    )
