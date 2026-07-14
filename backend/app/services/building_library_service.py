from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.models import Building, Document
from app.schemas.core import (
    BuildingLibraryIndexItem,
    BuildingLibraryRead,
    BuildingRead,
    DocumentRead,
    EvidenceCategorySummary,
    PropertyRead,
)
from app.services.building_service import building_service
from app.services.closeout_score_service import closeout_score_service


EVIDENCE_CATEGORIES = [
    "Building Protection Passport",
    "Drawings",
    "As-Built Drawings",
    "P.Eng. Compliance",
    "NFPA Contractor Compliance",
    "Material & Test Certificates",
    "Asset Register",
    "Warranty",
    "Product Data",
    "O&M Manuals",
    "Photos",
    "Handover",
    "ITM Transition",
    "Membership",
    "Other",
]


class BuildingLibraryService:
    def list_library(self, db: Session, current_user: CurrentUser, organization_id: UUID | None = None) -> list[BuildingLibraryIndexItem]:
        buildings = building_service.list_buildings(db, current_user, organization_id)
        return [self._index_item(db, building, current_user) for building in buildings]

    def get_building_library(self, db: Session, building_id: UUID, current_user: CurrentUser) -> BuildingLibraryRead:
        building = building_service.get_building(db, building_id, current_user)
        documents = self._documents_for_building(db, building.id)
        closeout = closeout_score_service.get_building_score(db, building.id, current_user)
        return BuildingLibraryRead(
            building=BuildingRead.model_validate(building),
            property=PropertyRead.model_validate(building.property) if building.property else None,
            total_evidence_items=len(documents),
            passport_completion_percentage=closeout.completion_percentage,
            closeout_readiness_state=self._readiness_state(closeout.ready_for_handover, closeout.completion_percentage),
            last_updated=self._last_updated(building, documents),
            missing_evidence_count=len(closeout.missing_items),
            lifecycle_stage=self._lifecycle_stage(building),
            categories=self._category_summaries(documents),
            documents=[DocumentRead.model_validate(document) for document in documents],
            missing_items=closeout.missing_items,
            closeout_score=closeout,
        )

    def _index_item(self, db: Session, building: Building, current_user: CurrentUser) -> BuildingLibraryIndexItem:
        documents = self._documents_for_building(db, building.id)
        closeout = closeout_score_service.get_building_score(db, building.id, current_user)
        return BuildingLibraryIndexItem(
            building_id=building.id,
            building_name=building.name,
            property_id=building.property_id,
            property_name=building.property.name if building.property else None,
            job_no=building.code,
            passport_no=building.bpid,
            total_evidence_items=len(documents),
            passport_completion_percentage=closeout.completion_percentage,
            closeout_readiness_state=self._readiness_state(closeout.ready_for_handover, closeout.completion_percentage),
            last_updated=self._last_updated(building, documents),
            missing_evidence_count=len(closeout.missing_items),
            lifecycle_stage=self._lifecycle_stage(building),
            status=building.passport_status or self._readiness_state(closeout.ready_for_handover, closeout.completion_percentage),
            library_url=f"/buildings/{building.id}/library",
            passport_url=f"/buildings/{building.id}/passport",
        )

    @staticmethod
    def _documents_for_building(db: Session, building_id: UUID) -> list[Document]:
        return list(
            db.scalars(
                select(Document)
                .where(Document.building_id == building_id, Document.deleted_at.is_(None))
                .order_by(Document.updated_at.desc())
            ).all()
        )

    @staticmethod
    def _last_updated(building: Building, documents: list[Document]) -> datetime | None:
        dates = [building.updated_at, *[document.updated_at for document in documents if document.updated_at]]
        return max(dates) if dates else None

    @staticmethod
    def _readiness_state(ready_for_handover: bool, completion_percentage: int) -> str:
        if ready_for_handover:
            return "Ready for Passport"
        if completion_percentage >= 80:
            return "Closeout Review"
        if completion_percentage > 0:
            return "Evidence Incomplete"
        return "Not Started"

    @staticmethod
    def _lifecycle_stage(building: Building) -> str:
        classification = (building.project_classification or building.status or "").lower()
        if "completed" in classification or building.passport_status in {"Passport Issued", "Passport Delivered"}:
            return "PROTECT"
        if "design" in classification or "service" in classification:
            return "ADVISE"
        return "BUILD"

    def _category_summaries(self, documents: list[Document]) -> list[EvidenceCategorySummary]:
        return [self._category_summary(category, documents) for category in EVIDENCE_CATEGORIES]

    @staticmethod
    def _category_summary(category: str, documents: list[Document]) -> EvidenceCategorySummary:
        category_key = category.lower()
        matches = [
            document
            for document in documents
            if (document.evidence_category or "").lower() == category_key
            or category_key in (document.evidence_category or "").lower()
            or category_key in (document.document_type or "").replace("_", " ").lower()
        ]
        latest = max(matches, key=lambda document: document.updated_at) if matches else None
        complete = any(document.is_passport_record or document.is_public_to_client for document in matches)
        return EvidenceCategorySummary(
            category=category,
            item_count=len(matches),
            complete=complete,
            status="Complete" if complete else ("Review" if matches else "Missing"),
            latest_revision=latest.revision if latest else None,
            latest_date=latest.updated_at if latest else None,
            missing=not complete,
        )


building_library_service = BuildingLibraryService()
