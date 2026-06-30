"""mvp schema

Revision ID: 0002_mvp_schema
Revises: 0001_initial_foundation
Create Date: 2026-06-30
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002_mvp_schema"
down_revision: str | Sequence[str] | None = "0001_initial_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def uuid_pk() -> sa.Column:
    return sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"))


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    ]


def deleted_at() -> sa.Column:
    return sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)


def org_fk(nullable: bool = False) -> sa.Column:
    return sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=nullable)


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        "organizations",
        uuid_pk(),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        *timestamps(),
        deleted_at(),
        sa.UniqueConstraint("slug", name="uq_organizations_slug"),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"])
    op.create_index("ix_organizations_status", "organizations", ["status"])

    op.create_table(
        "users",
        uuid_pk(),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        *timestamps(),
        deleted_at(),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_status", "users", ["status"])

    op.create_table(
        "roles",
        uuid_pk(),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        *timestamps(),
        sa.UniqueConstraint("name", name="uq_roles_name"),
    )

    op.create_table(
        "membership_plans",
        uuid_pk(),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("code", sa.String(80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("monthly_price", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *timestamps(),
        deleted_at(),
        sa.UniqueConstraint("name", name="uq_membership_plans_name"),
        sa.UniqueConstraint("code", name="uq_membership_plans_code"),
    )
    op.create_index("ix_membership_plans_code", "membership_plans", ["code"])

    op.create_table(
        "organization_users",
        uuid_pk(),
        org_fk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        *timestamps(),
        sa.UniqueConstraint("organization_id", "user_id", "role_id", name="uq_organization_users_org_user_role"),
    )
    op.create_index("ix_organization_users_organization_id", "organization_users", ["organization_id"])
    op.create_index("ix_organization_users_user_id", "organization_users", ["user_id"])

    op.create_table(
        "buildings",
        uuid_pk(),
        org_fk(),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(80), nullable=True),
        sa.Column("address_line1", sa.String(255), nullable=False),
        sa.Column("city", sa.String(120), nullable=False),
        sa.Column("region", sa.String(120), nullable=True),
        sa.Column("country", sa.String(120), nullable=False, server_default="Canada"),
        sa.Column("postal_code", sa.String(30), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        *timestamps(),
        deleted_at(),
        sa.UniqueConstraint("organization_id", "code", name="uq_buildings_org_code"),
    )
    op.create_index("ix_buildings_organization_id", "buildings", ["organization_id"])
    op.create_index("ix_buildings_org_status", "buildings", ["organization_id", "status"])
    op.create_index("ix_buildings_org_name", "buildings", ["organization_id", "name"])

    op.create_table(
        "asset_types",
        uuid_pk(),
        org_fk(nullable=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("code", sa.String(80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        *timestamps(),
        deleted_at(),
        sa.UniqueConstraint("organization_id", "code", name="uq_asset_types_org_code"),
    )
    op.create_index("ix_asset_types_organization_id", "asset_types", ["organization_id"])
    op.create_index("ix_asset_types_code", "asset_types", ["code"])

    op.create_table(
        "memberships",
        uuid_pk(),
        org_fk(),
        sa.Column("membership_plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("membership_plans.id"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=True),
        *timestamps(),
        deleted_at(),
    )
    op.create_index("ix_memberships_organization_id", "memberships", ["organization_id"])
    op.create_index("ix_memberships_membership_plan_id", "memberships", ["membership_plan_id"])
    op.create_index("ix_memberships_org_status", "memberships", ["organization_id", "status"])

    op.create_table(
        "building_contacts",
        uuid_pk(),
        org_fk(),
        sa.Column("building_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buildings.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(60), nullable=True),
        sa.Column("contact_type", sa.String(80), nullable=False),
        *timestamps(),
        deleted_at(),
    )
    op.create_index("ix_building_contacts_organization_id", "building_contacts", ["organization_id"])
    op.create_index("ix_building_contacts_building_id", "building_contacts", ["building_id"])

    op.create_table(
        "assets",
        uuid_pk(),
        org_fk(),
        sa.Column("building_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buildings.id"), nullable=False),
        sa.Column("asset_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("asset_types.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("tag", sa.String(120), nullable=True),
        sa.Column("serial_number", sa.String(120), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("installed_on", sa.Date(), nullable=True),
        *timestamps(),
        deleted_at(),
        sa.UniqueConstraint("organization_id", "tag", name="uq_assets_org_tag"),
    )
    op.create_index("ix_assets_organization_id", "assets", ["organization_id"])
    op.create_index("ix_assets_building_id", "assets", ["building_id"])
    op.create_index("ix_assets_asset_type_id", "assets", ["asset_type_id"])
    op.create_index("ix_assets_org_status", "assets", ["organization_id", "status"])

    op.create_table(
        "inspection_templates",
        uuid_pk(),
        org_fk(),
        sa.Column("asset_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("asset_types.id"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        *timestamps(),
        deleted_at(),
    )
    op.create_index("ix_inspection_templates_organization_id", "inspection_templates", ["organization_id"])
    op.create_index("ix_inspection_templates_asset_type_id", "inspection_templates", ["asset_type_id"])
    op.create_index("ix_inspection_templates_org_status", "inspection_templates", ["organization_id", "status"])

    op.create_table(
        "documents",
        uuid_pk(),
        org_fk(),
        sa.Column("building_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buildings.id"), nullable=True),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id"), nullable=True),
        sa.Column("uploaded_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("document_type", sa.String(80), nullable=False),
        sa.Column("storage_uri", sa.Text(), nullable=False),
        sa.Column("mime_type", sa.String(120), nullable=True),
        *timestamps(),
        deleted_at(),
    )
    op.create_index("ix_documents_organization_id", "documents", ["organization_id"])
    op.create_index("ix_documents_building_id", "documents", ["building_id"])
    op.create_index("ix_documents_asset_id", "documents", ["asset_id"])
    op.create_index("ix_documents_org_type", "documents", ["organization_id", "document_type"])

    op.create_table(
        "work_orders",
        uuid_pk(),
        org_fk(),
        sa.Column("building_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buildings.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id"), nullable=True),
        sa.Column("assigned_to_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("priority", sa.String(50), nullable=False, server_default="medium"),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        deleted_at(),
    )
    op.create_index("ix_work_orders_organization_id", "work_orders", ["organization_id"])
    op.create_index("ix_work_orders_building_id", "work_orders", ["building_id"])
    op.create_index("ix_work_orders_assigned_to_user_id", "work_orders", ["assigned_to_user_id"])
    op.create_index("ix_work_orders_org_status", "work_orders", ["organization_id", "status"])
    op.create_index("ix_work_orders_org_priority", "work_orders", ["organization_id", "priority"])

    op.create_table(
        "inspection_template_items",
        uuid_pk(),
        org_fk(),
        sa.Column("inspection_template_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inspection_templates.id"), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("response_type", sa.String(80), nullable=False, server_default="pass_fail"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.true()),
        *timestamps(),
        deleted_at(),
    )
    op.create_index("ix_inspection_template_items_organization_id", "inspection_template_items", ["organization_id"])
    op.create_index("ix_inspection_template_items_template_id", "inspection_template_items", ["inspection_template_id"])

    op.create_table(
        "inspections",
        uuid_pk(),
        org_fk(),
        sa.Column("building_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buildings.id"), nullable=False),
        sa.Column("inspection_template_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inspection_templates.id"), nullable=True),
        sa.Column("inspector_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="scheduled"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        deleted_at(),
    )
    op.create_index("ix_inspections_organization_id", "inspections", ["organization_id"])
    op.create_index("ix_inspections_building_id", "inspections", ["building_id"])
    op.create_index("ix_inspections_org_status", "inspections", ["organization_id", "status"])
    op.create_index("ix_inspections_scheduled_at", "inspections", ["scheduled_at"])

    op.create_table(
        "inspection_responses",
        uuid_pk(),
        org_fk(),
        sa.Column("inspection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inspections.id"), nullable=False),
        sa.Column("inspection_template_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inspection_template_items.id"), nullable=False),
        sa.Column("value", postgresql.JSONB(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *timestamps(),
        deleted_at(),
        sa.UniqueConstraint("inspection_id", "inspection_template_item_id", name="uq_inspection_responses_inspection_item"),
    )
    op.create_index("ix_inspection_responses_organization_id", "inspection_responses", ["organization_id"])
    op.create_index("ix_inspection_responses_inspection_id", "inspection_responses", ["inspection_id"])

    op.create_table(
        "deficiencies",
        uuid_pk(),
        org_fk(),
        sa.Column("building_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buildings.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id"), nullable=True),
        sa.Column("inspection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inspections.id"), nullable=True),
        sa.Column("assigned_to_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("severity", sa.String(50), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        deleted_at(),
    )
    op.create_index("ix_deficiencies_organization_id", "deficiencies", ["organization_id"])
    op.create_index("ix_deficiencies_building_id", "deficiencies", ["building_id"])
    op.create_index("ix_deficiencies_org_status", "deficiencies", ["organization_id", "status"])
    op.create_index("ix_deficiencies_org_severity", "deficiencies", ["organization_id", "severity"])

    op.create_table(
        "reports",
        uuid_pk(),
        org_fk(),
        sa.Column("building_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buildings.id"), nullable=True),
        sa.Column("generated_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("report_type", sa.String(80), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        deleted_at(),
    )
    op.create_index("ix_reports_organization_id", "reports", ["organization_id"])
    op.create_index("ix_reports_building_id", "reports", ["building_id"])
    op.create_index("ix_reports_org_type", "reports", ["organization_id", "report_type"])

    op.create_table(
        "certificates",
        uuid_pk(),
        org_fk(),
        sa.Column("building_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buildings.id"), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id"), nullable=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("certificate_type", sa.String(80), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="current"),
        sa.Column("issued_on", sa.Date(), nullable=True),
        sa.Column("expires_on", sa.Date(), nullable=True),
        *timestamps(),
        deleted_at(),
    )
    op.create_index("ix_certificates_organization_id", "certificates", ["organization_id"])
    op.create_index("ix_certificates_building_id", "certificates", ["building_id"])
    op.create_index("ix_certificates_org_status", "certificates", ["organization_id", "status"])
    op.create_index("ix_certificates_expires_on", "certificates", ["expires_on"])

    op.create_table(
        "health_scores",
        uuid_pk(),
        org_fk(),
        sa.Column("building_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buildings.id"), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("score_type", sa.String(80), nullable=False, server_default="overall"),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("inputs", postgresql.JSONB(), nullable=True),
        *timestamps(),
        sa.CheckConstraint("score >= 0 AND score <= 100", name="ck_health_scores_score_range"),
    )
    op.create_index("ix_health_scores_organization_id", "health_scores", ["organization_id"])
    op.create_index("ix_health_scores_building_id", "health_scores", ["building_id"])
    op.create_index("ix_health_scores_building_calculated_at", "health_scores", ["building_id", "calculated_at"])

    op.create_table(
        "notifications",
        uuid_pk(),
        org_fk(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("notification_type", sa.String(80), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
    )
    op.create_index("ix_notifications_organization_id", "notifications", ["organization_id"])
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_user_read_at", "notifications", ["user_id", "read_at"])

    op.create_table(
        "audit_logs",
        uuid_pk(),
        org_fk(nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("entity_type", sa.String(120), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        *timestamps(),
    )
    op.create_index("ix_audit_logs_organization_id", "audit_logs", ["organization_id"])
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_entity", "audit_logs", ["entity_type", "entity_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    for table in [
        "audit_logs",
        "notifications",
        "health_scores",
        "certificates",
        "reports",
        "deficiencies",
        "inspection_responses",
        "inspections",
        "inspection_template_items",
        "work_orders",
        "documents",
        "inspection_templates",
        "assets",
        "building_contacts",
        "memberships",
        "asset_types",
        "buildings",
        "organization_users",
        "membership_plans",
        "roles",
        "users",
        "organizations",
    ]:
        op.drop_table(table)
