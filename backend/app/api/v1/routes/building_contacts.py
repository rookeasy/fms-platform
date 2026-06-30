from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db, require_roles
from app.schemas.core import BuildingContactRead, BuildingContactUpdate
from app.services.building_service import building_service

router = APIRouter(prefix="/building-contacts", tags=["building-contacts"])


@router.get("/{contact_id}")
def get_building_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "readonly_viewer")),
) -> dict:
    contact = building_service.get_contact(db, contact_id, current_user)
    return {"data": BuildingContactRead.model_validate(contact)}


@router.patch("/{contact_id}")
def update_building_contact(
    contact_id: UUID,
    payload: BuildingContactUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager")),
) -> dict:
    contact = building_service.update_contact(db, contact_id, payload, current_user)
    return {"data": BuildingContactRead.model_validate(contact)}


@router.delete("/{contact_id}", status_code=204)
def delete_building_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager")),
) -> None:
    building_service.soft_delete_contact(db, contact_id, current_user)
