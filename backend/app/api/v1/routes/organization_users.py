from uuid import UUID

from fastapi import Query

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db, require_roles
from app.schemas.core import OrganizationUserCreate, OrganizationUserRead, OrganizationUserUpdate
from app.services.user_service import user_service

router = APIRouter(prefix="/organization-users", tags=["organization-users"])


@router.get("")
def list_organization_users(
    organization_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> dict:
    organization_users = user_service.list_organization_users(db, current_user, organization_id)
    return {"data": [OrganizationUserRead.model_validate(organization_user) for organization_user in organization_users]}


@router.post("")
def assign_organization_user(
    payload: OrganizationUserCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> dict:
    organization_user = user_service.assign_organization_user(db, payload, current_user)
    return {"data": OrganizationUserRead.model_validate(organization_user)}


@router.patch("/{organization_user_id}")
def update_organization_user(
    organization_user_id: UUID,
    payload: OrganizationUserUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> dict:
    organization_user = user_service.update_organization_user(db, organization_user_id, payload, current_user)
    return {"data": OrganizationUserRead.model_validate(organization_user)}


@router.delete("/{organization_user_id}", status_code=204)
def delete_organization_user(
    organization_user_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> None:
    user_service.remove_organization_user(db, organization_user_id, current_user)
