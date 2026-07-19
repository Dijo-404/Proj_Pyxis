"""Seed SQLite with deterministic, realistic synthetic compliance data."""

import argparse
import json
from datetime import timedelta

from backend.app.core.database import SessionLocal, initialize_database
from backend.app.models.case import RiskCase
from backend.app.models.compliance_report import ComplianceReport
from backend.app.schemas.case import RiskCaseImport
from backend.app.services.case_service import CaseService
from data_pipeline.synthetic_data.dataset import generate_case_dataset


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20260718)
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace existing local cases. Use only for disposable development databases.",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    initialize_database()
    generated = generate_case_dataset(seed=arguments.seed)
    inserted = 0
    skipped = 0
    with SessionLocal() as session:
        if arguments.replace:
            for existing in session.query(RiskCase).all():
                session.delete(existing)
            session.commit()

        for item in generated:
            existing = session.get(RiskCase, item.payload["case_id"])
            if existing is not None:
                skipped += 1
                continue
            risk_case = CaseService(session).import_case(
                RiskCaseImport.model_validate(item.payload)
            )
            risk_case.status = item.status
            risk_case.created_at = item.created_at
            risk_case.updated_at = item.updated_at
            session.commit()
            inserted += 1

        for index, item in enumerate(generated[:4], start=1):
            case_id = str(item.payload["case_id"])
            report_id = f"RPT-SYN-{index:04d}"
            if session.get(ComplianceReport, report_id) is not None:
                continue
            session.add(
                ComplianceReport(
                    report_id=report_id,
                    case_id=case_id,
                    status="GENERATED",
                    narrative=(
                        f"Synthetic compliance review for {item.payload['customer_name']}. "
                        "The report contains generated transactions and no real customer data."
                    ),
                    structured_report={
                        "synthetic": True,
                        "case_id": case_id,
                        "risk_score": item.payload["risk_score"],
                    },
                    html_path=f"reports/{case_id}/{report_id}.html",
                    pdf_path=None,
                    generated_by="OFFICER-12",
                    created_at=item.updated_at + timedelta(minutes=12),
                )
            )
        session.commit()

    print(
        json.dumps(
            {"seed": arguments.seed, "inserted_cases": inserted, "skipped_cases": skipped},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
