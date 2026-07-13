import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Organization(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True)
    legal_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    organization_type: Mapped[str] = mapped_column(String(80), nullable=False, default="client")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(Text, nullable=True)
    address_line_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    address_line_2: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(Text, nullable=True)
    province_state: Mapped[str | None] = mapped_column(Text, nullable=True)
    postal_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(Text, nullable=True, default="Canada")
    billing_contact_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    billing_contact_email: Mapped[str | None] = mapped_column(Text, nullable=True)
    billing_contact_phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    users: Mapped[list["OrganizationUser"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    properties: Mapped[list["Property"]] = relationship(back_populates="organization")
    buildings: Mapped[list["Building"]] = relationship(back_populates="organization")
    memberships: Mapped[list["Membership"]] = relationship(back_populates="organization")

    __table_args__ = (
        Index("ix_organizations_slug", "slug"),
        Index("ix_organizations_status", "status"),
        Index("ix_organizations_organization_type", "organization_type"),
    )


class Property(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "properties"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    property_type: Mapped[str] = mapped_column(String(80), nullable=False, default="single_site")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    address_line_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    address_line_2: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(Text, nullable=True)
    province_state: Mapped[str | None] = mapped_column(Text, nullable=True)
    postal_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(Text, nullable=True, default="Canada")
    owner_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    property_manager_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    organization: Mapped["Organization"] = relationship(back_populates="properties")
    campuses: Mapped[list["Campus"]] = relationship(back_populates="property")
    buildings: Mapped[list["Building"]] = relationship(back_populates="property")

    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_properties_org_name"),
        Index("ix_properties_organization_id", "organization_id"),
        Index("ix_properties_org_status", "organization_id", "status"),
        Index("ix_properties_org_type", "organization_id", "property_type"),
    )


class Campus(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "campuses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    property_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("properties.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    campus_type: Mapped[str] = mapped_column(String(80), nullable=False, default="campus")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    address_line_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    address_line_2: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(Text, nullable=True)
    province_state: Mapped[str | None] = mapped_column(Text, nullable=True)
    postal_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(Text, nullable=True, default="Canada")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    property: Mapped["Property | None"] = relationship(back_populates="campuses")
    buildings: Mapped[list["Building"]] = relationship(back_populates="campus")

    __table_args__ = (
        UniqueConstraint("organization_id", "name", name="uq_campuses_org_name"),
        Index("ix_campuses_organization_id", "organization_id"),
        Index("ix_campuses_property_id", "property_id"),
        Index("ix_campuses_org_status", "organization_id", "status"),
    )


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth_provider_user_id: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(Text, nullable=True)
    job_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organizations: Mapped[list["OrganizationUser"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    assigned_work_orders: Mapped[list["WorkOrder"]] = relationship(back_populates="assigned_user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_status", "status"),
    )


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system_role: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    organization_users: Mapped[list["OrganizationUser"]] = relationship(back_populates="role")


class OrganizationUser(Base, TimestampMixin):
    __tablename__ = "organization_users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    invited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped["Organization"] = relationship(back_populates="users")
    user: Mapped["User"] = relationship(back_populates="organizations")
    role: Mapped["Role"] = relationship(back_populates="organization_users")

    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", "role_id", name="uq_organization_users_org_user_role"),
        Index("ix_organization_users_organization_id", "organization_id"),
        Index("ix_organization_users_user_id", "user_id"),
    )


class Building(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "buildings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    property_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("properties.id"), nullable=True)
    campus_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("campuses.id"), nullable=True)
    bpid: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    address_line_2: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    province_state: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str] = mapped_column(String(120), nullable=False, default="Canada")
    postal_code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    building_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    occupancy_classification: Mapped[str | None] = mapped_column(Text, nullable=True)
    construction_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    number_of_storeys: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_area_sq_ft: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    owner_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    property_manager_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    fire_department: Mapped[str | None] = mapped_column(Text, nullable=True)
    ahj_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    insurance_provider: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    project_classification: Mapped[str | None] = mapped_column(String(50), nullable=True)
    passport_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    passport_status: Mapped[str] = mapped_column(String(80), nullable=False, default="Not Started")
    passport_issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    passport_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    client_handover_status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    organization: Mapped["Organization"] = relationship(back_populates="buildings")
    property: Mapped["Property | None"] = relationship(back_populates="buildings")
    campus: Mapped["Campus | None"] = relationship(back_populates="buildings")
    contacts: Mapped[list["BuildingContact"]] = relationship(back_populates="building")
    assets: Mapped[list["Asset"]] = relationship(back_populates="building")
    documents: Mapped[list["Document"]] = relationship(back_populates="building")
    work_orders: Mapped[list["WorkOrder"]] = relationship(back_populates="building")
    inspections: Mapped[list["Inspection"]] = relationship(back_populates="building")

    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_buildings_org_code"),
        Index("ix_buildings_organization_id", "organization_id"),
        Index("ix_buildings_property_id", "property_id"),
        Index("ix_buildings_campus_id", "campus_id"),
        Index("ix_buildings_bpid", "bpid"),
        Index("ix_buildings_org_status", "organization_id", "status"),
        Index("ix_buildings_org_name", "organization_id", "name"),
    )


class BuildingContact(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "building_contacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    building_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("buildings.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str | None] = mapped_column(Text, nullable=True)
    job_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(60), nullable=True)
    mobile: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_type: Mapped[str] = mapped_column(String(80), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_emergency_contact: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    building: Mapped["Building"] = relationship(back_populates="contacts")

    __table_args__ = (
        Index("ix_building_contacts_organization_id", "organization_id"),
        Index("ix_building_contacts_building_id", "building_id"),
    )


class AssetType(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "asset_types"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_inspection_frequency_months: Mapped[int | None] = mapped_column(Integer, nullable=True)

    assets: Mapped[list["Asset"]] = relationship(back_populates="asset_type")
    inspection_templates: Mapped[list["InspectionTemplate"]] = relationship(back_populates="asset_type")

    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_asset_types_org_code"),
        Index("ix_asset_types_organization_id", "organization_id"),
        Index("ix_asset_types_code", "code"),
    )


class Asset(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    building_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("buildings.id"), nullable=False)
    asset_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("asset_types.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tag: Mapped[str | None] = mapped_column(String(120), nullable=True)
    asset_tag: Mapped[str | None] = mapped_column(String(120), nullable=True)
    location_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(Text, nullable=True)
    model: Mapped[str | None] = mapped_column(Text, nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    installed_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    installation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    warranty_expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    condition_rating: Mapped[str | None] = mapped_column(String(50), nullable=True)
    inspection_frequency_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_inspected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_inspection_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    replacement_cost_estimate: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    remaining_useful_life_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    building: Mapped["Building"] = relationship(back_populates="assets")
    asset_type: Mapped["AssetType"] = relationship(back_populates="assets")
    documents: Mapped[list["Document"]] = relationship(back_populates="asset")
    work_orders: Mapped[list["WorkOrder"]] = relationship(back_populates="asset")

    __table_args__ = (
        UniqueConstraint("organization_id", "tag", name="uq_assets_org_tag"),
        Index("ix_assets_organization_id", "organization_id"),
        Index("ix_assets_building_id", "building_id"),
        Index("ix_assets_asset_type_id", "asset_type_id"),
        Index("ix_assets_org_status", "organization_id", "status"),
    )


class Document(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    building_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("buildings.id"), nullable=False)
    asset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    uploaded_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_type: Mapped[str] = mapped_column(String(80), nullable=False)
    storage_uri: Mapped[str] = mapped_column(Text, nullable=False)
    storage_bucket: Mapped[str | None] = mapped_column(String(255), nullable=True)
    storage_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    file_mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_document_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("documents.id"), nullable=True)
    generated_by_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_public_to_client: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_passport_record: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    building: Mapped["Building"] = relationship(back_populates="documents")
    asset: Mapped["Asset | None"] = relationship(back_populates="documents")
    parent_document: Mapped["Document | None"] = relationship(remote_side=[id], back_populates="versions")
    versions: Mapped[list["Document"]] = relationship(back_populates="parent_document")

    __table_args__ = (
        Index("ix_documents_organization_id", "organization_id"),
        Index("ix_documents_building_id", "building_id"),
        Index("ix_documents_asset_id", "asset_id"),
        Index("ix_documents_org_type", "organization_id", "document_type"),
        Index("ix_documents_org_building_type", "organization_id", "building_id", "document_type"),
        Index("ix_documents_passport_record", "building_id", "is_passport_record"),
        Index("ix_documents_parent_document_id", "parent_document_id"),
    )


class WorkOrder(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "work_orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    building_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("buildings.id"), nullable=False)
    asset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    assigned_to_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")
    priority: Mapped[str] = mapped_column(String(50), nullable=False, default="medium")
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    building: Mapped["Building"] = relationship(back_populates="work_orders")
    asset: Mapped["Asset"] = relationship(back_populates="work_orders")
    assigned_user: Mapped["User"] = relationship(back_populates="assigned_work_orders")

    __table_args__ = (
        Index("ix_work_orders_organization_id", "organization_id"),
        Index("ix_work_orders_building_id", "building_id"),
        Index("ix_work_orders_assigned_to_user_id", "assigned_to_user_id"),
        Index("ix_work_orders_org_status", "organization_id", "status"),
        Index("ix_work_orders_org_priority", "organization_id", "priority"),
    )


class InspectionTemplate(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "inspection_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    asset_type_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("asset_types.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")

    asset_type: Mapped["AssetType"] = relationship(back_populates="inspection_templates")
    items: Mapped[list["InspectionTemplateItem"]] = relationship(back_populates="template", cascade="all, delete-orphan")
    inspections: Mapped[list["Inspection"]] = relationship(back_populates="template")

    __table_args__ = (
        Index("ix_inspection_templates_organization_id", "organization_id"),
        Index("ix_inspection_templates_asset_type_id", "asset_type_id"),
        Index("ix_inspection_templates_org_status", "organization_id", "status"),
    )


class InspectionTemplateItem(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "inspection_template_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    inspection_template_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("inspection_templates.id"), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    response_type: Mapped[str] = mapped_column(String(80), nullable=False, default="pass_fail")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    template: Mapped["InspectionTemplate"] = relationship(back_populates="items")
    responses: Mapped[list["InspectionResponse"]] = relationship(back_populates="template_item")

    __table_args__ = (
        Index("ix_inspection_template_items_organization_id", "organization_id"),
        Index("ix_inspection_template_items_template_id", "inspection_template_id"),
    )


class Inspection(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "inspections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    building_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("buildings.id"), nullable=False)
    inspection_template_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("inspection_templates.id"), nullable=True)
    inspector_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="scheduled")
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    building: Mapped["Building"] = relationship(back_populates="inspections")
    template: Mapped["InspectionTemplate"] = relationship(back_populates="inspections")
    responses: Mapped[list["InspectionResponse"]] = relationship(back_populates="inspection")
    deficiencies: Mapped[list["Deficiency"]] = relationship(back_populates="inspection")

    __table_args__ = (
        Index("ix_inspections_organization_id", "organization_id"),
        Index("ix_inspections_building_id", "building_id"),
        Index("ix_inspections_org_status", "organization_id", "status"),
        Index("ix_inspections_scheduled_at", "scheduled_at"),
    )


class InspectionResponse(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "inspection_responses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    inspection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("inspections.id"), nullable=False)
    inspection_template_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("inspection_template_items.id"), nullable=False)
    value: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    inspection: Mapped["Inspection"] = relationship(back_populates="responses")
    template_item: Mapped["InspectionTemplateItem"] = relationship(back_populates="responses")

    __table_args__ = (
        UniqueConstraint("inspection_id", "inspection_template_item_id", name="uq_inspection_responses_inspection_item"),
        Index("ix_inspection_responses_organization_id", "organization_id"),
        Index("ix_inspection_responses_inspection_id", "inspection_id"),
    )


class Deficiency(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "deficiencies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    building_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("buildings.id"), nullable=False)
    asset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    inspection_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("inspections.id"), nullable=True)
    assigned_to_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    inspection: Mapped["Inspection"] = relationship(back_populates="deficiencies")

    __table_args__ = (
        Index("ix_deficiencies_organization_id", "organization_id"),
        Index("ix_deficiencies_building_id", "building_id"),
        Index("ix_deficiencies_org_status", "organization_id", "status"),
        Index("ix_deficiencies_org_severity", "organization_id", "severity"),
    )


class Report(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    building_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("buildings.id"), nullable=True)
    generated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_reports_organization_id", "organization_id"),
        Index("ix_reports_building_id", "building_id"),
        Index("ix_reports_org_type", "organization_id", "report_type"),
    )


class Certificate(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "certificates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    building_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("buildings.id"), nullable=False)
    asset_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    document_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("documents.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    certificate_type: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="current")
    issued_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    expires_on: Mapped[date | None] = mapped_column(Date, nullable=True)

    __table_args__ = (
        Index("ix_certificates_organization_id", "organization_id"),
        Index("ix_certificates_building_id", "building_id"),
        Index("ix_certificates_org_status", "organization_id", "status"),
        Index("ix_certificates_expires_on", "expires_on"),
    )


class MembershipPlan(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "membership_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    monthly_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    memberships: Mapped[list["Membership"]] = relationship(back_populates="membership_plan")

    __table_args__ = (Index("ix_membership_plans_code", "code"),)


class Membership(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "memberships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    membership_plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("membership_plans.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    starts_on: Mapped[date] = mapped_column(Date, nullable=False)
    ends_on: Mapped[date | None] = mapped_column(Date, nullable=True)

    organization: Mapped["Organization"] = relationship(back_populates="memberships")
    membership_plan: Mapped["MembershipPlan"] = relationship(back_populates="memberships")

    __table_args__ = (
        Index("ix_memberships_organization_id", "organization_id"),
        Index("ix_memberships_membership_plan_id", "membership_plan_id"),
        Index("ix_memberships_org_status", "organization_id", "status"),
    )


class HealthScore(Base, TimestampMixin):
    __tablename__ = "health_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    building_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("buildings.id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    score_type: Mapped[str] = mapped_column(String(80), nullable=False, default="overall")
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    inputs: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="ck_health_scores_score_range"),
        Index("ix_health_scores_organization_id", "organization_id"),
        Index("ix_health_scores_building_id", "building_id"),
        Index("ix_health_scores_building_calculated_at", "building_id", "calculated_at"),
    )


class PropertyIntelligenceSnapshot(Base, TimestampMixin):
    __tablename__ = "property_intelligence_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    property_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("properties.id"), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    calculation_version: Mapped[str] = mapped_column(String(40), nullable=False, default="m7-001")
    health_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    readiness_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    passport_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    building_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    shared_infrastructure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    asset_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    document_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    passport_record_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    client_visible_record_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    open_deficiency_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    overdue_work_order_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    capital_exposure_estimate: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    summary: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        CheckConstraint("health_score >= 0 AND health_score <= 100", name="ck_property_intelligence_health_score_range"),
        CheckConstraint("confidence_score >= 0 AND confidence_score <= 100", name="ck_property_intelligence_confidence_score_range"),
        CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="ck_property_intelligence_risk_score_range"),
        CheckConstraint("readiness_score >= 0 AND readiness_score <= 100", name="ck_property_intelligence_readiness_score_range"),
        CheckConstraint("passport_score >= 0 AND passport_score <= 100", name="ck_property_intelligence_passport_score_range"),
        Index("ix_property_intelligence_snapshots_organization_id", "organization_id"),
        Index("ix_property_intelligence_snapshots_property_id", "property_id"),
        Index("ix_property_intelligence_snapshots_property_calculated_at", "property_id", "calculated_at"),
    )


class PropertyIntelligenceFactor(Base, TimestampMixin):
    __tablename__ = "property_intelligence_factors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    property_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("properties.id"), nullable=False)
    snapshot_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("property_intelligence_snapshots.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    factor_key: Mapped[str] = mapped_column(String(120), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="info")
    source_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    impact_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)

    __table_args__ = (
        Index("ix_property_intelligence_factors_organization_id", "organization_id"),
        Index("ix_property_intelligence_factors_property_id", "property_id"),
        Index("ix_property_intelligence_factors_snapshot_id", "snapshot_id"),
        Index("ix_property_intelligence_factors_category", "property_id", "category"),
    )


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    notification_type: Mapped[str] = mapped_column(String(80), nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="notifications")

    __table_args__ = (
        Index("ix_notifications_organization_id", "organization_id"),
        Index("ix_notifications_user_id", "user_id"),
        Index("ix_notifications_user_read_at", "user_id", "read_at"),
    )


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)

    __table_args__ = (
        Index("ix_audit_logs_organization_id", "organization_id"),
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
        Index("ix_audit_logs_created_at", "created_at"),
    )
