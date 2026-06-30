from fastapi import APIRouter

from app.api.v1.routes import (
    auth,
    buildings,
    certificates,
    deficiencies,
    documents,
    inspections,
    memberships,
    reports,
    settings,
    users,
    work_orders,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(buildings.router)
api_router.include_router(work_orders.router)
api_router.include_router(inspections.router)
api_router.include_router(deficiencies.router)
api_router.include_router(documents.router)
api_router.include_router(reports.router)
api_router.include_router(certificates.router)
api_router.include_router(memberships.router)
api_router.include_router(users.router)
api_router.include_router(settings.router)
