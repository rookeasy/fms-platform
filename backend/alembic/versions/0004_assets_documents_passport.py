"""assets documents passport foundation

Revision ID: 0004_assets_documents_passport
Revises: 0003_core_domain_alignment
Create Date: 2026-06-30
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0004_assets_documents_passport"
down_revision: str | Sequence[str] | None = "0003_core_domain_alignment"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def add_column_if_missing(table_name: str, column: sa.Column) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {item["name"] for item in inspector.get_columns(table_name)}
    if column.name not in existing_columns:
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
    add_column_if_missing("asset_types", sa.Column("category", sa.String(80), nullable=True))
    add_column_if_missing("asset_types", sa.Column("default_inspection_frequency_months", sa.Integer(), nullable=True))

    add_column_if_missing("assets", sa.Column("asset_tag", sa.String(120), nullable=True))
    add_column_if_missing("assets", sa.Column("location_description", sa.Text(), nullable=True))
    add_column_if_missing("assets", sa.Column("manufacturer", sa.Text(), nullable=True))
    add_column_if_missing("assets", sa.Column("model", sa.Text(), nullable=True))
    add_column_if_missing("assets", sa.Column("installation_date", sa.Date(), nullable=True))
    add_column_if_missing("assets", sa.Column("warranty_expiry_date", sa.Date(), nullable=True))
    add_column_if_missing("assets", sa.Column("condition_rating", sa.String(50), nullable=True))
    add_column_if_missing("assets", sa.Column("inspection_frequency_months", sa.Integer(), nullable=True))
    add_column_if_missing("assets", sa.Column("last_inspected_at", sa.DateTime(timezone=True), nullable=True))
    add_column_if_missing("assets", sa.Column("next_inspection_due_at", sa.DateTime(timezone=True), nullable=True))
    add_column_if_missing("assets", sa.Column("replacement_cost_estimate", sa.Numeric(14, 2), nullable=True))
    add_column_if_missing("assets", sa.Column("remaining_useful_life_years", sa.Integer(), nullable=True))
    add_column_if_missing("assets", sa.Column("notes", sa.Text(), nullable=True))

    add_column_if_missing("documents", sa.Column("title", sa.String(255), nullable=True))
    add_column_if_missing("documents", sa.Column("description", sa.Text(), nullable=True))
    add_column_if_missing("documents", sa.Column("original_filename", sa.String(255), nullable=True))
    add_column_if_missing("documents", sa.Column("storage_bucket", sa.String(255), nullable=True))
    add_column_if_missing("documents", sa.Column("storage_key", sa.Text(), nullable=True))
    add_column_if_missing("documents", sa.Column("file_mime_type", sa.String(120), nullable=True))
    add_column_if_missing("documents", sa.Column("file_size_bytes", sa.Integer(), nullable=True))
    add_column_if_missing("documents", sa.Column("version_number", sa.Integer(), nullable=False, server_default="1"))
    add_column_if_missing("documents", sa.Column("parent_document_id", postgresql.UUID(as_uuid=True), nullable=True))
    add_column_if_missing("documents", sa.Column("generated_by_system", sa.Boolean(), nullable=False, server_default=sa.false()))
    add_column_if_missing("documents", sa.Column("effective_date", sa.Date(), nullable=True))
    add_column_if_missing("documents", sa.Column("expiry_date", sa.Date(), nullable=True))
    add_column_if_missing("documents", sa.Column("is_public_to_client", sa.Boolean(), nullable=False, server_default=sa.false()))
    add_column_if_missing("documents", sa.Column("is_passport_record", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.execute("UPDATE documents SET title = name WHERE title IS NULL")
    op.execute("UPDATE documents SET original_filename = name WHERE original_filename IS NULL")
    op.execute("UPDATE documents SET storage_key = storage_uri WHERE storage_key IS NULL")
    op.execute("UPDATE documents SET file_mime_type = mime_type WHERE file_mime_type IS NULL")
    op.alter_column("documents", "building_id", existing_type=postgresql.UUID(as_uuid=True), nullable=False)

    create_fk_if_missing(
        "fk_documents_parent_document_id_documents",
        "documents",
        "documents",
        ["parent_document_id"],
        ["id"],
    )
    create_index_if_missing("ix_documents_org_building_type", "documents", ["organization_id", "building_id", "document_type"])
    create_index_if_missing("ix_documents_passport_record", "documents", ["building_id", "is_passport_record"])
    create_index_if_missing("ix_documents_parent_document_id", "documents", ["parent_document_id"])


def downgrade() -> None:
    op.drop_index("ix_documents_parent_document_id", table_name="documents")
    op.drop_index("ix_documents_passport_record", table_name="documents")
    op.drop_index("ix_documents_org_building_type", table_name="documents")
    op.drop_constraint("fk_documents_parent_document_id_documents", "documents", type_="foreignkey")
    op.alter_column("documents", "building_id", existing_type=postgresql.UUID(as_uuid=True), nullable=True)
    for column_name in [
        "is_passport_record",
        "is_public_to_client",
        "expiry_date",
        "effective_date",
        "generated_by_system",
        "parent_document_id",
        "version_number",
        "file_size_bytes",
        "file_mime_type",
        "storage_key",
        "storage_bucket",
        "original_filename",
        "description",
        "title",
    ]:
        op.drop_column("documents", column_name)
    for column_name in [
        "notes",
        "remaining_useful_life_years",
        "replacement_cost_estimate",
        "next_inspection_due_at",
        "last_inspected_at",
        "inspection_frequency_months",
        "condition_rating",
        "warranty_expiry_date",
        "installation_date",
        "model",
        "manufacturer",
        "location_description",
        "asset_tag",
    ]:
        op.drop_column("assets", column_name)
    op.drop_column("asset_types", "default_inspection_frequency_months")
    op.drop_column("asset_types", "category")
