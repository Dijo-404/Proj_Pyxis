"""In-memory case storage dedicated to the recovered risk engine."""

from backend.app.schemas.risk_case import RiskCaseResponse


class RiskEngineCaseRepository:
    """Keep simulated cases separate from SQLite compliance cases."""

    def __init__(self) -> None:
        self._cases: dict[str, RiskCaseResponse] = {}

    def save(self, risk_case: RiskCaseResponse) -> RiskCaseResponse:
        self._cases[risk_case.case_id] = risk_case
        return risk_case

    def get(self, case_id: str) -> RiskCaseResponse | None:
        return self._cases.get(case_id)
