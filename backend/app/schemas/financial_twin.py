from pydantic import BaseModel, Field


class AmountProfile(BaseModel):
    median: float = 0
    p95: float = 0
    trusted_min: float = 0
    trusted_max: float = 0


class VelocityProfile(BaseModel):
    average_transactions_per_day: float = 0
    maximum_normal_hourly_count: int = 0


class BeneficiaryProfile(BaseModel):
    known_beneficiaries: int = 0
    known_beneficiary_ratio: float = 0
    known_beneficiary_ids: list[str] = Field(default_factory=list)


class GeographyProfile(BaseModel):
    common_countries: list[str] = Field(default_factory=list)
    international_transfer_frequency: float = 0


class TimeProfile(BaseModel):
    usual_start_hour: int = 0
    usual_end_hour: int = 23


class BusinessProfile(BaseModel):
    business_type: str | None = None
    expected_monthly_turnover: float | None = None


class BehaviorProfile(BaseModel):
    customer_id: str
    amount_profile: AmountProfile = Field(default_factory=AmountProfile)
    velocity_profile: VelocityProfile = Field(default_factory=VelocityProfile)
    beneficiary_profile: BeneficiaryProfile = Field(default_factory=BeneficiaryProfile)
    geography_profile: GeographyProfile = Field(default_factory=GeographyProfile)
    time_profile: TimeProfile = Field(default_factory=TimeProfile)

    @classmethod
    def for_empty_customer(cls, customer_id: str) -> "BehaviorProfile":
        return cls(customer_id=customer_id)


class FinancialTwin(BehaviorProfile):
    version: int = 1
    business_profile: BusinessProfile = Field(default_factory=BusinessProfile)

    @classmethod
    def demo_baseline(cls, customer_id: str) -> "FinancialTwin":
        return cls(
            customer_id=customer_id,
            version=1,
            amount_profile=AmountProfile(
                median=42000, p95=125000, trusted_min=10000, trusted_max=150000
            ),
            velocity_profile=VelocityProfile(
                average_transactions_per_day=3.2, maximum_normal_hourly_count=4
            ),
            beneficiary_profile=BeneficiaryProfile(
                known_beneficiaries=8,
                known_beneficiary_ratio=0.92,
                known_beneficiary_ids=["BEN-001", "BEN-002", "BEN-003"],
            ),
            geography_profile=GeographyProfile(
                common_countries=["India"], international_transfer_frequency=0.03
            ),
            time_profile=TimeProfile(usual_start_hour=8, usual_end_hour=21),
            business_profile=BusinessProfile(
                business_type="Textile Retail", expected_monthly_turnover=700000
            ),
        )
