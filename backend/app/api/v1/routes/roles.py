from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.schemas.core import RoleRead
from app.services.user_service import user_service

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("")
def list_roles(
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("platform_admin", "organization_admin")),
) -> dict:
    roles = user_service.list_roles(db)
    return {"data": [RoleRead.model_validate(role) for role in roles]}
