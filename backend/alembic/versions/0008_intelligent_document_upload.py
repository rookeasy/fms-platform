"""intelligent document upload and asset extraction

Revision ID: 0008_intelligent_docs
Revises: 0007_passport_queue
Create Date: 2026-07-13
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0008_intelligent_docs"
down_revision: str | Sequence[str] | None = "0007_passport_queue"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if not column_exists(table_name, column.name):
        op.add_column(table_name, column)


def create_index_if_missing(index_name: str, table_name: str, columns: list[str], unique: bool = False) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_indexes = {item["name"] for item in inspector.get_indexes(table_name)}
    if index_name not in existing_indexes:
        op.create_index(index_name, table_name, columns, unique=unique)


def create_fk_if_missing(name: str, source_table: str, referent_table: str, local_cols: list[str], remote_cols: list[str]) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {item["name"] for item in inspector.get_foreign_keys(source_table)}
    if name not in existing:
        op.create_foreign_key(name, source_table, referent_table, local_cols, remote_cols)


def upgrade() -> None:
    add_column_if_missing("assets", sa.Column("source_document_id", postgresql.UUID(as_uuid=True), nullable=True))
    create_fk_if_missing("fk_assets_source_document_id_documents", "assets", "documents", ["source_document_id"], ["id"])
    create_index_if_missing("ix_assets_source_document_id", "assets", ["source_document_id"])

    add_column_if_missing("documents", sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=True))
    add_column_if_missing("documents", sa.Column("evidence_category", sa.String(120), nullable=True))
    add_column_if_missing("documents", sa.Column("drawing_number", sa.String(120), nullable=True))
    add_column_if_missing("documents", sa.Column("revision", sa.String(80), nullable=True))
    add_column_if_missing("documents", sa.Column("issue_date", sa.Date(), nullable=True))
    add_column_if_missing("documents", sa.Column("status", sa.String(50), nullable=False, server_default="draft"))
    add_column_if_missing("documents", sa.Column("internal_only", sa.Boolean(), nullable=False, server_default=sa.text("true")))
    add_column_if_missing("documents", sa.Column("extraction_status", sa.String(50), nullable=False, server_default="pending"))
    add_column_if_missing("documents", sa.Column("extraction_source", sa.String(80), nullable=True))
    add_column_if_missing("documents", sa.Column("extraction_summary", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    add_column_if_missing("documents", sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True))
    add_column_if_missing("documents", sa.Column("notes", sa.Text(), nullable=True))

    create_fk_if_missing("fk_documents_property_id_properties", "documents", "properties", ["property_id"], ["id"])
    create_index_if_missing("ix_documents_property_id", "documents", ["property_id"])
    create_index_if_missing("ix_documents_extraction_status", "documents", ["extraction_status"])
    create_index_if_missing("ix_documents_evidence_category", "documents", ["evidence_category"])

    op.execute("UPDATE documents SET property_id = buildings.property_id FROM buildings WHERE documents.building_id = buildings.id AND documents.property_id IS NULL")
    op.execute("UPDATE documents SET internal_only = NOT (is_public_to_client OR is_passport_record) WHERE internal_only IS NULL")

    if not table_exists("document_asset_suggestions"):
        op.create_table(
            "document_asset_suggestions",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
            sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=False),
            sa.Column("building_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buildings.id"), nullable=True),
            sa.Column("asset_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("asset_types.id"), nullable=True),
            sa.Column("approved_asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id"), nullable=True),
            sa.Column("suggested_asset_type", sa.String(120), nullable=False),
            sa.Column("suggested_name", sa.String(255), nullable=False),
            sa.Column("location_description", sa.Text(), nullable=True),
            sa.Column("manufacturer", sa.Text(), nullable=True),
            sa.Column("model", sa.Text(), nullable=True),
            sa.Column("confidence", sa.Integer(), nullable=False, server_default="50"),
            sa.Column("evidence_snippet", sa.Text(), nullable=True),
            sa.Column("extraction_source", sa.String(80), nullable=False, server_default="rule_based"),
            sa.Column("review_status", sa.String(50), nullable=False, server_default="review_required"),
            sa.Column("reviewed_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        )

    create_index_if_missing("ix_document_asset_suggestions_organization_id", "document_asset_suggestions", ["organization_id"])
    create_index_if_missing("ix_document_asset_suggestions_document_id", "document_asset_suggestions", ["document_id"])
    create_index_if_missing("ix_document_asset_suggestions_building_id", "document_asset_suggestions", ["building_id"])
    create_index_if_missing("ix_document_asset_suggestions_review_status", "document_asset_suggestions", ["review_status"])


def downgrade() -> None:
    if table_exists("document_asset_suggestions"):
        op.drop_table("document_asset_suggestions")
    for index_name in [
        "ix_documents_evidence_category",
        "ix_documents_extraction_status",
        "ix_documents_property_id",
        "ix_assets_source_document_id",
    ]:
        try:
            op.drop_index(index_name, table_name="documents" if index_name.startswith("ix_documents") else "assets")
        except Exception:
            pass
    for column_name in [
        "notes",
        "archived_at",
        "extraction_summary",
        "extraction_source",
        "extraction_status",
        "internal_only",
        "status",
        "issue_date",
        "revision",
        "drawing_number",
        "evidence_category",
        "property_id",
    ]:
        if column_exists("documents", column_name):
            op.drop_column("documents", column_name)
    if column_exists("assets", "source_document_id"):
        op.drop_column("assets", "source_document_id")
