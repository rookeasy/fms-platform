from datetime import datetime, timezone
import re
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.config import settings
from app.core.constants import DOCUMENT_TYPES, DOCUMENT_UPDATED, DOCUMENT_UPLOADED
from app.models import Asset, Building, Document, Property
from app.schemas.core import DocumentCreate, DocumentUpdate
from app.services.document_extraction_service import document_extraction_service
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
        property_id: UUID | None = None,
        building_id: UUID | None = None,
        document_type: str | None = None,
        is_public_to_client: bool | None = None,
        is_passport_record: bool | None = None,
    ) -> list[Document]:
        query = select(Document).where(Document.deleted_at.is_(None)).order_by(Document.created_at.desc())
        if building_id is not None:
            building = building_service.get_building(db, building_id, current_user)
            query = query.where(Document.building_id == building.id, Document.organization_id == building.organization_id)
        elif property_id is not None:
            property_record = self._get_property(db, property_id, current_user)
            query = query.where(Document.property_id == property_record.id, Document.organization_id == property_record.organization_id)
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
        self._validate_document_status(payload.status)
        self._validate_asset(db, payload.asset_id, building.id, building.organization_id)
        document = Document(
            **payload.model_dump(exclude={"property_id"}),
            organization_id=building.organization_id,
            building_id=building.id,
            property_id=payload.property_id or building.property_id,
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
        building_id: UUID | None,
        payload: DocumentCreate,
        current_user: CurrentUser,
        content,
        filename: str,
        content_type: str | None,
        parent_document_id: UUID | None = None,
        storage: StorageAdapter = local_storage,
    ) -> Document:
        building = building_service.get_building(db, building_id, current_user) if building_id is not None else None
        property_record = self._resolve_property(db, payload.property_id, building, current_user)
        if building is None and property_record is None:
            raise validation_error("Upload must be assigned to a building or property.")
        self._validate_document_type(payload.document_type)
        self._validate_document_status(payload.status)
        self._validate_content_type(content_type)
        organization_id = building.organization_id if building is not None else property_record.organization_id
        if building is not None:
            self._validate_asset(db, payload.asset_id, building.id, organization_id)
        elif payload.asset_id is not None:
            raise validation_error("Asset assignment requires a building.")
        parent_document = None
        version_number = 1
        if parent_document_id is not None:
            parent_document = self.get_document(db, parent_document_id, current_user)
            if building is None or parent_document.building_id != building.id:
                raise validation_error("Replacement document must belong to the same building.")
            version_number = self._next_version_number(db, parent_document.id)

        key = self._build_storage_key(building.id if building is not None else property_record.id, parent_document_id or uuid4(), filename)
        stored_file = storage.save(key=key, content=content)
        if stored_file.size_bytes > settings.upload_max_size_bytes:
            Path(stored_file.path).unlink(missing_ok=True)
            raise validation_error("Uploaded file exceeds the configured size limit.")

        document = Document(
            organization_id=organization_id,
            property_id=payload.property_id or (building.property_id if building is not None else property_record.id),
            building_id=building.id if building is not None else None,
            asset_id=payload.asset_id,
            uploaded_by_user_id=None,
            name=payload.title,
            title=payload.title,
            description=payload.description,
            document_type=payload.document_type,
            evidence_category=payload.evidence_category,
            drawing_number=payload.drawing_number,
            revision=payload.revision,
            issue_date=payload.issue_date,
            status=payload.status,
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
            internal_only=not (payload.is_public_to_client or payload.is_passport_record),
            extraction_status="pending",
            notes=payload.notes,
        )
        db.add(document)
        db.flush()
        suggestions = document_extraction_service.run_extraction(db, document)
        audit_service.record(
            db,
            action=DOCUMENT_UPLOADED,
            entity_type="document",
            entity_id=document.id,
            organization_id=document.organization_id,
            current_user=current_user,
            metadata={
                "building_id": str(building.id) if building is not None else None,
                "property_id": str(document.property_id) if document.property_id else None,
                "document_type": document.document_type,
                "version_number": document.version_number,
                "is_passport_record": document.is_passport_record,
                "asset_suggestion_count": len(suggestions),
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
        if "status" in values:
            self._validate_document_status(values["status"])
        next_building_id = values.get("building_id", document.building_id)
        next_property_id = values.get("property_id", document.property_id)
        if next_building_id is not None and next_building_id != document.building_id:
            building = building_service.get_building(db, next_building_id, current_user)
            if building.organization_id != document.organization_id:
                raise validation_error("Building assignment must stay within the document organization.")
            if "property_id" not in values:
                values["property_id"] = building.property_id
        elif next_property_id is not None:
            self._get_property(db, next_property_id, current_user)
        if "asset_id" in values:
            if values["asset_id"] is not None and next_building_id is None:
                raise validation_error("Asset assignment requires a building.")
            self._validate_asset(db, values["asset_id"], next_building_id, document.organization_id)
        for key, value in values.items():
            setattr(document, key, value)
            if key == "title":
                document.name = value
        if {"is_public_to_client", "is_passport_record"}.intersection(values):
            document.internal_only = not (document.is_public_to_client or document.is_passport_record)
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
        document.archived_at = document.deleted_at
        document.status = "archived"
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
    def _validate_document_status(value: str) -> None:
        if value not in {"draft", "accepted", "as-built", "superseded", "archived"}:
            raise validation_error("Document status is not defined for upload review.")

    @staticmethod
    def _validate_content_type(value: str | None) -> None:
        content_type = (value or "application/octet-stream").split(";", 1)[0].lower()
        if content_type not in settings.allowed_upload_types:
            raise validation_error("Uploaded file type is not allowed.")

    @staticmethod
    def _validate_asset(db: Session, asset_id: UUID | None, building_id: UUID | None, organization_id: UUID) -> None:
        if asset_id is None:
            return
        asset = db.get(Asset, asset_id)
        if asset is None or asset.deleted_at is not None:
            raise not_found("Asset not found.")
        if building_id is None or asset.building_id != building_id or asset.organization_id != organization_id:
            raise validation_error("Asset does not belong to this building.")

    @staticmethod
    def _get_property(db: Session, property_id: UUID, current_user: CurrentUser) -> Property:
        property_record = db.get(Property, property_id)
        if property_record is None or property_record.deleted_at is not None:
            raise not_found("Property not found.")
        ensure_organization_access(current_user, property_record.organization_id)
        return property_record

    def _resolve_property(
        self,
        db: Session,
        property_id: UUID | None,
        building: Building | None,
        current_user: CurrentUser,
    ) -> Property | None:
        if property_id is not None:
            property_record = self._get_property(db, property_id, current_user)
            if building is not None and building.property_id is not None and building.property_id != property_record.id:
                raise validation_error("Property assignment does not match the selected building.")
            return property_record
        if building is not None and building.property_id is not None:
            return db.get(Property, building.property_id)
        return None

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
        safe_filename = re.sub(r"[^A-Za-z0-9._-]+", "_", filename.replace("\\", "_").replace("/", "_")).strip("._")
        if not safe_filename:
            safe_filename = "upload"
        return f"documents/{building_id}/{family_id}/{uuid4()}-{safe_filename[:160]}"


document_service = DocumentService()
