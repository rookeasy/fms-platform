"""completed project passport queue

Revision ID: 0007_passport_queue
Revises: 0006_property_intelligence
Create Date: 2026-07-13
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0007_passport_queue"
down_revision: str | Sequence[str] | None = "0006_property_intelligence"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def create_index_if_missing(index_name: str, table_name: str, columns: list[str], unique: bool = False) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_indexes = {item["name"] for item in inspector.get_indexes(table_name)}
    if index_name not in existing_indexes:
        op.create_index(index_name, table_name, columns, unique=unique)


def drop_index_if_exists(index_name: str, table_name: str) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_indexes = {item["name"] for item in inspector.get_indexes(table_name)}
    if index_name in existing_indexes:
        op.drop_index(index_name, table_name=table_name)


def upgrade() -> None:
    if not column_exists("buildings", "project_classification"):
        op.add_column("buildings", sa.Column("project_classification", sa.String(length=50), nullable=True))
    if not column_exists("buildings", "passport_eligible"):
        op.add_column(
            "buildings",
            sa.Column("passport_eligible", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )
    if not column_exists("buildings", "passport_status"):
        op.add_column(
            "buildings",
            sa.Column("passport_status", sa.String(length=80), nullable=False, server_default="Not Started"),
        )
    if not column_exists("buildings", "passport_issue_date"):
        op.add_column("buildings", sa.Column("passport_issue_date", sa.Date(), nullable=True))
    if not column_exists("buildings", "passport_version"):
        op.add_column("buildings", sa.Column("passport_version", sa.String(length=40), nullable=True))
    if not column_exists("buildings", "client_handover_status"):
        op.add_column("buildings", sa.Column("client_handover_status", sa.String(length=80), nullable=True))

    create_index_if_missing("ix_buildings_project_classification", "buildings", ["project_classification"])
    create_index_if_missing("ix_buildings_passport_eligible", "buildings", ["passport_eligible"])
    create_index_if_missing("ix_buildings_passport_status", "buildings", ["passport_status"])


def downgrade() -> None:
    drop_index_if_exists("ix_buildings_passport_status", "buildings")
    drop_index_if_exists("ix_buildings_passport_eligible", "buildings")
    drop_index_if_exists("ix_buildings_project_classification", "buildings")
    for column_name in [
        "client_handover_status",
        "passport_version",
        "passport_issue_date",
        "passport_status",
        "passport_eligible",
        "project_classification",
    ]:
        if column_exists("buildings", column_name):
            op.drop_column("buildings", column_name)
