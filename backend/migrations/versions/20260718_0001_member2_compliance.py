"""Create Member 2 compliance investigation tables.

Revision ID: 20260718_0001
Revises: None
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260718_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "risk_cases",
        sa.Column("case_id", sa.String(length=128), primary_key=True),
        sa.Column("customer_id", sa.String(length=128), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("anomalies", sa.JSON(), nullable=False),
        sa.Column("decision_critical_evidence", sa.JSON(), nullable=True),
        sa.Column("recommended_actions", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="ck_case_risk_score"),
        sa.CheckConstraint("priority >= 1 AND priority <= 5", name="ck_case_priority"),
    )
    op.create_index("ix_risk_cases_customer_id", "risk_cases", ["customer_id"])
    op.create_index("ix_risk_cases_risk_level", "risk_cases", ["risk_level"])
    op.create_index("ix_risk_cases_status", "risk_cases", ["status"])
    op.create_index("ix_risk_cases_priority", "risk_cases", ["priority"])

    op.create_table(
        "scenarios",
        sa.Column("scenario_id", sa.String(length=128), primary_key=True),
        sa.Column(
            "case_id",
            sa.String(length=128),
            sa.ForeignKey("risk_cases.case_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=16), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("match_score", sa.Float(), nullable=False),
        sa.CheckConstraint(
            "match_score >= 0 AND match_score <= 100", name="ck_scenario_match_score"
        ),
    )
    op.create_index("ix_scenarios_case_id", "scenarios", ["case_id"])
    op.create_index("ix_scenarios_category", "scenarios", ["category"])

    op.create_table(
        "evidence",
        sa.Column("evidence_id", sa.String(length=128), primary_key=True),
        sa.Column(
            "case_id",
            sa.String(length=128),
            sa.ForeignKey("risk_cases.case_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "scenario_id",
            sa.String(length=128),
            sa.ForeignKey("scenarios.scenario_id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("evidence_type", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source_reference", sa.String(length=512), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("submitted_by", sa.String(length=128), nullable=False),
        sa.Column("verification_reason", sa.Text(), nullable=True),
        sa.Column("verified_by", sa.String(length=128), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_evidence_confidence"),
    )
    op.create_index("ix_evidence_case_id", "evidence", ["case_id"])
    op.create_index("ix_evidence_status", "evidence", ["status"])
    op.create_index("ix_evidence_evidence_type", "evidence", ["evidence_type"])

    op.create_table(
        "documents",
        sa.Column("document_id", sa.String(length=128), primary_key=True),
        sa.Column(
            "case_id",
            sa.String(length=128),
            sa.ForeignKey("risk_cases.case_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("customer_id", sa.String(length=128), nullable=False),
        sa.Column("document_type", sa.String(length=64), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=128), nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=False, unique=True),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("extracted_data", sa.JSON(), nullable=False),
        sa.Column("index_entries", sa.JSON(), nullable=False),
        sa.Column("verification_status", sa.String(length=32), nullable=False),
        sa.Column("uploaded_by", sa.String(length=128), nullable=False),
        sa.Column("verified_by", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("size_bytes >= 0", name="ck_document_size"),
    )
    op.create_index("ix_documents_case_id", "documents", ["case_id"])
    op.create_index("ix_documents_customer_id", "documents", ["customer_id"])
    op.create_index("ix_documents_sha256", "documents", ["sha256"])

    op.create_table(
        "reviews",
        sa.Column("review_id", sa.String(length=128), primary_key=True),
        sa.Column(
            "case_id",
            sa.String(length=128),
            sa.ForeignKey("risk_cases.case_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("reviewer_id", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("previous_status", sa.String(length=32), nullable=False),
        sa.Column("resulting_status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_reviews_case_id", "reviews", ["case_id"])
    op.create_index("ix_reviews_action", "reviews", ["action"])

    op.create_table(
        "compliance_reports",
        sa.Column("report_id", sa.String(length=128), primary_key=True),
        sa.Column(
            "case_id",
            sa.String(length=128),
            sa.ForeignKey("risk_cases.case_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("narrative", sa.Text(), nullable=False),
        sa.Column("structured_report", sa.JSON(), nullable=False),
        sa.Column("html_path", sa.String(length=1024), nullable=False),
        sa.Column("pdf_path", sa.String(length=1024), nullable=True),
        sa.Column("generated_by", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_compliance_reports_case_id", "compliance_reports", ["case_id"])
    op.create_index("ix_compliance_reports_status", "compliance_reports", ["status"])

    op.create_table(
        "audit_logs",
        sa.Column("audit_id", sa.String(length=128), primary_key=True),
        sa.Column("case_id", sa.String(length=128), nullable=True),
        sa.Column("actor_type", sa.String(length=32), nullable=False),
        sa.Column("actor_id", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=128), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_logs_case_id", "audit_logs", ["case_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("compliance_reports")
    op.drop_table("reviews")
    op.drop_table("documents")
    op.drop_table("evidence")
    op.drop_table("scenarios")
    op.drop_table("risk_cases")
