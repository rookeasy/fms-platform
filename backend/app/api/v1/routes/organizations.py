from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db, require_roles
from app.schemas.core import OrganizationCreate, OrganizationRead, OrganizationUpdate
from app.services.organization_service import organization_service

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("")
def list_organizations(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> dict:
    organizations = organization_service.list_organizations(db, current_user)
    return {"data": [OrganizationRead.model_validate(organization) for organization in organizations]}


@router.post("")
def create_organization(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("platform_admin")),
) -> dict:
    organization = organization_service.create_organization(db, payload)
    return {"data": OrganizationRead.model_validate(organization)}


@router.get("/{organization_id}")
def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> dict:
    organization = organization_service.get_organization(db, organization_id, current_user)
    return {"data": OrganizationRead.model_validate(organization)}


@router.patch("/{organization_id}")
def update_organization(
    organization_id: UUID,
    payload: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> dict:
    organization = organization_service.update_organization(db, organization_id, payload, current_user)
    return {"data": OrganizationRead.model_validate(organization)}


@router.delete("/{organization_id}", status_code=204)
def delete_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin")),
) -> None:
    organization_service.soft_delete_organization(db, organization_id, current_user)
