"""protected state certification

Revision ID: 0009_protected_state
Revises: 0008_intelligent_docs
Create Date: 2026-07-13
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0009_protected_state"
down_revision: str | Sequence[str] | None = "0008_intelligent_docs"
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


def upgrade() -> None:
    if not table_exists("protected_state_certifications"):
        op.create_table(
            "protected_state_certifications",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
            sa.Column("building_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buildings.id"), nullable=False),
            sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=True),
            sa.Column("status", sa.String(50), nullable=False, server_default="review_required"),
            sa.Column("evaluation_version", sa.String(40), nullable=False, server_default="protected-state-mvp-001"),
            sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("evaluated_by", sa.String(255), nullable=True),
            sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("approved_by", sa.String(255), nullable=True),
            sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("reason", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("criteria_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.UniqueConstraint("building_id", name="uq_protected_state_certifications_building"),
        )
    create_index_if_missing("ix_protected_state_certifications_organization_id", "protected_state_certifications", ["organization_id"])
    create_index_if_missing("ix_protected_state_certifications_building_id", "protected_state_certifications", ["building_id"])
    create_index_if_missing("ix_protected_state_certifications_property_id", "protected_state_certifications", ["property_id"])
    create_index_if_missing("ix_protected_state_certifications_status", "protected_state_certifications", ["status"])


def downgrade() -> None:
    if table_exists("protected_state_certifications"):
        op.drop_table("protected_state_certifications")
