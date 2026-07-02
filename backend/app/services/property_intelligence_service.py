from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.models import (
    Asset,
    Building,
    Deficiency,
    Document,
    HealthScore,
    Inspection,
    Property,
    PropertyIntelligenceFactor,
    PropertyIntelligenceSnapshot,
    WorkOrder,
)
from app.schemas.core import PropertyRead
from app.services.exceptions import not_found
from app.services.tenant import ensure_organization_access


OPEN_DEFICIENCY_STATUSES = {"open", "new", "in_progress", "pending", "deferred"}
OPEN_WORK_ORDER_STATUSES = {"open", "new", "assigned", "scheduled", "in_progress"}
CRITICAL_SEVERITIES = {"critical", "high"}
POOR_CONDITIONS = {"poor", "critical", "failed", "needs_replacement"}
CALCULATION_VERSION = "m7-001"


class PropertyIntelligenceService:
    def get_intelligence(self, db: Session, property_id: UUID, current_user: CurrentUser) -> dict:
        property_record = self._get_property(db, property_id, current_user)
        context = self._build_context(db, property_record)
        result = self._calculate(property_record, context)
        result["latest_snapshot"] = self._latest_snapshot(db, property_record.id)
        return result

    def get_health_summary(self, db: Session, property_id: UUID, current_user: CurrentUser) -> dict:
        return self.get_intelligence(db, property_id, current_user)["health_summary"]

    def get_confidence_summary(self, db: Session, property_id: UUID, current_user: CurrentUser) -> dict:
        return self.get_intelligence(db, property_id, current_user)["confidence_summary"]

    def get_risk_summary(self, db: Session, property_id: UUID, current_user: CurrentUser) -> dict:
        return self.get_intelligence(db, property_id, current_user)["risk_summary"]

    def get_readiness_summary(self, db: Session, property_id: UUID, current_user: CurrentUser) -> dict:
        return self.get_intelligence(db, property_id, current_user)["readiness_summary"]

    def get_passport_summary(self, db: Session, property_id: UUID, current_user: CurrentUser) -> dict:
        return self.get_intelligence(db, property_id, current_user)["passport_rollup"]

    def get_capital_summary(self, db: Session, property_id: UUID, current_user: CurrentUser) -> dict:
        return self.get_intelligence(db, property_id, current_user)["capital_summary"]

    def get_deficiency_summary(self, db: Session, property_id: UUID, current_user: CurrentUser) -> dict:
        return self.get_intelligence(db, property_id, current_user)["deficiency_summary"]

    def recalculate_snapshot(self, db: Session, property_id: UUID, current_user: CurrentUser) -> dict:
        property_record = self._get_property(db, property_id, current_user)
        context = self._build_context(db, property_record)
        result = self._calculate(property_record, context)
        summary = self._snapshot_summary(result)
        snapshot = PropertyIntelligenceSnapshot(
            organization_id=property_record.organization_id,
            property_id=property_record.id,
            calculation_version=CALCULATION_VERSION,
            health_score=result["health"]["score"],
            confidence_score=result["confidence"]["score"],
            risk_score=result["risk"]["score"],
            readiness_score=result["readiness"]["score"],
            passport_score=result["passport"]["score"],
            building_count=self._count_value(result, "Buildings"),
            shared_infrastructure_count=self._count_value(result, "Shared Infrastructure"),
            asset_count=self._count_value(result, "Assets"),
            document_count=self._count_value(result, "Documents"),
            passport_record_count=self._count_value(result, "Passport Records"),
            client_visible_record_count=self._count_value(result, "Client Visible Records"),
            open_deficiency_count=result["deficiency_summary"]["open"],
            overdue_work_order_count=self._count_value(result, "Overdue Work Orders"),
            capital_exposure_estimate=result["capital_summary"]["replacement_cost_estimate"],
            summary=summary,
        )
        db.add(snapshot)
        db.flush()

        for factor in result["health_summary"]["factors"] + result["confidence_summary"]["factors"] + result["risk_summary"]["factors"] + result["readiness_summary"]["factors"] + result["passport_rollup"]["factors"]:
            db.add(
                PropertyIntelligenceFactor(
                    organization_id=property_record.organization_id,
                    property_id=property_record.id,
                    snapshot_id=snapshot.id,
                    category=factor["category"],
                    factor_key=factor["factor_key"],
                    label=factor["label"],
                    severity=factor["severity"],
                    source_type=factor.get("source_type"),
                    source_id=factor.get("source_id"),
                    impact_score=factor.get("impact_score", 0),
                    metadata_=factor.get("metadata", {}),
                )
            )

        db.commit()
        db.refresh(snapshot)
        result["latest_snapshot"] = self._snapshot_read(snapshot)
        return result

    def _get_property(self, db: Session, property_id: UUID, current_user: CurrentUser) -> Property:
        property_record = db.scalar(select(Property).where(Property.id == property_id, Property.deleted_at.is_(None)))
        if property_record is None:
            raise not_found("Property not found.")
        ensure_organization_access(current_user, property_record.organization_id)
        return property_record

    def _build_context(self, db: Session, property_record: Property) -> dict:
        buildings = list(
            db.scalars(
                select(Building)
                .where(
                    Building.property_id == property_record.id,
                    Building.organization_id == property_record.organization_id,
                    Building.deleted_at.is_(None),
                )
                .order_by(Building.name)
            ).all()
        )
        building_ids = [building.id for building in buildings]
        assets = self._list_for_buildings(db, Asset, building_ids)
        documents = self._list_for_buildings(db, Document, building_ids)
        deficiencies = self._list_for_buildings(db, Deficiency, building_ids)
        work_orders = self._list_for_buildings(db, WorkOrder, building_ids)
        inspections = self._list_for_buildings(db, Inspection, building_ids)
        health_scores = self._latest_building_health_scores(db, building_ids)
        return {
            "buildings": buildings,
            "assets": assets,
            "documents": documents,
            "deficiencies": deficiencies,
            "work_orders": work_orders,
            "inspections": inspections,
            "health_scores": health_scores,
        }

    def _calculate(self, property_record: Property, context: dict) -> dict:
        now = datetime.now(timezone.utc)
        buildings = context["buildings"]
        assets = context["assets"]
        documents = context["documents"]
        deficiencies = context["deficiencies"]
        work_orders = context["work_orders"]
        health_scores = context["health_scores"]

        open_deficiencies = [item for item in deficiencies if self._normalized(item.status) in OPEN_DEFICIENCY_STATUSES]
        critical_deficiencies = [item for item in open_deficiencies if self._normalized(item.severity) in CRITICAL_SEVERITIES]
        open_work_orders = [item for item in work_orders if self._normalized(item.status) in OPEN_WORK_ORDER_STATUSES]
        overdue_work_orders = [item for item in open_work_orders if item.due_at and item.due_at < now]
        expired_documents = [item for item in documents if item.expiry_date and item.expiry_date < now.date()]
        passport_documents = [item for item in documents if item.is_passport_record]
        client_visible_documents = [item for item in documents if item.is_public_to_client]
        shared_infrastructure = [building for building in buildings if self._is_shared_infrastructure(building)]
        operating_buildings = [building for building in buildings if building not in shared_infrastructure]
        poor_assets = [asset for asset in assets if self._normalized(asset.condition_rating) in POOR_CONDITIONS]

        passport_score = self._passport_score(buildings, passport_documents)
        readiness_score = self._readiness_score(buildings, assets, documents, shared_infrastructure, passport_score, critical_deficiencies, overdue_work_orders)
        confidence_score = self._confidence_score(buildings, assets, documents)
        risk_score = self._risk_score(open_deficiencies, critical_deficiencies, overdue_work_orders, expired_documents, poor_assets)
        building_health_score = self._average_latest_health_score(health_scores)
        health_score = self._health_score(building_health_score, confidence_score, readiness_score, passport_score, risk_score)

        readiness_checklist = self._readiness_checklist(buildings, assets, passport_documents, shared_infrastructure, critical_deficiencies, overdue_work_orders)
        capital_summary = self._capital_summary(buildings, assets, open_deficiencies)
        deficiency_summary = self._deficiency_summary(buildings, deficiencies, open_deficiencies, critical_deficiencies)
        building_rollups = [self._building_rollup(building, assets, documents, open_deficiencies, overdue_work_orders, health_scores) for building in buildings]

        health_factors = self._health_factors(buildings, health_score, risk_score, readiness_score, building_health_score)
        confidence_factors = self._confidence_factors(buildings, assets, documents)
        risk_factors = self._risk_factors(open_deficiencies, critical_deficiencies, overdue_work_orders, expired_documents, poor_assets)
        readiness_factors = self._readiness_factors(readiness_checklist)
        passport_factors = self._passport_factors(buildings, passport_documents, client_visible_documents)

        property_read = PropertyRead.model_validate(property_record)
        property_read.campus_count = len(getattr(property_record, "campuses", []) or [])
        property_read.building_count = len(buildings)

        health_summary = {
            "score": health_score,
            "status": self._score_status(health_score),
            "building_count": len(buildings),
            "active_building_count": len(operating_buildings),
            "shared_infrastructure_count": len(shared_infrastructure),
            "drivers": self._health_drivers(health_score, risk_score, readiness_score, building_health_score),
            "factors": health_factors,
        }
        confidence_summary = {
            "score": confidence_score,
            "status": self._score_status(confidence_score),
            "addressed_building_count": sum(1 for building in buildings if self._has_address(building)),
            "assets_with_condition_count": sum(1 for asset in assets if asset.condition_rating),
            "documents_with_visibility_count": sum(1 for document in documents if document.is_passport_record or document.is_public_to_client),
            "data_gap_count": self._data_gap_count(buildings, assets, documents),
            "drivers": self._confidence_drivers(buildings, assets, documents),
            "factors": confidence_factors,
        }
        risk_summary = {
            "score": risk_score,
            "status": self._risk_status(risk_score),
            "open_deficiency_count": len(open_deficiencies),
            "critical_or_high_deficiency_count": len(critical_deficiencies),
            "overdue_work_order_count": len(overdue_work_orders),
            "expired_document_count": len(expired_documents),
            "poor_condition_asset_count": len(poor_assets),
            "drivers": self._risk_drivers(open_deficiencies, critical_deficiencies, overdue_work_orders, expired_documents, poor_assets),
            "factors": risk_factors,
        }
        readiness_summary = {
            "score": readiness_score,
            "status": self._score_status(readiness_score),
            "ready_for_handover": readiness_score >= 80 and not critical_deficiencies and not overdue_work_orders,
            "checklist": readiness_checklist,
            "drivers": self._readiness_drivers(buildings, assets, documents, shared_infrastructure),
            "factors": readiness_factors,
        }
        passport_rollup = {
            "score": passport_score,
            "status": self._score_status(passport_score),
            "passport_records": len(passport_documents),
            "client_visible_records": len(client_visible_documents),
            "building_count": len(buildings),
            "shared_infrastructure_count": len(shared_infrastructure),
            "completeness_score": passport_score,
            "drivers": self._passport_drivers(buildings, passport_documents, client_visible_documents),
            "factors": passport_factors,
        }

        return {
            "property": property_read,
            "calculated_at": now,
            "health": self._score(health_score, "Property Health", self._score_status(health_score), health_summary["drivers"]),
            "confidence": self._score(confidence_score, "Property Confidence Index", self._score_status(confidence_score), confidence_summary["drivers"]),
            "risk": self._score(risk_score, "Property Risk", self._risk_status(risk_score), risk_summary["drivers"]),
            "readiness": self._score(readiness_score, "Property Readiness", self._score_status(readiness_score), readiness_summary["drivers"]),
            "passport": self._score(passport_score, "Property Passport", self._score_status(passport_score), passport_rollup["drivers"]),
            "executive_summary": self._executive_summary(property_record.name, health_score, risk_score, readiness_score),
            "counts": [
                self._count("Buildings", len(operating_buildings)),
                self._count("Shared Infrastructure", len(shared_infrastructure)),
                self._count("Assets", len(assets)),
                self._count("Documents", len(documents)),
                self._count("Passport Records", len(passport_documents)),
                self._count("Client Visible Records", len(client_visible_documents)),
                self._count("Open Deficiencies", len(open_deficiencies), "warning" if open_deficiencies else "good"),
                self._count("Overdue Work Orders", len(overdue_work_orders), "warning" if overdue_work_orders else "good"),
            ],
            "buildings": building_rollups,
            "health_summary": health_summary,
            "confidence_summary": confidence_summary,
            "risk_summary": risk_summary,
            "readiness_summary": readiness_summary,
            "passport_rollup": passport_rollup,
            "passport_summary": passport_rollup,
            "capital_summary": capital_summary,
            "deficiency_summary": deficiency_summary,
            "readiness_checklist": readiness_checklist,
            "executive_review": {
                "status": "placeholder",
                "title": f"{property_record.name} Executive Review",
                "message": "Executive review generation is reserved for a future M7 phase.",
            },
            "latest_snapshot": None,
        }

    def _list_for_buildings(self, db: Session, model, building_ids: list[UUID]) -> list:
        if not building_ids:
            return []
        query = select(model).where(model.building_id.in_(building_ids))
        if hasattr(model, "deleted_at"):
            query = query.where(model.deleted_at.is_(None))
        return list(db.scalars(query).all())

    def _latest_building_health_scores(self, db: Session, building_ids: list[UUID]) -> dict[UUID, HealthScore]:
        if not building_ids:
            return {}
        rows = list(
            db.scalars(
                select(HealthScore)
                .where(HealthScore.building_id.in_(building_ids), HealthScore.score_type == "overall")
                .order_by(HealthScore.building_id, HealthScore.calculated_at.desc())
            ).all()
        )
        latest: dict[UUID, HealthScore] = {}
        for row in rows:
            if row.building_id not in latest:
                latest[row.building_id] = row
        return latest

    def _latest_snapshot(self, db: Session, property_id: UUID) -> dict | None:
        snapshot = db.scalar(
            select(PropertyIntelligenceSnapshot)
            .where(PropertyIntelligenceSnapshot.property_id == property_id)
            .order_by(PropertyIntelligenceSnapshot.calculated_at.desc())
            .limit(1)
        )
        return self._snapshot_read(snapshot) if snapshot else None

    def _snapshot_read(self, snapshot: PropertyIntelligenceSnapshot) -> dict:
        return {
            "id": snapshot.id,
            "calculation_version": snapshot.calculation_version,
            "calculated_at": snapshot.calculated_at,
            "health_score": snapshot.health_score,
            "confidence_score": snapshot.confidence_score,
            "risk_score": snapshot.risk_score,
            "readiness_score": snapshot.readiness_score,
            "passport_score": snapshot.passport_score,
        }

    def _is_shared_infrastructure(self, building: Building) -> bool:
        name = building.name.lower()
        return self._normalized(building.building_type) == "shared_infrastructure" or "shared" in name or "common parking" in name

    def _score(self, score: int, label: str, status: str, drivers: list[str]) -> dict:
        return {"score": max(0, min(100, score)), "label": label, "status": status, "drivers": drivers}

    def _count(self, label: str, value: int | float, status: str = "neutral") -> dict:
        return {"label": label, "value": value, "status": status}

    def _score_status(self, score: int) -> str:
        if score >= 80:
            return "strong"
        if score >= 60:
            return "watch"
        return "needs_attention"

    def _risk_status(self, score: int) -> str:
        if score >= 70:
            return "high"
        if score >= 35:
            return "moderate"
        return "low"

    def _passport_score(self, buildings: list[Building], passport_documents: list[Document]) -> int:
        if not buildings:
            return 0
        expected_records = max(1, len(buildings) * 3)
        return round(min(100, (len(passport_documents) / expected_records) * 100))

    def _readiness_score(
        self,
        buildings: list[Building],
        assets: list[Asset],
        documents: list[Document],
        shared_infrastructure: list[Building],
        passport_score: int,
        critical_deficiencies: list[Deficiency],
        overdue_work_orders: list[WorkOrder],
    ) -> int:
        checks = [
            bool(buildings),
            bool(assets),
            bool(documents),
            bool(shared_infrastructure),
            passport_score >= 60,
            not critical_deficiencies,
            not overdue_work_orders,
        ]
        return round((sum(1 for item in checks if item) / len(checks)) * 100)

    def _confidence_score(self, buildings: list[Building], assets: list[Asset], documents: list[Document]) -> int:
        if not buildings:
            return 0
        buildings_with_address = sum(1 for building in buildings if self._has_address(building))
        assets_with_condition = sum(1 for asset in assets if asset.condition_rating)
        documents_with_visibility = sum(1 for document in documents if document.is_passport_record or document.is_public_to_client)
        building_component = buildings_with_address / len(buildings)
        asset_component = assets_with_condition / len(assets) if assets else 0
        document_component = documents_with_visibility / len(documents) if documents else 0
        return round(((building_component * 0.4) + (asset_component * 0.3) + (document_component * 0.3)) * 100)

    def _risk_score(
        self,
        open_deficiencies: list[Deficiency],
        critical_deficiencies: list[Deficiency],
        overdue_work_orders: list[WorkOrder],
        expired_documents: list[Document],
        poor_assets: list[Asset],
    ) -> int:
        score = (
            len(open_deficiencies) * 8
            + len(critical_deficiencies) * 18
            + len(overdue_work_orders) * 10
            + len(expired_documents) * 5
            + len(poor_assets) * 8
        )
        return min(100, score)

    def _health_score(self, building_health_score: int | None, confidence_score: int, readiness_score: int, passport_score: int, risk_score: int) -> int:
        if building_health_score is None:
            return round((confidence_score + readiness_score + passport_score + (100 - risk_score)) / 4)
        return round((building_health_score * 0.35) + (confidence_score * 0.2) + (readiness_score * 0.2) + (passport_score * 0.15) + ((100 - risk_score) * 0.1))

    def _average_latest_health_score(self, health_scores: dict[UUID, HealthScore]) -> int | None:
        if not health_scores:
            return None
        return round(sum(row.score for row in health_scores.values()) / len(health_scores))

    def _building_rollup(
        self,
        building: Building,
        assets: list[Asset],
        documents: list[Document],
        open_deficiencies: list[Deficiency],
        overdue_work_orders: list[WorkOrder],
        health_scores: dict[UUID, HealthScore],
    ) -> dict:
        building_assets = [asset for asset in assets if asset.building_id == building.id]
        building_documents = [document for document in documents if document.building_id == building.id]
        passport_records = [document for document in building_documents if document.is_passport_record]
        building_deficiencies = [item for item in open_deficiencies if item.building_id == building.id]
        building_work_orders = [item for item in overdue_work_orders if item.building_id == building.id]
        ready = bool(building_assets) and bool(passport_records) and not building_deficiencies and not building_work_orders
        return {
            "id": building.id,
            "name": building.name,
            "building_type": building.building_type,
            "bpid": building.bpid,
            "asset_count": len(building_assets),
            "document_count": len(building_documents),
            "passport_record_count": len(passport_records),
            "open_deficiency_count": len(building_deficiencies),
            "overdue_work_order_count": len(building_work_orders),
            "readiness_status": "ready" if ready else "watch",
            "health_score": health_scores.get(building.id).score if building.id in health_scores else None,
        }

    def _capital_summary(self, buildings: list[Building], assets: list[Asset], open_deficiencies: list[Deficiency]) -> dict:
        replacement_values = [float(asset.replacement_cost_estimate or 0) for asset in assets]
        near_term_assets = [asset for asset in assets if asset.remaining_useful_life_years is not None and asset.remaining_useful_life_years <= 3]
        missing_replacement_cost = [asset for asset in assets if not asset.replacement_cost_estimate]
        by_building = []
        for building in buildings:
            building_assets = [asset for asset in assets if asset.building_id == building.id]
            building_cost = sum(float(asset.replacement_cost_estimate or 0) for asset in building_assets)
            by_building.append(
                {
                    "building_id": str(building.id),
                    "building_name": building.name,
                    "replacement_cost_estimate": round(building_cost, 2),
                    "near_term_asset_count": len([asset for asset in building_assets if asset.remaining_useful_life_years is not None and asset.remaining_useful_life_years <= 3]),
                }
            )
        return {
            "replacement_cost_estimate": round(sum(replacement_values), 2),
            "near_term_asset_count": len(near_term_assets),
            "open_deficiency_count": len(open_deficiencies),
            "planning_status": "placeholder" if not replacement_values or sum(replacement_values) == 0 else "active",
            "assets_missing_replacement_cost_count": len(missing_replacement_cost),
            "by_building": by_building,
        }

    def _deficiency_summary(self, buildings: list[Building], deficiencies: list[Deficiency], open_deficiencies: list[Deficiency], critical_deficiencies: list[Deficiency]) -> dict:
        by_building = []
        for building in buildings:
            building_open = [item for item in open_deficiencies if item.building_id == building.id]
            by_building.append(
                {
                    "building_id": str(building.id),
                    "building_name": building.name,
                    "open": len(building_open),
                    "critical_or_high": len([item for item in building_open if self._normalized(item.severity) in CRITICAL_SEVERITIES]),
                }
            )
        return {
            "open": len(open_deficiencies),
            "critical_or_high": len(critical_deficiencies),
            "by_severity": self._count_by(open_deficiencies, "severity"),
            "by_status": self._count_by(deficiencies, "status"),
            "by_building": by_building,
        }

    def _readiness_checklist(
        self,
        buildings: list[Building],
        assets: list[Asset],
        passport_documents: list[Document],
        shared_infrastructure: list[Building],
        critical_deficiencies: list[Deficiency],
        overdue_work_orders: list[WorkOrder],
    ) -> list[dict]:
        return [
            {"key": "building_records", "label": "Property has related building records", "complete": bool(buildings)},
            {"key": "shared_infrastructure", "label": "Shared infrastructure is represented", "complete": bool(shared_infrastructure)},
            {"key": "asset_register", "label": "Assets are registered", "complete": bool(assets)},
            {"key": "passport_records", "label": "Passport records are available", "complete": bool(passport_documents)},
            {"key": "critical_deficiencies", "label": "No critical/high deficiencies are open", "complete": not critical_deficiencies},
            {"key": "overdue_work_orders", "label": "No overdue work orders are open", "complete": not overdue_work_orders},
        ]

    def _count_by(self, rows: list, field: str) -> dict[str, int]:
        values: dict[str, int] = {}
        for row in rows:
            key = str(getattr(row, field, None) or "unknown")
            values[key] = values.get(key, 0) + 1
        return values

    def _factor(self, category: str, factor_key: str, label: str, severity: str = "info", impact_score: int = 0, source_type: str | None = None, source_id: UUID | None = None, metadata: dict | None = None) -> dict:
        return {
            "category": category,
            "factor_key": factor_key,
            "label": label,
            "severity": severity,
            "source_type": source_type,
            "source_id": source_id,
            "impact_score": impact_score,
            "metadata": metadata or {},
        }

    def _health_factors(self, buildings: list[Building], health_score: int, risk_score: int, readiness_score: int, building_health_score: int | None) -> list[dict]:
        factors = [
            self._factor("health", "property_health_score", f"Property Health score is {health_score}.", "info", health_score),
            self._factor("health", "risk_contribution", f"Property Risk score is {risk_score}.", "warning" if risk_score >= 35 else "good", 100 - risk_score),
            self._factor("health", "readiness_contribution", f"Property Readiness score is {readiness_score}.", "info", readiness_score),
        ]
        if building_health_score is None:
            factors.append(self._factor("health", "missing_building_health_scores", "No building health scores are currently available.", "warning", -10))
        else:
            factors.append(self._factor("health", "building_health_rollup", f"Average latest building health score is {building_health_score}.", "info", building_health_score))
        if not buildings:
            factors.append(self._factor("health", "no_buildings", "No active buildings are assigned to this property.", "warning", -30))
        return factors

    def _confidence_factors(self, buildings: list[Building], assets: list[Asset], documents: list[Document]) -> list[dict]:
        factors = [
            self._factor("confidence", "building_records", f"{len(buildings)} building records contribute to the index.", "info", len(buildings)),
            self._factor("confidence", "asset_records", f"{len(assets)} asset records contribute to the index.", "info", len(assets)),
            self._factor("confidence", "document_records", f"{len(documents)} document records contribute to the index.", "info", len(documents)),
        ]
        if self._data_gap_count(buildings, assets, documents):
            factors.append(self._factor("confidence", "data_gaps", f"{self._data_gap_count(buildings, assets, documents)} data gaps were detected.", "warning", -10))
        return factors

    def _risk_factors(self, open_deficiencies: list[Deficiency], critical_deficiencies: list[Deficiency], overdue_work_orders: list[WorkOrder], expired_documents: list[Document], poor_assets: list[Asset]) -> list[dict]:
        return [
            self._factor("risk", "open_deficiencies", f"{len(open_deficiencies)} open deficiencies.", "warning" if open_deficiencies else "good", len(open_deficiencies) * 8),
            self._factor("risk", "critical_deficiencies", f"{len(critical_deficiencies)} critical/high deficiencies.", "critical" if critical_deficiencies else "good", len(critical_deficiencies) * 18),
            self._factor("risk", "overdue_work_orders", f"{len(overdue_work_orders)} overdue work orders.", "warning" if overdue_work_orders else "good", len(overdue_work_orders) * 10),
            self._factor("risk", "expired_documents", f"{len(expired_documents)} expired documents.", "warning" if expired_documents else "good", len(expired_documents) * 5),
            self._factor("risk", "poor_assets", f"{len(poor_assets)} poor/critical condition assets.", "warning" if poor_assets else "good", len(poor_assets) * 8),
        ]

    def _readiness_factors(self, checklist: list[dict]) -> list[dict]:
        return [
            self._factor("readiness", item["key"], item["label"], "good" if item["complete"] else "warning", 10 if item["complete"] else -10)
            for item in checklist
        ]

    def _passport_factors(self, buildings: list[Building], passport_documents: list[Document], client_visible_documents: list[Document]) -> list[dict]:
        return [
            self._factor("passport", "passport_records", f"{len(passport_documents)} Passport records across {len(buildings)} records.", "info", len(passport_documents)),
            self._factor("passport", "client_visible_records", f"{len(client_visible_documents)} client-visible records.", "info", len(client_visible_documents)),
        ]

    def _health_drivers(self, health_score: int, risk_score: int, readiness_score: int, building_health_score: int | None) -> list[str]:
        drivers = [f"Risk score is {risk_score}.", f"Readiness score is {readiness_score}."]
        if building_health_score is None:
            drivers.append("Building health scores are not yet available for this property.")
        if health_score >= 80:
            drivers.append("Overall property intelligence is strong.")
        elif health_score < 60:
            drivers.append("Property needs attention before executive review.")
        return drivers

    def _confidence_drivers(self, buildings: list[Building], assets: list[Asset], documents: list[Document]) -> list[str]:
        return [
            f"{len(buildings)} building records contribute to the index.",
            f"{len(assets)} asset records contribute to the index.",
            f"{len(documents)} document records contribute to the index.",
        ]

    def _risk_drivers(self, open_deficiencies: list[Deficiency], critical_deficiencies: list[Deficiency], overdue_work_orders: list[WorkOrder], expired_documents: list[Document], poor_assets: list[Asset]) -> list[str]:
        return [
            f"{len(open_deficiencies)} open deficiencies.",
            f"{len(critical_deficiencies)} critical/high deficiencies.",
            f"{len(overdue_work_orders)} overdue work orders.",
            f"{len(expired_documents)} expired documents.",
            f"{len(poor_assets)} poor/critical condition assets.",
        ]

    def _readiness_drivers(self, buildings: list[Building], assets: list[Asset], documents: list[Document], shared_infrastructure: list[Building]) -> list[str]:
        return [
            f"{len(buildings)} related building/shared infrastructure records.",
            f"{len(shared_infrastructure)} shared infrastructure records.",
            f"{len(assets)} assets registered.",
            f"{len(documents)} evidence records available.",
        ]

    def _passport_drivers(self, buildings: list[Building], passport_documents: list[Document], client_visible_documents: list[Document]) -> list[str]:
        return [
            f"{len(passport_documents)} Passport records across {len(buildings)} records.",
            f"{len(client_visible_documents)} client-visible records.",
        ]

    def _executive_summary(self, property_name: str, health_score: int, risk_score: int, readiness_score: int) -> str:
        return (
            f"{property_name} currently has a Property Health score of {health_score}, "
            f"Property Risk score of {risk_score}, and Property Readiness score of {readiness_score}. "
            "This M7 summary is generated from existing building, asset, document, deficiency, work order, inspection, and health score records."
        )

    def _snapshot_summary(self, result: dict) -> dict:
        return {
            "executive_summary": result["executive_summary"],
            "health_summary": self._json_safe(result["health_summary"]),
            "confidence_summary": self._json_safe(result["confidence_summary"]),
            "risk_summary": self._json_safe(result["risk_summary"]),
            "readiness_summary": self._json_safe(result["readiness_summary"]),
            "passport_rollup": self._json_safe(result["passport_rollup"]),
            "capital_summary": self._json_safe(result["capital_summary"]),
            "deficiency_summary": self._json_safe(result["deficiency_summary"]),
        }

    def _json_safe(self, value):
        if isinstance(value, dict):
            return {key: self._json_safe(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._json_safe(item) for item in value]
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    def _count_value(self, result: dict, label: str) -> int:
        for item in result["counts"]:
            if item["label"] == label:
                return int(item["value"])
        return 0

    def _has_address(self, building: Building) -> bool:
        return bool((building.address_line_1 or building.address_line1) and building.city and building.province_state)

    def _data_gap_count(self, buildings: list[Building], assets: list[Asset], documents: list[Document]) -> int:
        gaps = sum(1 for building in buildings if not self._has_address(building))
        gaps += sum(1 for asset in assets if not asset.condition_rating)
        gaps += sum(1 for document in documents if not document.is_passport_record and not document.is_public_to_client)
        return gaps

    def _normalized(self, value: str | None) -> str:
        return (value or "").strip().lower()


property_intelligence_service = PropertyIntelligenceService()
