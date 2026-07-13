from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db, require_roles
from app.schemas.core import PassportOnboardingQueueItem
from app.services.passport_onboarding_service import passport_onboarding_service

router = APIRouter(prefix="/passports", tags=["passport-onboarding"])


@router.get("/onboarding")
def list_passport_onboarding_queue(
    organization_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "readonly_viewer")),
) -> dict:
    queue = passport_onboarding_service.list_queue(db, current_user, organization_id)
    return {"data": [PassportOnboardingQueueItem.model_validate(item) for item in queue]}
