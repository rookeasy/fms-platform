from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.schemas.common import PlaceholderResponse

router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.get("", response_model=PlaceholderResponse)
def list_buildings(
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
    __: object = Depends(require_roles("admin", "manager", "viewer")),
) -> PlaceholderResponse:
    _ = db
    return PlaceholderResponse(
        module="buildings",
        message="Buildings route placeholder. Business logic is not implemented yet.",
    )
