from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db, require_roles
from app.schemas.core import SearchResult
from app.services.search_service import search_service

router = APIRouter(tags=["search"])


@router.get("/search")
def global_search(
    q: str = Query(default=""),
    type: str | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "technician", "engineer", "readonly_viewer")),
) -> dict:
    results = search_service.search(db, current_user, q, type, limit)
    return {"data": [SearchResult(**result) for result in results]}
