from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db, require_roles
from app.schemas.core import DocumentCreate
from app.schemas.mobile import (
    MobileCompletionStatusPayload,
    MobileDeficiencyPayload,
    MobileInspectionResponsePayload,
    MobileMaterialUsedPayload,
    MobileWorkOrderNotePayload,
)
from app.services.document_service import document_service
from app.services.mobile_field_service import mobile_field_service

router = APIRouter(prefix="/mobile", tags=["mobile-field"])
mobile_access = require_roles("platform_admin", "organization_admin", "property_manager", "technician")


@router.get("/assigned-jobs")
def list_assigned_jobs(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(mobile_access),
) -> dict:
    return {"data": mobile_field_service.list_assigned_jobs(db, current_user)}


@router.get("/work-orders/{work_order_id}")
def get_work_order_detail(
    work_order_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(mobile_access),
) -> dict:
    return {"data": mobile_field_service.get_job(db, work_order_id, current_user)}


@router.get("/work-orders/{work_order_id}/inspection-forms")
def list_work_order_inspection_forms(
    work_order_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(mobile_access),
) -> dict:
    return {"data": mobile_field_service.list_inspection_forms(db, work_order_id, current_user)}


@router.post("/inspection-responses")
def submit_inspection_response(
    payload: MobileInspectionResponsePayload,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(mobile_access),
) -> dict:
    return {"data": mobile_field_service.submit_inspection_response(db, payload, current_user)}


@router.post("/deficiencies")
def create_deficiency(
    payload: MobileDeficiencyPayload,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(mobile_access),
) -> dict:
    return {"data": mobile_field_service.create_deficiency(db, payload, current_user)}


@router.post("/site-notes")
def add_site_note(
    payload: MobileWorkOrderNotePayload,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(mobile_access),
) -> dict:
    return {"data": mobile_field_service.add_site_notes(db, payload, current_user)}


@router.post("/materials-used")
def add_material_used(
    payload: MobileMaterialUsedPayload,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(mobile_access),
) -> dict:
    return {"data": mobile_field_service.add_material_used(db, payload, current_user)}


@router.post("/completion-status")
def update_completion_status(
    payload: MobileCompletionStatusPayload,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(mobile_access),
) -> dict:
    return {"data": mobile_field_service.update_completion_status(db, payload, current_user)}


@router.post("/photos")
async def upload_field_photo(
    file: UploadFile = File(...),
    job_id: UUID = Form(...),
    building_id: UUID = Form(...),
    customer_site_id: UUID = Form(...),
    technician_id: str = Form(...),
    caption: str | None = Form(default=None),
    captured_at: datetime | None = Form(default=None),
    sync_status: str = Form(default="synced"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(mobile_access),
) -> dict:
    document = document_service.upload_document(
        db,
        building_id,
        _mobile_document_payload(
            document_type="photo",
            title=caption or "Base44 field photo",
            description=_mobile_upload_description("photo", technician_id, job_id, customer_site_id, sync_status, captured_at),
            file=file,
        ),
        current_user,
        content=file.file,
        filename=file.filename or "field-photo",
        content_type=file.content_type,
    )
    return {"data": mobile_field_service.attach_mobile_document(db, document, technician_id, job_id, customer_site_id, "photo")}


@router.post("/signatures")
async def upload_customer_signature(
    file: UploadFile = File(...),
    job_id: UUID = Form(...),
    building_id: UUID = Form(...),
    customer_site_id: UUID = Form(...),
    technician_id: str = Form(...),
    signer_name: str | None = Form(default=None),
    captured_at: datetime | None = Form(default=None),
    sync_status: str = Form(default="synced"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(mobile_access),
) -> dict:
    document = document_service.upload_document(
        db,
        building_id,
        _mobile_document_payload(
            document_type="service_record",
            title=f"Customer signature{f' - {signer_name}' if signer_name else ''}",
            description=_mobile_upload_description("customer_signature", technician_id, job_id, customer_site_id, sync_status, captured_at),
            file=file,
        ),
        current_user,
        content=file.file,
        filename=file.filename or "customer-signature",
        content_type=file.content_type,
    )
    return {
        "data": mobile_field_service.attach_mobile_document(
            db,
            document,
            technician_id,
            job_id,
            customer_site_id,
            "customer_signature",
        )
    }


def _mobile_document_payload(document_type: str, title: str, description: str, file: UploadFile) -> DocumentCreate:
    return DocumentCreate(
        document_type=document_type,
        title=title,
        description=description,
        original_filename=file.filename,
        file_mime_type=file.content_type,
        is_public_to_client=False,
        is_passport_record=False,
    )


def _mobile_upload_description(
    record_type: str,
    technician_id: str,
    job_id: UUID,
    customer_site_id: UUID,
    sync_status: str,
    captured_at: datetime | None,
) -> str:
    captured_value = captured_at.isoformat() if captured_at else "server_received"
    return (
        f"Base44 mobile {record_type}; technician_id={technician_id}; job_id={job_id}; "
        f"customer_site_id={customer_site_id}; sync_status={sync_status}; captured_at={captured_value}"
    )
