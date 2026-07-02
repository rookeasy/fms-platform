from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user, get_db, require_roles
from app.schemas.core import (
    PropertyCapitalSummary,
    PropertyConfidenceSummary,
    PropertyDeficiencySummary,
    PropertyHealthSummary,
    PropertyIntelligenceRead,
    PropertyPassportSummary,
    PropertyReadinessSummary,
    PropertyRiskSummary,
)
from app.services.property_intelligence_service import property_intelligence_service

router = APIRouter(tags=["property-intelligence"])
INTELLIGENCE_ROLES = ("platform_admin", "organization_admin", "property_manager", "building_owner", "readonly_viewer")


@router.get("/properties/{property_id}/intelligence")
def get_property_intelligence(
    property_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles(*INTELLIGENCE_ROLES)),
) -> dict:
    intelligence = property_intelligence_service.get_intelligence(db, property_id, current_user)
    return {"data": PropertyIntelligenceRead.model_validate(intelligence)}


@router.post("/properties/{property_id}/intelligence/recalculate")
def recalculate_property_intelligence(
    property_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles("platform_admin", "organization_admin", "property_manager")),
) -> dict:
    intelligence = property_intelligence_service.recalculate_snapshot(db, property_id, current_user)
    return {"data": PropertyIntelligenceRead.model_validate(intelligence)}


@router.get("/properties/{property_id}/intelligence/health")
def get_property_health_summary(
    property_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles(*INTELLIGENCE_ROLES)),
) -> dict:
    summary = property_intelligence_service.get_health_summary(db, property_id, current_user)
    return {"data": PropertyHealthSummary.model_validate(summary)}


@router.get("/properties/{property_id}/intelligence/confidence")
def get_property_confidence_summary(
    property_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles(*INTELLIGENCE_ROLES)),
) -> dict:
    summary = property_intelligence_service.get_confidence_summary(db, property_id, current_user)
    return {"data": PropertyConfidenceSummary.model_validate(summary)}


@router.get("/properties/{property_id}/intelligence/risk")
def get_property_risk_summary(
    property_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles(*INTELLIGENCE_ROLES)),
) -> dict:
    summary = property_intelligence_service.get_risk_summary(db, property_id, current_user)
    return {"data": PropertyRiskSummary.model_validate(summary)}


@router.get("/properties/{property_id}/intelligence/readiness")
def get_property_readiness_summary(
    property_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles(*INTELLIGENCE_ROLES)),
) -> dict:
    summary = property_intelligence_service.get_readiness_summary(db, property_id, current_user)
    return {"data": PropertyReadinessSummary.model_validate(summary)}


@router.get("/properties/{property_id}/intelligence/passport")
def get_property_passport_summary(
    property_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles(*INTELLIGENCE_ROLES)),
) -> dict:
    summary = property_intelligence_service.get_passport_summary(db, property_id, current_user)
    return {"data": PropertyPassportSummary.model_validate(summary)}


@router.get("/properties/{property_id}/intelligence/capital")
def get_property_capital_summary(
    property_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles(*INTELLIGENCE_ROLES)),
) -> dict:
    summary = property_intelligence_service.get_capital_summary(db, property_id, current_user)
    return {"data": PropertyCapitalSummary.model_validate(summary)}


@router.get("/properties/{property_id}/intelligence/deficiencies")
def get_property_deficiency_summary(
    property_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles(*INTELLIGENCE_ROLES)),
) -> dict:
    summary = property_intelligence_service.get_deficiency_summary(db, property_id, current_user)
    return {"data": PropertyDeficiencySummary.model_validate(summary)}


@router.get("/properties/{property_id}/executive-dashboard")
def get_property_executive_dashboard(
    property_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
    _: object = Depends(require_roles(*INTELLIGENCE_ROLES)),
) -> dict:
    intelligence = property_intelligence_service.get_intelligence(db, property_id, current_user)
    return {"data": PropertyIntelligenceRead.model_validate(intelligence)}
