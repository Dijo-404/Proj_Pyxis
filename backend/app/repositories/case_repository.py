from backend.app.schemas.risk_case import RiskCaseResponse


class CaseRepository:
    def __init__(self) -> None:
        self._cases: dict[str, RiskCaseResponse] = {}

    def save(self, risk_case: RiskCaseResponse) -> RiskCaseResponse:
        self._cases[risk_case.case_id] = risk_case
        return risk_case

    def get(self, case_id: str) -> RiskCaseResponse | None:
        return self._cases.get(case_id)

