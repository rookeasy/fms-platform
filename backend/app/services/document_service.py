from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.config import settings
from app.core.constants import DOCUMENT_TYPES, DOCUMENT_UPDATED, DOCUMENT_UPLOADED
from app.models import Asset, Document
from app.schemas.core import DocumentCreate, DocumentUpdate
from app.services.audit_log import audit_service
from app.services.building_service import building_service
from app.services.exceptions import not_found, validation_error
from app.services.tenant import ensure_organization_access
from app.storage.base import StorageAdapter
from app.storage.local import local_storage


class DocumentService:
    def list_documents(
        self,
        db: Session,
        current_user: CurrentUser,
        organization_id: UUID | None = None,
        building_id: UUID | None = None,
        document_type: str | None = None,
        is_public_to_client: bool | None = None,
        is_passport_record: bool | None = None,
    ) -> list[Document]:
        query = select(Document).where(Document.deleted_at.is_(None)).order_by(Document.created_at.desc())
        if building_id is not None:
            building = building_service.get_building(db, building_id, current_user)
            query = query.where(Document.building_id == building.id, Document.organization_id == building.organization_id)
        elif organization_id is not None:
            ensure_organization_access(current_user, organization_id)
            query = query.where(Document.organization_id == organization_id)
        elif not current_user.is_platform_admin and current_user.current_organization_id:
            query = query.where(Document.organization_id == UUID(current_user.current_organization_id))
        if document_type is not None:
            self._validate_document_type(document_type)
            query = query.where(Document.document_type == document_type)
        if is_public_to_client is not None:
            query = query.where(Document.is_public_to_client == is_public_to_client)
        if is_passport_record is not None:
            query = query.where(Document.is_passport_record == is_passport_record)
        return list(db.scalars(query).all())

    def get_document(self, db: Session, document_id: UUID, current_user: CurrentUser) -> Document:
        document = db.scalar(select(Document).where(Document.id == document_id, Document.deleted_at.is_(None)))
        if document is None:
            raise not_found("Document not found.")
        ensure_organization_access(current_user, document.organization_id)
        return document

    def create_metadata(
        self,
        db: Session,
        building_id: UUID,
        payload: DocumentCreate,
        current_user: CurrentUser,
    ) -> Document:
        building = building_service.get_building(db, building_id, current_user)
        self._validate_document_type(payload.document_type)
        self._validate_asset(db, payload.asset_id, building.id, building.organization_id)
        document = Document(
            **payload.model_dump(),
            organization_id=building.organization_id,
            building_id=building.id,
            name=payload.title,
            storage_uri=payload.storage_key or "",
            mime_type=payload.file_mime_type,
            version_number=1,
            uploaded_by_user_id=None,
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    def upload_document(
        self,
        db: Session,
        building_id: UUID,
        payload: DocumentCreate,
        current_user: CurrentUser,
        content,
        filename: str,
        content_type: str | None,
        parent_document_id: UUID | None = None,
        storage: StorageAdapter = local_storage,
    ) -> Document:
        building = building_service.get_building(db, building_id, current_user)
        self._validate_document_type(payload.document_type)
        self._validate_asset(db, payload.asset_id, building.id, building.organization_id)
        parent_document = None
        version_number = 1
        if parent_document_id is not None:
            parent_document = self.get_document(db, parent_document_id, current_user)
            if parent_document.building_id != building.id:
                raise validation_error("Replacement document must belong to the same building.")
            version_number = self._next_version_number(db, parent_document.id)

        key = self._build_storage_key(building.id, parent_document_id or uuid4(), filename)
        stored_file = storage.save(key=key, content=content)
        if stored_file.size_bytes > settings.max_upload_size_bytes:
            Path(stored_file.path).unlink(missing_ok=True)
            raise validation_error("Uploaded file exceeds the configured size limit.")

        document = Document(
            organization_id=building.organization_id,
            building_id=building.id,
            asset_id=payload.asset_id,
            uploaded_by_user_id=None,
            name=payload.title,
            title=payload.title,
            description=payload.description,
            document_type=payload.document_type,
            storage_uri=stored_file.key,
            storage_bucket=stored_file.bucket,
            storage_key=stored_file.key,
            original_filename=filename,
            mime_type=content_type,
            file_mime_type=content_type,
            file_size_bytes=stored_file.size_bytes,
            version_number=version_number,
            parent_document_id=parent_document.id if parent_document else None,
            effective_date=payload.effective_date,
            expiry_date=payload.expiry_date,
            is_public_to_client=payload.is_public_to_client,
            is_passport_record=payload.is_passport_record,
        )
        db.add(document)
        db.flush()
        audit_service.record(
            db,
            action=DOCUMENT_UPLOADED,
            entity_type="document",
            entity_id=document.id,
            organization_id=document.organization_id,
            current_user=current_user,
            metadata={
                "building_id": str(building.id),
                "document_type": document.document_type,
                "version_number": document.version_number,
                "is_passport_record": document.is_passport_record,
            },
        )
        db.commit()
        db.refresh(document)
        return document

    def update_document(
        self,
        db: Session,
        document_id: UUID,
        payload: DocumentUpdate,
        current_user: CurrentUser,
    ) -> Document:
        document = self.get_document(db, document_id, current_user)
        values = payload.model_dump(exclude_unset=True)
        if "document_type" in values:
            self._validate_document_type(values["document_type"])
        if "asset_id" in values:
            self._validate_asset(db, values["asset_id"], document.building_id, document.organization_id)
        for key, value in values.items():
            setattr(document, key, value)
            if key == "title":
                document.name = value
        audit_service.record(
            db,
            action=DOCUMENT_UPDATED,
            entity_type="document",
            entity_id=document.id,
            organization_id=document.organization_id,
            current_user=current_user,
            metadata={"changed_fields": sorted(values.keys())},
        )
        db.commit()
        db.refresh(document)
        return document

    def soft_delete_document(self, db: Session, document_id: UUID, current_user: CurrentUser) -> Document:
        document = self.get_document(db, document_id, current_user)
        document.deleted_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(document)
        return document

    def get_download_path(self, db: Session, document_id: UUID, current_user: CurrentUser) -> Path:
        document = self.get_document(db, document_id, current_user)
        if not document.storage_key:
            raise not_found("Document file is not available.")
        path = local_storage.resolve_path(key=document.storage_key)
        if not path.exists():
            raise not_found("Document file is not available in local storage.")
        return path

    @staticmethod
    def _validate_document_type(value: str) -> None:
        if value not in DOCUMENT_TYPES:
            raise validation_error("Document type is not defined in FMS-0010.")

    @staticmethod
    def _validate_asset(db: Session, asset_id: UUID | None, building_id: UUID, organization_id: UUID) -> None:
        if asset_id is None:
            return
        asset = db.get(Asset, asset_id)
        if asset is None or asset.deleted_at is not None:
            raise not_found("Asset not found.")
        if asset.building_id != building_id or asset.organization_id != organization_id:
            raise validation_error("Asset does not belong to this building.")

    @staticmethod
    def _next_version_number(db: Session, parent_document_id: UUID) -> int:
        max_version = db.scalar(
            select(func.max(Document.version_number)).where(
                (Document.parent_document_id == parent_document_id) | (Document.id == parent_document_id)
            )
        )
        return (max_version or 1) + 1

    @staticmethod
    def _build_storage_key(building_id: UUID, family_id: UUID, filename: str) -> str:
        safe_filename = filename.replace("\\", "_").replace("/", "_")
        return f"buildings/{building_id}/documents/{family_id}/{uuid4()}-{safe_filename}"


document_service = DocumentService()
