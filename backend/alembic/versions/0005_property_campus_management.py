"""property campus management

Revision ID: 0005_property_campus_management
Revises: 0004_assets_documents_passport
Create Date: 2026-07-02
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0005_property_campus_management"
down_revision: str | Sequence[str] | None = "0004_assets_documents_passport"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


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


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    ]


def upgrade() -> None:
    if not table_exists("properties"):
        op.create_table(
            "properties",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("property_type", sa.String(80), nullable=False, server_default="single_site"),
            sa.Column("status", sa.String(50), nullable=False, server_default="active"),
            sa.Column("address_line_1", sa.Text(), nullable=True),
            sa.Column("address_line_2", sa.Text(), nullable=True),
            sa.Column("city", sa.Text(), nullable=True),
            sa.Column("province_state", sa.Text(), nullable=True),
            sa.Column("postal_code", sa.Text(), nullable=True),
            sa.Column("country", sa.Text(), nullable=True, server_default="Canada"),
            sa.Column("owner_name", sa.Text(), nullable=True),
            sa.Column("property_manager_name", sa.Text(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            *timestamps(),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("organization_id", "name", name="uq_properties_org_name"),
        )

    if not table_exists("campuses"):
        op.create_table(
            "campuses",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
            sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=True),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("campus_type", sa.String(80), nullable=False, server_default="campus"),
            sa.Column("status", sa.String(50), nullable=False, server_default="active"),
            sa.Column("address_line_1", sa.Text(), nullable=True),
            sa.Column("address_line_2", sa.Text(), nullable=True),
            sa.Column("city", sa.Text(), nullable=True),
            sa.Column("province_state", sa.Text(), nullable=True),
            sa.Column("postal_code", sa.Text(), nullable=True),
            sa.Column("country", sa.Text(), nullable=True, server_default="Canada"),
            sa.Column("notes", sa.Text(), nullable=True),
            *timestamps(),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("organization_id", "name", name="uq_campuses_org_name"),
        )

    create_index_if_missing("ix_properties_organization_id", "properties", ["organization_id"])
    create_index_if_missing("ix_properties_org_status", "properties", ["organization_id", "status"])
    create_index_if_missing("ix_properties_org_type", "properties", ["organization_id", "property_type"])
    create_index_if_missing("ix_campuses_organization_id", "campuses", ["organization_id"])
    create_index_if_missing("ix_campuses_property_id", "campuses", ["property_id"])
    create_index_if_missing("ix_campuses_org_status", "campuses", ["organization_id", "status"])

    add_column_if_missing("buildings", sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=True))
    add_column_if_missing("buildings", sa.Column("campus_id", postgresql.UUID(as_uuid=True), nullable=True))
    create_fk_if_missing("fk_buildings_property_id_properties", "buildings", "properties", ["property_id"], ["id"])
    create_fk_if_missing("fk_buildings_campus_id_campuses", "buildings", "campuses", ["campus_id"], ["id"])
    create_index_if_missing("ix_buildings_property_id", "buildings", ["property_id"])
    create_index_if_missing("ix_buildings_campus_id", "buildings", ["campus_id"])


def downgrade() -> None:
    op.drop_index("ix_buildings_campus_id", table_name="buildings")
    op.drop_index("ix_buildings_property_id", table_name="buildings")
    op.drop_constraint("fk_buildings_campus_id_campuses", "buildings", type_="foreignkey")
    op.drop_constraint("fk_buildings_property_id_properties", "buildings", type_="foreignkey")
    op.drop_column("buildings", "campus_id")
    op.drop_column("buildings", "property_id")
    op.drop_table("campuses")
    op.drop_table("properties")
