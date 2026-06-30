"""core domain alignment

Revision ID: 0003_core_domain_alignment
Revises: 0002_mvp_schema
Create Date: 2026-06-30
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0003_core_domain_alignment"
down_revision: str | Sequence[str] | None = "0002_mvp_schema"
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


def upgrade() -> None:
    op.alter_column("organizations", "slug", existing_type=sa.String(120), nullable=True)
    add_column_if_missing("organizations", sa.Column("legal_name", sa.Text(), nullable=True))
    add_column_if_missing("organizations", sa.Column("organization_type", sa.String(80), nullable=False, server_default="client"))
    add_column_if_missing("organizations", sa.Column("phone", sa.Text(), nullable=True))
    add_column_if_missing("organizations", sa.Column("email", sa.Text(), nullable=True))
    add_column_if_missing("organizations", sa.Column("website", sa.Text(), nullable=True))
    add_column_if_missing("organizations", sa.Column("address_line_1", sa.Text(), nullable=True))
    add_column_if_missing("organizations", sa.Column("address_line_2", sa.Text(), nullable=True))
    add_column_if_missing("organizations", sa.Column("city", sa.Text(), nullable=True))
    add_column_if_missing("organizations", sa.Column("province_state", sa.Text(), nullable=True))
    add_column_if_missing("organizations", sa.Column("postal_code", sa.Text(), nullable=True))
    add_column_if_missing("organizations", sa.Column("country", sa.Text(), nullable=True, server_default="Canada"))
    add_column_if_missing("organizations", sa.Column("billing_contact_name", sa.Text(), nullable=True))
    add_column_if_missing("organizations", sa.Column("billing_contact_email", sa.Text(), nullable=True))
    add_column_if_missing("organizations", sa.Column("billing_contact_phone", sa.Text(), nullable=True))
    add_column_if_missing("organizations", sa.Column("notes", sa.Text(), nullable=True))
    create_index_if_missing("ix_organizations_organization_type", "organizations", ["organization_type"])

    op.alter_column("users", "full_name", existing_type=sa.String(255), nullable=True)
    add_column_if_missing("users", sa.Column("auth_provider_user_id", sa.Text(), nullable=True))
    add_column_if_missing("users", sa.Column("first_name", sa.Text(), nullable=True))
    add_column_if_missing("users", sa.Column("last_name", sa.Text(), nullable=True))
    add_column_if_missing("users", sa.Column("phone", sa.Text(), nullable=True))
    add_column_if_missing("users", sa.Column("job_title", sa.Text(), nullable=True))
    add_column_if_missing("users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
    create_index_if_missing("ix_users_auth_provider_user_id", "users", ["auth_provider_user_id"], unique=True)

    add_column_if_missing("roles", sa.Column("is_system_role", sa.Boolean(), nullable=False, server_default=sa.false()))

    add_column_if_missing("organization_users", sa.Column("invited_at", sa.DateTime(timezone=True), nullable=True))
    add_column_if_missing("organization_users", sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True))

    add_column_if_missing("buildings", sa.Column("bpid", sa.Text(), nullable=True))
    add_column_if_missing("buildings", sa.Column("address_line_1", sa.Text(), nullable=True))
    add_column_if_missing("buildings", sa.Column("address_line_2", sa.Text(), nullable=True))
    add_column_if_missing("buildings", sa.Column("province_state", sa.Text(), nullable=True))
    add_column_if_missing("buildings", sa.Column("latitude", sa.Numeric(10, 7), nullable=True))
    add_column_if_missing("buildings", sa.Column("longitude", sa.Numeric(10, 7), nullable=True))
    add_column_if_missing("buildings", sa.Column("building_type", sa.Text(), nullable=True))
    add_column_if_missing("buildings", sa.Column("occupancy_classification", sa.Text(), nullable=True))
    add_column_if_missing("buildings", sa.Column("construction_year", sa.Integer(), nullable=True))
    add_column_if_missing("buildings", sa.Column("number_of_storeys", sa.Integer(), nullable=True))
    add_column_if_missing("buildings", sa.Column("total_area_sq_ft", sa.Numeric(14, 2), nullable=True))
    add_column_if_missing("buildings", sa.Column("owner_name", sa.Text(), nullable=True))
    add_column_if_missing("buildings", sa.Column("property_manager_name", sa.Text(), nullable=True))
    add_column_if_missing("buildings", sa.Column("fire_department", sa.Text(), nullable=True))
    add_column_if_missing("buildings", sa.Column("ahj_name", sa.Text(), nullable=True))
    add_column_if_missing("buildings", sa.Column("insurance_provider", sa.Text(), nullable=True))
    add_column_if_missing("buildings", sa.Column("notes", sa.Text(), nullable=True))
    create_index_if_missing("ix_buildings_bpid", "buildings", ["bpid"], unique=True)

    add_column_if_missing("building_contacts", sa.Column("company", sa.Text(), nullable=True))
    add_column_if_missing("building_contacts", sa.Column("job_title", sa.Text(), nullable=True))
    add_column_if_missing("building_contacts", sa.Column("mobile", sa.Text(), nullable=True))
    add_column_if_missing("building_contacts", sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()))
    add_column_if_missing("building_contacts", sa.Column("is_emergency_contact", sa.Boolean(), nullable=False, server_default=sa.false()))
    add_column_if_missing("building_contacts", sa.Column("notes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_index("ix_buildings_bpid", table_name="buildings")
    op.drop_index("ix_users_auth_provider_user_id", table_name="users")
    op.drop_index("ix_organizations_organization_type", table_name="organizations")

    for column_name in ["notes", "is_emergency_contact", "is_primary", "mobile", "job_title", "company"]:
        op.drop_column("building_contacts", column_name)

    for column_name in [
        "notes",
        "insurance_provider",
        "ahj_name",
        "fire_department",
        "property_manager_name",
        "owner_name",
        "total_area_sq_ft",
        "number_of_storeys",
        "construction_year",
        "occupancy_classification",
        "building_type",
        "longitude",
        "latitude",
        "province_state",
        "address_line_2",
        "address_line_1",
        "bpid",
    ]:
        op.drop_column("buildings", column_name)

    op.drop_column("organization_users", "accepted_at")
    op.drop_column("organization_users", "invited_at")
    op.drop_column("roles", "is_system_role")

    for column_name in ["last_login_at", "job_title", "phone", "last_name", "first_name", "auth_provider_user_id"]:
        op.drop_column("users", column_name)
    op.alter_column("users", "full_name", existing_type=sa.String(255), nullable=False)

    for column_name in [
        "notes",
        "billing_contact_phone",
        "billing_contact_email",
        "billing_contact_name",
        "country",
        "postal_code",
        "province_state",
        "city",
        "address_line_2",
        "address_line_1",
        "website",
        "email",
        "phone",
        "organization_type",
        "legal_name",
    ]:
        op.drop_column("organizations", column_name)
    op.alter_column("organizations", "slug", existing_type=sa.String(120), nullable=False)
