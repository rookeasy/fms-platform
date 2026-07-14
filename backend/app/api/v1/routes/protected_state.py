from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db, require_roles
from app.schemas.core import ProtectedStateAction
from app.services.protected_state_service import protected_state_service

router = APIRouter(prefix="/buildings", tags=["protected-state"])


@router.get("/{building_id}/protected-state")
def get_building_protected_state(
    building_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "technician", "engineer", "readonly_viewer")),
) -> dict:
    state = protected_state_service.get_state(db, building_id, current_user)
    return {"data": jsonable_encoder(state)}


@router.post("/{building_id}/protected-state/evaluate")
def evaluate_building_protected_state(
    building_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "engineer")),
) -> dict:
    state = protected_state_service.evaluate(db, building_id, current_user)
    return {"data": jsonable_encoder(state)}


@router.post("/{building_id}/protected-state/approve")
def approve_building_protected_state(
    building_id: UUID,
    payload: ProtectedStateAction | None = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "engineer")),
) -> dict:
    state = protected_state_service.approve(db, building_id, payload or ProtectedStateAction(), current_user)
    return {"data": jsonable_encoder(state)}


@router.post("/{building_id}/protected-state/suspend")
def suspend_building_protected_state(
    building_id: UUID,
    payload: ProtectedStateAction | None = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "engineer")),
) -> dict:
    state = protected_state_service.suspend(db, building_id, payload or ProtectedStateAction(), current_user)
    return {"data": jsonable_encoder(state)}


@router.post("/{building_id}/protected-state/revoke")
def revoke_building_protected_state(
    building_id: UUID,
    payload: ProtectedStateAction | None = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "engineer")),
) -> dict:
    state = protected_state_service.revoke(db, building_id, payload or ProtectedStateAction(), current_user)
    return {"data": jsonable_encoder(state)}
