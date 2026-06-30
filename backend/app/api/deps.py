from collections.abc import Callable, Generator

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.constants import USER_ROLES
from app.db.session import SessionLocal


class CurrentUser(BaseModel):
    id: str
    email: str
    roles: list[str]
    current_organization_id: str | None = None

    @property
    def is_platform_admin(self) -> bool:
        return "platform_admin" in self.roles


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user() -> CurrentUser:
    return CurrentUser(
        id="placeholder-user",
        email="placeholder@fms.local",
        roles=["platform_admin"],
    )


def require_roles(*roles: str) -> Callable[[CurrentUser], None]:
    def dependency(current_user: CurrentUser = Depends(get_current_user)) -> None:
        allowed_roles = set(roles)
        if allowed_roles - USER_ROLES:
            raise HTTPException(status_code=500, detail="Configured role is not defined in FMS-0010.")
        if current_user.is_platform_admin:
            return None
        if not allowed_roles.intersection(current_user.roles):
            raise HTTPException(status_code=403, detail="Permission denied.")
        return None

    return dependency
