from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db, require_roles
from app.services.passport_service import passport_service

router = APIRouter(prefix="/buildings", tags=["passport"])


@router.get("/{building_id}/passport")
def get_building_passport(
    building_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "technician", "engineer", "readonly_viewer")),
) -> dict:
    passport = passport_service.get_passport(db, building_id, current_user)
    return {"data": jsonable_encoder(passport)}
