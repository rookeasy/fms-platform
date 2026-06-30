from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.schemas.common import PlaceholderResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=PlaceholderResponse)
def read_current_user(_: object = Depends(get_current_user)) -> PlaceholderResponse:
    return PlaceholderResponse(
        module="auth",
        message="Authentication dependency placeholder is active.",
    )
