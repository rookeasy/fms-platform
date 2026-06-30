from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.schemas.common import PlaceholderResponse

router = APIRouter(prefix="/deficiencies", tags=["deficiencies"])


@router.get("", response_model=PlaceholderResponse)
def list_deficiencies(
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
    __: object = Depends(require_roles("admin", "manager", "inspector")),
) -> PlaceholderResponse:
    _ = db
    return PlaceholderResponse(
        module="deficiencies",
        message="Deficiencies route placeholder. Business logic is not implemented yet.",
    )
