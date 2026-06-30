from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db, require_roles
from app.schemas.core import AssetCreate, AssetRead, AssetTypeRead, AssetUpdate
from app.services.asset_service import asset_service

router = APIRouter(tags=["assets"])


@router.get("/asset-types")
def list_asset_types(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "technician", "engineer", "readonly_viewer")),
) -> dict:
    asset_types = asset_service.list_asset_types(db, current_user)
    return {"data": [AssetTypeRead.model_validate(asset_type) for asset_type in asset_types]}


@router.get("/assets")
def list_assets(
    organization_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "technician", "engineer", "readonly_viewer")),
) -> dict:
    assets = asset_service.list_assets(db, current_user, organization_id=organization_id)
    return {"data": [AssetRead.model_validate(asset) for asset in assets]}


@router.get("/assets/{asset_id}")
def get_asset(
    asset_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "technician", "engineer", "readonly_viewer")),
) -> dict:
    asset = asset_service.get_asset(db, asset_id, current_user)
    return {"data": AssetRead.model_validate(asset)}


@router.patch("/assets/{asset_id}")
def update_asset(
    asset_id: UUID,
    payload: AssetUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "engineer")),
) -> dict:
    asset = asset_service.update_asset(db, asset_id, payload, current_user)
    return {"data": AssetRead.model_validate(asset)}


@router.delete("/assets/{asset_id}", status_code=204)
def delete_asset(
    asset_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> None:
    asset_service.soft_delete_asset(db, asset_id, current_user)


@router.get("/buildings/{building_id}/assets")
def list_building_assets(
    building_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "technician", "engineer", "readonly_viewer")),
) -> dict:
    assets = asset_service.list_assets(db, current_user, building_id=building_id)
    return {"data": [AssetRead.model_validate(asset) for asset in assets]}


@router.post("/buildings/{building_id}/assets")
def create_building_asset(
    building_id: UUID,
    payload: AssetCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "engineer")),
) -> dict:
    asset = asset_service.create_asset(db, building_id, payload, current_user)
    return {"data": AssetRead.model_validate(asset)}
