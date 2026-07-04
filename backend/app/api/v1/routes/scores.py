from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db, require_roles
from app.schemas.scores import FppScoreRead, PortfolioScoresRead
from app.services.fpp_score_service import fpp_score_service

router = APIRouter(tags=["fpp-scores"])
score_roles = require_roles("platform_admin", "organization_admin", "property_manager", "building_owner", "technician", "engineer", "readonly_viewer")


@router.get("/buildings/{building_id}/scores")
def get_building_scores(
    building_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(score_roles),
) -> dict:
    score = fpp_score_service.get_building_scores(db, building_id, current_user)
    return {"data": FppScoreRead.model_validate(score)}


@router.get("/buildings/{building_id}/health-index")
def get_building_health_index(
    building_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(score_roles),
) -> dict:
    score = fpp_score_service.get_building_health_index(db, building_id, current_user)
    return {"data": FppScoreRead.model_validate(score)}


@router.get("/portfolio/scores")
def get_portfolio_scores(
    organization_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(score_roles),
) -> dict:
    score = fpp_score_service.get_portfolio_scores(db, current_user, organization_id=organization_id)
    return {"data": PortfolioScoresRead.model_validate(score)}


@router.get("/projects/{project_id}/scores")
def get_project_scores(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(score_roles),
) -> dict:
    score = fpp_score_service.get_project_scores(db, project_id, current_user)
    return {"data": FppScoreRead.model_validate(score)}


@router.get("/inspections/{inspection_id}/scores")
def get_inspection_scores(
    inspection_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(score_roles),
) -> dict:
    score = fpp_score_service.get_inspection_scores(db, inspection_id, current_user)
    return {"data": FppScoreRead.model_validate(score)}


@router.get("/closeout/{closeout_id}/scores")
def get_closeout_scores(
    closeout_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(score_roles),
) -> dict:
    score = fpp_score_service.get_closeout_scores(db, closeout_id, current_user)
    return {"data": FppScoreRead.model_validate(score)}
