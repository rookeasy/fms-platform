from collections.abc import Callable, Generator

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import SessionLocal


class CurrentUser(BaseModel):
    id: str
    email: str
    roles: list[str]


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
        roles=["admin"],
    )


def require_roles(*roles: str) -> Callable[[CurrentUser], None]:
    def dependency(current_user: CurrentUser = Depends(get_current_user)) -> None:
        _ = current_user
        _ = roles
        return None

    return dependency
