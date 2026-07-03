from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MobileSyncReceipt(BaseModel):
    sync_status: str = "synced"
    synced_at: datetime
    technician_id: str
    job_id: UUID
    customer_site_id: UUID
    record_type: str
    record_id: UUID


class MobileAssignedJobRead(BaseModel):
    id: UUID
    organization_id: UUID
    building_id: UUID
    asset_id: UUID | None = None
    title: str
    description: str | None = None
    status: str
    priority: str
    due_at: datetime | None = None
    completed_at: datetime | None = None
    building_name: str | None = None
    site_address: str | None = None
    sync_status: str = "synced"


class MobileInspectionItemRead(BaseModel):
    id: UUID
    label: str
    response_type: str
    sort_order: int
    is_required: bool


class MobileInspectionRead(BaseModel):
    id: UUID
    organization_id: UUID
    building_id: UUID
    inspection_template_id: UUID | None = None
    status: str
    scheduled_at: datetime | None = None
    completed_at: datetime | None = None
    template_name: str | None = None
    items: list[MobileInspectionItemRead] = Field(default_factory=list)
    sync_status: str = "synced"


class MobileInspectionResponsePayload(BaseModel):
    inspection_id: UUID
    inspection_template_item_id: UUID
    value: dict
    notes: str | None = None
    technician_id: str
    job_id: UUID
    customer_site_id: UUID
    captured_at: datetime | None = None
    sync_status: str = "synced"


class MobileDeficiencyPayload(BaseModel):
    job_id: UUID
    building_id: UUID
    customer_site_id: UUID
    title: str
    severity: str = "medium"
    status: str = "open"
    asset_id: UUID | None = None
    inspection_id: UUID | None = None
    technician_id: str
    notes: str | None = None
    captured_at: datetime | None = None
    sync_status: str = "synced"


class MobileWorkOrderNotePayload(BaseModel):
    job_id: UUID
    customer_site_id: UUID
    technician_id: str
    notes: str
    captured_at: datetime | None = None
    sync_status: str = "synced"


class MobileMaterialUsedPayload(BaseModel):
    job_id: UUID
    customer_site_id: UUID
    technician_id: str
    material_name: str
    quantity: float = 1
    unit: str | None = None
    notes: str | None = None
    captured_at: datetime | None = None
    sync_status: str = "synced"


class MobileCompletionStatusPayload(BaseModel):
    job_id: UUID
    customer_site_id: UUID
    technician_id: str
    status: str
    notes: str | None = None
    completed_at: datetime | None = None
    sync_status: str = "synced"
