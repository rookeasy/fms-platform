from fastapi import APIRouter

from app.api.v1.routes import (
    auth,
    assets,
    building_contacts,
    buildings,
    certificates,
    deficiencies,
    documents,
    inspections,
    memberships,
    mobile,
    organization_users,
    organizations,
    passport,
    passport_onboarding,
    property_intelligence,
    properties,
    reports,
    roles,
    search,
    settings,
    scores,
    users,
    work_orders,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(organizations.router)
api_router.include_router(buildings.router)
api_router.include_router(assets.router)
api_router.include_router(building_contacts.router)
api_router.include_router(work_orders.router)
api_router.include_router(inspections.router)
api_router.include_router(deficiencies.router)
api_router.include_router(documents.router)
api_router.include_router(passport.router)
api_router.include_router(passport_onboarding.router)
api_router.include_router(property_intelligence.router)
api_router.include_router(properties.router)
api_router.include_router(reports.router)
api_router.include_router(certificates.router)
api_router.include_router(memberships.router)
api_router.include_router(mobile.router)
api_router.include_router(roles.router)
api_router.include_router(organization_users.router)
api_router.include_router(users.router)
api_router.include_router(settings.router)
api_router.include_router(search.router)
api_router.include_router(scores.router)
