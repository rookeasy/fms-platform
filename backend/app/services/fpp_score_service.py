from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.models import Asset, Building, Deficiency, Document, Inspection, WorkOrder
from app.schemas.scores import FppScoreRead, PortfolioBuildingScoreRead, PortfolioScoresRead
from app.services.building_service import building_service
from app.services.closeout_score_service import closeout_score_service
from app.services.exceptions import not_found
from app.services.tenant import ensure_organization_access


ACTIVE_DEFICIENCY_STATUSES = {"open", "new", "in_progress", "pending", "unresolved"}
CLOSED_DEFICIENCY_STATUSES = {"closed", "complete", "completed", "resolved"}
ACTIVE_WORK_ORDER_STATUSES = {"open", "new", "in_progress", "pending", "scheduled", "in_review"}
COMPLETE_WORK_ORDER_STATUSES = {"complete", "completed", "closed", "resolved"}
DRAWING_DOCUMENT_TYPES = {"drawing", "shop_drawing", "as_built_drawing"}
COMPLIANCE_DOCUMENT_TYPES = {
    "inspection_report",
    "certificate",
    "building_protection_certificate",
    "material_test_certificate",
    "contractors_material_test_certificate",
    "backflow_test_report",
    "fire_pump_test_report",
    "sprinkler_test_report",
    "standpipe_test_report",
    "alarm_verification_report",
}
SERVICE_DOCUMENT_TYPES = {"service_record", "work_order", "deficiency_report", "photo"}


@dataclass(frozen=True)
class BuildingScoreInputs:
    building: Building
    assets: list[Asset]
    documents: list[Document]
    inspections: list[Inspection]
    deficiencies: list[Deficiency]
    work_orders: list[WorkOrder]
    closeout_completion: int
    closeout_ready: bool


class FppScoreService:
    def get_building_scores(self, db: Session, building_id: UUID, current_user: CurrentUser) -> FppScoreRead:
        building = building_service.get_building(db, building_id, current_user)
        return self._score_building(db, building, current_user)

    def get_building_health_index(self, db: Session, building_id: UUID, current_user: CurrentUser) -> FppScoreRead:
        return self.get_building_scores(db, building_id, current_user)

    def get_portfolio_scores(
        self,
        db: Session,
        current_user: CurrentUser,
        organization_id: UUID | None = None,
    ) -> PortfolioScoresRead:
        query = select(Building).where(Building.deleted_at.is_(None)).order_by(Building.name)
        if organization_id is not None:
            ensure_organization_access(current_user, organization_id)
            query = query.where(Building.organization_id == organization_id)
        elif not current_user.is_platform_admin and current_user.current_organization_id:
            query = query.where(Building.organization_id == UUID(current_user.current_organization_id))

        buildings = list(db.scalars(query).all())
        scores = [self._score_building(db, building, current_user) for building in buildings]
        calculated_at = datetime.now(timezone.utc)
        return PortfolioScoresRead(
            protectionScore=self._average([score.protectionScore for score in scores]),
            complianceScore=self._average([score.complianceScore for score in scores]),
            readinessScore=self._average([score.readinessScore for score in scores]),
            intelligenceScore=self._average([score.intelligenceScore for score in scores]),
            buildingHealthIndex=self._average([score.buildingHealthIndex for score in scores]),
            scoreDrivers=self._portfolio_drivers(scores),
            lastCalculatedAt=calculated_at,
            buildingCount=len(buildings),
            buildings=[
                PortfolioBuildingScoreRead(
                    **score.model_dump(),
                    buildingName=building.name,
                )
                for building, score in zip(buildings, scores, strict=False)
            ],
        )

    def get_project_scores(self, db: Session, project_id: UUID, current_user: CurrentUser) -> FppScoreRead:
        building = db.scalar(select(Building).where(Building.id == project_id, Building.deleted_at.is_(None)))
        if building is not None:
            ensure_organization_access(current_user, building.organization_id)
            score = self._score_building(db, building, current_user)
            return score.model_copy(update={"targetType": "project", "targetId": project_id})

        work_order = db.scalar(select(WorkOrder).where(WorkOrder.id == project_id, WorkOrder.deleted_at.is_(None)))
        if work_order is None:
            raise not_found("Project score target not found.")
        ensure_organization_access(current_user, work_order.organization_id)
        building = building_service.get_building(db, work_order.building_id, current_user)
        score = self._score_building(db, building, current_user)
        return score.model_copy(update={"targetType": "project", "targetId": project_id})

    def get_inspection_scores(self, db: Session, inspection_id: UUID, current_user: CurrentUser) -> FppScoreRead:
        inspection = db.scalar(select(Inspection).where(Inspection.id == inspection_id, Inspection.deleted_at.is_(None)))
        if inspection is None:
            raise not_found("Inspection score target not found.")
        ensure_organization_access(current_user, inspection.organization_id)
        building = building_service.get_building(db, inspection.building_id, current_user)
        score = self._score_building(db, building, current_user)
        drivers = [
            *score.scoreDrivers,
            f"Inspection status is {inspection.status}.",
        ]
        if inspection.completed_at:
            drivers.append("Inspection has a completed timestamp.")
        return score.model_copy(update={"targetType": "inspection", "targetId": inspection_id, "scoreDrivers": drivers[:8]})

    def get_closeout_scores(self, db: Session, closeout_id: UUID, current_user: CurrentUser) -> FppScoreRead:
        score = self.get_building_scores(db, closeout_id, current_user)
        return score.model_copy(update={"targetType": "closeout", "targetId": closeout_id})

    def _score_building(self, db: Session, building: Building, current_user: CurrentUser) -> FppScoreRead:
        inputs = self._building_inputs(db, building, current_user)
        protection = self._protection_score(inputs)
        compliance = self._compliance_score(inputs)
        readiness = self._readiness_score(inputs)
        intelligence = self._intelligence_score(inputs)
        building_health = self._average([protection, compliance, readiness, intelligence])
        drivers = self._score_drivers(inputs, protection, compliance, readiness, intelligence, building_health)
        return FppScoreRead(
            protectionScore=protection,
            complianceScore=compliance,
            readinessScore=readiness,
            intelligenceScore=intelligence,
            buildingHealthIndex=building_health,
            scoreDrivers=drivers,
            lastCalculatedAt=datetime.now(timezone.utc),
            targetType="building",
            targetId=building.id,
            buildingId=building.id,
        )

    def _building_inputs(self, db: Session, building: Building, current_user: CurrentUser) -> BuildingScoreInputs:
        documents = list(
            db.scalars(
                select(Document).where(
                    Document.building_id == building.id,
                    Document.organization_id == building.organization_id,
                    Document.deleted_at.is_(None),
                )
            ).all()
        )
        assets = list(
            db.scalars(
                select(Asset).where(
                    Asset.building_id == building.id,
                    Asset.organization_id == building.organization_id,
                    Asset.deleted_at.is_(None),
                )
            ).all()
        )
        inspections = list(
            db.scalars(
                select(Inspection).where(
                    Inspection.building_id == building.id,
                    Inspection.organization_id == building.organization_id,
                    Inspection.deleted_at.is_(None),
                )
            ).all()
        )
        deficiencies = list(
            db.scalars(
                select(Deficiency).where(
                    Deficiency.building_id == building.id,
                    Deficiency.organization_id == building.organization_id,
                    Deficiency.deleted_at.is_(None),
                )
            ).all()
        )
        work_orders = list(
            db.scalars(
                select(WorkOrder).where(
                    WorkOrder.building_id == building.id,
                    WorkOrder.organization_id == building.organization_id,
                    WorkOrder.deleted_at.is_(None),
                )
            ).all()
        )
        try:
            closeout = closeout_score_service.get_building_score(db, building.id, current_user)
            closeout_completion = closeout.completion_percentage
            closeout_ready = closeout.ready_for_handover
        except Exception:
            closeout_completion = 0
            closeout_ready = False

        return BuildingScoreInputs(
            building=building,
            assets=assets,
            documents=documents,
            inspections=inspections,
            deficiencies=deficiencies,
            work_orders=work_orders,
            closeout_completion=closeout_completion,
            closeout_ready=closeout_ready,
        )

    def _protection_score(self, inputs: BuildingScoreInputs) -> int:
        open_deficiencies = self._open_deficiencies(inputs.deficiencies)
        overdue_deficiencies = self._overdue_deficiencies(inputs.deficiencies)
        active_work_orders = self._active_work_orders(inputs.work_orders)
        score = 88
        score -= min(36, len(open_deficiencies) * 6)
        score -= min(20, len(overdue_deficiencies) * 8)
        score -= min(15, len(active_work_orders) * 3)
        score += min(8, len(self._completed_work_orders(inputs.work_orders)) * 2)
        score += 4 if inputs.inspections and any(inspection.completed_at for inspection in inputs.inspections) else 0
        return self._clamp(score)

    def _compliance_score(self, inputs: BuildingScoreInputs) -> int:
        current_inspections = [inspection for inspection in inputs.inspections if inspection.completed_at or inspection.status in {"complete", "completed", "closed"}]
        compliance_documents = [document for document in inputs.documents if document.document_type in COMPLIANCE_DOCUMENT_TYPES]
        score = 55
        score += min(20, len(current_inspections) * 10)
        score += min(20, len(compliance_documents) * 5)
        score += 8 if any(document.document_type in DRAWING_DOCUMENT_TYPES for document in inputs.documents) else 0
        score -= min(25, len(self._overdue_deficiencies(inputs.deficiencies)) * 8)
        return self._clamp(score)

    def _readiness_score(self, inputs: BuildingScoreInputs) -> int:
        score = round(inputs.closeout_completion * 0.72)
        score += 8 if inputs.building.owner_name or inputs.building.property_manager_name else 0
        score += 8 if inputs.assets else 0
        score += 6 if any(document.document_type in DRAWING_DOCUMENT_TYPES for document in inputs.documents) else 0
        score += 6 if inputs.closeout_ready else 0
        return self._clamp(score)

    def _intelligence_score(self, inputs: BuildingScoreInputs) -> int:
        complete_assets = [
            asset
            for asset in inputs.assets
            if asset.condition_rating or asset.manufacturer or asset.model or asset.serial_number or asset.location_description
        ]
        score = 44
        score += min(22, len(inputs.documents) * 3)
        score += round((len(complete_assets) / len(inputs.assets)) * 24) if inputs.assets else 0
        score += 6 if inputs.building.occupancy_classification else 0
        score += 4 if inputs.building.total_area_sq_ft or inputs.building.number_of_storeys else 0
        score += 4 if inputs.inspections else 0
        return self._clamp(score)

    def _score_drivers(
        self,
        inputs: BuildingScoreInputs,
        protection: int,
        compliance: int,
        readiness: int,
        intelligence: int,
        building_health: int,
    ) -> list[str]:
        drivers: list[str] = []
        open_deficiencies = self._open_deficiencies(inputs.deficiencies)
        overdue_deficiencies = self._overdue_deficiencies(inputs.deficiencies)
        closed_deficiencies = [item for item in inputs.deficiencies if item.status in CLOSED_DEFICIENCY_STATUSES or item.resolved_at]
        drawings = [document for document in inputs.documents if document.document_type in DRAWING_DOCUMENT_TYPES]
        compliance_documents = [document for document in inputs.documents if document.document_type in COMPLIANCE_DOCUMENT_TYPES]

        drivers.append(f"Building Health Index is {building_health}% from Protection {protection}%, Compliance {compliance}%, Readiness {readiness}%, and Intelligence {intelligence}%.")
        if inputs.inspections:
            completed_count = sum(1 for inspection in inputs.inspections if inspection.completed_at or inspection.status in {"complete", "completed", "closed"})
            drivers.append(f"{completed_count}/{len(inputs.inspections)} inspection record(s) are complete or current.")
        else:
            drivers.append("No inspection records are available.")
        if open_deficiencies:
            drivers.append(f"{len(open_deficiencies)} open deficiencies remain unresolved.")
        else:
            drivers.append("No open deficiencies are currently recorded.")
        if overdue_deficiencies:
            drivers.append(f"{len(overdue_deficiencies)} deficiencies are overdue.")
        if closed_deficiencies:
            drivers.append(f"{len(closed_deficiencies)} deficiencies have been closed or resolved.")
        drivers.append(f"Closeout progress is {inputs.closeout_completion}%.")
        drivers.append("As-built or drawing evidence is uploaded." if drawings else "As-built drawings or drawing register evidence is missing.")
        drivers.append(f"{len(compliance_documents)} compliance document(s) are attached.")
        drivers.append(f"{len(inputs.assets)} asset register item(s) support the protection profile." if inputs.assets else "Asset register is empty.")
        if any(document.document_type in SERVICE_DOCUMENT_TYPES for document in inputs.documents) or inputs.work_orders:
            drivers.append("Service history is available for operational context.")
        else:
            drivers.append("Service history is not yet available.")
        return drivers[:9]

    @staticmethod
    def _portfolio_drivers(scores: list[FppScoreRead]) -> list[str]:
        if not scores:
            return ["No active buildings are available for portfolio scoring."]
        low_scores = [score for score in scores if score.buildingHealthIndex < 70]
        high_scores = [score for score in scores if score.buildingHealthIndex >= 85]
        return [
            f"{len(scores)} building(s) included in portfolio scoring.",
            f"{len(high_scores)} building(s) are above 85% Building Health Index.",
            f"{len(low_scores)} building(s) are below 70% Building Health Index.",
            "Portfolio scores are averaged from backend-backed building score calculations.",
        ]

    @staticmethod
    def _open_deficiencies(deficiencies: list[Deficiency]) -> list[Deficiency]:
        return [item for item in deficiencies if item.status in ACTIVE_DEFICIENCY_STATUSES and item.resolved_at is None]

    @staticmethod
    def _overdue_deficiencies(deficiencies: list[Deficiency]) -> list[Deficiency]:
        now = datetime.now(timezone.utc)
        return [item for item in deficiencies if item.due_at is not None and item.due_at < now and item.status not in CLOSED_DEFICIENCY_STATUSES]

    @staticmethod
    def _active_work_orders(work_orders: list[WorkOrder]) -> list[WorkOrder]:
        return [item for item in work_orders if item.status in ACTIVE_WORK_ORDER_STATUSES and item.completed_at is None]

    @staticmethod
    def _completed_work_orders(work_orders: list[WorkOrder]) -> list[WorkOrder]:
        return [item for item in work_orders if item.status in COMPLETE_WORK_ORDER_STATUSES or item.completed_at is not None]

    @staticmethod
    def _average(values: list[int]) -> int:
        return round(sum(values) / len(values)) if values else 0

    @staticmethod
    def _clamp(value: int | float) -> int:
        return max(0, min(100, round(value)))


fpp_score_service = FppScoreService()
