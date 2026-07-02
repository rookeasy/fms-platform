"""property intelligence platform

Revision ID: 0006_property_intelligence
Revises: 0005_property_campus_management
Create Date: 2026-07-02
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0006_property_intelligence"
down_revision: str | Sequence[str] | None = "0005_property_campus_management"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def create_index_if_missing(index_name: str, table_name: str, columns: list[str], unique: bool = False) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_indexes = {item["name"] for item in inspector.get_indexes(table_name)}
    if index_name not in existing_indexes:
        op.create_index(index_name, table_name, columns, unique=unique)


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    ]


def upgrade() -> None:
    if not table_exists("property_intelligence_snapshots"):
        op.create_table(
            "property_intelligence_snapshots",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
            sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
            sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("calculation_version", sa.String(40), nullable=False, server_default="m7-001"),
            sa.Column("health_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("confidence_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("risk_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("readiness_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("passport_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("building_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("shared_infrastructure_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("asset_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("document_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("passport_record_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("client_visible_record_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("open_deficiency_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("overdue_work_order_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("capital_exposure_estimate", sa.Numeric(14, 2), nullable=False, server_default="0"),
            sa.Column("summary", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            *timestamps(),
            sa.CheckConstraint("health_score >= 0 AND health_score <= 100", name="ck_property_intelligence_health_score_range"),
            sa.CheckConstraint("confidence_score >= 0 AND confidence_score <= 100", name="ck_property_intelligence_confidence_score_range"),
            sa.CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="ck_property_intelligence_risk_score_range"),
            sa.CheckConstraint("readiness_score >= 0 AND readiness_score <= 100", name="ck_property_intelligence_readiness_score_range"),
            sa.CheckConstraint("passport_score >= 0 AND passport_score <= 100", name="ck_property_intelligence_passport_score_range"),
        )

    if not table_exists("property_intelligence_factors"):
        op.create_table(
            "property_intelligence_factors",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
            sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
            sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("property_intelligence_snapshots.id"), nullable=True),
            sa.Column("category", sa.String(80), nullable=False),
            sa.Column("factor_key", sa.String(120), nullable=False),
            sa.Column("label", sa.String(255), nullable=False),
            sa.Column("severity", sa.String(50), nullable=False, server_default="info"),
            sa.Column("source_type", sa.String(80), nullable=True),
            sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("impact_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            *timestamps(),
        )

    create_index_if_missing("ix_property_intelligence_snapshots_organization_id", "property_intelligence_snapshots", ["organization_id"])
    create_index_if_missing("ix_property_intelligence_snapshots_property_id", "property_intelligence_snapshots", ["property_id"])
    create_index_if_missing(
        "ix_property_intelligence_snapshots_property_calculated_at",
        "property_intelligence_snapshots",
        ["property_id", "calculated_at"],
    )
    create_index_if_missing("ix_property_intelligence_factors_organization_id", "property_intelligence_factors", ["organization_id"])
    create_index_if_missing("ix_property_intelligence_factors_property_id", "property_intelligence_factors", ["property_id"])
    create_index_if_missing("ix_property_intelligence_factors_snapshot_id", "property_intelligence_factors", ["snapshot_id"])
    create_index_if_missing("ix_property_intelligence_factors_category", "property_intelligence_factors", ["property_id", "category"])


def downgrade() -> None:
    op.drop_index("ix_property_intelligence_factors_category", table_name="property_intelligence_factors")
    op.drop_index("ix_property_intelligence_factors_snapshot_id", table_name="property_intelligence_factors")
    op.drop_index("ix_property_intelligence_factors_property_id", table_name="property_intelligence_factors")
    op.drop_index("ix_property_intelligence_factors_organization_id", table_name="property_intelligence_factors")
    op.drop_index("ix_property_intelligence_snapshots_property_calculated_at", table_name="property_intelligence_snapshots")
    op.drop_index("ix_property_intelligence_snapshots_property_id", table_name="property_intelligence_snapshots")
    op.drop_index("ix_property_intelligence_snapshots_organization_id", table_name="property_intelligence_snapshots")
    op.drop_table("property_intelligence_factors")
    op.drop_table("property_intelligence_snapshots")
