from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db, require_roles
from app.schemas.core import UserCreate, UserInvite, UserRead, UserUpdate
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def list_users(
    organization_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> dict:
    users = user_service.list_users(db, current_user, organization_id)
    return {"data": [UserRead.model_validate(user) for user in users]}


@router.post("")
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> dict:
    user = user_service.create_user(db, payload)
    return {"data": UserRead.model_validate(user)}


@router.post("/invite")
def invite_user(
    payload: UserInvite,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> dict:
    user = user_service.invite_user(db, payload, current_user)
    return {"data": UserRead.model_validate(user)}


@router.get("/{user_id}")
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> dict:
    user = user_service.get_user(db, user_id)
    return {"data": UserRead.model_validate(user)}


@router.patch("/{user_id}")
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> dict:
    user = user_service.update_user(db, user_id, payload)
    return {"data": UserRead.model_validate(user)}


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> None:
    user_service.soft_delete_user(db, user_id)
