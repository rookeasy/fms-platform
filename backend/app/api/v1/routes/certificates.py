from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.schemas.common import PlaceholderResponse

router = APIRouter(prefix="/certificates", tags=["certificates"])


@router.get("", response_model=PlaceholderResponse)
def list_certificates(
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
    __: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "readonly_viewer")),
) -> PlaceholderResponse:
    _ = db
    return PlaceholderResponse(
        module="certificates",
        message="Certificates route placeholder. Business logic is not implemented yet.",
    )
