from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db, require_roles
from app.schemas.core import BuildingContactCreate, BuildingContactRead, BuildingCreate, BuildingLibraryRead, BuildingRead, BuildingUpdate, CloseoutScore
from app.services.building_service import building_service
from app.services.building_library_service import building_library_service
from app.services.closeout_score_service import closeout_score_service

router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.get("")
def list_buildings(
    organization_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "readonly_viewer")),
) -> dict:
    buildings = building_service.list_buildings(db, current_user, organization_id)
    return {"data": [BuildingRead.model_validate(building) for building in buildings]}


@router.post("")
def create_building(
    payload: BuildingCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager")),
) -> dict:
    building = building_service.create_building(db, payload, current_user)
    return {"data": BuildingRead.model_validate(building)}


@router.get("/{building_id}")
def get_building(
    building_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "readonly_viewer")),
) -> dict:
    building = building_service.get_building(db, building_id, current_user)
    return {"data": BuildingRead.model_validate(building)}


@router.get("/{building_id}/closeout/score")
def get_building_closeout_score(
    building_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "readonly_viewer")),
) -> dict:
    score = closeout_score_service.get_building_score(db, building_id, current_user)
    return {"data": CloseoutScore.model_validate(score)}


@router.get("/{building_id}/library")
def get_building_library(
    building_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "technician", "engineer", "readonly_viewer")),
) -> dict:
    library = building_library_service.get_building_library(db, building_id, current_user)
    return {"data": BuildingLibraryRead.model_validate(library)}


@router.patch("/{building_id}")
def update_building(
    building_id: UUID,
    payload: BuildingUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager")),
) -> dict:
    building = building_service.update_building(db, building_id, payload, current_user)
    return {"data": BuildingRead.model_validate(building)}


@router.delete("/{building_id}", status_code=204)
def delete_building(
    building_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> None:
    building_service.soft_delete_building(db, building_id, current_user)


@router.get("/{building_id}/contacts")
def list_building_contacts(
    building_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "readonly_viewer")),
) -> dict:
    contacts = building_service.list_contacts(db, building_id, current_user)
    return {"data": [BuildingContactRead.model_validate(contact) for contact in contacts]}


@router.post("/{building_id}/contacts")
def create_building_contact(
    building_id: UUID,
    payload: BuildingContactCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager")),
) -> dict:
    contact = building_service.create_contact(db, building_id, payload, current_user)
    return {"data": BuildingContactRead.model_validate(contact)}
