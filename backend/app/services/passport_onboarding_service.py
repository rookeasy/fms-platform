from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import CurrentUser
from app.models import Building
from app.schemas.core import PassportOnboardingQueueItem
from app.services.closeout_score_service import closeout_score_service
from app.services.protected_state_service import protected_state_service
from app.services.tenant import ensure_organization_access

FUZION_SOURCE_MARKER = "source=fuzion_active_completed_projects"
PASSPORT_LIFECYCLE_STATUSES = {
    "Not Started",
    "Building Registered",
    "Documents Imported",
    "Assets Verified",
    "Closeout Incomplete",
    "Ready for Passport",
    "Passport Issued",
    "Passport Delivered",
}


class PassportOnboardingService:
    def list_queue(self, db: Session, current_user: CurrentUser, organization_id: UUID | None = None) -> list[PassportOnboardingQueueItem]:
        query = (
            select(Building)
            .options(selectinload(Building.property))
            .where(
                Building.deleted_at.is_(None),
                Building.notes.contains(FUZION_SOURCE_MARKER),
            )
        )
        if organization_id is not None:
            ensure_organization_access(current_user, organization_id)
            query = query.where(Building.organization_id == organization_id)
        elif not current_user.is_platform_admin and current_user.current_organization_id:
            query = query.where(Building.organization_id == UUID(current_user.current_organization_id))

        buildings = list(db.scalars(query.order_by(Building.code, Building.name)).all())
        return [self._queue_item(db, building, current_user) for building in buildings]

    def _queue_item(self, db: Session, building: Building, current_user: CurrentUser) -> PassportOnboardingQueueItem:
        ensure_organization_access(current_user, building.organization_id)
        score = closeout_score_service.get_building_score(db, building.id, current_user)
        protected_state = protected_state_service.get_state(db, building.id, current_user)
        classification = building.project_classification or self._classify_building(building)
        completion_status = self._completion_status(classification, building.status)
        passport_status = building.passport_status if building.passport_status in PASSPORT_LIFECYCLE_STATUSES else "Not Started"
        return PassportOnboardingQueueItem(
            project=building.name,
            property=building.property.name if building.property else None,
            building_id=building.id,
            building=building.name,
            job_no=building.code,
            passport_no=building.bpid,
            project_classification=classification,
            completion_status=completion_status,
            closeout_score=score.completion_percentage,
            missing_items=score.missing_items,
            passport_eligible=building.passport_eligible,
            passport_status=passport_status,
            passport_issue_date=building.passport_issue_date,
            passport_version=building.passport_version,
            client_handover_status=building.client_handover_status,
            protected_state_status=protected_state.protected_state_status,
            halo_eligible=protected_state.halo_eligible,
            next_action=self._next_action(building.passport_eligible, passport_status, score.missing_items, protected_state.protected_state_status),
            closeout_url=f"/buildings/{building.id}/closeout",
            passport_url=f"/buildings/{building.id}/passport",
        )

    @staticmethod
    def _classify_building(building: Building) -> str:
        if building.status == "completed_occupied":
            return "completed"
        if building.status == "archived":
            return "archived"
        return "active"

    @staticmethod
    def _completion_status(classification: str, status: str) -> str:
        if classification == "completed":
            return "Completed Prime Contract"
        if classification == "service-only":
            return "Service Only"
        if classification == "design-only":
            return "Design Only"
        if classification == "archived" or status == "archived":
            return "Archived"
        return "Active"

    @staticmethod
    def _next_action(passport_eligible: bool, passport_status: str, missing_items: list[str], protected_state_status: str) -> str:
        if not passport_eligible:
            return "Monitor project status"
        if protected_state_status == "approved":
            return "Maintain protected-state audit record"
        if protected_state_status == "eligible":
            return "Approve Protected State"
        if protected_state_status in {"suspended", "revoked"}:
            return "Review protected-state exception"
        if passport_status in {"Passport Issued", "Passport Delivered"}:
            return "Evaluate and approve Protected State"
        if protected_state_status == "review_required":
            return "Confirm handover record"
        if missing_items:
            return "Import closeout evidence"
        if passport_status != "Ready for Passport":
            return "Review and mark Ready for Passport"
        return "Issue Passport"


passport_onboarding_service = PassportOnboardingService()
