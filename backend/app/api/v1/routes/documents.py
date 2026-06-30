from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.schemas.common import PlaceholderResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=PlaceholderResponse)
def list_documents(
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
    __: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "readonly_viewer")),
) -> PlaceholderResponse:
    _ = db
    return PlaceholderResponse(
        module="documents",
        message="Documents route placeholder. Business logic is not implemented yet.",
    )
