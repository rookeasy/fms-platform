from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, require_roles
from app.schemas.common import PlaceholderResponse

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=PlaceholderResponse)
def read_settings(
    _: object = Depends(get_current_user),
    __: object = Depends(require_roles("admin")),
) -> PlaceholderResponse:
    return PlaceholderResponse(
        module="settings",
        message="Settings route placeholder. Business logic is not implemented yet.",
    )
