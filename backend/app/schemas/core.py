from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DataResponse(BaseModel):
    data: object


class ListResponse(BaseModel):
    data: list[object]


class OrganizationBase(BaseModel):
    name: str
    legal_name: str | None = None
    organization_type: str = "client"
    status: str = "active"
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    province_state: str | None = None
    postal_code: str | None = None
    country: str | None = "Canada"
    billing_contact_name: str | None = None
    billing_contact_email: str | None = None
    billing_contact_phone: str | None = None
    notes: str | None = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = None
    legal_name: str | None = None
    organization_type: str | None = None
    status: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    province_state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    billing_contact_name: str | None = None
    billing_contact_email: str | None = None
    billing_contact_phone: str | None = None
    notes: str | None = None


class OrganizationRead(OrganizationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    auth_provider_user_id: str | None = None
    email: str
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    job_title: str | None = None
    status: str = "active"


class UserCreate(UserBase):
    pass


class UserInvite(BaseModel):
    organization_id: UUID
    email: str
    first_name: str | None = None
    last_name: str | None = None
    role: str


class UserUpdate(BaseModel):
    auth_provider_user_id: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    job_title: str | None = None
    status: str | None = None


class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoleRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    is_system_role: bool

    model_config = ConfigDict(from_attributes=True)


class OrganizationUserCreate(BaseModel):
    organization_id: UUID
    user_id: UUID
    role_id: UUID
    status: str = "active"


class OrganizationUserUpdate(BaseModel):
    status: str | None = None


class OrganizationUserRead(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    role_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BuildingBase(BaseModel):
    organization_id: UUID
    name: str
    address_line_1: str
    address_line_2: str | None = None
    city: str
    province_state: str
    postal_code: str | None = None
    country: str = "Canada"
    latitude: float | None = None
    longitude: float | None = None
    building_type: str
    occupancy_classification: str | None = None
    construction_year: int | None = None
    number_of_storeys: int | None = Field(default=None, ge=0)
    total_area_sq_ft: float | None = Field(default=None, ge=0)
    owner_name: str | None = None
    property_manager_name: str | None = None
    fire_department: str | None = None
    ahj_name: str | None = None
    insurance_provider: str | None = None
    status: str = "active"
    notes: str | None = None


class BuildingCreate(BuildingBase):
    pass


class BuildingUpdate(BaseModel):
    name: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    province_state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    building_type: str | None = None
    occupancy_classification: str | None = None
    construction_year: int | None = None
    number_of_storeys: int | None = Field(default=None, ge=0)
    total_area_sq_ft: float | None = Field(default=None, ge=0)
    owner_name: str | None = None
    property_manager_name: str | None = None
    fire_department: str | None = None
    ahj_name: str | None = None
    insurance_provider: str | None = None
    status: str | None = None
    notes: str | None = None


class BuildingRead(BuildingBase):
    id: UUID
    bpid: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BuildingContactBase(BaseModel):
    contact_type: str
    name: str
    company: str | None = None
    job_title: str | None = None
    email: str | None = None
    phone: str | None = None
    mobile: str | None = None
    is_primary: bool = False
    is_emergency_contact: bool = False
    notes: str | None = None


class BuildingContactCreate(BuildingContactBase):
    pass


class BuildingContactUpdate(BaseModel):
    contact_type: str | None = None
    name: str | None = None
    company: str | None = None
    job_title: str | None = None
    email: str | None = None
    phone: str | None = None
    mobile: str | None = None
    is_primary: bool | None = None
    is_emergency_contact: bool | None = None
    notes: str | None = None


class BuildingContactRead(BuildingContactBase):
    id: UUID
    organization_id: UUID
    building_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
