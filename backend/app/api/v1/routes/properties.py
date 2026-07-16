from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db, require_roles
from app.schemas.core import (
    BuildingAssignment,
    BuildingRead,
    CampusCreate,
    CampusRead,
    CampusUpdate,
    PropertyCampusSummary,
    PropertyCloseoutScore,
    PropertyCreate,
    PropertyRead,
    PropertyUpdate,
    SohoPassportReadinessRead,
)
from app.services.closeout_score_service import closeout_score_service
from app.services.property_service import property_service
from app.services.soho_passport_readiness_service import soho_passport_readiness_service

router = APIRouter(tags=["properties"])


@router.get("/properties/summary")
def get_property_campus_summary(
    organization_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "readonly_viewer")),
) -> dict:
    summary = property_service.get_summary(db, current_user, organization_id)
    return {"data": PropertyCampusSummary(**summary)}


@router.get("/properties")
def list_properties(
    organization_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "readonly_viewer")),
) -> dict:
    properties = property_service.list_properties(db, current_user, organization_id)
    return {"data": [PropertyRead.model_validate(property_record) for property_record in properties]}


@router.post("/properties")
def create_property(
    payload: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager")),
) -> dict:
    property_record = property_service.create_property(db, payload, current_user)
    return {"data": PropertyRead.model_validate(property_record)}


@router.get("/properties/{property_id}")
def get_property(
    property_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "readonly_viewer")),
) -> dict:
    property_record = property_service.get_property(db, property_id, current_user)
    return {"data": PropertyRead.model_validate(property_record)}


@router.get("/properties/{property_id}/closeout/score")
def get_property_closeout_score(
    property_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "readonly_viewer")),
) -> dict:
    score = closeout_score_service.get_property_score(db, property_id, current_user)
    return {"data": PropertyCloseoutScore.model_validate(score)}


@router.get("/properties/{property_id}/passport-readiness")
def get_property_passport_readiness(
    property_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "readonly_viewer")),
) -> dict:
    readiness = soho_passport_readiness_service.get_readiness(db, property_id, current_user)
    return {"data": SohoPassportReadinessRead.model_validate(readiness)}


@router.patch("/properties/{property_id}")
def update_property(
    property_id: UUID,
    payload: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager")),
) -> dict:
    property_record = property_service.update_property(db, property_id, payload, current_user)
    return {"data": PropertyRead.model_validate(property_record)}


@router.delete("/properties/{property_id}", status_code=204)
def delete_property(
    property_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> None:
    property_service.soft_delete_property(db, property_id, current_user)


@router.get("/campuses")
def list_campuses(
    organization_id: UUID | None = Query(default=None),
    property_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "readonly_viewer")),
) -> dict:
    campuses = property_service.list_campuses(db, current_user, organization_id, property_id)
    return {"data": [CampusRead.model_validate(campus) for campus in campuses]}


@router.post("/campuses")
def create_campus(
    payload: CampusCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager")),
) -> dict:
    campus = property_service.create_campus(db, payload, current_user)
    return {"data": CampusRead.model_validate(campus)}


@router.get("/campuses/{campus_id}")
def get_campus(
    campus_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "readonly_viewer")),
) -> dict:
    campus = property_service.get_campus(db, campus_id, current_user)
    return {"data": CampusRead.model_validate(campus)}


@router.patch("/campuses/{campus_id}")
def update_campus(
    campus_id: UUID,
    payload: CampusUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager")),
) -> dict:
    campus = property_service.update_campus(db, campus_id, payload, current_user)
    return {"data": CampusRead.model_validate(campus)}


@router.delete("/campuses/{campus_id}", status_code=204)
def delete_campus(
    campus_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> None:
    property_service.soft_delete_campus(db, campus_id, current_user)


@router.patch("/buildings/{building_id}/property-campus")
def assign_building_to_property_campus(
    building_id: UUID,
    payload: BuildingAssignment,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager")),
) -> dict:
    building = property_service.assign_building(db, building_id, payload, current_user)
    return {"data": BuildingRead.model_validate(building)}
