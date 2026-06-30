from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
def read_current_user(current_user: CurrentUser = Depends(get_current_user)) -> dict:
    return {
        "data": {
            "id": current_user.id,
            "email": current_user.email,
            "roles": current_user.roles,
            "current_organization_id": current_user.current_organization_id,
        }
    }
