from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db, require_roles
from app.schemas.core import DocumentAssetSuggestionRead, DocumentAssetSuggestionUpdate, DocumentCreate, DocumentRead, DocumentUpdate
from app.services.document_extraction_service import document_extraction_service
from app.services.document_service import document_service

router = APIRouter(tags=["documents"])


@router.get("/documents")
def list_documents(
    organization_id: UUID | None = Query(default=None),
    property_id: UUID | None = Query(default=None),
    document_type: str | None = Query(default=None),
    is_public_to_client: bool | None = Query(default=None),
    is_passport_record: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "technician", "engineer", "readonly_viewer")),
) -> dict:
    documents = document_service.list_documents(
        db,
        current_user,
        organization_id=organization_id,
        property_id=property_id,
        document_type=document_type,
        is_public_to_client=is_public_to_client,
        is_passport_record=is_passport_record,
    )
    return {"data": [DocumentRead.model_validate(document) for document in documents]}


@router.get("/buildings/{building_id}/documents")
def list_building_documents(
    building_id: UUID,
    document_type: str | None = Query(default=None),
    is_public_to_client: bool | None = Query(default=None),
    is_passport_record: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "technician", "engineer", "readonly_viewer")),
) -> dict:
    documents = document_service.list_documents(
        db,
        current_user,
        building_id=building_id,
        document_type=document_type,
        is_public_to_client=is_public_to_client,
        is_passport_record=is_passport_record,
    )
    return {"data": [DocumentRead.model_validate(document) for document in documents]}


@router.post("/buildings/{building_id}/documents")
def create_document_metadata(
    building_id: UUID,
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "technician", "engineer")),
) -> dict:
    document = document_service.create_metadata(db, building_id, payload, current_user)
    return {"data": DocumentRead.model_validate(document)}


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    building_id: UUID | None = Form(default=None),
    property_id: UUID | None = Form(default=None),
    document_type: str = Form(...),
    title: str = Form(...),
    description: str | None = Form(default=None),
    asset_id: UUID | None = Form(default=None),
    evidence_category: str | None = Form(default=None),
    drawing_number: str | None = Form(default=None),
    revision: str | None = Form(default=None),
    issue_date: date | None = Form(default=None),
    status: str = Form(default="draft"),
    effective_date: date | None = Form(default=None),
    expiry_date: date | None = Form(default=None),
    is_public_to_client: bool = Form(default=False),
    is_passport_record: bool = Form(default=False),
    parent_document_id: UUID | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "technician", "engineer")),
) -> dict:
    payload = DocumentCreate(
        document_type=document_type,
        title=title,
        description=description,
        property_id=property_id,
        asset_id=asset_id,
        evidence_category=evidence_category,
        drawing_number=drawing_number,
        revision=revision,
        issue_date=issue_date,
        status=status,
        effective_date=effective_date,
        expiry_date=expiry_date,
        is_public_to_client=is_public_to_client,
        is_passport_record=is_passport_record,
        original_filename=file.filename,
        file_mime_type=file.content_type,
    )
    document = document_service.upload_document(
        db,
        building_id,
        payload,
        current_user,
        content=file.file,
        filename=file.filename or "upload",
        content_type=file.content_type,
        parent_document_id=parent_document_id,
    )
    return {"data": DocumentRead.model_validate(document)}


@router.get("/documents/{document_id}")
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "technician", "engineer", "readonly_viewer")),
) -> dict:
    document = document_service.get_document(db, document_id, current_user)
    return {"data": DocumentRead.model_validate(document)}


@router.get("/documents/{document_id}/download")
def download_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "technician", "engineer", "readonly_viewer")),
) -> FileResponse:
    document = document_service.get_document(db, document_id, current_user)
    path = document_service.get_download_path(db, document_id, current_user)
    return FileResponse(path, media_type=document.file_mime_type, filename=document.original_filename or document.title)


@router.get("/documents/{document_id}/download-url")
def get_document_download_url(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "technician", "engineer", "readonly_viewer")),
) -> dict:
    document_service.get_document(db, document_id, current_user)
    return {"data": {"download_url": f"/api/v1/documents/{document_id}/download"}}


@router.patch("/documents/{document_id}")
def update_document(
    document_id: UUID,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "engineer")),
) -> dict:
    document = document_service.update_document(db, document_id, payload, current_user)
    return {"data": DocumentRead.model_validate(document)}


@router.post("/documents/{document_id}/archive")
def archive_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "engineer")),
) -> dict:
    document = document_service.soft_delete_document(db, document_id, current_user)
    return {"data": DocumentRead.model_validate(document)}


@router.post("/documents/{document_id}/new-version")
async def upload_document_version(
    document_id: UUID,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str | None = Form(default=None),
    document_type: str = Form(...),
    asset_id: UUID | None = Form(default=None),
    evidence_category: str | None = Form(default=None),
    drawing_number: str | None = Form(default=None),
    revision: str | None = Form(default=None),
    issue_date: date | None = Form(default=None),
    status: str = Form(default="draft"),
    effective_date: date | None = Form(default=None),
    expiry_date: date | None = Form(default=None),
    is_public_to_client: bool = Form(default=False),
    is_passport_record: bool = Form(default=False),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "technician", "engineer")),
) -> dict:
    parent = document_service.get_document(db, document_id, current_user)
    payload = DocumentCreate(
        document_type=document_type,
        title=title,
        description=description,
        property_id=getattr(parent, "property_id", None),
        asset_id=asset_id,
        evidence_category=evidence_category,
        drawing_number=drawing_number,
        revision=revision,
        issue_date=issue_date,
        status=status,
        effective_date=effective_date,
        expiry_date=expiry_date,
        is_public_to_client=is_public_to_client,
        is_passport_record=is_passport_record,
        original_filename=file.filename,
        file_mime_type=file.content_type,
    )
    document = document_service.upload_document(
        db,
        parent.building_id,
        payload,
        current_user,
        content=file.file,
        filename=file.filename or "upload",
        content_type=file.content_type,
        parent_document_id=parent.id,
    )
    return {"data": DocumentRead.model_validate(document)}


@router.delete("/documents/{document_id}", status_code=204)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> None:
    document_service.soft_delete_document(db, document_id, current_user)


@router.get("/documents/{document_id}/asset-suggestions")
def list_document_asset_suggestions(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "technician", "engineer", "readonly_viewer")),
) -> dict:
    suggestions = document_extraction_service.list_suggestions(db, document_id, current_user)
    return {"data": [DocumentAssetSuggestionRead.model_validate(suggestion) for suggestion in suggestions]}


@router.post("/documents/{document_id}/asset-suggestions/{suggestion_id}/approve")
def approve_document_asset_suggestion(
    document_id: UUID,
    suggestion_id: UUID,
    payload: DocumentAssetSuggestionUpdate | None = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "engineer")),
) -> dict:
    suggestion = document_extraction_service.approve_suggestion(db, document_id, suggestion_id, current_user, payload)
    return {"data": DocumentAssetSuggestionRead.model_validate(suggestion)}


@router.post("/documents/{document_id}/asset-suggestions/{suggestion_id}/reject")
def reject_document_asset_suggestion(
    document_id: UUID,
    suggestion_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "engineer")),
) -> dict:
    suggestion = document_extraction_service.reject_suggestion(db, document_id, suggestion_id, current_user)
    return {"data": DocumentAssetSuggestionRead.model_validate(suggestion)}


@router.post("/documents/{document_id}/asset-suggestions/approve-all")
def approve_all_document_asset_suggestions(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "engineer")),
) -> dict:
    suggestions = document_extraction_service.approve_all(db, document_id, current_user)
    return {"data": [DocumentAssetSuggestionRead.model_validate(suggestion) for suggestion in suggestions]}
